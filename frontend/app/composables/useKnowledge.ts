export interface KnowledgeItem {
  name: string
  size: number
  updated_at: string | null
  indexed: boolean
}

export interface KnowledgeContent {
  name: string
  content: string
}

export const useKnowledge = () => {
  const { fetchAuth } = useAuth()

  const list = (): Promise<KnowledgeItem[]> =>
    fetchAuth<KnowledgeItem[]>('/api/knowledge/')

  const view = (name: string): Promise<KnowledgeContent> =>
    fetchAuth<KnowledgeContent>(`/api/knowledge/content?name=${encodeURIComponent(name)}`)

  const upload = (file: File): Promise<KnowledgeItem> => {
    const fd = new FormData()
    fd.append('file', file)
    return fetchAuth<KnowledgeItem>('/api/knowledge/upload', { method: 'POST', body: fd })
  }

  const remove = (name: string): Promise<{ detail: string }> =>
    fetchAuth<{ detail: string }>(`/api/knowledge/?name=${encodeURIComponent(name)}`, { method: 'DELETE' })

  const index = (name: string): Promise<KnowledgeItem> =>
    fetchAuth<KnowledgeItem>(`/api/knowledge/index?name=${encodeURIComponent(name)}`, { method: 'POST' })

  const indexBulk = (names: string[]): Promise<{ queued: number }> =>
    fetchAuth<{ queued: number }>('/api/knowledge/index-bulk', { method: 'POST', body: { names } })

  const unindex = (names: string[]): Promise<{ unindexed: number }> =>
    fetchAuth<{ unindexed: number }>('/api/knowledge/unindex', { method: 'POST', body: { names } })

  const download = async (name: string): Promise<void> => {
    const blob = await fetchAuth<Blob>(
      `/api/knowledge/download?name=${encodeURIComponent(name)}`,
      { responseType: 'blob' },
    )
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    document.body.appendChild(a)
    a.click()
    a.remove()
    URL.revokeObjectURL(url)
  }

  return { list, view, upload, remove, download, index, indexBulk, unindex }
}
