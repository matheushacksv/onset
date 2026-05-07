export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const host = getRequestHost(event)
  return proxyRequest(event, `${config.internalBackendUrl}${event.path}`, {
    headers: { host },
  })
})
