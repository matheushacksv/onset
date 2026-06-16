<script setup lang="ts">
import { computed } from 'vue'
import type { ClosingMaterial, MeetingStep } from '~/composables/useOnboarding'

const props = defineProps<{ closing: ClosingMaterial }>()

// Fontes do playbook (display serif + corpo). Só carrega quando o componente renderiza.
useHead({
  link: [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    {
      rel: 'stylesheet',
      href: 'https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500;1,600&family=DM+Sans:wght@300;400;500;600;700;800&display=swap',
    },
  ],
})

const steps = computed<MeetingStep[]>(() => props.closing?.meeting_structure ?? [])

// Fases distintas (ordem de 1ª aparição) — pintam timeline + divisores.
const phases = computed<string[]>(() => {
  const seen: string[] = []
  for (const s of steps.value) {
    const p = (s.phase || '').trim()
    if (p && !seen.includes(p)) seen.push(p)
  }
  return seen
})

// Paleta cíclica p/ fases (mistura cores do tema + semânticas fixas).
const PHASE_COLORS = [
  'var(--accent)',
  'var(--accent2)',
  'var(--pb-blue)',
  'var(--pb-purple)',
  'var(--pb-amber)',
]
function phaseColor(phase: string): string {
  const i = phases.value.indexOf((phase || '').trim())
  return i < 0 ? 'var(--muted)' : PHASE_COLORS[i % PHASE_COLORS.length]
}

// num exibido (fallback p/ índice).
function stepNum(s: MeetingStep, i: number): string {
  return s.num || String(i + 1).padStart(2, '0')
}

// label curto p/ timeline.
function shortLabel(s: MeetingStep): string {
  const t = (s.title || '').trim()
  return t.length > 22 ? t.slice(0, 21) + '…' : t
}

// Marca o 1º step de cada fase p/ render do divisor.
function isPhaseStart(i: number): boolean {
  const cur = (steps.value[i]?.phase || '').trim()
  if (!cur) return false
  const prev = (steps.value[i - 1]?.phase || '').trim()
  return cur !== prev
}

const ACT_LABEL: Record<string, string> = { falar: 'FALAR', ouvir: 'OUVIR', fazer: 'FAZER' }

const hasDiagnostic = computed(() => (props.closing?.diagnostic_questions?.length ?? 0) > 0)
const hasObjections = computed(() => (props.closing?.objection_matrix?.length ?? 0) > 0)
</script>

