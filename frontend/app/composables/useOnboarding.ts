// ── Material types ──────────────────────────────────────────────
export interface CadenceAction { channel: string; message: string; instructions?: string }
export interface CadenceDay { day: number; actions: CadenceAction[] }
export interface PipelineStage { name: string; objective: string; dev_instructions: string; cadence: CadenceDay[]; advance_criteria: string; loss_reason?: string }
export interface CRMScript { stages: PipelineStage[] }
export interface ObjectionRow { objection: string; hidden_concern: string; counter_script: string }
export interface ClosingMaterial { diagnostic_questions: string[]; price_presentation: string; objection_matrix: ObjectionRow[]; closing_script: string; special_condition?: string }
export interface QualStep { type: string; content: string; channel?: string }
export interface QualificationScript { profile: string; whatsapp_flow: QualStep[]; call_pitch: string; advance_criteria: string[]; disqualification_criteria: string[] }
export interface MaterialOut {
  id: number
  status: 'idle' | 'pending' | 'running' | 'complete' | 'failed'
  crm?: CRMScript
  closing?: ClosingMaterial
  qualification?: QualificationScript
  quality_alerts: string[]
  error: string
  created_at: string
}

export interface FunilEtapa {
  name: string
  action: string
  active: boolean
  optional?: boolean
}

export interface ClosingStep {
  num: string
  text: string
  active: boolean
}

export interface DateEntry {
  date: string
  time: string
  responsible: string
}

export interface BonusEntry {
  label: string
  date: string
  time: string
  responsible: string
}

export interface OnboardingData {
  // Step 1 — Negócio
  nome_empresa: string
  nicho: string
  produto: string
  tipo_venda: string
  ticket: string
  modelo_venda: string
  como_vende: string
  crosssell: string
  vendas_atual: string
  vendas_meta: string
  fat_atual: string
  fat_meta: string
  volume_leads: string
  funcionarios: string
  entrada_crm: string
  integracoes: string
  followup_estruturado: string
  gravacoes: string
  // Step 2 — Lead
  perfil_lead: string
  dor_principal: string
  objecoes: string
  tom: string[]
  caso_sucesso: string
  gatilho_urgencia: string
  // Step 3 — Funis
  funis: string[]
  trafego_isca: string
  trafego_plataforma: string
  trafego_dias: string
  trafego_bot: string
  trafego_etapas: FunilEtapa[]
  prosp_perfil: string
  prosp_dias: string
  prosp_canais: string[]
  prosp_fonte: string
  prosp_etapas: FunilEtapa[]
  social_plat: string
  social_dias: string
  social_etapas: FunilEtapa[]
  carteira_quem: string
  cart_freq: string
  carteira_etapas: FunilEtapa[]
  posvenda_obs: string
  posvenda_etapas: FunilEtapa[]
  custom_fluxo: string
  custom_etapas: FunilEtapa[]
  // Step 4 — Time
  sdr: string
  closer: string
  especialista: string
  empresa_scripts: string
  perfil_operador: string
  etapas_fechamento: ClosingStep[]
  fech_especifico: string
  tipo_reuniao: string
  passagem: string
  apresenta_preco: string
  metodo: string[]
  condicao_especial: string
  objecoes_fecha: string
  // Step 5 — Scripts
  wpp_perguntas: string
  wpp_criterio: string
  wpp_desqualifica: string
  wpp_proximo: string
  lig_pitch: string
  lig_perguntas: string
  lig_objecoes: string
  fech_estrutura: string
  particularidades: string
  tem_ref: string
  ref_cliente: string
  // Step 6 — Datas
  plano_selecionado: string
  assessorias: DateEntry[]
  cs_encontros: DateEntry[]
  bonus_encontros: BonusEntry[]
  // Step 7 — Pesquisa
  fonte_conteudo: string
  como_descobriu: string
  decisivo_prospeccao: string[]
  experiencia_reuniao: string[]
  indicador_sucesso: string
}

