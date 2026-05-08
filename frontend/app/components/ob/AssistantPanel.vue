<script setup lang="ts">
import type { MaterialOut } from '~/composables/useOnboarding'
import type { AssistantSection, AssistantFocus } from '~/composables/useAssistant'

const props = defineProps<{
  open: boolean
  onboardingId: string
  material: MaterialOut | null
  section: AssistantSection
  focus: AssistantFocus
  focusLabel?: string
}>()

const emit = defineEmits<{ close: [] }>()

const materialRef = computed({
  get: () => props.material,
  set: () => {},
})

const { history, sending, send, undoLast, canUndoMessage, reset } = useAssistant(
  props.onboardingId,
  materialRef as any,
)

const input = ref('')
const scrollEl = ref<HTMLElement | null>(null)

function handleEsc(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

watch(() => props.open, (v) => {
  if (v) document.addEventListener('keydown', handleEsc)
  else document.removeEventListener('keydown', handleEsc)
})

onUnmounted(() => document.removeEventListener('keydown', handleEsc))

async function submit() {
  const text = input.value
  if (!text.trim() || sending.value) return
  input.value = ''
  await send(text, props.section, props.focus)
  await nextTick()
  scrollEl.value?.scrollTo({ top: scrollEl.value.scrollHeight, behavior: 'smooth' })
}

function handleEnter(e: KeyboardEvent) {
  if (e.shiftKey) return
  e.preventDefault()
  submit()
}

const SECTION_TITLE: Record<AssistantSection, string> = {
  crm: 'CRM',
  closing: 'Fechamento',
  qualification: 'Qualificação',
}

const suggestions = computed<string[]>(() => {
  if (props.section === 'crm') {
    if (props.focus.stage_idx != null) {
      return [
        'Crie todos os dias da cadência dessa etapa',
        'Sugira mensagens mais empáticas',
        'Reescreve o objetivo dessa etapa',
        'Adiciona um dia 7 com ultimato',
      ]
    }
    return [
      'Crie 3 etapas pra esse funil',
      'Renomeia o funil pra algo mais comercial',
      'Adiciona etapa de Qualificação',
    ]
  }
  if (props.section === 'closing') {
    return [
      'Sugira 3 objeções comuns para esse nicho',
      'Cria 5 perguntas de diagnóstico',
      'Refina o script de fechamento',
      'Adiciona apresentação de preço com ancoragem',
    ]
  }
  return [
    'Cria fluxo de WhatsApp em 5 passos',
    'Sugira 3 critérios de avanço',
    'Sugira 3 critérios de desqualificação',
    'Reescreve o pitch de ligação',
  ]
})

function pickSuggestion(s: string) {
  input.value = s
  submit()
}

watch(() => props.section, () => reset())
</script>

<template>
  <Transition
    enter-active-class="transition-transform duration-200 ease-out"
    enter-from-class="translate-x-full"
    leave-active-class="transition-transform duration-150 ease-in"
    leave-to-class="translate-x-full"
  >
    <aside
      v-if="open"
      class="fixed top-0 right-0 h-screen w-full sm:w-[26rem] z-30 bg-[#0a0a0a] border-l border-white/[0.06] flex flex-col"
    >
      <div class="px-5 py-4 border-b border-white/[0.06] flex items-center justify-between gap-3 shrink-0">
        <div class="min-w-0">
          <p class="text-xs text-white/40 uppercase tracking-widest flex items-center gap-1.5">
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-emerald-400/80" />
            Assistente IA
          </p>
          <p class="text-sm font-medium text-white truncate">
            {{ SECTION_TITLE[section] }}<span v-if="focusLabel" class="text-white/40"> · {{ focusLabel }}</span>
          </p>
        </div>
        <button
          class="text-white/40 hover:text-white transition-colors shrink-0"
          title="Fechar"
          @click="emit('close')"
        >
          <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div ref="scrollEl" class="flex-1 overflow-y-auto p-4 space-y-3">
        <div v-if="!history.length" class="space-y-3">
          <p class="text-sm text-white/60">
            Conta o que precisa. A IA conhece o onboarding e os padrões da casa, e aplica direto no editor 🪄
          </p>
          <div class="space-y-2">
            <p class="text-[10px] text-white/30 uppercase tracking-widest">Sugestões</p>
            <button
              v-for="s in suggestions"
              :key="s"
              type="button"
              class="w-full text-left text-sm text-white/80 bg-white/[0.04] hover:bg-white/[0.07] ring-1 ring-white/[0.08] rounded-xl px-3 py-2 transition-colors"
              :disabled="sending"
              @click="pickSuggestion(s)"
            >
              {{ s }}
            </button>
          </div>
        </div>

        <template v-for="(m, idx) in history" :key="idx">
          <div v-if="m.role === 'user'" class="flex justify-end">
            <div class="max-w-[85%] bg-white text-neutral-900 rounded-2xl rounded-br-sm px-3.5 py-2 text-sm whitespace-pre-wrap break-words">
              {{ m.content }}
            </div>
          </div>
          <div v-else class="flex justify-start">
            <div class="max-w-[90%] bg-white/[0.05] ring-1 ring-white/[0.08] text-white/90 rounded-2xl rounded-bl-sm px-3.5 py-2 text-sm whitespace-pre-wrap break-words">
              <p>{{ m.content }}</p>
              <div v-if="m.changes && m.changes.length" class="mt-2 flex flex-wrap gap-1.5">
                <span
                  v-for="(c, ci) in m.changes"
                  :key="ci"
                  class="text-[10px] text-emerald-300/90 bg-emerald-400/10 ring-1 ring-emerald-400/20 px-2 py-0.5 rounded-full"
                >
                  {{ c }}
                </span>
              </div>
              <button
                v-if="canUndoMessage(idx)"
                type="button"
                class="mt-2 text-[11px] text-white/50 hover:text-white transition-colors flex items-center gap-1"
                @click="undoLast"
              >
                <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 15 3 9m0 0 6-6M3 9h12a6 6 0 0 1 0 12h-3" />
                </svg>
                Desfazer
              </button>
            </div>
          </div>
        </template>

        <div v-if="sending" class="flex justify-start">
          <div class="bg-white/[0.05] ring-1 ring-white/[0.08] text-white/60 rounded-2xl rounded-bl-sm px-3.5 py-2 text-sm flex items-center gap-2">
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-white/60 animate-pulse" />
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-white/40 animate-pulse [animation-delay:120ms]" />
            <span class="inline-block w-1.5 h-1.5 rounded-full bg-white/30 animate-pulse [animation-delay:240ms]" />
          </div>
        </div>
      </div>

      <div class="border-t border-white/[0.06] p-3 shrink-0">
        <div class="bg-white/[0.04] ring-1 ring-white/[0.08] rounded-2xl p-2 flex items-end gap-2">
          <textarea
            v-model="input"
            rows="1"
            placeholder="Pergunte ou peça uma alteração…"
            class="flex-1 bg-transparent text-sm text-white placeholder:text-white/30 focus:outline-none resize-none px-2 py-1.5 max-h-32"
            :disabled="sending"
            @keydown.enter="handleEnter"
          />
          <button
            type="button"
            class="bg-white text-neutral-900 text-sm font-medium px-3 py-1.5 rounded-xl disabled:opacity-30 disabled:cursor-not-allowed hover:bg-white/90 transition-colors shrink-0"
            :disabled="sending || !input.trim()"
            @click="submit"
          >
            <svg v-if="!sending" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
            </svg>
            <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="9" stroke-opacity="0.25" />
              <path stroke-linecap="round" d="M21 12a9 9 0 0 1-9 9" />
            </svg>
          </button>
        </div>
        <p class="text-[10px] text-white/30 mt-2 px-1">Enter envia · Shift+Enter quebra linha</p>
      </div>
    </aside>
  </Transition>
</template>
