<template>
  <div class="min-h-screen bg-neutral-100 dark:bg-[#0a0a0a] py-10 px-6">
    <div class="max-w-6xl mx-auto">
      <header class="mb-8">
        <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white">Materiais publicados</h1>
        <p class="text-sm text-neutral-500 dark:text-white/40 mt-1">Funis prontos para implementação operacional.</p>
      </header>

      <div v-if="loading" class="text-center py-16 text-neutral-400 dark:text-white/30 text-sm">
        Carregando...
      </div>
      <div v-else-if="items.length === 0" class="text-center py-16 text-neutral-400 dark:text-white/30 text-sm">
        Nenhum material publicado ainda.
      </div>
      <div v-else class="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
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
    </div>
  </div>
</template>

<script setup lang="ts">
import type { MaterialLibraryItem } from '~/composables/useOnboarding'

definePageMeta({ middleware: 'dev' })

const { list } = useDevMaterials()
const items = ref<MaterialLibraryItem[]>([])
const loading = ref(true)

const formatDate = (iso: string) => new Date(iso).toLocaleString('pt-BR', { dateStyle: 'short', timeStyle: 'short' })

onMounted(async () => {
  try { items.value = await list() } finally { loading.value = false }
})
</script>
