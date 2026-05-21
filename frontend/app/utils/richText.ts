// Converte markdown simples em HTML seguro: escapa tudo, depois injeta só anchors.
// Suporta [texto](url) e URLs cruas (http/https). Quebras de linha viram <br>.

const escapeHtml = (s: string): string =>
  s.replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const ANCHOR = 'text-blue-300 underline underline-offset-2 hover:text-blue-200 break-words'

const safeUrl = (url: string): string | null => {
  const u = url.trim()
  return /^https?:\/\//i.test(u) ? u : null
}

export const renderRichText = (input: string): string => {
  if (!input) return ''
  let out = escapeHtml(input)

  // [texto](url) — texto e url já escapados
  out = out.replace(/\[([^\]]+)\]\(([^)\s]+)\)/g, (m, label, url) => {
    const safe = safeUrl(url)
    if (!safe) return m
    return `<a href="${safe}" target="_blank" rel="noopener noreferrer" class="${ANCHOR}">${label}</a>`
  })

  // URLs cruas restantes (não já dentro de href=")
  out = out.replace(/(^|[\s])(https?:\/\/[^\s<]+)/gi, (m, pre, url) => {
    return `${pre}<a href="${url}" target="_blank" rel="noopener noreferrer" class="${ANCHOR}">${url}</a>`
  })

  return out.replace(/\n/g, '<br>')
}
