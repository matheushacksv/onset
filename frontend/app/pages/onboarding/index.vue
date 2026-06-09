<template>
  <div class="p-8 max-w-6xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div>
        <p class="text-xs text-neutral-500 tracking-widest uppercase mb-1">Módulo</p>
        <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white tracking-tight">Onboarding</h1>
      </div>
      <div class="flex items-center gap-2">
        <div v-if="!isDesenvolvedor" ref="newMenuRef" class="relative">
          <button
            class="flex items-center gap-2 px-4 py-2 bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 text-sm font-semibold rounded-full hover:-translate-y-0.5 transition-all disabled:opacity-50"
            :disabled="loadingDeals || creatingBlank"
            @click="newMenuOpen = !newMenuOpen"
          >
            <svg v-if="loadingDeals || creatingBlank" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Novo
            <svg class="w-3 h-3 transition-transform" :class="newMenuOpen ? 'rotate-180' : ''" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
            </svg>
          </button>
          <div
            v-show="newMenuOpen"
            class="absolute right-0 top-full mt-1 bg-neutral-900 ring-1 ring-white/10 rounded-xl py-1 min-w-64 z-50 shadow-xl"
          >
            <button class="w-full text-left px-3 py-2.5 text-sm text-white/80 hover:bg-white/5 transition-colors" @click="onNewWithDeal">
              <p class="font-medium">Onboarding com deal</p>
              <p class="text-[11px] text-white/40">Vincula a um deal do Pipedrive</p>
            </button>
            <button class="w-full text-left px-3 py-2.5 text-sm text-white/80 hover:bg-white/5 transition-colors" @click="onNewBlank">
              <p class="font-medium">Material em branco (IA)</p>
              <p class="text-[11px] text-white/40">Abre editor direto, sem deal nem formulário</p>
            </button>
            <button class="w-full text-left px-3 py-2.5 text-sm text-white/80 hover:bg-white/5 transition-colors" @click="onCloneExisting">
              <p class="font-medium">Duplicar material existente</p>
              <p class="text-[11px] text-white/40">Clona conteúdo de outro material publicado</p>
            </button>
          </div>
        </div>
        <button
          v-if="user?.is_superuser"
          class="flex items-center gap-1.5 px-3 py-2 text-sm font-medium border border-white/[0.08] rounded-full hover:bg-white/5 transition-all disabled:opacity-40"
          :disabled="creatingTest"
          @click="handleCreateTest"
        >
          <svg v-if="creatingTest" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
          <svg v-else class="w-4 h-4 text-white/40" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9.75 3.104v5.714a2.25 2.25 0 0 1-.659 1.591L5 14.5M9.75 3.104c-.251.023-.501.05-.75.082m.75-.082a24.301 24.301 0 0 1 4.5 0m0 0v5.714c0 .597.237 1.17.659 1.591L19.8 15.3M14.25 3.104c.251.023.501.05.75.082M19.8 15.3l-1.57.393A9.065 9.065 0 0 1 12 15a9.065 9.065 0 0 0-6.23.693L5 14.5m14.8.8 1.402 1.402c1.232 1.232.65 3.318-1.067 3.611A48.309 48.309 0 0 1 12 21c-2.773 0-5.491-.235-8.135-.687-1.718-.293-2.3-2.379-1.067-3.61L5 14.5" />
          </svg>
          Teste
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-5 gap-6">
      <!-- Lista de onboardings existentes -->
      <div class="lg:col-span-3">
        <div v-if="loadingList" class="space-y-3">
          <div v-for="i in 3" :key="i" class="h-20 bg-black/[0.03] dark:bg-white/[0.03] rounded-2xl animate-pulse" />
        </div>
        <div v-else-if="onboardings.length === 0" class="flex flex-col items-center justify-center py-20 text-center">
          <div class="w-12 h-12 rounded-2xl bg-black/[0.03] dark:bg-white/[0.03] ring-1 ring-black/[0.06] dark:ring-white/[0.06] flex items-center justify-center mb-4">
            <svg class="w-5 h-5 text-neutral-300 dark:text-white/20" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m0 12.75h7.5m-7.5 3H12M10.5 2.25H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z" />
            </svg>
          </div>
          <p class="text-neutral-400 dark:text-white/30 text-sm">Nenhum onboarding ainda</p>
          <p class="text-neutral-300 dark:text-white/20 text-xs mt-1">Clique em "Novo onboarding" para começar</p>
        </div>
        <div v-else class="space-y-3">
          <div
            v-for="item in onboardings"
            :key="item.id"
            class="relative group bg-black/[0.03] dark:bg-white/[0.03] ring-1 ring-black/[0.06] dark:ring-white/[0.06] rounded-2xl p-4 hover:bg-black/[0.05] dark:hover:bg-white/[0.05] hover:ring-black/10 dark:hover:ring-white/10 transition-all"
          >
            <NuxtLink :to="`/onboarding/${item.id}`" class="block pr-8">
              <div class="flex items-start justify-between gap-4">
                <div class="min-w-0">
                  <p class="text-neutral-900 dark:text-white text-sm font-medium truncate">{{ cleanDealName(item.pipedrive_deal_name) }}</p>
                </div>
                <div class="flex items-center gap-1.5 shrink-0 transition-opacity group-hover:opacity-0">
                  <span
                    v-if="!item.pipedrive_deal_id"
                    class="text-[10px] px-2 py-0.5 rounded-full font-medium uppercase tracking-wide bg-amber-400/15 text-amber-600 dark:text-amber-300"
                  >
                    Sem deal
                  </span>
                  <span
                    class="text-xs px-2.5 py-1 rounded-full font-medium"
                    :class="{
                      'bg-black/5 dark:bg-white/5 text-neutral-500 dark:text-white/40': item.status === 'draft',
                      'bg-blue-400/15 text-blue-600 dark:text-blue-300': item.status === 'complete',
                      'bg-emerald-400/15 text-emerald-600 dark:text-emerald-300': item.status === 'synced',
                    }"
                  >
                    {{ STATUS_LABEL[item.status] }}
                  </span>
                </div>
              </div>
              <div class="mt-3 flex items-center gap-3">
                <div class="flex-1 h-1 bg-black/[0.06] dark:bg-white/[0.06] rounded-full overflow-hidden">
                  <div class="h-full bg-neutral-400 dark:bg-white/20 rounded-full transition-all" :style="{ width: `${item.progress ?? 0}%` }" />
                </div>
                <span class="text-xs text-neutral-400 dark:text-white/30 shrink-0">{{ item.progress ?? 0 }}%</span>
              </div>
            </NuxtLink>

            <!-- Botão materiais (quando gerado) -->
            <a
              v-if="item.material_status === 'complete'"
              :href="`/onboarding/${item.id}/materials`"
              target="_blank"
              class="mt-3 flex items-center gap-1.5 text-xs font-medium text-emerald-600 dark:text-emerald-400 hover:text-emerald-700 dark:hover:text-emerald-300 transition-colors"
              @click.stop
            >
              <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25" />
              </svg>
              Ver materiais
            </a>

            <!-- chevron repouso / ações hover -->
            <div class="absolute top-4 right-4 flex items-center justify-center gap-1">
              <svg class="w-4 h-4 text-neutral-300 dark:text-white/20 group-hover:hidden" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
              <button
                v-if="!isDesenvolvedor && !item.pipedrive_deal_id"
                class="hidden group-hover:flex items-center justify-center p-1 rounded-lg text-amber-500 dark:text-amber-400 hover:bg-amber-400/10 transition-all"
                title="Anexar deal Pipedrive"
                @click.prevent="openAttach(item)"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M13.19 8.688a4.5 4.5 0 0 1 1.242 7.244l-4.5 4.5a4.5 4.5 0 0 1-6.364-6.364l1.757-1.757m13.35-.622 1.757-1.757a4.5 4.5 0 0 0-6.364-6.364l-4.5 4.5a4.5 4.5 0 0 0 1.242 7.244" />
                </svg>
              </button>
              <button
                v-if="!isDesenvolvedor"
                class="hidden group-hover:flex items-center justify-center p-1 rounded-lg text-neutral-400 dark:text-white/30 hover:text-neutral-700 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/10 transition-all"
                title="Duplicar onboarding"
                @click.prevent="openDuplicate(item)"
              >
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 17.25v3.375c0 .621-.504 1.125-1.125 1.125h-9.75a1.125 1.125 0 0 1-1.125-1.125V7.875c0-.621.504-1.125 1.125-1.125H6.75a9.06 9.06 0 0 1 1.5.124m7.5 10.376h3.375c.621 0 1.125-.504 1.125-1.125V11.25c0-4.46-3.243-8.161-7.5-8.876a9.06 9.06 0 0 0-1.5-.124H9.375c-.621 0-1.125.504-1.125 1.125v3.5m7.5 10.375H9.375a1.125 1.125 0 0 1-1.125-1.125v-9.25m12 6.625v-1.875a3.375 3.375 0 0 0-3.375-3.375h-1.5a1.125 1.125 0 0 1-1.125-1.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H9.75" />
                </svg>
              </button>
              <button
                v-if="!isDesenvolvedor"
                class="hidden group-hover:flex items-center justify-center p-1 rounded-lg text-neutral-400 dark:text-white/30 hover:text-red-500 hover:bg-red-500/10 transition-all"
                :disabled="deletingId === item.id"
                @click.prevent="deleteOnboarding(item.id)"
              >
                <svg v-if="deletingId === item.id" class="w-3.5 h-3.5 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                </svg>
                <svg v-else class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Painel de seleção de deal -->
      <div class="lg:col-span-2">
        <div class="bg-black/[0.03] dark:bg-white/[0.03] ring-1 ring-black/[0.06] dark:ring-white/[0.06] rounded-2xl p-5">
          <p class="text-xs text-neutral-500 tracking-widest uppercase mb-4">Selecionar deal</p>

          <div class="relative mb-3">
            <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-300 dark:text-white/20 pointer-events-none" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" />
            </svg>
            <input
              v-model="dealQuery"
              placeholder="Filtrar deals..."
              :disabled="allDeals.length === 0"
              class="w-full pl-9 pr-4 py-2.5 bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl text-sm text-neutral-900 dark:text-white placeholder-neutral-400 dark:placeholder-white/20 focus:outline-none focus:border-black/20 dark:focus:border-white/20 transition-colors disabled:opacity-40"
            />
          </div>

          <div v-if="loadingDeals" class="space-y-2">
            <div v-for="i in 3" :key="i" class="h-14 bg-black/[0.03] dark:bg-white/[0.03] rounded-xl animate-pulse" />
          </div>
          <div v-else-if="allDeals.length === 0" class="py-8 text-center text-neutral-300 dark:text-white/20 text-xs">
            Clique em "Novo onboarding" para carregar os deals
          </div>
          <div v-else-if="filteredDeals.length === 0" class="py-6 text-center text-neutral-400 dark:text-white/30 text-xs">
            Nenhum deal encontrado
          </div>
          <div v-else class="space-y-2 max-h-80 overflow-y-auto">
            <button
              v-for="deal in filteredDeals"
              :key="deal.id"
              class="w-full text-left p-3 rounded-xl bg-black/[0.03] dark:bg-white/[0.03] ring-1 ring-black/[0.06] dark:ring-white/[0.06] hover:bg-black/[0.06] dark:hover:bg-white/[0.06] hover:ring-black/10 dark:hover:ring-white/10 transition-all disabled:opacity-50"
              :disabled="creatingId === deal.id"
              @click="startOnboarding(deal)"
            >
              <div class="flex items-center justify-between gap-2">
                <div class="min-w-0">
                  <p class="text-neutral-900 dark:text-white text-xs font-medium truncate">{{ cleanDealName(deal.title) }}</p>
                </div>
                <div v-if="creatingId === deal.id" class="shrink-0">
                  <svg class="w-4 h-4 text-neutral-400 dark:text-white/40 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
                  </svg>
                </div>
                <svg v-else class="w-3.5 h-3.5 text-neutral-300 dark:text-white/20 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                  <path stroke-linecap="round" stroke-linejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
                </svg>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>

    <ObDuplicateModal
      :open="duplicateOpen"
      :source-id="duplicateSource?.id ?? null"
      :source-name="duplicateSource ? cleanDealName(duplicateSource.pipedrive_deal_name) : ''"
      :has-material="duplicateSource?.material_status === 'complete'"
      @close="duplicateOpen = false"
      @duplicated="onDuplicated"
    />

    <ObAttachDealModal
      :open="attachOpen"
      :onboarding-id="attachTarget?.id ?? null"
      @close="attachOpen = false"
      @attached="onAttached"
    />

    <ObCloneMaterialModal
      :open="cloneOpen"
      @close="cloneOpen = false"
      @cloned="onCloned"
    />
  </div>
