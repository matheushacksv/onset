<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <!-- Gradient bg blobs -->
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/8 rounded-full blur-3xl" />
    </div>

    <div class="relative w-full max-w-sm">
      <!-- Card -->
      <div class="border-gradient rounded-2xl bg-white/5 backdrop-blur-xl ring-1 ring-white/10 p-8">
        <!-- Header -->
        <div class="mb-8 text-center">
          <div class="inline-flex items-center justify-center w-14 h-14 mb-4">
            <img src="/favicon.svg" alt="Grupo Enriquecedor" class="w-14 h-14 object-contain" />
          </div>
          <h1 class="text-white text-xl font-semibold tracking-tight">Onboarding</h1>
          <h4 class="text-white text-md">Grupo Enriquecedor</h4>
          <p class="text-neutral-400 text-sm mt-1">Entre com sua conta</p>
        </div>

        <!-- Form -->
        <form class="space-y-4" @submit.prevent="handleLogin">
          <!-- Email -->
          <div class="space-y-1.5">
            <label class="text-neutral-300 text-sm font-medium">E-mail</label>
            <input
              v-model="form.email"
              type="email"
              autocomplete="email"
              placeholder="voce@empresa.com"
              required
              class="w-full bg-white/5 border border-white/10 rounded-lg px-3.5 py-2.5 text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30 transition-colors"
            />
          </div>

          <!-- Senha -->
          <div class="space-y-1.5">
            <label class="text-neutral-300 text-sm font-medium">Senha</label>
            <div class="relative">
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="current-password"
                placeholder="••••••••"
                required
                minlength="6"
                class="w-full bg-white/5 border border-white/10 rounded-lg px-3.5 py-2.5 pr-10 text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30 transition-colors"
              />
              <button
                type="button"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors"
                @click="showPassword = !showPassword"
              >
                <svg v-if="!showPassword" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                  <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                </svg>
                <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                </svg>
              </button>
            </div>
          </div>

          <!-- Erro -->
          <div v-if="error" class="rounded-lg bg-red-500/10 border border-red-500/20 px-3.5 py-2.5">
            <p class="text-red-400 text-sm">{{ error }}</p>
          </div>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full mt-2 bg-white text-neutral-900 font-medium text-sm rounded-full px-4 py-2.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:-translate-y-0.5 active:translate-y-0 transition-transform disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          >
            <span v-if="!loading">Entrar</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              Entrando...
            </span>
          </button>
        </form>

        <!-- Footer -->
        <div class="mt-6 text-center">
          <NuxtLink to="/forgot-password" class="text-neutral-500 text-sm hover:text-neutral-300 transition-colors">
            Esqueceu sua senha?
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { login } = useAuth()

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await login(form.email, form.password)
    await navigateTo('/')
  } catch (e: any) {
    const detail = e?.data?.detail
    if (detail) {
      error.value = typeof detail === 'string' ? detail : 'Credenciais inválidas.'
    } else {
      error.value = 'Erro ao conectar. Tente novamente.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.border-gradient {
  position: relative;
}
.border-gradient::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255,255,255,0.12) 0%, rgba(255,255,255,0.04) 50%, rgba(255,255,255,0.08) 100%);
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}
</style>
