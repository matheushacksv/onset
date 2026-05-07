<template>
  <div class="grid grid-cols-4 gap-2 items-center bg-white/[0.02] rounded-xl p-3">
    <div class="flex items-center gap-2">
      <div class="w-6 h-6 rounded bg-white/10 text-white text-xs font-black flex items-center justify-center shrink-0">{{ num }}</div>
      <span class="text-xs text-white/40">{{ label }}</span>
    </div>
    <input v-model="entry.date" type="date" class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-white/20 transition-colors" />
    <input v-model="entry.time" type="time" class="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-xl text-xs text-white focus:outline-none focus:border-white/20 transition-colors" />
    <span class="text-xs text-white/30 text-right">{{ responsibleLabel }}</span>
  </div>
</template>

<script setup lang="ts">
import type { DateEntry } from '~/composables/useOnboarding'
defineProps<{ num: number; entry: DateEntry; label: string; responsibleLabel: string }>()
</script>
