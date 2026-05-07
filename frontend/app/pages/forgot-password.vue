<template>
  <div class="min-h-screen bg-[#0a0a0a] flex items-center justify-center px-4">
    <div class="fixed inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-indigo-500/8 rounded-full blur-3xl" />
    </div>

    <div class="relative w-full max-w-sm">
      <div class="border-gradient rounded-2xl bg-white/5 backdrop-blur-xl ring-1 ring-white/10 p-8">
        <!-- Header -->
        <div class="mb-8 text-center">
          <div class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-white/10 ring-1 ring-white/20 mb-4">
            <svg class="w-5 h-5 text-white/80" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
            </svg>
          </div>
          <h1 class="text-white text-xl font-semibold tracking-tight">Esqueceu sua senha?</h1>
          <p class="text-neutral-400 text-sm mt-1">Enviaremos um link de redefinição</p>
        </div>

        <!-- Success state -->
        <div v-if="sent" class="text-center space-y-4">
          <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-green-500/10 ring-1 ring-green-500/20">
            <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
              <path stroke-linecap="round" stroke-linejoin="round" d="m4.5 12.75 6 6 9-13.5" />
            </svg>
          </div>
          <p class="text-neutral-300 text-sm">Se o e-mail existir em nossa base, você receberá um link em breve.</p>
          <NuxtLink to="/login" class="block text-sm text-white/60 hover:text-white/90 transition-colors mt-2">
            ← Voltar ao login
          </NuxtLink>
        </div>

        <!-- Form -->
        <form v-else class="space-y-4" @submit.prevent="handleSubmit">
          <div class="space-y-1.5">
            <label class="text-neutral-300 text-sm font-medium">E-mail</label>
            <input
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="voce@empresa.com"
              required
              class="w-full bg-white/5 border border-white/10 rounded-lg px-3.5 py-2.5 text-white text-sm placeholder:text-neutral-500 focus:outline-none focus:ring-1 focus:ring-white/30 focus:border-white/30 transition-colors"
            />
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full mt-2 bg-white text-neutral-900 font-medium text-sm rounded-full px-4 py-2.5 shadow-[inset_0_1px_0_rgba(255,255,255,0.15)] hover:-translate-y-0.5 active:translate-y-0 transition-transform disabled:opacity-60 disabled:cursor-not-allowed disabled:hover:translate-y-0"
          >
            <span v-if="!loading">Enviar link</span>
            <span v-else class="flex items-center justify-center gap-2">
              <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
              </svg>
              Enviando...
            </span>
          </button>

          <div class="text-center pt-1">
            <NuxtLink to="/login" class="text-neutral-500 text-sm hover:text-neutral-300 transition-colors">
              ← Voltar ao login
            </NuxtLink>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const email = ref('')
const loading = ref(false)
const sent = ref(false)

const handleSubmit = async () => {
  loading.value = true
  try {
    await $fetch('/api/auth/forgot-password', {
      method: 'POST',
      body: { email: email.value },
    })
    sent.value = true
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
