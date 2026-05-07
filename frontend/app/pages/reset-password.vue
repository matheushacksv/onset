<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/8 rounded-full blur-3xl" />
    </div>

    <div class="relative w-full max-w-sm">
      <div class="border-gradient rounded-2xl bg-white/5 backdrop-blur-xl ring-1 ring-white/10 p-8">

        <!-- Token inválido -->
        <div v-if="!uid || !token" class="text-center space-y-4">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-500/10 ring-1 ring-red-500/20">
            <svg class="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0Zm-9 3.75h.008v.008H12v-.008Z" />
            </svg>
          </div>
          <p class="text-neutral-300 text-sm">Link inválido ou expirado.</p>
          <NuxtLink to="/forgot-password" class="block text-sm text-white/60 hover:text-white/90 transition-colors">
            Solicitar novo link →
          </NuxtLink>
        </div>

        <!-- Sucesso -->
        <div v-else-if="success" class="text-center space-y-4">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/10 ring-1 ring-green-500/20">
            <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
          </div>
          <p class="text-neutral-300 text-sm">Senha redefinida com sucesso.</p>
          <NuxtLink to="/login" class="block text-sm text-white/60 hover:text-white/90 transition-colors">
            ← Fazer login
          </NuxtLink>
        </div>

        <!-- Form -->
        <template v-else>
          <div class="mb-8 text-center">
            <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/10 ring-1 ring-white/20 mb-4">
              <svg class="w-5 h-5 text-white/80" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
              </svg>
            </div>
            <h1 class="text-white text-xl font-semibold tracking-tight">Nova senha</h1>
            <p class="text-neutral-400 text-sm mt-1">Escolha uma senha segura</p>
          </div>

          <form class="space-y-4" @submit.prevent="handleSubmit">
            <div class="space-y-1.5">
              <label class="text-neutral-300 text-sm font-medium">Nova senha</label>
              <div class="relative">
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="••••••••"
                  required
                  minlength="6"
                  class="w-full bg-white/5 border border-white/10 rounded-lg px-3.5 py-2.5 pr-10 text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30 transition-colors"
                />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors" @click="showPassword = !showPassword">
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

            <div class="space-y-1.5">
              <label class="text-neutral-300 text-sm font-medium">Confirmar senha</label>
              <div class="relative">
                <input
                  v-model="form.confirm"
                  :type="showConfirm ? 'text' : 'password'"
                  autocomplete="new-password"
                  placeholder="••••••••"
                  required
                  minlength="6"
                  class="w-full bg-white/5 border border-white/10 rounded-lg px-3.5 py-2.5 pr-10 text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30 transition-colors"
                />
                <button type="button" class="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-500 hover:text-neutral-300 transition-colors" @click="showConfirm = !showConfirm">
                  <svg v-if="!showConfirm" class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                  </svg>
                  <svg v-else class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 0 0 1.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.451 10.451 0 0 1 12 4.5c4.756 0 8.773 3.162 10.065 7.498a10.522 10.522 0 0 1-4.293 5.774M6.228 6.228 3 3m3.228 3.228 3.65 3.65m7.894 7.894L21 21m-3.228-3.228-3.65-3.65m0 0a3 3 0 1 0-4.243-4.243m4.242 4.242L9.88 9.88" />
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="error" class="rounded-lg bg-red-500/10 border border-red-500/20 px-3.5 py-2.5">
              <p class="text-red-400 text-sm">{{ error }}</p>
            </div>

            <button
              type="submit"
              :disabled="loading"
              class="w-full mt-2 bg-white text-neutral-900 font-medium text-sm rounded-full px-4 py-2.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:-translate-y-0.5 active:translate-y-0 transition-transform disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
            >
              <span v-if="!loading">Redefinir senha</span>
              <span v-else class="flex items-center justify-center gap-2">
                <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                </svg>
                Salvando...
              </span>
            </button>
          </form>
        </template>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const route = useRoute()
const uid = route.query.uid as string | undefined
const token = route.query.token as string | undefined

const form = reactive({ password: '', confirm: '' })
const loading = ref(false)
const error = ref('')
const success = ref(false)
const showPassword = ref(false)
const showConfirm = ref(false)

const handleSubmit = async () => {
  if (form.password !== form.confirm) {
    error.value = 'As senhas não coincidem.'
    return
  }
  error.value = ''
  loading.value = true
  try {
    await $fetch('/api/auth/reset-password', {
      method: 'POST',
      body: { uid, token, password: form.password },
    })
    success.value = true
  } catch (e: any) {
    error.value = e?.data?.detail ?? 'Token inválido ou expirado.'
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
