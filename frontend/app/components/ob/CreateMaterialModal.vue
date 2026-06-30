<script setup lang="ts">
import type { MaterialLibraryItem } from '~/composables/useOnboarding'

const props = defineProps<{
  open: boolean
  loading?: boolean
  loadLibrary: () => Promise<MaterialLibraryItem[]>
}>()

const emit = defineEmits<{
  close: []
  create: [payload: { mode: 'ai' | 'blank' | 'copy'; sourceId?: number; templateMaterialId?: number; templateKnowledgeName?: string }]
}>()

const { names: fetchKnowledgeNames } = useKnowledge()

const mode = ref<'ai' | 'blank' | 'copy'>('ai')
const sourceId = ref<number | null>(null)
const search = ref('')
const library = ref<MaterialLibraryItem[]>([])
const libraryLoading = ref(false)

// Material modelo (template) para o modo 'ai' — opcional
const templateSource = ref<'none' | 'material' | 'knowledge'>('none')
const templateMaterialId = ref<number | null>(null)
const templateKnowledgeName = ref<string | null>(null)
const knowledgeNames = ref<string[]>([])
const knowledgeLoading = ref(false)

const filteredLibrary = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return library.value
  return library.value.filter(item =>
    item.pipedrive_deal_name.toLowerCase().includes(q) ||
    (item.assessor_name?.toLowerCase().includes(q))
  )
})

const filteredKnowledge = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return knowledgeNames.value
  return knowledgeNames.value.filter(n => n.toLowerCase().includes(q))
})

const canSubmit = computed(() => {
  if (props.loading) return false
  if (mode.value === 'copy') return sourceId.value !== null
  return true
})

async function ensureLibrary() {
  if (library.value.length || libraryLoading.value) return
  libraryLoading.value = true
  try {
    library.value = await props.loadLibrary()
  } catch {
    library.value = []
  } finally {
    libraryLoading.value = false
  }
}

async function ensureKnowledge() {
  if (knowledgeNames.value.length || knowledgeLoading.value) return
  knowledgeLoading.value = true
  try {
    knowledgeNames.value = await fetchKnowledgeNames()
  } catch {
    knowledgeNames.value = []
  } finally {
    knowledgeLoading.value = false
  }
}

watch(() => props.open, async (isOpen) => {
  if (isOpen) {
    mode.value = 'ai'
    sourceId.value = null
    search.value = ''
    templateSource.value = 'none'
    templateMaterialId.value = null
    templateKnowledgeName.value = null
  }
})

watch(mode, async (m) => {
  search.value = ''
  if (m === 'copy') await ensureLibrary()
})

watch(templateSource, async (s) => {
  search.value = ''
  templateMaterialId.value = null
  templateKnowledgeName.value = null
  if (s === 'material') await ensureLibrary()
  else if (s === 'knowledge') await ensureKnowledge()
})

function submit() {
  if (!canSubmit.value) return
  if (mode.value === 'copy') {
    emit('create', { mode: 'copy', sourceId: sourceId.value! })
  } else if (mode.value === 'ai') {
    emit('create', {
      mode: 'ai',
      templateMaterialId: templateSource.value === 'material' ? (templateMaterialId.value ?? undefined) : undefined,
      templateKnowledgeName: templateSource.value === 'knowledge' ? (templateKnowledgeName.value ?? undefined) : undefined,
    })
  } else {
    emit('create', { mode: mode.value })
  }
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })
}

const TEMPLATE_SOURCES = [
  { value: 'none' as const, label: 'Nenhum' },
  { value: 'material' as const, label: 'Material concluído' },
  { value: 'knowledge' as const, label: 'Doc do knowledge' },
]

