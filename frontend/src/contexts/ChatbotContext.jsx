import React, { createContext, useContext, useReducer, useEffect } from 'react'
import api from '../config/api'
import toast from 'react-hot-toast'

const ChatbotContext = createContext()

const initialState = {
  chatbots: [],
  currentChatbot: null,
  isLoading: false,
  isGenerating: false,
  chatHistory: [],
  llmProviders: [
    { id: 'openai', name: 'OpenAI', description: 'GPT-3.5/4 via API' },
    { id: 'local', name: 'Local LLM', description: 'Modelo local (GPT-OSS)' },
    { id: 'vllm', name: 'vLLM', description: 'vLLM server local' },
  ]
}

const chatbotReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload }
    case 'SET_GENERATING':
      return { ...state, isGenerating: action.payload }
    case 'SET_CHATBOTS':
      return { ...state, chatbots: action.payload }
    case 'SET_CURRENT_CHATBOT':
      return { ...state, currentChatbot: action.payload }
    case 'ADD_MESSAGE_TO_HISTORY':
      return { 
        ...state, 
        chatHistory: [...state.chatHistory, action.payload]
      }
    case 'CLEAR_CHAT_HISTORY':
      return { ...state, chatHistory: [] }
    case 'UPDATE_CHATBOT':
      return {
        ...state,
        chatbots: state.chatbots.map(bot => 
          bot.id === action.payload.id ? action.payload : bot
        )
      }
    default:
      return state
  }
}

export const ChatbotProvider = ({ children }) => {
  const [state, dispatch] = useReducer(chatbotReducer, initialState)

  // Fetch chatbots on mount
  useEffect(() => {
    fetchChatbots()
  }, [])

  const fetchChatbots = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      const response = await api.get('/api/chatbots')
      const chatbotsData = response.data.chatbots || response.data || []
      dispatch({ type: 'SET_CHATBOTS', payload: chatbotsData })
    } catch (error) {
      console.error('Error fetching chatbots:', error)
      // Crear chatbots per defecte si no hi ha API
      const defaultChatbots = [
        {
          id: 'default-catalan',
          name: 'Assistent Català',
          description: 'Assistent intel·ligent en català',
          system_prompt: 'Ets un assistent útil i amigable. Respon sempre en català.',
          llm_provider: 'openai',
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          voice_id: 'ca-ES-EnricNeural',
          created_at: new Date().toISOString()
        },
        {
          id: 'default-spanish',
          name: 'Asistente Español',
          description: 'Asistente inteligente en español',
          system_prompt: 'Eres un asistente útil y amigable. Responde siempre en español.',
          llm_provider: 'openai',
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          voice_id: 'es-ES-AlvaroNeural',
          created_at: new Date().toISOString()
        }
      ]
      dispatch({ type: 'SET_CHATBOTS', payload: defaultChatbots })
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const createChatbot = async (chatbotData) => {
    try {
      const response = await api.post('/api/chatbots', chatbotData)
      toast.success('Chatbot creado exitosamente')
      fetchChatbots() // Refresh chatbots list
      return response.data
    } catch (error) {
      console.error('Error creating chatbot:', error)
      toast.error('Error al crear el chatbot')
      throw error
    }
  }

  const updateChatbot = async (chatbotId, updates) => {
    try {
      const response = await api.put(`/api/chatbots/${chatbotId}`, updates)
      dispatch({ type: 'UPDATE_CHATBOT', payload: response.data })
      toast.success('Chatbot actualizado exitosamente')
      return response.data
    } catch (error) {
      console.error('Error updating chatbot:', error)
      toast.error('Error al actualizar el chatbot')
      throw error
    }
  }

  const deleteChatbot = async (chatbotId) => {
    try {
      await api.delete(`/api/chatbots/${chatbotId}`)
      toast.success('Chatbot eliminado exitosamente')
      fetchChatbots() // Refresh chatbots list
    } catch (error) {
      console.error('Error deleting chatbot:', error)
      toast.error('Error al eliminar el chatbot')
      throw error
    }
  }

  const sendMessage = async (message, chatbotId = null) => {
    try {
      dispatch({ type: 'SET_GENERATING', payload: true })
      
      // Add user message to history
      const userMessage = {
        id: Date.now().toString(),
        type: 'user',
        content: message,
        timestamp: new Date().toISOString()
      }
      dispatch({ type: 'ADD_MESSAGE_TO_HISTORY', payload: userMessage })

      const response = await api.post('/api/chatbots/chat', {
        message,
        chatbot_id: chatbotId || state.currentChatbot?.id,
      })

      // Add bot response to history
      const botMessage = {
        id: (Date.now() + 1).toString(),
        type: 'bot',
        content: response.data.response,
        timestamp: new Date().toISOString()
      }
      dispatch({ type: 'ADD_MESSAGE_TO_HISTORY', payload: botMessage })

      return response.data
    } catch (error) {
      console.error('Error sending message:', error)
      toast.error('Error al enviar el mensaje')
      throw error
    } finally {
      dispatch({ type: 'SET_GENERATING', payload: false })
    }
  }

  const clearChatHistory = () => {
    dispatch({ type: 'CLEAR_CHAT_HISTORY' })
  }

  const setCurrentChatbot = (chatbot) => {
    dispatch({ type: 'SET_CURRENT_CHATBOT', payload: chatbot })
    dispatch({ type: 'CLEAR_CHAT_HISTORY' }) // Clear history when switching chatbots
  }

  const value = {
    ...state,
    fetchChatbots,
    createChatbot,
    updateChatbot,
    deleteChatbot,
    sendMessage,
    clearChatHistory,
    setCurrentChatbot,
  }

  return (
    <ChatbotContext.Provider value={value}>
      {children}
    </ChatbotContext.Provider>
  )
}

export const useChatbot = () => {
  const context = useContext(ChatbotContext)
  if (!context) {
    throw new Error('useChatbot must be used within a ChatbotProvider')
  }
  return context
}
