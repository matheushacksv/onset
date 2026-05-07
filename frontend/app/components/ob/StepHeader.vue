<template>
  <div class="mb-6">
    <p class="text-xs text-neutral-500 tracking-widest uppercase mb-1">{{ tag }}</p>
    <h2 class="text-xl font-semibold text-white tracking-tight mb-1">{{ title }}</h2>
    <p class="text-sm text-neutral-500">{{ desc }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps<{ tag: string; title: string; desc: string }>()
</script>
