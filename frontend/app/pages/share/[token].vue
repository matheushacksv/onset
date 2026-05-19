<template>
  <div class="min-h-screen bg-[#f3ede0] text-[#1c1917] font-sans">

    <!-- ── Loading ── -->
    <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
      <div class="w-7 h-7 rounded-full border-2 border-[#4d7c58]/30 border-t-[#4d7c58] animate-spin" />
    </div>

    <!-- ── Senha ── -->
    <div v-else-if="view === 'password'" class="min-h-screen flex items-center justify-center px-6">
      <div class="w-full max-w-sm bg-white rounded-2xl border border-[#e2d8c5] p-8 shadow-sm">
        <div class="w-10 h-10 rounded-xl bg-[#2c3f31] text-[#f3ede0] flex items-center justify-center font-bold mb-5">GE</div>
        <h1 class="text-lg font-semibold">{{ dealName || 'Material protegido' }}</h1>
        <p class="text-sm text-[#5a5048] mt-1 mb-5">Esse material é protegido. Informe a senha para visualizar.</p>
        <form @submit.prevent="onUnlock">
          <input
            v-model="pwd"
            type="password"
            placeholder="Senha"
            class="w-full px-3.5 py-2.5 rounded-xl border border-[#e2d8c5] bg-[#f9f5ef] text-sm focus:outline-none focus:border-[#4d7c58]"
          />
          <p v-if="unlockError" class="text-xs text-[#b83030] mt-2">{{ unlockError }}</p>
          <button
            type="submit"
            :disabled="unlocking || !pwd"
            class="mt-4 w-full py-2.5 rounded-xl bg-[#2c3f31] text-[#f3ede0] text-sm font-medium disabled:opacity-40"
          >
            {{ unlocking ? 'Verificando...' : 'Acessar material' }}
          </button>
        </form>
      </div>
    </div>

    <!-- ── Expirado / não encontrado / erro ── -->
    <div v-else-if="view === 'expired' || view === 'notfound' || view === 'error'" class="min-h-screen flex items-center justify-center px-6">
      <div class="text-center max-w-sm">
        <div class="w-12 h-12 rounded-2xl bg-[#e2d8c5] flex items-center justify-center mx-auto mb-5 text-2xl">·</div>
        <h1 class="text-lg font-semibold">
          {{ view === 'expired' ? 'Link indisponível' : view === 'notfound' ? 'Link não encontrado' : 'Algo deu errado' }}
        </h1>
        <p class="text-sm text-[#5a5048] mt-2">
          {{ view === 'expired'
            ? 'Esse link de visualização expirou ou foi revogado. Solicite um novo ao seu assessor.'
            : view === 'notfound'
              ? 'Esse link não existe. Confira o endereço.'
              : 'Não foi possível carregar o material. Tente novamente em instantes.' }}
        </p>
      </div>
    </div>

    <!-- ── Viewer ── -->
    <template v-else-if="view === 'ready' && material">
      <!-- Header -->
      <header class="sticky top-0 z-30 bg-[#f3ede0]/90 backdrop-blur-xl border-b border-[#e2d8c5]">
        <div class="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <div class="w-8 h-8 rounded-lg bg-[#2c3f31] text-[#f3ede0] flex items-center justify-center text-xs font-bold shrink-0">GE</div>
            <div class="min-w-0">
              <p class="text-sm font-semibold truncate">{{ material.deal_name }}</p>
              <p class="text-xs text-[#9a9088]">Material de vendas · Grupo Enriquecedor</p>
            </div>
          </div>
          <a
            :href="pdfUrl('master')"
            target="_blank"
            class="shrink-0 px-3.5 py-1.5 rounded-full border border-[#e2d8c5] text-sm text-[#5a5048] hover:border-[#4d7c58] hover:text-[#1c1917] transition-colors"
          >
            Baixar PDF
          </a>
        </div>
        <!-- Tabs -->
        <div class="max-w-6xl mx-auto px-6 pb-3 flex gap-1">
          <button
            v-for="t in tabs"
            :key="t.key"
            class="px-4 py-1.5 rounded-full text-sm font-medium transition-colors"
            :class="tab === t.key ? 'bg-[#2c3f31] text-[#f3ede0]' : 'text-[#5a5048] hover:bg-white/60'"
            @click="tab = t.key"
          >
            {{ t.label }}
          </button>
        </div>
      </header>

      <!-- ── CRM ── -->
      <section v-show="tab === 'crm'">
        <div class="max-w-6xl mx-auto px-6 pt-5 flex items-center gap-2 flex-wrap">
          <span class="text-xs font-semibold text-[#9a9088] uppercase tracking-widest mr-1">Funil</span>
          <button
            v-for="(f, fi) in funnels"
            :key="fi"
            class="px-3 py-1.5 rounded-full text-xs font-medium transition-colors"
            :class="activeFunnel === fi ? 'bg-[#4d7c58] text-white' : 'bg-white border border-[#e2d8c5] text-[#5a5048]'"
            @click="activeFunnel = fi"
          >
            {{ f.name || f.key || 'Funil ' + (fi + 1) }}
          </button>
          <span class="w-px h-4 bg-[#e2d8c5] mx-1" />
          <span class="text-xs font-semibold text-[#9a9088] uppercase tracking-widest mr-1">Canal</span>
          <button
            v-for="c in channelFilters"
            :key="c"
            class="px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors capitalize"
            :class="channelFilter === c ? 'bg-[#4d7c58] text-white' : 'bg-white border border-[#e2d8c5] text-[#5a5048]'"
            @click="channelFilter = channelFilter === c ? '' : c"
          >
            {{ c }}
          </button>
        </div>

        <!-- Board pannable -->
        <div
          class="relative mt-4 overflow-hidden cursor-grab select-none"
          :class="dragging ? 'cursor-grabbing' : ''"
          style="height: calc(100vh - 168px)"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
        >
          <div class="absolute top-0 left-0 origin-top-left p-8" :style="{ transform }">
            <div v-if="currentFunnel" class="flex gap-4 items-start">
              <div
                v-for="(stage, si) in currentFunnel.stages"
                :key="si"
                class="w-[300px] shrink-0 bg-white rounded-2xl border border-[#e2d8c5]"
              >
                <div class="flex items-center gap-2.5 px-4 py-3 border-b-2 border-[#4d7c58]">
                  <span class="w-6 h-6 rounded-md bg-[#edf7f1] text-[#3a6a4a] text-xs font-bold flex items-center justify-center shrink-0">{{ si + 1 }}</span>
                  <span class="text-sm font-semibold leading-tight">{{ stage.name || 'Etapa ' + (si + 1) }}</span>
                </div>
                <div class="p-4 space-y-3">
                  <div class="rounded-xl bg-[#edf7f1] border-l-[3px] border-[#4d7c58] px-3 py-2.5">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-[#4d7c58] mb-1">Objetivo</p>
                    <p class="text-[13px] leading-relaxed text-[#5a5048] whitespace-pre-wrap">{{ stage.objective || '—' }}</p>
                  </div>
                  <div class="rounded-xl bg-[#edf3fc] border-l-[3px] border-[#3a6a4a] px-3 py-2.5">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-[#3a6a4a] mb-1">Critério de avanço</p>
                    <p class="text-[13px] leading-relaxed text-[#5a5048] whitespace-pre-wrap">{{ stage.advance_criteria || '—' }}</p>
                  </div>
                  <div v-if="stage.loss_reason" class="rounded-xl bg-[#fef0f0] border-l-[3px] border-[#b83030] px-3 py-2.5">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-[#b83030] mb-1">Motivo de perda</p>
                    <p class="text-[13px] leading-relaxed text-[#5a5048] whitespace-pre-wrap">{{ stage.loss_reason }}</p>
                  </div>

                  <div v-if="visibleCadence(stage).length">
                    <p class="text-[10px] font-bold uppercase tracking-wider text-[#9a9088] mt-1 mb-2">Cadência</p>
                    <div
                      v-for="(day, di) in visibleCadence(stage)"
                      :key="di"
                      class="mb-2.5"
                    >
                      <p class="text-[10px] font-bold uppercase tracking-wider text-[#1c1917] mb-1">Dia {{ day.day }}</p>
                      <div
                        v-for="(action, ai) in day.actions"
                        :key="ai"
                        class="rounded-xl border border-[#e2d8c5] bg-[#f9f5ef] px-3 py-2 mb-1.5"
                      >
                        <div class="flex items-center justify-between gap-2 mb-1.5">
                          <span
                            class="inline-block text-[9px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full border"
                            :class="badgeClass(action.channel)"
                          >{{ action.channel }}</span>
                          <button
                            class="text-[10px] font-medium text-[#4d7c58] hover:text-[#2c3f31] transition-colors shrink-0"
                            @click="copyText(action.message, `${si}-${di}-${ai}`)"
                          >
                            {{ copiedKey === `${si}-${di}-${ai}` ? '✓ Copiado' : 'Copiar' }}
                          </button>
                        </div>
                        <p class="text-[12px] leading-relaxed text-[#1c1917] whitespace-pre-wrap">{{ action.message }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Zoom controls -->
          <div class="absolute bottom-5 right-5 flex flex-col gap-1 bg-white border border-[#e2d8c5] rounded-xl p-1.5 shadow-sm">
            <button class="w-7 h-7 rounded-lg hover:bg-[#f9f5ef] text-[#5a5048] font-mono" @click="zoom(0.15)">+</button>
            <span class="text-[10px] text-center text-[#9a9088] font-semibold">{{ Math.round(scale * 100) }}%</span>
            <button class="w-7 h-7 rounded-lg hover:bg-[#f9f5ef] text-[#5a5048] font-mono" @click="zoom(-0.15)">−</button>
            <button class="w-7 h-7 rounded-lg hover:bg-[#f9f5ef] text-[#9a9088] text-xs" title="Resetar" @click="reset">↺</button>
          </div>
          <p class="absolute bottom-5 left-5 text-xs text-[#9a9088]">Arraste para navegar · role o zoom nos controles</p>
        </div>
      </section>

      <!-- ── Fechamento ── -->
      <section v-show="tab === 'fechamento'" class="max-w-3xl mx-auto px-6 py-8 space-y-5">
        <div v-if="material.closing?.diagnostic_questions?.length">
          <h2 class="share-h2">Perguntas de diagnóstico</h2>
          <ol class="space-y-1.5">
            <li
              v-for="(q, qi) in material.closing.diagnostic_questions"
              :key="qi"
              class="flex gap-3 py-2 border-b border-[#ede8dc] text-[14px]"
            >
              <span class="text-[#4d7c58] font-bold text-xs pt-0.5">{{ String(qi + 1).padStart(2, '0') }}</span>
              <span class="text-[#5a5048]">{{ q }}</span>
            </li>
          </ol>
        </div>
        <div v-if="material.closing?.price_presentation">
          <h2 class="share-h2">Apresentação de preço</h2>
          <div class="share-block">{{ material.closing.price_presentation }}</div>
        </div>
        <div v-if="material.closing?.objection_matrix?.length">
          <h2 class="share-h2">Matriz de objeções</h2>
          <div class="rounded-2xl border border-[#e2d8c5] overflow-hidden bg-white">
            <div
              v-for="(row, ri) in material.closing.objection_matrix"
              :key="ri"
              class="px-4 py-3 border-b border-[#ede8dc] last:border-0"
            >
              <p class="text-sm font-semibold text-[#1c1917]">{{ row.objection }}</p>
              <p class="text-xs text-[#9a9088] mt-0.5 mb-1.5">Medo real: {{ row.hidden_concern }}</p>
              <p class="text-[13px] text-[#5a5048] leading-relaxed">{{ row.counter_script }}</p>
            </div>
          </div>
        </div>
        <div v-if="material.closing?.closing_script">
          <h2 class="share-h2">Script de fechamento</h2>
          <div class="share-block">{{ material.closing.closing_script }}</div>
        </div>
        <div v-if="material.closing?.special_condition">
          <h2 class="share-h2">Condição especial</h2>
          <div class="rounded-2xl bg-[#edf3fc] border-l-[3px] border-[#3a6a4a] px-4 py-3 text-[14px] text-[#5a5048] whitespace-pre-wrap">{{ material.closing.special_condition }}</div>
        </div>
      </section>

      <!-- ── Qualificação ── -->
      <section v-show="tab === 'qualificacao'" class="max-w-3xl mx-auto px-6 py-8 space-y-5">
        <div v-if="material.qualification?.whatsapp_flow?.length">
          <h2 class="share-h2">Fluxo WhatsApp</h2>
          <div class="space-y-2.5">
            <div
              v-for="(step, si) in material.qualification.whatsapp_flow"
              :key="si"
              class="flex gap-3"
            >
              <span class="w-7 h-7 rounded-full bg-[#4d7c58] text-white text-xs font-bold flex items-center justify-center shrink-0">{{ String(si + 1).padStart(2, '0') }}</span>
              <div class="flex-1 rounded-2xl border border-[#e2d8c5] bg-white px-4 py-3">
                <span class="text-[10px] font-bold uppercase tracking-wider text-[#9a9088]">{{ step.type }}</span>
                <p class="text-[14px] text-[#5a5048] leading-relaxed mt-1 whitespace-pre-wrap">{{ step.content }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-if="material.qualification?.call_pitch">
          <h2 class="share-h2">Pitch de ligação</h2>
          <div class="share-block">{{ material.qualification.call_pitch }}</div>
        </div>
        <div v-if="material.qualification?.advance_criteria?.length || material.qualification?.disqualification_criteria?.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div v-if="material.qualification?.advance_criteria?.length" class="rounded-2xl border border-[#e2d8c5] border-l-[3px] border-l-[#4d7c58] bg-white px-4 py-3">
            <p class="text-[10px] font-bold uppercase tracking-wider text-[#4d7c58] mb-2">Avanço</p>
            <ul class="space-y-1.5">
              <li v-for="(c, ci) in material.qualification.advance_criteria" :key="ci" class="text-[13px] text-[#5a5048]">· {{ c }}</li>
            </ul>
          </div>
          <div v-if="material.qualification?.disqualification_criteria?.length" class="rounded-2xl border border-[#e2d8c5] border-l-[3px] border-l-[#b83030] bg-white px-4 py-3">
            <p class="text-[10px] font-bold uppercase tracking-wider text-[#b83030] mb-2">Desqualificação</p>
            <ul class="space-y-1.5">
              <li v-for="(c, ci) in material.qualification.disqualification_criteria" :key="ci" class="text-[13px] text-[#5a5048]">· {{ c }}</li>
            </ul>
          </div>
        </div>
      </section>

      <footer class="max-w-6xl mx-auto px-6 py-6 text-center text-xs text-[#9a9088] border-t border-[#e2d8c5] mt-4">
        Grupo Enriquecedor · Material gerado em {{ formatDate(material.generated_at) }}
      </footer>
    </template>
  </div>
</template>

<script setup lang="ts">
import type { PipelineStage, CadenceDay } from '~/composables/useOnboarding'

definePageMeta({ layout: false })
useHead({ title: 'Material de Vendas' })

const route = useRoute()
const token = route.params.token as string

const { view, material, dealName, unlocking, unlockError, load, unlock, pdfUrl } = useSharedMaterial(token)
const { scale, transform, dragging, onPointerDown, onPointerMove, onPointerUp, zoom, reset } = usePanZoom({ initial: 0.8 })

const pwd = ref('')
const tab = ref<'crm' | 'fechamento' | 'qualificacao'>('crm')
const activeFunnel = ref(0)
const channelFilter = ref('')

const tabs = [
  { key: 'crm' as const, label: 'Funil CRM' },
  { key: 'fechamento' as const, label: 'Fechamento' },
  { key: 'qualificacao' as const, label: 'Qualificação' },
]

const funnels = computed(() => material.value?.crm?.funnels ?? [])
const currentFunnel = computed(() => funnels.value[activeFunnel.value] ?? null)

const channelFilters = computed(() => {
  const set = new Set<string>()
  for (const f of funnels.value)
    for (const s of f.stages)
      for (const d of s.cadence || [])
        for (const a of d.actions || [])
          if (a.channel) set.add(a.channel)
  return [...set]
})

function visibleCadence(stage: PipelineStage): CadenceDay[] {
  const cadence = stage.cadence || []
  if (!channelFilter.value) return cadence
  return cadence
    .map(d => ({ ...d, actions: (d.actions || []).filter(a => a.channel === channelFilter.value) }))
    .filter(d => d.actions.length)
}

function badgeClass(channel: string) {
  const c = (channel || '').toLowerCase()
  if (c.includes('whats')) return 'bg-[#e6f9ee] border-[#80d4a0] text-[#1a7a3a]'
  if (c.includes('lig')) return 'bg-[#edf3fc] border-[#90b8f0] text-[#3a6a4a]'
  if (c.includes('mail')) return 'bg-[#fff3e0] border-[#f0c060] text-[#a06010]'
  if (c.includes('auto')) return 'bg-[#f0ecfc] border-[#c0a8f0] text-[#6040b0]'
  return 'bg-[#f9f5ef] border-[#e2d8c5] text-[#5a5048]'
}

const copiedKey = ref('')
function copyText(text: string, key: string) {
  navigator.clipboard.writeText(text || '')
  copiedKey.value = key
  setTimeout(() => { if (copiedKey.value === key) copiedKey.value = '' }, 1800)
}

function formatDate(iso: string) {
  try { return new Date(iso).toLocaleDateString('pt-BR') } catch { return '' }
}

async function onUnlock() {
  await unlock(pwd.value)
}

onMounted(load)
</script>

<style scoped>
.share-h2 {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #3a6a4a;
  border-bottom: 2px solid #4d7c58;
  padding-bottom: 4px;
  margin-bottom: 12px;
  display: inline-block;
}
.share-block {
  background: #fff;
  border: 1px solid #e2d8c5;
  border-left: 3px solid #4d7c58;
  border-radius: 14px;
  padding: 16px 18px;
  font-size: 14px;
  line-height: 1.65;
  color: #1c1917;
  white-space: pre-wrap;
}
</style>
