export interface Rule {
  id: number
  name: string
  content: string
  active: boolean
  order: number
}

export interface RuleWithAck {
  id: number
  name: string
  content: string
  checked: boolean
}

export interface RuleInput {
  name: string
  content: string
  active: boolean
  order: number
}

export const useRules = () => {
  const { fetchAuth } = useAuth()

  // ── Admin CRUD ──
  const listRules = () =>
    fetchAuth<Rule[]>('/api/onboarding/list-rules')

  const createRule = (body: RuleInput) =>
    fetchAuth<Rule>('/api/onboarding/rules', { method: 'POST', body })

  const updateRule = (id: number, body: RuleInput) =>
    fetchAuth<Rule>(`/api/onboarding/rules/${id}`, { method: 'PUT', body })

  const deleteRule = (id: number) =>
    fetchAuth(`/api/onboarding/rules/${id}`, { method: 'DELETE' })

  // ── Onboarding view ──
  const loadOnboardingRules = (onboardingId: number | string) =>
    fetchAuth<RuleWithAck[]>(`/api/onboarding/${onboardingId}/rules`)

  const toggleAck = (onboardingId: number | string, ruleId: number) =>
    fetchAuth<{ checked: boolean }>(`/api/onboarding/${onboardingId}/rules/${ruleId}`, { method: 'POST' })

  return { listRules, createRule, updateRule, deleteRule, loadOnboardingRules, toggleAck }
}
