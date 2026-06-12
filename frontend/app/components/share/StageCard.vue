<template>
  <div class="bg-[var(--surface)] rounded-2xl border border-[var(--border)] flex flex-col">
    <div class="flex items-center gap-2.5 px-4 py-3 border-b-2 border-[var(--accent)] shrink-0">
      <span class="w-6 h-6 rounded-md bg-[var(--s2)] text-[color:var(--accent2)] text-xs font-bold flex items-center justify-center shrink-0">{{ index + 1 }}</span>
      <span class="text-sm font-semibold leading-tight text-[color:var(--text)]">{{ stage.name || 'Etapa ' + (index + 1) }}</span>
    </div>
    <div class="p-4 space-y-3 overflow-y-auto">
      <div class="rounded-xl bg-[var(--s2)] border-l-[3px] border-[var(--accent)] px-3 py-2.5">
        <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--accent)] mb-1">Objetivo</p>
        <p class="text-[13px] leading-relaxed text-[color:var(--dim)] whitespace-pre-wrap">{{ stage.objective || '—' }}</p>
      </div>
      <div class="rounded-xl bg-[var(--blue-bg)] border-l-[3px] border-[var(--accent2)] px-3 py-2.5">
        <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--accent2)] mb-1">Critério de avanço</p>
        <p class="text-[13px] leading-relaxed text-[color:var(--dim)] whitespace-pre-wrap">{{ stage.advance_criteria || '—' }}</p>
      </div>
      <div v-if="stage.loss_reason" class="rounded-xl bg-[var(--s2)] border-l-[3px] border-[var(--red)] px-3 py-2.5">
        <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--red)] mb-1">Motivo de perda</p>
        <p class="text-[13px] leading-relaxed text-[color:var(--dim)] whitespace-pre-wrap">{{ stage.loss_reason }}</p>
      </div>

      <div v-if="cadence.length">
        <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--muted)] mt-1 mb-2">Cadência</p>
        <div v-for="(day, di) in cadence" :key="di" class="mb-2.5">
          <p class="text-[10px] font-bold uppercase tracking-wider text-[color:var(--text)] mb-1">Dia {{ day.day }}</p>
          <div
            v-for="(action, ai) in day.actions"
            :key="ai"
            class="rounded-xl border border-[var(--border)] bg-[var(--s2)] px-3 py-2 mb-1.5"
          >
            <div class="flex items-center justify-between gap-2 mb-1.5">
              <span
                class="inline-block text-[9px] font-bold uppercase tracking-wide px-2 py-0.5 rounded-full border"
                :class="badgeClass(action.channel)"
              >{{ action.channel }}</span>
              <button
                class="text-[10px] font-medium text-[color:var(--accent)] hover:text-[color:var(--accent-d)] transition-colors shrink-0"
                @click="$emit('copy', action.message, `${index}-${di}-${ai}`)"
              >
                {{ copiedKey === `${index}-${di}-${ai}` ? '✓ Copiado' : 'Copiar' }}
              </button>
            </div>
            <p class="text-[12px] leading-relaxed text-[color:var(--text)] whitespace-pre-wrap">{{ action.message }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { PipelineStage, CadenceDay } from '~/composables/useOnboarding'

const props = defineProps<{
  stage: PipelineStage
  index: number
  channelFilter: string
  copiedKey: string
}>()

defineEmits<{ copy: [message: string, key: string] }>()

const cadence = computed<CadenceDay[]>(() => {
  const c = props.stage.cadence || []
  if (!props.channelFilter) return c
  return c
    .map(d => ({ ...d, actions: (d.actions || []).filter(a => a.channel === props.channelFilter) }))
    .filter(d => d.actions.length)
})

// Cores de canal ficam fixas (identidade visual do canal, não muda com o tema).
function badgeClass(channel: string) {
  const c = (channel || '').toLowerCase()
  if (c.includes('whats')) return 'bg-[#e6f9ee] border-[#80d4a0] text-[#1a7a3a]'
  if (c.includes('lig')) return 'bg-[#edf3fc] border-[#90b8f0] text-[#3a6a4a]'
  if (c.includes('mail')) return 'bg-[#fff3e0] border-[#f0c060] text-[#a06010]'
  if (c.includes('auto')) return 'bg-[#f0ecfc] border-[#c0a8f0] text-[#6040b0]'
  return 'bg-[#f9f5ef] border-[#e2d8c5] text-[#5a5048]'
}
</script>
