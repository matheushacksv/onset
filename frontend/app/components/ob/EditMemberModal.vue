<script setup lang="ts">
interface Member {
  id: number
  name: string | null
  email: string
  avatar: string | null
  is_staff?: boolean
  is_active?: boolean
  role: string[]
}

const props = defineProps<{
  open: boolean
  member: Member | null
  loadRoles: () => Promise<string[]>
}>()

const emit = defineEmits<{
  close: []
  saved: [member: Member]
}>()

const { fetchAuth } = useAuth()

const form = reactive({
  is_active: true,
  is_staff: false,
  role: [] as string[],
})

const availableRoles = ref<string[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

watch(() => props.open, async (v) => {
  if (!v || !props.member) return
  form.is_active = props.member.is_active ?? true
  form.is_staff = props.member.is_staff ?? false
  form.role = [...(props.member.role || [])]
  error.value = null
  if (!availableRoles.value.length) {
    try {
      availableRoles.value = await props.loadRoles()
    } catch {}
  }
})

function toggleRole(r: string) {
  const i = form.role.indexOf(r)
  if (i >= 0) form.role.splice(i, 1)
  else form.role.push(r)
}

async function save() {
  if (!props.member) return
  loading.value = true
  error.value = null
  try {
    const updated = await fetchAuth<Member>(`/api/auth/${props.member.id}`, {
      method: 'PATCH',
      body: {
        is_active: form.is_active,
        is_staff: form.is_staff,
        role: form.role,
      },
    })
    emit('saved', updated)
    emit('close')
  } catch (err: any) {
    error.value = err?.data?.detail || err?.message || 'Erro ao salvar'
  } finally {
    loading.value = false
  }
}

function handleEsc(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

watch(() => props.open, (v) => {
  if (v) document.addEventListener('keydown', handleEsc)
  else document.removeEventListener('keydown', handleEsc)
})

onUnmounted(() => document.removeEventListener('keydown', handleEsc))
</script>

<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-150"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="open && member"
        class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
        @click.self="emit('close')"
      >
        <div class="bg-white dark:bg-neutral-900 ring-1 ring-neutral-200 dark:ring-white/10 rounded-2xl w-full max-w-md overflow-hidden shadow-2xl">

          <div class="px-6 py-5 border-b border-neutral-200 dark:border-white/[0.06]">
            <h2 class="text-base font-semibold text-neutral-900 dark:text-white">Editar membro</h2>
            <p class="text-xs text-neutral-500 dark:text-white/40 mt-0.5 truncate">{{ member.name || member.email }}</p>
          </div>

          <div class="p-5 space-y-4">

            <label class="flex items-start gap-3 bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-3 cursor-pointer">
              <input v-model="form.is_active" type="checkbox" class="mt-0.5 w-4 h-4" />
              <div class="flex-1">
                <p class="text-sm font-medium text-neutral-900 dark:text-white">Conta ativa</p>
                <p class="text-xs text-neutral-500 dark:text-white/40 mt-0.5">Desmarque para desativar acesso</p>
              </div>
            </label>

            <label class="flex items-start gap-3 bg-neutral-50 dark:bg-white/5 ring-1 ring-neutral-200 dark:ring-white/10 rounded-xl px-4 py-3 cursor-pointer">
              <input v-model="form.is_staff" type="checkbox" class="mt-0.5 w-4 h-4" />
              <div class="flex-1">
                <p class="text-sm font-medium text-neutral-900 dark:text-white">Acesso de admin</p>
                <p class="text-xs text-neutral-500 dark:text-white/40 mt-0.5">Pode editar outros membros</p>
              </div>
            </label>

            <div>
              <p class="text-xs font-medium text-neutral-600 dark:text-white/60 uppercase tracking-widest mb-2">Funções</p>
              <div class="flex flex-wrap gap-1.5">
                <button
                  v-for="r in availableRoles"
                  :key="r"
                  type="button"
                  class="text-xs px-3 py-1.5 rounded-full transition-colors ring-1"
                  :class="form.role.includes(r)
                    ? 'bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 ring-neutral-900 dark:ring-white'
                    : 'bg-neutral-100 dark:bg-white/5 text-neutral-700 dark:text-white/70 ring-neutral-200 dark:ring-white/10 hover:bg-neutral-200 dark:hover:bg-white/10'"
                  @click="toggleRole(r)"
                >
                  {{ r }}
                </button>
                <span v-if="!availableRoles.length" class="text-xs text-neutral-500 dark:text-white/40">Nenhuma função disponível</span>
              </div>
            </div>

            <div v-if="error" class="bg-red-500/10 ring-1 ring-red-400/30 rounded-xl px-4 py-3 text-sm text-red-500 dark:text-red-300">
              {{ error }}
            </div>
          </div>

          <div class="px-5 py-4 border-t border-neutral-200 dark:border-white/[0.06] flex justify-end gap-3">
            <button
              type="button"
              class="px-4 py-2 text-sm text-neutral-600 dark:text-white/60 hover:text-neutral-900 dark:hover:text-white transition-colors"
              @click="emit('close')"
            >
              Cancelar
            </button>
            <button
              type="button"
              :disabled="loading"
              class="bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 text-sm font-medium px-5 py-2 rounded-full hover:bg-neutral-800 dark:hover:bg-white/90 disabled:opacity-40 transition-colors"
              @click="save"
            >
              {{ loading ? 'Salvando...' : 'Salvar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>
