<template>
  <div class="min-h-screen bg-neutral-100 dark:bg-[#0a0a0a] py-10 px-6">
    <div class="max-w-6xl mx-auto">
      <header class="mb-6">
        <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white">Materiais publicados</h1>
        <p class="text-sm text-neutral-500 dark:text-white/40 mt-1">Funis prontos para implementação operacional.</p>
      </header>

      <!-- Filtros -->
      <div class="flex flex-wrap gap-2 mb-6">
        <input
          v-model="q"
          type="text"
          placeholder="Buscar por nome..."
          class="flex-1 min-w-[200px] px-3.5 py-2 rounded-xl text-sm bg-white dark:bg-white/5 ring-1 ring-black/5 dark:ring-white/10 text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-white/30 focus:outline-none focus:ring-black/20 dark:focus:ring-white/30"
        />
        <select
          v-model="assessorId"
          class="px-3.5 py-2 rounded-xl text-sm bg-white dark:bg-white/5 ring-1 ring-black/5 dark:ring-white/10 text-neutral-900 dark:text-white focus:outline-none focus:ring-black/20 dark:focus:ring-white/30"
        >
          <option :value="null">Todos os assessores</option>
          <option v-for="a in assessors" :key="a.id" :value="a.id">{{ a.name }}</option>
        </select>
        <select
          v-model="sort"
          class="px-3.5 py-2 rounded-xl text-sm bg-white dark:bg-white/5 ring-1 ring-black/5 dark:ring-white/10 text-neutral-900 dark:text-white focus:outline-none focus:ring-black/20 dark:focus:ring-white/30"
        >
          <option value="recent">Mais recentes</option>
          <option value="old">Mais antigos</option>
          <option value="name">Nome (A-Z)</option>
        </select>
      </div>

      <!-- Estados -->
      <div v-if="loading" class="text-center py-16 text-neutral-400 dark:text-white/30 text-sm">
        Carregando...
      </div>
      <div v-else-if="items.length === 0" class="text-center py-16 text-neutral-400 dark:text-white/30 text-sm">
        {{ q || assessorId ? 'Nenhum material para esse filtro.' : 'Nenhum material publicado ainda.' }}
      </div>
      <template v-else>
        <p class="text-xs text-neutral-400 dark:text-white/30 mb-3">{{ items.length }} de {{ total }} materiais</p>
        <div class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <NuxtLink
            v-for="item in items"
            :key="item.id"
            :to="`/dev/materiais/${item.id}`"
            class="block rounded-2xl bg-white dark:bg-white/5 ring-1 ring-black/5 dark:ring-white/10 p-4 hover:ring-black/20 dark:hover:ring-white/30 transition-all"
          >
            <p class="font-medium text-neutral-900 dark:text-white truncate">{{ item.pipedrive_deal_name || 'Sem nome' }}</p>
            <p class="text-xs text-neutral-500 dark:text-white/40 mt-1 truncate">{{ item.assessor_name || '—' }}</p>
            <p v-if="item.published_at" class="text-[10px] uppercase tracking-wide text-emerald-500 dark:text-emerald-400 mt-3">Publicado {{ formatDate(item.published_at) }}</p>
          </NuxtLink>
        </div>

        <!-- Carregar mais -->
        <div v-if="items.length < total" class="text-center mt-6">
          <button
            class="px-5 py-2 rounded-full text-sm font-medium bg-white dark:bg-white/5 ring-1 ring-black/10 dark:ring-white/15 text-neutral-700 dark:text-white/70 hover:ring-black/25 dark:hover:ring-white/30 transition-all disabled:opacity-40"
            :disabled="loadingMore"
            @click="loadMore"
          >
            {{ loadingMore ? 'Carregando...' : 'Carregar mais' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MaterialLibraryItem } from '~/composables/useOnboarding'
import type { AssessorOption } from '~/composables/useDevMaterials'

definePageMeta({ middleware: 'dev' })

const { list, listAssessors } = useDevMaterials()

const LIMIT = 12

const items = ref<MaterialLibraryItem[]>([])
const total = ref(0)
const assessors = ref<AssessorOption[]>([])
const loading = ref(true)
const loadingMore = ref(false)

const q = ref('')
const assessorId = ref<number | null>(null)
const sort = ref('recent')

const formatDate = (iso: string) => new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

async function fetchPage(reset: boolean) {
  if (reset) loading.value = true
  else loadingMore.value = true
  try {
    const offset = reset ? 0 : items.value.length
    const page = await list({ q: q.value, assessorId: assessorId.value, sort: sort.value, limit: LIMIT, offset })
    items.value = reset ? page.items : [...items.value, ...page.items]
    total.value = page.total
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

function loadMore() {
  fetchPage(false)
}

let _debounce: ReturnType<typeof setTimeout> | null = null
watch(q, () => {
  if (_debounce) clearTimeout(_debounce)
  _debounce = setTimeout(() => fetchPage(true), 300)
})
watch([assessorId, sort], () => fetchPage(true))

onMounted(async () => {
  await fetchPage(true)
  try { assessors.value = await listAssessors() } catch { /* noop */ }
})
</script>
