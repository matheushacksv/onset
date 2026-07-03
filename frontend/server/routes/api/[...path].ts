export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  // Sem override de `host`: proxyRequest já encaminha o Host original (que está no
  // ALLOWED_HOSTS). Injetar um 2º host aqui gerava Host duplicado/inválido sob
  // concorrência (reuso de conexão undici) → Django respondia 400 DisallowedHost
  // intermitente, sumindo dados do dashboard.
  return proxyRequest(event, `${config.internalBackendUrl}${event.path}`)
})