const ETAPAS_PADRAO: Record<string, FunilEtapa[]> = {
  trafego: [
    { name: 'Novo Lead', action: 'Analisar e mover para prospecção imediatamente', active: true },
    { name: 'Tentando Contato', action: 'Iniciar cadência — 3 tentativas de ligação antes do WhatsApp', active: true },
    { name: 'Conversando', action: 'Qualificação ativa — conduzir para agendamento', active: true },
    { name: 'Manter Relacionamento', action: 'Lead quer mas não é o momento — nutrir até ficar pronto', active: true },
    { name: 'Reunião Agendada', action: 'Enviar confirmação 1h antes — criar atividade de lembrete', active: true },
    { name: 'No-Show', action: 'Iniciar cadência de remarcação — 4 dias', active: true },
    { name: 'Negociação', action: 'Follow-ups com data combinada', active: true },
    { name: 'Contrato Enviado', action: 'Cobrar assinatura', active: true, optional: true },
    { name: 'Ganho', action: 'Mover para pós-venda ou carteira', active: true },
  ],
  prospeccao: [
    { name: 'Sem Contato', action: 'Aguardando primeiro acesso — analisar perfil antes de abordar', active: true },
    { name: 'Em Prospecção', action: 'Iniciar cadência de abordagem ativa', active: true },
    { name: 'Respondeu', action: 'Engajar e conduzir para qualificação', active: true },
    { name: 'Interessado', action: 'Qualificação aprofundada — identificar dor e decidir se agenda', active: true },
    { name: 'Reunião Agendada', action: 'Enviar confirmação 1h antes — criar atividade de lembrete', active: true },
    { name: 'No-Show', action: 'Iniciar cadência de remarcação — 4 dias', active: true },
    { name: 'Negociação', action: 'Follow-ups com data combinada', active: true },
    { name: 'Contrato Enviado', action: 'Cobrar assinatura', active: true, optional: true },
    { name: 'Ganho', action: 'Mover para pós-venda ou carteira', active: true },
  ],
  social: [
    { name: 'Novo Lead', action: 'Verificar perfil — curtiu, comentou ou seguiu recentemente', active: true },
    { name: 'Aquecimento', action: 'Interagir no perfil por 3 a 7 dias antes de abordar na DM', active: true },
    { name: 'Tentando Contato', action: 'Enviar mensagem na DM — abordagem baseada no engajamento', active: true },
    { name: 'Conversando', action: 'Qualificação na DM — 2 perguntas por lead, não vender ainda', active: true },
    { name: 'Interessado', action: 'Conduzir para agendamento de reunião ou ligação', active: true },
    { name: 'Reunião Agendada', action: 'Enviar confirmação 1h antes — criar atividade de lembrete', active: true },
    { name: 'No-Show', action: 'Iniciar cadência de remarcação — 4 dias', active: true },
    { name: 'Negociação', action: 'Follow-ups com data combinada', active: true },
    { name: 'Ganho', action: 'Mover para pós-venda ou carteira', active: true },
  ],
  carteira: [
    { name: 'Em Reativação', action: 'Enviar mensagem de reativação personalizada', active: true },
    { name: 'Conversando', action: 'Qualificação — entender o que mudou desde o último contato', active: true },
    { name: 'Reunião Agendada', action: 'Enviar confirmação 1h antes — criar atividade de lembrete', active: true },
    { name: 'Não Compareceu', action: 'Tentativa de remarcação — máximo 2 tentativas', active: true },
    { name: 'Negociação', action: 'Follow-ups com data combinada', active: true },
    { name: 'Ganho', action: 'Mover para pós-venda', active: true },
  ],
  posvenda: [
    { name: 'Novo Fechamento', action: 'Pedir indicações e solicitar documentos necessários', active: true },
    { name: 'Enviar Contrato', action: 'Enviar contrato para assinatura digital', active: true },
    { name: 'Aguardando Assinatura', action: 'Cobrar assinatura — prazo máximo 48h', active: true },
    { name: 'Agendar Onboarding', action: 'Combinar data e hora do onboarding com o cliente', active: true },
    { name: 'Onboarding Agendado', action: 'Confirmar onboarding 24h antes — enviar agenda', active: true },
    { name: 'Em Execução', action: 'Acompanhar andamento e responder dúvidas', active: true },
    { name: 'Finalização', action: 'Colher depoimento e pedido de indicação', active: true },
  ],
  custom: [],
}

