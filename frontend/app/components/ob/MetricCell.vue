<template>
  <div class="bg-white/[0.03] p-4">
    <label class="block text-xs text-neutral-600 tracking-widest uppercase mb-2">{{ label }}</label>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ label: string }>()
</script>
