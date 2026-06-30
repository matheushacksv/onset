import asyncio
import json
import re
import shutil
import tempfile
from pathlib import Path

import boto3
from agno.agent import Agent
from agno.knowledge import Knowledge
from agno.models.openai import OpenAIChat
from agno.tools.knowledge import KnowledgeTools
from agno.vectordb.pgvector import PgVector
from decouple import config

from .contexts_functions import (
    closing_context,
    crm_context,
    onboarding_to_dict,
    qual_context,
)
from .prompts import CLOSING_PROMPT, CRM_PROMPT, QUAL_PROMPT, VALIDATOR_PROMPT
from .schemas import (
    ClosingMaterial,
    CRMFunnel,
    CRMScript,
    GeneratedMaterialResult,
    QualificationScript,
    QualityAlerts,
)

# KNOWLEDGE_DIR = (Path(__file__).parent.parent) / 'knowledge'


def _download_knowledge() -> str:
    s3 = boto3.client(
        's3',
        endpoint_url=config('MINIO_ENDPOINT_URL'),
        aws_access_key_id=config('MINIO_ACCESS_KEY'),
        aws_secret_access_key=config('MINIO_SECRET_KEY'),
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
        max_results=5,
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
        user = config('POSTGRES_USER')
        password = config('POSTGRES_PASSWORD')
        host = config('POSTGRES_HOST', default='localhost')
        port = config('POSTGRES_PORT', default='5432')
        db = config('POSTGRES_DB')
        url = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    return url.replace('postgres://', 'postgresql+psycopg://').replace(
        'postgresql://', 'postgresql+psycopg://'
    )


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
    'default': 'Pipeline',
}


# temperatura no default (não setar baixa): o retry em _arun_clean precisa de variância —
# re-roll só limpa o \x7f se sair diferente. temperatura baixa re-produz o mesmo \x7f e só
# desperdiça o re-run. Default = retry efetivo (conserta no 1º re-roll) + sem custo extra.
MODEL = OpenAIChat('gpt-5.4-nano', api_key=config('OPENAI_API_KEY'))


# gpt-5.4-nano às vezes emite chars de controle (ex.: \x7f no lugar de acento) — quirk de
# sampling no output de texto, não-determinístico. Vira tofu no PDF. Detecta p/ re-rodar o
# agent (uma geração nova costuma vir limpa). C0 (exceto \t\n\r), DEL e C1.
_CTRL_RE = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]')


def _has_ctrl(content) -> bool:
    if content is None:
        return False
    try:
        s = json.dumps(content.model_dump(), ensure_ascii=False, default=str)
    except Exception:
        s = str(content)
    return bool(_CTRL_RE.search(s))


async def _arun_clean(agent: Agent, payload: str, attempts: int = 2):
    """Roda o agent; se o output tiver chars de controle, re-roda até `attempts` vezes.
    Retorna a primeira resposta limpa (ou a última tentativa se nenhuma limpar).
    attempts baixo de propósito: cada re-roll soma latência e a task tem timeout (Q_CLUSTER).
    O strip em tasks._strip_ctrl é a rede de segurança final se o re-roll não limpar."""
    resp = await agent.arun(payload)
    for _ in range(attempts - 1):
        if not _has_ctrl(resp.content):
            return resp
        resp = await agent.arun(payload)
    return resp


def _with_template(ctx: dict, template: dict | None, section: str) -> dict:
    """Injeta o material modelo no context do agente (mesmo padrão de campo-extra que
    `particularidades_funil`). `modelo` = JSON da seção de um material pronto; `modelo_referencia`
    = texto cru de um doc do knowledge. None = sem modelo (input idêntico ao comportamento atual)."""
    if not template:
        return ctx
    if template.get('reference_text'):
        ctx['modelo_referencia'] = template['reference_text']
    elif template.get(section):
        ctx['modelo'] = template[section]
    return ctx


class MaterialWorkflow:
    def __init__(self):
        knowledge = get_knowledge()

        # Validator só audita o INPUT do form (campos preenchidos/qualidade) contra critérios
        # fixos do prompt — não precisa de knowledge (KB é exemplo de script, irrelevante aqui).
        # Sem search_knowledge → 1 call só, não um loop agêntico. Grande economia de tempo.
        self.validator = Agent(
            model=MODEL,
            instructions=VALIDATOR_PROMPT,
            markdown=True,
            output_schema=QualityAlerts,
        )
        self.crm_agent = Agent(
            model=MODEL,
            instructions=CRM_PROMPT,
            knowledge=knowledge,
            add_knowledge_to_context=True,
            search_knowledge=False,
            markdown=True,
            output_schema=CRMScript,
        )
        self.closing_agent = Agent(
            model=MODEL,
            instructions=CLOSING_PROMPT,
            knowledge=knowledge,
            add_knowledge_to_context=True,
            search_knowledge=False,
            markdown=True,
            output_schema=ClosingMaterial,
        )
        self.qual_agent = Agent(
            model=MODEL,
            instructions=QUAL_PROMPT,
            knowledge=knowledge,
            add_knowledge_to_context=True,
            search_knowledge=False,
            markdown=True,
            output_schema=QualificationScript,
        )

    async def arun(
        self, onboarding_data: dict, template: dict | None = None
    ) -> GeneratedMaterialResult:
        funis: list[str] = onboarding_data.get('funis') or []
        if not funis:
            funis = ['default']

        # Com modelo, o CRM segue a estrutura/estilo do `modelo`/`modelo_referencia` no input —
        # o RAG amplo (5 docs/funil) só dilui. Desliga só no CRM; closing/qual mantêm os exemplos
        # do KB. Workflow é instanciado por task, então mutar o agent aqui é seguro.
        if template:
            self.crm_agent.add_knowledge_to_context = False

        crm_tasks = [
            _arun_clean(
                self.crm_agent,
                json.dumps(
                    _with_template(
                        crm_context(onboarding_data, funil_key=k), template, 'crm'
                    )
                ),
            )
            for k in funis
        ]

        # Validator roda EM PARALELO com os content agents — seu output (alerts) é
        # independente, não alimenta crm/closing/qual. Antes serializava antes de tudo.
        val_resp, crm_results, closing, qual = await asyncio.gather(
            self.validator.arun(json.dumps(onboarding_data)),
            asyncio.gather(*crm_tasks),
            _arun_clean(
                self.closing_agent,
                json.dumps(
                    _with_template(closing_context(onboarding_data), template, 'closing')
                ),
            ),
            _arun_clean(
                self.qual_agent,
                json.dumps(
                    _with_template(
                        qual_context(onboarding_data), template, 'qualification'
                    )
                ),
            ),
        )
        alerts: list[str] = val_resp.content.alerts if val_resp.content else []
        funnels = []
        for key, resp in zip(funis, crm_results):
            stages = resp.content.funnels[0].stages if resp.content.funnels else []
            funnels.append(
                CRMFunnel(
                    key=key, name=FUNIL_LABELS.get(key, 'Pipeline'), stages=stages
                )
            )

        return GeneratedMaterialResult(
            crm=CRMScript(funnels=funnels),
            closing=closing.content,
            qualification=qual.content,
            quality_alerts=alerts,
        )
