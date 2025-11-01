import React, { createContext, useContext, useReducer, useEffect } from 'react'
import api from '../config/api'
import toast from 'react-hot-toast'

const VoiceContext = createContext()

const initialState = {
  voices: [],
  currentVoice: null,
  isLoading: false,
  isGenerating: false,
  audioHistory: [],
  settings: {
    language: 'ca',
    speed: 1.0,
    pitch: 1.0,
    volume: 1.0,
  }
}

const voiceReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_GENERATING':
      return { ...state, isGenerating: action.payload }
    case 'SET_VOICES':
      return { ...state, voices: action.payload }
    case 'SET_CURRENT_VOICE':
      return { ...state, currentVoice: action.payload }
    case 'ADD_AUDIO_TO_HISTORY':
      return { 
        ...state, 
        audioHistory: [action.payload, ...state.audioHistory].slice(0, 50) // Keep last 50
      }
    case 'UPDATE_SETTINGS':
      return { 
        ...state, 
        settings: { ...state.settings, ...action.payload }
      }
    default:
      return state
  }
}

export const VoiceProvider = ({ children }) => {
  const [state, dispatch] = useReducer(voiceReducer, initialState)

  // Fetch voices on mount
  useEffect(() => {
    fetchVoices()
  }, [])

  const fetchVoices = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      // Intentar carregar totes les veus unificades primer
      try {
        const response = await api.get('/api/voices/all')
        const voicesData = response.data.voices || []
        
        // Transform voices to match frontend format
        const transformedVoices = voicesData.map(voice => ({
          id: voice.id,
          name: voice.name,
          language: voice.language,
          description: voice.description,
          gender: voice.gender,
          quality: voice.quality,
          available: true,
          source: voice.source,
          system: voice.system,
          system_name: voice.system_name,
          voice_type: voice.voice_type,
          segre_enabled: voice.segre_enabled || false
        }))
        
        console.log('✅ Totes les veus carregades:', transformedVoices.length)
        dispatch({ type: 'SET_VOICES', payload: transformedVoices })
        
        // Set first voice as current if none selected
        if (transformedVoices.length > 0) {
          dispatch({ type: 'SET_CURRENT_VOICE', payload: transformedVoices[0] })
        }
      } catch (unifiedError) {
        console.warn('Unified voices not available, trying individual endpoints')
        
        // Fallback a endpoint individual
        const response = await api.get('/api/voices')
        const voicesData = response.data.voices || response.data || []
        
        const transformedVoices = voicesData.map(voice => ({
          id: voice.speaker_id || voice.id,
          name: voice.name,
          language: voice.language,
          description: voice.description,
          gender: voice.gender,
          quality: voice.quality,
          available: voice.available,
          source: voice.source
        }))
        
        console.log('Fetched voices (fallback):', transformedVoices.length)
        dispatch({ type: 'SET_VOICES', payload: transformedVoices })
        
        if (transformedVoices.length > 0) {
          dispatch({ type: 'SET_CURRENT_VOICE', payload: transformedVoices[0] })
        }
      }
    } catch (error) {
      console.error('Error fetching voices:', error)
      toast.error('Error al cargar las voces')
      // Add default voices if API fails
      const defaultVoices = [
        { id: 'catalan_enhanced', name: 'Voz Catalana Mejorada', language: 'ca', description: 'Voz catalana de alta calidad' },
        { id: 'spanish_default', name: 'Voz Española', language: 'es', description: 'Voz española estándar' }
      ]
      dispatch({ type: 'SET_VOICES', payload: defaultVoices })
      dispatch({ type: 'SET_CURRENT_VOICE', payload: defaultVoices[0] })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const generateSpeech = async (text, voiceId = null) => {
    try {
      dispatch({ type: 'SET_GENERATING', payload: true })
      
      console.log('VoiceContext: Generating speech with:', { text, voiceId, language: state.settings.language })
      
      const response = await api.post('/api/synthesis', {
        text,
        voice_model_id: voiceId || state.currentVoice?.id,
        language: state.settings.language,
        speaker_id: voiceId || state.currentVoice?.id,
      })

      console.log('VoiceContext: API response:', response.data)

      const audioData = {
        id: Date.now().toString(),
        text,
        voice: voiceId || state.currentVoice?.id,
        audioUrl: `data:audio/wav;base64,${response.data.audio_base64}`,
        timestamp: new Date().toISOString(),
        settings: { ...state.settings }
      }

      console.log('VoiceContext: Audio data created:', { ...audioData, audioUrl: audioData.audioUrl.substring(0, 50) + '...' })

      dispatch({ type: 'ADD_AUDIO_TO_HISTORY', payload: audioData })
      toast.success('Audio generado exitosamente')
      
      return audioData
    } catch (error) {
      console.error('VoiceContext: Error generating speech:', error)
      toast.error('Error al generar el audio')
      throw error
    } finally {
      dispatch({ type: 'SET_GENERATING', payload: false })
    }
  }

  const uploadVoice = async (file, metadata) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('name', metadata.name)
      formData.append('language', metadata.language)
      formData.append('description', metadata.description)

      const response = await api.post('/api/voices/import', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      toast.success('Voz importada exitosamente')
      fetchVoices() // Refresh voices list
      return response.data
    } catch (error) {
      console.error('Error uploading voice:', error)
      toast.error('Error al importar la voz')
      throw error
    }
  }

  const deleteVoice = async (voiceId) => {
    try {
      await api.delete(`/api/voices/${voiceId}`)
      toast.success('Voz eliminada exitosamente')
      fetchVoices() // Refresh voices list
    } catch (error) {
      console.error('Error deleting voice:', error)
      toast.error('Error al eliminar la voz')
      throw error
    }
  }

  const updateSettings = (newSettings) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: newSettings })
  }

  const value = {
    ...state,
    fetchVoices,
    generateSpeech,
    uploadVoice,
    deleteVoice,
    updateSettings,
  }

  return (
    <VoiceContext.Provider value={value}>
      {children}
    </VoiceContext.Provider>
  )
}

export const useVoice = () => {
  const context = useContext(VoiceContext)
  if (!context) {
    throw new Error('useVoice must be used within a VoiceProvider')
  }
  return context
}
