<template>
  <div v-if="funnels.length === 0" class="text-center py-16 text-white/30 text-sm">
    Nenhum funil neste material.
  </div>
  <div v-else class="space-y-4">
    <!-- Tabs funis + busca -->
    <div class="flex items-center gap-2 border-b border-white/10">
      <div class="flex items-center gap-1 overflow-x-auto flex-1 min-w-0 scrollbar-none">
        <button
          v-for="(f, i) in funnels"
          :key="f.key"
          class="px-4 py-2 text-sm whitespace-nowrap border-b-2 transition-colors -mb-px"
          :class="i === activeFunnel ? 'text-white border-white' : 'text-white/40 border-transparent hover:text-white/70'"
          @click="setFunnel(i)"
        >
          {{ f.name || f.key }}
        </button>
      </div>
      <button
        class="shrink-0 mb-1 px-3 py-1.5 text-xs text-white/50 hover:text-white/80 hover:bg-white/5 rounded-lg flex items-center gap-2 transition-colors"
        @click="searchOpen = true"
      >
        <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
        </svg>
        Buscar
        <kbd class="text-[10px] text-white/30 px-1 py-0.5 bg-white/5 rounded">Ctrl K</kbd>
      </button>
    </div>

    <ObCrmSearchPalette
      :open="searchOpen"
      :crm="crm"
      @close="searchOpen = false"
      @pick="onPick"
    />

    <div v-if="currentFunnel">
      <div v-if="currentFunnel.stages.length === 0" class="text-center py-12 text-white/30 text-sm">
        Funil sem etapas.
      </div>
      <div v-else class="grid gap-4" style="grid-template-columns: 16rem 1fr;">
        <!-- Sidebar etapas -->
        <aside class="space-y-1">
          <button
            v-for="(stage, si) in currentFunnel.stages"
            :key="si"
            class="w-full text-left px-3 py-2 rounded-xl text-sm transition-colors"
            :class="si === activeStage
              ? 'bg-white/10 text-white ring-1 ring-white/20'
              : 'text-white/50 hover:text-white/80 hover:bg-white/5'"
            @click="activeStage = si"
          >
            <div class="flex items-center justify-between gap-2">
              <span class="truncate">{{ stage.name || `Etapa ${si + 1}` }}</span>
              <span class="text-[10px] text-white/30 shrink-0">{{ (stage.cadence?.length ?? 0) }}d</span>
            </div>
          </button>
        </aside>

        <!-- Detalhe etapa -->
        <main v-if="currentStage" class="min-w-0">
          <header class="mb-4">
            <h2 class="text-lg font-medium text-white">{{ currentStage.name || `Etapa ${activeStage + 1}` }}</h2>
            <p v-if="currentStage.objective" class="text-sm text-white/60 mt-1">{{ currentStage.objective }}</p>
            <div v-if="currentStage.advance_criteria" class="mt-3 rounded-lg bg-white/[0.03] ring-1 ring-white/10 p-3">
              <p class="text-[10px] uppercase tracking-wide text-white/40 font-medium mb-1">Avança quando</p>
              <p class="text-xs text-white/70">{{ currentStage.advance_criteria }}</p>
            </div>
            <div v-if="currentStage.dev_instructions">
              <button
                class="mt-3 text-xs text-amber-400/70 hover:text-amber-300 flex items-center gap-1.5 transition-colors"
                @click="showDevInstructions = !showDevInstructions"
              >
                <svg class="w-3 h-3 transition-transform" :class="showDevInstructions ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                </svg>
                {{ showDevInstructions ? 'Ocultar' : 'Ver' }} instruções dev da etapa
              </button>
              <div v-if="showDevInstructions" class="mt-2 rounded-lg bg-amber-500/5 ring-1 ring-amber-500/20 p-3">
                <p class="text-xs text-amber-100/80 whitespace-pre-wrap">{{ currentStage.dev_instructions }}</p>
              </div>
            </div>
          </header>

          <div v-if="(currentStage.cadence?.length ?? 0) === 0" class="text-center py-8 text-white/30 text-sm">
            Sem cadência nesta etapa.
          </div>
          <div v-else class="space-y-4">
            <section v-for="day in sortedDays" :key="day.day" class="relative pl-6">
              <span class="absolute left-0 top-0 bottom-0 w-px bg-white/10"></span>
              <span class="absolute left-0 top-2 -translate-x-1/2 w-2 h-2 rounded-full bg-white/40 ring-4 ring-[#0a0a0a]"></span>
              <p class="text-xs uppercase tracking-wide text-white/40 font-medium mb-2">Dia {{ day.day }}</p>
              <div v-if="day.actions.length === 0" class="text-xs text-white/30 italic">Sem ações.</div>
              <div v-else class="space-y-2">
                <ObCrmMatrixCell v-for="(a, ai) in day.actions" :key="ai" :action="a" />
              </div>
            </section>
          </div>
        </main>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CRMScript, CRMFunnel, CadenceDay } from '~/composables/useOnboarding'

const props = defineProps<{ crm: CRMScript | null | undefined }>()

const route = useRoute()
const router = useRouter()

const funnels = computed<CRMFunnel[]>(() => props.crm?.funnels ?? [])
const activeFunnel = ref(0)
const activeStage = ref(0)
const showDevInstructions = ref(false)

const syncFromQuery = () => {
  const fKey = route.query.funil as string | undefined
  const eIdx = parseInt(route.query.etapa as string)
  if (fKey) {
    const i = funnels.value.findIndex(f => f.key === fKey)
    if (i >= 0) activeFunnel.value = i
  }
  if (!isNaN(eIdx)) {
    const stages = funnels.value[activeFunnel.value]?.stages ?? []
    if (eIdx >= 0 && eIdx < stages.length) activeStage.value = eIdx
  }
}

watch(() => props.crm, () => syncFromQuery(), { immediate: true })
watch(() => route.query, () => syncFromQuery())

const syncToQuery = () => {
  const f = funnels.value[activeFunnel.value]
  if (!f) return
  router.replace({ query: { ...route.query, funil: f.key, etapa: String(activeStage.value) } })
}
watch([activeFunnel, activeStage], () => syncToQuery())

const currentFunnel = computed<CRMFunnel | null>(() => funnels.value[activeFunnel.value] ?? null)
const currentStage = computed(() => currentFunnel.value?.stages[activeStage.value] ?? null)

const sortedDays = computed<CadenceDay[]>(() => {
  return [...(currentStage.value?.cadence ?? [])].sort((a, b) => a.day - b.day)
})

const setFunnel = (i: number) => {
  activeFunnel.value = i
  activeStage.value = 0
  showDevInstructions.value = false
}

const searchOpen = ref(false)
const onPick = (p: { funnelIdx: number; stageIdx: number }) => {
  activeFunnel.value = p.funnelIdx
  activeStage.value = p.stageIdx
  showDevInstructions.value = false
}

const onKeydown = (e: KeyboardEvent) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
    e.preventDefault()
    searchOpen.value = true
  }
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onBeforeUnmount(() => window.removeEventListener('keydown', onKeydown))

watch(activeStage, () => { showDevInstructions.value = false })
</script>
