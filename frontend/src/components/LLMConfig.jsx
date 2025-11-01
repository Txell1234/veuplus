import React, { useState, useEffect } from 'react'
import { Key, Settings, TestTube, Check, X } from 'lucide-react'
import toast from 'react-hot-toast'

const LLMConfig = ({ 
  selectedProvider, 
  onProviderChange, 
  selectedModel, 
  onModelChange,
  apiKey,
  onApiKeyChange,
  className = ""
}) => {
  const [providers, setProviders] = useState({})
  const [isLoading, setIsLoading] = useState(false)
  const [testResult, setTestResult] = useState(null)

  useEffect(() => {
    fetchProviders()
  }, [])

  const fetchProviders = async () => {
    try {
      setIsLoading(true)
      const response = await fetch('/api/llm/providers')
      if (response.ok) {
        const data = await response.json()
        setProviders(data.providers || {})
        console.log('✅ LLM Providers carregats:', Object.keys(data.providers || {}))
      }
    } catch (error) {
      console.error('Error fetching providers:', error)
      toast.error('Error carregant proveïdors LLM')
    } finally {
      setIsLoading(false)
    }
  }

  const testProvider = async (providerId) => {
    try {
      setIsLoading(true)
      const response = await fetch(`/api/llm/providers/${providerId}/test`, {
        method: 'POST'
      })
      
      if (response.ok) {
        const data = await response.json()
        setTestResult(data.test_result)
        toast.success(`Test ${data.test_result.connection_status}`)
      } else {
        setTestResult({ connection_status: 'failed', error: 'Test failed' })
        toast.error('Test fallit')
      }
    } catch (error) {
      console.error('Error testing provider:', error)
      setTestResult({ connection_status: 'failed', error: error.message })
      toast.error('Error en el test')
    } finally {
      setIsLoading(false)
    }
  }

  const currentProvider = providers[selectedProvider]

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Provider Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Proveïdor LLM *
        </label>
        <div className="flex space-x-2">
          <select
            value={selectedProvider || ''}
            onChange={(e) => {
              const provider = e.target.value
              const providerConfig = providers[provider]
              onProviderChange(provider)
              onModelChange(providerConfig?.default_model || '')
              onApiKeyChange('')
            }}
            className="flex-1 input-field"
            required
          >
            <option value="">Selecciona un proveïdor</option>
            {Object.entries(providers).map(([id, provider]) => (
              <option key={id} value={id}>
                {provider.name} {provider.available ? '✅' : '❌'}
              </option>
            ))}
          </select>
          
          {selectedProvider && (
            <button
              type="button"
              onClick={() => testProvider(selectedProvider)}
              disabled={isLoading}
              className="px-3 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              title="Testar connexió"
            >
              <TestTube className="w-4 h-4" />
            </button>
          )}
        </div>
        
        {currentProvider && (
          <p className="text-xs text-gray-500 mt-1">
            {currentProvider.description}
          </p>
        )}
      </div>

      {/* Model Selection */}
      {currentProvider && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Model *
          </label>
          <select
            value={selectedModel || ''}
            onChange={(e) => onModelChange(e.target.value)}
            className="input-field"
            required
          >
            <option value="">Selecciona un model</option>
            {currentProvider.models?.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* API Key Configuration */}
      {currentProvider?.api_key_required && (
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            API Key *
          </label>
          <div className="flex space-x-2">
            <input
              type="password"
              value={apiKey || ''}
              onChange={(e) => onApiKeyChange(e.target.value)}
              className="flex-1 input-field"
              placeholder={`Introduce tu API key de ${currentProvider.name}`}
              required
            />
            <div className="flex items-center">
              {apiKey && apiKey.length > 10 ? (
                <Check className="w-5 h-5 text-green-500" />
              ) : (
                <X className="w-5 h-5 text-red-500" />
              )}
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            La API key se guardará de forma segura y solo se usará para este voicebot
          </p>
        </div>
      )}

      {/* Test Result */}
      {testResult && (
        <div className={`p-3 rounded-lg ${
          testResult.connection_status === 'success' 
            ? 'bg-green-50 border border-green-200' 
            : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center space-x-2">
            {testResult.connection_status === 'success' ? (
              <Check className="w-4 h-4 text-green-500" />
            ) : (
              <X className="w-4 h-4 text-red-500" />
            )}
            <span className={`text-sm font-medium ${
              testResult.connection_status === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              Test: {testResult.connection_status}
            </span>
          </div>
          {testResult.test_message && (
            <p className="text-xs text-gray-600 mt-1">
              {testResult.test_message} → {testResult.test_response}
            </p>
          )}
        </div>
      )}

      {/* Provider Info */}
      {currentProvider && (
        <div className="bg-gray-50 p-3 rounded-lg">
          <h4 className="text-sm font-medium text-gray-900 mb-2">
            Informació del Proveïdor
          </h4>
          <div className="grid grid-cols-2 gap-2 text-xs text-gray-600">
            <div>
              <span className="font-medium">Idiomes:</span> {currentProvider.languages?.join(', ')}
            </div>
            <div>
              <span className="font-medium">Max Tokens:</span> {currentProvider.max_tokens}
            </div>
            <div>
              <span className="font-medium">Streaming:</span> {currentProvider.supports_streaming ? 'Sí' : 'No'}
            </div>
            <div>
              <span className="font-medium">Funcions:</span> {currentProvider.supports_functions ? 'Sí' : 'No'}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default LLMConfig
