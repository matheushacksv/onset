<script setup lang="ts">
import { computed } from 'vue'
import type { QualificationScript, QualPlaybookStep } from '~/composables/useOnboarding'

const props = defineProps<{ qualification: QualificationScript }>()

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

const steps = computed<QualPlaybookStep[]>(() => props.qualification?.steps ?? [])

// Fases distintas (ordem de 1ª aparição) — pintam timeline + divisores.
const phases = computed<string[]>(() => {
  const seen: string[] = []
  for (const s of steps.value) {
    const p = (s.phase || '').trim()
    if (p && !seen.includes(p)) seen.push(p)
  }
  return seen
})

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

function stepNum(s: QualPlaybookStep, i: number): string {
  return s.num || String(i + 1).padStart(2, '0')
}
function shortLabel(s: QualPlaybookStep): string {
  const t = (s.title || '').trim()
  return t.length > 22 ? t.slice(0, 21) + '…' : t
}
function isPhaseStart(i: number): boolean {
  const cur = (steps.value[i]?.phase || '').trim()
  if (!cur) return false
  const prev = (steps.value[i - 1]?.phase || '').trim()
  return cur !== prev
}

const ACT_LABEL: Record<string, string> = { falar: 'FALAR', ouvir: 'OUVIR' }
const NOTE_LABEL: Record<string, string> = {
  instrucao: 'Instrução',
  alerta: 'Alerta',
  anote: 'Anote',
  stop: 'Checkpoint',
  transicao: 'Transição',
}

// Perguntas essenciais p/ o cheat-sheet: as que têm marcador (note) preenchido.
const essentialQuestions = computed(() => {
  const out: { num: string; text: string; note: string }[] = []
  steps.value.forEach((s, i) => {
    for (const b of s.blocks || []) {
      if (b.kind !== 'perguntas') continue
      for (const q of b.questions || []) {
        if ((q.note || '').trim() && (q.text || '').trim()) out.push({ num: stepNum(s, i), text: q.text, note: q.note })
      }
    }
  })
  return out
})

const advance = computed(() => props.qualification?.advance_criteria ?? [])
const disq = computed(() => props.qualification?.disqualification_criteria ?? [])
</script>

