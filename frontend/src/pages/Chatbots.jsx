import React, { useState } from 'react'
import { 
  Bot, 
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
  User
} from 'lucide-react'
import { useChatbot } from '../contexts/ChatbotContext'
import LLMConfig from '../components/LLMConfig'
import toast from 'react-hot-toast'

const Chatbots = () => {
  const { 
    chatbots, 
    createChatbot, 
    updateChatbot, 
    deleteChatbot, 
    sendMessage, 
    chatHistory, 
    isGenerating,
    llmProviders,
    setCurrentChatbot,
    currentChatbot 
  } = useChatbot()
  
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showChatModal, setShowChatModal] = useState(false)
  const [message, setMessage] = useState('')
  const [selectedChatbot, setSelectedChatbot] = useState(null)

  const CreateChatbotModal = () => {
    const [formData, setFormData] = useState({
      name: '',
      description: '',
      system_prompt: 'Eres un asistente útil y amigable. Responde en catalán.',
      llm_provider: 'local',
      model: 'distilgpt2',
      temperature: 0.7,
      max_tokens: 1000,
      voice_id: null
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
        }
      } catch (error) {
        console.error('Error fetching providers:', error)
      }
    }

    const handleSubmit = async (e) => {
      e.preventDefault()
      try {
        await createChatbot(formData)
        setShowCreateModal(false)
        setFormData({
          name: '',
          description: '',
          system_prompt: 'Eres un asistente útil y amigable. Responde en catalán.',
          llm_provider: 'openai',
          model: 'gpt-3.5-turbo',
          temperature: 0.7,
          max_tokens: 1000,
          voice_id: null
        })
      } catch (error) {
        console.error('Error creating chatbot:', error)
      }
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">Crear Nuevo Chatbot</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Chatbot *
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="input-field"
                  placeholder="Ej: Asistente Virtual"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Proveedor LLM *
                </label>
                <select
                  value={formData.llm_provider}
                  onChange={(e) => {
                    const provider = e.target.value
                    const providerConfig = availableProviders[provider]
                    setFormData({ 
                      ...formData, 
                      llm_provider: provider,
                      model: providerConfig?.default_model || formData.model
                    })
                  }}
                  className="input-field"
                  required
                >
                  <option value="">Selecciona un proveedor</option>
                  {Object.entries(availableProviders).map(([id, provider]) => (
                    <option key={id} value={id}>
                      {provider.name} {provider.available ? '✅' : '❌'}
                    </option>
                  ))}
                </select>
                
                {/* Mostrar información del proveedor seleccionado */}
                {formData.llm_provider && availableProviders[formData.llm_provider] && (
                  <div className="mt-2 p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-800">
                      <strong>{availableProviders[formData.llm_provider].name}</strong>
                      <div className="mt-1">
                        Streaming: {availableProviders[formData.llm_provider].supports_streaming ? '✅' : '❌'} |
                        Funciones: {availableProviders[formData.llm_provider].supports_functions ? '✅' : '❌'}
                      </div>
                    </div>
                  </div>
                )}
                
                {/* Selector de modelo */}
                {formData.llm_provider && availableProviders[formData.llm_provider] && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Modelo LLM
                    </label>
                    <select
                      value={formData.model}
                      onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                      className="input-field"
                      required
                    >
                      {availableProviders[formData.llm_provider].models.map(model => (
                        <option key={model} value={model}>
                          {model}
                        </option>
                      ))}
                    </select>
                  </div>
                )}
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
                placeholder="Describe qué hace este chatbot..."
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
                placeholder="Define cómo debe comportarse el chatbot..."
                required
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Modelo
                </label>
                <select
                  value={formData.model}
                  onChange={(e) => setFormData({ ...formData, model: e.target.value })}
                  className="input-field"
                >
                  <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                  <option value="gpt-4">GPT-4</option>
                  <option value="gpt-4-turbo">GPT-4 Turbo</option>
                </select>
              </div>

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

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Máx. Tokens
                </label>
                <input
                  type="number"
                  value={formData.max_tokens}
                  onChange={(e) => setFormData({ ...formData, max_tokens: parseInt(e.target.value) })}
                  className="input-field"
                  min="100"
                  max="4000"
                />
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
                Crear Chatbot
              </button>
            </div>
          </form>
        </div>
      </div>
    )
  }

  const ChatModal = ({ chatbot }) => {
    const handleSendMessage = async (e) => {
      e.preventDefault()
      if (!message.trim()) return

      try {
        // Use ALIA LLM API for intelligent responses
        const response = await fetch('/api/alia/llm/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            messages: [
              {
                role: 'system',
                content: chatbot.system_prompt || 'Eres un asistente útil y amigable. Responde en catalán.'
              },
              {
                role: 'user',
                content: message
              }
            ],
            model_name: chatbot.model || 'salamandra-7b',
            language: 'ca',
            max_tokens: chatbot.max_tokens || 1000,
            temperature: chatbot.temperature || 0.7
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
            content: result.response,
            timestamp: new Date().toISOString()
          }
          
          console.log('User:', userMessage)
          console.log('Bot:', botMessage)
          
          // If voice is enabled, generate audio
          if (chatbot.voice_id) {
            const audioResponse = await fetch('/api/voicebots/synthesize', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({
                text: result.response,
                voice_id: chatbot.voice_id,
                system: 'catalan',
                language: 'ca'
              })
            })
            
            const audioResult = await audioResponse.json()
            if (audioResult.success) {
              botMessage.audioUrl = `data:audio/mp3;base64,${audioResult.audio_base64}`
            }
          }
        }
        
        setMessage('')
      } catch (error) {
        console.error('Error sending message:', error)
        toast.error('Error enviant el missatge')
      }
    }

    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg w-full max-w-4xl mx-4 h-[80vh] flex flex-col">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">{chatbot.name}</h3>
                <p className="text-sm text-gray-500">{chatbot.description}</p>
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
                <MessageSquare className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Inicia una conversación con {chatbot.name}</p>
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
                  <span className="text-sm">Pensando...</span>
                </div>
              </div>
            )}
          </div>

          {/* Message Input */}
          <div className="p-4 border-t border-gray-200">
            <form onSubmit={handleSendMessage} className="flex space-x-2">
              <input
                type="text"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Escribe tu mensaje..."
                className="flex-1 input-field"
                disabled={isGenerating}
              />
              <button
                type="submit"
                disabled={!message.trim() || isGenerating}
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
          <h1 className="text-3xl font-bold text-gray-900">Chatbots</h1>
          <p className="mt-2 text-gray-600">
            Crea y gestiona chatbots inteligentes con integración LLM.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="w-5 h-5" />
          <span>Crear Chatbot</span>
        </button>
      </div>

      {/* Chatbots Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {chatbots.map((chatbot) => (
          <div key={chatbot.id} className="card group hover:shadow-md transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">{chatbot.name}</h3>
                  <div className="flex items-center space-x-2 text-sm text-gray-500">
                    <Brain className="w-3 h-3" />
                    <span>{llmProviders.find(p => p.id === chatbot.llm_provider)?.name}</span>
                  </div>
                </div>
              </div>
              <div className="relative">
                <button className="p-2 text-gray-400 hover:text-gray-600 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Settings className="w-4 h-4" />
                </button>
              </div>
            </div>

            {chatbot.description && (
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">{chatbot.description}</p>
            )}

            {/* Chatbot Stats */}
            <div className="grid grid-cols-2 gap-4 mb-4 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <Sparkles className="w-3 h-3" />
                <span>{chatbot.model}</span>
              </div>
              <div className="flex items-center space-x-1">
                <Zap className="w-3 h-3" />
                <span>T: {chatbot.temperature}</span>
              </div>
            </div>

            {/* Actions */}
            <div className="flex items-center justify-between">
              <button
                onClick={() => {
                  setSelectedChatbot(chatbot)
                  setCurrentChatbot(chatbot)
                  setShowChatModal(true)
                }}
                className="btn-primary flex items-center space-x-2 text-sm"
              >
                <MessageSquare className="w-4 h-4" />
                <span>Chatear</span>
              </button>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => deleteChatbot(chatbot.id)}
                  className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                  title="Eliminar chatbot"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {chatbots.length === 0 && (
        <div className="card text-center py-12">
          <Bot className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No hay chatbots creados</h3>
          <p className="text-gray-500 mb-6">
            Crea tu primer chatbot para comenzar conversaciones inteligentes.
          </p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="btn-primary"
          >
            Crear Primer Chatbot
          </button>
        </div>
      )}

      {/* Modals */}
      {showCreateModal && <CreateChatbotModal />}
      {showChatModal && selectedChatbot && <ChatModal chatbot={selectedChatbot} />}
    </div>
  )
}

export default Chatbots
