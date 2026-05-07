<template>
  <div id="print-content" class="print-page">
    <div v-if="loading" class="loading">Carregando...</div>
    <div v-else-if="!data" class="loading">Materiais não encontrados.</div>
    <template v-else>

      <!-- Fechamento -->
      <section v-if="!section || section === 'fechamento'" class="section">
        <h1 class="section-title">Material de Fechamento — {{ dealName }}</h1>

        <h2 class="sub-title">Perguntas de Diagnóstico</h2>
        <ol>
          <li v-for="(q, i) in data.closing?.diagnostic_questions" :key="i" class="body">{{ q }}</li>
        </ol>

        <h2 class="sub-title">Apresentação de Preço</h2>
        <p class="body pre">{{ data.closing?.price_presentation }}</p>

        <h2 class="sub-title">Matriz de Objeções</h2>
        <table>
          <thead>
            <tr>
              <th>Objeção</th>
              <th>Medo real</th>
              <th>Contra-argumento</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, ri) in data.closing?.objection_matrix" :key="ri">
              <td>{{ row.objection }}</td>
              <td>{{ row.hidden_concern }}</td>
              <td>{{ row.counter_script }}</td>
            </tr>
          </tbody>
        </table>

        <h2 class="sub-title">Script de Fechamento</h2>
        <p class="body pre">{{ data.closing?.closing_script }}</p>

        <div v-if="data.closing?.special_condition">
          <h2 class="sub-title">Condição Especial</h2>
          <p class="body">{{ data.closing.special_condition }}</p>
        </div>
      </section>

      <!-- Qualificação -->
      <section v-if="!section || section === 'qualificacao'" class="section">
        <h1 class="section-title">Roteiro de Qualificação — {{ dealName }}</h1>

        <h2 class="sub-title">Fluxo WhatsApp</h2>
        <div v-for="(s, si) in data.qualification?.whatsapp_flow" :key="si" class="qual-step">
          <span class="channel-badge">{{ s.type }}<span v-if="s.channel"> · {{ s.channel }}</span></span>
          <p class="body">{{ s.content }}</p>
        </div>

        <h2 class="sub-title">Pitch de Ligação</h2>
        <p class="body pre">{{ data.qualification?.call_pitch }}</p>

        <h2 class="sub-title">Critérios de Avanço</h2>
        <ul>
          <li v-for="(c, ci) in data.qualification?.advance_criteria" :key="ci" class="body">{{ c }}</li>
        </ul>

        <h2 class="sub-title">Critérios de Desqualificação</h2>
        <ul>
          <li v-for="(c, ci) in data.qualification?.disqualification_criteria" :key="ci" class="body">{{ c }}</li>
        </ul>
      </section>

    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

useHead({
  style: [{ key: 'page-size', innerHTML: '@page { size: A4 landscape; margin: 10mm; }' }],
})

const route = useRoute()
const id = route.params.id as string
const section = computed(() => route.query.section as string | undefined)

const { materials, loadMaterials, dealName, load } = useOnboarding(id)

const data = computed(() =>
  materials.value?.status === 'complete' ? materials.value : null
)
const loading = ref(true)

onMounted(async () => {
  const pageStyle = document.createElement('style')
  pageStyle.textContent = '@page { size: A4 landscape; margin: 10mm; }'
  document.head.appendChild(pageStyle)

  await Promise.all([load(), loadMaterials()])
  loading.value = false
  await nextTick()
  if (!data.value) return

  await nextTick()
  const el = document.getElementById('print-content')
  if (el) {
    const usableH = (210 - 20) * 3.7795
    const usableW = (297 - 20) * 3.7795
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
  body { background: white; color: black; }
}

.print-page {
  font-family: 'Inter', sans-serif;
  max-width: 760px;
  margin: 0 auto;
  padding: 32px;
  background: white;
  color: #111;
  font-size: 12px;
  line-height: 1.5;
}

.loading { text-align: center; padding: 80px; color: #666; }
.section { margin-bottom: 40px; }
.section-title { font-size: 17px; font-weight: 700; border-bottom: 2px solid #111; padding-bottom: 8px; margin-bottom: 18px; }
.sub-title { font-size: 13px; font-weight: 700; margin-top: 18px; margin-bottom: 8px; color: #333; }
.label { font-size: 9px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #888; margin-bottom: 2px; margin-top: 8px; }
.body { margin: 0 0 4px 0; white-space: pre-wrap; font-size: 11px; }
.pre { white-space: pre-wrap; }
.instructions { color: #666; font-size: 10px; margin: 2px 0 0; font-style: italic; }
.qual-step { border-left: 2px solid #e5e5e5; padding-left: 10px; margin-bottom: 12px; }
.page-break { page-break-before: always; height: 0; }
table { width: 100%; border-collapse: collapse; margin-top: 8px; }
th { background: #f5f5f5; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; padding: 6px 8px; text-align: left; border: 1px solid #ddd; }
td { padding: 6px 8px; border: 1px solid #ddd; font-size: 11px; vertical-align: top; }
ol, ul { padding-left: 18px; margin: 0 0 8px 0; }
li { margin-bottom: 3px; }

/* Kanban */
.kanban-board {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 10px;
  align-items: start;
}
.kanban-col {
  border: 1px solid #e5e5e5;
  border-radius: 6px;
  overflow: hidden;
  break-inside: avoid;
}
.kanban-header {
  background: #1a1a1a;
  padding: 7px 10px;
  display: flex;
  align-items: center;
  gap: 7px;
}
.kanban-num {
  width: 18px;
  height: 18px;
  background: white;
  color: #111;
  border-radius: 50%;
  font-size: 9px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.kanban-name {
  font-size: 10px;
  font-weight: 700;
  color: white;
  line-height: 1.3;
}
.kanban-body { padding: 8px; }
.dev-label { color: #ccc; }
.dev-body { color: #999; font-size: 10px; }

/* Cadência com dias destacados */
.cadence { margin-top: 8px; border-top: 1px solid #eee; padding-top: 6px; }
.day {
  background: #f7f7f7;
  border-radius: 5px;
  padding: 6px 8px;
  margin-bottom: 6px;
}
.day-label {
  font-size: 9px;
  font-weight: 800;
  color: #333;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: 5px;
}
.action { margin-bottom: 6px; }
.channel-badge {
  display: inline-block;
  font-size: 8px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  padding: 2px 6px;
  border-radius: 3px;
  margin-bottom: 3px;
}
/* cores por canal */
.channel-badge-whatsapp { background: #dcfce7; color: #166534; }
.channel-badge-ligacao  { background: #dbeafe; color: #1e40af; }
.channel-badge-email    { background: #fef9c3; color: #854d0e; }
.channel-badge-auto     { background: #f3e8ff; color: #6b21a8; }
.channel-badge-default  { background: #f0f0f0; color: #555; }
</style>
