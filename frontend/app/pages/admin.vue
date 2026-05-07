<script setup lang="ts">
const config = useRuntimeConfig()

onMounted(() => {
  window.location.href = `${config.public.backendUrl}/admin/`
})
</script>

<template>
  <div class="min-h-full flex items-center justify-center">
    <p class="text-white/40 text-sm">Redirecionando para o admin...</p>
  </div>
</template>
