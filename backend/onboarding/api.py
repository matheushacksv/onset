from django_q.tasks import async_task
from ninja import Router, Status
from .models import OnboardingForm
from .schemas import DealOut, OnboardingStepIn, OnboardingOut, OnboardingCreateIn, MaterialLibraryItemOut, DevMaterialDetailOut
from .agents.schemas import MaterialOut, MaterialPatchIn, AssistantIn, AssistantOut
from .agents.assistant import AssistantSession
from .pipedrive_services import list_deals, update_deal, create_note
from core.errors import Error
from django.shortcuts import get_object_or_404
from .models import GeneratedMaterial
from django.utils import timezone

router = Router(tags=['Onboarding'])

def _is_desenvolvedor(user) -> bool:
    return user.groups.filter(name='Desenvolvedor').exists() and not user.is_superuser

def _build_note(o: OnboardingForm) -> str:
    def v(value) -> str:
        """Retorna o valor ou traço se vazio."""
        if value is None or value == '' or value == []:
            return '—'
        return str(value)

    def lst(items: list) -> str:
        """Formata lista simples separada por vírgula."""
        if not items:
            return '—'
        return ', '.join(str(i) for i in items)

    def etapas(items: list) -> str:
        """Formata etapas do funil em sequência."""
        if not items:
            return '—'
        labels = []
        for item in items:
            if isinstance(item, dict):
                labels.append(item.get('label') or item.get('nome') or str(item))
            else:
                labels.append(str(item))
        return ' → '.join(labels)

    def encontros(items: list) -> str:
        """Formata lista de encontros agendados."""
        if not items:
            return '—'
        lines = []
        for item in items:
            if isinstance(item, dict):
                parts = [str(val) for val in item.values() if val]
                lines.append(', '.join(parts))
            else:
                lines.append(str(item))
        return '\n  ' + '\n  '.join(lines)

    lines = [
        f'# Onboarding — {o.pipedrive_deal_name}',
        '',
        '## Negócio',
        f'Empresa: {v(o.nome_empresa)}',
        f'Nicho: {v(o.nicho)}',
        f'Produto/serviço: {v(o.produto)}',
        f'Tipo de venda: {v(o.tipo_venda)}',
        f'Ticket médio: {v(o.ticket)}',
        f'Modelo de cobrança: {v(o.modelo_venda)}',
        f'Como vende hoje: {v(o.como_vende)}',
        f'Cross-sell / upsell: {v(o.crosssell)}',
        f'Vendas mensais (atual / meta): {v(o.vendas_atual)} / {v(o.vendas_meta)}',
        f'Faturamento mensal (atual / meta): {v(o.fat_atual)} / {v(o.fat_meta)}',
        f'Volume de leads/mês: {v(o.volume_leads)}',
        f'Funcionários: {v(o.funcionarios)}',
        '',
        '### Infraestrutura comercial',
        f'Entrada de leads no CRM: {v(o.entrada_crm)}',
        f'Integrações: {v(o.integracoes)}',
        f'Follow-up estruturado: {v(o.followup_estruturado)}',
        f'Gravações disponíveis: {v(o.gravacoes)}',
        '',
        '## Lead',
        f'Perfil ICP: {v(o.perfil_lead)}',
        f'Dor principal: {v(o.dor_principal)}',
        f'Objeções conhecidas: {v(o.objecoes)}',
        f'Tom de comunicação: {lst(o.tom)}',
        f'Caso de sucesso: {v(o.caso_sucesso)}',
        f'Gatilho de urgência: {v(o.gatilho_urgencia)}',
        '',
        '## Funis ativos',
        f'{lst(o.funis)}',
    ]

    # Detalhes de cada funil ativo
    funil_detalhes = {
        'trafego': ('Tráfego Pago', [
            ('Etapas', etapas(o.trafego_etapas)),
            ('Isca / lead magnet', v(o.trafego_isca)),
            ('Plataforma', v(o.trafego_plataforma)),
            ('Dias no funil', v(o.trafego_dias)),
            ('Bot / automação', v(o.trafego_bot)),
        ]),
        'prosp': ('Prospecção Ativa', [
            ('Etapas', etapas(o.prosp_etapas)),
            ('Perfil alvo', v(o.prosp_perfil)),
            ('Dias no funil', v(o.prosp_dias)),
            ('Canais', lst(o.prosp_canais)),
            ('Fonte de lista', v(o.prosp_fonte)),
        ]),
        'social': ('Social Orgânico', [
            ('Etapas', etapas(o.social_etapas)),
            ('Plataforma', v(o.social_plat)),
            ('Dias no funil', v(o.social_dias)),
        ]),
        'carteira': ('Carteira', [
            ('Etapas', etapas(o.carteira_etapas)),
            ('Responsável', v(o.carteira_quem)),
            ('Frequência de contato', v(o.cart_freq)),
        ]),
        'posvenda': ('Pós-venda', [
            ('Etapas', etapas(o.posvenda_etapas)),
            ('Observações', v(o.posvenda_obs)),
        ]),
        'custom': ('Funil Personalizado', [
            ('Etapas', etapas(o.custom_etapas)),
            ('Descrição do fluxo', v(o.custom_fluxo)),
        ]),
    }

    for key, (titulo, campos) in funil_detalhes.items():
        if key in (o.funis or []):
            lines.append('')
            lines.append(f'### {titulo}')
            for label, valor in campos:
                lines.append(f'{label}: {valor}')

    lines += [
        '',
        '## Time',
        f'SDR: {v(o.sdr)}',
        f'Closer: {v(o.closer)}',
        f'Especialista: {v(o.especialista)}',
        f'Empresa de scripts: {v(o.empresa_scripts)}',
        f'Perfil do operador: {v(o.perfil_operador)}',
        f'Etapas de fechamento: {etapas(o.etapas_fechamento)}',
        f'Fechamento específico: {v(o.fech_especifico)}',
        f'Tipo de reunião: {v(o.tipo_reuniao)}',
        f'Passagem SDR → Closer: {v(o.passagem)}',
        f'Apresentação de preço: {v(o.apresenta_preco)}',
        f'Método de vendas: {lst(o.metodo)}',
        f'Condição especial: {v(o.condicao_especial)}',
        f'Objeções no fechamento: {v(o.objecoes_fecha)}',
        '',
        '## Scripts',
        '',
        '### Qualificação WhatsApp',
        f'Perguntas: {v(o.wpp_perguntas)}',
        f'Critério de qualificação: {v(o.wpp_criterio)}',
        f'Critério de desqualificação: {v(o.wpp_desqualifica)}',
        f'Próximo passo: {v(o.wpp_proximo)}',
        '',
        '### Ligação',
        f'Pitch: {v(o.lig_pitch)}',
        f'Perguntas: {v(o.lig_perguntas)}',
        f'Objeções: {v(o.lig_objecoes)}',
        '',
        '### Fechamento',
        f'Estrutura: {v(o.fech_estrutura)}',
        f'Particularidades: {v(o.particularidades)}',
        f'Usa referência de cliente: {v(o.tem_ref)}',
        f'Referência: {v(o.ref_cliente)}',
        '',
        '## Datas',
        f'Plano: {v(o.plano_selecionado)}',
        f'Assessorias: {encontros(o.assessorias)}',
        f'Encontros CS: {encontros(o.cs_encontros)}',
        f'Encontros bônus: {encontros(o.bonus_encontros)}',
        '',
        '## Pesquisa',
        f'Fonte de conteúdo: {v(o.fonte_conteudo)}',
        f'Como descobriu a empresa: {v(o.como_descobriu)}',
        f'Decisivo na prospecção: {lst(o.decisivo_prospeccao)}',
        f'Experiência na reunião: {lst(o.experiencia_reuniao)}',
        f'Indicador de sucesso: {v(o.indicador_sucesso)}',
    ]

    return '\n'.join(lines)


