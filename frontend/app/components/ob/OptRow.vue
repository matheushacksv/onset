<template>
  <button
    class="w-full flex items-start gap-3 p-3 rounded-xl border transition-all text-left"
    :class="selected
      ? 'border-white/15 bg-white/[0.04]'
      : 'border-white/[0.06] bg-white/[0.02] hover:border-white/10'"
    @click="emit('click')"
  >
    <div
      class="shrink-0 mt-0.5 transition-all"
      :class="multi ? 'w-4 h-4 rounded border flex items-center justify-center text-xs font-black' : 'w-3.5 h-3.5 rounded-full border-2 mt-1'"
      :style="selected
        ? multi ? 'background:#fff;border-color:#fff;color:#111' : 'background:#fff;border-color:#fff'
        : 'border-color:rgba(255,255,255,0.2)'"
    >
      <span v-if="multi && selected">✓</span>
    </div>
    <span class="text-sm leading-relaxed" :class="selected ? 'text-white/90' : 'text-white/40'">{{ text }}</span>
  </button>
</template>

<script setup lang="ts">
defineProps<{ text: string; selected: boolean; multi?: boolean }>()
const emit = defineEmits<{ click: [] }>()
</script>
