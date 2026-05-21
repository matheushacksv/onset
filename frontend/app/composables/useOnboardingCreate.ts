export const useOnboardingCreate = () => {
  const { fetchAuth } = useAuth()

  const createWithDeal = (pipedrive_deal_id: string, pipedrive_deal_name: string) =>
    fetchAuth<{ id: number }>('/api/onboarding/', {
      method: 'POST',
      body: { pipedrive_deal_id, pipedrive_deal_name },
    })

  const createBlankMaterial = (name?: string) =>
    fetchAuth<{ id: number }>('/api/onboarding/blank-material', {
      method: 'POST',
      body: { name },
    })

  const cloneMaterial = (source_material_id: number, name?: string) =>
    fetchAuth<{ id: number }>('/api/onboarding/clone-material', {
      method: 'POST',
      body: { source_material_id, name },
    })

  const attachDeal = (id: number, pipedrive_deal_id: string, pipedrive_deal_name: string) =>
    fetchAuth(`/api/onboarding/${id}/attach-deal`, {
      method: 'POST',
      body: { pipedrive_deal_id, pipedrive_deal_name },
    })

  return { createWithDeal, createBlankMaterial, cloneMaterial, attachDeal }
}