<template>
  <div class="pb">
    <!-- Cheat-sheet / timeline -->
    <section v-if="steps.length" class="pb-cs">
      <h2 class="pb-cs-title">Mapa da <em>reunião</em></h2>
      <div class="pb-timeline">
        <div
          v-for="(s, i) in steps"
          :key="'tl' + i"
          class="pb-tl-step"
          :style="{ background: s.phase ? phaseColor(s.phase) + '22' : 'transparent' }"
        >
          <div class="pb-tl-n" :style="{ color: s.phase ? phaseColor(s.phase) : 'var(--text)' }">{{ stepNum(s, i) }}</div>
          <div class="pb-tl-lbl">{{ shortLabel(s) }}</div>
        </div>
      </div>
      <div v-if="phases.length" class="pb-legend">
        <span v-for="p in phases" :key="p" class="pb-legend-item">
          <span class="pb-dot" :style="{ background: phaseColor(p) }" />{{ p }}
        </span>
      </div>
    </section>

    <!-- Steps -->
    <template v-for="(s, i) in steps" :key="'st' + i">
      <div v-if="isPhaseStart(i)" class="pb-divider" :style="{ background: phaseColor(s.phase) }">
        <span class="pb-divider-tag">Fase</span>
        <span class="pb-divider-tit">{{ s.phase }}</span>
      </div>

      <section class="pb-step">
        <div class="pb-head">
          <div class="pb-head-num" :style="{ color: s.phase ? phaseColor(s.phase) : 'var(--accent)' }">{{ stepNum(s, i) }}</div>
          <div class="pb-head-titles">
            <h3>{{ s.title }}</h3>
            <div v-if="s.subtitle" class="pb-sub">{{ s.subtitle }}</div>
          </div>
        </div>

        <!-- blocks -->
        <div v-for="(b, bi) in s.blocks" :key="'b' + bi" class="pb-block">
          <div class="pb-act" :class="b.kind">{{ ACT_LABEL[b.kind] || b.kind }}</div>
          <div class="pb-body" :class="b.kind">
            <div v-if="b.label" class="pb-b-label">{{ b.label }}</div>
            <p v-if="b.open" class="pb-open">{{ b.open }}</p>
            <ul v-if="b.points?.length" class="pb-points">
              <li v-for="(pt, pi) in b.points" :key="pi">{{ pt }}</li>
            </ul>
            <p v-if="b.close" class="pb-close-q">{{ b.close }}</p>
          </div>
        </div>

        <!-- notes -->
        <template v-for="(n, ni) in s.notes" :key="'n' + ni">
          <div v-if="n.kind === 'pausa'" class="pb-pause">
            <div class="pb-pause-ico">⏸</div>
            <div>
              <div class="pb-pause-title">{{ n.title || 'Pausa' }}</div>
              <div class="pb-pause-sub">{{ n.text }}</div>
            </div>
          </div>
          <div v-else-if="n.kind === 'pergunta_chave'" class="pb-keyq">
            <div class="pb-keyq-title">{{ n.title || 'Pergunta-chave' }}</div>
            <div class="pb-keyq-text">{{ n.text }}</div>
          </div>
          <div v-else-if="n.kind === 'validacao'" class="pb-valida">
            <div class="pb-valida-ico">✓</div>
            <div>
              <div class="pb-valida-lbl">{{ n.title || 'Validação' }}</div>
              <div class="pb-valida-t">{{ n.text }}</div>
            </div>
          </div>
          <div v-else class="pb-alert">
            <div class="pb-alert-title">{{ n.title || 'Atenção' }}</div>
            <div class="pb-alert-txt">{{ n.text }}</div>
          </div>
        </template>
      </section>
    </template>

    <!-- Diagnóstico -->
    <section v-if="hasDiagnostic" class="pb-qgroup">
      <div class="pb-qgroup-h"><span class="pb-qg-n">?</span> Perguntas de diagnóstico</div>
      <ul class="pb-qlist">
        <li v-for="(q, qi) in closing.diagnostic_questions" :key="qi">{{ q }}</li>
      </ul>
    </section>

    <!-- Apresentação de preço -->
    <section v-if="closing.price_presentation" class="pb-priceblock">
      <div class="pb-block-h">Apresentação de preço</div>
      <p class="pb-block-body">{{ closing.price_presentation }}</p>
    </section>

    <!-- Condição especial -->
    <section v-if="closing.special_condition" class="pb-special">
      <div class="pb-special-lbl">Condição especial</div>
      <p>{{ closing.special_condition }}</p>
    </section>

    <!-- Matriz de objeções -->
    <section v-if="hasObjections" class="pb-objwrap">
      <h2 class="pb-cs-title">Matriz de <em>objeções</em></h2>
      <table class="pb-obj-table">
        <thead>
          <tr>
            <th style="width: 30px"></th>
            <th>Objeção</th>
            <th>O que esconde</th>
            <th>Contra-script</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, ri) in closing.objection_matrix" :key="ri">
            <td class="pb-obj-num">{{ String(ri + 1).padStart(2, '0') }}</td>
            <td class="pb-obj-name">{{ row.objection }}</td>
            <td class="pb-obj-what">{{ row.hidden_concern }}</td>
            <td class="pb-obj-script">{{ row.counter_script }}</td>
          </tr>
        </tbody>
      </table>
    </section>
  </div>
</template>

<style scoped>
/* Cores semânticas fixas (fazer/alerta/pergunta-chave) — legibilidade independe do tema.
   Demais cores herdam os tokens do tema na raiz (--accent, --accent2, --red, etc). */
.pb {
  --pb-blue: #0e528c;
  --pb-blue-soft: var(--blue-bg);
  --pb-amber: #7e4e08;
  --pb-amber-soft: #fcefd0;
  --pb-purple: #4020a0;
  --pb-purple-soft: #ece5fa;
  --pb-serif: 'Cormorant Garamond', Georgia, serif;
  font-family: 'DM Sans', Inter, ui-sans-serif, system-ui, sans-serif;
  max-width: 760px;
  margin: 0 auto;
  padding: 8px 24px 48px;
  color: var(--text);
}

