import React, { useState, useEffect } from 'react'
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw, 
  Database, 
  Key, 
  Globe,
  Volume2,
  Bot,
  Shield,
  Download,
  Upload,
  Trash2,
  Check,
  X
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'
import { useVoice } from '../contexts/VoiceContext'
import { useTheme } from '../contexts/ThemeContext'
import SettingsDebug from '../components/SettingsDebug'
import { 
  API_CONFIG, 
  LLM_PROVIDERS, 
  LANGUAGES, 
  THEMES, 
  LOG_LEVELS, 
  AUDIO_CONFIG, 
  CHATBOT_CONFIG, 
  SYSTEM_CONFIG 
} from '../config/constants'

const Settings = () => {
  const { voices } = useVoice()
  const { theme, language, changeTheme, changeLanguage } = useTheme()
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    // General Settings
    language: 'ca',
    theme: 'light',
    autoSave: true,
    notifications: true,
    
    // API Settings
    openaiApiKey: '',
    openaiBaseUrl: 'https://api.openai.com/v1',
    vllmBaseUrl: API_CONFIG.VLLM_URL,
    transformersProvider: 'openai',
    
    // Voicebots & SIP Settings
    sipEnabled: true,
    knowledgeBaseEnabled: true,
    voiceTrainingEnabled: true,
    aliaKitEnabled: true,
    
    // Voice Settings
    defaultVoice: '',
    defaultSpeed: AUDIO_CONFIG.DEFAULT_SPEED,
    defaultPitch: AUDIO_CONFIG.DEFAULT_PITCH,
    defaultVolume: AUDIO_CONFIG.DEFAULT_VOLUME,
    
    // Chatbot Settings
    defaultModel: CHATBOT_CONFIG.DEFAULT_MODEL,
    defaultTemperature: CHATBOT_CONFIG.DEFAULT_TEMPERATURE,
    defaultMaxTokens: CHATBOT_CONFIG.DEFAULT_MAX_TOKENS,
    
    // System Settings
    maxAudioHistory: SYSTEM_CONFIG.DEFAULT_MAX_AUDIO_HISTORY,
    autoCleanup: SYSTEM_CONFIG.DEFAULT_AUTO_CLEANUP,
    logLevel: SYSTEM_CONFIG.DEFAULT_LOG_LEVEL
  })

  const [isSaving, setIsSaving] = useState(false)
  const [isTestingConnection, setIsTestingConnection] = useState(false)
  const [availableProviders, setAvailableProviders] = useState({})
  const [testResults, setTestResults] = useState({})

  // Load settings from localStorage on component mount
  useEffect(() => {
    const savedSettings = localStorage.getItem('veuplus-settings')
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings)
        setSettings(prev => ({ ...prev, ...parsed }))
      } catch (error) {
        console.error('Error loading settings:', error)
      }
    }
    
    // Sync with theme context
    setSettings(prev => ({ ...prev, theme, language }))
  }, [theme, language])

  // Save settings to localStorage whenever settings change
  useEffect(() => {
    localStorage.setItem('veuplus-settings', JSON.stringify(settings))
  }, [settings])

  // Load available providers on component mount
  useEffect(() => {
    fetchAvailableProviders()
  }, [])

  const tabs = [
    { id: 'general', name: 'General', icon: SettingsIcon },
    { id: 'api', name: 'API', icon: Key },
    { id: 'voice', name: 'Voz', icon: Volume2 },
    { id: 'chatbot', name: 'Chatbot', icon: Bot },
    { id: 'system', name: 'Sistema', icon: Database },
  ]

  const handleSettingChange = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    
    // Handle theme and language changes immediately
    if (key === 'theme') {
      changeTheme(value)
    }
    if (key === 'language') {
      changeLanguage(value)
    }
  }

  const handleSaveSettings = async () => {
    setIsSaving(true)
    try {
      // Save to localStorage (already done in useEffect)
      // In a real app, you would also save to the backend
      await new Promise(resolve => setTimeout(resolve, 500))
      toast.success('Configuración guardada exitosamente')
    } catch (error) {
      toast.error('Error al guardar la configuración')
    } finally {
      setIsSaving(false)
    }
  }

  const testApiConnection = async (provider) => {
    setIsTestingConnection(true)
    try {
      // Simulate API test
      await new Promise(resolve => setTimeout(resolve, 2000))
      toast.success(`Conexión ${provider} exitosa`)
    } catch (error) {
      toast.error(`Error conectando con ${provider}`)
    } finally {
      setIsTestingConnection(false)
    }
  }

  const exportSettings = () => {
    const dataStr = JSON.stringify(settings, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = 'veuplus-settings.json'
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
    
    toast.success('Configuración exportada')
  }

  const importSettings = (event) => {
    const file = event.target.files[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result)
          setSettings(importedSettings)
          toast.success('Configuración importada')
        } catch (error) {
          toast.error('Error al importar la configuración')
        }
      }
      reader.readAsText(file)
    }
  }

  const resetSettings = () => {
    if (confirm('¿Estás seguro de que quieres restaurar la configuración por defecto?')) {
      // Reset to default settings
      const defaultSettings = {
        language: 'ca',
        theme: 'light',
        autoSave: true,
        notifications: true,
        openaiApiKey: '',
        openaiBaseUrl: 'https://api.openai.com/v1',
        vllmBaseUrl: API_CONFIG.VLLM_URL,
        transformersProvider: 'openai',
        defaultVoice: '',
        defaultSpeed: AUDIO_CONFIG.DEFAULT_SPEED,
        defaultPitch: AUDIO_CONFIG.DEFAULT_PITCH,
        defaultVolume: AUDIO_CONFIG.DEFAULT_VOLUME,
        defaultModel: CHATBOT_CONFIG.DEFAULT_MODEL,
        defaultTemperature: CHATBOT_CONFIG.DEFAULT_TEMPERATURE,
        defaultMaxTokens: CHATBOT_CONFIG.DEFAULT_MAX_TOKENS,
        maxAudioHistory: SYSTEM_CONFIG.DEFAULT_MAX_AUDIO_HISTORY,
        autoCleanup: SYSTEM_CONFIG.DEFAULT_AUTO_CLEANUP,
        logLevel: SYSTEM_CONFIG.DEFAULT_LOG_LEVEL
      }
      setSettings(defaultSettings)
      localStorage.setItem('veuplus-settings', JSON.stringify(defaultSettings))
      toast.success('Configuración restaurada')
    }
  }

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Idioma de la Interfaz
        </label>
        <select
          value={settings.language}
          onChange={(e) => handleSettingChange('language', e.target.value)}
          className="input-field"
        >
          {Object.entries(LANGUAGES).map(([key, lang]) => (
            <option key={key} value={lang.code}>
              {lang.flag} {lang.name}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Tema
        </label>
        <select
          value={settings.theme}
          onChange={(e) => handleSettingChange('theme', e.target.value)}
          className="input-field"
        >
          {Object.entries(THEMES).map(([key, theme]) => (
            <option key={key} value={theme.code}>
              {theme.icon} {theme.name}
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-700">Guardado Automático</h3>
            <p className="text-sm text-gray-500">Guarda automáticamente los cambios</p>
          </div>
          <button
            onClick={() => handleSettingChange('autoSave', !settings.autoSave)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              settings.autoSave ? 'bg-primary-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                settings.autoSave ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-gray-700">Notificaciones</h3>
            <p className="text-sm text-gray-500">Recibe notificaciones de eventos importantes</p>
          </div>
          <button
            onClick={() => handleSettingChange('notifications', !settings.notifications)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              settings.notifications ? 'bg-primary-600' : 'bg-gray-200'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                settings.notifications ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  )

  // Provider configurations moved outside the function
  const providerConfigs = {
    openai: {
      name: 'OpenAI',
      icon: '🤖',
      description: 'GPT-4, GPT-3.5-turbo y otros modelos de OpenAI',
      instructions: 'Configura OPENAI_API_KEY en variables de entorno'
    },
    gemini: {
      name: 'Google Gemini',
      icon: '🔮',
      description: 'Gemini Pro, Gemini 1.5 Pro/Flash de Google',
      instructions: 'Configura GEMINI_API_KEY en variables de entorno'
    },
    anthropic: {
      name: 'Anthropic Claude',
      icon: '🧠',
      description: 'Claude 3.5 Sonnet, Claude 3 Haiku/Opus',
      instructions: 'Configura ANTHROPIC_API_KEY en variables de entorno'
    },
    azure: {
      name: 'Azure OpenAI',
      icon: '☁️',
      description: 'Modelos OpenAI en Azure Cloud',
      instructions: 'Configura AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_NAME'
    },
    ollama: {
      name: 'Ollama (Local)',
      icon: '🏠',
      description: 'Modelos locales con Ollama',
      instructions: 'Instala Ollama: https://ollama.ai'
    },
    local: {
      name: 'Local Transformers',
      icon: '💻',
      description: 'Modelos Hugging Face locales',
      instructions: 'No requiere configuración adicional'
    }
  }

  const fetchAvailableProviders = async () => {
    try {
      const response = await api.get('/api/llm/providers')
      setAvailableProviders(response.data.providers || {})
    } catch (error) {
      console.error('Error fetching providers:', error)
      // Set mock data for demo purposes
      setAvailableProviders({
        openai: { available: false, models: ['gpt-3.5-turbo', 'gpt-4'] },
        gemini: { available: false, models: ['gemini-pro'] },
        anthropic: { available: false, models: ['claude-3-sonnet'] },
        azure: { available: false, models: ['gpt-35-turbo'] },
        ollama: { available: true, models: ['llama2', 'codellama'] },
        local: { available: true, models: ['gpt-oss-20b'] }
      })
    }
  }
  
  const testProvider = async (providerId) => {
    setIsTestingConnection(true)
    try {
      const response = await api.post('/api/llm/test', { provider: providerId })
      const result = response.data

      setTestResults(prev => ({
        ...prev,
        [providerId]: result
      }))

      if (result.success) {
        toast.success(`✅ ${providerConfigs[providerId]?.name} funcionando correctamente`)
      } else {
        toast.error(`❌ Error en ${providerConfigs[providerId]?.name}: ${result.error}`)
      }
    } catch (error) {
      console.error('Error testing provider:', error)
      toast.error('Error probando proveedor')
      setTestResults(prev => ({
        ...prev,
        [providerId]: { success: false, error: error.message }
      }))
    } finally {
      setIsTestingConnection(false)
    }
  }

  const renderApiSettings = () => (
    <div className="space-y-6">
      <div className="bg-blue-50 rounded-lg p-4 mb-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-2">
          🔧 Configuración de Proveedores LLM
        </h3>
        <p className="text-sm text-blue-800">
          VeuPlus soporta múltiples proveedores LLM. Configura las API keys como variables de entorno y reinicia el servidor.
        </p>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        {Object.entries(providerConfigs).map(([providerId, config]) => {
          const provider = availableProviders[providerId]
          const isAvailable = provider?.available || false
          const testResult = testResults[providerId]

          return (
            <div key={providerId} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-3">
                  <span className="text-xl">{config.icon}</span>
                  <div>
                    <h4 className="font-semibold text-gray-900">{config.name}</h4>
                    <p className="text-sm text-gray-600">{config.description}</p>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  isAvailable 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {isAvailable ? 'Disponible' : 'No configurado'}
                </div>
              </div>

              <div className="text-sm text-gray-600 mb-3">
                💡 {config.instructions}
              </div>

              {/* Modelos disponibles */}
              {provider && (
                <div className="mb-3">
                  <h5 className="text-sm font-medium text-gray-700 mb-1">Modelos:</h5>
                  <div className="flex flex-wrap gap-1">
                    {provider.models.map(model => (
                      <span
                        key={model}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                      >
                        {model}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Botón de prueba */}
              <button
                onClick={() => testProvider(providerId)}
                disabled={isTestingConnection || !isAvailable}
                className={`w-full py-2 px-3 rounded-lg font-medium text-sm transition-colors ${
                  isAvailable
                    ? 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {isTestingConnection ? 'Probando...' : 'Probar Conexión'}
              </button>

              {/* Resultado de la prueba */}
              {testResult && (
                <div className={`mt-2 p-2 rounded text-xs ${
                  testResult.success
                    ? 'bg-green-50 text-green-800'
                    : 'bg-red-50 text-red-800'
                }`}>
                  {testResult.success ? (
                    <>✅ Conexión exitosa - Modelo: {testResult.model}</>
                  ) : (
                    <>❌ Error: {testResult.error}</>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )

  const renderVoiceSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Voz por Defecto
        </label>
        <select
          value={settings.defaultVoice}
          onChange={(e) => handleSettingChange('defaultVoice', e.target.value)}
          className="input-field"
        >
          <option value="">Seleccionar voz...</option>
          {voices.map(voice => (
            <option key={voice.id} value={voice.id}>
              {voice.name} ({voice.language})
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Velocidad: {settings.defaultSpeed}x
          </label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={settings.defaultSpeed}
            onChange={(e) => handleSettingChange('defaultSpeed', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tono: {settings.defaultPitch}x
          </label>
          <input
            type="range"
            min="0.5"
            max="2.0"
            step="0.1"
            value={settings.defaultPitch}
            onChange={(e) => handleSettingChange('defaultPitch', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Volumen: {Math.round(settings.defaultVolume * 100)}%
          </label>
          <input
            type="range"
            min="0.1"
            max="1.0"
            step="0.1"
            value={settings.defaultVolume}
            onChange={(e) => handleSettingChange('defaultVolume', parseFloat(e.target.value))}
            className="w-full"
          />
        </div>
      </div>
    </div>
  )

  const renderChatbotSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Modelo por Defecto
        </label>
        <select
          value={settings.defaultModel}
          onChange={(e) => handleSettingChange('defaultModel', e.target.value)}
          className="input-field"
        >
          <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
          <option value="gpt-4">GPT-4</option>
          <option value="gpt-4-turbo">GPT-4 Turbo</option>
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Temperatura: {settings.defaultTemperature}
        </label>
        <input
          type="range"
          min="0"
          max="2"
          step="0.1"
          value={settings.defaultTemperature}
          onChange={(e) => handleSettingChange('defaultTemperature', parseFloat(e.target.value))}
          className="w-full"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Máximo de Tokens
        </label>
        <input
          type="number"
          value={settings.defaultMaxTokens}
          onChange={(e) => handleSettingChange('defaultMaxTokens', parseInt(e.target.value))}
          className="input-field"
          min="100"
          max="4000"
        />
      </div>
    </div>
  )

  const renderSystemSettings = () => (
    <div className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Máximo Historial de Audio
        </label>
        <input
          type="number"
          value={settings.maxAudioHistory}
          onChange={(e) => handleSettingChange('maxAudioHistory', parseInt(e.target.value))}
          className="input-field"
          min="10"
          max="200"
        />
        <p className="text-sm text-gray-500 mt-1">
          Número máximo de audios a mantener en el historial
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-medium text-gray-700">Limpieza Automática</h3>
          <p className="text-sm text-gray-500">Elimina automáticamente archivos temporales</p>
        </div>
        <button
          onClick={() => handleSettingChange('autoCleanup', !settings.autoCleanup)}
          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
            settings.autoCleanup ? 'bg-primary-600' : 'bg-gray-200'
          }`}
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
              settings.autoCleanup ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Nivel de Log
        </label>
        <select
          value={settings.logLevel}
          onChange={(e) => handleSettingChange('logLevel', e.target.value)}
          className="input-field"
        >
          {Object.entries(LOG_LEVELS).map(([key, level]) => (
            <option key={key} value={level.code}>
              {level.name}
            </option>
          ))}
        </select>
      </div>

      {/* Import/Export */}
      <div className="border-t border-gray-200 pt-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Importar/Exportar Configuración</h3>
        <div className="flex space-x-3">
          <button
            onClick={exportSettings}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Exportar</span>
          </button>
          
          <label className="btn-secondary flex items-center space-x-2 cursor-pointer">
            <Upload className="w-4 h-4" />
            <span>Importar</span>
            <input
              type="file"
              accept=".json"
              onChange={importSettings}
              className="hidden"
            />
          </label>
          
          <button
            onClick={resetSettings}
            className="btn-secondary flex items-center space-x-2 text-red-600 hover:text-red-700"
          >
            <RefreshCw className="w-4 h-4" />
            <span>Restaurar</span>
          </button>
        </div>
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings()
      case 'api':
        return renderApiSettings()
      case 'voice':
        return renderVoiceSettings()
      case 'chatbot':
        return renderChatbotSettings()
      case 'system':
        return renderSystemSettings()
      default:
        return renderGeneralSettings()
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Configuración</h1>
        <p className="mt-2 text-gray-600">
          Personaliza VeuPlus según tus necesidades.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="lg:col-span-1">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-700'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5 mr-3" />
                  {tab.name}
                </button>
              )
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="lg:col-span-3">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-gray-900">
                {tabs.find(tab => tab.id === activeTab)?.name}
              </h2>
              <button
                onClick={handleSaveSettings}
                disabled={isSaving}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50"
              >
                {isSaving ? (
                  <RefreshCw className="w-4 h-4 animate-spin" />
                ) : (
                  <Save className="w-4 h-4" />
                )}
                <span>{isSaving ? 'Guardando...' : 'Guardar'}</span>
              </button>
            </div>

            {renderTabContent()}
          </div>
          
          {/* Debug Info */}
          {activeTab === 'api' && <SettingsDebug />}
        </div>
      </div>
    </div>
  )
}

export default Settings
