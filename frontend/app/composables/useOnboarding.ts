// ── Material types ──────────────────────────────────────────────
export interface CadenceAction { channel: string; message: string; instructions?: string }
export interface CadenceDay { day: number; actions: CadenceAction[] }
export interface PipelineStage { name: string; objective: string; dev_instructions: string; cadence: CadenceDay[]; advance_criteria: string; loss_reason?: string }
export interface CRMFunnel { key: string; name: string; stages: PipelineStage[] }
export interface CRMScript { funnels: CRMFunnel[] }
export interface ObjectionRow { objection: string; hidden_concern: string; counter_script: string }
export type MeetingBlockKind = 'falar' | 'ouvir' | 'fazer'
export interface MeetingBlock { kind: MeetingBlockKind; label: string; open: string; points: string[]; close: string }
export type MeetingNoteKind = 'alerta' | 'pausa' | 'pergunta_chave' | 'validacao'
export interface MeetingNote { kind: MeetingNoteKind; title: string; text: string }
export interface MeetingStep { num: string; title: string; phase: string; subtitle: string; blocks: MeetingBlock[]; notes: MeetingNote[] }
export interface ClosingMaterial { diagnostic_questions: string[]; price_presentation: string; objection_matrix: ObjectionRow[]; meeting_structure?: MeetingStep[]; closing_script: string; special_condition?: string }
export interface QualStep { type: string; content: string; channel?: string } // legado
export interface QualQuestion { text: string; branch: string; note: string }
export interface QualCard { title: string; text: string }
export type QualBlockKind = 'falar' | 'ouvir' | 'perguntas' | 'cards'
export interface QualBlock { kind: QualBlockKind; label: string; open: string; points: string[]; close: string; questions: QualQuestion[]; cards: QualCard[] }
export type QualNoteKind = 'instrucao' | 'alerta' | 'anote' | 'stop' | 'transicao'
export interface QualNote { kind: QualNoteKind; title: string; text: string }
export interface QualPlaybookStep { num: string; title: string; phase: string; subtitle: string; gpctba: string; objective: string; blocks: QualBlock[]; notes: QualNote[] }
export interface QualificationScript { profile: string; framework: string; steps?: QualPlaybookStep[]; advance_criteria: string[]; disqualification_criteria: string[]; whatsapp_flow?: QualStep[]; call_pitch?: string }
export interface MaterialOut {
  id: number
  status: 'idle' | 'pending' | 'running' | 'complete' | 'failed'
  crm?: CRMScript
  closing?: ClosingMaterial
  qualification?: QualificationScript
  quality_alerts: string[]
  error: string
  created_at: string
  published: boolean
  published_at: string | null
  theme?: string
}

export interface MaterialLibraryItem {
  id: number
  pipedrive_deal_name: string
  assessor_name: string | null
  updated_at: string
  published?: boolean
  published_at?: string | null
}

export const cleanDealName = (name: string) =>
  (name || '').replace(/\[.*?\]/g, '').replace(/\s+/g, ' ').trim()

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
  // Step 4 — Fechamento
  etapas_fechamento: ClosingStep[]
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
  fonte_conteudo_outro: string
  como_descobriu_outro: string
  decisivo_prospeccao_outro: string
  experiencia_reuniao_outro: string
  indicador_sucesso_outro: string
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
    etapas_fechamento: JSON.parse(JSON.stringify(ETAPAS_FECHAMENTO_PADRAO)),
    wpp_perguntas: '', wpp_criterio: '', wpp_desqualifica: '', wpp_proximo: '',
    lig_pitch: '', lig_perguntas: '', lig_objecoes: '',
    fech_estrutura: '', particularidades: '', tem_ref: '', ref_cliente: '',
    plano_selecionado: '',
    assessorias: [], cs_encontros: [], bonus_encontros: [],
    fonte_conteudo: '', como_descobriu: '',
    decisivo_prospeccao: [], experiencia_reuniao: [], indicador_sucesso: '',
    fonte_conteudo_outro: '', como_descobriu_outro: '',
    decisivo_prospeccao_outro: '', experiencia_reuniao_outro: '', indicador_sucesso_outro: '',
  }
}