const ETAPAS_FECHAMENTO_PADRAO: ClosingStep[] = [
  { num: '01', text: 'Rapport inicial — conexão e quebra de gelo', active: true },
  { num: '02', text: 'Quem é o Closer e a Empresa — apresentação e autoridade', active: true },
  { num: '03', text: 'Gatilho da sinceridade — abrir espaço para honestidade mútua', active: true },
  { num: '04', text: 'Recapitulação do cenário do SDR — resumo do que foi levantado', active: true },
  { num: '05', text: 'Diagnóstico profundo — perguntas abertas para aprofundar a dor', active: true },
  { num: '06', text: 'Validação das dores — confirmar e amplificar o problema', active: true },
  { num: '07', text: 'Validar a solução — conectar a dor ao que será entregue', active: true },
  { num: '08', text: 'Case e prova social — resultado real de cliente do mesmo nicho', active: true },
  { num: '09', text: '[Pergunta chave] — pergunta de comprometimento antes de apresentar preço', active: true },
  { num: '10', text: 'Ancoragem de perdas — o que o lead perde se não agir agora', active: true },
  { num: '11', text: 'Aviso sobre início de negociação — transição para apresentação da proposta', active: true },
  { num: '12', text: 'Entregáveis e proposta na tela — apresentar o que está sendo comprado', active: true },
  { num: '13', text: 'Contorno de objeções — isolamento e contra-ataque', active: true },
  { num: '14', text: 'Definição de próximos passos — fechamento, compromisso de retorno ou pedir 3 indicações', active: true },
]

const PLANOS: Record<string, { assessorias: number; cs: number; label: string }> = {
  fast:   { assessorias: 4, cs: 0, label: '4 assessorias com Amanda' },
  growth: { assessorias: 3, cs: 3, label: '3 assessorias + 3 CS' },
  pro:    { assessorias: 4, cs: 4, label: '4 assessorias + 4 CS' },
  custom: { assessorias: 0, cs: 0, label: 'Personalizado' },
}

function emptyForm(): OnboardingData {
  return {
    nome_empresa: '', nicho: '', produto: '', tipo_venda: '',
    ticket: '', modelo_venda: '', como_vende: '', crosssell: '',
    vendas_atual: '', vendas_meta: '', fat_atual: '', fat_meta: '',
    volume_leads: '', funcionarios: '',
    entrada_crm: '', integracoes: '', followup_estruturado: '', gravacoes: '',
    perfil_lead: '', dor_principal: '', objecoes: '', tom: [], caso_sucesso: '', gatilho_urgencia: '',
    funis: [],
    trafego_isca: '', trafego_plataforma: '', trafego_dias: '', trafego_bot: '',
    trafego_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.trafego)),
    prosp_perfil: '', prosp_dias: '', prosp_canais: [], prosp_fonte: '',
    prosp_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.prospeccao)),
    social_plat: '', social_dias: '',
    social_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.social)),
    carteira_quem: '', cart_freq: '',
    carteira_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.carteira)),
    posvenda_obs: '',
    posvenda_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.posvenda)),
    custom_fluxo: '', custom_etapas: [],
    sdr: '', closer: '', especialista: '', empresa_scripts: '',
    perfil_operador: '',
    etapas_fechamento: JSON.parse(JSON.stringify(ETAPAS_FECHAMENTO_PADRAO)),
    fech_especifico: '', tipo_reuniao: '', passagem: '',
    apresenta_preco: '', metodo: [], condicao_especial: '', objecoes_fecha: '',
    wpp_perguntas: '', wpp_criterio: '', wpp_desqualifica: '', wpp_proximo: '',
    lig_pitch: '', lig_perguntas: '', lig_objecoes: '',
    fech_estrutura: '', particularidades: '', tem_ref: '', ref_cliente: '',
    plano_selecionado: '',
    assessorias: [], cs_encontros: [], bonus_encontros: [],
    fonte_conteudo: '', como_descobriu: '',
    decisivo_prospeccao: [], experiencia_reuniao: [], indicador_sucesso: '',
  }
}