@router.get('/dev/materials', response={200: list[MaterialLibraryItemOut], 403: Error})
def list_materials_to_dev(request):
    if not _is_desenvolvedor(request.auth) and not request.auth.is_superuser:
        return Status(403, Error(detail='Não autorizado'))
    return (
        OnboardingForm.objects
        .filter(material__status=GeneratedMaterial.Status.COMPLETE, material__published=True)
        .select_related('assessor', 'material')
        .order_by('-material__published_at')
    )


@router.get('/dev/materials/{onboarding_id}', response={200: DevMaterialDetailOut, 403: Error, 404: Error})
def get_materials_to_dev(request, onboarding_id: int):
    if not _is_desenvolvedor(request.auth) and not request.auth.is_superuser:
        return Status(403, Error(detail='Não autorizado'))
    return get_object_or_404(
        OnboardingForm.objects.select_related('assessor', 'material'),
        id=onboarding_id,
        material__status=GeneratedMaterial.Status.COMPLETE,
        material__published=True,
    )


@router.get('/deals/', response={200: list[DealOut], 400: Error})
def list_onboarding_deals(request):
    try:
        deals = list_deals()
    except Exception as e:
        return Status(400, Error(detail=f'Erro ao buscar deals: {e}'))
    return Status(200, deals)

