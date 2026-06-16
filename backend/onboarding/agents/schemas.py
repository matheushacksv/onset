from typing import Optional, Literal
from ninja import Schema
from datetime import datetime

#* CRM
# Canais válidos de cadência. Fonte ÚNICA — importado por tasks.py (sanitize do CRM gerado)
# e assistant.py (validação das tools do chat). Bate com o <select> do front.
CANONICAL_CHANNELS = {'whatsapp', 'ligacao', 'email', 'sms', 'atividade'}


class CadenceAction(Schema):
    # Canônico: whatsapp | ligacao | email | sms | atividade (bate com o <select> do front
    # e CANONICAL_CHANNELS em tasks.py). str (não Literal) pra não quebrar a leitura de
    # materiais legados que tenham valor fora do conjunto; o sanitize no save normaliza.
    channel: str
    message: str
    instructions: Optional[str] = None

class CadenceDay(Schema):
    day: int
    actions: list[CadenceAction]

class PipelineStage(Schema):
    name: str
    objective: str
    dev_instructions: str
    cadence: list[CadenceDay]
    advance_criteria: str
    loss_reason: Optional[str] = None

class CRMFunnel(Schema):
    key: str
    name: str
    stages: list[PipelineStage] = []

class CRMScript(Schema):
    funnels: list[CRMFunnel] = []

#* Fechamento
class ObjectionRow(Schema):
    objection: str
    hidden_concern: str
    counter_script: str

class MeetingBlock(Schema):
    kind: Literal['falar', 'ouvir', 'fazer'] = 'falar'
    label: str = ''
    open: str = ''
    points: list[str] = []
    close: str = ''

class MeetingNote(Schema):
    kind: Literal['alerta', 'pausa', 'pergunta_chave', 'validacao'] = 'alerta'
    title: str = ''
    text: str = ''

class MeetingStep(Schema):
    num: str
    title: str
    phase: str = ''
    subtitle: str = ''
    blocks: list[MeetingBlock] = []
    notes: list[MeetingNote] = []

class ClosingMaterial(Schema):
    diagnostic_questions: list[str] = []
    price_presentation: str = ''
    objection_matrix: list[ObjectionRow] = []
    meeting_structure: list[MeetingStep] = []
    closing_script: str = ''
    special_condition: Optional[str] = None

#* Qualificação — Playbook rico (espelha ClosingMaterial.meeting_structure)
class QualQuestion(Schema):
    text: str = ''            # pergunta (badge P)
    branch: str = ''          # follow-up condicional ("se só 1: ...")
    note: str = ''            # marca ANOTE / "pergunta de ouro"

class QualCard(Schema):       # cards se-X / se-Y (2 colunas)
    title: str = ''           # ex "SE CONFIRMAR INTERESSE"
    text: str = ''

class QualBlock(Schema):
    kind: Literal['falar', 'ouvir', 'perguntas', 'cards'] = 'falar'
    label: str = ''
    open: str = ''            # falar/ouvir
    points: list[str] = []    # falar/ouvir
    close: str = ''           # falar/ouvir
    questions: list[QualQuestion] = []   # perguntas
    cards: list[QualCard] = []           # cards

class QualNote(Schema):
    kind: Literal['instrucao', 'alerta', 'anote', 'stop', 'transicao'] = 'instrucao'
    title: str = ''
    text: str = ''

class QualPlaybookStep(Schema):
    num: str = ''
    title: str = ''
    phase: str = ''           # ex "Conexão", "Diagnóstico" (agrupa + colore)
    subtitle: str = ''        # ex "DIAGNÓSTICO · GOALS"
    gpctba: str = ''          # letra G/P/C/T/B/A (chip canto, opcional)
    objective: str = ''       # banda OBJETIVO (sempre exibida)
    blocks: list[QualBlock] = []
    notes: list[QualNote] = []

class QualificationScript(Schema):
    profile: Optional[Literal['b2b','b2c']] = None
    framework: str = ''                        # ex "GPCTBA" (label cheat-sheet)
    steps: list[QualPlaybookStep] = []         # playbook rico
    advance_criteria: list[str] = []
    disqualification_criteria: list[str] = []

class QualityAlerts(Schema):
    alerts: list[str] = []

#* Output consolidado
class GeneratedMaterialResult(Schema):
    crm: CRMScript
    closing: ClosingMaterial
    qualification: QualificationScript
    quality_alerts: list[str]

class MaterialOut(Schema):
    id: int
    status: str
    crm: Optional[CRMScript] = None
    closing: Optional[ClosingMaterial] = None
    qualification: Optional[QualificationScript] = None
    quality_alerts: list[str] = []
    error: str = ''
    created_at: datetime
    published: bool = False
    published_at: Optional[datetime] = None
    theme: str = 'warm'

class MaterialPatchIn(Schema):
    crm: Optional[CRMScript] = None
    closing: Optional[ClosingMaterial] = None
    qualification: Optional[QualificationScript] = None
    theme: Optional[str] = None

#* ----- Assistant -----

class AssistantFocus(Schema):
    funnel_key: Optional[str] = None
    stage_idx: Optional[int] = None
    day: Optional[int] = None

class AssistantHistoryMessage(Schema):
    role: Literal['user', 'assistant']
    content: str

class AssistantIn(Schema):
    section: Literal['crm', 'closing', 'qualification']
    message: str
    focus: Optional[AssistantFocus] = None
    history: list[AssistantHistoryMessage] = []

class AssistantOut(Schema):
    message: str
    section: str
    value: dict
    changes: list[str]

class ScriptSuggestionOut(Schema):
    wpp_perguntas: str
    wpp_criterio: str
    wpp_desqualifica: str
    wpp_proximo: str
    lig_pitch: str
    lig_perguntas: str
    lig_objecoes: str