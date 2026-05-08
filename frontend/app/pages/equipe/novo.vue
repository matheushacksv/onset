<script setup lang="ts">
const { user, fetchAuth } = useAuth()
const router = useRouter()

if (!user.value?.is_superuser) {
  await navigateTo('/')
}

const availableRoles = ref<string[]>([])

const form = reactive({
  name: '',
  email: '',
  role: [] as string[],
  is_staff: false,
  password: '',
  repeat_password: '',
})

const roleMenuOpen = ref(false)
const roleMenuRef = ref<HTMLElement | null>(null)

function toggleRole(role: string) {
  const i = form.role.indexOf(role)
  if (i >= 0) form.role.splice(i, 1)
  else form.role.push(role)
}

const roleLabel = computed(() => {
  if (!form.role.length) return 'Selecione funções (opcional)'
  if (form.role.length === 1) return form.role[0]
  return `${form.role.length} selecionadas`
})

onMounted(async () => {
  try {
    availableRoles.value = await fetchAuth<string[]>('/api/auth/roles')
  } catch {
    availableRoles.value = []
  }
  document.addEventListener('click', (e) => {
    if (roleMenuRef.value && !roleMenuRef.value.contains(e.target as Node)) {
      roleMenuOpen.value = false
    }
  })
})

const loading = ref(false)
const error = ref<string | null>(null)
const success = ref(false)

const passwordsMatch = computed(() =>
  !form.repeat_password || form.password === form.repeat_password
)

const canSubmit = computed(() =>
  form.email.trim() &&
  form.password.length >= 8 &&
  passwordsMatch.value &&
  !loading.value
)

