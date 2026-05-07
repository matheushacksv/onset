<template>
  <div class="mb-0">
    <label v-if="label" class="block text-xs text-neutral-500 tracking-widest uppercase mb-1.5">
      {{ label }}<span v-if="required" class="text-red-400/60 ml-0.5">*</span>
    </label>
    <p v-if="hint" class="text-xs text-neutral-600 mb-2 leading-relaxed">{{ hint }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{ label?: string; hint?: string; required?: boolean }>()
</script>
