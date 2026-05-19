<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/70 backdrop-blur-sm"
      @click.self="$emit('close')"
    >
      <div class="w-full max-w-md bg-neutral-900 ring-1 ring-white/10 rounded-2xl p-6 shadow-2xl">
        <div class="flex items-center justify-between mb-5">
          <h2 class="text-white font-semibold">Compartilhar com o cliente</h2>
          <button class="text-white/30 hover:text-white/70 text-xl leading-none" @click="$emit('close')">×</button>
        </div>

        <!-- Loading -->
        <div v-if="loading" class="py-10 flex justify-center">
          <div class="w-6 h-6 rounded-full border-2 border-white/20 border-t-white/60 animate-spin" />
        </div>

        <!-- Link ativo -->
        <template v-else-if="share && !share.revoked">
          <p class="text-xs text-white/40 mb-2">Link de visualização ativo</p>
          <div class="flex gap-2 mb-3">
            <input
              :value="fullUrl"
              readonly
              class="flex-1 px-3 py-2 bg-white/[0.04] border border-white/10 rounded-xl text-xs text-white/80 focus:outline-none"
            />
            <button
              class="px-3 py-2 bg-white text-neutral-900 text-xs font-medium rounded-xl hover:bg-white/90 transition-colors shrink-0"
              @click="copy"
            >
              {{ copied ? 'Copiado' : 'Copiar' }}
            </button>
          </div>
          <div class="grid grid-cols-3 gap-2 mb-5 text-center">
            <div class="bg-white/[0.04] rounded-xl py-2">
              <p class="text-sm text-white font-semibold">{{ share.view_count }}</p>
              <p class="text-[10px] text-white/30 uppercase tracking-wide">Visitas</p>
            </div>
            <div class="bg-white/[0.04] rounded-xl py-2">
              <p class="text-sm text-white font-semibold">{{ share.has_password ? 'Sim' : 'Não' }}</p>
              <p class="text-[10px] text-white/30 uppercase tracking-wide">Senha</p>
            </div>
            <div class="bg-white/[0.04] rounded-xl py-2">
              <p class="text-sm text-white font-semibold">{{ expiryLabel }}</p>
              <p class="text-[10px] text-white/30 uppercase tracking-wide">Expira</p>
            </div>
          </div>
          <div class="flex gap-2">
            <button
              class="flex-1 py-2 text-sm text-white/50 hover:text-white/80 border border-white/10 rounded-xl transition-colors"
              @click="regenMode = true; share = null"
            >
              Gerar novo link
            </button>
            <button
              class="flex-1 py-2 text-sm text-red-300/70 hover:text-red-300 border border-red-500/20 rounded-xl transition-colors disabled:opacity-40"
              :disabled="working"
              @click="onRevoke"
            >
              Revogar
            </button>
          </div>
        </template>

        <!-- Configurar novo link -->
        <template v-else>
          <p class="text-xs text-white/40 mb-2">Expiração</p>
          <div class="flex gap-1.5 flex-wrap mb-3">
            <button
              v-for="opt in EXPIRY_OPTS"
              :key="opt.value"
              class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
              :class="expiryMode === opt.value ? 'bg-white text-neutral-900' : 'bg-white/5 text-white/50 ring-1 ring-white/10'"
              @click="expiryMode = opt.value"
            >
              {{ opt.label }}
            </button>
          </div>
          <input
            v-if="expiryMode === 'custom'"
            v-model="customDate"
            type="date"
            class="w-full px-3 py-2 mb-3 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white focus:outline-none focus:border-white/20"
          />

          <label class="flex items-center gap-2 mb-2 cursor-pointer">
            <input v-model="usePassword" type="checkbox" class="accent-white" />
            <span class="text-xs text-white/60">Proteger com senha</span>
          </label>
          <input
            v-if="usePassword"
            v-model="password"
            type="text"
            placeholder="Senha do link"
            class="w-full px-3 py-2 mb-3 bg-white/[0.04] border border-white/10 rounded-xl text-sm text-white placeholder-white/20 focus:outline-none focus:border-white/20"
          />

          <p v-if="errorMsg" class="text-xs text-red-300/80 mb-2">{{ errorMsg }}</p>
          <button
            class="w-full py-2.5 bg-white text-neutral-900 text-sm font-medium rounded-xl hover:bg-white/90 transition-colors disabled:opacity-40"
            :disabled="working || (usePassword && !password)"
            @click="onCreate"
          >
            {{ working ? 'Gerando...' : 'Gerar link' }}
          </button>
        </template>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
interface ShareData {
  token: string
  url: string
  has_password: boolean
  expires_at: string | null
  revoked: boolean
  view_count: number
  last_viewed_at: string | null
  created_at: string
}

const props = defineProps<{ open: boolean; onboardingId: string }>()
defineEmits<{ close: [] }>()

const { fetchAuth } = useAuth()

const loading = ref(false)
const working = ref(false)
const share = ref<ShareData | null>(null)
const errorMsg = ref('')
const copied = ref(false)
const regenMode = ref(false)

const expiryMode = ref<'7' | '30' | '90' | 'custom' | 'never'>('30')
const customDate = ref('')
const usePassword = ref(false)
const password = ref('')

const EXPIRY_OPTS = [
  { value: '7' as const, label: '7 dias' },
  { value: '30' as const, label: '30 dias' },
  { value: '90' as const, label: '90 dias' },
  { value: 'custom' as const, label: 'Data...' },
  { value: 'never' as const, label: 'Nunca' },
]

const fullUrl = computed(() =>
  share.value ? `${window.location.origin}${share.value.url}` : ''
)

const expiryLabel = computed(() => {
  if (!share.value?.expires_at) return 'Nunca'
  try { return new Date(share.value.expires_at).toLocaleDateString('pt-BR') } catch { return '—' }
})

async function loadShare() {
  loading.value = true
  errorMsg.value = ''
  try {
    share.value = await fetchAuth<ShareData>(`/api/onboarding/${props.onboardingId}/materials/share`)
  } catch {
    share.value = null
  } finally {
    loading.value = false
  }
}

async function onCreate() {
  working.value = true
  errorMsg.value = ''
  const body: Record<string, unknown> = {}
  if (expiryMode.value === 'custom') {
    if (!customDate.value) { errorMsg.value = 'Escolha uma data.'; working.value = false; return }
    body.expires_at = new Date(customDate.value).toISOString()
  } else if (expiryMode.value !== 'never') {
    body.expires_in_days = Number(expiryMode.value)
  }
  if (usePassword.value && password.value) body.password = password.value
  try {
    share.value = await fetchAuth<ShareData>(`/api/onboarding/${props.onboardingId}/materials/share`, {
      method: 'POST',
      body,
    })
    regenMode.value = false
  } catch (e: any) {
    errorMsg.value = e?.data?.detail || 'Erro ao gerar o link.'
  } finally {
    working.value = false
  }
}

async function onRevoke() {
  if (!confirm('Revogar o link? O cliente perde o acesso imediatamente.')) return
  working.value = true
  try {
    await fetchAuth(`/api/onboarding/${props.onboardingId}/materials/share`, { method: 'DELETE' })
    share.value = null
  } catch { /* noop */ } finally {
    working.value = false
  }
}

function copy() {
  navigator.clipboard.writeText(fullUrl.value)
  copied.value = true
  setTimeout(() => { copied.value = false }, 1800)
}

watch(() => props.open, (v) => {
  if (v) {
    regenMode.value = false
    loadShare()
  }
})
</script>