<template>
  <div class="pb">
    <!-- Cheat-sheet / timeline -->
    <section v-if="steps.length" class="pb-cs">
      <h2 class="pb-cs-title">
        Mapa da <em>qualificação</em>
        <span v-if="qualification.framework" class="pbq-framework">{{ qualification.framework }}</span>
      </h2>
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

      <div v-if="essentialQuestions.length" class="pbq-essentials">
        <div class="pbq-ess-h"><span class="pb-qg-n">?</span> Perguntas essenciais</div>
        <div v-for="(q, qi) in essentialQuestions" :key="qi" class="pbq-ess-row">
          <span class="pbq-ess-n">{{ q.num }}</span>
          <div>
            <p class="pbq-ess-q">{{ q.text }}</p>
            <p class="pbq-ess-note">{{ q.note }}</p>
          </div>
        </div>
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
            <h3>
              {{ s.title }}
              <span v-if="s.gpctba" class="pbq-gpctba" :style="{ background: s.phase ? phaseColor(s.phase) : 'var(--accent)' }">{{ s.gpctba }}</span>
            </h3>
            <div v-if="s.subtitle" class="pb-sub">{{ s.subtitle }}</div>
          </div>
        </div>

        <div v-if="s.objective" class="pbq-objective" :style="{ borderColor: s.phase ? phaseColor(s.phase) : 'var(--accent)' }">
          <span class="pbq-obj-lbl">Objetivo</span>
          <p>{{ s.objective }}</p>
        </div>

        <!-- blocks -->
        <template v-for="(b, bi) in s.blocks" :key="'b' + bi">
          <!-- perguntas -->
          <div v-if="b.kind === 'perguntas'" class="pbq-qblock">
            <div v-if="b.label" class="pb-b-label">{{ b.label }}</div>
            <div v-for="(q, qi) in b.questions" :key="qi" class="pbq-q">
              <span class="pbq-q-badge">P</span>
              <div class="pbq-q-body">
                <p class="pbq-q-text">{{ q.text }}</p>
                <p v-if="q.branch" class="pbq-q-branch">{{ q.branch }}</p>
                <span v-if="q.note" class="pbq-q-note">{{ q.note }}</span>
              </div>
            </div>
          </div>

          <!-- cards se-X / se-Y -->
          <div v-else-if="b.kind === 'cards'" class="pbq-cards-wrap">
            <div v-if="b.label" class="pb-b-label">{{ b.label }}</div>
            <div class="pbq-cards">
              <div v-for="(c, ci) in b.cards" :key="ci" class="pbq-card">
                <div v-if="c.title" class="pbq-card-t">{{ c.title }}</div>
                <p class="pbq-card-x">{{ c.text }}</p>
              </div>
            </div>
          </div>

          <!-- falar / ouvir -->
          <div v-else class="pb-block">
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
        </template>

        <!-- notes -->
        <template v-for="(n, ni) in s.notes" :key="'n' + ni">
          <div v-if="n.kind === 'transicao'" class="pbq-transicao">
            <span class="pbq-trans-arrow">→</span>
            <span>{{ n.text || n.title }}</span>
          </div>
          <div v-else-if="n.kind === 'stop'" class="pbq-stop">
            <div class="pbq-stop-ico">⬤</div>
            <div>
              <div class="pbq-stop-lbl">{{ n.title || NOTE_LABEL.stop }}</div>
              <div class="pbq-stop-t">{{ n.text }}</div>
            </div>
          </div>
          <div v-else-if="n.kind === 'anote'" class="pbq-anote">
            <div class="pbq-anote-lbl">{{ n.title || NOTE_LABEL.anote }}</div>
            <div class="pbq-anote-t">{{ n.text }}</div>
          </div>
          <div v-else-if="n.kind === 'instrucao'" class="pbq-instr">
            <div class="pbq-instr-lbl">{{ n.title || NOTE_LABEL.instrucao }}</div>
            <div class="pbq-instr-t">{{ n.text }}</div>
          </div>
          <div v-else class="pb-alert">
            <div class="pb-alert-title">{{ n.title || NOTE_LABEL.alerta }}</div>
            <div class="pb-alert-txt">{{ n.text }}</div>
          </div>
        </template>
      </section>
    </template>

    <!-- Critérios -->
    <section v-if="advance.length || disq.length" class="pbq-criteria">
      <div v-if="advance.length" class="pbq-crit-col adv">
        <div class="pbq-crit-h">Critérios de avanço</div>
        <ul>
          <li v-for="(c, ci) in advance" :key="ci">{{ c }}</li>
        </ul>
      </div>
      <div v-if="disq.length" class="pbq-crit-col disq">
        <div class="pbq-crit-h">Critérios de desqualificação</div>
        <ul>
          <li v-for="(c, ci) in disq" :key="ci">{{ c }}</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Cores semânticas fixas; demais herdam tokens do tema na raiz. */
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
.pb-cs { margin-bottom: 28px; }
.pb-cs-title {
  font-family: var(--pb-serif);
  font-size: 26px;
  font-weight: 600;
  margin-bottom: 14px;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 12px;
}
.pb-cs-title em { font-style: italic; color: var(--accent); }
.pbq-framework {
  font-family: 'DM Sans', sans-serif;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--on-accent);
  background: var(--accent);
  padding: 4px 10px;
  border-radius: 999px;
}
.pb-timeline {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(72px, 1fr));
  gap: 1px;
  border-top: 2px solid var(--text);
  border-bottom: 2px solid var(--text);
  overflow: hidden;
}
.pb-tl-step { padding: 10px 6px; text-align: center; }
.pb-tl-n { font-family: var(--pb-serif); font-size: 20px; font-weight: 700; line-height: 1; }
.pb-tl-lbl { font-size: 9px; font-weight: 600; color: var(--dim); line-height: 1.25; margin-top: 4px; }
.pb-legend { display: flex; flex-wrap: wrap; gap: 14px; margin-top: 12px; }
.pb-legend-item { display: inline-flex; align-items: center; gap: 6px; font-size: 11px; font-weight: 600; color: var(--dim); }
.pb-dot { width: 9px; height: 9px; border-radius: 2px; }

