<template>
  <div class="min-h-screen bg-[#0a0a0a]">
    <!-- Header sticky -->
    <div class="sticky top-0 z-20 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-white/[0.06]">
      <div class="max-w-4xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
        <!-- Voltar + nome -->
        <div class="flex items-center gap-3 min-w-0">
          <NuxtLink :to="`/onboarding/${id}`" class="text-white/30 hover:text-white/60 transition-colors shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
          </NuxtLink>
          <div class="min-w-0">
            <p class="text-white text-sm font-medium truncate">{{ dealName || 'Materiais' }}</p>
            <p class="text-xs text-white/30">Script CRM · Fechamento · Qualificação</p>
          </div>
        </div>

        <!-- Ações -->
        <div class="flex items-center gap-3 shrink-0">
          <!-- indicador de save -->
          <template v-if="!isDesenvolvedor">
            <span v-if="saveStatus === 'saving'" class="flex items-center gap-1.5 text-xs text-white/30">
              <svg class="w-3 h-3 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
              </svg>
              Salvando...
            </span>
            <span v-else-if="saveStatus === 'saved'" class="text-xs text-emerald-400/70">Salvo</span>
          </template>

          <!-- Dropdown exportar PDF -->
          <div ref="pdfDropdownRef" class="relative">
            <button
              class="px-3 py-1.5 text-sm text-white/50 hover:text-white/80 border border-white/10 rounded-lg transition-all flex items-center gap-1.5"
              @click.stop="pdfMenuOpen = !pdfMenuOpen"
            >
              Exportar PDF
              <svg class="w-3 h-3 transition-transform" :class="pdfMenuOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
              </svg>
            </button>
            <div
              v-show="pdfMenuOpen"
              class="absolute right-0 top-full mt-1 bg-neutral-900 ring-1 ring-white/10 rounded-xl py-1 min-w-44 z-50 shadow-xl"
            >
              <a
                v-for="opt in PDF_OPTS"
                :key="opt.key"
                :href="opt.key === 'crm' ? `/onboarding/${id}/print-crm` : `/onboarding/${id}/print?section=${opt.key}`"
                target="_blank"
                class="flex items-center gap-2 px-3 py-2.5 text-sm text-white/60 hover:text-white hover:bg-white/5 transition-colors"
                @click="pdfMenuOpen = false"
              >
                {{ opt.label }}
              </a>
            </div>
          </div>
          <button
            v-if="!isDesenvolvedor"
            class="px-3 py-1.5 text-sm text-white/50 hover:text-white/80 border border-white/10 rounded-lg transition-all disabled:opacity-40"
            :disabled="materialsGenerating"
            @click="handleRegenerate"
          >
            {{ materialsGenerating ? 'Gerando...' : 'Regenerar' }}
          </button>
        </div>
      </div>
    </div>

    <div class="max-w-4xl mx-auto px-6 py-8 pb-24">

      <!-- Generating state -->
      <div v-if="generating" class="flex flex-col items-center py-24 gap-4">
        <svg class="w-8 h-8 text-white/30 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
        </svg>
        <p class="text-white/40 text-sm">Regenerando materiais... (~20–30s)</p>
      </div>

      <!-- Not generated -->
      <div v-else-if="!materials || materials.status !== 'complete'" class="flex flex-col items-center py-24 gap-4">
        <p class="text-white/40 text-sm">Material ainda não gerado.</p>
        <NuxtLink :to="`/onboarding/${id}`" class="text-sm text-white/60 underline underline-offset-4">Voltar ao formulário</NuxtLink>
      </div>

      <!-- Content -->
      <template v-else-if="editedMaterials">

        <!-- Quality alerts banner (colapsável) -->
        <div v-if="materials.quality_alerts?.length" class="mb-6 bg-amber-400/5 ring-1 ring-amber-400/10 rounded-2xl overflow-hidden">
          <button
            class="w-full flex items-center justify-between px-4 py-3 text-sm text-amber-300/70 hover:text-amber-300/90 transition-colors"
            @click="alertsOpen = !alertsOpen"
          >
            <span class="flex items-center gap-2 font-medium">
              <span>⚠</span>
              {{ materials.quality_alerts.length }} alerta{{ materials.quality_alerts.length > 1 ? 's' : '' }} de qualidade
            </span>
            <svg class="w-4 h-4 transition-transform" :class="alertsOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          <div v-show="alertsOpen" class="border-t border-amber-400/10 px-4 py-3 space-y-2">
            <p v-for="alert in materials.quality_alerts" :key="alert" class="text-sm text-amber-300/60 flex gap-2">
              <span class="shrink-0">·</span>
              <span>{{ alert }}</span>
            </p>
          </div>
        </div>

        <!-- Tabs -->
        <div class="flex gap-1 p-1 bg-white/5 rounded-xl mb-6 w-fit">
          <button
            v-for="t in TABS"
            :key="t.key"
            class="px-5 py-2 rounded-lg text-sm font-medium transition-all"
            :class="activeTab === t.key ? 'bg-white text-neutral-900' : 'text-white/50 hover:text-white/80'"
            @click="activeTab = t.key as any"
          >
            {{ t.label }}
          </button>
        </div>

        <!-- ── CRM ── -->
        <div v-show="activeTab === 'crm'" :inert="isDesenvolvedor || undefined">
          <!-- Seletor de etapa -->
          <div class="flex gap-1 flex-wrap mb-5">
            <button
              v-for="(stage, si) in editedMaterials.crm!.stages"
              :key="si"
              class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all"
              :class="activeStage === si
                ? 'bg-white/10 text-white ring-1 ring-white/20'
                : 'text-white/40 hover:text-white/70 hover:bg-white/5'"
              @click="activeStage = si"
            >
              <span class="text-white/30">{{ si + 1 }}</span>
              {{ stage.name || 'Etapa ' + (si + 1) }}
            </button>
          </div>

          <!-- Conteúdo da etapa selecionada -->
          <template v-if="editedMaterials.crm!.stages[activeStage]">
            <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5 space-y-5">
              <!-- Nome -->
              <div class="flex items-center gap-3">
                <span class="text-xs font-bold text-white/20 w-5 text-center shrink-0">{{ activeStage + 1 }}</span>
                <input
                  v-model="editedMaterials.crm!.stages[activeStage].name"
                  placeholder="Nome da etapa"
                  class="flex-1 bg-transparent text-base font-semibold text-white placeholder-white/20 focus:outline-none border-b border-white/10 pb-1"
                />
              </div>

              <div class="grid grid-cols-2 gap-4">
                <div>
                  <p class="text-xs text-white/30 mb-1.5">Objetivo</p>
                  <textarea v-model="editedMaterials.crm!.stages[activeStage].objective" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                </div>
                <div>
                  <p class="text-xs text-white/30 mb-1.5">Critério de avanço</p>
                  <textarea v-model="editedMaterials.crm!.stages[activeStage].advance_criteria" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                </div>
              </div>

              <div>
                <p class="text-xs text-white/20 mb-1.5">Instruções para o dev</p>
                <textarea v-model="editedMaterials.crm!.stages[activeStage].dev_instructions" class="w-full px-3 py-2 bg-white/[0.02] border border-white/[0.06] rounded-xl text-xs text-white/40 focus:outline-none focus:border-white/10 transition-colors resize-y" rows="3" />
              </div>

              <!-- Cadência -->
              <div class="border-t border-white/[0.06] pt-4">
                <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-4">Cadência</p>
                <div
                  v-for="(day, di) in editedMaterials.crm!.stages[activeStage].cadence"
                  :key="di"
                  class="mb-5"
                >
                  <p class="text-xs font-bold text-white/30 mb-3">Dia {{ day.day }}</p>
                  <div v-for="(action, ai) in day.actions" :key="ai" class="mb-4 pl-4 border-l border-white/[0.08] space-y-2">
                    <span class="inline-flex text-xs px-2 py-0.5 bg-white/5 rounded-full text-white/40 capitalize border border-white/[0.06]">{{ action.channel }}</span>
                    <textarea v-model="action.message" placeholder="Mensagem" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                    <textarea v-if="action.instructions !== undefined" v-model="action.instructions" placeholder="Instruções" class="w-full px-3 py-2 bg-white/[0.02] border border-white/[0.06] rounded-xl text-xs text-white/40 focus:outline-none resize-y" rows="2" />
                  </div>
                </div>
              </div>
            </div>

            <!-- Navegação entre etapas -->
            <div class="flex justify-between mt-4">
              <button
                v-if="activeStage > 0"
                class="flex items-center gap-2 px-4 py-2 text-sm text-white/40 hover:text-white/70 border border-white/10 rounded-xl transition-all"
                @click="activeStage--"
              >
                ← {{ editedMaterials.crm!.stages[activeStage - 1].name || 'Anterior' }}
              </button>
              <div v-else />
              <button
                v-if="activeStage < editedMaterials.crm!.stages.length - 1"
                class="flex items-center gap-2 px-4 py-2 text-sm text-white/40 hover:text-white/70 border border-white/10 rounded-xl transition-all"
                @click="activeStage++"
              >
                {{ editedMaterials.crm!.stages[activeStage + 1].name || 'Próxima' }} →
              </button>
            </div>
          </template>
        </div>

        <!-- ── Fechamento ── -->
        <div v-show="activeTab === 'fechamento'" class="space-y-4" :inert="isDesenvolvedor || undefined">
          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Perguntas de diagnóstico</p>
            <div v-for="(q, qi) in editedMaterials.closing!.diagnostic_questions" :key="qi" class="flex gap-2 mb-2">
              <textarea v-model="editedMaterials.closing!.diagnostic_questions[qi]" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="3" />
              <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.closing!.diagnostic_questions.splice(qi, 1)">×</button>
            </div>
            <button class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all mt-1" @click="editedMaterials.closing!.diagnostic_questions.push('')">+ Adicionar pergunta</button>
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Apresentação de preço</p>
            <textarea v-model="editedMaterials.closing!.price_presentation" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="8" />
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Matriz de objeções</p>
            <div class="grid grid-cols-3 gap-2 mb-2 px-1">
              <p class="text-xs text-white/20">Objeção</p>
              <p class="text-xs text-white/20">Medo real</p>
              <p class="text-xs text-white/20">Contra-argumento</p>
            </div>
            <div v-for="(row, ri) in editedMaterials.closing!.objection_matrix" :key="ri" class="grid grid-cols-3 gap-2 mb-2 items-start">
              <textarea v-model="row.objection" class="px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
              <textarea v-model="row.hidden_concern" class="px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
              <div class="flex gap-1">
                <textarea v-model="row.counter_script" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
                <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.closing!.objection_matrix.splice(ri, 1)">×</button>
              </div>
            </div>
            <button class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.closing!.objection_matrix.push({ objection: '', hidden_concern: '', counter_script: '' })">+ Adicionar objeção</button>
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Script de fechamento</p>
            <textarea v-model="editedMaterials.closing!.closing_script" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="16" />
          </div>

          <div v-if="editedMaterials.closing!.special_condition" class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Condição especial</p>
            <textarea v-model="editedMaterials.closing!.special_condition" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
          </div>
        </div>

        <!-- ── Qualificação ── -->
        <div v-show="activeTab === 'qualificacao'" class="space-y-4" :inert="isDesenvolvedor || undefined">
          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <div class="flex items-center justify-between mb-3">
              <p class="text-xs font-semibold text-white/30 uppercase tracking-widest">Fluxo WhatsApp</p>
              <span class="text-xs px-2 py-0.5 bg-white/5 rounded-full text-white/30 capitalize">{{ editedMaterials.qualification!.profile }}</span>
            </div>
            <div v-for="(s, si) in editedMaterials.qualification!.whatsapp_flow" :key="si" class="mb-3 flex gap-3 items-start">
              <div class="shrink-0 pt-2">
                <span class="text-xs px-2 py-0.5 bg-white/5 rounded-full text-white/40 capitalize block text-center">{{ s.type }}</span>
                <span v-if="s.channel" class="text-xs text-white/20 block text-center mt-1">{{ s.channel }}</span>
              </div>
              <textarea v-model="s.content" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="5" />
              <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg mt-2 shrink-0" @click="editedMaterials.qualification!.whatsapp_flow.splice(si, 1)">×</button>
            </div>
            <button class="w-full py-2.5 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.qualification!.whatsapp_flow.push({ type: 'message', content: '' })">+ Adicionar step</button>
          </div>

          <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
            <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Pitch de ligação</p>
            <textarea v-model="editedMaterials.qualification!.call_pitch" class="w-full px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-y" rows="12" />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
              <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Critérios de avanço</p>
              <div v-for="(c, ci) in editedMaterials.qualification!.advance_criteria" :key="ci" class="flex gap-2 mb-2">
                <textarea v-model="editedMaterials.qualification!.advance_criteria[ci]" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="4" />
                <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.qualification!.advance_criteria.splice(ci, 1)">×</button>
              </div>
              <button class="w-full py-2 border border-dashed border-white/10 rounded-xl text-xs text-white/30 hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.qualification!.advance_criteria.push('')">+ Adicionar</button>
            </div>

            <div class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-5">
              <p class="text-xs font-semibold text-white/30 uppercase tracking-widest mb-3">Critérios de desqualificação</p>
              <div v-for="(c, ci) in editedMaterials.qualification!.disqualification_criteria" :key="ci" class="flex gap-2 mb-2">
                <textarea v-model="editedMaterials.qualification!.disqualification_criteria[ci]" class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20 transition-colors resize-y" rows="4" />
                <button class="text-white/20 hover:text-red-400/60 transition-colors text-lg self-start mt-1 shrink-0" @click="editedMaterials.qualification!.disqualification_criteria.splice(ci, 1)">×</button>
              </div>
              <button class="w-full py-2 border border-dashed border-white/10 rounded-xl text-xs text-white/30 hover:border-white/20 hover:text-white/50 transition-all" @click="editedMaterials.qualification!.disqualification_criteria.push('')">+ Adicionar</button>
            </div>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MaterialOut } from '~/composables/useOnboarding'

