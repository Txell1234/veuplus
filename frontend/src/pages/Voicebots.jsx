import React, { useState } from 'react'
import { 
  Phone, 
  Plus, 
  MessageSquare, 
  Send, 
  Settings, 
  Trash2, 
  Edit,
  Copy,
  Loader2,
  Sparkles,
  Brain,
  Zap,
  Globe,
  User,
  Mic,
  Volume2,
  Play,
  Pause
} from 'lucide-react'
import { useVoicebot } from '../contexts/VoicebotContext'
import { useVoice } from '../contexts/VoiceContext'
import LLMConfig from '../components/LLMConfig'
import toast from 'react-hot-toast'

const Voicebots = () => {
  const { 
    voicebots, 
    createVoicebot, 
    updateVoicebot, 
    deleteVoicebot, 
    sendVoiceMessage, 
    chatHistory, 
    isGenerating,
    llmProviders,
    setCurrentVoicebot,
    currentVoicebot 
  } = useVoicebot()
  
  const { voices } = useVoice()
  const [allVoices, setAllVoices] = useState([])
  const [availableModels, setAvailableModels] = useState([])
  
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showChatModal, setShowChatModal] = useState(false)
  const [message, setMessage] = useState('')
  const [selectedVoicebot, setSelectedVoicebot] = useState(null)
  const [isRecording, setIsRecording] = useState(false)
  const [audioBlob, setAudioBlob] = useState(null)

  // Carregar totes les veus disponibles
  React.useEffect(() => {
    fetchAllVoices()
  }, [])

  const fetchAllVoices = async () => {
    try {
      const response = await fetch('/api/voices/all')
      if (response.ok) {
        const data = await response.json()
        setAllVoices(data.voices || [])
        console.log('✅ Totes les veus carregades:', data.voices?.length || 0)
      }
    } catch (error) {
      console.error('Error fetching all voices:', error)
    }
  }

  const CreateVoicebotModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      description: '',
      system_prompt: 'Eres un asistente de voz útil y amigable. Responde en catalán.',
      llm_provider: 'openai',
      model: 'gpt-3.5-turbo',
      temperature: 0.7,
      max_tokens: 1000,
      voice_id: '',
      voice_system: 'edge-tts',
      api_key: '',
      api_key_required: false,
      tts_enabled: true,
      asr_enabled: true
    })
    
    const [availableProviders, setAvailableProviders] = useState({})
    
    React.useEffect(() => {
      fetchAvailableProviders()
    }, [])
    
    const fetchAvailableProviders = async () => {
      try {
        const response = await fetch('/api/llm/providers')
        if (response.ok) {
          const data = await response.json()
          setAvailableProviders(data.providers || {})
          console.log('✅ LLM Providers carregats:', Object.keys(data.providers || {}))
        }
      } catch (error) {
        console.error('Error fetching providers:', error)
        // Fallback providers
        setAvailableProviders({
          "openai": {
            "id": "openai",
            "name": "OpenAI",
            "description": "GPT-3.5/4 via API",
            "available": true,
            "api_key_required": true,
            "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"],
            "default_model": "gpt-3.5-turbo"
          },
          "alia": {
            "id": "alia",
            "name": "ALIA Kit (BSC)",
            "description": "Modelos multilingües oficiales ALIA Kit",
            "available": true,
            "api_key_required": false,
            "models": ["BSC-LT/salamandra-7b", "BSC-LT/alia-40b"],
            "default_model": "BSC-LT/salamandra-7b"
          },
          "ollama": {
            "id": "ollama",
            "name": "Ollama",
            "description": "Modelos locales via Ollama",
            "available": true,
            "api_key_required": false,
            "models": ["llama2", "mistral", "codellama"],
            "default_model": "llama2"
          }
        })
      }
    }

    const handleSubmit = async (e) => {
      e.preventDefault()
      try {
        await createVoicebot(formData)
        setShowCreateModal(false)
        setFormData({
          name: '',
          description: '',
          system_prompt: 'Eres un asistente de voz útil y amigable. Responde en catalán.',
          llm_provider: 'openai',
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          voice_id: '',
          voice_system: 'edge-tts',
          api_key: '',
          api_key_required: false,
          tts_enabled: true,
          asr_enabled: true
        })
      } catch (error) {
        console.error('Error creating voicebot:', error)
      }
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Crear Nuevo Voicebot</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Voicebot *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input-field"
                  placeholder="Ej: Asistente de Voz Catalán"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Voz *
                </label>
                <select
                  value={formData.voice_id || ''}
                  onChange={(e) => {
                    const selectedVoice = allVoices.find(v => v.id === e.target.value)
                    setFormData({ 
                      ...formData, 
                      voice_id: e.target.value,
                      voice_system: selectedVoice?.system || 'edge-tts'
                    })
                  }}
                  className="input-field"
                  required
                >
                  <option value="">Selecciona una voz</option>
                  {allVoices.map((voice) => (
                    <option key={voice.id} value={voice.id}>
                      {voice.name} ({voice.system_name}) - {voice.language}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Descripción
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="input-field h-20 resize-none"
                placeholder="Describe qué hace este voicebot..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Prompt del Sistema *
              </label>
              <textarea
                value={formData.system_prompt}
                onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
                className="input-field h-24 resize-none"
                placeholder="Define cómo debe comportarse el voicebot..."
                required
              />
            </div>

            {/* LLM Configuration */}
            <LLMConfig
              selectedProvider={formData.llm_provider}
              onProviderChange={(provider) => setFormData({ ...formData, llm_provider: provider })}
              selectedModel={formData.model}
              onModelChange={(model) => setFormData({ ...formData, model })}
              apiKey={formData.api_key}
              onApiKeyChange={(apiKey) => setFormData({ ...formData, api_key: apiKey })}
            />

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Temperatura: {formData.temperature}
              </label>
              <input
                type="range"
                min="0"
                max="2"
                step="0.1"
                value={formData.temperature}
                onChange={(e) => setFormData({ ...formData, temperature: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="tts_enabled"
                  checked={formData.tts_enabled}
                  onChange={(e) => setFormData({ ...formData, tts_enabled: e.target.checked })}
                  className="mr-2 w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                />
                <label htmlFor="tts_enabled" className="text-sm font-medium text-gray-700">
                  Síntesis de Voz (TTS)
                </label>
              </div>
              
              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="asr_enabled"
                  checked={formData.asr_enabled}
                  onChange={(e) => setFormData({ ...formData, asr_enabled: e.target.checked })}
                  className="mr-2 w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                />
                <label htmlFor="asr_enabled" className="text-sm font-medium text-gray-700">
                  Reconocimiento de Voz (ASR)
                </label>
              </div>
            </div>

            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                className="btn-secondary"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="btn-primary"
              >
                Crear Voicebot
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  const VoiceChatModal = ({ voicebot }) => {
    const handleSendMessage = async (e) => {
      e.preventDefault()
      if (!message.trim() && !audioBlob) return

      try {
        if (audioBlob) {
          // Send voice message using SIP API
          const formData = new FormData()
          formData.append('audio', audioBlob, 'recording.wav')
          formData.append('call_id', `voicebot_${voicebot.id}_${Date.now()}`)
          formData.append('language', 'ca')
          formData.append('voice_system', 'catalan')
          
          const response = await fetch('/api/sip/process-voice', {
            method: 'POST',
            body: formData
          })
          
          const result = await response.json()
          if (result.success) {
            // Add to chat history
            const userMessage = {
              id: Date.now(),
              type: 'user',
              content: result.user_input || 'Mensaje de voz',
              timestamp: new Date().toISOString()
            }
            
            const botMessage = {
              id: Date.now() + 1,
              type: 'bot',
              content: result.agent_response,
              audioUrl: `data:audio/wav;base64,${result.response_audio_base64}`,
              timestamp: new Date().toISOString()
            }
            
            // Update chat history (you'll need to implement this in context)
            console.log('User:', userMessage)
            console.log('Bot:', botMessage)
          }
          
          setAudioBlob(null)
        } else {
          // Send text message using voicebots API
          const response = await fetch('/api/voicebots/synthesize', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              text: message,
              voice_id: voicebot.voice_id || 'ca-ES-EnricNeural',
              system: 'catalan',
              language: 'ca'
            })
          })
          
          const result = await response.json()
          if (result.success) {
            // Add to chat history
            const userMessage = {
              id: Date.now(),
              type: 'user',
              content: message,
              timestamp: new Date().toISOString()
            }
            
            const botMessage = {
              id: Date.now() + 1,
              type: 'bot',
              content: 'Resposta generada',
              audioUrl: `data:audio/mp3;base64,${result.audio_base64}`,
              timestamp: new Date().toISOString()
            }
            
            console.log('User:', userMessage)
            console.log('Bot:', botMessage)
          }
          
          setMessage('')
        }
      } catch (error) {
        console.error('Error sending message:', error)
        toast.error('Error enviant el missatge')
      }
    }

    const startRecording = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const mediaRecorder = new MediaRecorder(stream)
        const audioChunks = []

        mediaRecorder.addEventListener('dataavailable', (event) => {
          audioChunks.push(event.data)
        })

        mediaRecorder.addEventListener('stop', () => {
          const audioBlob = new Blob(audioChunks, { type: 'audio/wav' })
          setAudioBlob(audioBlob)
          stream.getTracks().forEach(track => track.stop())
        })

        mediaRecorder.start()
        setIsRecording(true)

        // Stop recording after 10 seconds max
        setTimeout(() => {
          if (mediaRecorder.state === 'recording') {
            mediaRecorder.stop()
            setIsRecording(false)
          }
        }, 10000)

        // Store recorder reference for manual stop
        window.currentRecorder = mediaRecorder
      } catch (error) {
        console.error('Error starting recording:', error)
        toast.error('Error al acceder al micrófono')
      }
    }

    const stopRecording = () => {
      if (window.currentRecorder && window.currentRecorder.state === 'recording') {
        window.currentRecorder.stop()
        setIsRecording(false)
      }
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg w-full max-w-4xl mx-4 h-[80vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                <Phone className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{voicebot.name}</h3>
                <p className="text-sm text-gray-500">{voicebot.description}</p>
              </div>
            </div>
            <button
              onClick={() => setShowChatModal(false)}
              className="p-2 text-gray-400 hover:text-gray-600"
            >
              ×
            </button>
          </div>

          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {chatHistory.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <Phone className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Inicia una conversación por voz con {voicebot.name}</p>
              </div>
            ) : (
              chatHistory.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      msg.type === 'user'
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-100 text-gray-900'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    {msg.audioUrl && (
                      <audio controls className="mt-2 w-full">
                        <source src={msg.audioUrl} type="audio/wav" />
                      </audio>
                    )}
                    <p className={`text-xs mt-1 ${
                      msg.type === 'user' ? 'text-primary-100' : 'text-gray-500'
                    }`}>
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            
            {isGenerating && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-900 px-4 py-2 rounded-lg flex items-center space-x-2">
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span className="text-sm">Procesando...</span>
                </div>
              </div>
            )}
          </div>

          {/* Voice Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex items-center space-x-4 mb-4">
              <button
                onClick={isRecording ? stopRecording : startRecording}
                disabled={isGenerating}
                className={`flex items-center justify-center w-12 h-12 rounded-full transition-colors ${
                  isRecording 
                    ? 'bg-red-500 hover:bg-red-600 text-white' 
                    : 'bg-primary-500 hover:bg-primary-600 text-white'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isRecording ? (
                  <Square className="w-5 h-5" />
                ) : (
                  <Mic className="w-5 h-5" />
                )}
              </button>
              <div className="flex-1">
                {audioBlob ? (
                  <div className="flex items-center space-x-2 p-2 bg-gray-50 rounded-lg">
                    <Volume2 className="w-4 h-4 text-gray-600" />
                    <span className="text-sm text-gray-600">Audio grabado listo para enviar</span>
                    <button
                      onClick={() => setAudioBlob(null)}
                      className="text-red-500 hover:text-red-700"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ) : (
                  <span className="text-sm text-gray-500">
                    {isRecording ? 'Grabando... (máx. 10s)' : 'Mantén presionado para grabar'}
                  </span>
                )}
              </div>
            </div>

            {/* Text Input Fallback */}
            <form onSubmit={handleSendMessage} className="flex space-x-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="O escribe tu mensaje..."
                className="flex-1 input-field"
                disabled={isGenerating || audioBlob}
              />
              <button
                type="submit"
                disabled={(!message.trim() && !audioBlob) || isGenerating}
                className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Voicebots</h1>
          <p className="mt-2 text-gray-600">
            Crea y gestiona voicebots inteligentes con síntesis y reconocimiento de voz.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Crear Voicebot</span>
        </button>
      </div>

      {/* Voicebots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {voicebots.map((voicebot) => (
          <div key={voicebot.id} className="card group hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-green-500 to-blue-500 rounded-full flex items-center justify-center">
                  <Phone className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{voicebot.name}</h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Volume2 className="w-3 h-3" />
                    <span>{voices.find(v => v.id === voicebot.voice_id)?.name || 'Voz no encontrada'}</span>
                  </div>
                </div>
              </div>
              <div className="relative">
                <button className="p-2 text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>

            {voicebot.description && (
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">{voicebot.description}</p>
            )}

            {/* Voicebot Features */}
            <div className="grid grid-cols-2 gap-4 mb-4 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <Mic className="w-3 h-3" />
                <span>{voicebot.asr_enabled ? 'ASR ✅' : 'ASR ❌'}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Volume2 className="w-3 h-3" />
                <span>{voicebot.tts_enabled ? 'TTS ✅' : 'TTS ❌'}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => {
                  setSelectedVoicebot(voicebot)
                  setCurrentVoicebot(voicebot)
                  setShowChatModal(true)
                }}
                className="btn-primary flex items-center space-x-2 text-sm"
              >
                <Phone className="w-4 h-4" />
                <span>Conversar</span>
              </button>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => deleteVoicebot(voicebot.id)}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Eliminar voicebot"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {voicebots.length === 0 && (
        <div className="card text-center py-12">
          <Phone className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No hay voicebots creados</h3>
          <p className="text-gray-500 mb-6">
            Crea tu primer voicebot para comenzar conversaciones por voz inteligentes.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary"
          >
            Crear Primer Voicebot
          </button>
        </div>
      )}

      {/* Modals */}
      {showCreateModal && <CreateVoicebotModal />}
      {showChatModal && selectedVoicebot && <VoiceChatModal voicebot={selectedVoicebot} />}
    </div>
  )
}

export default Voicebots
