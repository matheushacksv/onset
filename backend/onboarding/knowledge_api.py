import os
import shutil
import tempfile
from typing import cast
from urllib.parse import quote

import boto3
from agno.vectordb.pgvector import PgVector
from decouple import config
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.core.files.storage import default_storage as _raw_storage
from django.db import connection
from django.http import HttpResponse
from django_q.tasks import async_task
from ninja import File, Router, Status
from ninja.files import UploadedFile

from core.errors import Error

from .agents.workflow import get_knowledge
from .schemas import KnowledgeContent, KnowledgeItem, KnowledgeNamesIn

router = Router(tags=['Knowledge'])

KNOWLEDGE_PREFIX = 'knowledge/'

storage = cast(Storage, _raw_storage)


def _vdb() -> PgVector:
    return cast(PgVector, get_knowledge().vector_db)


def _deny(request):
    """Retorna Status 403 se não superuser, senão None"""
    if not request.auth.is_superuser:
        return Status(403, Error(detail='Apenas administradores'))
    return None


def _valid_name(name: str) -> bool:
    return name.endswith('.md') and '/' not in name and '\\' not in name


def _insert_md(name: str, data: bytes) -> None:
    """Indexa um .md no PgVector via arquivo temp (path.name = nome canônico)."""
    tmpdir = tempfile.mkdtemp()
    try:
        tmppath = os.path.join(tmpdir, name)
        with open(tmppath, 'wb') as fh:
            fh.write(data)
        get_knowledge().insert(path=tmppath, skip_if_exists=True)
    finally:
        shutil.rmtree(tmpdir)


def _index_one(name: str) -> None:
    """Baixa o .md do S3 e indexa. Usado pelo index singular e pela task em massa."""
    with storage.open(KNOWLEDGE_PREFIX + name) as f:
        data = f.read()
    _insert_md(name, data)


def _pdf_to_markdown(data: bytes) -> str:
    """Extrai texto de um PDF (pypdf) em parágrafos. Texto puro serve como .md."""
    from io import BytesIO

    from pypdf import PdfReader

    reader = PdfReader(BytesIO(data))
    parts = []
    for page in reader.pages:
        txt = (page.extract_text() or '').strip()
        if txt:
            parts.append(txt)
    return '\n\n'.join(parts).strip()


def _s3():
    """Client boto3 cru + bucket (mesma config do workflow._download_knowledge)."""
    client = boto3.client(
        's3',
        endpoint_url=config('MINIO_ENDPOINT_URL'),
        aws_access_key_id=config('MINIO_ACCESS_KEY'),
        aws_secret_access_key=config('MINIO_SECRET_KEY'),
    )
    return client, config('MINIO_BUCKET_NAME')


def _indexed_names() -> set[str]:
    """Nomes de doc indexados no PgVector — UMA query (DISTINCT name).
    Tabela vive no schema do agno (default 'ai'), não em public."""
    vdb = _vdb()
    schema = getattr(vdb, 'schema', 'ai') or 'ai'
    table = getattr(vdb, 'table_name', 'onboarding_kb')
    with connection.cursor() as c:
        c.execute(f'SELECT DISTINCT name FROM "{schema}"."{table}"')
        return {r[0] for r in c.fetchall()}


@router.get('/', response={200: list[KnowledgeItem], 403: Error})
def list_knowledge(request):
    if deny := _deny(request):
        return deny
    indexed = _indexed_names()
    client, bucket = _s3()
    items = []
    paginator = client.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=bucket, Prefix=KNOWLEDGE_PREFIX):
        for obj in page.get('Contents', []):
            key = obj['Key']
            if not key.endswith('.md'):
                continue
            name = key[len(KNOWLEDGE_PREFIX) :]
            if not name:
                continue
            items.append(
                KnowledgeItem(
                    name=name,
                    size=obj['Size'],
                    updated_at=obj['LastModified'],
                    indexed=name in indexed,
                )
            )
    items.sort(key=lambda i: i.name)
    return items


@router.get('/names', response={200: list[str]})
def knowledge_names(request):
    """Nomes dos docs indexados — fonte do picker de material modelo na geração.
    SEM gate superuser: vendedor precisa escolher template (só auth JWT global)."""
    return sorted(_indexed_names())


