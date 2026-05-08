<template>
  <div id="print-content" class="print-page">
    <div v-if="loading" class="loading">Carregando...</div>
    <div v-else-if="!data" class="loading">Materiais não encontrados.</div>
    <template v-else>
      <template v-for="(funnel, fi) in data.crm?.funnels" :key="fi">
        <h1 class="section-title">Script CRM — {{ dealName }} · {{ funnel.name || funnel.key }}</h1>
        <div class="kanban-board" :class="{ 'page-break': fi > 0 }">
          <div v-for="(stage, si) in funnel.stages" :key="si" class="kanban-col">
            <div class="kanban-header">
              <span class="kanban-num">{{ si + 1 }}</span>
              <span class="kanban-name">{{ stage.name }}</span>
            </div>
            <div class="kanban-body">
              <p class="label">Objetivo</p>
              <p class="body">{{ stage.objective }}</p>
              <p class="label">Critério de avanço</p>
              <p class="body">{{ stage.advance_criteria }}</p>
              <p class="label dev-label">Dev</p>
              <p class="body dev-body">{{ stage.dev_instructions }}</p>
              <div class="cadence">
                <p class="label">Cadência</p>
                <div v-for="day in stage.cadence" :key="day.day" class="day">
                  <p class="day-label">Dia {{ day.day }}</p>
                  <div v-for="action in day.actions" :key="action.channel + action.message" class="action">
                    <span class="channel-badge" :class="`channel-badge-${action.channel?.toLowerCase().replace('ç','c').replace('ã','a') || 'default'}`">{{ action.channel }}</span>
                    <p class="body">{{ action.message }}</p>
                    <p v-if="action.instructions" class="instructions">{{ action.instructions }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

// String estática (não computed) → injetada no SSR HTML pelo Nuxt
useHead({
  style: [{ key: 'page-size', innerHTML: '@page { size: A4 landscape; margin: 10mm; }' }],
})

const route = useRoute()
const id = route.params.id as string

const { materials, loadMaterials, dealName, load } = useOnboarding(id)

const data = computed(() =>
  materials.value?.status === 'complete' ? materials.value : null
)
const loading = ref(true)

onMounted(async () => {
  // Backup: injeção via DOM também (belt-and-suspenders para dev mode)
  const pageStyle = document.createElement('style')
  pageStyle.textContent = '@page { size: A4 landscape; margin: 10mm; }'
  document.head.appendChild(pageStyle)

  await Promise.all([load(), loadMaterials()])
  loading.value = false
  await nextTick()
  if (!data.value) return

  await nextTick()

  // Zoom automático para garantir 1 página
  const el = document.getElementById('print-content')
  if (el) {
    const usableH = (210 - 20) * 3.7795  // A4 paisagem altura útil em px
    const usableW = (297 - 20) * 3.7795  // A4 paisagem largura útil em px
    const scaleH = usableH / el.scrollHeight
    const scaleW = usableW / el.scrollWidth
    const scale = Math.min(scaleH, scaleW, 1)
    if (scale < 1) {
      const zoomStyle = document.createElement('style')
      zoomStyle.textContent = `@media print { #print-content { zoom: ${scale.toFixed(4)}; } }`
      document.head.appendChild(zoomStyle)
    }
  }

  setTimeout(() => window.print(), 200)
})
</script>

<style>
@media print {
  nav, header, .no-print { display: none !important; }
  body { background: white; color: black; margin: 0; }
}

.print-page {
  font-family: 'Inter', sans-serif;
  padding: 0;
  background: white;
  color: #111;
  font-size: 8px;
  line-height: 1.4;
}

.loading { text-align: center; padding: 80px; color: #666; }
.section-title { font-size: 13px; font-weight: 700; border-bottom: 2px solid #111; padding-bottom: 6px; margin-bottom: 10px; }
.label { font-size: 7px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #888; margin-bottom: 1px; margin-top: 5px; }
.body { margin: 0 0 2px 0; white-space: pre-wrap; font-size: 8px; }
.instructions { color: #666; font-size: 7px; margin: 1px 0 0; font-style: italic; }

.kanban-board {
  display: flex;
  flex-wrap: nowrap;
  gap: 6px;
  align-items: flex-start;
  width: 100%;
}
.kanban-col {
  flex: 1;
  min-width: 0;
  border: 1px solid #e5e5e5;
  border-radius: 4px;
  overflow: hidden;
}
.kanban-header {
  background: #1a1a1a;
  padding: 4px 6px;
  display: flex;
  align-items: center;
  gap: 4px;
}
.kanban-num {
  width: 14px;
  height: 14px;
  background: white;
  color: #111;
  border-radius: 50%;
  font-size: 7px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kanban-name { font-size: 8px; font-weight: 700; color: white; line-height: 1.2; }
.kanban-body { padding: 5px; }
.dev-label { color: #bbb; }
.dev-body { color: #999; font-size: 7px; }

.cadence { margin-top: 5px; border-top: 1px solid #eee; padding-top: 4px; }
.day { background: #f7f7f7; border-radius: 3px; padding: 3px 5px; margin-bottom: 4px; }
.day-label { font-size: 7px; font-weight: 800; color: #333; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 3px; }
.action { margin-bottom: 4px; }
.channel-badge {
  display: inline-block;
  font-size: 6px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 1px 4px;
  border-radius: 2px;
  margin-bottom: 2px;
}
.channel-badge-whatsapp { background: #dcfce7; color: #166534; }
.channel-badge-ligacao  { background: #dbeafe; color: #1e40af; }
.channel-badge-email    { background: #fef9c3; color: #854d0e; }
.channel-badge-auto     { background: #f3e8ff; color: #6b21a8; }
.channel-badge-default  { background: #f0f0f0; color: #555; }
.page-break { page-break-before: always; margin-top: 10px; }
</style>
