<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      leave-active-class="transition-opacity duration-100"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-start justify-center pt-24 px-4"
        @click.self="close"
      >
        <div class="w-full max-w-2xl bg-neutral-900 ring-1 ring-white/10 rounded-2xl shadow-2xl overflow-hidden">
          <div class="flex items-center gap-3 px-4 py-3 border-b border-white/10">
            <svg class="w-4 h-4 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
            </svg>
            <input
              ref="inputRef"
              v-model="query"
              type="text"
              placeholder="Buscar etapa, dia, canal ou mensagem..."
              class="flex-1 bg-transparent text-white text-sm placeholder-white/30 outline-none"
              @keydown.down.prevent="move(1)"
              @keydown.up.prevent="move(-1)"
              @keydown.enter.prevent="pickActive"
              @keydown.esc="close"
            >
            <kbd class="text-[10px] text-white/30 px-1.5 py-0.5 bg-white/5 rounded">ESC</kbd>
          </div>
          <div class="max-h-[60vh] overflow-y-auto">
            <div v-if="results.length === 0" class="text-center py-10 text-white/30 text-sm">
              {{ query ? 'Nenhum resultado.' : 'Digite para buscar.' }}
            </div>
            <button
              v-for="(r, i) in results"
              :key="i"
              class="w-full text-left px-4 py-2.5 flex items-start gap-3 transition-colors"
              :class="i === activeIdx ? 'bg-white/10' : 'hover:bg-white/5'"
              @mouseenter="activeIdx = i"
              @click="pick(r)"
            >
              <span
                class="mt-0.5 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wide ring-1 shrink-0"
                :class="channelStyle(r.channel)"
              >
                {{ r.channelLabel }}
              </span>
              <div class="min-w-0 flex-1">
                <p class="text-xs text-white/40 truncate">
                  {{ r.funnelName }} <span class="text-white/20">›</span> {{ r.stageName }}
                  <span v-if="r.day" class="text-white/20">·</span>
                  <span v-if="r.day" class="text-white/40">Dia {{ r.day }}</span>
                </p>
                <p class="text-sm text-white/85 truncate" v-html="highlight(r.preview)"></p>
              </div>
            </button>
          </div>
          <div class="px-4 py-2 border-t border-white/10 flex items-center gap-4 text-[10px] text-white/30">
            <span><kbd class="px-1 py-0.5 bg-white/5 rounded">↑↓</kbd> navegar</span>
            <span><kbd class="px-1 py-0.5 bg-white/5 rounded">↵</kbd> abrir</span>
            <span class="ml-auto">{{ results.length }} resultado(s)</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import type { CRMScript } from '~/composables/useOnboarding'

const props = defineProps<{ open: boolean; crm: CRMScript | null | undefined }>()
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'pick', payload: { funnelIdx: number; stageIdx: number }): void
}>()

const query = ref('')
const activeIdx = ref(0)
const inputRef = ref<HTMLInputElement>()

interface Result {
  funnelIdx: number
  stageIdx: number
  funnelName: string
  stageName: string
  day: number | null
  channel: string
  channelLabel: string
  preview: string
}

const CHANNEL_LABELS: Record<string, string> = {
  whatsapp: 'WhatsApp', 'ligação': 'Ligação', ligacao: 'Ligação', email: 'E-mail', auto: 'Auto',
}
const CHANNEL_STYLES: Record<string, string> = {
  whatsapp: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
  'ligação': 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
  ligacao: 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
  email: 'bg-violet-500/15 text-violet-300 ring-violet-500/30',
  auto: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
}
const channelStyle = (c: string) => CHANNEL_STYLES[c?.toLowerCase()] || 'bg-white/10 text-white/80 ring-white/15'

const allEntries = computed<Result[]>(() => {
  const out: Result[] = []
  const funnels = props.crm?.funnels ?? []
  funnels.forEach((f, fi) => {
    f.stages.forEach((s, si) => {
      out.push({
        funnelIdx: fi, stageIdx: si,
        funnelName: f.name || f.key,
        stageName: s.name || `Etapa ${si + 1}`,
        day: null, channel: 'etapa', channelLabel: 'ETAPA',
        preview: s.objective || s.advance_criteria || s.name || '',
      })
      ;(s.cadence ?? []).forEach(d => {
        d.actions.forEach(a => {
          const ck = (a.channel || '').toLowerCase()
          out.push({
            funnelIdx: fi, stageIdx: si,
            funnelName: f.name || f.key,
            stageName: s.name || `Etapa ${si + 1}`,
            day: d.day,
            channel: a.channel,
            channelLabel: CHANNEL_LABELS[ck] || a.channel || 'Ação',
            preview: a.message || '',
          })
        })
      })
    })
  })
  return out
})

const results = computed<Result[]>(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return allEntries.value.slice(0, 30)
  return allEntries.value
    .filter(r => {
      const hay = `${r.stageName} ${r.funnelName} ${r.channelLabel} ${r.preview} dia ${r.day ?? ''}`.toLowerCase()
      return q.split(/\s+/).every(t => hay.includes(t))
    })
    .slice(0, 50)
})

const escapeHtml = (s: string) => s.replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]!))
const highlight = (text: string) => {
  const q = query.value.trim()
  const safe = escapeHtml(text)
  if (!q) return safe
  const re = new RegExp(`(${q.split(/\s+/).map(t => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})`, 'ig')
  return safe.replace(re, '<mark class="bg-yellow-400/30 text-white rounded px-0.5">$1</mark>')
}

const move = (delta: number) => {
  if (results.value.length === 0) return
  activeIdx.value = (activeIdx.value + delta + results.value.length) % results.value.length
}
const pickActive = () => {
  const r = results.value[activeIdx.value]
  if (r) pick(r)
}
const pick = (r: Result) => {
  emit('pick', { funnelIdx: r.funnelIdx, stageIdx: r.stageIdx })
  close()
}
const close = () => emit('close')

watch(query, () => { activeIdx.value = 0 })
watch(() => props.open, (v) => {
  if (v) {
    query.value = ''
    activeIdx.value = 0
    nextTick(() => inputRef.value?.focus())
  }
})
</script>
