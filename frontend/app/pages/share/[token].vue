<template>
  <div class="min-h-screen bg-[var(--bg)] text-[color:var(--text)]" :style="rootStyle">

    <!-- ── Loading ── -->
    <div v-if="view === 'loading'" class="min-h-screen flex items-center justify-center">
      <div class="w-7 h-7 rounded-full border-2 border-[var(--border)] border-t-[var(--accent)] animate-spin" />
    </div>

    <!-- ── Senha ── -->
    <div v-else-if="view === 'password'" class="min-h-screen flex items-center justify-center px-6">
      <div class="w-full max-w-sm bg-[var(--surface)] rounded-2xl border border-[var(--border)] p-8 shadow-sm">
        <img src="/favicon.svg" alt="Grupo Enriquecedor" class="w-16 h-16 object-contain mb-5" />
        <h1 class="text-lg font-semibold">{{ dealName || 'Material protegido' }}</h1>
        <p class="text-sm text-[color:var(--dim)] mt-1 mb-5">Esse material é protegido. Informe a senha para visualizar.</p>
        <form @submit.prevent="onUnlock">
          <input
            v-model="pwd"
            type="password"
            placeholder="Senha"
            class="w-full px-3.5 py-2.5 rounded-xl border border-[var(--border)] bg-[var(--s2)] text-sm focus:outline-none focus:border-[var(--accent)]"
          />
          <p v-if="unlockError" class="text-xs text-[color:var(--red)] mt-2">{{ unlockError }}</p>
          <button
            type="submit"
            :disabled="unlocking || !pwd"
            class="mt-4 w-full py-2.5 rounded-xl bg-[var(--accent-d)] text-[color:var(--on-accent)] text-sm font-medium disabled:opacity-40"
          >
            {{ unlocking ? 'Verificando...' : 'Acessar material' }}
          </button>
        </form>
      </div>
    </div>

    <!-- ── Expirado / não encontrado / erro ── -->
    <div v-else-if="view === 'expired' || view === 'notfound' || view === 'error'" class="min-h-screen flex items-center justify-center px-6">
      <div class="text-center max-w-sm">
        <div class="w-12 h-12 rounded-2xl bg-[var(--border)] flex items-center justify-center mx-auto mb-5 text-2xl">·</div>
        <h1 class="text-lg font-semibold">
          {{ view === 'expired' ? 'Link indisponível' : view === 'notfound' ? 'Link não encontrado' : 'Algo deu errado' }}
        </h1>
        <p class="text-sm text-[color:var(--dim)] mt-2">
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
      <header class="sticky top-0 z-30 bg-[var(--bg)] backdrop-blur-xl border-b border-[var(--border)]">
        <div class="max-w-6xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
          <div class="flex items-center gap-3 min-w-0">
            <img src="/favicon.svg" alt="Grupo Enriquecedor" class="w-12 h-12 object-contain shrink-0" />
            <div class="min-w-0">
              <p class="text-sm font-semibold truncate">{{ material.deal_name }}</p>
              <p class="text-xs text-[color:var(--muted)]">Material de vendas · Grupo Enriquecedor</p>
            </div>
          </div>
          <a
            :href="pdfUrl('master')"
            target="_blank"
            class="shrink-0 px-3.5 py-1.5 rounded-full border border-[var(--border)] text-sm text-[color:var(--dim)] hover:border-[var(--accent)] hover:text-[color:var(--text)] transition-colors"
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
            :class="tab === t.key ? 'bg-[var(--accent-d)] text-[color:var(--on-accent)]' : 'text-[color:var(--dim)] hover:bg-[var(--s2)]'"
            @click="tab = t.key"
          >
            {{ t.label }}
          </button>
        </div>
      </header>

      <!-- ── CRM ── -->
      <section v-show="tab === 'crm'">
        <!-- Filtros: scroll-x no mobile, wrap no desktop -->
        <div class="max-w-6xl mx-auto px-6 pt-5 flex items-center gap-2 overflow-x-auto sm:flex-wrap [&::-webkit-scrollbar]:hidden [scrollbar-width:none]">
          <span class="text-xs font-semibold text-[color:var(--muted)] uppercase tracking-widest mr-1 shrink-0">Funil</span>
          <button
            v-for="(f, fi) in funnels"
            :key="fi"
            class="px-3 py-1.5 rounded-full text-xs font-medium transition-colors shrink-0"
            :class="activeFunnel === fi ? 'bg-[var(--accent)] text-[color:var(--on-accent)]' : 'bg-[var(--surface)] border border-[var(--border)] text-[color:var(--dim)]'"
            @click="activeFunnel = fi"
          >
            {{ f.name || f.key || 'Funil ' + (fi + 1) }}
          </button>
          <span class="w-px h-4 bg-[var(--border)] mx-1 shrink-0" />
          <span class="text-xs font-semibold text-[color:var(--muted)] uppercase tracking-widest mr-1 shrink-0">Canal</span>
          <button
            v-for="c in channelFilters"
            :key="c"
            class="px-2.5 py-1 rounded-full text-[11px] font-medium transition-colors capitalize shrink-0"
            :class="channelFilter === c ? 'bg-[var(--accent)] text-[color:var(--on-accent)]' : 'bg-[var(--surface)] border border-[var(--border)] text-[color:var(--dim)]'"
            @click="channelFilter = channelFilter === c ? '' : c"
          >
            {{ c }}
          </button>
        </div>

        <!-- Desktop: board pannable (pan/zoom) -->
        <div
          class="relative mt-4 overflow-hidden cursor-grab select-none hidden sm:block"
          :class="dragging ? 'cursor-grabbing' : ''"
          style="height: calc(100vh - 168px)"
          @pointerdown="onPointerDown"
          @pointermove="onPointerMove"
          @pointerup="onPointerUp"
          @pointercancel="onPointerUp"
        >
          <div class="absolute top-0 left-0 origin-top-left p-8" :style="{ transform }">
            <div v-if="currentFunnel" class="flex gap-4 items-start">
              <ShareStageCard
                v-for="(stage, si) in currentFunnel.stages"
                :key="si"
                :stage="stage"
                :index="si"
                :channel-filter="channelFilter"
                :copied-key="copiedKey"
                class="w-[300px] shrink-0"
                @copy="copyText"
              />
            </div>
          </div>

          <!-- Zoom controls -->
          <div class="absolute bottom-5 right-5 flex flex-col gap-1 bg-[var(--surface)] border border-[var(--border)] rounded-xl p-1.5 shadow-sm">
            <button class="w-7 h-7 rounded-lg hover:bg-[var(--s2)] text-[color:var(--dim)] font-mono" @click="zoom(0.15)">+</button>
            <span class="text-[10px] text-center text-[color:var(--muted)] font-semibold">{{ Math.round(scale * 100) }}%</span>
            <button class="w-7 h-7 rounded-lg hover:bg-[var(--s2)] text-[color:var(--dim)] font-mono" @click="zoom(-0.15)">−</button>
            <button class="w-7 h-7 rounded-lg hover:bg-[var(--s2)] text-[color:var(--muted)] text-xs" title="Resetar" @click="reset">↺</button>
          </div>
          <p class="absolute bottom-5 left-5 text-xs text-[color:var(--muted)]">Arraste para navegar · role o zoom nos controles</p>
        </div>

        <!-- Mobile: carrossel scroll-snap (1 etapa por tela, swipe lateral, scroll vertical interno) -->
        <div v-if="currentFunnel" class="sm:hidden mt-4">
          <div class="flex gap-3 overflow-x-auto snap-x snap-mandatory px-4 pb-3 scroll-px-4 [&::-webkit-scrollbar]:hidden [scrollbar-width:none]">
            <ShareStageCard
              v-for="(stage, si) in currentFunnel.stages"
              :key="si"
              :stage="stage"
              :index="si"
              :channel-filter="channelFilter"
              :copied-key="copiedKey"
              class="w-[calc(100vw-2rem)] max-w-[420px] shrink-0 snap-start max-h-[calc(100dvh-210px)]"
              @copy="copyText"
            />
          </div>
          <p class="text-center text-xs text-[color:var(--muted)] pb-5 pt-1">
            {{ currentFunnel.stages.length }} etapas · deslize para o lado
          </p>
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
              class="flex gap-3 py-2 border-b border-[var(--border)] text-[14px]"
            >
              <span class="text-[color:var(--accent)] font-bold text-xs pt-0.5">{{ String(qi + 1).padStart(2, '0') }}</span>
              <span class="text-[color:var(--dim)]">{{ q }}</span>
            </li>
          </ol>
        </div>
        <div v-if="material.closing?.price_presentation">
          <h2 class="share-h2">Apresentação de preço</h2>
          <div class="share-block">{{ material.closing.price_presentation }}</div>
        </div>
        <div v-if="material.closing?.objection_matrix?.length">
          <h2 class="share-h2">Matriz de objeções</h2>
          <div class="rounded-2xl border border-[var(--border)] overflow-hidden bg-[var(--surface)]">
            <div
              v-for="(row, ri) in material.closing.objection_matrix"
              :key="ri"
              class="px-4 py-3 border-b border-[var(--border)] last:border-0"
            >
              <p class="text-sm font-semibold text-[color:var(--text)]">{{ row.objection }}</p>
              <p class="text-xs text-[color:var(--muted)] mt-0.5 mb-1.5">Medo real: {{ row.hidden_concern }}</p>
              <p class="text-[13px] text-[color:var(--dim)] leading-relaxed">{{ row.counter_script }}</p>
            </div>
          </div>
        </div>
        <div v-if="material.closing?.closing_script">
          <h2 class="share-h2">Script de fechamento</h2>
          <div class="share-block">{{ material.closing.closing_script }}</div>
        </div>
        <div v-if="material.closing?.special_condition">
          <h2 class="share-h2">Condição especial</h2>
          <div class="rounded-2xl bg-[var(--blue-bg)] border-l-[3px] border-[var(--accent2)] px-4 py-3 text-[14px] text-[color:var(--dim)] whitespace-pre-wrap">{{ material.closing.special_condition }}</div>
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
              <span class="w-7 h-7 rounded-full bg-[var(--accent)] text-[color:var(--on-accent)] text-xs font-bold flex items-center justify-center shrink-0">{{ String(si + 1).padStart(2, '0') }}</span>
              <div class="flex-1 rounded-2xl border border-[var(--border)] bg-[var(--surface)] px-4 py-3">
                <span class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--muted)]">{{ step.type }}</span>
                <p class="text-[14px] text-[color:var(--dim)] leading-relaxed mt-1 whitespace-pre-wrap">{{ step.content }}</p>
              </div>
            </div>
          </div>
        </div>
        <div v-if="material.qualification?.call_pitch">
          <h2 class="share-h2">Pitch de ligação</h2>
          <div class="share-block">{{ material.qualification.call_pitch }}</div>
        </div>
        <div v-if="material.qualification?.advance_criteria?.length || material.qualification?.disqualification_criteria?.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div v-if="material.qualification?.advance_criteria?.length" class="rounded-2xl border border-[var(--border)] border-l-[3px] border-l-[var(--accent)] bg-[var(--surface)] px-4 py-3">
            <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--accent)] mb-2">Avanço</p>
            <ul class="space-y-1.5">
              <li v-for="(c, ci) in material.qualification.advance_criteria" :key="ci" class="text-[13px] text-[color:var(--dim)]">· {{ c }}</li>
            </ul>
          </div>
          <div v-if="material.qualification?.disqualification_criteria?.length" class="rounded-2xl border border-[var(--border)] border-l-[3px] border-l-[var(--red)] bg-[var(--surface)] px-4 py-3">
            <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--red)] mb-2">Desqualificação</p>
            <ul class="space-y-1.5">
              <li v-for="(c, ci) in material.qualification.disqualification_criteria" :key="ci" class="text-[13px] text-[color:var(--dim)]">· {{ c }}</li>
            </ul>
          </div>
        </div>
      </section>

      <footer class="max-w-6xl mx-auto px-6 py-6 text-center text-xs text-[color:var(--muted)] border-t border-[var(--border)] mt-4">
        Grupo Enriquecedor · Material gerado em {{ formatDate(material.generated_at) }}
      </footer>
    </template>
  </div>
</template>

<script setup lang="ts">
import { getShareTheme } from '~/utils/shareThemes'

definePageMeta({ layout: false })
useHead({ title: 'Material de Vendas' })

const route = useRoute()
const token = route.params.token as string

const { view, material, dealName, unlocking, unlockError, load, unlock, pdfUrl } = useSharedMaterial(token)
const { scale, transform, dragging, onPointerDown, onPointerMove, onPointerUp, zoom, reset } = usePanZoom({ initial: 0.8 })

// Tema (preset) do material — aplica cores + fonte via CSS vars na raiz.
const theme = computed(() => getShareTheme(material.value?.theme))
const rootStyle = computed(() => ({ ...theme.value.vars, fontFamily: theme.value.font }))

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
  color: var(--accent2);
  border-bottom: 2px solid var(--accent);
  padding-bottom: 4px;
  margin-bottom: 12px;
  display: inline-block;
}
.share-block {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--accent);
  border-radius: 14px;
  padding: 16px 18px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text);
  white-space: pre-wrap;
}
</style>
