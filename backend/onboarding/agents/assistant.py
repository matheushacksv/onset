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


VALID_CHANNELS = {'whatsapp', 'ligação', 'email', 'auto'}


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
            '\n3. Aplique as mudanças USANDO AS TOOLS. Prefira tools que aceitam listas (fill_cadence, set_whatsapp_flow, set_diagnostic_questions, set_advance_criteria) pra fazer mais em 1 chamada.'
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
            days = [{"day": 1, "actions": [{"channel": "whatsapp"|"ligação"|"email"|"auto", "message": "...", "instructions": "..."}]}]
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
        draft.setdefault('closing_script', '')

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

        def set_closing_script(text: str) -> str:
            """Define o script completo de fechamento."""
            draft['closing_script'] = text
            self._log("Script de fechamento atualizado")
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
            set_closing_script,
            set_special_condition,
        ]

    # ---------- Qualification tools ----------

    def _build_qual_tools(self) -> list:
        draft = self.draft
        draft.setdefault('whatsapp_flow', [])
        draft.setdefault('advance_criteria', [])
        draft.setdefault('disqualification_criteria', [])
        draft.setdefault('call_pitch', '')
        draft.setdefault('profile', 'b2b')

        VALID_TYPES = {'message', 'question', 'instruction'}
        VALID_QUAL_CHANNELS = {'whatsapp', 'audio', None}

        def set_profile(profile: str) -> str:
            """Define o perfil de qualificação. profile = 'b2b' ou 'b2c'."""
            if profile not in ('b2b', 'b2c'):
                raise ValueError("profile deve ser 'b2b' ou 'b2c'")
            draft['profile'] = profile
            self._log(f"Perfil definido como {profile.upper()}")
            return 'ok'

        def set_whatsapp_flow(steps: list[dict]) -> str:
            """Substitui o fluxo de WhatsApp inteiro.

            CADA step tem 3 campos distintos — NÃO confunda:
              - type (categoria do passo): "message" (texto pro lead), "question" (pergunta de qualificação), "instruction" (orientação interna pro SDR)
              - content (texto do passo): string com mensagem/pergunta/instrução
              - channel (formato de envio, opcional): "whatsapp" (texto, padrão) ou "audio" (gravação de voz)

            Exemplo: {"type": "message", "content": "Oi!", "channel": "audio"}  -> mensagem em áudio
            ERRADO: {"type": "audio", ...}  -> 'audio' é channel, não type!
            """
            normalized = []
            for s in steps:
                t = s.get('type')
                ch = s.get('channel')
                if t not in VALID_TYPES:
                    raise ValueError(f"type inválido: {t}. Use um de {VALID_TYPES}")
                if ch not in VALID_QUAL_CHANNELS:
                    raise ValueError(f"channel inválido: {ch}")
                normalized.append({'type': t, 'content': s.get('content', ''), 'channel': ch})
            draft['whatsapp_flow'] = normalized
            self._log(f"Fluxo WhatsApp definido com {len(normalized)} passos")
            return 'ok'

        def add_whatsapp_step(
            type: str,
            content: str,
            channel: Optional[str] = None,
            position: Optional[int] = None,
        ) -> str:
            """Adiciona um passo ao fluxo de WhatsApp.
              - type (categoria): "message" | "question" | "instruction"
              - content: texto do passo
              - channel (formato, opcional): "whatsapp" (padrão) | "audio" (mensagem de voz)
              - position: índice (None = adiciona no final)
            'audio' é VALOR de channel, NÃO de type.
            """
            if type not in VALID_TYPES:
                raise ValueError(f"type inválido: {type}")
            if channel not in VALID_QUAL_CHANNELS:
                raise ValueError(f"channel inválido: {channel}")
            step = {'type': type, 'content': content, 'channel': channel}
            flow = draft['whatsapp_flow']
            if position is None:
                flow.append(step)
            else:
                flow.insert(position, step)
            self._log(f"Passo {type} adicionado ao fluxo WhatsApp")
            return 'ok'

        def remove_whatsapp_step(idx: int) -> str:
            """Remove passo do fluxo WhatsApp pelo índice."""
            flow = draft['whatsapp_flow']
            if idx < 0 or idx >= len(flow):
                raise ValueError(f"idx {idx} fora de range")
            flow.pop(idx)
            self._log("Passo WhatsApp removido")
            return 'ok'

        def set_call_pitch(text: str) -> str:
            """Define o pitch de abertura de ligação."""
            draft['call_pitch'] = text
            self._log("Pitch de ligação atualizado")
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
            set_whatsapp_flow,
            add_whatsapp_step,
            remove_whatsapp_step,
            set_call_pitch,
            set_advance_criteria,
            add_advance_criterion,
            set_disqualification_criteria,
            add_disqualification_criterion,
        ]
