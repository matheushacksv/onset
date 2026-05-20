<template>
  <div class="rounded-xl bg-white/[0.03] ring-1 ring-white/10 hover:ring-white/20 transition-all">
    <div
      role="button"
      tabindex="0"
      class="w-full flex items-center gap-3 px-3 py-2.5 text-left cursor-pointer select-none"
      @click="expanded = !expanded"
      @keydown.enter.prevent="expanded = !expanded"
      @keydown.space.prevent="expanded = !expanded"
    >
      <span
        class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium uppercase tracking-wide shrink-0 ring-1"
        :class="channelStyle"
      >
        <component :is="channelIcon" class="w-3 h-3" />
        {{ channelLabel }}
      </span>
      <p class="flex-1 text-xs text-white/70 truncate">{{ action.message || '—' }}</p>
      <button
        class="shrink-0 p-1 rounded text-white/30 hover:text-white/70 hover:bg-white/5 transition-colors"
        :title="copied ? 'Copiado' : 'Copiar mensagem'"
        @click.stop="copy"
      >
        <svg v-if="!copied" class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h3.75M9 15h3.75M9 18h3.75m3 .75H18a2.25 2.25 0 0 0 2.25-2.25V6.108c0-1.135-.845-2.098-1.976-2.192a48.424 48.424 0 0 0-1.123-.08m-5.801 0c-.065.21-.1.433-.1.664 0 .414.336.75.75.75h4.5a.75.75 0 0 0 .75-.75 2.25 2.25 0 0 0-.1-.664m-5.8 0A2.251 2.251 0 0 1 13.5 2.25H15c1.012 0 1.867.668 2.15 1.586m-5.8 0c-.376.023-.75.05-1.124.08C9.095 4.01 8.25 4.973 8.25 6.108V8.25m0 0H4.875c-.621 0-1.125.504-1.125 1.125v11.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125V9.375c0-.621-.504-1.125-1.125-1.125H8.25Z" />
        </svg>
        <svg v-else class="w-3.5 h-3.5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
        </svg>
      </button>
      <svg class="w-3.5 h-3.5 text-white/40 transition-transform shrink-0" :class="expanded ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
      </svg>
    </div>
    <div v-if="expanded" class="px-3 pb-3 space-y-2 border-t border-white/5">
      <p class="text-xs text-white/85 whitespace-pre-wrap mt-2">{{ action.message || '—' }}</p>
      <div v-if="action.instructions" class="rounded-lg bg-amber-500/5 ring-1 ring-amber-500/20 p-2">
        <p class="text-[10px] uppercase tracking-wide text-amber-400/70 font-medium mb-1">Instruções dev</p>
        <p class="text-xs text-amber-100/80 whitespace-pre-wrap">{{ action.instructions }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { h } from 'vue'
import type { CadenceAction } from '~/composables/useOnboarding'

const props = defineProps<{ action: CadenceAction }>()
const expanded = ref(false)
const copied = ref(false)

const CHANNEL_LABELS: Record<string, string> = {
  whatsapp: 'WhatsApp',
  'ligação': 'Ligação',
  ligacao: 'Ligação',
  email: 'E-mail',
  auto: 'Automação',
}
const CHANNEL_STYLES: Record<string, string> = {
  whatsapp: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/30',
  'ligação': 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
  ligacao: 'bg-sky-500/15 text-sky-300 ring-sky-500/30',
  email: 'bg-violet-500/15 text-violet-300 ring-violet-500/30',
  auto: 'bg-amber-500/15 text-amber-300 ring-amber-500/30',
}
const channelKey = computed(() => (props.action.channel || '').toLowerCase())
const channelLabel = computed(() => CHANNEL_LABELS[channelKey.value] || props.action.channel || 'Ação')
const channelStyle = computed(() => CHANNEL_STYLES[channelKey.value] || 'bg-white/10 text-white/80 ring-white/15')

const IconWhatsapp = h('svg', { viewBox: '0 0 24 24', fill: 'currentColor' }, [
  h('path', { d: 'M.057 24l1.687-6.163a11.867 11.867 0 0 1-1.587-5.946C.16 5.335 5.495 0 12.05 0a11.817 11.817 0 0 1 8.413 3.488 11.824 11.824 0 0 1 3.48 8.414c-.003 6.557-5.338 11.892-11.893 11.892a11.9 11.9 0 0 1-5.688-1.448L.057 24zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884a9.86 9.86 0 0 0 1.683 5.527l-.999 3.648 3.805-.974zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.29.173-1.414z' })
])
const IconPhone = h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2.5' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M2.25 6.75c0 8.284 6.716 15 15 15h2.25a2.25 2.25 0 0 0 2.25-2.25v-1.372c0-.516-.351-.966-.852-1.091l-4.423-1.106c-.44-.11-.902.055-1.173.417l-.97 1.293c-.282.376-.769.542-1.21.38a12.035 12.035 0 0 1-7.143-7.143c-.162-.441.004-.928.38-1.21l1.293-.97c.363-.271.527-.734.417-1.173L6.963 3.102a1.125 1.125 0 0 0-1.091-.852H4.5A2.25 2.25 0 0 0 2.25 4.5v2.25Z' })
])
const IconMail = h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M21.75 6.75v10.5a2.25 2.25 0 0 1-2.25 2.25h-15a2.25 2.25 0 0 1-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0 0 19.5 4.5h-15a2.25 2.25 0 0 0-2.25 2.25m19.5 0v.243a2.25 2.25 0 0 1-1.07 1.916l-7.5 4.615a2.25 2.25 0 0 1-2.36 0L3.32 8.91a2.25 2.25 0 0 1-1.07-1.916V6.75' })
])
const IconBolt = h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2' }, [
  h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M3.75 13.5 13.5 3v7.5h6.75L10.5 21v-7.5H3.75Z' })
])
const ICONS: Record<string, any> = {
  whatsapp: IconWhatsapp,
  'ligação': IconPhone,
  ligacao: IconPhone,
  email: IconMail,
  auto: IconBolt,
}
const channelIcon = computed(() => ICONS[channelKey.value] || IconBolt)

const copy = async () => {
  try {
    await navigator.clipboard.writeText(props.action.message || '')
    copied.value = true
    setTimeout(() => { copied.value = false }, 1500)
  } catch { /* ignore */ }
}
</script>
