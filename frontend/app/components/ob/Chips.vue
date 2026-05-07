<template>
  <div class="flex flex-wrap gap-2 mt-1">
    <button
      v-for="opt in options"
      :key="opt"
      class="px-3.5 py-1.5 rounded-full text-xs font-semibold tracking-wide border transition-all"
      :class="value.includes(opt)
        ? 'bg-white/10 text-white border-white/20'
        : 'bg-transparent text-white/40 border-white/10 hover:border-white/20 hover:text-white/60'"
      @click="emit('toggle', opt)"
    >
      {{ opt }}
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{ options: string[]; value: string[]; single?: boolean }>()
const emit = defineEmits<{ toggle: [v: string] }>()
</script>
