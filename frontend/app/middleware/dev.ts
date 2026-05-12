export default defineNuxtRouteMiddleware(() => {
  const { hasRole, user } = useAuth()
  if (!user.value) return
  if (!hasRole('Desenvolvedor')) return navigateTo('/')
})