</template>

<script setup lang="ts">
const { hasRole, user, fetchAuth } = useAuth()
if (!hasRole('Assessor') && !hasRole('Desenvolvedor')) await navigateTo('/')

const isDesenvolvedor = computed(() => user.value?.role?.includes('Desenvolvedor') && !user.value?.is_superuser)

import { cleanDealName, generateFakeForm } from '~/composables/useOnboarding'

const STATUS_LABEL: Record<string, string> = {
  draft: 'Rascunho',
  complete: 'Concluído',
  synced: 'Sincronizado',
}

type Deal = { id: number; title: string; person_name: string; value: number }
const DEALS_CACHE_KEY = 'ob:deals'
const DEALS_CACHE_TTL = 60_000

const dealQuery = ref('')
const allDeals = ref<Deal[]>([])
const loadingDeals = ref(false)
const creatingId = ref<number | null>(null)
const deletingId = ref<number | null>(null)

const readDealsCache = (): Deal[] | null => {
  try {
    const raw = sessionStorage.getItem(DEALS_CACHE_KEY)
    if (!raw) return null
    const { data, ts } = JSON.parse(raw)
    return Date.now() - ts < DEALS_CACHE_TTL ? data : null
  } catch { return null }
}
const writeDealsCache = (data: Deal[]) => {
  try { sessionStorage.setItem(DEALS_CACHE_KEY, JSON.stringify({ data, ts: Date.now() })) } catch {}
}

