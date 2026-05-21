<template>
  <div class="min-h-full max-w-3xl mx-auto px-6 py-10">
    <!-- Header -->
    <div class="flex items-center justify-between mb-8">
      <div class="flex items-center gap-3 min-w-0">
        <NuxtLink to="/" class="text-white/30 hover:text-white/60 transition-colors shrink-0">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
          </svg>
        </NuxtLink>
        <div>
          <h1 class="text-white text-lg font-semibold">Regras de onboarding</h1>
          <p class="text-xs text-white/40">Avisos que cada assessor confirma antes de sincronizar.</p>
        </div>
      </div>
      <button
        class="px-4 py-2 bg-white text-neutral-900 text-xs font-semibold rounded-full hover:-translate-y-0.5 transition-all"
        @click="openCreate"
      >
        + Nova regra
      </button>
    </div>

    <!-- Lista -->
    <div v-if="loading" class="space-y-3">
      <div v-for="i in 3" :key="i" class="h-20 bg-white/[0.03] rounded-2xl animate-pulse" />
    </div>
    <div v-else-if="rules.length === 0" class="py-16 text-center text-white/30 text-sm">
      Nenhuma regra criada ainda.
    </div>
    <div v-else class="space-y-3">
      <div
        v-for="rule in rules"
        :key="rule.id"
        class="bg-white/5 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-4 flex items-start gap-4"
      >
        <div class="flex-1 min-w-0">
          <div class="flex items-center gap-2 mb-1">
            <p class="text-white text-sm font-medium truncate">{{ rule.name }}</p>
            <span
              v-if="!rule.active"
              class="text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded bg-white/10 text-white/40"
            >Inativa</span>
          </div>
          <p class="text-xs text-white/40 line-clamp-2 whitespace-pre-line">{{ rule.content }}</p>
        </div>
        <div class="shrink-0 flex items-center gap-1">
          <button class="px-2.5 py-1 text-xs text-white/50 hover:text-white transition-colors" @click="openEdit(rule)">Editar</button>
          <button class="px-2.5 py-1 text-xs text-red-400/60 hover:text-red-400 transition-colors" @click="remove(rule)">Excluir</button>
        </div>
      </div>
    </div>

    <!-- Modal form -->
    <Teleport to="body">
      <div
        v-if="modalOpen"
        class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm"
        @click.self="modalOpen = false"
      >
        <div class="w-full max-w-lg bg-neutral-900 ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl">
          <div class="flex items-center justify-between mb-5">
            <h2 class="text-white font-semibold">{{ editing ? 'Editar regra' : 'Nova regra' }}</h2>
            <button class="text-white/30 hover:text-white/70 text-xl leading-none" @click="modalOpen = false">×</button>
          </div>

          <label class="block text-xs text-white/50 mb-1.5">Nome</label>
          <input
            v-model="formData.name"
            placeholder="Ex: Configurar webhook do Pipedrive"
            class="w-full mb-4 px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors"
          />

          <label class="block text-xs text-white/50 mb-1.5">Texto (markdown — links: <code class="text-white/40">[texto](url)</code>)</label>
          <textarea
            v-model="formData.content"
            placeholder="Siga o passo a passo em [esta documentação](https://...) antes de marcar."
            class="w-full mb-4 px-3.5 py-2.5 bg-white/5 border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20 transition-colors resize-vertical"
            style="min-height:120px; line-height:1.6"
          />

          <div class="flex items-center gap-4 mb-5">
            <label class="flex items-center gap-2 text-xs text-white/60 cursor-pointer">
              <input v-model="formData.active" type="checkbox" class="accent-white" />
              Ativa
            </label>
            <label class="flex items-center gap-2 text-xs text-white/60">
              Ordem
              <input
                v-model.number="formData.order"
                type="number"
                class="w-16 px-2 py-1 bg-white/5 border border-white/10 rounded-lg text-sm text-white focus:outline-none focus:border-white/20"
              />
            </label>
          </div>

          <p v-if="error" class="text-xs text-red-400 mb-3">{{ error }}</p>

          <div class="flex justify-end gap-2">
            <button class="px-4 py-2 text-xs font-medium text-white/60 hover:text-white transition-colors" @click="modalOpen = false">Cancelar</button>
            <button
              class="px-4 py-2 bg-white text-neutral-900 text-xs font-semibold rounded-full hover:bg-white/90 transition-colors disabled:opacity-40"
              :disabled="!formData.name.trim() || !formData.content.trim() || saving"
              @click="save"
            >
              {{ saving ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import type { Rule, RuleInput } from '~/composables/useRules'

const { user } = useAuth()
if (!user.value?.is_superuser) await navigateTo('/')

const { listRules, createRule, updateRule, deleteRule } = useRules()

const rules = ref<Rule[]>([])
const loading = ref(true)
const modalOpen = ref(false)
const editing = ref<Rule | null>(null)
const saving = ref(false)
const error = ref('')

const formData = reactive<RuleInput>({ name: '', content: '', active: true, order: 0 })

const load = async () => {
  loading.value = true
  try { rules.value = await listRules() }
  catch { rules.value = [] }
  finally { loading.value = false }
}

const openCreate = () => {
  editing.value = null
  Object.assign(formData, { name: '', content: '', active: true, order: rules.value.length })
  error.value = ''
  modalOpen.value = true
}

const openEdit = (rule: Rule) => {
  editing.value = rule
  Object.assign(formData, { name: rule.name, content: rule.content, active: rule.active, order: rule.order })
  error.value = ''
  modalOpen.value = true
}

const save = async () => {
  if (saving.value) return
  saving.value = true
  error.value = ''
  try {
    if (editing.value) await updateRule(editing.value.id, { ...formData })
    else await createRule({ ...formData })
    modalOpen.value = false
    await load()
  } catch {
    error.value = 'Falha ao salvar regra.'
  } finally {
    saving.value = false
  }
}

const remove = async (rule: Rule) => {
  if (!confirm(`Excluir a regra "${rule.name}"?`)) return
  try {
    await deleteRule(rule.id)
    await load()
  } catch {
    alert('Falha ao excluir regra.')
  }
}

await load()
</script>
