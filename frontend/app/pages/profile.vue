<template>
  <div class="p-8 max-w-2xl mx-auto space-y-6">
    <h1 class="text-neutral-900 dark:text-white text-xl font-semibold">Perfil</h1>

    <!-- Avatar -->
    <div class="bg-black/[0.02] dark:bg-white/5 ring-1 ring-black/10 dark:ring-white/10 rounded-2xl p-6">
      <div class="flex items-center gap-5">
        <button
          class="relative w-20 h-20 rounded-full ring-2 ring-black/10 dark:ring-white/10 overflow-hidden hover:ring-black/25 dark:hover:ring-white/30 transition-all group cursor-pointer flex-shrink-0"
          @click="triggerAvatarUpload"
          :disabled="uploadingAvatar"
        >
          <img v-if="previewUrl || user?.avatar" :src="previewUrl || user?.avatar || ''" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full bg-black/[0.04] dark:bg-white/5 flex items-center justify-center">
            <span class="text-neutral-400 dark:text-white/40 text-2xl font-medium">
              {{ user?.name?.[0]?.toUpperCase() || '?' }}
            </span>
          </div>
          <div class="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.75">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z" />
            </svg>
          </div>
        </button>

        <div>
          <p class="text-neutral-900 dark:text-white text-sm font-medium">Foto de perfil</p>
          <p class="text-neutral-400 dark:text-white/40 text-xs mt-0.5">JPG, PNG ou WEBP. Máx 5 MB.</p>
          <button
            class="mt-2 text-xs text-neutral-400 dark:text-white/40 hover:text-neutral-900 dark:hover:text-white transition-colors"
            @click="triggerAvatarUpload"
            :disabled="uploadingAvatar"
          >
            {{ uploadingAvatar ? 'Enviando...' : 'Alterar foto' }}
          </button>
          <p v-if="avatarError" class="mt-1 text-red-500 text-xs">{{ avatarError }}</p>
        </div>
      </div>
      <input ref="fileInput" type="file" accept="image/jpeg,image/png,image/webp" class="hidden" @change="handleAvatarChange" />
    </div>

    <!-- Informações -->
    <div class="bg-black/[0.02] dark:bg-white/5 ring-1 ring-black/10 dark:ring-white/10 rounded-2xl p-6 space-y-4">
      <h2 class="text-neutral-900 dark:text-white text-sm font-medium">Informações</h2>
      <div class="space-y-3">
        <div>
          <label class="text-neutral-400 dark:text-white/40 text-xs block mb-1">Nome</label>
          <input
            v-model="nameForm.name"
            type="text"
            placeholder="Seu nome"
            class="w-full bg-black/[0.02] dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl px-3 py-2 text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-black/30 dark:focus:border-white/30 transition-colors"
          />
        </div>
        <div>
          <label class="text-neutral-400 dark:text-white/40 text-xs block mb-1">Email</label>
          <input
            :value="user?.email"
            type="email"
            disabled
            class="w-full bg-black/[0.01] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 rounded-xl px-3 py-2 text-neutral-400 dark:text-white/30 text-sm cursor-not-allowed"
          />
        </div>
      </div>
      <div class="flex items-center gap-3 pt-1">
        <button
          @click="saveName"
          :disabled="savingName"
          class="bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 text-sm font-medium px-4 py-2 rounded-full hover:bg-neutral-700 dark:hover:bg-white/90 transition-colors disabled:opacity-50"
        >
          {{ savingName ? 'Salvando...' : 'Salvar' }}
        </button>
        <p v-if="nameSuccess" class="text-green-500 text-xs">Salvo com sucesso.</p>
        <p v-if="nameError" class="text-red-500 text-xs">{{ nameError }}</p>
      </div>
    </div>

    <!-- Segurança -->
    <div class="bg-black/[0.02] dark:bg-white/5 ring-1 ring-black/10 dark:ring-white/10 rounded-2xl p-6 space-y-4">
      <h2 class="text-neutral-900 dark:text-white text-sm font-medium">Segurança</h2>
      <div class="space-y-3">
        <div>
          <label class="text-neutral-400 dark:text-white/40 text-xs block mb-1">Senha atual</label>
          <input
            v-model="passwordForm.current_password"
            type="password"
            autocomplete="current-password"
            class="w-full bg-black/[0.02] dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl px-3 py-2 text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-black/30 dark:focus:border-white/30 transition-colors"
          />
        </div>
        <div>
          <label class="text-neutral-400 dark:text-white/40 text-xs block mb-1">Nova senha</label>
          <input
            v-model="passwordForm.new_password"
            type="password"
            autocomplete="new-password"
            class="w-full bg-black/[0.02] dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl px-3 py-2 text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-black/30 dark:focus:border-white/30 transition-colors"
          />
        </div>
        <div>
          <label class="text-neutral-400 dark:text-white/40 text-xs block mb-1">Confirmar nova senha</label>
          <input
            v-model="passwordForm.confirm_password"
            type="password"
            autocomplete="new-password"
            class="w-full bg-black/[0.02] dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl px-3 py-2 text-neutral-900 dark:text-white text-sm focus:outline-none focus:border-black/30 dark:focus:border-white/30 transition-colors"
          />
        </div>
      </div>
      <div class="flex items-center gap-3 pt-1">
        <button
          @click="savePassword"
          :disabled="savingPassword"
          class="bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 text-sm font-medium px-4 py-2 rounded-full hover:bg-neutral-700 dark:hover:bg-white/90 transition-colors disabled:opacity-50"
        >
          {{ savingPassword ? 'Salvando...' : 'Alterar senha' }}
        </button>
        <p v-if="passwordSuccess" class="text-green-500 text-xs">Senha alterada.</p>
        <p v-if="passwordError" class="text-red-500 text-xs">{{ passwordError }}</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { user, fetchUser, fetchAuth } = useAuth()

