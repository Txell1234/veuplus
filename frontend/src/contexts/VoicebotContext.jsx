import React, { createContext, useContext, useReducer, useEffect } from 'react'
import api from '../config/api'
import toast from 'react-hot-toast'

const VoicebotContext = createContext()

const initialState = {
  voicebots: [],
  currentVoicebot: null,
  isLoading: false,
  isGenerating: false,
  chatHistory: [],
  llmProviders: [
    { id: 'openai', name: 'OpenAI', description: 'GPT-3.5/4 via API' },
    { id: 'local', name: 'Local LLM', description: 'Modelo local (GPT-OSS)' },
    { id: 'vllm', name: 'vLLM', description: 'vLLM server local' },
  ]
}

const voicebotReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_GENERATING':
      return { ...state, isGenerating: action.payload }
    case 'SET_VOICEBOTS':
      return { ...state, voicebots: action.payload }
    case 'SET_CURRENT_VOICEBOT':
      return { ...state, currentVoicebot: action.payload }
    case 'ADD_MESSAGE_TO_HISTORY':
      return { 
        ...state, 
        chatHistory: [...state.chatHistory, action.payload]
      }
    case 'CLEAR_CHAT_HISTORY':
      return { ...state, chatHistory: [] }
    case 'UPDATE_VOICEBOT':
      return {
        ...state,
        voicebots: state.voicebots.map(bot => 
          bot.id === action.payload.id ? action.payload : bot
        )
      }
    default:
      return state
  }
}

export const VoicebotProvider = ({ children }) => {
  const [state, dispatch] = useReducer(voicebotReducer, initialState)

  // Fetch voicebots on mount
  useEffect(() => {
    fetchVoicebots()
  }, [])

  const fetchVoicebots = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      const response = await api.get('/api/voicebots')
      const voicebotsData = response.data.voicebots || response.data || []
      dispatch({ type: 'SET_VOICEBOTS', payload: voicebotsData })
    } catch (error) {
      console.error('Error fetching voicebots:', error)
      // Crear voicebots per defecte si no hi ha API
      const defaultVoicebots = [
        {
          id: 'default-catalan-voicebot',
          name: 'Voicebot Català',
          description: 'Voicebot intel·ligent en català amb veu',
          system_prompt: 'Ets un assistent de veu útil i amigable. Respon sempre en català.',
          llm_provider: 'openai',
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          voice_id: 'ca-ES-EnricNeural',
          tts_enabled: true,
          asr_enabled: true,
          created_at: new Date().toISOString()
        },
        {
          id: 'default-spanish-voicebot',
          name: 'Voicebot Español',
          description: 'Voicebot inteligente en español con voz',
          system_prompt: 'Eres un asistente de voz útil y amigable. Responde siempre en español.',
          llm_provider: 'openai',
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          voice_id: 'es-ES-AlvaroNeural',
          tts_enabled: true,
          asr_enabled: true,
          created_at: new Date().toISOString()
        }
      ]
      dispatch({ type: 'SET_VOICEBOTS', payload: defaultVoicebots })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const createVoicebot = async (voicebotData) => {
    try {
      const response = await api.post('/api/voicebots', voicebotData)
      toast.success('Voicebot creado exitosamente')
      fetchVoicebots() // Refresh voicebots list
      return response.data
    } catch (error) {
      console.error('Error creating voicebot:', error)
      toast.error('Error al crear el voicebot')
      throw error
    }
  }

  const updateVoicebot = async (voicebotId, updates) => {
    try {
      const response = await api.put(`/api/voicebots/${voicebotId}`, updates)
      dispatch({ type: 'UPDATE_VOICEBOT', payload: response.data })
      toast.success('Voicebot actualizado exitosamente')
      return response.data
    } catch (error) {
      console.error('Error updating voicebot:', error)
      toast.error('Error al actualizar el voicebot')
      throw error
    }
  }

  const deleteVoicebot = async (voicebotId) => {
    try {
      await api.delete(`/api/voicebots/${voicebotId}`)
      toast.success('Voicebot eliminado exitosamente')
      fetchVoicebots() // Refresh voicebots list
    } catch (error) {
      console.error('Error deleting voicebot:', error)
      toast.error('Error al eliminar el voicebot')
      throw error
    }
  }

  const sendVoiceMessage = async (messageOrBlob, voicebotId = null) => {
    try {
      dispatch({ type: 'SET_GENERATING', payload: true })
      
      let userMessage
      let requestData

      if (messageOrBlob instanceof Blob) {
        // Voice message (audio blob)
        const formData = new FormData()
        formData.append('audio', messageOrBlob, 'voice_message.wav')
        formData.append('voicebot_id', voicebotId || state.currentVoicebot?.id)

        userMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: '[Mensaje de voz]',
          audioBlob: messageOrBlob,
          timestamp: new Date().toISOString()
        }
        
        requestData = formData
      } else {
        // Text message
        userMessage = {
          id: Date.now().toString(),
          type: 'user',
          content: messageOrBlob,
          timestamp: new Date().toISOString()
        }
        
        requestData = {
          message: messageOrBlob,
          voicebot_id: voicebotId || state.currentVoicebot?.id,
        }
      }

      // Add user message to history
      dispatch({ type: 'ADD_MESSAGE_TO_HISTORY', payload: userMessage })

      const response = await api.post('/api/voicebots/chat', requestData, {
        headers: messageOrBlob instanceof Blob ? {
          'Content-Type': 'multipart/form-data'
        } : {
          'Content-Type': 'application/json'
        }
      })

      // Add bot response to history
      const botMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.data.response,
        audioUrl: response.data.audio_url, // TTS response
        timestamp: new Date().toISOString()
      }
      dispatch({ type: 'ADD_MESSAGE_TO_HISTORY', payload: botMessage })

      return response.data
    } catch (error) {
      console.error('Error sending voice message:', error)
      toast.error('Error al enviar el mensaje')
      throw error
    } finally {
      dispatch({ type: 'SET_GENERATING', payload: false })
    }
  }

  const clearChatHistory = () => {
    dispatch({ type: 'CLEAR_CHAT_HISTORY' })
  }

  const setCurrentVoicebot = (voicebot) => {
    dispatch({ type: 'SET_CURRENT_VOICEBOT', payload: voicebot })
    dispatch({ type: 'CLEAR_CHAT_HISTORY' }) // Clear history when switching voicebots
  }

  const value = {
    ...state,
    fetchVoicebots,
    createVoicebot,
    updateVoicebot,
    deleteVoicebot,
    sendVoiceMessage,
    clearChatHistory,
    setCurrentVoicebot,
  }

  return (
    <VoicebotContext.Provider value={value}>
      {children}
    </VoicebotContext.Provider>
  )
}

export const useVoicebot = () => {
  const context = useContext(VoicebotContext)
  if (!context) {
    throw new Error('useVoicebot must be used within a VoicebotProvider')
  }
  return context
}