@router.get('', response={200: list[OnboardingOut]})
def list_onboardings(request):
    if request.auth.is_superuser or _is_desenvolvedor(request.auth):
        qs = OnboardingForm.objects.select_related('assessor').prefetch_related('material').all()
    else:
        qs = OnboardingForm.objects.select_related('assessor').prefetch_related('material').filter(assessor=request.auth)

    return Status(200, list(qs))

@router.post('', response={200: OnboardingOut, 403: Error, 409: Error})
def create_onboarding(request, data: OnboardingCreateIn):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))

    if OnboardingForm.objects.filter(pipedrive_deal_id=data.pipedrive_deal_id).exists():
        return Status(409, Error(detail='Já existe um onboarding para este deal'))

    onboarding = OnboardingForm.objects.create(
        pipedrive_deal_id=data.pipedrive_deal_id,
        pipedrive_deal_name=data.pipedrive_deal_name,
        assessor=request.auth
    )
    return Status(200, onboarding)

@router.get('/{id}', response={200: OnboardingOut, 404: Error})
def get_onboarding(request, id: int):
    onboarding = get_object_or_404(OnboardingForm, id=id)
    return Status(200, onboarding)

@router.patch('/{id}', response={200: OnboardingOut, 403: Error, 404: Error})
def update_onboarding(request, id: int, data: OnboardingStepIn):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    onboarding = get_object_or_404(OnboardingForm, id=id)
    fields = data.model_dump(exclude_none=True)
    for field, value in fields.items():
        setattr(onboarding, field, value)
    onboarding.save()
    return Status(200, onboarding)

@router.post('/{id}/submit', response={200: OnboardingOut, 400: Error, 403: Error, 404: Error})
def submit_onboarding(request, id: int):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    onboarding = get_object_or_404(OnboardingForm, id=id)

    try:
        create_note(
            deal_id=onboarding.pipedrive_deal_id,
            content=_build_note(onboarding)
        )
    except Exception as e:
        return Status(400, Error(detail=f'Erro ao sincronizar com Pipedrive: {e}'))

    onboarding.status = OnboardingForm.Status.SYNCED
    onboarding.save()
    return Status(200, onboarding)

@router.delete('/{id}', response={204: None, 403: Error, 404: Error})
def delete_draft_onboarding(request, id: int):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    try:
        OnboardingForm.objects.get(id=id).delete()
    except Exception as e:
        return Status(404, Error(detail=f'Erro ao deletar rascunho: {e}'))

    return Status(204, None)

#* ----- Material -----

@router.post('/{id}/generate', response={200: MaterialOut, 202: MaterialOut, 400: Error, 403: Error})
def generate_materials(request, id: int):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    onboarding = get_object_or_404(OnboardingForm, id=id)

    material, created = GeneratedMaterial.objects.get_or_create(onboarding=onboarding)

    if not created and material.status == 'complete':
        return Status(200, material)
    material.status = 'pending'
    material.save(update_fields=['status', 'error'])
    async_task('onboarding.tasks.generate_materials_task', onboarding.id)
    return Status(202, material)

@router.get('/{id}/materials', response={200: MaterialOut, 404: Error})
def get_materials(request, id: int):
    material = get_object_or_404(GeneratedMaterial, onboarding_id=id)
    return Status(200, material)

@router.patch('/{id}/materials', response={200: MaterialOut, 403: Error, 404: Error})
def update_materials(request, id: int, data: MaterialPatchIn):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    material = get_object_or_404(GeneratedMaterial, onboarding_id=id)
    fields = data.model_dump(exclude_none=True)

    for field, value in fields.items():
        setattr(material, field, value)
    material.save()
    return Status(200, material)


#* ---- Manual Material ----

@router.post('/{onboarding_id}/materials/manual', response={201: MaterialOut, 400: Error})
def create_manual_material(request, onboarding_id: int):
    onboarding = get_object_or_404(OnboardingForm, id=onboarding_id, assessor=request.auth)

    if hasattr(onboarding, 'material'):
        return Status(400, Error(detail='Material já existe'))
    
    material = GeneratedMaterial.objects.create(
        onboarding=onboarding,
        status=GeneratedMaterial.Status.COMPLETE,
        crm={'funnels': []},
        closing={
            'diagnostic_questions': [],
            'price_presentation': '',
            'objection_matrix': [],
            'closing_script': ''
        },
        qualification={
            'profile': 'b2b',
            'whatsapp_flow': [],
            'call_pitch': '',
            'advance_criteria': [],
            'disqualification_criteria': []
        }
    )
    return Status(201, material)

