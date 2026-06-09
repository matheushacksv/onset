<template>
  <button
    v-if="!unsupported"
    class="shrink-0 w-7 h-7 flex items-center justify-center rounded-full transition-all text-sm relative"
    :class="btnClass"
    :title="tooltip"
    @click="toggle"
  >
    <svg v-if="state === 'transcribing'" class="w-3.5 h-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
    </svg>
    <svg v-else-if="state === 'recording_speech' || state === 'recording_whisper'" class="w-3.5 h-3.5 animate-pulse" viewBox="0 0 24 24" fill="currentColor">
      <rect x="6" y="4" width="4" height="16" rx="1" />
      <rect x="14" y="4" width="4" height="16" rx="1" />
    </svg>
    <svg v-else class="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
      <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
      <line x1="12" y1="19" x2="12" y2="23" />
      <line x1="8" y1="23" x2="16" y2="23" />
    </svg>
  </button>
</template>

<script setup lang="ts">
const props = defineProps<{ modelValue: string }>()
const emit = defineEmits<{ 'update:modelValue': [value: string] }>()
const { fetchAuth } = useAuth()

type State = 'idle' | 'recording_speech' | 'recording_whisper' | 'transcribing'
const state = ref<State>('idle')
const unsupported = ref(false)
const errorMsg = ref('')

let recognition: any = null
let finalized = ''
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []

const btnClass = computed(() => {
  if (state.value === 'transcribing') return 'bg-white/10 text-white/60'
  if (state.value === 'recording_speech' || state.value === 'recording_whisper') return 'bg-red-500 text-white shadow-lg shadow-red-500/30 scale-110'
  if (errorMsg.value) return 'text-amber-400/70 hover:bg-white/5'
  return 'text-white/30 hover:text-white/60 hover:bg-white/5'
})

const tooltip = computed(() => {
  if (errorMsg.value) return errorMsg.value
  if (state.value === 'recording_speech') return 'Gravando (voz para texto) — clique para parar'
  if (state.value === 'recording_whisper') return 'Gravando áudio — clique para transcrever'
  if (state.value === 'transcribing') return 'Transcrevendo áudio...'
  return 'Gravar áudio (voz para texto)'
})

// ── Web Speech API ────────────────────────────────────────────

const startSpeech = () => {
  const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
  if (!SpeechRecognition) return false

  finalized = props.modelValue || ''
  recognition = new SpeechRecognition()
  recognition.lang = 'pt-BR'
  recognition.continuous = true
  recognition.interimResults = true
  recognition.maxAlternatives = 1

  recognition.onresult = (e: any) => {
    let interim = ''
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const r = e.results[i]
      if (r.isFinal) {
        finalized += (finalized ? ' ' : '') + r[0].transcript
      } else {
        interim = r[0].transcript
      }
    }
    emit('update:modelValue', (finalized + (interim ? ' ' + interim : '')).trim())
  }

  recognition.onerror = (e: any) => {
    if (e.error === 'network') {
      // Speech blocked (Vivaldi/HTTP) → fallback Whisper
      startWhisper()
    } else if (e.error === 'not-allowed') {
      errorMsg.value = 'Microfone bloqueado'
      state.value = 'idle'
    } else if (e.error === 'no-speech') {
      state.value = 'idle'
    } else {
      console.warn('[MicButton] Speech error:', e.error)
      state.value = 'idle'
    }
  }

  recognition.onend = () => {
    if (state.value === 'recording_speech') state.value = 'idle'
  }

  try {
    recognition.start()
    state.value = 'recording_speech'
    errorMsg.value = ''
    return true
  } catch (err: any) {
    if (err.name === 'InvalidStateError' || err.message?.includes('insecure')) {
      startWhisper()
      return true
    }
    return false
  }
}

const stopSpeech = () => {
  recognition?.stop()
  state.value = 'idle'
}

// ── Whisper (MediaRecorder) ───────────────────────────────────

const startWhisper = () => {
  if (!navigator.mediaDevices?.getUserMedia) {
    errorMsg.value = 'Gravação de áudio não suportada'
    state.value = 'idle'
    return
  }

  audioChunks = []
  state.value = 'recording_whisper'
  errorMsg.value = ''
  navigator.mediaDevices.getUserMedia({ audio: true }).then((stream) => {
    mediaRecorder = new MediaRecorder(stream)
    mediaRecorder.ondataavailable = (e) => { audioChunks.push(e.data) }
    mediaRecorder.onstop = () => {
      stream.getTracks().forEach(t => t.stop())
      uploadAudio()
    }
    mediaRecorder.start()
  }).catch((err) => {
    console.warn('[MicButton] getUserMedia error:', err)
    errorMsg.value = err.name === 'NotAllowedError' ? 'Microfone bloqueado' : 'Erro ao acessar microfone'
    state.value = 'idle'
  })
}

const stopWhisper = () => {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
    state.value = 'transcribing'
  } else {
    state.value = 'idle'
  }
}

const uploadAudio = async () => {
  if (audioChunks.length === 0) { state.value = 'idle'; return }
  const blob = new Blob(audioChunks, { type: 'audio/webm' })
  const formData = new FormData()
  formData.append('file', blob, 'audio.webm')

  try {
    const data = await fetchAuth<{ text: string }>('/api/onboarding/transcribe-audio', {
      method: 'POST',
      body: formData,
    })
    emit('update:modelValue', data.text)
  } catch (err: any) {
    console.warn('[MicButton] Whisper error:', err)
    errorMsg.value = err?.data?.detail || 'Erro ao transcrever áudio'
  } finally {
    state.value = 'idle'
  }
}

// ── Toggle ────────────────────────────────────────────────────

const toggle = () => {
  if (state.value === 'idle') {
    errorMsg.value = ''
    if (!startSpeech()) {
      startWhisper()
    }
  } else if (state.value === 'recording_speech') {
    stopSpeech()
  } else if (state.value === 'recording_whisper') {
    stopWhisper()
  }
}
</script>
