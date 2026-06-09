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

class ClosingMaterial(Schema):
    diagnostic_questions: list[str] = []
    price_presentation: str = ''
    objection_matrix: list[ObjectionRow] = []
    closing_script: str = ''
    special_condition: Optional[str] = None

#* Qualificação
class QualStep(Schema):
    type: Literal['message','question','instruction']
    content: str
    channel: Optional[Literal['whatsapp', 'audio']] = None

class QualificationScript(Schema):
    profile: Optional[Literal['b2b','b2c']] = None
    whatsapp_flow: list[QualStep] = []
    call_pitch: str = ''
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

class MaterialPatchIn(Schema):
    crm: Optional[CRMScript] = None
    closing: Optional[ClosingMaterial] = None
    qualification: Optional[QualificationScript] = None

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