"""Acesso ao Google Drive via service account com domain-wide delegation.

Todos os assessores estão no mesmo Google Workspace. Uma service account com
delegation autorizada no Admin Console pode impersonar qualquer usuário do
domínio (`with_subject`), sem OAuth interativo nem verificação de app.

Fluxo: gravação do Meet cai no "Meet Recordings" do Drive do assessor; aqui
localizamos por código da reunião e movemos pra pasta compartilhada do cliente.
"""
import json

from decouple import config
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']

# Aceita JSON inline ou caminho de arquivo na env GOOGLE_SA_JSON.
_SA_RAW = config('GOOGLE_SA_JSON', default='')


def _service_account_info() -> dict:
    raw = _SA_RAW.strip()
    if not raw:
        raise RuntimeError('GOOGLE_SA_JSON não configurada')
    if raw.startswith('{'):
        return json.loads(raw)
    with open(raw, 'r', encoding='utf-8') as fh:
        return json.load(fh)


def _drive(owner_email: str):
    """Client Drive impersonando `owner_email` via domain-wide delegation."""
    creds = service_account.Credentials.from_service_account_info(
        _service_account_info(), scopes=SCOPES,
    ).with_subject(owner_email)
    return build('drive', 'v3', credentials=creds, cache_discovery=False)


def find_recording(owner_email: str, meet_code: str) -> str | None:
    """Acha o file_id da gravação do Meet no Drive do assessor.

    Match por nome contendo o código da reunião (ex: 'igf-yfqv-ftd'), só vídeos,
    não-lixeira. Retorna o mais recente ou None se ainda não apareceu.
    """
    drive = _drive(owner_email)
    safe = meet_code.replace("'", "")
    query = (
        f"name contains '{safe}' and trashed = false "
        "and mimeType contains 'video/'"
    )
    resp = drive.files().list(
        q=query,
        spaces='drive',
        fields='files(id, name, parents, createdTime)',
        orderBy='createdTime desc',
        pageSize=10,
        supportsAllDrives=True,
        includeItemsFromAllDrives=True,
    ).execute()
    files = resp.get('files', [])
    return files[0]['id'] if files else None


def move_file(owner_email: str, file_id: str, dest_folder_id: str) -> None:
    """Move o arquivo pra pasta destino: tira os parents atuais, adiciona o destino."""
    drive = _drive(owner_email)
    meta = drive.files().get(
        fileId=file_id, fields='parents', supportsAllDrives=True,
    ).execute()
    prev_parents = ','.join(meta.get('parents', []))
    drive.files().update(
        fileId=file_id,
        addParents=dest_folder_id,
        removeParents=prev_parents,
        fields='id, parents',
        supportsAllDrives=True,
    ).execute()
