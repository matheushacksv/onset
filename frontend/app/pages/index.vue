<script setup lang="ts">
interface TeamUser {
  id: number
  name: string | null
  email: string
  avatar: string | null
  role: string[]
}

interface OnboardingItem {
  id: number
  pipedrive_deal_name: string
  material_status: string | null
}

const { user, fetchAuth, hasRole } = useAuth()
const router = useRouter()

const isDesenvolvedor = computed(() => user.value?.roles?.includes('Desenvolvedor') && !user.value?.is_superuser)

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Bom dia'
  if (h < 18) return 'Boa tarde'
  return 'Boa noite'
})

const dateLabel = computed(() => new Date().toLocaleDateString('pt-BR', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
}))

const firstName = computed(() => {
  const name = user.value?.name || user.value?.email || ''
  return name.split(' ')[0]
})

const onboardings = ref<OnboardingItem[]>([])
const team = ref<TeamUser[]>([])
const loading = ref(true)

const totalOnboardings = computed(() => onboardings.value.length)
const withMaterial = computed(() => onboardings.value.filter(o => o.material_status === 'complete').length)
const pendingMaterial = computed(() => totalOnboardings.value - withMaterial.value)

function roleLabel(role: string[]) {
  if (!role.length) return 'Sem função'
  return role.join(', ')
}

function initials(name: string | null, email: string) {
  const src = name || email
  return src.slice(0, 2).toUpperCase()
}

onMounted(async () => {
  try {
    const [onbData, teamData] = await Promise.all([
      fetchAuth<OnboardingItem[]>('/api/onboarding/'),
      fetchAuth<TeamUser[]>('/api/auth/users'),
    ])
    onboardings.value = onbData
    team.value = teamData
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="min-h-full p-6 md:p-10 space-y-8 max-w-5xl mx-auto">

    <!-- Saudação -->
    <div class="flex items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-semibold text-white">
          {{ greeting }}, {{ firstName }}
        </h1>
        <p class="text-sm text-white/40 mt-0.5 capitalize">{{ dateLabel }}</p>
      </div>
      <div v-if="user?.avatar" class="w-11 h-11 rounded-full overflow-hidden ring-1 ring-white/10 shrink-0">
        <img :src="user.avatar" :alt="user.name || ''" class="w-full h-full object-cover" />
      </div>
      <div v-else class="w-11 h-11 rounded-full bg-white/10 ring-1 ring-white/10 flex items-center justify-center text-white/60 text-sm font-medium shrink-0">
        {{ initials(user?.name ?? null, user?.email ?? '') }}
      </div>
    </div>

    <!-- Cards de métricas -->
    <div v-if="!loading" class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white/5 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6">
        <p class="text-xs text-white/40 uppercase tracking-widest mb-2">Total</p>
        <p class="text-4xl font-bold text-white">{{ totalOnboardings }}</p>
        <p class="text-sm text-white/40 mt-1">onboardings</p>
      </div>
      <div class="bg-white/5 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6">
        <p class="text-xs text-white/40 uppercase tracking-widest mb-2">Materiais gerados</p>
        <p class="text-4xl font-bold text-emerald-400">{{ withMaterial }}</p>
        <p class="text-sm text-white/40 mt-1">com IA concluída</p>
      </div>
      <div class="bg-white/5 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl p-6">
        <p class="text-xs text-white/40 uppercase tracking-widest mb-2">Pendentes</p>
        <p class="text-4xl font-bold text-amber-400">{{ pendingMaterial }}</p>
        <p class="text-sm text-white/40 mt-1">sem material gerado</p>
      </div>
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div v-for="i in 3" :key="i" class="bg-white/5 ring-1 ring-white/10 rounded-2xl p-6 animate-pulse h-28" />
    </div>

    <!-- Ações rápidas -->
    <div class="flex flex-wrap gap-3">
      <button
        v-if="!isDesenvolvedor"
        class="bg-white text-neutral-900 text-sm font-medium px-5 py-2.5 rounded-full hover:bg-white/90 transition-colors"
        @click="router.push('/onboarding')"
      >
        Novo Onboarding
      </button>
      <button
        class="bg-white/10 text-white text-sm font-medium px-5 py-2.5 rounded-full hover:bg-white/15 transition-colors ring-1 ring-white/10"
        @click="router.push('/onboarding')"
      >
        Ver Onboardings
      </button>
    </div>

    <!-- Equipe -->
    <div>
      <div class="flex items-center justify-between mb-4">
        <h2 class="text-sm font-medium text-white/50 uppercase tracking-widest">Equipe</h2>
        <button
          v-if="user?.is_superuser"
          class="text-xs font-medium text-white/70 hover:text-white bg-white/5 hover:bg-white/10 ring-1 ring-white/10 px-3 py-1.5 rounded-full transition-colors flex items-center gap-1.5"
          @click="router.push('/equipe/novo')"
        >
          <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Novo funcionário
        </button>
      </div>
      <div v-if="!loading" class="bg-white/5 backdrop-blur-xl ring-1 ring-white/10 rounded-2xl divide-y divide-white/5">
        <div
          v-for="member in team"
          :key="member.id"
          class="flex items-center gap-4 px-6 py-4"
        >
          <div class="shrink-0">
            <img
              v-if="member.avatar"
              :src="member.avatar"
              :alt="member.name || ''"
              class="w-9 h-9 rounded-full object-cover ring-1 ring-white/10"
            />
            <div
              v-else
              class="w-9 h-9 rounded-full bg-white/10 ring-1 ring-white/10 flex items-center justify-center text-white/50 text-xs font-medium"
            >
              {{ initials(member.name, member.email) }}
            </div>
          </div>
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-white truncate">{{ member.name || member.email }}</p>
            <p class="text-xs text-white/40 truncate">{{ member.email }}</p>
          </div>
          <div class="shrink-0 flex flex-wrap gap-1.5 justify-end max-w-[60%]">
            <span
              v-if="!member.role.length"
              class="text-xs text-white/40 bg-white/5 ring-1 ring-white/10 px-3 py-1 rounded-full"
            >
              Sem função
            </span>
            <span
              v-for="r in member.role"
              :key="r"
              class="text-xs text-white/50 bg-white/5 ring-1 ring-white/10 px-3 py-1 rounded-full"
            >
              {{ r }}
            </span>
          </div>
        </div>
        <div v-if="!team.length" class="px-6 py-8 text-center text-sm text-white/30">
          Nenhum funcionário encontrado.
        </div>
      </div>
      <div v-else class="bg-white/5 ring-1 ring-white/10 rounded-2xl animate-pulse h-40" />
    </div>

  </div>
</template>