@router.post('/{onboarding_id}/materials/copy-from/{source_id}', response={201: MaterialOut, 400: Error, 401: Error})
def copy_material(request, onboarding_id: int, source_id: int):
    onboarding_target = get_object_or_404(OnboardingForm, id=onboarding_id, assessor=request.auth)
    onboarding_source = get_object_or_404(OnboardingForm, id=source_id)

    if hasattr(onboarding_target, 'material'):
        return Status(400, Error(detail='Material já existe'))
    
    if not hasattr(onboarding_source, 'material') or onboarding_source.material.status != GeneratedMaterial.Status.COMPLETE:
        return Status(401, Error(detail='Onboarding de origem não existe material completo'))
    
    source_material = onboarding_source.material
    material = GeneratedMaterial.objects.create(
        onboarding=onboarding_target,
        status=GeneratedMaterial.Status.COMPLETE,
        crm=source_material.crm, closing=source_material.closing, qualification=source_material.qualification
    )
    return Status(201, material)

@router.post('/{onboarding_id}/materials/assist/prepare', response={202: dict, 400: Error, 403: Error, 404: Error})
def prepare_assistant(request, onboarding_id: int):
    """Dispara prewarm em background pra popular cache OpenAI. Fire-and-forget."""
    from django.core.cache import cache
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    onboarding = get_object_or_404(OnboardingForm, id=onboarding_id)
    if not request.auth.is_superuser and onboarding.assessor_id != request.auth.id:
        return Status(403, Error(detail='Acesso negado'))
    if not hasattr(onboarding, 'material') or onboarding.material.status != GeneratedMaterial.Status.COMPLETE:
        return Status(400, Error(detail='Material indisponível'))

    # debounce: 1 task por material a cada 10 min
    cache_key = f'assistant_warmed:{onboarding.material.id}'
    if cache.get(cache_key):
        return Status(202, {'status': 'already_warm'})
    cache.set(cache_key, True, timeout=600)
    async_task(
        'onboarding.tasks.prewarm_assistant_task',
        onboarding.material.id,
        q_options={'timeout': 300, 'retry': 600},
    )
    return Status(202, {'status': 'warming'})


@router.post('/{onboarding_id}/materials/assist', response={200: AssistantOut, 400: Error, 403: Error, 404: Error})
def assist_material(request, onboarding_id: int, payload: AssistantIn):
    if _is_desenvolvedor(request.auth):
        return Status(403, Error(detail='Acesso negado'))
    onboarding = get_object_or_404(OnboardingForm, id=onboarding_id)
    if not request.auth.is_superuser and onboarding.assessor_id != request.auth.id:
        return Status(403, Error(detail='Acesso negado'))
    if not hasattr(onboarding, 'material') or onboarding.material.status != GeneratedMaterial.Status.COMPLETE:
        return Status(400, Error(detail='Material indisponível'))

    session = AssistantSession(
        material=onboarding.material,
        section=payload.section,
        focus=payload.focus.dict() if payload.focus else None,
    )
    result = session.run(
        message=payload.message,
        history=[m.dict() for m in payload.history],
    )
    return Status(200, result)


@router.get('/materials/library', response=list[MaterialLibraryItemOut])
def list_materials(request):
    return OnboardingForm.objects.filter(
        material__status=GeneratedMaterial.Status.COMPLETE
    ).select_related('assessor').order_by('-updated_at')

@router.post('/{onboarding_id}/materials/publish', response={200: MaterialOut, 400: Error, 403: Error, 404: Error})
def publish_material(request, onboarding_id: int):
    qs = OnboardingForm.objects.select_related('material')
    if not request.auth.is_superuser:
        qs = qs.filter(assessor=request.auth)
    onboarding = get_object_or_404(qs, id=onboarding_id)
    material = getattr(onboarding, 'material', None)
    if material is None or material.status != GeneratedMaterial.Status.COMPLETE:
        return Status(400, Error(detail='Material indisponível'))

    material.published = not material.published
    material.published_at = timezone.now() if material.published else None
    material.save(update_fields=['published', 'published_at', 'updated_at'])

    return Status(200, material)


