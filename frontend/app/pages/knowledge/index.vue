<script setup lang="ts">
import type { KnowledgeItem } from '~/composables/useKnowledge'

const { user } = useAuth()
const { list, view, upload, remove, download, index, indexBulk, unindex } = useKnowledge()

if (!user.value?.is_superuser) {
  await navigateTo('/')
}

const items = ref<KnowledgeItem[]>([])
const loading = ref(true)
const error = ref<string | null>(null)

const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)

// Painel de visualização do conteúdo do MD.
const viewing = ref<string | null>(null)
const viewContent = ref('')
const viewLoading = ref(false)

// Confirmação de exclusão.
const confirmName = ref<string | null>(null)
const deleting = ref(false)

async function load() {
  loading.value = true
  error.value = null
  try {
    items.value = await list()
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao carregar materiais'
  } finally {
    loading.value = false
  }
}

function pickFile() {
  error.value = null
  fileInput.value?.click()
}

async function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  uploading.value = true
  error.value = null
  try {
    const created = await upload(file)
    items.value = [...items.value.filter(i => i.name !== created.name), created].sort((a, b) =>
      a.name.localeCompare(b.name),
    )
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao enviar material'
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function openView(name: string) {
  viewing.value = name
  viewLoading.value = true
  viewContent.value = ''
  try {
    const data = await view(name)
    viewContent.value = data.content
  } catch (err: any) {
    viewContent.value = err?.data?.detail || 'Erro ao carregar conteúdo'
  } finally {
    viewLoading.value = false
  }
}

function closeView() {
  viewing.value = null
  viewContent.value = ''
}

async function confirmDelete() {
  if (!confirmName.value) return
  deleting.value = true
  error.value = null
  try {
    await remove(confirmName.value)
    items.value = items.value.filter(i => i.name !== confirmName.value)
    confirmName.value = null
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao excluir material'
  } finally {
    deleting.value = false
  }
}

async function onDownload(name: string) {
  error.value = null
  try {
    await download(name)
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao baixar material'
  }
}

// Seleção em massa.
const selected = ref<string[]>([])
const busy = ref<string[]>([])
const bulkBusy = ref(false)
const bulkMsg = ref<string | null>(null)

function isSelected(n: string) { return selected.value.includes(n) }
function toggleSelect(n: string) {
  const i = selected.value.indexOf(n)
  if (i >= 0) selected.value.splice(i, 1)
  else selected.value.push(n)
}
const allSelected = computed(() => items.value.length > 0 && selected.value.length === items.value.length)
function toggleSelectAll() {
  selected.value = allSelected.value ? [] : items.value.map(i => i.name)
}

function setIndexed(names: string[], value: boolean) {
  items.value.forEach(i => { if (names.includes(i.name)) i.indexed = value })
}

async function indexOne(name: string) {
  error.value = null
  busy.value.push(name)
  try {
    await index(name)
    setIndexed([name], true)
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao indexar'
  } finally {
    busy.value = busy.value.filter(n => n !== name)
  }
}

async function unindexOne(name: string) {
  error.value = null
  busy.value.push(name)
  try {
    await unindex([name])
    setIndexed([name], false)
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao desindexar'
  } finally {
    busy.value = busy.value.filter(n => n !== name)
  }
}

async function bulkIndex() {
  if (!selected.value.length) return
  error.value = null
  bulkMsg.value = null
  bulkBusy.value = true
  try {
    const names = [...selected.value]
    const res = await indexBulk(names)
    bulkMsg.value = `Indexação de ${res.queued} material(is) em andamento (assíncrono). Atualize em instantes.`
    selected.value = []
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao enfileirar indexação'
  } finally {
    bulkBusy.value = false
  }
}

async function bulkUnindex() {
  if (!selected.value.length) return
  error.value = null
  bulkBusy.value = true
  try {
    const names = [...selected.value]
    await unindex(names)
    setIndexed(names, false)
    selected.value = []
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao desindexar'
  } finally {
    bulkBusy.value = false
  }
}

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function fmtDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
}

onMounted(load)
</script>

