// Temas (presets) do share público de materiais. Fonte única — usada tanto pela
// página pública (pages/share/[token].vue) quanto pelo seletor no editor
// (pages/onboarding/[id]/materials.vue). Aplica SÓ na web (PDF mantém paleta warm).
//
// As keys (warm/midnight/azul/mono) espelham VALID_THEMES no backend (onboarding/api.py).
//
// Mapa hex(antigo) -> token, p/ converter os valores hardcoded da página de share:
//   #f3ede0 --bg | #ffffff --surface | #f9f5ef --s2 | #e2d8c5 --border
//   #1c1917 --text | #5a5048 --dim | #9a9088 --muted
//   #4d7c58 --accent | #3a6a4a --accent2 | #2c3f31 --accent-d
//   #b83030 --red | #edf3fc --blue-bg

const SANS = 'Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif'
const SERIF = 'Georgia, "Times New Roman", Cambria, serif'

export interface ShareTheme {
  key: string
  name: string
  font: string
  swatch: { bg: string; accent: string } // dot do seletor (fundo + acento)
  vars: Record<string, string>            // CSS custom properties aplicadas na raiz
}

export const SHARE_THEMES: Record<string, ShareTheme> = {
  warm: {
    key: 'warm',
    name: 'Clássico',
    font: SANS,
    swatch: { bg: '#f3ede0', accent: '#4d7c58' },
    vars: {
      '--bg': '#f3ede0', '--surface': '#ffffff', '--s2': '#f9f5ef', '--border': '#e2d8c5',
      '--text': '#1c1917', '--dim': '#5a5048', '--muted': '#9a9088',
      '--accent': '#4d7c58', '--accent2': '#3a6a4a', '--accent-d': '#2c3f31',
      '--on-accent': '#f3ede0', '--red': '#b83030', '--blue-bg': '#edf3fc',
    },
  },
  midnight: {
    key: 'midnight',
    name: 'Midnight',
    font: SANS,
    swatch: { bg: '#181b21', accent: '#3f7bd6' },
    vars: {
      '--bg': '#0f1115', '--surface': '#181b21', '--s2': '#1f232b', '--border': '#2c313a',
      '--text': '#e8eaed', '--dim': '#aab0bb', '--muted': '#6b7280',
      '--accent': '#3f7bd6', '--accent2': '#336cc0', '--accent-d': '#12161d',
      '--on-accent': '#eaf1ff', '--red': '#f0686a', '--blue-bg': '#1b2330',
    },
  },
  azul: {
    key: 'azul',
    name: 'Corporativo',
    font: SANS,
    swatch: { bg: '#eef2f8', accent: '#2563eb' },
    vars: {
      '--bg': '#eef2f8', '--surface': '#ffffff', '--s2': '#f5f8fc', '--border': '#d4def0',
      '--text': '#0f1f3a', '--dim': '#44557a', '--muted': '#8895ad',
      '--accent': '#2563eb', '--accent2': '#1e4fc4', '--accent-d': '#0f2a66',
      '--on-accent': '#eaf1ff', '--red': '#c0392b', '--blue-bg': '#e6efff',
    },
  },
  mono: {
    key: 'mono',
    name: 'Editorial',
    font: SERIF,
    swatch: { bg: '#f6f5f3', accent: '#333333' },
    vars: {
      '--bg': '#f6f5f3', '--surface': '#ffffff', '--s2': '#faf9f7', '--border': '#e0ddd6',
      '--text': '#1a1a1a', '--dim': '#555555', '--muted': '#999999',
      '--accent': '#333333', '--accent2': '#1a1a1a', '--accent-d': '#111111',
      '--on-accent': '#ffffff', '--red': '#a33030', '--blue-bg': '#eef0f2',
    },
  },
  oceano: {
    key: 'oceano',
    name: 'Oceano',
    font: SANS,
    swatch: { bg: '#eef5f6', accent: '#0e9aa7' },
    vars: {
      '--bg': '#eef5f6', '--surface': '#ffffff', '--s2': '#f5fafb', '--border': '#cfe3e6',
      '--text': '#0e2a2e', '--dim': '#3f5a5e', '--muted': '#88a3a6',
      '--accent': '#0e9aa7', '--accent2': '#0b7d88', '--accent-d': '#0a3b40',
      '--on-accent': '#effbfc', '--red': '#c0392b', '--blue-bg': '#e6f2fb',
    },
  },
  bordo: {
    key: 'bordo',
    name: 'Bordô',
    font: SERIF,
    swatch: { bg: '#f6f1ef', accent: '#8c2f39' },
    vars: {
      '--bg': '#f6f1ef', '--surface': '#ffffff', '--s2': '#faf5f3', '--border': '#e6d8d3',
      '--text': '#2a1416', '--dim': '#5e4a48', '--muted': '#9a8884',
      '--accent': '#8c2f39', '--accent2': '#6f242c', '--accent-d': '#3a1418',
      '--on-accent': '#f8ece9', '--red': '#b83030', '--blue-bg': '#efe8f0',
    },
  },
  roxo: {
    key: 'roxo',
    name: 'Violeta',
    font: SANS,
    swatch: { bg: '#f3f0fa', accent: '#6d4ad6' },
    vars: {
      '--bg': '#f3f0fa', '--surface': '#ffffff', '--s2': '#f8f6fd', '--border': '#ddd5f0',
      '--text': '#1f1340', '--dim': '#4a3f6a', '--muted': '#8b82a8',
      '--accent': '#6d4ad6', '--accent2': '#5638b4', '--accent-d': '#2c1f5e',
      '--on-accent': '#f1ecff', '--red': '#c0392b', '--blue-bg': '#ebe6fb',
    },
  },
  dourado: {
    key: 'dourado',
    name: 'Dourado',
    font: SANS,
    swatch: { bg: '#1e1c16', accent: '#c9a24b' },
    vars: {
      '--bg': '#14130f', '--surface': '#1e1c16', '--s2': '#26241c', '--border': '#38342a',
      '--text': '#ece7d8', '--dim': '#b8b09a', '--muted': '#7a7363',
      '--accent': '#a87f2c', '--accent2': '#8c6a24', '--accent-d': '#0e0d09',
      '--on-accent': '#f3ead0', '--red': '#e08a6a', '--blue-bg': '#1d2330',
    },
  },
}

export const DEFAULT_THEME = 'warm'

export const SHARE_THEME_LIST: ShareTheme[] = Object.values(SHARE_THEMES)

export function getShareTheme(key?: string | null): ShareTheme {
  return SHARE_THEMES[key ?? DEFAULT_THEME] ?? SHARE_THEMES[DEFAULT_THEME]
}