// Avatar
const fileInput = ref<HTMLInputElement | null>(null)
const previewUrl = ref<string | null>(null)
const avatarError = ref('')
const uploadingAvatar = ref(false)

const triggerAvatarUpload = () => fileInput.value?.click()

const handleAvatarChange = async (e: Event) => {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return

  if (file.size > 5 * 1024 * 1024) {
    avatarError.value = 'Arquivo muito grande. Máx 5 MB.'
    return
  }

  previewUrl.value = URL.createObjectURL(file)
  avatarError.value = ''
  uploadingAvatar.value = true

  try {
    const formData = new FormData()
    formData.append('file', file)
    await fetchAuth('/api/auth/me/avatar', { method: 'POST', body: formData })
    await fetchUser()
  } catch (err: any) {
    avatarError.value = err?.data?.detail || 'Erro ao enviar foto.'
    previewUrl.value = null
  } finally {
    uploadingAvatar.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

// Nome
const nameForm = reactive({ name: '' })
const savingName = ref(false)
const nameError = ref('')
const nameSuccess = ref(false)

watch(() => user.value?.name, (val) => {
  if (val !== undefined) nameForm.name = val ?? ''
}, { immediate: true })

const saveName = async () => {
  savingName.value = true
  nameError.value = ''
  nameSuccess.value = false
  try {
    await fetchAuth('/api/auth/me', { method: 'PUT', body: { name: nameForm.name } })
    await fetchUser()
    nameSuccess.value = true
    setTimeout(() => { nameSuccess.value = false }, 3000)
  } catch (err: any) {
    nameError.value = err?.data?.detail || 'Erro ao salvar.'
  } finally {
    savingName.value = false
  }
}

// Senha
const passwordForm = reactive({ current_password: '', new_password: '', confirm_password: '' })
const savingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref(false)

const savePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = false

  if (!passwordForm.current_password || !passwordForm.new_password) {
    passwordError.value = 'Preencha todos os campos.'
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    passwordError.value = 'As senhas não coincidem.'
    return
  }

  savingPassword.value = true
  try {
    await fetchAuth('/api/auth/me', {
      method: 'PUT',
      body: { current_password: passwordForm.current_password, new_password: passwordForm.new_password },
    })
    passwordSuccess.value = true
    passwordForm.current_password = ''
    passwordForm.new_password = ''
    passwordForm.confirm_password = ''
    setTimeout(() => { passwordSuccess.value = false }, 3000)
  } catch (err: any) {
    passwordError.value = err?.data?.detail || 'Erro ao alterar senha.'
  } finally {
    savingPassword.value = false
  }
}
</script>
