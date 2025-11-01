import React, { useEffect, useRef, useState } from 'react'
import { Headphones, Loader2, Mic, Play, Send, Volume2, Zap } from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const LiveSandbox = () => {
  const [ttsVoices, setTtsVoices] = useState([])
  const [selectedTtsVoice, setSelectedTtsVoice] = useState('')
  const [ttsText, setTtsText] = useState('Hola! Aquesta és una prova amb VeuPlus.')
  const [ttsLoading, setTtsLoading] = useState(false)
  const [ttsAudioUrl, setTtsAudioUrl] = useState('')

  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [chatInput, setChatInput] = useState('')
  const [chatLoading, setChatLoading] = useState(false)
  const [chatHistory, setChatHistory] = useState([])

  const [micStatus, setMicStatus] = useState('idle') // idle | granted | denied

  const ttsAudioRef = useRef(null)
  const chatAudioRef = useRef(null)

  useEffect(() => {
    const loadData = async () => {
      try {
        const [voicesResponse, agentsResponse] = await Promise.all([
          api.get('/api/edge-tts/voices').catch(() => ({ data: { voices: [] } })),
          api.get('/api/convhi/agents').catch(() => ({ data: { agents: [] } })),
        ])

        const voices = voicesResponse.data.voices || []
        setTtsVoices(voices)
        if (voices.length > 0) {
          setSelectedTtsVoice(voices[0].id || voices[0].voice_id || '')
        }

        const convhiAgents = agentsResponse.data.agents || []
        setAgents(convhiAgents)
        if (convhiAgents.length > 0) {
          setSelectedAgent(convhiAgents[0].id)
        }
      } catch (error) {
        console.error('Error carregant dades del sandbox:', error)
        toast.error('No s’han pogut carregar totes les dades.')
      }
    }
    loadData()
  }, [])

  const handleMicTest = async () => {
    try {
      await navigator.mediaDevices.getUserMedia({ audio: true })
      setMicStatus('granted')
      toast.success('Micròfon detectat correctament!')
    } catch (error) {
      console.error('Mic test error:', error)
      setMicStatus('denied')
      toast.error('No s’ha pogut accedir al micròfon.')
    }
  }

  const handleGenerateTts = async () => {
    if (!ttsText.trim()) {
      toast.error('Introdueix un text per sintetitzar')
      return
    }
    if (!selectedTtsVoice) {
      toast.error('Selecciona una veu Edge-TTS')
      return
    }
    try {
      setTtsLoading(true)
      const response = await api.post('/api/edge-tts/synthesize', {
        text: ttsText,
        voice_id: selectedTtsVoice,
      })
      if (response.data?.audio_base64) {
        const url = `data:${response.data.mime_type || 'audio/mpeg'};base64,${response.data.audio_base64}`
        setTtsAudioUrl(url)
        toast.success('Àudio generat!')
        if (ttsAudioRef.current) {
          ttsAudioRef.current.src = url
          await ttsAudioRef.current.play().catch(() => setTimeout(() => ttsAudioRef.current.play(), 200))
        }
      } else {
        throw new Error('Resposta sense àudio')
      }
    } catch (error) {
      console.error('Error generant àudio:', error)
      toast.error('No s’ha pogut generar l’àudio.')
    } finally {
      setTtsLoading(false)
    }
  }

  const handleSendChat = async () => {
    if (!selectedAgent) {
      toast.error('No hi ha cap agent disponible.')
      return
    }
    if (!chatInput.trim()) {
      toast.error('Introdueix un missatge.')
      return
    }

    const userMessage = {
      id: `user_${Date.now()}`,
      role: 'user',
      text: chatInput,
      timestamp: new Date().toLocaleTimeString(),
    }
    setChatHistory((prev) => [...prev, userMessage])
    setChatInput('')
    setChatLoading(true)

    try {
      const response = await api.post(`/api/convhi/agents/${selectedAgent}/chat`, {
        agent_id: selectedAgent,
        message: userMessage.text,
        message_type: 'text',
      })
      const data = response.data
      const assistantMessage = {
        id: `agent_${Date.now()}`,
        role: 'agent',
        text: data.response || '(Sense resposta textual)',
        timestamp: new Date().toLocaleTimeString(),
        audio: data.audio_base64 ? `data:${data.mime_type || 'audio/mpeg'};base64,${data.audio_base64}` : null,
      }
      setChatHistory((prev) => [...prev, assistantMessage])

      if (assistantMessage.audio && chatAudioRef.current) {
        chatAudioRef.current.src = assistantMessage.audio
        await chatAudioRef.current.play().catch(() => setTimeout(() => chatAudioRef.current.play(), 200))
      }
    } catch (error) {
      console.error('Error enviant missatge:', error)
      toast.error('No s’ha pogut enviar el missatge.')
    } finally {
      setChatLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <Headphones className="w-6 h-6 text-primary-500" />
            Live Sandbox
          </h1>
          <p className="text-sm text-neutral-600">
            Prova ràpida d’àudio i xat sense sortir del navegador. Ideat per validar agents i configuracions.
          </p>
        </div>
        <button onClick={handleMicTest} className="btn-secondary flex items-center gap-2">
          <Mic className="w-4 h-4" />
          {micStatus === 'granted'
            ? 'Micròfon detectat'
            : micStatus === 'denied'
            ? 'Permís rebutjat'
            : 'Test micròfon'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-primary-500" />
              TTS ràpid
            </h2>
            {ttsLoading && <Loader2 className="w-4 h-4 animate-spin text-neutral-400" />}
          </div>
          <textarea
            className="input-field min-h-[120px]"
            value={ttsText}
            onChange={(event) => setTtsText(event.target.value)}
            placeholder="Escriu el text a sintetitzar..."
          />
          <div className="flex items-center gap-3">
            <select
              className="input-field flex-1"
              value={selectedTtsVoice}
              onChange={(event) => setSelectedTtsVoice(event.target.value)}
            >
              {ttsVoices.map((voice) => {
                const id = voice.id || voice.voice_id
                const label = voice.name || voice.DisplayName || id
                return (
                  <option key={id} value={id}>
                    {label}
                  </option>
                )
              })}
            </select>
            <button onClick={handleGenerateTts} className="btn-primary inline-flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Generar
            </button>
          </div>
          {ttsAudioUrl ? (
            <audio ref={ttsAudioRef} controls className="w-full" src={ttsAudioUrl} />
          ) : (
            <p className="text-xs text-neutral-500">Genera un àudio per sentir la prova.</p>
          )}
        </div>

        <div className="card space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
              <Send className="w-5 h-5 text-primary-500" />
              Chat ConvHi
            </h2>
            {chatLoading && <Loader2 className="w-4 h-4 animate-spin text-neutral-400" />}
          </div>
          {agents.length === 0 ? (
            <div className="rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-600">
              No hi ha agents. Crea’n un a <strong>ConvHi &gt; Agents</strong> abans de provar el sandbox.
            </div>
          ) : (
            <>
              <select
                className="input-field"
                value={selectedAgent}
                onChange={(event) => setSelectedAgent(event.target.value)}
              >
                {agents.map((agent) => (
                  <option key={agent.id} value={agent.id}>
                    {agent.name || agent.id}
                  </option>
                ))}
              </select>
              <div className="border border-neutral-200 rounded-lg p-3 h-60 overflow-y-auto space-y-2 bg-neutral-50">
                {chatHistory.length === 0 ? (
                  <p className="text-xs text-neutral-500">Encara cap conversa. Escriu el primer missatge.</p>
                ) : (
                  chatHistory.map((entry) => (
                    <div key={entry.id} className="text-sm">
                      <p
                        className={`font-semibold ${
                          entry.role === 'user' ? 'text-primary-600' : 'text-emerald-600'
                        }`}
                      >
                        {entry.role === 'user' ? 'Tu' : 'Agent'} · {entry.timestamp}
                      </p>
                      <p className="text-neutral-700">{entry.text}</p>
                      {entry.audio && (
                        <audio controls className="mt-1 w-full" src={entry.audio}>
                          El teu navegador no suporta l’àudio.
                        </audio>
                      )}
                    </div>
                  ))
                )}
              </div>
              <div className="flex items-center gap-2">
                <input
                  className="input-field flex-1"
                  placeholder="Escriu un missatge..."
                  value={chatInput}
                  onChange={(event) => setChatInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !event.shiftKey) {
                      event.preventDefault()
                      handleSendChat()
                    }
                  }}
                />
                <button
                  onClick={handleSendChat}
                  className="btn-primary inline-flex items-center gap-2"
                  disabled={chatLoading}
                >
                  {chatLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  Envia
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      <audio ref={chatAudioRef} hidden />
    </div>
  )
}

export default LiveSandbox
