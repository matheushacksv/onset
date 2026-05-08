import asyncio
import json
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector
from decouple import config
from pathlib import Path
from .prompts import VALIDATOR_PROMPT, CRM_PROMPT, CLOSING_PROMPT, QUAL_PROMPT
from .schemas import CRMScript, ClosingMaterial, QualificationScript, GeneratedMaterialResult, QualityAlerts, CRMFunnel
from .contexts_functions import crm_context, closing_context, qual_context, onboarding_to_dict
from agno.tools.knowledge import KnowledgeTools
import tempfile
import shutil
import boto3

#KNOWLEDGE_DIR = (Path(__file__).parent.parent) / 'knowledge'

def _download_knowledge() -> str:
    s3 = boto3.client(
        's3',
        endpoint_url=config('MINIO_ENDPOINT_URL'),
        aws_access_key_id=config('MINIO_ACCESS_KEY'),
        aws_secret_access_key=config('MINIO_SECRET_KEY')
    )
    bucket = config('MINIO_BUCKET_NAME')
    tmpdir = tempfile.mkdtemp()

    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix='knowledge/'):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if key.endswith('.md'):
                filename = key.split('/')[-1]
                s3.download_file(bucket, key, f'{tmpdir}/{filename}')
    return tmpdir

_knowledge: Knowledge | None = None


def _runtime_knowledge() -> Knowledge:
    """Conecta ao PgVector existente. Sem download/insert. Use em runtime."""
    return Knowledge(
        vector_db=PgVector(
            table_name='onboarding_kb',
            db_url=_db_url(),
        )
    )


def get_knowledge() -> Knowledge:
    """Singleton runtime. Assume que `build_knowledge` rodou no deploy."""
    global _knowledge
    if _knowledge is None:
        _knowledge = _runtime_knowledge()
    return _knowledge


def _db_url() -> str:
    try:
        url = config('DATABASE_URL')
    except Exception:
        user     = config('POSTGRES_USER')
        password = config('POSTGRES_PASSWORD')
        host     = config('POSTGRES_HOST', default='localhost')
        port     = config('POSTGRES_PORT', default='5432')
        db       = config('POSTGRES_DB')
        url = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    return url.replace('postgres://', 'postgresql+psycopg://').replace('postgresql://', 'postgresql+psycopg://')


def build_knowledge(recreate: bool = False) -> Knowledge:
    """Deploy-time: baixa MDs do S3 e indexa no PgVector. Idempotente.
    Em runtime use get_knowledge()."""
    knowledge = _runtime_knowledge()

    if recreate:
        knowledge.vector_db.drop()
        knowledge.vector_db.create()

    tmpdir = _download_knowledge()
    try:
        for path in Path(tmpdir).glob('*.md'):
            knowledge.insert(path=str(path), skip_if_exists=True)
    finally:
        shutil.rmtree(tmpdir)

    return knowledge

FUNIL_LABELS = {
    'trafego': 'Tráfego Pago',
    'prospeccao': 'Prospecção Ativa',
    'social': 'Social Selling',
    'carteira': 'Carteira / Reativação',
    'posvenda': 'Pós-venda / Indicação',
    'custom': 'Funil Customizado',
    'default': 'Pipeline'
}


MODEL = OpenAIChat('gpt-5.4-nano', api_key=config('OPENAI_API_KEY'))

class MaterialWorkflow:

    def __init__(self):
        knowledge = get_knowledge()
        
        self.validator = Agent(model=MODEL, instructions=VALIDATOR_PROMPT, knowledge=knowledge, add_knowledge_to_context=True, search_knowledge=True, read_tool_call_history=True, markdown=True, output_schema=QualityAlerts)
        self.crm_agent = Agent(model=MODEL, tools=[KnowledgeTools(num_documents=6)], instructions=CRM_PROMPT, knowledge=knowledge, add_knowledge_to_context=True, search_knowledge=True, read_tool_call_history=True, markdown=True, output_schema=CRMScript)
        self.closing_agent = Agent(model=MODEL, instructions=CLOSING_PROMPT, knowledge=knowledge, add_knowledge_to_context=True, search_knowledge=True, read_tool_call_history=True, markdown=True, output_schema=ClosingMaterial)
        self.qual_agent = Agent(model=MODEL, instructions=QUAL_PROMPT, knowledge=knowledge, add_knowledge_to_context=True, search_knowledge=True, read_tool_call_history=True, markdown=True, output_schema=QualificationScript)

    async def arun(self, onboarding_data: dict) -> GeneratedMaterialResult:
        val_resp = await self.validator.arun(json.dumps(onboarding_data))
        alerts: list[str] = val_resp.content.alerts if val_resp.content else []

        funis: list[str] = onboarding_data.get('funis') or []
        if not funis:
            funis = ['default']

        crm_tasks = [
            self.crm_agent.arun(json.dumps(crm_context(onboarding_data, funil_key=k)))
            for k in funis
        ]

        crm_results, closing, qual = await asyncio.gather(
            asyncio.gather(*crm_tasks),
            self.closing_agent.arun(json.dumps(closing_context(onboarding_data))),
            self.qual_agent.arun(json.dumps(qual_context(onboarding_data)))
        )
        funnels = []
        for key, resp in zip(funis, crm_results):
            stages = resp.content.funnels[0].stages if resp.content.funnels else []
            funnels.append(CRMFunnel(
                key=key,
                name=FUNIL_LABELS.get(key, 'Pipeline'),
                stages=stages
            ))

        return GeneratedMaterialResult(
            crm=CRMScript(funnels=funnels),
            closing=closing.content,
            qualification=qual.content,
            quality_alerts=alerts
        )