/* perguntas essenciais */
.pbq-essentials {
  margin-top: 18px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px 16px;
  background: var(--s2);
}
.pbq-ess-h {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--text);
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}
.pbq-ess-row { display: flex; gap: 10px; padding: 7px 0; border-top: 1px solid var(--border); }
.pbq-ess-n {
  font-family: var(--pb-serif);
  font-size: 15px;
  font-weight: 700;
  color: var(--accent);
  min-width: 22px;
}
.pbq-ess-q { font-size: 14px; font-weight: 600; color: var(--text); font-style: italic; line-height: 1.45; }
.pbq-ess-note { font-size: 11px; color: var(--dim); margin-top: 2px; }

/* ---- Divisor de fase ---- */
.pb-divider { border-radius: 10px; padding: 18px 22px; margin: 26px 0 18px; color: #fff; }
.pb-divider-tag { display: block; font-size: 10px; font-weight: 800; letter-spacing: 0.28em; text-transform: uppercase; opacity: 0.7; margin-bottom: 4px; }
.pb-divider-tit { font-family: var(--pb-serif); font-size: 30px; font-weight: 600; }

/* ---- Step ---- */
.pb-step { margin-bottom: 26px; }
.pb-head { display: flex; align-items: baseline; gap: 14px; border-bottom: 1px solid var(--border); padding-bottom: 10px; margin-bottom: 14px; }
.pb-head-num { font-family: var(--pb-serif); font-size: 40px; font-weight: 700; line-height: 0.85; min-width: 48px; }
.pb-head-titles h3 { font-family: var(--pb-serif); font-size: 24px; font-weight: 600; line-height: 1.05; color: var(--text); display: flex; align-items: center; gap: 10px; }
.pbq-gpctba {
  font-family: 'DM Sans', sans-serif;
  font-size: 12px;
  font-weight: 800;
  color: #fff;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.pb-sub { font-size: 10px; font-weight: 700; letter-spacing: 0.18em; text-transform: uppercase; color: var(--muted); margin-top: 4px; }

/* objetivo */
.pbq-objective {
  background: color-mix(in srgb, var(--accent) 9%, transparent);
  border-left: 3px solid var(--accent);
  border-radius: 0 8px 8px 0;
  padding: 11px 16px;
  margin-bottom: 14px;
}
.pbq-obj-lbl { font-size: 9px; font-weight: 800; letter-spacing: 0.18em; text-transform: uppercase; color: var(--accent); display: block; margin-bottom: 4px; }
.pbq-objective p { font-size: 14px; color: var(--dim); line-height: 1.55; }

/* ---- Block (FALAR/OUVIR) ---- */
.pb-block { display: grid; grid-template-columns: 50px 1fr; gap: 0; margin-bottom: 14px; }
.pb-act { font-size: 9px; font-weight: 800; letter-spacing: 0.14em; writing-mode: vertical-rl; transform: rotate(180deg); text-align: center; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #fff; line-height: 1; }
.pb-act.falar { background: var(--accent); }
.pb-act.ouvir { background: var(--red); }
.pb-body { padding: 4px 0 4px 16px; border-left: 2px solid var(--border); margin-left: 8px; }
.pb-body.falar { border-left-color: var(--accent); }
.pb-body.ouvir { border-left-color: var(--red); }
.pb-b-label { font-size: 9px; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); margin-bottom: 7px; }
.pb-open { font-size: 15px; font-weight: 600; color: var(--text); line-height: 1.55; margin-bottom: 8px; white-space: pre-wrap; }
.pb-points { list-style: none; margin: 6px 0; padding: 0; }
.pb-points li { font-size: 13.5px; color: var(--dim); line-height: 1.6; padding: 3px 0 3px 18px; position: relative; }
.pb-points li::before { content: ''; position: absolute; left: 0; top: 12px; width: 8px; height: 1.5px; background: var(--muted); }
.pb-close-q { font-size: 15px; font-weight: 600; color: var(--accent2); line-height: 1.55; margin-top: 8px; white-space: pre-wrap; }

/* ---- Perguntas ---- */
.pbq-qblock { margin: 8px 0 14px; }
.pbq-q { display: flex; gap: 12px; padding: 9px 0; border-bottom: 1px solid var(--border); }
.pbq-q-badge {
  font-size: 11px;
  font-weight: 800;
  color: #fff;
  background: var(--pb-blue);
  width: 22px;
  height: 22px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.pbq-q-body { flex: 1; }
.pbq-q-text { font-size: 14.5px; font-weight: 600; color: var(--text); line-height: 1.5; }
.pbq-q-branch {
  font-size: 13px;
  color: var(--dim);
  font-style: italic;
  line-height: 1.5;
  margin-top: 5px;
  padding-left: 16px;
  border-left: 2px solid var(--border);
}
.pbq-q-note {
  display: inline-block;
  margin-top: 6px;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: var(--pb-blue);
  background: var(--pb-blue-soft);
  padding: 3px 9px;
  border-radius: 999px;
}

/* ---- Cards se-X / se-Y ---- */
.pbq-cards-wrap { margin: 8px 0 14px; }
.pbq-cards { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.pbq-card { border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px; background: var(--surface); }
.pbq-card-t { font-size: 10px; font-weight: 800; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); margin-bottom: 6px; }
.pbq-card-x { font-size: 13px; color: var(--dim); line-height: 1.55; white-space: pre-wrap; }

/* ---- Notes ---- */
.pb-alert { background: var(--pb-amber-soft); border-left: 4px solid var(--pb-amber); border-radius: 0 6px 6px 0; padding: 11px 16px; margin: 14px 0; }
.pb-alert-title { font-size: 9px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--pb-amber); margin-bottom: 5px; }
.pb-alert-txt { font-size: 13px; color: var(--dim); line-height: 1.6; }
.pbq-instr { background: var(--s2); border-left: 4px solid var(--muted); border-radius: 0 6px 6px 0; padding: 11px 16px; margin: 14px 0; }
.pbq-instr-lbl { font-size: 9px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--muted); margin-bottom: 5px; }
.pbq-instr-t { font-size: 13px; color: var(--dim); line-height: 1.6; }
.pbq-anote { background: var(--pb-blue-soft); border-left: 4px solid var(--pb-blue); border-radius: 0 6px 6px 0; padding: 11px 16px; margin: 14px 0; }
.pbq-anote-lbl { font-size: 9px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--pb-blue); margin-bottom: 5px; }
.pbq-anote-t { font-size: 13px; color: var(--dim); line-height: 1.6; }
.pbq-stop { display: flex; align-items: center; gap: 14px; background: color-mix(in srgb, var(--red) 12%, transparent); border: 2px solid var(--red); border-radius: 6px; padding: 12px 16px; margin: 14px 0; }
.pbq-stop-ico { font-size: 13px; color: var(--red); }
.pbq-stop-lbl { font-size: 11px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; color: var(--red); margin-bottom: 3px; }
.pbq-stop-t { font-size: 13px; color: var(--dim); line-height: 1.5; }
.pbq-transicao {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
  text-align: center;
  font-size: 13.5px;
  font-weight: 700;
  color: var(--accent2);
  border: 1px dashed var(--accent2);
  border-radius: 999px;
  padding: 9px 18px;
  margin: 16px auto;
  max-width: 90%;
}
.pbq-trans-arrow { font-weight: 800; }