@router.get('/content', response={200: KnowledgeContent, 403: Error, 404: Error})
def view_knowledge(request, name: str):
    if deny := _deny(request):
        return deny
    key = KNOWLEDGE_PREFIX + name
    if not _valid_name(name) or not storage.exists(key):
        return Status(404, Error(detail='Material não encontrado'))
    with storage.open(key) as f:
        content = f.read().decode('utf-8', errors='replace')
    return KnowledgeContent(name=name, content=content)


@router.get('/download', response={200: None, 403: Error, 404: Error})
def download_knowledge(request, name: str):
    if deny := _deny(request):
        return deny
    key = KNOWLEDGE_PREFIX + name
    if not _valid_name(name) or not storage.exists(key):
        return Status(404, Error(detail='Material não encontrado'))
    with storage.open(key) as f:
        data = f.read()
    resp = HttpResponse(data, content_type='text/markdown; charset=utf-8')

    ascii_name = name.encode('ascii', 'ignore').decode() or 'material.md'
    resp['Content-Disposition'] = (
        f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{quote(name)}'
    )
    return resp


@router.post(
    '/upload', response={200: KnowledgeItem, 400: Error, 403: Error, 409: Error}
)
def upload_knowledge(request, file: UploadedFile = File()):
    if deny := _deny(request):
        return deny
    src = os.path.basename(file.name or '')
    stem, ext = os.path.splitext(src)
    ext = ext.lower()
    if ext not in ('.md', '.pdf') or not stem:
        return Status(400, Error(detail='Só arquivos .md ou .pdf'))

    raw = file.read()
    if ext == '.pdf':
        try:
            md = _pdf_to_markdown(raw)
        except Exception as e:
            return Status(400, Error(detail=f'Falha ao ler o PDF: {e}'))
        if not md:
            return Status(
                400, Error(detail='PDF sem texto extraível (escaneado/imagem?)')
            )
        data = md.encode('utf-8')
    else:
        data = raw

    name = stem + '.md'
    if not _valid_name(name):
        return Status(400, Error(detail='Nome de arquivo inválido'))

    key = KNOWLEDGE_PREFIX + name
    vec_db = _vdb()
    if storage.exists(key) or vec_db.name_exists(name):
        return Status(
            409, Error(detail='Material já existe. Exclua antes de re-enviar')
        )

    storage.save(key, ContentFile(data))
    _insert_md(name, data)

    try:
        updated = storage.get_modified_time(key)
    except Exception:
        updated = None
    return KnowledgeItem(name=name, size=len(data), updated_at=updated, indexed=True)


@router.post(
    '/index', response={200: KnowledgeItem, 400: Error, 403: Error, 404: Error}
)
def index_knowledge(request, name: str):
    """Indexa um material já no S3 (singular, inline)."""
    if deny := _deny(request):
        return deny
    key = KNOWLEDGE_PREFIX + name
    if not _valid_name(name) or not storage.exists(key):
        return Status(404, Error(detail='Material não encontrado'))
    _index_one(name)
    try:
        updated = storage.get_modified_time(key)
    except Exception:
        updated = None
    return KnowledgeItem(
        name=name, size=storage.size(key), updated_at=updated, indexed=True
    )


@router.post('/index-bulk', response={200: dict, 403: Error})
def index_bulk(request, data: KnowledgeNamesIn):
    """Indexação em massa: enfileira django-q (embedding é lento/caro, não bloqueia o web)."""
    if deny := _deny(request):
        return deny
    names = [n for n in data.names if _valid_name(n)]
    async_task('onboarding.tasks.index_knowledge_task', names)
    return {'queued': len(names)}


@router.post('/unindex', response={200: dict, 403: Error})
def unindex_knowledge(request, data: KnowledgeNamesIn):
    """Tira do índice (singular ou massa). Mantém o .md no S3 — só remove do PgVector."""
    if deny := _deny(request):
        return deny
    vec_db = _vdb()
    n = 0
    for name in data.names:
        if not _valid_name(name):
            continue
        vec_db.delete_by_name(name)
        n += 1
    return {'unindexed': n}


@router.delete('/', response={200: dict, 403: Error, 404: Error})
def delete_knowledge(request, name: str):
    if deny := _deny(request):
        return deny
    key = KNOWLEDGE_PREFIX + name
    vec_db = _vdb()
    if not _valid_name(name) or not (storage.exists(key) or vec_db.name_exists(name)):
        return Status(404, Error(detail='Material não encontrado'))

    vec_db.delete_by_name(name)  # tira chunks do PgVector
    if storage.exists(key):
        storage.delete(key)  # tira MD do S3 (senão deploy re-indexa)
    return {'detail': 'Material excluído'}
