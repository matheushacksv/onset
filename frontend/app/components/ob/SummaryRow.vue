<template>
  <div class="flex items-start justify-between gap-4 py-2 border-b border-white/[0.04] last:border-0">
    <span class="text-xs text-neutral-500 shrink-0">{{ k }}</span>
    <span class="text-xs text-white/70 text-right">{{ v || '—' }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{ k: string; v: string }>()
</script>
