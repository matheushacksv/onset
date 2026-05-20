import type { CRMScript, MaterialLibraryItem } from '~/composables/useOnboarding'

export interface DevMaterialDetail {
  id: number
  pipedrive_deal_name: string
  assessor_name: string | null
  updated_at: string
  crm: CRMScript | null
}

export interface MaterialQuery {
  q?: string
  assessorId?: number | null
  sort?: string
  limit?: number
  offset?: number
}

export interface MaterialPage {
  items: MaterialLibraryItem[]
  total: number
}

export interface AssessorOption {
  id: number
  name: string
}

export const useDevMaterials = () => {
  const { fetchAuth } = useAuth()

  const list = async (params: MaterialQuery = {}): Promise<MaterialPage> => {
    const query = new URLSearchParams()
    if (params.q) query.set('q', params.q)
    if (params.assessorId) query.set('assessor_id', String(params.assessorId))
    if (params.sort) query.set('sort', params.sort)
    query.set('limit', String(params.limit ?? 12))
    query.set('offset', String(params.offset ?? 0))
    const page = await fetchAuth<MaterialPage>(`/api/onboarding/dev/materials?${query.toString()}`)
    return {
      ...page,
      items: page.items.map(it => ({ ...it, pipedrive_deal_name: cleanDealName(it.pipedrive_deal_name) })),
    }
  }

  const listAssessors = async (): Promise<AssessorOption[]> =>
    fetchAuth<AssessorOption[]>('/api/onboarding/dev/materials/assessors')

  const get = async (onboardingId: string | number): Promise<DevMaterialDetail> => {
    const data = await fetchAuth<DevMaterialDetail>(`/api/onboarding/dev/materials/${onboardingId}`)
    return { ...data, pipedrive_deal_name: cleanDealName(data.pipedrive_deal_name) }
  }

  return { list, listAssessors, get }
}
