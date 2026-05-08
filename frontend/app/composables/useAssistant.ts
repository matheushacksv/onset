import type { Ref } from 'vue'
import type { MaterialOut } from '~/composables/useOnboarding'

export type AssistantSection = 'crm' | 'closing' | 'qualification'

export interface AssistantFocus {
  funnel_key?: string | null
  stage_idx?: number | null
  day?: number | null
}

export interface AssistantChatMsg {
  role: 'user' | 'assistant'
  content: string
  changes?: string[]
}

interface AssistantResponse {
  message: string
  section: AssistantSection
  value: any
  changes: string[]
}

interface UndoEntry {
  section: AssistantSection
  snapshot: any
  msgIndex: number
}

export const useAssistant = (
  onboardingId: string | number,
  materialRef: Ref<MaterialOut | null>,
) => {
  const { fetchAuth } = useAuth()

  const history = ref<AssistantChatMsg[]>([])
  const sending = ref(false)
  const undoStack = ref<UndoEntry[]>([])

  const send = async (
    message: string,
    section: AssistantSection,
    focus: AssistantFocus = {},
  ) => {
    const trimmed = message.trim()
    if (!trimmed || sending.value) return
    if (!materialRef.value) return

    sending.value = true
    history.value.push({ role: 'user', content: trimmed })

    const sectionKey = section
    const snapshot = JSON.parse(JSON.stringify(materialRef.value[sectionKey] ?? null))

    try {
      const res = await fetchAuth<AssistantResponse>(
        `/api/onboarding/${onboardingId}/materials/assist`,
        {
          method: 'POST',
          body: {
            section,
            message: trimmed,
            focus,
            history: history.value
              .slice(0, -1)
              .slice(-10)
              .map(m => ({ role: m.role, content: m.content })),
          },
        },
      )

      if (materialRef.value) {
        ;(materialRef.value as any)[sectionKey] = res.value
      }

      const msg: AssistantChatMsg = {
        role: 'assistant',
        content: res.message || (res.changes?.length ? 'Aplicado.' : 'Sem alterações.'),
        changes: res.changes || [],
      }
      history.value.push(msg)

      if (res.changes && res.changes.length) {
        undoStack.value.push({
          section: sectionKey,
          snapshot,
          msgIndex: history.value.length - 1,
        })
      }
    } catch (err: any) {
      const detail = err?.data?.detail || err?.message || 'Erro ao chamar assistente'
      history.value.push({ role: 'assistant', content: `⚠️ ${detail}` })
    } finally {
      sending.value = false
    }
  }

  const undoLast = async () => {
    const last = undoStack.value.pop()
    if (!last || !materialRef.value) return
    ;(materialRef.value as any)[last.section] = last.snapshot
    try {
      await fetchAuth(`/api/onboarding/${onboardingId}/materials`, {
        method: 'PATCH',
        body: { [last.section]: last.snapshot },
      })
    } catch { /* watcher do editor vai reenviar PATCH em breve */ }
    history.value.push({ role: 'assistant', content: '↩️ Última mudança desfeita.' })
  }

  const canUndoMessage = (idx: number) =>
    undoStack.value.length > 0 && undoStack.value[undoStack.value.length - 1]?.msgIndex === idx

  const reset = () => {
    history.value = []
    undoStack.value = []
  }

  return { history, sending, send, undoLast, canUndoMessage, reset }
}
