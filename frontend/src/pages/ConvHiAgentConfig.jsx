import React, { useState, useEffect } from 'react'
import {
  Bot,
  Mic,
  BookOpen,
  Settings,
  Activity,
  TestTube,
  CheckCircle2,
  XCircle,
  Upload,
  Play,
  RefreshCw,
  Search,
  Download,
  Eye,
  Edit,
  Trash2,
  Plus,
  Phone,
  Radio,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ConvHiAgentConfig = () => {
  const [agentId, setAgentId] = useState('')
  const [agent, setAgent] = useState(null)
  const [activeTab, setActiveTab] = useState('asr')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  // ASR State
  const [asrEnabled, setAsrEnabled] = useState(false)
  const [asrLanguage, setAsrLanguage] = useState('auto')
  const [asrTranscriptions, setAsrTranscriptions] = useState([])
  const [testAudio, setTestAudio] = useState(null)
  const [transcriptionResult, setTranscriptionResult] = useState(null)

  // Knowledge Base State
  const [knowledgeItems, setKnowledgeItems] = useState([])
  const [uploadingDoc, setUploadingDoc] = useState(false)

  // LLM State
  const [llmProvider, setLlmProvider] = useState('openai')
  const [llmModel, setLlmModel] = useState('gpt-4o-mini')
  const [apiKey, setApiKey] = useState('')
  const [connectionStatus, setConnectionStatus] = useState(null)
  const [testingConnection, setTestingConnection] = useState(false)

  // Monitoring State
  const [monitoringEnabled, setMonitoringEnabled] = useState(false)
  const [metrics, setMetrics] = useState({})

  // ⭐ NOU: SIP & WebRTC per aquest agent
  const [sipTrunk, setSipTrunk] = useState(null)
  const [webrtcConfig, setWebrtcConfig] = useState(null)

  useEffect(() => {
    const pathAgentId = window.location.pathname.split('/').pop()
    if (pathAgentId && pathAgentId !== 'config') {
      setAgentId(pathAgentId)
      loadAgent(pathAgentId)
    }
  }, [])

  const loadAgent = async (id) => {
    try {
      const response = await api.get(`/api/convhi/agents/${id}`)
      const agentData = response.data.agent || response.data
      setAgent(agentData)
      setAsrEnabled(agentData.asr_enabled || false)
      setAsrLanguage(agentData.language || 'ca')
      setLlmProvider(agentData.llm_provider || 'openai')
      setLlmModel(agentData.llm_model || 'gpt-4o-mini')
      setMonitoringEnabled(agentData.monitoring_enabled || false)
      
      // ⭐ NOU: Carregar config SIP/WebRTC d'aquest agent
      await loadSIPConfig(id)
      await loadWebRTCConfig(id)
      await loadKnowledgeItems(id)
      await loadMetrics(id)
      
    } catch (error) {
      console.error('Error loading agent:', error)
      toast.error('Error carregant agent')
    } finally {
      setLoading(false)
    }
  }

  const loadSIPConfig = async (agentId) => {
    try {
      // Buscar si aquest agent té trunk SIP
      const response = await api.get('/api/convhi/sip/trunks')
      const trunks = response.data.trunks || []
      const agentTrunk = trunks.find(t => t.agent_id === agentId)
      setSipTrunk(agentTrunk || null)
    } catch (error) {
      console.error('Error loading SIP config:', error)
    }
  }

  const loadWebRTCConfig = async (agentId) => {
    try {
      // Config WebRTC per agent
      const response = await api.get('/api/convhi/webrtc/config')
      setWebrtcConfig(response.data)
    } catch (error) {
      console.error('Error loading WebRTC config:', error)
    }
  }

  const loadKnowledgeItems = async (agentId) => {
    try {
      const response = await api.get(`/api/convhi/knowledge/agent/${agentId}`)
      const items = response.data.items || Object.values(response.data)
      setKnowledgeItems(items || [])
    } catch (error) {
      console.error('Error loading knowledge:', error)
      setKnowledgeItems([])
    }
  }

  const loadMetrics = async (agentId) => {
    try {
      const response = await api.get(`/api/convhi/agents/${agentId}/metrics`)
      setMetrics(response.data.metrics || {})
    } catch (error) {
      console.error('Error loading metrics:', error)
    }
  }

  // 🆕 NOU: Funcions Knowledge Base
  const handleUploadFile = async (file) => {
    setUploadingDoc(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('agent_id', agentId)
      
      await api.post('/api/convhi/knowledge/file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      toast.success('Document pujat correctament!')
      await loadKnowledgeItems(agentId)
    } catch (error) {
      toast.error('Error pujant document')
      console.error(error)
    } finally {
      setUploadingDoc(false)
    }
  }

  const handleAddURL = async (url) => {
    try {
      await api.post('/api/convhi/knowledge/url', {
        agent_id: agentId,
        url: url
      })
      toast.success('URL afegida correctament!')
      await loadKnowledgeItems(agentId)
    } catch (error) {
      toast.error('Error afegint URL')
    }
  }

  const handleDownloadTranscription = async (transcriptionId) => {
    try {
      const response = await api.get(`/api/convhi/agents/${agentId}/asr/transcriptions/${transcriptionId}`, {
        responseType: 'blob'
      })
      
      const blob = new Blob([response.data], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `transcription_${transcriptionId}.txt`
      link.click()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      toast.error('Error descarregant transcripció')
    }
  }

  const saveConfig = async () => {
    try {
      setSubmitting(true)
      await api.put(`/api/convhi/agents/${agentId}`, {
        asr_enabled: asrEnabled,
        asr_language: asrLanguage,
        llm_provider: llmProvider,
        llm_model: llmModel,
        api_key: apiKey,
        monitoring_enabled: monitoringEnabled
      })
      
      toast.success('Configuració desada')
      
    } catch (error) {
      console.error('Error saving config:', error)
      toast.error('Error desant configuració')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-3 text-neutral-600">
          <RefreshCw className="w-5 h-5 animate-spin" />
          Carregant configuració...
        </div>
      </div>
    )
  }

  if (!agent) {
    return (
      <div className="text-center py-20">
        <p className="text-neutral-600">Agent no trobat</p>
      </div>
    )
  }

  const tabs = [
    { id: 'asr', label: 'ASR', icon: Mic },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen },
    { id: 'llm', label: 'LLM', icon: Bot },
    { id: 'monitoring', label: 'Monitoring', icon: Activity },
    { id: 'sip', label: 'SIP', icon: Phone },
    { id: 'webrtc', label: 'WebRTC', icon: Radio },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-2">
            <Bot className="w-8 h-8 text-primary-500" />
            {agent.name} - Configuració
          </h1>
          <p className="text-sm text-neutral-600 mt-1">
            {agent.description}
          </p>
        </div>
        <button
          onClick={saveConfig}
          disabled={submitting}
          className="btn-primary inline-flex items-center gap-2"
        >
          {submitting ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
          Desar Configuració
        </button>
      </div>

      {/* Tabs */}
      <div className="border-b border-neutral-200 overflow-x-auto">
        <div className="flex gap-1 min-w-fit">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition whitespace-nowrap ${
                  isActive
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-neutral-600 hover:text-neutral-900'
                }`}
              >
                <Icon className="w-5 h-5" />
                {tab.label}
              </button>
            )
          })}
        </div>
      </div>

      {/* Tab Content */}
      <div className="card">
        {activeTab === 'asr' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-neutral-900">Configuració ASR</h2>
            
            <div className="flex items-center justify-between p-4 bg-neutral-50 rounded-lg">
              <div>
                <h3 className="font-semibold text-neutral-900">Activar ASR</h3>
                <p className="text-sm text-neutral-600">Transcripció automàtica d'àudio a text</p>
              </div>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={asrEnabled}
                  onChange={(e) => setAsrEnabled(e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-14 h-7 bg-neutral-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-primary-600"></div>
              </label>
            </div>

            <div>
              <label className="block text-sm font-semibold text-neutral-900 mb-2">Idioma ASR</label>
              <select
                value={asrLanguage}
                onChange={(e) => setAsrLanguage(e.target.value)}
                className="input-field"
              >
                <option value="auto">Detectar automàticament</option>
                <option value="ca">Català</option>
                <option value="es">Castellà</option>
                <option value="en">Anglès</option>
                <option value="fr">Francès</option>
              </select>
            </div>

            <div className="border border-neutral-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <TestTube className="w-5 h-5 text-primary-500" />
                Provar ASR
              </h3>
              
              <div className="space-y-4">
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setTestAudio(e.target.files[0])}
                  className="input-field"
                />
                
                <button
                  onClick={() => testAudio && toast.success('Test ASR (funcionalitat en desenvolupament)')}
                  disabled={!testAudio}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Transcriure Àudio
                </button>

                {transcriptionResult && (
                  <div className="border border-neutral-200 rounded p-4 bg-neutral-50">
                    <p className="text-sm text-neutral-600 mb-2">Resultat:</p>
                    <p className="text-sm text-neutral-900">{transcriptionResult}</p>
                    <button
                      onClick={() => {
                        const blob = new Blob([transcriptionResult], { type: 'text/plain' })
                        const url = window.URL.createObjectURL(blob)
                        const link = document.createElement('a')
                        link.href = url
                        link.download = `transcripcion_${Date.now()}.txt`
                        link.click()
                        window.URL.revokeObjectURL(url)
                      }}
                      className="mt-2 btn-secondary inline-flex items-center gap-2 text-sm"
                    >
                      <Download className="w-4 h-4" />
                      Descarregar Transcripció
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Transcripcions Anteriors */}
            <div className="border border-neutral-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <Eye className="w-5 h-5 text-primary-500" />
                Transcripcions Anteriors
              </h3>
              
              {asrTranscriptions.length === 0 ? (
                <p className="text-sm text-neutral-500">No hi ha transcripcions encara</p>
              ) : (
                <div className="space-y-2">
                  {asrTranscriptions.map((transcription, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 bg-neutral-50 rounded">
                      <div>
                        <p className="text-sm font-medium text-neutral-900">{transcription.text}</p>
                        <p className="text-xs text-neutral-500">{transcription.timestamp}</p>
                      </div>
                      <button
                        onClick={() => handleDownloadTranscription(transcription.id)}
                        className="btn-secondary text-sm inline-flex items-center gap-1"
                      >
                        <Download className="w-3 h-3" />
                        Descarregar
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'knowledge' && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-semibold text-neutral-900 mb-2">Knowledge Base</h2>
              <p className="text-sm text-neutral-600">
                Puja documents, afegeix URLs o escriu text directament per millorar les respostes de l'agent
              </p>
            </div>

            {/* Upload Documents */}
            <div className="border border-neutral-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-primary-500" />
                Pujar Documents
              </h3>
              
              <div className="space-y-4">
                <div className="border-2 border-dashed border-neutral-300 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    id="file-upload"
                    accept=".pdf,.txt,.doc,.docx,.md"
                    onChange={(e) => e.target.files[0] && handleUploadFile(e.target.files[0])}
                    className="hidden"
                    disabled={uploadingDoc}
                  />
                  <label
                    htmlFor="file-upload"
                    className="cursor-pointer inline-flex items-center gap-2 btn-secondary"
                  >
                    {uploadingDoc ? (
                      <>
                        <RefreshCw className="w-4 h-4 animate-spin" />
                        Pujant...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Seleccionar Document
                      </>
                    )}
                  </label>
                  <p className="text-xs text-neutral-500 mt-2">
                    Suporta PDF, TXT, DOC, DOCX, MD
                  </p>
                </div>
              </div>
            </div>

            {/* Add URL */}
            <div className="border border-neutral-200 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
                <Globe className="w-5 h-5 text-primary-500" />
                Afegir URL
              </h3>
              
              <form
                onSubmit={(e) => {
                  e.preventDefault()
                  const form = e.target
                  const urlInput = form.querySelector('input[type="url"]')
                  if (urlInput?.value) {
                    handleAddURL(urlInput.value)
                    urlInput.value = ''
                  }
                }}
                className="flex gap-2"
              >
                <input
                  type="url"
                  placeholder="https://example.com/document"
                  className="input-field flex-1"
                  required
                />
                <button type="submit" className="btn-primary">
                  <Plus className="w-4 h-4" />
                </button>
              </form>
            </div>

            {/* Knowledge Items List */}
            <div className="border border-neutral-200 rounded-lg">
              <div className="p-4 border-b border-neutral-200">
                <h3 className="font-semibold text-neutral-900">Documents carregats ({knowledgeItems.length})</h3>
              </div>
              
              <div className="divide-y divide-neutral-200">
                {knowledgeItems.length === 0 ? (
                  <div className="p-8 text-center text-neutral-500">
                    No hi ha documents encara. Puja un document o afegeix una URL.
                  </div>
                ) : (
                  knowledgeItems.map((item, idx) => (
                    <div key={idx} className="p-4 flex items-center justify-between hover:bg-neutral-50">
                      <div className="flex items-center gap-3">
                        <BookOpen className="w-5 h-5 text-neutral-400" />
                        <div>
                          <p className="font-medium text-neutral-900">{item.name || item.title}</p>
                          <p className="text-sm text-neutral-500">{item.type || 'Document'}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => item.id && toast.info('Funció d\'eliminar en desenvolupament')}
                        className="text-red-500 hover:text-red-700"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'llm' && (
          <div className="p-8 text-center">
            <p className="text-neutral-500">Configuració LLM (implementació en curs)</p>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <div className="p-8 text-center">
            <p className="text-neutral-500">Monitoring (implementació en curs)</p>
          </div>
        )}

        {activeTab === 'sip' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-neutral-900">SIP Trunking per aquest Agent</h2>
            
            {sipTrunk ? (
              <div className="border border-neutral-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="font-semibold text-neutral-900">Trunk Configurat</h3>
                  <button className="btn-secondary inline-flex items-center gap-2">
                    <Edit className="w-4 h-4" />
                    Editar
                  </button>
                </div>
                <div className="space-y-2 text-sm">
                  <p><strong>Número:</strong> {sipTrunk.phone_number}</p>
                  <p><strong>Outbound:</strong> {sipTrunk.outbound_address}</p>
                  <p><strong>Transport:</strong> {sipTrunk.transport_type}</p>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-neutral-300 rounded-lg p-8 text-center">
                <Phone className="w-12 h-12 mx-auto text-neutral-400 mb-4" />
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">No hi ha SIP Trunk configurat</h3>
                <p className="text-sm text-neutral-600 mb-4">
                  Configura un trunk SIP per aquest agent
                </p>
                <button className="btn-primary inline-flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Configurar SIP Trunk
                </button>
              </div>
            )}
          </div>
        )}

        {activeTab === 'webrtc' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-neutral-900">WebRTC per aquest Agent</h2>
            
            {webrtcConfig ? (
              <div className="border border-neutral-200 rounded-lg p-6">
                <h3 className="font-semibold text-neutral-900 mb-4">Configuració WebRTC</h3>
                <div className="space-y-2 text-sm">
                  <p><strong>STUN Servers:</strong> {webrtcConfig.stun_servers?.length || 0}</p>
                  <p><strong>TURN Servers:</strong> {webrtcConfig.turn_servers?.length || 0}</p>
                </div>
              </div>
            ) : (
              <div className="border-2 border-dashed border-neutral-300 rounded-lg p-8 text-center">
                <Radio className="w-12 h-12 mx-auto text-neutral-400 mb-4" />
                <h3 className="text-lg font-semibold text-neutral-900 mb-2">No hi ha WebRTC configurat</h3>
                <p className="text-sm text-neutral-600 mb-4">
                  Configura WebRTC per aquest agent
                </p>
                <button className="btn-primary inline-flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Configurar WebRTC
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default ConvHiAgentConfig
