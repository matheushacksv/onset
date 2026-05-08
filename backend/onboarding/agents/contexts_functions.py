from onboarding.models import OnboardingForm

FUNIL_LABELS = {
    'trafego': 'Tráfego Pago',
    'prospeccao': 'Prospecção Ativa',
    'social': 'Social Selling',
    'carteira': 'Carteira / Reativação',
    'posvenda': 'Pós-venda / Indicação',
    'custom': 'Funil Customizado',
    'default': 'Pipeline',
}

def crm_context(data: dict, funil_key: str = 'default') -> dict:
    """Campos para o agente de CRM: 1 funil específico + contexto de negócio/lead."""
    base_keys = [
        'nome_empresa', 'nicho', 'produto', 'tipo_venda', 'ticket', 'modelo_venda', 'como_vende',
        'sdr', 'closer', 'especialista', 'perfil_operador',
        'perfil_lead', 'dor_principal', 'tom',
        'gatilho_urgencia', 'caso_sucesso',
    ]
    base = {k: data[k] for k in base_keys if k in data}

    funil_specific = {
        'trafego': {
            'isca': data.get('trafego_isca'),
            'plataforma': data.get('trafego_plataforma'),
            'dias': data.get('trafego_dias'),
            'bot': data.get('trafego_bot'),
            'etapas': data.get('trafego_etapas'),
        },
        'prospeccao': {
            'perfil': data.get('prosp_perfil'),
            'dias': data.get('prosp_dias'),
            'canais': data.get('prosp_canais'),
            'fonte': data.get('prosp_fonte'),
            'etapas': data.get('prosp_etapas'),
        },
        'social': {
            'plataforma': data.get('social_plat'),
            'dias': data.get('social_dias'),
            'etapas': data.get('social_etapas'),
        },
        'carteira': {
            'quem': data.get('carteira_quem'),
            'frequencia': data.get('cart_freq'),
            'etapas': data.get('carteira_etapas'),
        },
        'posvenda': {
            'observacoes': data.get('posvenda_obs'),
            'etapas': data.get('posvenda_etapas'),
        },
        'custom': {
            'fluxo': data.get('custom_fluxo'),
            'etapas': data.get('custom_etapas'),
        },
    }.get(funil_key, {})

    return {
        **base,
        'funil': {
            'key': funil_key,
            'name': FUNIL_LABELS.get(funil_key, 'Pipeline'),
            **funil_specific,
        },
    }

def closing_context(data: dict) -> dict:
     """Campos para o agente de fechamento: closer, objeções, método, gatilhos."""
     keys = [
         'nome_empresa', 'nicho', 'produto', 'tipo_venda', 'ticket', 'modelo_venda',
         'closer', 'especialista',
         'perfil_lead', 'dor_principal', 'objecoes',
         'caso_sucesso', 'gatilho_urgencia', 'tom',
         'metodo', 'tipo_reuniao', 'apresenta_preco', 'condicao_especial', 'objecoes_fecha',
         'fech_estrutura', 'etapas_fechamento', 'fech_especifico', 'passagem',
     ]
     return {k: data[k] for k in keys if k in data}

def qual_context(data: dict) -> dict:
    """Campos para o agente de qualificação: SDR, perguntas, perfil lead."""
    keys = [
        'nome_empresa', 'nicho', 'produto', 'tipo_venda',
        'sdr', 'closer',
        'perfil_lead', 'dor_principal', 'objecoes', 'tom',
        'caso_sucesso', 'gatilho_urgencia',
        'wpp_perguntas', 'wpp_criterio', 'wpp_desqualifica', 'wpp_proximo',
        'lig_pitch', 'lig_perguntas', 'lig_objecoes',
    ]
    return {k: data[k] for k in keys if k in data}

def onboarding_to_dict(onboarding: OnboardingForm) -> dict:
    '''Conversão do model Django em dict para workflow'''
    from onboarding.schemas import OnboardingOut
    return OnboardingOut.from_orm(onboarding).model_dump(mode='json')