const filteredDeals = computed(() => {
  if (!dealQuery.value) return allDeals.value
  const q = dealQuery.value.toLowerCase()
  return allDeals.value.filter(d =>
    d.title.toLowerCase().includes(q) || (d.person_name || '').toLowerCase().includes(q)
  )
})

const onboardings = ref<{
  id: number
  pipedrive_deal_id: string | null
  pipedrive_deal_name: string
  nome_empresa: string
  nicho: string
  status: string
  progress: number
  material_status: string | null
}[]>([])
const loadingList = ref(true)

const loadOnboardings = async () => {
  loadingList.value = true
  try {
    onboardings.value = await fetchAuth('/api/onboarding/')
  } catch {
    onboardings.value = []
  } finally {
    loadingList.value = false
  }
}

const loadDeals = async () => {
  if (loadingDeals.value) return
  const cached = readDealsCache()
  if (cached) { allDeals.value = cached; dealQuery.value = ''; return }
  loadingDeals.value = true
  dealQuery.value = ''
  try {
    const data = await fetchAuth<Deal[]>('/api/onboarding/deals/')
    allDeals.value = data
    writeDealsCache(data)
  } catch {
    allDeals.value = []
  } finally {
    loadingDeals.value = false
  }
}

const startOnboarding = async (deal: { id: number; title: string }) => {
  creatingId.value = deal.id
  try {
    const result = await fetchAuth<{ id: number }>('/api/onboarding/', {
      method: 'POST',
      body: { pipedrive_deal_id: String(deal.id), pipedrive_deal_name: deal.title },
    })
    await navigateTo(`/onboarding/${result.id}`)
  } catch (err: any) {
    if (err?.status === 409) {
      const existing = onboardings.value.find(o => o.pipedrive_deal_name === deal.title)
      if (existing) await navigateTo(`/onboarding/${existing.id}`)
    }
  } finally {
    creatingId.value = null
  }
}

