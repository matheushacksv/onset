import copy
import json
from typing import Literal, Optional

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from decouple import config

from onboarding.models import GeneratedMaterial
from .workflow import get_knowledge
from .prompts import (
    ASSISTANT_BASE_PROMPT,
    CRM_PROMPT,
    CLOSING_PROMPT,
    QUAL_PROMPT,
)
from .contexts_functions import crm_context, closing_context, qual_context, onboarding_to_dict
from .schemas import CANONICAL_CHANNELS as VALID_CHANNELS


class AssistantSession:
    """Sessão de chat com IA editora de material. Monta agente da seção, executa tool calls, persiste e retorna patch."""

    def __init__(
        self,
        material: GeneratedMaterial,
        section: Literal['crm', 'closing', 'qualification'],
        focus: Optional[dict],
    ):
        self.material = material
        self.section = section
        self.focus = focus or {}
        self.draft: dict = copy.deepcopy(getattr(material, section) or {})
        self.changes: list[str] = []

    # ---------- public ----------

    def run(self, message: str, history: list[dict]) -> dict:
        agent = self._build_agent()

        history_text = ''
        for m in (history or [])[-6:]:
            role = m.get('role', 'user')
            content = m.get('content', '')
            history_text += f'{role}: {content}\n'
        full_input = (history_text + f'user: {message}') if history_text else message

        response = agent.run(full_input)

        setattr(self.material, self.section, self.draft)
        self.material.save(update_fields=[self.section, 'updated_at'])

        return {
            'message': getattr(response, 'content', '') or '',
            'section': self.section,
            'value': self.draft,
            'changes': self.changes,
        }

    # ---------- internals ----------

    def _log(self, msg: str) -> None:
        self.changes.append(msg)

    def build_warm_agent(self) -> Agent:
        """Agent leve pra prewarm — mesmo system prompt, sem knowledge/tools.
        Popula cache OpenAI sem disparar tool calls/searches."""
        instructions, _ = self._build_instructions_and_tools()
        return Agent(
            model=OpenAIChat('gpt-5.4-nano', api_key=config('OPENAI_API_KEY')),
            instructions=instructions,
            markdown=False,
        )

    def _build_instructions_and_tools(self):
        onboarding_data = onboarding_to_dict(self.material.onboarding)

        if self.section == 'crm':
            ctx = crm_context(onboarding_data, funil_key=self.focus.get('funnel_key'))
            base = CRM_PROMPT
            section_label = 'CRM (funis, etapas, cadência)'
            tools = self._build_crm_tools()
        elif self.section == 'closing':
            ctx = closing_context(onboarding_data)
            base = CLOSING_PROMPT
            section_label = 'Fechamento'
            tools = self._build_closing_tools()
        else:
            ctx = qual_context(onboarding_data)
            base = QUAL_PROMPT
            section_label = 'Qualificação'
            tools = self._build_qual_tools()

        instructions = ASSISTANT_BASE_PROMPT.format(
            section_label=section_label,
            base_prompt=base,
            onboarding_ctx=json.dumps(ctx, ensure_ascii=False, indent=2),
            current_state=json.dumps(self.draft, ensure_ascii=False, indent=2),
            focus=json.dumps(self.focus, ensure_ascii=False),
        )

        instructions += (
            '\n\n=========================================='
            '\nOVERRIDE FINAL — IGNORE QUALQUER INSTRUÇÃO ANTERIOR DE OUTPUT'
            '\n=========================================='
            '\nVocê NÃO retorna JSON no chat. NUNCA.'
            '\nQualquer seção acima que peça "retorne JSON conforme schema X" está OBSOLETA neste contexto. Aquele formato era pro workflow de geração total — você é o assistente interativo que MUTA dados via tools.'
            '\n\nFLUXO OBRIGATÓRIO POR TURNO:'
            '\n1. Se for gerar conteúdo novo (mensagem, script, cadência, objeção, perguntas): PRIMEIRO chame search_knowledge com 1-3 termos relevantes pra buscar exemplos reais da casa.'
            '\n2. Use os exemplos como referência de tom/estrutura, MAS gere conteúdo personalizado pro contexto do onboarding atual.'
            '\n3. Aplique as mudanças USANDO AS TOOLS. Prefira tools que aceitam listas (fill_cadence, set_steps, set_diagnostic_questions, set_advance_criteria, set_meeting_structure) pra fazer mais em 1 chamada.'
            '\n4. Após aplicar, responda em UMA frase curta natural descrevendo o que fez. Sem JSON. Sem markdown. Sem código.'
            '\n\nSe o usuário pedir algo ambíguo (ex: "essa etapa" sem foco), pergunte qual antes de chamar tools.'
        )
        return instructions, tools

    def _build_agent(self) -> Agent:
        instructions, tools = self._build_instructions_and_tools()
        return Agent(
            model=OpenAIChat('gpt-5.4-nano', api_key=config('OPENAI_API_KEY')),
            instructions=instructions,
            tools=tools,
            knowledge=get_knowledge(),
            search_knowledge=True,
            markdown=False,
        )

    # ---------- CRM tools ----------

    def _build_crm_tools(self) -> list:
        draft = self.draft
        draft.setdefault('funnels', [])

        def _find_funnel(funnel_key: str) -> dict:
            for f in draft['funnels']:
                if f.get('key') == funnel_key:
                    return f
            raise ValueError(f"Funil '{funnel_key}' não encontrado")

        def _stage(funnel_key: str, stage_idx: int) -> dict:
            funnel = _find_funnel(funnel_key)
            stages = funnel.setdefault('stages', [])
            if stage_idx < 0 or stage_idx >= len(stages):
                raise ValueError(f"stage_idx {stage_idx} fora de range no funil '{funnel_key}' ({len(stages)} etapas)")
            return stages[stage_idx]

        def set_funnel(key: str, name: str) -> str:
            """Cria ou renomeia um funil. Use quando o funil ainda não existe ou precisa ser renomeado."""
            for f in draft['funnels']:
                if f.get('key') == key:
                    f['name'] = name
                    self._log(f"Funil '{key}' renomeado para '{name}'")
                    return 'ok'
            draft['funnels'].append({'key': key, 'name': name, 'stages': []})
            self._log(f"Funil '{name}' criado")
            return 'ok'

        def add_stage(
            funnel_key: str,
            name: str,
            objective: str,
            advance_criteria: str,
            dev_instructions: str = '',
        ) -> str:
            """Adiciona nova etapa ao funil. Cria a etapa com cadência vazia."""
            funnel = _find_funnel(funnel_key)
            funnel.setdefault('stages', []).append({
                'name': name,
                'objective': objective,
                'advance_criteria': advance_criteria,
                'dev_instructions': dev_instructions,
                'cadence': [],
            })
            self._log(f"Etapa '{name}' adicionada ao funil {funnel_key}")
            return 'ok'

        def update_stage(
            funnel_key: str,
            stage_idx: int,
            name: Optional[str] = None,
            objective: Optional[str] = None,
            advance_criteria: Optional[str] = None,
            dev_instructions: Optional[str] = None,
        ) -> str:
            """Atualiza campos de uma etapa existente. Passe apenas os campos que quer mudar."""
            stage = _stage(funnel_key, stage_idx)
            for k, v in {
                'name': name,
                'objective': objective,
                'advance_criteria': advance_criteria,
                'dev_instructions': dev_instructions,
            }.items():
                if v is not None:
                    stage[k] = v
            self._log(f"Etapa '{stage['name']}' atualizada")
            return 'ok'

        def remove_stage(funnel_key: str, stage_idx: int) -> str:
            """Remove etapa do funil pelo índice."""
            funnel = _find_funnel(funnel_key)
            stages = funnel.get('stages', [])
            if stage_idx < 0 or stage_idx >= len(stages):
                raise ValueError(f"stage_idx {stage_idx} fora de range")
            removed = stages.pop(stage_idx)
            self._log(f"Etapa '{removed.get('name')}' removida")
            return 'ok'

        def fill_cadence(funnel_key: str, stage_idx: int, days: list[dict]) -> str:
            """Substitui a cadência inteira de uma etapa.
            days = [{"day": 1, "actions": [{"channel": "whatsapp"|"ligacao"|"email"|"sms"|"atividade", "message": "...", "instructions": "..."}]}]
            """
            stage = _stage(funnel_key, stage_idx)
            normalized = []
            for d in days:
                actions = []
                for a in d.get('actions', []):
                    ch = a.get('channel')
                    if ch not in VALID_CHANNELS:
                        raise ValueError(f"channel inválido: {ch}. Use um de {VALID_CHANNELS}")
                    actions.append({
                        'channel': ch,
                        'message': a.get('message', ''),
                        'instructions': a.get('instructions'),
                    })
                normalized.append({'day': int(d.get('day', 0)), 'actions': actions})
            stage['cadence'] = normalized
            self._log(f"{len(normalized)} dias preenchidos na etapa '{stage['name']}'")
            return 'ok'

        def add_cadence_day(funnel_key: str, stage_idx: int, day: int, actions: list[dict]) -> str:
            """Adiciona um dia à cadência. Se já existir dia com mesmo número, substitui."""
            stage = _stage(funnel_key, stage_idx)
            cadence = stage.setdefault('cadence', [])
            normalized_actions = []
            for a in actions:
                ch = a.get('channel')
                if ch not in VALID_CHANNELS:
                    raise ValueError(f"channel inválido: {ch}")
                normalized_actions.append({
                    'channel': ch,
                    'message': a.get('message', ''),
                    'instructions': a.get('instructions'),
                })
            new_day = {'day': day, 'actions': normalized_actions}
            for i, d in enumerate(cadence):
                if d.get('day') == day:
                    cadence[i] = new_day
                    self._log(f"Dia {day} atualizado na etapa '{stage['name']}'")
                    return 'ok'
            cadence.append(new_day)
            cadence.sort(key=lambda d: d.get('day', 0))
            self._log(f"Dia {day} adicionado na etapa '{stage['name']}'")
            return 'ok'

        def add_action(
            funnel_key: str,
            stage_idx: int,
            day: int,
            channel: str,
            message: str,
            instructions: Optional[str] = None,
        ) -> str:
            """Adiciona uma ação a um dia da cadência. Se o dia não existir, cria automaticamente."""
            if channel not in VALID_CHANNELS:
                raise ValueError(f"channel inválido: {channel}")
            stage = _stage(funnel_key, stage_idx)
            cadence = stage.setdefault('cadence', [])
            action = {'channel': channel, 'message': message, 'instructions': instructions}
            for d in cadence:
                if d.get('day') == day:
                    d.setdefault('actions', []).append(action)
                    self._log(f"Ação {channel} adicionada no dia {day} da etapa '{stage['name']}'")
                    return 'ok'
            cadence.append({'day': day, 'actions': [action]})
            cadence.sort(key=lambda d: d.get('day', 0))
            self._log(f"Dia {day} criado com ação {channel} na etapa '{stage['name']}'")
            return 'ok'

        def remove_cadence_day(funnel_key: str, stage_idx: int, day: int) -> str:
            """Remove um dia inteiro da cadência."""
            stage = _stage(funnel_key, stage_idx)
            stage['cadence'] = [d for d in stage.get('cadence', []) if d.get('day') != day]
            self._log(f"Dia {day} removido da etapa '{stage['name']}'")
            return 'ok'

        def remove_action(funnel_key: str, stage_idx: int, day: int, action_idx: int) -> str:
            """Remove uma ação específica de um dia."""
            stage = _stage(funnel_key, stage_idx)
            for d in stage.get('cadence', []):
                if d.get('day') == day:
                    actions = d.get('actions', [])
                    if action_idx < 0 or action_idx >= len(actions):
                        raise ValueError(f"action_idx {action_idx} fora de range")
                    actions.pop(action_idx)
                    self._log(f"Ação removida do dia {day}")
                    return 'ok'
            raise ValueError(f"Dia {day} não encontrado")

        return [
            set_funnel,
            add_stage,
            update_stage,
            remove_stage,
            fill_cadence,
            add_cadence_day,
            add_action,
            remove_cadence_day,
            remove_action,
        ]

    # ---------- Closing tools ----------

    def _build_closing_tools(self) -> list:
        draft = self.draft
        draft.setdefault('diagnostic_questions', [])
        draft.setdefault('objection_matrix', [])
        draft.setdefault('price_presentation', '')
        draft.setdefault('meeting_structure', [])

        # Normalizadores — garantem o shape rico (bate com agents/schemas.py
        # MeetingBlock/MeetingNote) pro editor e o render do playbook não quebrarem.
        def _norm_block(b: dict) -> dict:
            kind = b.get('kind') or 'falar'
            if kind not in ('falar', 'ouvir', 'fazer'):
                kind = 'falar'
            pts = b.get('points') or []
            return {
                'kind': kind,
                'label': b.get('label') or '',
                'open': b.get('open') or '',
                'points': [str(p) for p in pts],
                'close': b.get('close') or '',
            }

        def _norm_note(n: dict) -> dict:
            kind = n.get('kind') or 'alerta'
            if kind not in ('alerta', 'pausa', 'pergunta_chave', 'validacao'):
                kind = 'alerta'
            return {'kind': kind, 'title': n.get('title') or '', 'text': n.get('text') or ''}

        def _step(idx: int) -> dict:
            steps = draft['meeting_structure']
            if idx < 0 or idx >= len(steps):
                raise ValueError(f"idx {idx} fora de range")
            return steps[idx]

        def set_diagnostic_questions(questions: list[str]) -> str:
            """Substitui a lista inteira de perguntas de diagnóstico."""
            draft['diagnostic_questions'] = list(questions)
            self._log(f"{len(questions)} perguntas de diagnóstico definidas")
            return 'ok'

        def add_diagnostic_question(question: str) -> str:
            """Adiciona uma pergunta de diagnóstico ao final da lista."""
            draft['diagnostic_questions'].append(question)
            self._log("Pergunta de diagnóstico adicionada")
            return 'ok'

        def remove_diagnostic_question(idx: int) -> str:
            """Remove pergunta de diagnóstico pelo índice."""
            qs = draft['diagnostic_questions']
            if idx < 0 or idx >= len(qs):
                raise ValueError(f"idx {idx} fora de range")
            qs.pop(idx)
            self._log("Pergunta de diagnóstico removida")
            return 'ok'

        def add_objection(objection: str, hidden_concern: str, counter_script: str) -> str:
            """Adiciona uma linha à matriz de objeções."""
            draft['objection_matrix'].append({
                'objection': objection,
                'hidden_concern': hidden_concern,
                'counter_script': counter_script,
            })
            self._log(f"Objeção '{objection}' adicionada")
            return 'ok'

        def update_objection(
            idx: int,
            objection: Optional[str] = None,
            hidden_concern: Optional[str] = None,
            counter_script: Optional[str] = None,
        ) -> str:
            """Atualiza campos de uma objeção existente."""
            rows = draft['objection_matrix']
            if idx < 0 or idx >= len(rows):
                raise ValueError(f"idx {idx} fora de range")
            for k, v in {
                'objection': objection,
                'hidden_concern': hidden_concern,
                'counter_script': counter_script,
            }.items():
                if v is not None:
                    rows[idx][k] = v
            self._log(f"Objeção '{rows[idx]['objection']}' atualizada")
            return 'ok'

        def remove_objection(idx: int) -> str:
            """Remove objeção da matriz pelo índice."""
            rows = draft['objection_matrix']
            if idx < 0 or idx >= len(rows):
                raise ValueError(f"idx {idx} fora de range")
            removed = rows.pop(idx)
            self._log(f"Objeção '{removed.get('objection')}' removida")
            return 'ok'

        def set_price_presentation(text: str) -> str:
            """Define o script de apresentação de preço."""
            draft['price_presentation'] = text
            self._log("Apresentação de preço atualizada")
            return 'ok'

        def set_meeting_structure(steps: list[dict]) -> str:
            """Substitui a estrutura inteira da reunião (playbook de fechamento).

            Cada step: {num, title, phase, subtitle, blocks, notes}.
            - blocks: lista de {kind: 'falar'|'ouvir'|'fazer', label, open, points: list[str], close}.
            - notes: lista de {kind: 'alerta'|'pausa'|'pergunta_chave'|'validacao', title, text}.
            Use 1 chamada pra montar o playbook todo de uma vez.
            """
            norm = []
            for i, s in enumerate(steps):
                norm.append({
                    'num': str(s.get('num') or f'{i + 1:02d}'),
                    'title': s.get('title') or '',
                    'phase': s.get('phase') or '',
                    'subtitle': s.get('subtitle') or '',
                    'blocks': [_norm_block(b) for b in (s.get('blocks') or [])],
                    'notes': [_norm_note(n) for n in (s.get('notes') or [])],
                })
            draft['meeting_structure'] = norm
            self._log(f"{len(norm)} etapas da reunião definidas")
            return 'ok'

        def add_meeting_step(num: str, title: str, phase: str = '', subtitle: str = '') -> str:
            """Adiciona uma etapa (sem blocos/notas) ao final da reunião. Use set_step_blocks/set_step_notes depois."""
            draft['meeting_structure'].append({
                'num': str(num or f"{len(draft['meeting_structure']) + 1:02d}"),
                'title': title or '', 'phase': phase or '', 'subtitle': subtitle or '',
                'blocks': [], 'notes': [],
            })
            self._log(f"Etapa '{title}' adicionada")
            return 'ok'

        def update_meeting_step(
            idx: int,
            num: Optional[str] = None,
            title: Optional[str] = None,
            phase: Optional[str] = None,
            subtitle: Optional[str] = None,
        ) -> str:
            """Atualiza os campos de cabeçalho de uma etapa (não mexe em blocks/notes)."""
            st = _step(idx)
            for k, v in {'num': num, 'title': title, 'phase': phase, 'subtitle': subtitle}.items():
                if v is not None:
                    st[k] = str(v) if k == 'num' else v
            self._log(f"Etapa '{st.get('title')}' atualizada")
            return 'ok'

        def remove_meeting_step(idx: int) -> str:
            """Remove uma etapa da reunião pelo índice."""
            st = _step(idx)
            draft['meeting_structure'].pop(idx)
            self._log(f"Etapa '{st.get('title')}' removida")
            return 'ok'

        def set_step_blocks(step_idx: int, blocks: list[dict]) -> str:
            """Substitui os blocos de uma etapa. blocks: {kind: 'falar'|'ouvir'|'fazer', label, open, points: list[str], close}."""
            st = _step(step_idx)
            st['blocks'] = [_norm_block(b) for b in blocks]
            self._log(f"{len(st['blocks'])} blocos definidos na etapa '{st.get('title')}'")
            return 'ok'

        def set_step_notes(step_idx: int, notes: list[dict]) -> str:
            """Substitui os avisos de uma etapa. notes: {kind: 'alerta'|'pausa'|'pergunta_chave'|'validacao', title, text}."""
            st = _step(step_idx)
            st['notes'] = [_norm_note(n) for n in notes]
            self._log(f"{len(st['notes'])} avisos definidos na etapa '{st.get('title')}'")
            return 'ok'

        def set_special_condition(text: Optional[str]) -> str:
            """Define a condição especial de fechamento. Passe null/None pra remover."""
            draft['special_condition'] = text
            self._log("Condição especial atualizada")
            return 'ok'

        return [
            set_diagnostic_questions,
            add_diagnostic_question,
            remove_diagnostic_question,
            add_objection,
            update_objection,
            remove_objection,
            set_price_presentation,
            set_meeting_structure,
            add_meeting_step,
            update_meeting_step,
            remove_meeting_step,
            set_step_blocks,
            set_step_notes,
            set_special_condition,
        ]

    # ---------- Qualification tools ----------

    def _build_qual_tools(self) -> list:
        draft = self.draft
        draft.setdefault('steps', [])
        draft.setdefault('advance_criteria', [])
        draft.setdefault('disqualification_criteria', [])
        draft.setdefault('profile', 'b2b')
        draft.setdefault('framework', '')

        # Normalizadores — garantem o shape rico (bate com agents/schemas.py
        # QualBlock/QualNote/QualQuestion/QualCard) pro editor e o render do playbook não quebrarem.
        def _norm_question(q: dict) -> dict:
            return {'text': q.get('text') or '', 'branch': q.get('branch') or '', 'note': q.get('note') or ''}

        def _norm_card(c: dict) -> dict:
            return {'title': c.get('title') or '', 'text': c.get('text') or ''}

        def _norm_qblock(b: dict) -> dict:
            kind = b.get('kind') or 'falar'
            if kind not in ('falar', 'ouvir', 'perguntas', 'cards'):
                kind = 'falar'
            pts = b.get('points') or []
            return {
                'kind': kind,
                'label': b.get('label') or '',
                'open': b.get('open') or '',
                'points': [str(p) for p in pts],
                'close': b.get('close') or '',
                'questions': [_norm_question(q) for q in (b.get('questions') or [])],
                'cards': [_norm_card(c) for c in (b.get('cards') or [])],
            }

        def _norm_qnote(n: dict) -> dict:
            kind = n.get('kind') or 'instrucao'
            if kind not in ('instrucao', 'alerta', 'anote', 'stop', 'transicao'):
                kind = 'instrucao'
            return {'kind': kind, 'title': n.get('title') or '', 'text': n.get('text') or ''}

        def _step(idx: int) -> dict:
            steps = draft['steps']
            if idx < 0 or idx >= len(steps):
                raise ValueError(f"idx {idx} fora de range")
            return steps[idx]

        def set_profile(profile: str) -> str:
            """Define o perfil de qualificação. profile = 'b2b' ou 'b2c'."""
            if profile not in ('b2b', 'b2c'):
                raise ValueError("profile deve ser 'b2b' ou 'b2c'")
            draft['profile'] = profile
            self._log(f"Perfil definido como {profile.upper()}")
            return 'ok'

        def set_framework(framework: str) -> str:
            """Define o nome do framework exibido no cheat-sheet (ex 'GPCTBA')."""
            draft['framework'] = framework or ''
            self._log("Framework atualizado")
            return 'ok'

        def set_steps(steps: list[dict]) -> str:
            """Substitui as etapas inteiras do playbook de qualificação.

            Cada step: {num, title, phase, subtitle, gpctba, objective, blocks, notes}.
            - blocks: lista de {kind: 'falar'|'ouvir'|'perguntas'|'cards', label, open, points: list[str],
              close, questions: [{text, branch, note}], cards: [{title, text}]}.
              'falar'/'ouvir' usam open/points/close; 'perguntas' usa questions; 'cards' usa cards.
            - notes: lista de {kind: 'instrucao'|'alerta'|'anote'|'stop'|'transicao', title, text}.
            Use 1 chamada pra montar o playbook todo de uma vez.
            """
            norm = []
            for i, s in enumerate(steps):
                norm.append({
                    'num': str(s.get('num') or f'{i + 1:02d}'),
                    'title': s.get('title') or '',
                    'phase': s.get('phase') or '',
                    'subtitle': s.get('subtitle') or '',
                    'gpctba': s.get('gpctba') or '',
                    'objective': s.get('objective') or '',
                    'blocks': [_norm_qblock(b) for b in (s.get('blocks') or [])],
                    'notes': [_norm_qnote(n) for n in (s.get('notes') or [])],
                })
            draft['steps'] = norm
            self._log(f"{len(norm)} etapas de qualificação definidas")
            return 'ok'

        def add_step(
            num: str,
            title: str,
            phase: str = '',
            subtitle: str = '',
            gpctba: str = '',
            objective: str = '',
        ) -> str:
            """Adiciona uma etapa (sem blocos/notas) ao final. Use set_step_blocks/set_step_notes depois."""
            draft['steps'].append({
                'num': str(num or f"{len(draft['steps']) + 1:02d}"),
                'title': title or '', 'phase': phase or '', 'subtitle': subtitle or '',
                'gpctba': gpctba or '', 'objective': objective or '',
                'blocks': [], 'notes': [],
            })
            self._log(f"Etapa '{title}' adicionada")
            return 'ok'

        def update_step(
            idx: int,
            num: Optional[str] = None,
            title: Optional[str] = None,
            phase: Optional[str] = None,
            subtitle: Optional[str] = None,
            gpctba: Optional[str] = None,
            objective: Optional[str] = None,
        ) -> str:
            """Atualiza os campos de cabeçalho de uma etapa (não mexe em blocks/notes)."""
            st = _step(idx)
            for k, v in {
                'num': num, 'title': title, 'phase': phase, 'subtitle': subtitle,
                'gpctba': gpctba, 'objective': objective,
            }.items():
                if v is not None:
                    st[k] = str(v) if k == 'num' else v
            self._log(f"Etapa '{st.get('title')}' atualizada")
            return 'ok'

        def remove_step(idx: int) -> str:
            """Remove uma etapa do playbook pelo índice."""
            st = _step(idx)
            draft['steps'].pop(idx)
            self._log(f"Etapa '{st.get('title')}' removida")
            return 'ok'

        def set_step_blocks(step_idx: int, blocks: list[dict]) -> str:
            """Substitui os blocos de uma etapa. blocks: {kind: 'falar'|'ouvir'|'perguntas'|'cards', label,
            open, points: list[str], close, questions: [{text, branch, note}], cards: [{title, text}]}."""
            st = _step(step_idx)
            st['blocks'] = [_norm_qblock(b) for b in blocks]
            self._log(f"{len(st['blocks'])} blocos definidos na etapa '{st.get('title')}'")
            return 'ok'

        def set_step_notes(step_idx: int, notes: list[dict]) -> str:
            """Substitui os avisos de uma etapa. notes: {kind: 'instrucao'|'alerta'|'anote'|'stop'|'transicao', title, text}."""
            st = _step(step_idx)
            st['notes'] = [_norm_qnote(n) for n in notes]
            self._log(f"{len(st['notes'])} avisos definidos na etapa '{st.get('title')}'")
            return 'ok'

        def set_advance_criteria(criteria: list[str]) -> str:
            """Substitui a lista de critérios de avanço."""
            draft['advance_criteria'] = list(criteria)
            self._log(f"{len(criteria)} critérios de avanço definidos")
            return 'ok'

        def add_advance_criterion(criterion: str) -> str:
            """Adiciona um critério de avanço."""
            draft['advance_criteria'].append(criterion)
            self._log("Critério de avanço adicionado")
            return 'ok'

        def set_disqualification_criteria(criteria: list[str]) -> str:
            """Substitui a lista de critérios de desqualificação."""
            draft['disqualification_criteria'] = list(criteria)
            self._log(f"{len(criteria)} critérios de desqualificação definidos")
            return 'ok'

        def add_disqualification_criterion(criterion: str) -> str:
            """Adiciona um critério de desqualificação."""
            draft['disqualification_criteria'].append(criterion)
            self._log("Critério de desqualificação adicionado")
            return 'ok'

        return [
            set_profile,
            set_framework,
            set_steps,
            add_step,
            update_step,
            remove_step,
            set_step_blocks,
            set_step_notes,
            set_advance_criteria,
            add_advance_criterion,
            set_disqualification_criteria,
            add_disqualification_criterion,
        ]
