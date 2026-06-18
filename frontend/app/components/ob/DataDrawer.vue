<script setup lang="ts">
import type { OnboardingData } from '~/composables/useOnboarding'

const props = defineProps<{
  open: boolean
  form: OnboardingData
  dealName?: string
  assessorName?: string
}>()

const emit = defineEmits<{ close: [] }>()

const openSections = ref<Record<string, boolean>>({
  negocio: true,
  lead: false,
  funis: false,
  time: false,
  scripts: false,
  datas: false,
  pesquisa: false,
})

function toggle(key: string) {
  openSections.value[key] = !openSections.value[key]
}

function handleEsc(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

watch(() => props.open, (v) => {
  if (v) document.addEventListener('keydown', handleEsc)
  else document.removeEventListener('keydown', handleEsc)
})

onUnmounted(() => document.removeEventListener('keydown', handleEsc))

interface FieldDef { label: string; key: keyof OnboardingData }

const SECTIONS: { key: string; title: string; fields: FieldDef[] }[] = [
  {
    key: 'negocio', title: 'Negócio',
    fields: [
      { label: 'Empresa', key: 'nome_empresa' },
      { label: 'Nicho', key: 'nicho' },
      { label: 'Produto', key: 'produto' },
      { label: 'Tipo de venda', key: 'tipo_venda' },
      { label: 'Ticket', key: 'ticket' },
      { label: 'Modelo de venda', key: 'modelo_venda' },
      { label: 'Como vende', key: 'como_vende' },
      { label: 'Cross/Up sell', key: 'crosssell' },
      { label: 'Vendas atual', key: 'vendas_atual' },
      { label: 'Vendas meta', key: 'vendas_meta' },
      { label: 'Faturamento atual', key: 'fat_atual' },
      { label: 'Faturamento meta', key: 'fat_meta' },
      { label: 'Volume de leads', key: 'volume_leads' },
      { label: 'Funcionários', key: 'funcionarios' },
      { label: 'Entrada de leads no CRM', key: 'entrada_crm' },
      { label: 'Integrações', key: 'integracoes' },
      { label: 'Follow-up estruturado', key: 'followup_estruturado' },
      { label: 'Gravações', key: 'gravacoes' },
    ],
  },
  {
    key: 'lead', title: 'Lead',
    fields: [
      { label: 'Perfil do lead', key: 'perfil_lead' },
      { label: 'Dor principal', key: 'dor_principal' },
      { label: 'Objeções', key: 'objecoes' },
      { label: 'Tom', key: 'tom' },
      { label: 'Caso de sucesso', key: 'caso_sucesso' },
      { label: 'Gatilho de urgência', key: 'gatilho_urgencia' },
    ],
  },
  {
    key: 'funis', title: 'Funis',
    fields: [
      { label: 'Funis ativos', key: 'funis' },
      { label: 'Tráfego — isca', key: 'trafego_isca' },
      { label: 'Tráfego — plataforma', key: 'trafego_plataforma' },
      { label: 'Tráfego — dias', key: 'trafego_dias' },
      { label: 'Prospecção — perfil', key: 'prosp_perfil' },
      { label: 'Prospecção — canais', key: 'prosp_canais' },
      { label: 'Prospecção — fonte', key: 'prosp_fonte' },
      { label: 'Social — plataforma', key: 'social_plat' },
      { label: 'Carteira — quem', key: 'carteira_quem' },
      { label: 'Carteira — frequência', key: 'cart_freq' },
      { label: 'Pós-venda — observações', key: 'posvenda_obs' },
      { label: 'Custom — fluxo', key: 'custom_fluxo' },
    ],
  },
  {
    key: 'scripts', title: 'Scripts',
    fields: [
      { label: 'WhatsApp — perguntas', key: 'wpp_perguntas' },
      { label: 'WhatsApp — critério', key: 'wpp_criterio' },
      { label: 'WhatsApp — desqualifica', key: 'wpp_desqualifica' },
      { label: 'WhatsApp — próximo passo', key: 'wpp_proximo' },
      { label: 'Ligação — pitch', key: 'lig_pitch' },
      { label: 'Ligação — perguntas', key: 'lig_perguntas' },
      { label: 'Ligação — objeções', key: 'lig_objecoes' },
      { label: 'Particularidades no funil', key: 'fech_estrutura' },
      { label: 'Particularidades', key: 'particularidades' },
      { label: 'Tem referência', key: 'tem_ref' },
      { label: 'Cliente referência', key: 'ref_cliente' },
    ],
  },
  {
    key: 'datas', title: 'Datas',
    fields: [
      { label: 'Plano selecionado', key: 'plano_selecionado' },
      { label: 'Assessorias', key: 'assessorias' },
      { label: 'Encontros CS', key: 'cs_encontros' },
      { label: 'Bônus', key: 'bonus_encontros' },
    ],
  },
  {
    key: 'pesquisa', title: 'Pesquisa',
    fields: [
      { label: 'Fonte de conteúdo', key: 'fonte_conteudo' },
      { label: 'Como descobriu', key: 'como_descobriu' },
      { label: 'Decisivo na prospecção', key: 'decisivo_prospeccao' },
      { label: 'Experiência na reunião', key: 'experiencia_reuniao' },
      { label: 'Indicador de sucesso', key: 'indicador_sucesso' },
    ],
  },
]

function formatDate(d: string) {
  if (!d) return ''
  const [y, m, day] = d.split('-')
  if (!y || !m || !day) return d
  return `${day}/${m}/${y.slice(2)}`
}

function renderValue(val: any): string {
  if (val == null || val === '') return '—'
  if (Array.isArray(val)) {
    if (!val.length) return '—'
    if (typeof val[0] === 'string') return val.join(', ')
    if (typeof val[0] === 'object') {
      return val.map((item: any, i: number) => {
        const parts: string[] = []
        if (item.label) parts.push(item.label)
        else parts.push(`#${i + 1}`)
        if (item.date) parts.push(formatDate(item.date))
        if (item.time) parts.push(item.time)
        if (item.responsible) parts.push(`(${item.responsible})`)
        return parts.join(' · ')
      }).join('\n')
    }
    return `${val.length} item${val.length > 1 ? 's' : ''}`
  }
  return String(val)
}
</script>

<template>
  <Transition
    enter-active-class="transition-transform duration-200 ease-out"
    enter-from-class="translate-x-full"
    leave-active-class="transition-transform duration-150 ease-in"
    leave-to-class="translate-x-full"
  >
    <aside
      v-if="open"
      class="fixed top-0 right-0 h-screen w-full sm:w-[24rem] z-30 bg-[#0a0a0a] border-l border-white/[0.06] flex flex-col"
    >
      <div class="px-5 py-4 border-b border-white/[0.06] flex items-center justify-between gap-3 shrink-0">
        <div class="min-w-0">
          <p class="text-xs text-white/40 uppercase tracking-widest">Dados do onboarding</p>
          <p class="text-sm font-medium text-white truncate">{{ dealName || '—' }}</p>
          <p v-if="assessorName" class="text-xs text-white/50 truncate mt-0.5">
            Assessor: <span class="text-white/70">{{ assessorName }}</span>
          </p>
        </div>
        <button
          class="text-white/40 hover:text-white transition-colors shrink-0"
          title="Fechar"
          @click="emit('close')"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div
          v-for="section in SECTIONS"
          :key="section.key"
          class="bg-white/[0.03] ring-1 ring-white/[0.08] rounded-2xl overflow-hidden"
        >
          <button
            type="button"
            class="w-full flex items-center justify-between px-4 py-3 hover:bg-white/[0.03] transition-colors"
            @click="toggle(section.key)"
          >
            <span class="text-xs font-semibold text-white/60 uppercase tracking-widest">
              {{ section.title }}
            </span>
            <svg class="w-4 h-4 text-white/30 transition-transform" :class="{ 'rotate-180': openSections[section.key] }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          <div v-show="openSections[section.key]" class="border-t border-white/[0.06] divide-y divide-white/[0.04]">
            <div
              v-for="field in section.fields"
              :key="field.key as string"
              class="px-4 py-2.5"
            >
              <p class="text-[10px] text-white/30 uppercase tracking-widest mb-0.5">{{ field.label }}</p>
              <p class="text-sm text-white/80 whitespace-pre-wrap break-words">
                {{ renderValue(form[field.key]) }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  </Transition>
</template>
