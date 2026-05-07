<template>
  <div class="bg-white/[0.02] ring-1 ring-white/[0.06] rounded-2xl p-5 mb-4">
    <div class="flex items-center justify-between mb-4 pb-3 border-b border-white/[0.06]">
      <p class="text-xs text-white/60 tracking-widest uppercase font-semibold">{{ title }}</p>
      <span class="text-xs text-neutral-600 bg-white/[0.03] px-2 py-0.5 rounded border border-white/[0.04]">{{ badge }}</span>
    </div>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; badge: string }>()
</script>