type OnboardingRow = typeof onboardings.value[number]
const duplicateOpen = ref(false)
const duplicateSource = ref<OnboardingRow | null>(null)
const openDuplicate = (item: OnboardingRow) => {
  duplicateSource.value = item
  duplicateOpen.value = true
}
const onDuplicated = async (newId: number) => {
  duplicateOpen.value = false
  await navigateTo(`/onboarding/${newId}`)
}

// ── Novo (dropdown) ─────────────────────────────────────────
const { createBlankMaterial } = useOnboardingCreate()
const newMenuRef = ref<HTMLElement | null>(null)
const newMenuOpen = ref(false)
const creatingBlank = ref(false)
const cloneOpen = ref(false)

const onNewWithDeal = async () => {
  newMenuOpen.value = false
  await loadDeals()
}
const onNewBlank = async () => {
  if (creatingBlank.value) return
  newMenuOpen.value = false
  creatingBlank.value = true
  try {
    const r = await createBlankMaterial()
    await navigateTo(`/onboarding/${r.id}/materials`)
  } catch {
    /* noop */
  } finally {
    creatingBlank.value = false
  }
}
const onCloneExisting = () => {
  newMenuOpen.value = false
  cloneOpen.value = true
}
const onCloned = async (newId: number) => {
  cloneOpen.value = false
  await navigateTo(`/onboarding/${newId}/materials`)
}

