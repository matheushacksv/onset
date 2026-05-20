<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-lg bg-neutral-900 ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-1">
          <h2 class="text-white font-semibold">Duplicar onboarding</h2>
          <button class="text-white/30 hover:text-white/70 text-xl leading-none" @click="$emit('close')">×</button>
        </div>
        <p class="text-xs text-white/40 mb-5 truncate">
          Origem: <span class="text-white/70">{{ sourceName || '—' }}</span>
        </p>

        <!-- Seletor de deal -->
        <p class="text-[11px] text-white/40 uppercase tracking-widest mb-2">Selecionar deal alvo</p>
        <div class="relative mb-3">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          <input
            v-model="dealQuery"
            placeholder="Filtrar deals..."
            :disabled="loadingDeals"
            class="w-full pl-9 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors disabled:opacity-40"
          />
        </div>

        <div v-if="loadingDeals" class="space-y-2 mb-3">
          <div v-for="i in 3" :key="i" class="h-12 bg-white/[0.03] rounded-xl animate-pulse" />
        </div>
        <div v-else-if="filteredDeals.length === 0" class="py-6 text-center text-white/30 text-xs mb-3">
          Nenhum deal encontrado
        </div>
        <div v-else class="space-y-2 max-h-64 overflow-y-auto mb-4">
          <button
            v-for="deal in filteredDeals"
            :key="deal.id"
            class="w-full text-left p-3 rounded-xl bg-white/[0.03] ring-1 transition-all"
            :class="selectedDeal?.id === deal.id ? 'ring-white/40 bg-white/[0.06]' : 'ring-white/[0.06] hover:bg-white/[0.06] hover:ring-white/10'"
            @click="selectedDeal = deal"
          >
            <p class="text-white text-xs font-medium truncate">{{ cleanDealName(deal.title) }}</p>
          </button>
        </div>

        <!-- Opção material -->
        <label
          v-if="hasMaterial"
          class="flex items-start gap-2.5 p-3 rounded-xl bg-white/[0.03] ring-1 ring-white/[0.06] cursor-pointer mb-5"
        >
          <input
            v-model="includeMaterial"
            type="checkbox"
            class="mt-0.5 accent-white"
          />
          <span class="text-xs text-white/70 leading-relaxed">
            Também copiar o material gerado
            <span class="block text-white/30 mt-0.5">Cria novo material com mesmo conteúdo (não publicado).</span>
          </span>
        </label>

        <p v-if="error" class="text-xs text-red-400 mb-3">{{ error }}</p>

        <div class="flex justify-end gap-2">
          <button
            class="px-4 py-2 text-xs font-medium text-white/60 hover:text-white transition-colors"
            @click="$emit('close')"
          >
            Cancelar
          </button>
          <button
            class="px-4 py-2 bg-white text-neutral-900 text-xs font-semibold rounded-full hover:bg-white/90 transition-colors disabled:opacity-40"
            :disabled="!selectedDeal || submitting"
            @click="submit"
          >
            {{ submitting ? 'Duplicando...' : 'Duplicar' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { cleanDealName } from '~/composables/useOnboarding'

const props = defineProps<{
  open: boolean
  sourceId: number | null
  sourceName: string
  hasMaterial: boolean
}>()
const emit = defineEmits<{ close: []; duplicated: [id: number] }>()

const { fetchAuth } = useAuth()

type Deal = { id: number; title: string; person_name: string; value: number }
const DEALS_CACHE_KEY = 'ob:deals'
const DEALS_CACHE_TTL = 60_000

const dealQuery = ref('')
const allDeals = ref<Deal[]>([])
const loadingDeals = ref(false)
const selectedDeal = ref<Deal | null>(null)
const includeMaterial = ref(false)
const submitting = ref(false)
const error = ref('')

const filteredDeals = computed(() => {
  if (!dealQuery.value) return allDeals.value
  const q = dealQuery.value.toLowerCase()
  return allDeals.value.filter(d =>
    d.title.toLowerCase().includes(q) || (d.person_name || '').toLowerCase().includes(q)
  )
})

const readCache = (): Deal[] | null => {
  try {
    const raw = sessionStorage.getItem(DEALS_CACHE_KEY)
    if (!raw) return null
    const { data, ts } = JSON.parse(raw)
    return Date.now() - ts < DEALS_CACHE_TTL ? data : null
  } catch { return null }
}
const writeCache = (data: Deal[]) => {
  try { sessionStorage.setItem(DEALS_CACHE_KEY, JSON.stringify({ data, ts: Date.now() })) } catch {}
}

const loadDeals = async () => {
  const cached = readCache()
  if (cached) { allDeals.value = cached; return }
  loadingDeals.value = true
  try {
    const data = await fetchAuth<Deal[]>('/api/onboarding/deals/')
    allDeals.value = data
    writeCache(data)
  } catch {
    allDeals.value = []
  } finally {
    loadingDeals.value = false
  }
}

const submit = async () => {
  if (!props.sourceId || !selectedDeal.value || submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const result = await fetchAuth<{ id: number }>(`/api/onboarding/${props.sourceId}/duplicate`, {
      method: 'POST',
      body: {
        pipedrive_deal_id: String(selectedDeal.value.id),
        pipedrive_deal_name: selectedDeal.value.title,
        include_material: includeMaterial.value,
      },
    })
    emit('duplicated', result.id)
  } catch (err: any) {
    if (err?.status === 409) {
      error.value = 'Esse deal já tem onboarding.'
    } else {
      error.value = 'Falha ao duplicar. Tente novamente.'
    }
  } finally {
    submitting.value = false
  }
}

watch(() => props.open, (v) => {
  if (v) {
    dealQuery.value = ''
    selectedDeal.value = null
    includeMaterial.value = false
    error.value = ''
    loadDeals()
  }
})
</script>
