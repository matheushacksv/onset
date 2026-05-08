export default defineNuxtConfig({
  runtimeConfig: {
    internalBackendUrl: 'http://localhost:8000',
    public: {
      backendUrl: process.env.NUXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
    },
  },
  compatibilityDate: '2025-07-15',
  devtools: { enabled: process.env.NODE_ENV !== 'production' },
  modules: ['@nuxt/ui', '@pinia/nuxt'],
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      title: 'Onset — Plataforma',
      titleTemplate: '%s · Onset',
      link: [
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
      ],
      meta: [
        { name: 'description', content: 'Plataforma interna Onset' },
      ],
    },
  },
  colorMode: {
    preference: 'dark',
  },
})
