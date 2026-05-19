import type { CRMScript, ClosingMaterial, QualificationScript } from '~/composables/useOnboarding'

export interface SharedMaterial {
  deal_name: string
  assessor_name: string | null
  generated_at: string
  crm?: CRMScript
  closing?: ClosingMaterial
  qualification?: QualificationScript
  grant?: string | null
}

export type ShareView = 'loading' | 'password' | 'ready' | 'expired' | 'notfound' | 'error'

export function useSharedMaterial(token: string) {
  const view = ref<ShareView>('loading')
  const material = ref<SharedMaterial | null>(null)
  const dealName = ref('')
  const unlocking = ref(false)
  const unlockError = ref('')

  const base = `/api/onboarding/share/${encodeURIComponent(token)}`

  function handleError(e: any) {
    const status = e?.status ?? e?.statusCode ?? e?.response?.status
    if (status === 401) {
      dealName.value = e?.data?.deal_name || ''
      view.value = 'password'
    } else if (status === 410) {
      view.value = 'expired'
    } else if (status === 404) {
      view.value = 'notfound'
    } else {
      view.value = 'error'
    }
  }

  async function load() {
    view.value = 'loading'
    try {
      const data = await $fetch<SharedMaterial>(base)
      material.value = data
      dealName.value = data.deal_name
      view.value = 'ready'
    } catch (e) {
      handleError(e)
    }
  }

  async function unlock(password: string) {
    if (unlocking.value) return
    unlocking.value = true
    unlockError.value = ''
    try {
      const data = await $fetch<SharedMaterial>(`${base}/unlock`, {
        method: 'POST',
        body: { password },
      })
      material.value = data
      dealName.value = data.deal_name
      view.value = 'ready'
    } catch (e: any) {
      const status = e?.status ?? e?.statusCode ?? e?.response?.status
      if (status === 403) unlockError.value = 'Senha incorreta.'
      else if (status === 410) view.value = 'expired'
      else unlockError.value = 'Erro ao validar a senha.'
    } finally {
      unlocking.value = false
    }
  }

  function pdfUrl(kind: 'master' | 'crm' | 'closing' | 'qualification' = 'master') {
    const g = material.value?.grant
    return `${base}/pdf/${kind}` + (g ? `?grant=${encodeURIComponent(g)}` : '')
  }

  return { view, material, dealName, unlocking, unlockError, load, unlock, pdfUrl }
}
