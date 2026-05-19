from onboarding.models import GeneratedMaterial
from typing import Literal
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from weasyprint import HTML

BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / 'assets'
TEMPLATES_DIR = BASE_DIR / 'templates'

_CHANNEL_MAP = {
    'whatsapp': 'whatsapp',
    'ligação': 'ligacao',
    'ligacao': 'ligacao',
    'email': 'email',
    'auto': 'auto',
}

def _channel_slug(value: str) -> str:
    if not value:
        return 'default'
    return _CHANNEL_MAP.get(value.lower(), 'default')

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(['html'])
)
_env.filters['channel_slug'] = _channel_slug

_TEMPLATES = {
    'master': 'master.html',
    'crm': 'crm.html',
    'closing': 'closing.html',
    'qualification': 'qualification.html'
}

Kind = Literal['master', 'crm', 'closing', 'qualification']

def render_material_pdf(material: GeneratedMaterial, kind: Kind, public: bool = False) -> bytes:
    tmpl = _env.get_template(_TEMPLATES[kind])
    onboarding = material.onboarding

    ctx = {
        'material': material,
        'crm': material.crm or {},
        'closing': material.closing or {},
        'qualification': material.qualification or {},
        'deal_name': onboarding.pipedrive_deal_name,
        'assessor_name': getattr(onboarding.assessor, 'first_name', '') or onboarding.assessor.email,
        'generated_at': material.updated_at,
        'kind': kind,
        'public': public,
    }
    html_str = tmpl.render(**ctx)
    return HTML(string=html_str, base_url=str(ASSETS_DIR)).write_pdf()