/* ---- Cheat-sheet / timeline ---- */
.pb-cs {
  margin-bottom: 28px;
}
.pb-cs-title {
  font-family: var(--pb-serif);
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 14px;
  color: var(--text);
}
.pb-cs-title em {
  font-style: italic;
  color: var(--accent);
}
.pb-timeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(72px, 1fr));
  gap: 1px;
  border-top: 2px solid var(--text);
  border-bottom: 2px solid var(--text);
  overflow: hidden;
}
.pb-tl-step {
  padding: 10px 6px;
  text-align: center;
}
.pb-tl-n {
  font-family: var(--pb-serif);
  font-size: 20px;
  font-weight: 700;
  line-height: 1;
}
.pb-tl-lbl {
  font-size: 9px;
  font-weight: 600;
  color: var(--dim);
  line-height: 1.25;
  margin-top: 4px;
}
.pb-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 12px;
}
.pb-legend-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  font-weight: 600;
  color: var(--dim);
}
.pb-dot {
  width: 9px;
  height: 9px;
  border-radius: 2px;
}

/* ---- Divisor de fase ---- */
.pb-divider {
  border-radius: 10px;
  padding: 18px 22px;
  margin: 26px 0 18px;
  color: #fff;
}
.pb-divider-tag {
  display: block;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  opacity: 0.7;
  margin-bottom: 4px;
}
.pb-divider-tit {
  font-family: var(--pb-serif);
  font-size: 30px;
  font-weight: 600;
}

/* ---- Step ---- */
.pb-step {
  margin-bottom: 26px;
}
.pb-head {
  display: flex;
  align-items: baseline;
  gap: 14px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 10px;
  margin-bottom: 14px;
}
.pb-head-num {
  font-family: var(--pb-serif);
  font-size: 40px;
  font-weight: 700;
  line-height: 0.85;
  min-width: 48px;
}
.pb-head-titles h3 {
  font-family: var(--pb-serif);
  font-size: 24px;
  font-weight: 600;
  line-height: 1.05;
  color: var(--text);
}
.pb-sub {
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
  margin-top: 4px;
}

/* ---- Block (FALAR/OUVIR/FAZER) ---- */
.pb-block {
  display: grid;
  grid-template-columns: 50px 1fr;
  gap: 0;
  margin-bottom: 14px;
}
.pb-act {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.14em;
  writing-mode: vertical-rl;
  transform: rotate(180deg);
  text-align: center;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  line-height: 1;
}
.pb-act.falar {
  background: var(--accent);
}
.pb-act.ouvir {
  background: var(--red);
}
.pb-act.fazer {
  background: var(--pb-blue);
}
.pb-body {
  padding: 4px 0 4px 16px;
  border-left: 2px solid var(--border);
  margin-left: 8px;
}
.pb-body.falar {
  border-left-color: var(--accent);
}
.pb-body.ouvir {
  border-left-color: var(--red);
}
.pb-body.fazer {
  border-left-color: var(--pb-blue);
}
.pb-b-label {
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 7px;
}
.pb-open {
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  line-height: 1.55;
  margin-bottom: 8px;
  white-space: pre-wrap;
}
.pb-points {
  list-style: none;
  margin: 6px 0;
  padding: 0;
}
.pb-points li {
  font-size: 13.5px;
  color: var(--dim);
  line-height: 1.6;
  padding: 3px 0 3px 18px;
  position: relative;
}
.pb-points li::before {
  content: '';
  position: absolute;
  left: 0;
  top: 12px;
  width: 8px;
  height: 1.5px;
  background: var(--muted);
}
.pb-close-q {
  font-size: 15px;
  font-weight: 600;
  color: var(--accent2);
  line-height: 1.55;
  margin-top: 8px;
  white-space: pre-wrap;
}