/* ---- Critérios ---- */
.pbq-criteria { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 30px; }
.pbq-crit-col { border: 1px solid var(--border); border-left-width: 3px; border-radius: 10px; padding: 14px 16px; background: var(--surface); }
.pbq-crit-col.adv { border-left-color: var(--accent); }
.pbq-crit-col.disq { border-left-color: var(--red); }
.pbq-crit-h { font-size: 10px; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; margin-bottom: 9px; }
.pbq-crit-col.adv .pbq-crit-h { color: var(--accent); }
.pbq-crit-col.disq .pbq-crit-h { color: var(--red); }
.pbq-crit-col ul { list-style: none; margin: 0; padding: 0; }
.pbq-crit-col li { font-size: 13px; color: var(--dim); line-height: 1.5; padding: 4px 0 4px 14px; position: relative; }
.pbq-crit-col li::before { content: '·'; position: absolute; left: 2px; font-weight: 800; }

/* shared */
.pb-qg-n { font-family: var(--pb-serif); font-size: 16px; color: var(--accent); font-weight: 700; }

@media (max-width: 640px) {
  .pb { padding: 8px 14px 40px; }
  .pb-timeline { grid-template-columns: repeat(auto-fit, minmax(56px, 1fr)); }
  .pbq-cards { grid-template-columns: 1fr; }
  .pbq-criteria { grid-template-columns: 1fr; }
}
</style>