definePageMeta({ layout: false })

const route = useRoute()
const id = route.params.id as string

const { materials, materialsGenerating, loadMaterials, generateMaterials, saveMaterials, dealName, load } = useOnboarding(id)

const { user } = useAuth()
const isDesenvolvedor = computed(() => user.value?.roles?.includes('Desenvolvedor') && !user.value?.is_superuser)

const activeTab = ref<'crm' | 'fechamento' | 'qualificacao'>('crm')
const activeStage = ref(0)
const alertsOpen = ref(false)
const pdfMenuOpen = ref(false)
const pdfDropdownRef = ref<HTMLElement | null>(null)

const PDF_OPTS = [
  { key: 'crm', label: 'Script CRM' },
  { key: 'fechamento', label: 'Fechamento' },
  { key: 'qualificacao', label: 'Qualificação' },
]
const editedMaterials = ref<MaterialOut | null>(null)
const saveStatus = ref<'idle' | 'saving' | 'saved'>('idle')
const generating = ref(false)

const TABS = [
  { key: 'crm', label: 'CRM' },
  { key: 'fechamento', label: 'Fechamento' },
  { key: 'qualificacao', label: 'Qualificação' },
]

let _initialized = false
let _saveTimer: ReturnType<typeof setTimeout> | null = null

watch(materials, (m) => {
  if (m?.status === 'complete' && m.crm) {
    _initialized = false
    editedMaterials.value = JSON.parse(JSON.stringify(m))
    nextTick(() => { _initialized = true })
  }
}, { immediate: true })

watch(editedMaterials, () => {
  if (!_initialized || !editedMaterials.value || isDesenvolvedor.value) return
  saveStatus.value = 'saving'
  if (_saveTimer) clearTimeout(_saveTimer)
  _saveTimer = setTimeout(async () => {
    if (!editedMaterials.value) return
    await saveMaterials({
      crm: editedMaterials.value.crm,
      closing: editedMaterials.value.closing,
      qualification: editedMaterials.value.qualification,
    })
    saveStatus.value = 'saved'
    setTimeout(() => { saveStatus.value = 'idle' }, 2000)
  }, 1000)
}, { deep: true })

const handleRegenerate = async () => {
  generating.value = true
  await generateMaterials()
  generating.value = false
}

onMounted(async () => {
  await load()
  await loadMaterials()
  document.addEventListener('click', (e) => {
    if (pdfDropdownRef.value && !pdfDropdownRef.value.contains(e.target as Node)) {
      pdfMenuOpen.value = false
    }
  })
})
</script>