<template>
  <div class="min-h-full p-6 md:p-10 max-w-4xl mx-auto">
    <div class="flex items-start justify-between gap-4 mb-8">
      <div>
        <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white">Knowledge</h1>
        <p class="text-sm text-neutral-500 dark:text-white/40 mt-1">
          Materiais (.md) que alimentam os agentes de geração. Add/remove vale na hora.
        </p>
      </div>
      <button
        :disabled="uploading"
        class="shrink-0 bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 text-sm font-medium px-5 py-2.5 rounded-full hover:bg-neutral-800 dark:hover:bg-white/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        @click="pickFile"
      >
        {{ uploading ? 'Enviando...' : 'Adicionar .md / .pdf' }}
      </button>
      <input ref="fileInput" type="file" accept=".md,.pdf,text/markdown,application/pdf" class="hidden" @change="onFileChange" />
    </div>

    <div v-if="error" class="bg-red-500/10 ring-1 ring-red-400/30 rounded-xl px-4 py-3 text-sm text-red-300 mb-5">
      {{ error }}
    </div>

    <div v-if="bulkMsg" class="bg-blue-500/10 ring-1 ring-blue-400/30 rounded-xl px-4 py-3 text-sm text-blue-300 mb-5 flex items-center justify-between gap-3">
      <span>{{ bulkMsg }}</span>
      <button class="text-xs underline hover:no-underline shrink-0" @click="load">Atualizar lista</button>
    </div>

    <!-- Toolbar de seleção em massa -->
    <div v-if="!loading && items.length" class="flex items-center gap-3 mb-3 px-1">
      <label class="flex items-center gap-2 text-xs text-neutral-500 dark:text-white/50 cursor-pointer">
        <input
          type="checkbox"
          :checked="allSelected"
          class="w-4 h-4 rounded border-neutral-300 dark:border-white/20"
          @change="toggleSelectAll"
        />
        Selecionar todos ({{ items.length }})
      </label>
      <template v-if="selected.length">
        <span class="text-xs text-neutral-500 dark:text-white/50">· {{ selected.length }} selecionado(s)</span>
        <div class="flex-1"></div>
        <button
          :disabled="bulkBusy"
          class="text-xs font-medium text-emerald-600 dark:text-emerald-400 px-3 py-1.5 rounded-full ring-1 ring-emerald-400/30 hover:bg-emerald-500/10 disabled:opacity-40 transition-colors"
          @click="bulkIndex"
        >Indexar</button>
        <button
          :disabled="bulkBusy"
          class="text-xs font-medium text-amber-600 dark:text-amber-400 px-3 py-1.5 rounded-full ring-1 ring-amber-400/30 hover:bg-amber-500/10 disabled:opacity-40 transition-colors"
          @click="bulkUnindex"
        >Desindexar</button>
        <button
          class="text-xs text-neutral-400 dark:text-white/40 hover:text-neutral-700 dark:hover:text-white/70 transition-colors"
          @click="selected = []"
        >Limpar</button>
      </template>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-sm text-neutral-500 dark:text-white/40 py-10 text-center">
      Carregando...
    </div>

    <!-- Empty -->
    <div
      v-else-if="!items.length"
      class="bg-white dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-2xl px-6 py-12 text-center"
    >
      <p class="text-sm text-neutral-500 dark:text-white/40">Nenhum material ainda. Adicione um arquivo .md ou .pdf.</p>
    </div>

    <!-- List -->
    <div v-else class="bg-white dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-2xl divide-y divide-neutral-100 dark:divide-white/[0.06]">
      <div
        v-for="item in items"
        :key="item.name"
        class="flex items-center gap-3 px-4 py-3"
        :class="isSelected(item.name) ? 'bg-black/[0.02] dark:bg-white/[0.03]' : ''"
      >
        <input
          type="checkbox"
          :checked="isSelected(item.name)"
          class="w-4 h-4 rounded border-neutral-300 dark:border-white/20 shrink-0"
          @change="toggleSelect(item.name)"
        />
        <svg class="w-5 h-5 text-neutral-400 dark:text-white/30 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
          <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
        </svg>
        <div class="min-w-0 flex-1">
          <p class="text-sm font-medium text-neutral-900 dark:text-white truncate">{{ item.name }}</p>
          <p class="text-xs text-neutral-400 dark:text-white/30">{{ fmtSize(item.size) }} · {{ fmtDate(item.updated_at) }}</p>
        </div>
        <span
          v-if="item.indexed"
          class="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-500 ring-1 ring-emerald-400/30"
        >indexado</span>
        <span
          v-else
          class="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-500 ring-1 ring-amber-400/30"
        >não indexado</span>
        <button
          v-if="item.indexed"
          :disabled="busy.includes(item.name)"
          class="text-xs text-amber-600 dark:text-amber-400/80 hover:text-amber-500 px-2.5 py-1.5 rounded-lg hover:bg-amber-500/10 transition-colors disabled:opacity-40"
          @click="unindexOne(item.name)"
        >{{ busy.includes(item.name) ? '...' : 'Desindexar' }}</button>
        <button
          v-else
          :disabled="busy.includes(item.name)"
          class="text-xs text-emerald-600 dark:text-emerald-400/80 hover:text-emerald-500 px-2.5 py-1.5 rounded-lg hover:bg-emerald-500/10 transition-colors disabled:opacity-40"
          @click="indexOne(item.name)"
        >{{ busy.includes(item.name) ? '...' : 'Indexar' }}</button>
        <button
          class="text-xs text-neutral-600 dark:text-white/60 hover:text-neutral-900 dark:hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          @click="openView(item.name)"
        >Ver</button>
        <button
          class="text-xs text-neutral-600 dark:text-white/60 hover:text-neutral-900 dark:hover:text-white px-2.5 py-1.5 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition-colors"
          @click="onDownload(item.name)"
        >Baixar</button>
        <button
          class="text-xs text-red-500/70 hover:text-red-500 px-2.5 py-1.5 rounded-lg hover:bg-red-500/10 transition-colors"
          @click="confirmName = item.name"
        >Excluir</button>
      </div>
    </div>

    <!-- View modal -->
    <Teleport to="body">
      <div
        v-if="viewing"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="closeView"
      >
        <div class="bg-white dark:bg-neutral-900 ring-1 ring-neutral-200 dark:ring-white/10 rounded-2xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl">
          <div class="flex items-center justify-between gap-3 px-5 py-3.5 border-b border-neutral-100 dark:border-white/[0.06]">
            <p class="text-sm font-medium text-neutral-900 dark:text-white truncate">{{ viewing }}</p>
            <button
              class="text-neutral-400 dark:text-white/40 hover:text-neutral-900 dark:hover:text-white transition-colors"
              @click="closeView"
            >
              <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          <div class="overflow-auto p-5">
            <p v-if="viewLoading" class="text-sm text-neutral-500 dark:text-white/40">Carregando...</p>
            <pre v-else class="text-xs text-neutral-700 dark:text-white/70 whitespace-pre-wrap font-mono leading-relaxed">{{ viewContent }}</pre>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Delete confirm modal -->
    <Teleport to="body">
      <div
        v-if="confirmName"
        class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
        @click.self="confirmName = null"
      >
        <div class="bg-white dark:bg-neutral-900 ring-1 ring-neutral-200 dark:ring-white/10 rounded-2xl w-full max-w-sm p-6 shadow-2xl">
          <h2 class="text-lg font-semibold text-neutral-900 dark:text-white">Excluir material?</h2>
          <p class="text-sm text-neutral-500 dark:text-white/40 mt-1.5">
            <span class="font-medium text-neutral-700 dark:text-white/70">{{ confirmName }}</span> sai do índice e do storage. Não dá pra desfazer.
          </p>
          <div class="flex justify-end gap-3 mt-6">
            <button
              :disabled="deleting"
              class="bg-neutral-100 dark:bg-white/10 text-neutral-700 dark:text-white text-sm font-medium px-4 py-2 rounded-full hover:bg-neutral-200 dark:hover:bg-white/15 transition-colors ring-1 ring-neutral-200 dark:ring-white/10 disabled:opacity-40"
              @click="confirmName = null"
            >Cancelar</button>
            <button
              :disabled="deleting"
              class="bg-red-500 text-white text-sm font-medium px-4 py-2 rounded-full hover:bg-red-600 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
              @click="confirmDelete"
            >{{ deleting ? 'Excluindo...' : 'Excluir' }}</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
