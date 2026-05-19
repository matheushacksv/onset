const PUBLIC_ROUTES = ['/login', '/forgot-password', '/reset-password', '/admin']

export default defineNuxtRouteMiddleware((to) => {
  const { isLoggedIn } = useAuth()

  if (to.path === '/login' && isLoggedIn.value) {
    return navigateTo('/')
  }

  // /share/** é público (link de visualização do cliente)
  if (to.path.startsWith('/share')) return

  if (!PUBLIC_ROUTES.includes(to.path) && !to.path.startsWith('/admin') && !isLoggedIn.value) {
    return navigateTo('/login')
  }
})