export function generateFakeForm(): OnboardingData {
  return {
    nome_empresa: 'Tech Solutions Ltda',
    nicho: 'Consultoria em Marketing Digital',
    produto: 'Gestão de tráfego pago e automação de vendas para e-commerces de moda, com foco em ROAS e escalabilidade de campanhas Meta Ads e Google Ads.',
    tipo_venda: 'B2B — Empresa para Empresa',
    ticket: 'R$ 4.500',
    modelo_venda: 'Mensalidade recorrente',
    como_vende: 'Indicação e prospecção ativa via LinkedIn, sem processo de cadência definido atualmente. Leads vêm também de formulário no site e tráfego orgânico.',
    crosssell: 'Migração de plano Básico para Enterprise após 3 meses de resultado comprovado, incluindo funil completo de CRM',
    vendas_atual: '5',
    vendas_meta: '15',
    fat_atual: 'R$ 22.500',
    fat_meta: 'R$ 67.500',
    volume_leads: '80 leads/mês',
    funcionarios: '6 funcionários',
    entrada_crm: 'WhatsApp Business + formulário de lead dos anúncios Meta Ads + landing page',
    integracoes: 'API Oficial Meta, Google Ads API, Calendly, Chatbear, n8n',
    followup_estruturado: 'Parcialmente',
    gravacoes: 'Sim, tenho gravações',
    perfil_lead: 'Proprietários de e-commerces de moda que faturam entre R$ 50k e R$ 200k por mês, com experiência em tráfego pago mas sem escala previsível',
    dor_principal: 'Baixo ROAS (1.8–2.5), dificuldade em escalar campanhas sem aumentar CAC, falta de dados claros para decisão de investimento em mídia',
    objecoes: 'Já tentei outra consultoria e não funcionou / Preciso pensar e analisar o orçamento / Está caro para o que estou faturando hoje',
    tom: ['Direto e objetivo'],
    caso_sucesso: 'E-commerce de moda feminina estava estagnado em R$ 45k mensais com ROAS de 1.8. Em 90 dias otimizamos catálogo e campanhas, alcançando R$ 112k com ROAS de 4.2',
    gatilho_urgencia: 'O algoritmo das plataformas de anúncios penaliza contas com baixo histórico de conversão. Cada dia sem otimização aumenta o CAC de forma irreversível a curto prazo',
    funis: ['trafego', 'prospeccao'],
    trafego_isca: 'Raio-X gratuito de 30 minutos das contas de anúncio com diagnóstico de gargalos',
    trafego_plataforma: 'Meta Ads + Google Ads',
    trafego_dias: '7 dias',
    trafego_bot: 'Chatbear faz 2 perguntas de qualificação no Messenger: "Qual seu faturamento mensal?" e "Já investe em tráfego pago?". Só cai no Pipedrive quem responde ambas.',
    trafego_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.trafego)),
    prosp_perfil: 'E-commerces de moda (vestuário feminino, masculino, acessórios) com faturamento entre R$ 50k e R$ 200k mensais, que já investem em tráfego pago mas sem gestão profissional',
    prosp_dias: '5 dias',
    prosp_canais: ['WhatsApp', 'LinkedIn'],
    prosp_fonte: 'Apollo.io + Google Maps + lista segmentada da base do LinkedIn Sales Navigator',
    prosp_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.prospeccao)),
    social_plat: '',
    social_dias: '',
    social_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.social)),
    carteira_quem: '',
    cart_freq: '',
    carteira_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.carteira)),
    posvenda_obs: '',
    posvenda_etapas: JSON.parse(JSON.stringify(ETAPAS_PADRAO.posvenda)),
    custom_fluxo: '',
    custom_etapas: [],
    etapas_fechamento: JSON.parse(JSON.stringify(ETAPAS_FECHAMENTO_PADRAO)),
    wpp_perguntas: '1. Qual seu faturamento médio mensal com o e-commerce?\n2. Você já investe em tráfego pago ou quer começar do zero?\n3. Qual seu maior desafio hoje com as vendas online?\n4. Quanto você está disposto a investir mensalmente em tráfego?',
    wpp_criterio: 'Faturamento acima de R$ 50k/mês + já investe em tráfego pago OU tem verba mínima de R$ 3k para começar',
    wpp_desqualifica: 'Faturamento abaixo de R$ 20k/mês ou sem interesse/verba para tráfego pago',
    wpp_proximo: 'Agendar reunião',
    lig_pitch: 'Alô, [Nome]? Aqui é [SDR], da Tech Solutions. Você pediu um diagnóstico de tráfego pelo nosso site, certo? Posso fazer umas perguntas rápidas para entender melhor seu momento?',
    lig_perguntas: '1. Como estão os resultados dos seus anúncios hoje?\n2. Qual o produto que mais vende atualmente?\n3. Você mesmo gerencia o tráfego ou tem agência?\n4. Qual seria o cenário ideal para você em 90 dias?',
    lig_objecoes: 'Não tenho tempo agora → Entendo, podemos marcar um horário melhor para você. 15 minutos é suficiente?\nJá tenho agência → Que legal! E qual o ROAS que estão te entregando? Posso fazer uma comparação rápida.\nEstá caro → Comparado a continuar perdendo [X] por mês em anúncios mal otimizados, o investimento se paga em quanto tempo?',
    fech_estrutura: '',
    particularidades: '',
    tem_ref: '',
    ref_cliente: '',
    plano_selecionado: 'fast',
    assessorias: [
      { date: '', time: '', responsible: 'Assessor' },
      { date: '', time: '', responsible: 'Assessor' },
      { date: '', time: '', responsible: 'Assessor' },
      { date: '', time: '', responsible: 'Assessor' },
    ],
    cs_encontros: [],
    bonus_encontros: [],
    fonte_conteudo: 'YouTube',
    como_descobriu: 'Um amigo ou parceiro recomendou',
    decisivo_prospeccao: ['A abordagem foi 100% personalizada — ele provou que estudou meu negócio antes de entrar em contato'],
    experiencia_reuniao: ['O especialista identificou um gargalo que eu nem sabia que existia'],
    indicador_sucesso: 'ROI — o aumento de faturamento pagou a assessoria e gerou lucro real no caixa',
    fonte_conteudo_outro: '',
    como_descobriu_outro: '',
    decisivo_prospeccao_outro: '',
    experiencia_reuniao_outro: '',
    indicador_sucesso_outro: '',
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
  const dealId = ref<string | null>(null)
  const dealName = ref('')
  const assessorName = ref('')

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

  const generateMaterials = async (opts?: { templateMaterialId?: number; templateKnowledgeName?: string }) => {
    _stopPolling()
    materialsGenerating.value = true
    try {
      const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/generate`, {
        method: 'POST',
        body: {
          template_material_id: opts?.templateMaterialId ?? null,
          template_knowledge_name: opts?.templateKnowledgeName ?? null,
        },
      })
      materials.value = data
      if (data.status !== 'complete') _pollingTimer = setTimeout(_pollOnce, 3000)
    } finally {
      materialsGenerating.value = false
    }
  }

  const createManualMaterial = async () => {
    const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/materials/manual`, { method: 'POST' })
    materials.value = data
  }

  const copyMaterialFrom = async (sourceId: number) => {
    const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/materials/copy-from/${sourceId}`, { method: 'POST' })
    materials.value = data
  }

  const loadMaterialLibrary = async () => {
    const items = await fetchAuth<MaterialLibraryItem[]>('/api/onboarding/materials/library')
    return items.map(it => ({ ...it, pipedrive_deal_name: cleanDealName(it.pipedrive_deal_name) }))
  }

  let _prewarmFired = false
  const prepareAssistant = async () => {
    if (_prewarmFired) return
    _prewarmFired = true
    try {
      await fetchAuth(`/api/onboarding/${resolvedId}/materials/assist/prepare`, { method: 'POST' })
    } catch { /* fire-and-forget */ }
  }

  const publishMaterial = async () => {
    const data = await fetchAuth<MaterialOut>(`/api/onboarding/${resolvedId}/materials/publish`, { method: 'POST' })
    materials.value = data
    return data
  }

  const saveMaterials = async (patch: Partial<Pick<MaterialOut, 'crm' | 'closing' | 'qualification' | 'theme'>>) => {
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
      dealId.value = (data.pipedrive_deal_id ?? null) as string | null
      dealName.value = cleanDealName(data.pipedrive_deal_name)
      assessorName.value = data.assessor_name || ''
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

  const moveInList = <T,>(list: T[], i: number, dir: -1 | 1) => {
    const j = i + dir
    if (j < 0 || j >= list.length) return
    ;[list[i], list[j]] = [list[j], list[i]]
  }

  // Etapas da reunião de fechamento: num é o rótulo de ordem (01, 02...). Re-sequencia
  // após add/remover/mover para manter consistência (a IA usa num como ordem).
  const renumberEtapasFechamento = () => {
    form.value.etapas_fechamento.forEach((e, i) => { e.num = String(i + 1).padStart(2, '0') })
  }
  const addEtapaFechamento = () => {
    form.value.etapas_fechamento.push({ num: '', text: '', active: true })
    renumberEtapasFechamento()
  }
  const removeEtapaFechamento = (i: number) => {
    form.value.etapas_fechamento.splice(i, 1)
    renumberEtapasFechamento()
  }
  const moveEtapaFechamento = (i: number, dir: -1 | 1) => {
    moveInList(form.value.etapas_fechamento, i, dir)
    renumberEtapasFechamento()
  }

  const suggestingScripts = ref(false)

  const suggestScripts = async () => {
    suggestingScripts.value = true
    try {
      const data: Record<string, string> = await fetchAuth(`/api/onboarding/${resolvedId}/suggest-scripts`, { method: 'POST' })
      for (const key of ['wpp_perguntas', 'wpp_criterio', 'wpp_desqualifica', 'wpp_proximo', 'lig_pitch', 'lig_perguntas', 'lig_objecoes']) {
        if (data[key] !== undefined) (form.value as any)[key] = data[key]
      }
    } finally {
      suggestingScripts.value = false
    }
  }

  return {
    form, step, saving, submitting, loading, status, dealId, dealName, assessorName,
    load, saveStep, nextStep, prevStep, submit,
    toggleChip, selectOne, toggleFunil, selectPlano, addEtapa, addBonus, moveInList,
    addEtapaFechamento, removeEtapaFechamento, moveEtapaFechamento,
    PLANOS, suggestingScripts,
    materials, materialsGenerating, loadMaterials, generateMaterials, saveMaterials,
    createManualMaterial, copyMaterialFrom, loadMaterialLibrary,
    prepareAssistant, publishMaterial, suggestScripts,
  }
}
