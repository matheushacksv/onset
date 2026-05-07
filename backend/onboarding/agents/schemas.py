from typing import Optional, Literal
from ninja import Schema
from datetime import datetime

#* CRM
class CadenceAction(Schema):
    channel: Literal['whatsapp','ligação','email','auto']
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

class CRMScript(Schema):
    stages: list[PipelineStage]

#* Fechamento
class ObjectionRow(Schema):
    objection: str
    hidden_concern: str
    counter_script: str

class ClosingMaterial(Schema):
    diagnostic_questions: list[str]
    price_presentation: str
    objection_matrix: list[ObjectionRow]
    closing_script: str
    special_condition: Optional[str] = None

#* Qualificação
class QualStep(Schema):
    type: Literal['message','question','instruction']
    content: str
    channel: Optional[Literal['whatsapp', 'audio']] = None

class QualificationScript(Schema):
    profile: Literal['b2b','b2c']
    whatsapp_flow: list[QualStep]
    call_pitch: str
    advance_criteria: list[str]
    disqualification_criteria: list[str]

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

class MaterialPatchIn(Schema):
    crm: Optional[CRMScript] = None
    closing: Optional[ClosingMaterial] = None
    qualification: Optional[QualificationScript] = None