export const useOnboarding = (id: Ref<string | string[]> | string) => {
  const resolvedId = typeof id === 'string' ? id : (id as Ref<string | string[]>).value as string
  const { fetchAuth } = useAuth()

  const form = ref<OnboardingData>(emptyForm())
  const step = ref(1)
  const saving = ref(false)
  const submitting = ref(false)
  const loading = ref(false)
  const status = ref<'draft' | 'complete' | 'synced'>('draft')
  const dealName = ref('')

  // ── Materials ────────────────────────────────────────────────
  const materials = ref<MaterialOut | null>(null)
  const materialsGenerating = ref(false)
  let _pollingTimer: ReturnType<typeof setTimeout> | null = null

  const _stopPolling = () => { if (_pollingTimer) { clearTimeout(_pollingTimer); _pollingTimer = null } }

  const _pollOnce = async () => {
    const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/materials`)
    materials.value = data
    if (data.status === 'pending' || data.status === 'running') {
      _pollingTimer = setTimeout(_pollOnce, 3000)
    }
  }

  const loadMaterials = async () => {
    try {
      const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/materials`)
      materials.value = data
    } catch { /* not yet generated */ }
  }

  const generateMaterials = async () => {
    _stopPolling()
    materialsGenerating.value = true
    try {
      const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/generate`, { method: 'POST' })
      materials.value = data
      if (data.status !== 'complete') _pollingTimer = setTimeout(_pollOnce, 3000)
    } finally {
      materialsGenerating.value = false
    }
  }

  const saveMaterials = async (patch: Partial<Pick<MaterialOut, 'crm' | 'closing' | 'qualification'>>) => {
    const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/materials`, {
      method: 'PATCH',
      body: patch,
    })
    materials.value = data
  }

  const _formKeys = Object.keys(emptyForm()) as Array<keyof OnboardingData>

  const load = async () => {
    loading.value = true
    try {
      const data = await fetchAuth<Record<string, any>>(`/api/onboarding/${resolvedId}`)
      const defaults = emptyForm()
      const formData: Partial<OnboardingData> = {}
      for (const k of _formKeys) {
        if (data[k] === undefined) continue
        const val = data[k]
        const def = (defaults as any)[k]
        // Preserva os padrões não-vazios quando o backend retorna array vazio
        // (formulário novo que ainda não teve as etapas salvas)
        if (Array.isArray(val) && val.length === 0 && Array.isArray(def) && def.length > 0) continue
        formData[k] = val as any
      }
      form.value = { ...defaults, ...formData }
      status.value = data.status as 'draft' | 'complete' | 'synced'
      dealName.value = data.pipedrive_deal_name
    } catch {
      // novo formulário ainda não tem dados
    } finally {
      loading.value = false
    }
  }

  const saveStep = async () => {
    if (saving.value) return
    saving.value = true
    try {
      const raw = JSON.parse(JSON.stringify(form.value)) as Record<string, unknown>
      const payload: Record<string, unknown> = {}
      for (const k of _formKeys) {
        if (raw[k] !== undefined) payload[k] = raw[k]
      }
      await fetchAuth(`/api/onboarding/${resolvedId}`, {
        method: 'PATCH',
        body: payload,
      })
    } finally {
      saving.value = false
    }
  }

  const nextStep = async () => {
    await saveStep()
    step.value = Math.min(step.value + 1, 8)
  }

  const prevStep = () => {
    step.value = Math.max(step.value - 1, 1)
  }

  const submit = async () => {
    submitting.value = true
    try {
      await fetchAuth(`/api/onboarding/${resolvedId}/submit`, { method: 'POST' })
      status.value = 'synced'
    } finally {
      submitting.value = false
    }
  }

  const toggleChip = (arr: string[], val: string) => {
    const idx = arr.indexOf(val)
    if (idx === -1) arr.push(val)
    else arr.splice(idx, 1)
  }

  const selectOne = (key: keyof OnboardingData, val: string) => {
    (form.value[key] as string) = (form.value[key] as string) === val ? '' : val
  }

  const toggleFunil = (key: string) => {
    const arr = form.value.funis
    const idx = arr.indexOf(key)
    if (idx === -1) arr.push(key)
    else arr.splice(idx, 1)
  }

  const selectPlano = (plano: string) => {
    form.value.plano_selecionado = plano
    const cfg = PLANOS[plano]
    if (!cfg) return
    form.value.assessorias = Array.from({ length: cfg.assessorias }, () => ({ date: '', time: '', responsible: 'Assessor' }))
    form.value.cs_encontros = Array.from({ length: cfg.cs }, () => ({ date: '', time: '', responsible: 'Amanda' }))
  }

  const addEtapa = (funil: string) => {
    const key = `${funil}_etapas` as keyof OnboardingData
    ;(form.value[key] as FunilEtapa[]).push({ name: '', action: '', active: true })
  }

  const addBonus = () => {
    form.value.bonus_encontros.push({ label: '', date: '', time: '', responsible: '' })
  }

  return {
    form, step, saving, submitting, loading, status, dealName,
    load, saveStep, nextStep, prevStep, submit,
    toggleChip, selectOne, toggleFunil, selectPlano, addEtapa, addBonus,
    PLANOS,
    materials, materialsGenerating, loadMaterials, generateMaterials, saveMaterials,
  }
}
