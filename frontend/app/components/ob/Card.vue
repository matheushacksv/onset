<template>
  <div class="bg-white/[0.03] ring-1 ring-white/[0.06] rounded-2xl p-5 mb-4">
    <p class="text-xs text-neutral-500 tracking-widest uppercase font-semibold mb-4 pb-3 border-b border-white/[0.06]">{{ title }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>()
</script>
