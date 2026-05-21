<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-lg bg-neutral-900 ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-1">
          <h2 class="text-white font-semibold">Duplicar material existente</h2>
          <button class="text-white/30 hover:text-white/70 text-xl leading-none" @click="$emit('close')">×</button>
        </div>
        <p class="text-xs text-white/40 mb-5">Cria novo material em branco com o conteúdo do escolhido. Form do onboarding fica vazio.</p>

        <div class="relative mb-3">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-white/20 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
            <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
          </svg>
          <input
            v-model="query"
            placeholder="Filtrar materiais..."
            :disabled="loading"
            class="w-full pl-9 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors disabled:opacity-40"
          />
        </div>

        <div v-if="loading" class="space-y-2 mb-3">
          <div v-for="i in 3" :key="i" class="h-14 bg-white/[0.03] rounded-xl animate-pulse" />
        </div>
        <div v-else-if="filtered.length === 0" class="py-6 text-center text-white/30 text-xs mb-3">
          Nenhum material disponível
        </div>
        <div v-else class="space-y-2 max-h-72 overflow-y-auto mb-4">
          <button
            v-for="item in filtered"
            :key="item.id"
            class="w-full text-left p-3 rounded-xl bg-white/[0.03] ring-1 transition-all"
            :class="selected?.id === item.id ? 'ring-white/40 bg-white/[0.06]' : 'ring-white/[0.06] hover:bg-white/[0.06] hover:ring-white/10'"
            @click="selected = item"
          >
            <p class="text-white text-xs font-medium truncate">{{ item.pipedrive_deal_name || 'Sem nome' }}</p>
            <p class="text-[10px] text-white/30 mt-0.5 truncate">{{ item.assessor_name || '—' }}</p>
          </button>
        </div>

        <p v-if="error" class="text-xs text-red-400 mb-3">{{ error }}</p>

        <div class="flex justify-end gap-2">
          <button class="px-4 py-2 text-xs font-medium text-white/60 hover:text-white transition-colors" @click="$emit('close')">
            Cancelar
          </button>
          <button
            class="px-4 py-2 bg-white text-neutral-900 text-xs font-semibold rounded-full hover:bg-white/90 transition-colors disabled:opacity-40"
            :disabled="!selected || submitting"
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
import type { MaterialLibraryItem } from '~/composables/useOnboarding'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ close: []; cloned: [newOnboardingId: number] }>()

const { fetchAuth } = useAuth()
const { cloneMaterial } = useOnboardingCreate()

const query = ref('')
const items = ref<MaterialLibraryItem[]>([])
const loading = ref(false)
const selected = ref<MaterialLibraryItem | null>(null)
const submitting = ref(false)
const error = ref('')

const filtered = computed(() => {
  if (!query.value) return items.value
  const q = query.value.toLowerCase()
  return items.value.filter(it =>
    (it.pipedrive_deal_name || '').toLowerCase().includes(q) ||
    (it.assessor_name || '').toLowerCase().includes(q)
  )
})

const load = async () => {
  loading.value = true
  try {
    const data = await fetchAuth<MaterialLibraryItem[]>('/api/onboarding/materials/library')
    items.value = data
  } catch { items.value = [] }
  finally { loading.value = false }
}

const submit = async () => {
  if (!selected.value || submitting.value) return
  submitting.value = true
  error.value = ''
  try {
    const result = await cloneMaterial(selected.value.id)
    emit('cloned', result.id)
  } catch {
    error.value = 'Falha ao duplicar material.'
  } finally {
    submitting.value = false
  }
}

watch(() => props.open, (v) => {
  if (v) {
    query.value = ''
    selected.value = null
    error.value = ''
    load()
  }
})
</script>
