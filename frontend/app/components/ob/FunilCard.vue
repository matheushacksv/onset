<template>
  <button
    class="p-3 rounded-xl border cursor-pointer transition-all text-left"
    :class="active
      ? 'border-white/20 bg-white/5'
      : 'border-white/[0.06] bg-white/[0.02] hover:border-white/10'"
    @click="emit('click')"
  >
    <p class="text-xs font-bold tracking-wide" :class="active ? 'text-white' : 'text-white/40'">{{ name }}</p>
    <p class="text-xs mt-0.5" :class="active ? 'text-white/50' : 'text-white/20'">{{ desc }}</p>
  </button>
</template>

<script setup lang="ts">
defineProps<{ name: string; desc: string; active: boolean }>()
const emit = defineEmits<{ click: [] }>()
</script>