async function submit() {
  if (!canSubmit.value) return
  loading.value = true
  error.value = null
  try {
    await fetchAuth('/api/auth/create-user', {
      method: 'POST',
      body: {
        email: form.email.trim(),
        name: form.name.trim() || null,
        role: form.role,
        is_staff: form.is_staff,
        password: form.password,
        repeat_password: form.repeat_password,
      },
    })
    success.value = true
    setTimeout(() => router.push('/'), 1200)
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao criar usuário'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-full p-6 md:p-10 max-w-xl mx-auto">

    <button
      class="text-sm text-neutral-500 dark:text-white/50 hover:text-neutral-800 dark:text-white/80 transition-colors mb-6 flex items-center gap-1.5"
      @click="router.back()"
    >
      <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
        <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
      </svg>
      Voltar
    </button>

    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-neutral-900 dark:text-white">Novo funcionário</h1>
      <p class="text-sm text-neutral-500 dark:text-white/40 mt-1">Crie uma conta de acesso à plataforma.</p>
    </div>

    <form
      class="bg-white dark:bg-white/5 backdrop-blur-xl ring-1 ring-neutral-200 dark:ring-white/10 rounded-2xl p-6 space-y-5"
      @submit.prevent="submit"
    >

      <div>
        <label class="block text-xs font-medium text-neutral-600 dark:text-white/60 uppercase tracking-widest mb-2">
          Nome
        </label>
        <input
          v-model="form.name"
          type="text"
          placeholder="Nome completo"
          class="w-full bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-2.5 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-white/30 focus:outline-none focus:ring-neutral-400 dark:focus:ring-white/30 transition-shadow"
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-neutral-600 dark:text-white/60 uppercase tracking-widest mb-2">
          Email <span class="text-red-400">*</span>
        </label>
        <input
          v-model="form.email"
          type="email"
          required
          placeholder="email@empresa.com"
          class="w-full bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-2.5 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-white/30 focus:outline-none focus:ring-neutral-400 dark:focus:ring-white/30 transition-shadow"
        />
      </div>

      <div ref="roleMenuRef" class="relative">
        <label class="block text-xs font-medium text-neutral-600 dark:text-white/60 uppercase tracking-widest mb-2">
          Funções
        </label>
        <button
          type="button"
          class="w-full bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-2.5 text-sm text-left flex items-center justify-between hover:ring-neutral-300 dark:hover:ring-white/20 transition-shadow"
          :class="form.role.length ? 'text-neutral-900 dark:text-white' : 'text-neutral-500 dark:text-white/40'"
          @click="roleMenuOpen = !roleMenuOpen"
        >
          <span class="truncate">{{ roleLabel }}</span>
          <svg class="w-4 h-4 text-neutral-500 dark:text-white/40 shrink-0 transition-transform" :class="{ 'rotate-180': roleMenuOpen }" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
          </svg>
        </button>

        <div
          v-if="roleMenuOpen"
          class="absolute z-10 left-0 right-0 mt-2 bg-white dark:bg-neutral-900 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl overflow-hidden shadow-xl"
        >
          <div v-if="!availableRoles.length" class="px-4 py-3 text-sm text-neutral-500 dark:text-white/40">
            Nenhuma função disponível
          </div>
          <button
            v-for="role in availableRoles"
            :key="role"
            type="button"
            class="w-full flex items-center gap-3 px-4 py-2.5 text-sm text-neutral-900 dark:text-white hover:bg-neutral-100 dark:hover:bg-white/5 transition-colors text-left"
            @click="toggleRole(role)"
          >
            <span
              class="w-4 h-4 rounded border ring-1 flex items-center justify-center shrink-0 transition-colors"
              :class="form.role.includes(role) ? 'bg-neutral-900 dark:bg-white border-neutral-900 dark:border-white ring-neutral-900 dark:ring-white' : 'border-neutral-300 dark:border-white/20 ring-neutral-200 dark:ring-white/10'"
            >
              <svg v-if="form.role.includes(role)" class="w-3 h-3 text-white dark:text-neutral-900" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="3">
                <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
              </svg>
            </span>
            {{ role }}
          </button>
        </div>

        <div v-if="form.role.length" class="flex flex-wrap gap-1.5 mt-2">
          <span
            v-for="role in form.role"
            :key="role"
            class="text-xs text-neutral-700 dark:text-white/70 bg-neutral-100 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 px-2.5 py-1 rounded-full flex items-center gap-1.5"
          >
            {{ role }}
            <button
              type="button"
              class="text-neutral-500 dark:text-white/40 hover:text-neutral-900 dark:hover:text-white transition-colors"
              @click="toggleRole(role)"
            >
              <svg class="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </span>
        </div>
      </div>

      <div>
        <label class="block text-xs font-medium text-neutral-600 dark:text-white/60 uppercase tracking-widest mb-2">
          Senha <span class="text-red-400">*</span>
        </label>
        <input
          v-model="form.password"
          type="password"
          required
          minlength="8"
          placeholder="Mínimo 8 caracteres"
          class="w-full bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-2.5 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-white/30 focus:outline-none focus:ring-neutral-400 dark:focus:ring-white/30 transition-shadow"
        />
      </div>

      <div>
        <label class="block text-xs font-medium text-neutral-600 dark:text-white/60 uppercase tracking-widest mb-2">
          Repetir senha <span class="text-red-400">*</span>
        </label>
        <input
          v-model="form.repeat_password"
          type="password"
          required
          placeholder="Confirme a senha"
          class="w-full bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-2.5 text-sm text-neutral-900 dark:text-white placeholder:text-neutral-400 dark:placeholder:text-white/30 focus:outline-none focus:ring-neutral-400 dark:focus:ring-white/30 transition-shadow"
          :class="{ 'ring-red-400/50': !passwordsMatch }"
        />
        <p v-if="!passwordsMatch" class="text-xs text-red-400 mt-1.5">
          As senhas não coincidem.
        </p>
      </div>

      <label class="flex items-start gap-3 bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-3 cursor-pointer">
        <input
          v-model="form.is_staff"
          type="checkbox"
          class="mt-0.5 w-4 h-4 rounded border-neutral-300 dark:border-white/20"
        />
        <div class="flex-1">
          <p class="text-sm font-medium text-neutral-900 dark:text-white">Acesso de admin</p>
          <p class="text-xs text-neutral-500 dark:text-white/40 mt-0.5">Pode editar membros e acessar painel admin</p>
        </div>
      </label>

      <div v-if="error" class="bg-red-500/10 ring-1 ring-red-400/30 rounded-xl px-4 py-3 text-sm text-red-300">
        {{ error }}
      </div>

      <div v-if="success" class="bg-emerald-500/10 ring-1 ring-emerald-400/30 rounded-xl px-4 py-3 text-sm text-emerald-300">
        Funcionário criado com sucesso. Redirecionando...
      </div>

      <div class="flex justify-end gap-3 pt-2">
        <button
          type="button"
          class="bg-neutral-100 dark:bg-white/10 text-neutral-700 dark:text-white text-sm font-medium px-5 py-2.5 rounded-full hover:bg-neutral-200 dark:hover:bg-white/15 transition-colors ring-1 ring-neutral-200 dark:ring-white/10"
          @click="router.back()"
        >
          Cancelar
        </button>
        <button
          type="submit"
          :disabled="!canSubmit"
          class="bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 text-sm font-medium px-5 py-2.5 rounded-full hover:bg-neutral-800 dark:hover:bg-white/90 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {{ loading ? 'Criando...' : 'Criar funcionário' }}
        </button>
      </div>
    </form>
  </div>
</template>
