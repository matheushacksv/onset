<template>
  <div class="min-h-screen bg-[#0a0a0a]">
    <div class="sticky top-0 z-20 bg-[#0a0a0a]/90 backdrop-blur-xl border-b border-white/[0.06]">
      <div class="max-w-7xl mx-auto px-6 py-3 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3 min-w-0">
          <NuxtLink to="/dev/materiais" class="text-white/30 hover:text-white/60 transition-colors shrink-0">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
            </svg>
          </NuxtLink>
          <div class="min-w-0">
            <p class="text-white text-sm font-medium truncate">{{ detail?.pipedrive_deal_name || 'Material' }}</p>
            <p class="text-xs text-white/30">{{ detail?.assessor_name || '—' }} · Visualização CRM</p>
          </div>
        </div>
      </div>
    </div>

    <div class="max-w-7xl mx-auto px-6 py-6">
      <div v-if="loading" class="text-center py-24 text-white/30 text-sm">Carregando...</div>
      <div v-else-if="!detail" class="text-center py-24 text-white/30 text-sm">Material não encontrado.</div>
      <ObCrmMatrixViewer v-else :crm="detail.crm" />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { DevMaterialDetail } from '~/composables/useDevMaterials'

definePageMeta({ middleware: 'dev', layout: false })

const route = useRoute()
const id = route.params.id as string
const { get } = useDevMaterials()

const detail = ref<DevMaterialDetail | null>(null)
const loading = ref(true)

onMounted(async () => {
  try { detail.value = await get(id) } catch { detail.value = null } finally { loading.value = false }
})
</script>
