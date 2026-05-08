interface User {
  id: number
  name: string | null
  email: string
  avatar: string | null
  is_superuser: boolean
  is_staff: boolean
  is_active: boolean
  roles: string[]
}

export const useAuth = () => {
  const accessToken = useCookie('access_token', { maxAge: 60 * 60 })
  const refreshToken = useCookie('refresh_token', { maxAge: 60 * 60 * 24 * 7 })
  const user = useState<User | null>('auth:user', () => null)

  const fetchUser = async () => {
    if (!accessToken.value) return
    try {
      user.value = await $fetch<User>('/api/auth/me', {
        headers: { Authorization: `Bearer ${accessToken.value}` },
      })
    } catch {
      user.value = null
    }
  }

  const login = async (email: string, password: string) => {
    const data = await $fetch<{ access: string; refresh: string }>('/api/auth/login', {
      method: 'POST',
      body: { email, password },
    })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    await fetchUser()
  }

  const logout = () => {
    accessToken.value = null
    refreshToken.value = null
    user.value = null
    navigateTo('/login')
  }

  const refreshAccessToken = async (): Promise<boolean> => {
    if (!refreshToken.value) return false
    try {
      const data = await $fetch<{ access: string }>('/api/token/refresh', {
        method: 'POST',
        body: { refresh: refreshToken.value },
      })
      accessToken.value = data.access
      return true
    } catch {
      logout()
      return false
    }
  }

  const fetchAuth = async <T>(url: string, options: Parameters<typeof $fetch>[1] = {}): Promise<T> => {
    const headers = { Authorization: `Bearer ${accessToken.value}`, ...(options.headers as object ?? {}) }
    try {
      return await $fetch<T>(url, { ...options, headers })
    } catch (err: any) {
      if (err?.status === 401) {
        const ok = await refreshAccessToken()
        if (ok) {
          return await $fetch<T>(url, {
            ...options,
            headers: { Authorization: `Bearer ${accessToken.value}`, ...(options.headers as object ?? {}) },
          })
        }
      }
      throw err
    }
  }

  const hasRole = (role: string) => user.value?.is_superuser || user.value?.roles?.includes(role) || false

  const isLoggedIn = computed(() => !!accessToken.value)

  return { login, logout, fetchUser, refreshAccessToken, fetchAuth, isLoggedIn, accessToken, refreshToken, user, hasRole }
}
