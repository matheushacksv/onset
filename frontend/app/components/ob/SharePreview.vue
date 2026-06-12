<template>
  <!-- Mini-mock do share público, pintado com as CSS vars + fonte do tema.
       Espelha pages/share/[token].vue pro assessor pré-visualizar sem abrir o link. -->
  <div
    class="w-[300px] rounded-xl overflow-hidden ring-1 ring-black/20 shadow-2xl select-none"
    :style="{ ...theme.vars, fontFamily: theme.font, background: 'var(--bg)' }"
  >
    <!-- Header -->
    <div class="px-3 py-2 border-b" style="border-color: var(--border); background: var(--bg)">
      <div class="flex items-center justify-between gap-2">
        <div class="flex items-center gap-2 min-w-0">
          <img src="/favicon.svg" alt="" class="w-6 h-6 object-contain shrink-0" />
          <div class="min-w-0">
            <p class="text-[11px] font-semibold leading-tight truncate" style="color: var(--text)">Material de vendas</p>
            <p class="text-[8px] leading-tight" style="color: var(--muted)">Grupo Enriquecedor</p>
          </div>
        </div>
        <span class="text-[8px] px-2 py-0.5 rounded-full border shrink-0" style="border-color: var(--border); color: var(--dim)">Baixar PDF</span>
      </div>
      <!-- Tabs -->
      <div class="flex gap-1 mt-1.5">
        <span class="text-[8px] px-2 py-0.5 rounded-full font-medium" style="background: var(--accent-d); color: var(--on-accent)">Funil CRM</span>
        <span class="text-[8px] px-2 py-0.5 rounded-full" style="color: var(--dim)">Fechamento</span>
        <span class="text-[8px] px-2 py-0.5 rounded-full" style="color: var(--dim)">Qualificação</span>
      </div>
    </div>

    <!-- Corpo -->
    <div class="p-3 space-y-2">
      <!-- Mini stage card -->
      <div class="rounded-lg border" style="border-color: var(--border); background: var(--surface)">
        <div class="flex items-center gap-1.5 px-2.5 py-1.5 border-b-2" style="border-color: var(--accent)">
          <span class="w-4 h-4 rounded text-[8px] font-bold flex items-center justify-center" style="background: var(--s2); color: var(--accent2)">1</span>
          <span class="text-[10px] font-semibold" style="color: var(--text)">Prospecção</span>
        </div>
        <div class="p-2.5 space-y-1.5">
          <div class="rounded-md border-l-[3px] px-2 py-1.5" style="background: var(--s2); border-color: var(--accent)">
            <p class="text-[7px] font-bold uppercase tracking-wider" style="color: var(--accent)">Objetivo</p>
            <p class="text-[9px] leading-snug" style="color: var(--dim)">Qualificar o lead e agendar reunião.</p>
          </div>
          <div class="rounded-md border px-2 py-1.5" style="border-color: var(--border); background: var(--s2)">
            <span class="inline-block text-[7px] font-bold uppercase px-1.5 py-0.5 rounded-full border" style="background: #e6f9ee; border-color: #80d4a0; color: #1a7a3a">whatsapp</span>
            <p class="text-[9px] leading-snug mt-1" style="color: var(--text)">Olá! Vi seu interesse e queria entender seu momento.</p>
          </div>
        </div>
      </div>

      <!-- Mini bloco de fechamento -->
      <div>
        <span
          class="text-[7px] font-bold uppercase tracking-wider inline-block pb-0.5 mb-1"
          style="color: var(--accent2); border-bottom: 2px solid var(--accent)"
        >Script de fechamento</span>
        <div
          class="rounded-lg border border-l-[3px] px-2.5 py-1.5 text-[9px] leading-snug"
          style="background: var(--surface); border-color: var(--border); border-left-color: var(--accent); color: var(--text)"
        >Faça o resumo do valor e conduza para a decisão com segurança.</div>
      </div>
    </div>

    <!-- Rodapé com nome do tema -->
    <div class="px-3 py-1.5 text-center text-[8px] border-t" style="border-color: var(--border); color: var(--muted)">
      Tema: {{ theme.name }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ShareTheme } from '~/utils/shareThemes'

defineProps<{ theme: ShareTheme }>()
</script>
