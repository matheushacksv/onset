from onboarding.models import OnboardingForm

def crm_context(data: dict) -> dict:
    """Campos para o agente de CRM: funis, time, cadência, nicho."""
    keys = [
        'nome_empresa', 'nicho', 'produto', 'tipo_venda', 'ticket', 'modelo_venda', 'como_vende',
        'sdr', 'closer', 'especialista', 'perfil_operador',
        'funis',
        'trafego_etapas', 'trafego_isca', 'trafego_plataforma', 'trafego_dias', 'trafego_bot',
        'prosp_etapas', 'prosp_perfil', 'prosp_dias', 'prosp_canais', 'prosp_fonte',
        'social_etapas', 'social_plat', 'social_dias',
        'carteira_etapas', 'carteira_quem', 'cart_freq',
        'posvenda_etapas', 'posvenda_obs',
        'custom_etapas', 'custom_fluxo',
        'perfil_lead', 'dor_principal', 'tom',
        'gatilho_urgencia', 'caso_sucesso',
    ]
    return {k: data[k] for k in keys if k in data}

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