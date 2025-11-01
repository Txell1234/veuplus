import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Mic,
  Volume2,
  Bot,
  Activity,
  Database,
  Zap,
  TrendingUp,
  Users,
  MessageSquare,
  BarChart3,
  Phone,
  Rocket,
  Headphones,
} from 'lucide-react'
import { useVoice } from '../contexts/VoiceContext'
import { useChatbot } from '../contexts/ChatbotContext'
import { useVoicebot } from '../contexts/VoicebotContext'
import api from '../config/api'

const Dashboard = () => {
  const { voices, audioHistory, isLoading: voiceLoading } = useVoice()
  const { chatbots, isLoading: chatbotLoading } = useChatbot()
  const { voicebots } = useVoicebot()
  const [systemStats, setSystemStats] = useState({
    apiStatus: 'checking',
    databaseStatus: 'checking',
    uptime: '0m',
    totalRequests: 0,
    ttsEngine: 'unknown',
    sipStatus: 'checking',
    knowledgeBaseStatus: 'checking',
    voiceTrainingStatus: 'checking',
    aliaKitStatus: 'checking'
  })

  // Fetch system status
  useEffect(() => {
    fetchSystemStatus()
  }, [])

  const fetchSystemStatus = async () => {
    try {
      // Check main API health
      const response = await api.get('/api/health')
      setSystemStats(prev => ({
        ...prev,
        apiStatus: response.data.status === 'healthy' ? 'healthy' : 'unhealthy',
        databaseStatus: response.data.database === 'sqlite' ? 'connected' : 'disconnected',
        uptime: response.data.uptime || 'unknown',
        ttsEngine: response.data.tts_engine || 'unknown'
      }))
      
      // Check SIP status
      try {
        const sipResponse = await api.get('/api/sip/configuration')
        setSystemStats(prev => ({
          ...prev,
          sipStatus: sipResponse.data.success ? 'healthy' : 'unhealthy'
        }))
      } catch (e) {
        setSystemStats(prev => ({ ...prev, sipStatus: 'unhealthy' }))
      }
      
      // Check Knowledge Base status
      try {
        const kbResponse = await api.get('/api/sip/knowledge-stats')
        setSystemStats(prev => ({
          ...prev,
          knowledgeBaseStatus: kbResponse.data.success ? 'healthy' : 'unhealthy'
        }))
      } catch (e) {
        setSystemStats(prev => ({ ...prev, knowledgeBaseStatus: 'unhealthy' }))
      }
      
      // Check ALIA Kit status
      try {
        const aliaResponse = await api.get('/api/alia/status')
        setSystemStats(prev => ({
          ...prev,
          aliaKitStatus: aliaResponse.data.success ? 'healthy' : 'unhealthy'
        }))
      } catch (e) {
        setSystemStats(prev => ({ ...prev, aliaKitStatus: 'unhealthy' }))
      }
      
      // Check Voice Training status
      try {
        const trainingResponse = await api.get('/api/voicebots/trained')
        setSystemStats(prev => ({
          ...prev,
          voiceTrainingStatus: trainingResponse.data.success ? 'healthy' : 'unhealthy'
        }))
      } catch (e) {
        setSystemStats(prev => ({ ...prev, voiceTrainingStatus: 'unhealthy' }))
      }
      
    } catch (error) {
      console.error('Error fetching system status:', error)
      setSystemStats(prev => ({
        ...prev,
        apiStatus: 'error',
        databaseStatus: 'error'
      }))
    }
  }

  const stats = [
    {
      name: 'Voces Disponibles',
      value: voices.length,
      icon: Volume2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      change: '+2 esta semana',
      changeType: 'positive'
    },
    {
      name: 'Chatbots Activos',
      value: chatbots.length,
      icon: Bot,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      change: `+${Math.max(0, chatbots.length)} total`,
      changeType: 'positive'
    },
    {
      name: 'Voicebots Activos',
      value: voicebots.length,
      icon: Phone,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      change: `+${Math.max(0, voicebots.length)} total`,
      changeType: 'positive'
    },
    {
      name: 'Audios Generados',
      value: audioHistory.length,
      icon: Mic,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
      change: `+${Math.max(0, audioHistory.length)} total`,
      changeType: 'positive'
    },
    {
      name: 'Estado del Sistema',
      value: systemStats.apiStatus === 'healthy' ? 'Operativo' : 'Error',
      icon: Activity,
      color: systemStats.apiStatus === 'healthy' ? 'text-green-600' : 'text-red-600',
      bgColor: systemStats.apiStatus === 'healthy' ? 'bg-green-100' : 'bg-red-100',
      change: systemStats.uptime,
      changeType: 'neutral'
    }
  ]

  const recentActivity = [
    {
      id: 1,
      type: 'voice_generation',
      message: 'Audio generado: "Bon dia, com estàs?"',
      timestamp: 'hace 5 minutos',
      icon: Mic,
      color: 'text-blue-600'
    },
    {
      id: 2,
      type: 'chatbot_created',
      message: 'Nuevo chatbot creado: "Assistent Virtual"',
      timestamp: 'hace 1 hora',
      icon: Bot,
      color: 'text-green-600'
    },
    {
      id: 3,
      type: 'voice_uploaded',
      message: 'Nueva voz importada: "Voz Masculina CA"',
      timestamp: 'hace 2 horas',
      icon: Volume2,
      color: 'text-purple-600'
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Bienvenido a VeuPlus. Gestiona tus voces, chatbots y síntesis de audio.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="bg-white border border-neutral-200 rounded-2xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <p className="text-sm font-semibold text-neutral-800 uppercase tracking-wide">Comença aquí</p>
          <p className="text-sm text-neutral-600">
            Configura en quatre passos l’organització, canals i el primer agent pilot.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/onboarding" className="btn-primary inline-flex items-center gap-2">
            <Rocket className="w-4 h-4" />
            Obrir wizard d’onboarding
          </Link>
          <Link to="/docs" className="btn-secondary text-sm">
            Llegir documentació
          </Link>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <div key={stat.name} className="card animate-fade-in">
              <div className="flex items-center">
                <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                  <Icon className={`w-6 h-6 ${stat.color}`} />
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                  <div className="flex items-baseline">
                    <p className="text-2xl font-semibold text-gray-900">
                      {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
                    </p>
                    <p className={`ml-2 text-sm ${
                      stat.changeType === 'positive' ? 'text-green-600' : 
                      stat.changeType === 'negative' ? 'text-red-600' : 
                      'text-gray-500'
                    }`}>
                      {stat.change}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <div className="lg:col-span-2">
          <div className="card">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-semibold text-gray-900">Actividad Reciente</h2>
              <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                Ver todo
              </button>
            </div>
            <div className="space-y-4">
              {recentActivity.map((activity) => {
                const Icon = activity.icon
                return (
                  <div key={activity.id} className="flex items-center space-x-4 animate-slide-up">
                    <div className="flex-shrink-0">
                      <Icon className={`w-5 h-5 ${activity.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-900">{activity.message}</p>
                      <p className="text-sm text-gray-500">{activity.timestamp}</p>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Accions ràpides</h2>
            <div className="space-y-3">
              <Link
                to="/sandbox"
                className="w-full flex items-center justify-center px-4 py-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors"
              >
                <Headphones className="w-5 h-5 mr-2 text-primary-600" />
                <span className="text-sm font-medium">Obrir Live Sandbox</span>
              </Link>
              <Link
                to="/chatbots"
                className="w-full flex items-center justify-center px-4 py-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors"
              >
                <Bot className="w-5 h-5 mr-2 text-emerald-600" />
                <span className="text-sm font-medium">Crear chatbot</span>
              </Link>
              <Link
                to="/voices"
                className="w-full flex items-center justify-center px-4 py-3 border border-neutral-200 rounded-lg hover:bg-neutral-50 transition-colors"
              >
                <Volume2 className="w-5 h-5 mr-2 text-purple-600" />
                <span className="text-sm font-medium">Importar veu</span>
              </Link>
            </div>
          </div>

          {/* System Status */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Estado del Sistema</h2>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">API Status</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  systemStats.apiStatus === 'healthy' 
                    ? 'bg-green-100 text-green-800' 
                    : systemStats.apiStatus === 'checking'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-red-100 text-red-800'
                }`}>
                  {systemStats.apiStatus === 'healthy' ? 'Healthy' : 
                   systemStats.apiStatus === 'checking' ? 'Checking...' : 'Error'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Base de Datos</span>
                <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                  systemStats.databaseStatus === 'connected' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {systemStats.databaseStatus === 'connected' ? 'Conectada' : 'Error'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Motor TTS</span>
                <span className="text-sm font-medium text-gray-900">
                  {systemStats.ttsEngine === 'unknown' ? 'Cargando...' : systemStats.ttsEngine}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Voces Catalanas</span>
                <span className="text-sm font-medium text-gray-900">
                  {voices.filter(v => v.language === 'ca').length} disponibles
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Total Bots</span>
                <span className="text-sm font-medium text-gray-900">
                  {chatbots.length + voicebots.length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Loading States */}
      {(voiceLoading || chatbotLoading) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-3">
            <div className="spinner"></div>
            <span className="text-gray-600">Cargando datos...</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