/* ---- Notes ---- */
.pb-pause {
  display: flex;
  align-items: center;
  gap: 14px;
  background: color-mix(in srgb, var(--red) 12%, transparent);
  border: 2px solid var(--red);
  border-radius: 6px;
  padding: 12px 16px;
  margin: 14px 0;
}
.pb-pause-ico {
  font-size: 22px;
  color: var(--red);
}
.pb-pause-title {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--red);
  margin-bottom: 3px;
}
.pb-pause-sub {
  font-size: 13px;
  color: var(--dim);
  line-height: 1.5;
}
.pb-alert {
  background: var(--pb-amber-soft);
  border-left: 4px solid var(--pb-amber);
  border-radius: 0 6px 6px 0;
  padding: 11px 16px;
  margin: 14px 0;
}
.pb-alert-title {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--pb-amber);
  margin-bottom: 5px;
}
.pb-alert-txt {
  font-size: 13px;
  color: var(--dim);
  line-height: 1.6;
}
.pb-keyq {
  background: var(--pb-purple-soft);
  border: 2px solid var(--pb-purple);
  border-radius: 6px;
  padding: 14px 18px;
  margin: 16px 0;
}
.pb-keyq-title {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--pb-purple);
  margin-bottom: 7px;
}
.pb-keyq-text {
  font-size: 15px;
  font-weight: 600;
  color: var(--pb-purple);
  line-height: 1.6;
}
.pb-valida {
  display: flex;
  align-items: center;
  gap: 12px;
  background: color-mix(in srgb, var(--accent2) 12%, transparent);
  border-left: 3px solid var(--accent2);
  border-radius: 0 6px 6px 0;
  padding: 10px 16px;
  margin: 12px 0;
}
.pb-valida-ico {
  font-size: 16px;
  color: var(--accent2);
}
.pb-valida-lbl {
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--accent2);
  margin-bottom: 2px;
}
.pb-valida-t {
  font-size: 13px;
  color: var(--text);
  line-height: 1.5;
}

/* ---- Diagnóstico ---- */
.pb-qgroup {
  margin: 30px 0 22px;
}
.pb-qgroup-h {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--text);
  padding: 6px 0;
  border-top: 1.5px solid var(--text);
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.pb-qg-n {
  font-family: var(--pb-serif);
  font-size: 16px;
  color: var(--accent);
  font-weight: 700;
}
.pb-qlist {
  list-style: none;
  margin: 0;
  padding: 0;
}
.pb-qlist li {
  font-size: 14px;
  color: var(--dim);
  line-height: 1.55;
  padding: 6px 0 6px 20px;
  position: relative;
  border-bottom: 1px solid var(--border);
}
.pb-qlist li::before {
  content: '→';
  position: absolute;
  left: 0;
  color: var(--accent);
  font-weight: 700;
}

/* ---- Preço / condição especial ---- */
.pb-priceblock {
  background: var(--s2);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px 18px;
  margin: 22px 0;
}
.pb-block-h {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 8px;
}
.pb-block-body {
  font-size: 14px;
  color: var(--text);
  line-height: 1.6;
  white-space: pre-wrap;
}
.pb-special {
  background: var(--blue-bg);
  border-left: 3px solid var(--accent2);
  border-radius: 0 10px 10px 0;
  padding: 14px 18px;
  margin: 22px 0;
}
.pb-special-lbl {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--accent2);
  margin-bottom: 6px;
}
.pb-special p {
  font-size: 14px;
  color: var(--dim);
  line-height: 1.6;
  white-space: pre-wrap;
}

/* ---- Matriz de objeções ---- */
.pb-objwrap {
  margin-top: 32px;
}
.pb-obj-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  margin-top: 12px;
}
.pb-obj-table thead th {
  background: var(--text);
  color: var(--surface);
  text-align: left;
  padding: 8px 10px;
  font-size: 9px;
  font-weight: 800;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.pb-obj-table tbody tr {
  border-bottom: 1px solid var(--border);
}
.pb-obj-table tbody tr:nth-child(odd) {
  background: var(--s2);
}
.pb-obj-table td {
  padding: 9px 10px;
  vertical-align: top;
  line-height: 1.55;
}
.pb-obj-num {
  font-family: var(--pb-serif);
  font-weight: 700;
  color: var(--text);
  font-size: 15px;
  text-align: center;
}
.pb-obj-name {
  font-weight: 700;
  color: var(--text);
  width: 26%;
}
.pb-obj-what {
  color: var(--red);
  font-style: italic;
  width: 26%;
}
.pb-obj-script {
  color: var(--dim);
  font-size: 12px;
}

@media (max-width: 640px) {
  .pb {
    padding: 8px 14px 40px;
  }
  .pb-timeline {
    grid-template-columns: repeat(auto-fit, minmax(56px, 1fr));
  }
  .pb-obj-table {
    font-size: 11px;
  }
  .pb-obj-table thead {
    display: none;
  }
  .pb-obj-table tr {
    display: grid;
    grid-template-columns: 36px 1fr;
    padding: 8px 0;
  }
  .pb-obj-num {
    grid-row: span 3;
  }
  .pb-obj-name,
  .pb-obj-what,
  .pb-obj-script {
    width: auto;
    padding: 3px 10px;
  }
}
</style>
