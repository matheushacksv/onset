from ninja import Schema
from typing import Optional, Any
from datetime import datetime


class DealOut(Schema):
    id: int
    title: str
    value: Optional[float] = None
    status: str
    person_name: Optional[str] = None


class OnboardingCreateIn(Schema):
    pipedrive_deal_id: str
    pipedrive_deal_name: str


class OnboardingStepIn(Schema):
    # Step 1 — Negócio
    nome_empresa:          Optional[str] = None
    nicho:                 Optional[str] = None
    produto:               Optional[str] = None
    tipo_venda:            Optional[str] = None
    ticket:                Optional[str] = None
    modelo_venda:          Optional[str] = None
    como_vende:            Optional[str] = None
    crosssell:             Optional[str] = None
    vendas_atual:          Optional[str] = None
    vendas_meta:           Optional[str] = None
    fat_atual:             Optional[str] = None
    fat_meta:              Optional[str] = None
    volume_leads:          Optional[str] = None
    funcionarios:          Optional[str] = None
    entrada_crm:           Optional[str] = None
    integracoes:           Optional[str] = None
    followup_estruturado:  Optional[str] = None
    gravacoes:             Optional[str] = None
    # Step 2 — Lead
    perfil_lead:           Optional[str] = None
    dor_principal:         Optional[str] = None
    objecoes:              Optional[str] = None
    tom:                   Optional[list[str]] = None
    caso_sucesso:          Optional[str] = None
    gatilho_urgencia:      Optional[str] = None
    # Step 3 — Funis
    funis:                 Optional[list[str]] = None
    trafego_etapas:        Optional[list[Any]] = None
    trafego_isca:          Optional[str] = None
    trafego_plataforma:    Optional[str] = None
    trafego_dias:          Optional[str] = None
    trafego_bot:           Optional[str] = None
    prosp_etapas:          Optional[list[Any]] = None
    prosp_perfil:          Optional[str] = None
    prosp_dias:            Optional[str] = None
    prosp_canais:          Optional[list[str]] = None
    prosp_fonte:           Optional[str] = None
    social_etapas:         Optional[list[Any]] = None
    social_plat:           Optional[str] = None
    social_dias:           Optional[str] = None
    carteira_etapas:       Optional[list[Any]] = None
    carteira_quem:         Optional[str] = None
    cart_freq:             Optional[str] = None
    posvenda_etapas:       Optional[list[Any]] = None
    posvenda_obs:          Optional[str] = None
    custom_etapas:         Optional[list[Any]] = None
    custom_fluxo:          Optional[str] = None
    # Step 4 — Time
    sdr:                   Optional[str] = None
    closer:                Optional[str] = None
    especialista:          Optional[str] = None
    empresa_scripts:       Optional[str] = None
    perfil_operador:       Optional[str] = None
    etapas_fechamento:     Optional[list[Any]] = None
    fech_especifico:       Optional[str] = None
    tipo_reuniao:          Optional[str] = None
    passagem:              Optional[str] = None
    apresenta_preco:       Optional[str] = None
    metodo:                Optional[list[str]] = None
    condicao_especial:     Optional[str] = None
    objecoes_fecha:        Optional[str] = None
    # Step 5 — Scripts
    wpp_perguntas:         Optional[str] = None
    wpp_criterio:          Optional[str] = None
    wpp_desqualifica:      Optional[str] = None
    wpp_proximo:           Optional[str] = None
    lig_pitch:             Optional[str] = None
    lig_perguntas:         Optional[str] = None
    lig_objecoes:          Optional[str] = None
    fech_estrutura:        Optional[str] = None
    particularidades:      Optional[str] = None
    tem_ref:               Optional[str] = None
    ref_cliente:           Optional[str] = None
    # Step 6 — Datas
    plano_selecionado:     Optional[str] = None
    assessorias:           Optional[list[Any]] = None
    cs_encontros:          Optional[list[Any]] = None
    bonus_encontros:       Optional[list[Any]] = None
    # Step 7 — Pesquisa
    fonte_conteudo:        Optional[str] = None
    como_descobriu:        Optional[str] = None
    decisivo_prospeccao:   Optional[list[str]] = None
    experiencia_reuniao:   Optional[list[str]] = None
    indicador_sucesso:     Optional[str] = None


class OnboardingOut(Schema):
    id: int
    pipedrive_deal_id: str
    pipedrive_deal_name: str
    assessor_name: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: datetime
    # Step 1
    nome_empresa:          str
    nicho:                 str
    produto:               str
    tipo_venda:            str
    ticket:                str
    modelo_venda:          str
    como_vende:            str
    crosssell:             str
    vendas_atual:          str
    vendas_meta:           str
    fat_atual:             str
    fat_meta:              str
    volume_leads:          str
    funcionarios:          str
    entrada_crm:           str
    integracoes:           str
    followup_estruturado:  str
    gravacoes:             str
    # Step 2
    perfil_lead:           str
    dor_principal:         str
    objecoes:              str
    tom:                   list
    caso_sucesso:          str
    gatilho_urgencia:      str
    # Step 3
    funis:                 list
    trafego_etapas:        list
    trafego_isca:          str
    trafego_plataforma:    str
    trafego_dias:          str
    trafego_bot:           str
    prosp_etapas:          list
    prosp_perfil:          str
    prosp_dias:            str
    prosp_canais:          list
    prosp_fonte:           str
    social_etapas:         list
    social_plat:           str
    social_dias:           str
    carteira_etapas:       list
    carteira_quem:         str
    cart_freq:             str
    posvenda_etapas:       list
    posvenda_obs:          str
    custom_etapas:         list
    custom_fluxo:          str
    # Step 4
    sdr:                   str
    closer:                str
    especialista:          str
    empresa_scripts:       str
    perfil_operador:       str
    etapas_fechamento:     list
    fech_especifico:       str
    tipo_reuniao:          str
    passagem:              str
    apresenta_preco:       str
    metodo:                list
    condicao_especial:     str
    objecoes_fecha:        str
    # Step 5
    wpp_perguntas:         str
    wpp_criterio:          str
    wpp_desqualifica:      str
    wpp_proximo:           str
    lig_pitch:             str
    lig_perguntas:         str
    lig_objecoes:          str
    fech_estrutura:        str
    particularidades:      str
    tem_ref:               str
    ref_cliente:           str
    # Step 6
    plano_selecionado:     str
    assessorias:           list
    cs_encontros:          list
    bonus_encontros:       list
    # Step 7
    fonte_conteudo:        str
    como_descobriu:        str
    decisivo_prospeccao:   list
    experiencia_reuniao:   list
    indicador_sucesso:     str

    progress: int = 0
    material_status: Optional[str] = None

    @staticmethod
    def resolve_assessor_name(obj):
        return obj.assessor.name or obj.assessor.email

    @staticmethod
    def resolve_progress(obj):
        steps = [
            bool(obj.nome_empresa and obj.nicho and obj.produto),
            bool(obj.perfil_lead and obj.dor_principal),
            bool(obj.funis),
            bool(obj.etapas_fechamento),
            bool(obj.wpp_perguntas or obj.lig_pitch),
            bool(obj.plano_selecionado),
            bool(obj.fonte_conteudo),
        ]
        return round(sum(steps) / 7 * 100)

    @staticmethod
    def resolve_material_status(obj):
        try:
            return obj.material.status
        except Exception:
            return None