const OPTIONS = [
  { value: 'ai' as const, title: 'Gerar com IA', desc: 'Análise automática dos dados do onboarding (~20–30s)' },
  { value: 'blank' as const, title: 'Começar em branco', desc: 'Você preenche todas as seções do zero' },
  { value: 'copy' as const, title: 'Copiar de outro onboarding', desc: 'Reutiliza um material já concluído como base' },
]
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open"
        class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
        @click.self="emit('close')"
      >
        <div class="bg-neutral-900 ring-1 ring-white/10 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">

          <div class="px-6 py-5 border-b border-white/[0.06] shrink-0">
            <h2 class="text-base font-semibold text-white">Como criar o material?</h2>
            <p class="text-xs text-white/40 mt-0.5">Escolha a forma de iniciar</p>
          </div>

          <div class="p-5 space-y-2.5 flex-1 overflow-y-auto min-h-0">
            <button
              v-for="opt in OPTIONS"
              :key="opt.value"
              type="button"
              class="w-full text-left rounded-xl px-4 py-3.5 ring-1 transition-all flex gap-3 items-start"
              :class="mode === opt.value
                ? 'bg-white/10 ring-white/30'
                : 'bg-white/[0.03] ring-white/[0.08] hover:bg-white/5 hover:ring-white/15'"
              @click="mode = opt.value"
            >
              <span
                class="w-4 h-4 rounded-full ring-1 flex items-center justify-center shrink-0 mt-0.5 transition-colors"
                :class="mode === opt.value ? 'ring-white' : 'ring-white/20'"
              >
                <span
                  v-if="mode === opt.value"
                  class="w-2 h-2 rounded-full bg-white"
                />
              </span>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-white">{{ opt.title }}</p>
                <p class="text-xs text-white/40 mt-0.5">{{ opt.desc }}</p>
              </div>
            </button>

            <div v-if="mode === 'ai'" class="mt-4 space-y-2.5">
              <p class="text-xs font-medium text-white/60">Usar um material como modelo <span class="text-white/30">(opcional)</span></p>
              <p class="text-xs text-white/40">A IA segue a estrutura e o estilo do modelo, mas troca todo o conteúdo pelos dados deste onboarding.</p>

              <div class="flex gap-2">
                <button
                  v-for="opt in TEMPLATE_SOURCES"
                  :key="opt.value"
                  type="button"
                  class="flex-1 rounded-xl px-3 py-2 text-xs font-medium ring-1 transition-all"
                  :class="templateSource === opt.value
                    ? 'bg-white/10 ring-white/30 text-white'
                    : 'bg-white/[0.03] ring-white/[0.08] text-white/50 hover:bg-white/5 hover:ring-white/15'"
                  @click="templateSource = opt.value"
                >
                  {{ opt.label }}
                </button>
              </div>

              <template v-if="templateSource !== 'none'">
                <input
                  v-model="search"
                  type="text"
                  :placeholder="templateSource === 'material' ? 'Buscar por nome do deal ou assessor' : 'Buscar material indexado'"
                  class="w-full bg-white/5 ring-1 ring-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/30 focus:outline-none focus:ring-white/30 transition-shadow"
                />

                <div class="max-h-52 overflow-y-auto rounded-xl ring-1 ring-white/10 divide-y divide-white/[0.05]">
                  <!-- Material concluído -->
                  <template v-if="templateSource === 'material'">
                    <div v-if="libraryLoading" class="px-4 py-6 text-center text-sm text-white/40">Carregando...</div>
                    <div v-else-if="!filteredLibrary.length" class="px-4 py-6 text-center text-sm text-white/40">Nenhum material concluído.</div>
                    <button
                      v-for="item in filteredLibrary"
                      :key="item.id"
                      type="button"
                      class="w-full text-left px-4 py-3 hover:bg-white/5 transition-colors flex items-center gap-3"
                      :class="templateMaterialId === item.id ? 'bg-white/[0.07]' : ''"
                      @click="templateMaterialId = templateMaterialId === item.id ? null : item.id"
                    >
                      <span
                        class="w-4 h-4 rounded-full ring-1 flex items-center justify-center shrink-0 transition-colors"
                        :class="templateMaterialId === item.id ? 'bg-white border-white ring-white' : 'border-white/20 ring-white/10'"
                      >
                        <span v-if="templateMaterialId === item.id" class="w-2 h-2 rounded-full bg-neutral-900" />
                      </span>
                      <div class="flex-1 min-w-0">
                        <p class="text-sm text-white truncate">{{ item.pipedrive_deal_name }}</p>
                        <p class="text-xs text-white/40 truncate">
                          <span v-if="item.assessor_name">{{ item.assessor_name }} · </span>{{ formatDate(item.updated_at) }}
                        </p>
                      </div>
                    </button>
                  </template>

                  <!-- Doc do knowledge -->
                  <template v-else>
                    <div v-if="knowledgeLoading" class="px-4 py-6 text-center text-sm text-white/40">Carregando...</div>
                    <div v-else-if="!filteredKnowledge.length" class="px-4 py-6 text-center text-sm text-white/40">Nenhum material indexado.</div>
                    <button
                      v-for="name in filteredKnowledge"
                      :key="name"
                      type="button"
                      class="w-full text-left px-4 py-3 hover:bg-white/5 transition-colors flex items-center gap-3"
                      :class="templateKnowledgeName === name ? 'bg-white/[0.07]' : ''"
                      @click="templateKnowledgeName = templateKnowledgeName === name ? null : name"
                    >
                      <span
                        class="w-4 h-4 rounded-full ring-1 flex items-center justify-center shrink-0 transition-colors"
                        :class="templateKnowledgeName === name ? 'bg-white border-white ring-white' : 'border-white/20 ring-white/10'"
                      >
                        <span v-if="templateKnowledgeName === name" class="w-2 h-2 rounded-full bg-neutral-900" />
                      </span>
                      <p class="text-sm text-white truncate">{{ name }}</p>
                    </button>
                  </template>
                </div>
              </template>
            </div>

            <div v-if="mode === 'copy'" class="mt-4 space-y-2.5">
              <input
                v-model="search"
                type="text"
                placeholder="Buscar por nome do deal ou assessor"
                class="w-full bg-white/5 ring-1 ring-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/30 focus:outline-none focus:ring-white/30 transition-shadow"
              />

              <div class="max-h-60 overflow-y-auto rounded-xl ring-1 ring-white/10 divide-y divide-white/[0.05]">
                <div v-if="libraryLoading" class="px-4 py-6 text-center text-sm text-white/40">
                  Carregando...
                </div>
                <div v-else-if="!filteredLibrary.length" class="px-4 py-6 text-center text-sm text-white/40">
                  Nenhum onboarding com material concluído.
                </div>
                <button
                  v-for="item in filteredLibrary"
                  :key="item.id"
                  type="button"
                  class="w-full text-left px-4 py-3 hover:bg-white/5 transition-colors flex items-center gap-3"
                  :class="sourceId === item.id ? 'bg-white/[0.07]' : ''"
                  @click="sourceId = item.id"
                >
                  <span
                    class="w-4 h-4 rounded border ring-1 flex items-center justify-center shrink-0 transition-colors"
                    :class="sourceId === item.id ? 'bg-white border-white ring-white' : 'border-white/20 ring-white/10'"
                  >
                    <svg v-if="sourceId === item.id" class="w-3 h-3 text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                      <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
                    </svg>
                  </span>
                  <div class="flex-1 min-w-0">
                    <p class="text-sm text-white truncate">{{ item.pipedrive_deal_name }}</p>
                    <p class="text-xs text-white/40 truncate">
                      <span v-if="item.assessor_name">{{ item.assessor_name }} · </span>
                      {{ formatDate(item.updated_at) }}
                    </p>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <div class="px-5 py-4 border-t border-white/[0.06] flex justify-end gap-3 shrink-0">
            <button
              type="button"
              class="px-4 py-2 text-sm text-white/60 hover:text-white transition-colors"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <button
              type="button"
              :disabled="!canSubmit"
              class="bg-white text-neutral-900 text-sm font-medium px-5 py-2 rounded-full hover:bg-white/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              @click="submit"
            >
              {{ loading ? 'Criando...' : 'Criar material' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