const creatingTest = ref(false)
const handleCreateTest = async () => {
  creatingTest.value = true
  try {
    const { id } = await fetchAuth<{ id: number }>('/api/onboarding/', {
      method: 'POST',
      body: { pipedrive_deal_name: '🧪 Teste — Tech Solutions' },
    })
    const fake = generateFakeForm()
    const payload: Record<string, unknown> = {}
    for (const k of Object.keys(fake)) {
      const v = (fake as any)[k]
      if (v !== undefined) payload[k] = v
    }
    await fetchAuth(`/api/onboarding/${id}`, { method: 'PATCH', body: payload })
    await navigateTo(`/onboarding/${id}`)
  } finally {
    creatingTest.value = false
  }
}

onMounted(() => {
  const handler = (e: MouseEvent) => {
    if (newMenuRef.value && !newMenuRef.value.contains(e.target as Node)) newMenuOpen.value = false
  }
  document.addEventListener('click', handler)
  onUnmounted(() => document.removeEventListener('click', handler))
})

// ── Attach deal ──────────────────────────────────────────────
const attachOpen = ref(false)
const attachTarget = ref<OnboardingRow | null>(null)
const openAttach = (item: OnboardingRow) => {
  attachTarget.value = item
  attachOpen.value = true
}
const onAttached = async (deal: { id: number; title: string }) => {
  if (attachTarget.value) {
    attachTarget.value.pipedrive_deal_id = String(deal.id)
    attachTarget.value.pipedrive_deal_name = deal.title
  }
  attachOpen.value = false
}

const deleteOnboarding = async (id: number) => {
  if (!confirm('Deletar este onboarding?')) return
  deletingId.value = id
  try {
    await fetchAuth(`/api/onboarding/${id}`, { method: 'DELETE' })
    onboardings.value = onboardings.value.filter(o => o.id !== id)
  } catch {
    // silently ignore
  } finally {
    deletingId.value = null
  }
}

onMounted(() => {
  const cached = readDealsCache()
  if (cached) allDeals.value = cached
})

await loadOnboardings()
</script>
