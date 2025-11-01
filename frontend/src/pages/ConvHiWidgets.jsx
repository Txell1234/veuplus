import React, { useEffect, useState } from 'react'
import {
  Bot,
  Code,
  Copy,
  Eye,
  Globe,
  Loader2,
  Palette,
  Settings,
  Share2,
  Smartphone,
  Tablet,
  Monitor,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Download,
  Upload,
  Trash2,
  Edit3,
  Save,
  X,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ConvHiWidgets = () => {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [widgetConfig, setWidgetConfig] = useState(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [previewMode, setPreviewMode] = useState('desktop') // desktop, tablet, mobile
  const [showEmbedCode, setShowEmbedCode] = useState(false)
  const [embedCode, setEmbedCode] = useState('')
  const [previewUrl, setPreviewUrl] = useState('')

  // Configuración del widget
  const [config, setConfig] = useState({
    variant: 'compact',
    mode: 'voice_only',
    avatar_image_url: '',
    avatar_orb_color_1: '#6DB035',
    avatar_orb_color_2: '#F5CABB',
    primary_color: '#3B82F6',
    secondary_color: '#1E40AF',
    action_text: 'Need assistance?',
    start_call_text: 'Begin conversation',
    end_call_text: 'End call',
    expand_text: 'Open chat',
    listening_text: 'Listening...',
    speaking_text: 'Assistant speaking',
    feedback_enabled: true,
    terms_enabled: false,
    terms_content: '',
    mute_enabled: true,
    language: 'ca',
    dynamic_variables: {},
    overrides: {},
  })

  useEffect(() => {
    loadAgents()
  }, [])

  useEffect(() => {
    if (selectedAgent) {
      loadWidgetConfig(selectedAgent)
    }
  }, [selectedAgent])

  const loadAgents = async () => {
    try {
      const response = await api.get('/api/convhi/agents')
      setAgents(response.data.agents || [])
      if (response.data.agents?.length > 0) {
        setSelectedAgent(response.data.agents[0].id)
      }
    } catch (error) {
      console.error('Error carregant agents:', error)
      toast.error('No s\'han pogut carregar els agents')
    }
  }

  const loadWidgetConfig = async (agentId) => {
    try {
      setLoading(true)
      const response = await api.get(`/api/convhi/widgets/config/${agentId}`)
      
      if (response.data.success && response.data.config) {
        setWidgetConfig(response.data.config)
        setConfig(prev => ({ ...prev, ...response.data.config }))
      } else {
        // Crear configuració per defecte
        setWidgetConfig(null)
        setConfig(prev => ({ ...prev, agent_id: agentId }))
      }
    } catch (error) {
      console.error('Error carregant configuració:', error)
      setWidgetConfig(null)
    } finally {
      setLoading(false)
    }
  }

  const saveWidgetConfig = async () => {
    if (!selectedAgent) {
      toast.error('Selecciona un agent primer')
      return
    }

    try {
      setSaving(true)
      const configData = {
        ...config,
        agent_id: selectedAgent,
      }

      const response = await api.post('/api/convhi/widgets/config', configData)
      
      if (response.data.success) {
        setWidgetConfig(response.data.config)
        toast.success('Configuració guardada correctament!')
      }
    } catch (error) {
      console.error('Error guardant configuració:', error)
      toast.error('Error guardant configuració')
    } finally {
      setSaving(false)
    }
  }

  const generateEmbedCode = async () => {
    if (!selectedAgent) {
      toast.error('Selecciona un agent primer')
      return
    }

    try {
      setLoading(true)
      const response = await api.post('/api/convhi/widgets/embed', {
        agent_id: selectedAgent,
        config: config,
        domain: window.location.origin,
      })

      if (response.data.success) {
        setEmbedCode(response.data.embed_code)
        setPreviewUrl(response.data.preview_url)
        setShowEmbedCode(true)
        toast.success('Codi d\'integració generat!')
      }
    } catch (error) {
      console.error('Error generant codi:', error)
      toast.error('Error generant codi d\'integració')
    } finally {
      setLoading(false)
    }
  }

  const copyEmbedCode = () => {
    navigator.clipboard.writeText(embedCode)
    toast.success('Codi copiat al portapapers!')
  }

  const updateConfig = (key, value) => {
    setConfig(prev => ({ ...prev, [key]: value }))
  }

  const updateDynamicVariable = (key, value) => {
    setConfig(prev => ({
      ...prev,
      dynamic_variables: { ...prev.dynamic_variables, [key]: value }
    }))
  }

  const removeDynamicVariable = (key) => {
    setConfig(prev => {
      const newVars = { ...prev.dynamic_variables }
      delete newVars[key]
      return { ...prev, dynamic_variables: newVars }
    })
  }

  const addDynamicVariable = () => {
    const key = prompt('Nom de la variable:')
    if (key) {
      updateDynamicVariable(key, '')
    }
  }

  const renderPreview = () => {
    const previewStyles = {
      desktop: { width: '100%', height: '600px' },
      tablet: { width: '768px', height: '600px', margin: '0 auto' },
      mobile: { width: '375px', height: '600px', margin: '0 auto' }
    }

    return (
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-neutral-900">Vista prèvia</h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPreviewMode('desktop')}
              className={`p-2 rounded ${previewMode === 'desktop' ? 'bg-primary-100 text-primary-700' : 'text-neutral-500'}`}
            >
              <Monitor className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPreviewMode('tablet')}
              className={`p-2 rounded ${previewMode === 'tablet' ? 'bg-primary-100 text-primary-700' : 'text-neutral-500'}`}
            >
              <Tablet className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPreviewMode('mobile')}
              className={`p-2 rounded ${previewMode === 'mobile' ? 'bg-primary-100 text-primary-700' : 'text-neutral-500'}`}
            >
              <Smartphone className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="border border-neutral-200 rounded-lg overflow-hidden" style={previewStyles[previewMode]}>
          <div className="bg-neutral-50 p-4 border-b border-neutral-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div
                  className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
                  style={{
                    background: config.avatar_image_url 
                      ? `url(${config.avatar_image_url})` 
                      : `linear-gradient(45deg, ${config.avatar_orb_color_1}, ${config.avatar_orb_color_2})`
                  }}
                >
                  {!config.avatar_image_url && '🤖'}
                </div>
                <div>
                  <p className="font-semibold text-neutral-900">{config.action_text}</p>
                  <p className="text-sm text-neutral-600">Agent: {selectedAgent}</p>
                </div>
              </div>
              <button
                className="px-4 py-2 rounded-lg text-white font-medium"
                style={{ backgroundColor: config.primary_color }}
              >
                {config.start_call_text}
              </button>
            </div>
          </div>

          <div className="p-4 bg-white">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500"></div>
                <span className="text-sm text-neutral-600">Widget actiu</span>
              </div>
              <div className="text-sm text-neutral-500">
                <p><strong>Mode:</strong> {config.mode}</p>
                <p><strong>Variant:</strong> {config.variant}</p>
                <p><strong>Idioma:</strong> {config.language}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  const renderConfiguration = () => (
    <div className="space-y-6">
      {/* Configuració bàsica */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Settings className="w-5 h-5 text-primary-500" />
          Configuració bàsica
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Variant</label>
            <select
              className="input-field"
              value={config.variant}
              onChange={(e) => updateConfig('variant', e.target.value)}
            >
              <option value="compact">Compact</option>
              <option value="expanded">Expanded</option>
              <option value="fullscreen">Fullscreen</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Mode</label>
            <select
              className="input-field"
              value={config.mode}
              onChange={(e) => updateConfig('mode', e.target.value)}
            >
              <option value="voice_only">Només veu</option>
              <option value="voice_text">Veu + text</option>
              <option value="chat_only">Només chat</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Idioma</label>
            <select
              className="input-field"
              value={config.language}
              onChange={(e) => updateConfig('language', e.target.value)}
            >
              <option value="ca">Català</option>
              <option value="es">Castellà</option>
              <option value="en">Anglès</option>
              <option value="fr">Francès</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">URL d'avatar (opcional)</label>
            <input
              type="url"
              className="input-field"
              placeholder="https://example.com/avatar.png"
              value={config.avatar_image_url}
              onChange={(e) => updateConfig('avatar_image_url', e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Personalització visual */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Palette className="w-5 h-5 text-primary-500" />
          Personalització visual
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Color primari</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                className="w-10 h-10 rounded border border-neutral-300"
                value={config.primary_color}
                onChange={(e) => updateConfig('primary_color', e.target.value)}
              />
              <input
                type="text"
                className="input-field flex-1"
                value={config.primary_color}
                onChange={(e) => updateConfig('primary_color', e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Color secundari</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                className="w-10 h-10 rounded border border-neutral-300"
                value={config.secondary_color}
                onChange={(e) => updateConfig('secondary_color', e.target.value)}
              />
              <input
                type="text"
                className="input-field flex-1"
                value={config.secondary_color}
                onChange={(e) => updateConfig('secondary_color', e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Color avatar 1</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                className="w-10 h-10 rounded border border-neutral-300"
                value={config.avatar_orb_color_1}
                onChange={(e) => updateConfig('avatar_orb_color_1', e.target.value)}
              />
              <input
                type="text"
                className="input-field flex-1"
                value={config.avatar_orb_color_1}
                onChange={(e) => updateConfig('avatar_orb_color_1', e.target.value)}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Color avatar 2</label>
            <div className="flex items-center gap-2">
              <input
                type="color"
                className="w-10 h-10 rounded border border-neutral-300"
                value={config.avatar_orb_color_2}
                onChange={(e) => updateConfig('avatar_orb_color_2', e.target.value)}
              />
              <input
                type="text"
                className="input-field flex-1"
                value={config.avatar_orb_color_2}
                onChange={(e) => updateConfig('avatar_orb_color_2', e.target.value)}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Textos personalitzats */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Textos personalitzats</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Text d'acció</label>
            <input
              className="input-field"
              value={config.action_text}
              onChange={(e) => updateConfig('action_text', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Text iniciar trucada</label>
            <input
              className="input-field"
              value={config.start_call_text}
              onChange={(e) => updateConfig('start_call_text', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Text finalitzar trucada</label>
            <input
              className="input-field"
              value={config.end_call_text}
              onChange={(e) => updateConfig('end_call_text', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Text expandir</label>
            <input
              className="input-field"
              value={config.expand_text}
              onChange={(e) => updateConfig('expand_text', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Text escoltant</label>
            <input
              className="input-field"
              value={config.listening_text}
              onChange={(e) => updateConfig('listening_text', e.target.value)}
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Text parlant</label>
            <input
              className="input-field"
              value={config.speaking_text}
              onChange={(e) => updateConfig('speaking_text', e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Variables dinàmiques */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
          <Code className="w-5 h-5 text-primary-500" />
          Variables dinàmiques
        </h3>
        
        <div className="space-y-3">
          {Object.entries(config.dynamic_variables).map(([key, value]) => (
            <div key={key} className="flex items-center gap-2">
              <input
                className="input-field flex-1"
                placeholder="Nom de la variable"
                value={key}
                onChange={(e) => {
                  const newKey = e.target.value
                  if (newKey !== key) {
                    const newVars = { ...config.dynamic_variables }
                    delete newVars[key]
                    newVars[newKey] = value
                    setConfig(prev => ({ ...prev, dynamic_variables: newVars }))
                  }
                }}
              />
              <input
                className="input-field flex-1"
                placeholder="Valor"
                value={value}
                onChange={(e) => updateDynamicVariable(key, e.target.value)}
              />
              <button
                onClick={() => removeDynamicVariable(key)}
                className="p-2 text-red-500 hover:bg-red-50 rounded"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          ))}
          
          <button
            onClick={addDynamicVariable}
            className="btn-secondary text-sm"
          >
            Afegir variable
          </button>
        </div>
      </div>

      {/* Funcionalitats */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-4">Funcionalitats</h3>
        
        <div className="space-y-3">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.feedback_enabled}
              onChange={(e) => updateConfig('feedback_enabled', e.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">Activar feedback</span>
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.terms_enabled}
              onChange={(e) => updateConfig('terms_enabled', e.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">Mostrar termes i condicions</span>
          </label>

          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={config.mute_enabled}
              onChange={(e) => updateConfig('mute_enabled', e.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">Permetre silenciar</span>
          </label>
        </div>

        {config.terms_enabled && (
          <div className="mt-4">
            <label className="block text-sm font-semibold text-neutral-800 mb-1">Contingut dels termes</label>
            <textarea
              className="input-field min-h-[100px]"
              placeholder="Introdueix els termes i condicions..."
              value={config.terms_content}
              onChange={(e) => updateConfig('terms_content', e.target.value)}
            />
          </div>
        )}
      </div>
    </div>
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <Globe className="w-6 h-6 text-primary-500" />
            ConvHi Widgets
          </h1>
          <p className="text-sm text-neutral-600">
            Configura i personalitza widgets per integrar agents ConvHi en qualsevol lloc web.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={generateEmbedCode}
            disabled={!selectedAgent || loading}
            className="btn-primary inline-flex items-center gap-2"
          >
            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Code className="w-4 h-4" />}
            Generar codi
          </button>
          
          <button
            onClick={saveWidgetConfig}
            disabled={!selectedAgent || saving}
            className="btn-secondary inline-flex items-center gap-2"
          >
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
            Guardar
          </button>
        </div>
      </div>

      {/* Selecció d'agent */}
      <div className="card">
        <h3 className="text-lg font-semibold text-neutral-900 mb-3">Seleccionar agent</h3>
        <select
          className="input-field"
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
        >
          <option value="">Selecciona un agent...</option>
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name || agent.id} - {agent.voice_system}
            </option>
          ))}
        </select>
      </div>

      {selectedAgent && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Configuració */}
          <div>
            {renderConfiguration()}
          </div>

          {/* Vista prèvia */}
          <div>
            {renderPreview()}
          </div>
        </div>
      )}

      {/* Modal de codi d'integració */}
      {showEmbedCode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="flex items-center justify-between p-6 border-b border-neutral-200">
              <h3 className="text-lg font-semibold text-neutral-900">Codi d'integració</h3>
              <button
                onClick={() => setShowEmbedCode(false)}
                className="p-2 text-neutral-500 hover:text-neutral-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="flex items-center gap-3">
                <button
                  onClick={copyEmbedCode}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  <Copy className="w-4 h-4" />
                  Copiar codi
                </button>
                
                <a
                  href={previewUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary inline-flex items-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Veure preview
                </a>
              </div>
              
              <div className="bg-neutral-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-neutral-800 mb-2">Codi HTML:</h4>
                <pre className="text-xs text-neutral-700 overflow-x-auto whitespace-pre-wrap">
                  {embedCode}
                </pre>
              </div>
              
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="text-sm font-semibold text-blue-800 mb-2">Instruccions:</h4>
                <ol className="text-sm text-blue-700 list-decimal list-inside space-y-1">
                  <li>Copia el codi HTML anterior</li>
                  <li>Enganxa'l al final del teu lloc web, abans del tag &lt;/body&gt;</li>
                  <li>El widget apareixerà automàticament</li>
                  <li>Pots personalitzar la posició amb CSS</li>
                </ol>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ConvHiWidgets


