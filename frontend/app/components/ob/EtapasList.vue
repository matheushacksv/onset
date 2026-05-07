<template>
  <div>
    <p class="text-xs text-neutral-600 mb-2">Desmarque etapas que não se aplicam. Edite a ação de cada etapa se necessário.</p>
    <div class="space-y-1.5">
      <div
        v-for="(etapa, i) in etapas"
        :key="i"
        class="flex items-center gap-2 p-2.5 rounded-xl border transition-all"
        :class="etapa.active ? 'border-white/10 bg-white/[0.03]' : 'border-white/[0.04] opacity-40'"
      >
        <button
          class="w-4 h-4 rounded flex items-center justify-center shrink-0 transition-all text-xs font-black"
          :class="etapa.active ? 'bg-white text-neutral-900' : 'border border-white/20'"
          @click="etapa.active = !etapa.active"
        >
          <span v-if="etapa.active">✓</span>
        </button>
        <span class="text-xs font-semibold text-white/50 shrink-0 min-w-0">{{ etapa.name }}</span>
        <span class="text-white/20 text-xs shrink-0">—</span>
        <input
          v-model="etapa.action"
          class="flex-1 bg-transparent border-none text-xs text-white/50 focus:outline-none focus:text-white/80 min-w-0"
          :placeholder="etapa.action || 'Descreva a ação...'"
          :disabled="!etapa.active"
        />
        <span v-if="etapa.optional" class="text-xs text-white/20 shrink-0">opcional</span>
      </div>
    </div>
    <button
      class="w-full mt-2 py-2 border border-dashed border-white/10 rounded-xl text-xs text-white/30 font-semibold tracking-widest uppercase hover:border-white/20 hover:text-white/50 transition-all"
      @click="emit('add')"
    >
      + Adicionar etapa
    </button>
  </div>
</template>

<script setup lang="ts">
import type { FunilEtapa } from '~/composables/useOnboarding'
defineProps<{ etapas: FunilEtapa[] }>()
const emit = defineEmits<{ add: [] }>()
</script>
