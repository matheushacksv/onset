import type { CRMScript, MaterialLibraryItem } from '~/composables/useOnboarding'

export interface DevMaterialDetail {
  id: number
  pipedrive_deal_name: string
  assessor_name: string | null
  updated_at: string
  crm: CRMScript | null
}

export const useDevMaterials = () => {
  const { fetchAuth } = useAuth()

  const list = async (): Promise<MaterialLibraryItem[]> => {
    const items = await fetchAuth<MaterialLibraryItem[]>('/api/onboarding/dev/materials')
    return items.map(it => ({ ...it, pipedrive_deal_name: cleanDealName(it.pipedrive_deal_name) }))
  }

  const get = async (onboardingId: string | number): Promise<DevMaterialDetail> => {
    const data = await fetchAuth<DevMaterialDetail>(`/api/onboarding/dev/materials/${onboardingId}`)
    return { ...data, pipedrive_deal_name: cleanDealName(data.pipedrive_deal_name) }
  }

  return { list, get }
}
