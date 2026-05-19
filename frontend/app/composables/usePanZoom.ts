// Pan + zoom genérico via pointer events. Aplica transform translate/scale.
export function usePanZoom(opts: { min?: number; max?: number; initial?: number } = {}) {
  const min = opts.min ?? 0.4
  const max = opts.max ?? 1.6
  const scale = ref(opts.initial ?? 0.8)
  const x = ref(0)
  const y = ref(0)

  const dragging = ref(false)
  let startX = 0, startY = 0, origX = 0, origY = 0

  const transform = computed(() => `translate(${x.value}px, ${y.value}px) scale(${scale.value})`)

  function onPointerDown(e: PointerEvent) {
    // ignora se clicou em elemento interativo (botão, link, input)
    const el = e.target as HTMLElement
    if (el.closest('button, a, input, select, textarea')) return
    dragging.value = true
    startX = e.clientX; startY = e.clientY
    origX = x.value; origY = y.value
    ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
  }

  function onPointerMove(e: PointerEvent) {
    if (!dragging.value) return
    x.value = origX + (e.clientX - startX)
    y.value = origY + (e.clientY - startY)
  }

  function onPointerUp() {
    dragging.value = false
  }

  function zoom(delta: number) {
    scale.value = Math.min(max, Math.max(min, +(scale.value + delta).toFixed(2)))
  }

  function reset() {
    scale.value = opts.initial ?? 0.8
    x.value = 0
    y.value = 0
  }

  return { scale, x, y, transform, dragging, onPointerDown, onPointerMove, onPointerUp, zoom, reset }
}
