import React, { useEffect, useMemo, useState } from 'react'
import {
  BookOpen,
  Link2,
  Loader2,
  Plus,
  RefreshCw,
  Trash2,
  BarChart3,
  Settings,
  CheckCircle2,
  AlertCircle,
  Clock,
  FileText,
  Database,
  Zap,
  TrendingUp,
  Activity,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const KnowledgePanel = () => {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('')

  const [knowledgeItems, setKnowledgeItems] = useState([])
  const [connectors, setConnectors] = useState([])
  const [jobs, setJobs] = useState([])

  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  const [textTitle, setTextTitle] = useState('')
  const [textContent, setTextContent] = useState('')

  const [urlTitle, setUrlTitle] = useState('')
  const [urlValue, setUrlValue] = useState('')

  const [connectorName, setConnectorName] = useState('')
  const [connectorType, setConnectorType] = useState('notion')
  
  // RAG Configuration
  const [ragConfig, setRagConfig] = useState({
    enabled: true,
    top_k: 5,
    similarity_threshold: 0.7,
    max_tokens: 1000,
    chunk_size: 500,
    chunk_overlap: 50
  })
  
  // Statistics
  const [stats, setStats] = useState({
    total_items: 0,
    total_jobs: 0,
    successful_jobs: 0,
    failed_jobs: 0,
    avg_processing_time: 0,
    last_indexed: null
  })

  useEffect(() => {
    const loadAgents = async () => {
      try {
        const response = await api.get('/api/convhi/agents')
        const agentList = response.data.agents || []
        setAgents(agentList)
        if (agentList.length > 0) {
          setSelectedAgent(agentList[0].id)
        }
      } catch (error) {
        console.error('Error carregant agents:', error)
        toast.error('No s’han pogut carregar els agents.')
      }
    }
    loadAgents()
  }, [])

  const fetchAllForAgent = async (agentId) => {
    try {
      setLoading(true)
      const [itemsRes, connectorsRes, jobsRes, statsRes] = await Promise.all([
        api.get(`/api/convhi/knowledge/agent/${agentId}`),
        api.get(`/api/convhi/knowledge/agent/${agentId}/connectors`).catch(() => ({
          data: { connectors: [] },
        })),
        api.get(`/api/convhi/knowledge/agent/${agentId}/jobs`).catch(() => ({
          data: { jobs: [] },
        })),
        api.get(`/api/convhi/knowledge/agent/${agentId}/stats`).catch(() => ({
          data: { stats: {} },
        })),
      ])
      setKnowledgeItems(itemsRes.data.knowledge_items || [])
      setConnectors(connectorsRes.data.connectors || [])
      setJobs(jobsRes.data.jobs || [])
      setStats(statsRes.data.stats || {})
    } catch (error) {
      console.error('Error carregant coneixement:', error)
      toast.error('No s’ha pogut obtenir el coneixement de l’agent.')
    } finally {
      setLoading(false)
    }
  }

  const refreshJobs = async () => {
    if (!selectedAgent) return
    try {
      const response = await api.get(`/api/convhi/knowledge/agent/${selectedAgent}/jobs`)
      setJobs(response.data.jobs || [])
    } catch (error) {
      console.error('Error actualitzant feines:', error)
    }
  }

  useEffect(() => {
    if (!selectedAgent) return
    fetchAllForAgent(selectedAgent)
    const interval = setInterval(refreshJobs, 5000)
    return () => clearInterval(interval)
  }, [selectedAgent])

  const handleTextIngest = async () => {
    if (!selectedAgent) {
      toast.error('Selecciona un agent.')
      return
    }
    if (!textContent.trim()) {
      toast.error('Introdueix el contingut a indexar.')
      return
    }
    try {
      setSubmitting(true)
      await api.post('/api/convhi/knowledge/jobs', {
        agent_id: selectedAgent,
        source_type: 'text',
        payload: {
          title: textTitle || 'Text manual',
          content: textContent,
        },
      })
      toast.success('Feina d’ingestió programada!')
      setTextTitle('')
      setTextContent('')
      refreshJobs()
    } catch (error) {
      console.error('Error creant feina de text:', error)
      toast.error('No s’ha pogut crear la feina.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleUrlIngest = async () => {
    if (!selectedAgent) {
      toast.error('Selecciona un agent.')
      return
    }
    if (!urlValue.trim()) {
      toast.error('Introdueix una URL.')
      return
    }
    try {
      setSubmitting(true)
      await api.post('/api/convhi/knowledge/jobs', {
        agent_id: selectedAgent,
        source_type: 'url',
        payload: {
          title: urlTitle,
          url: urlValue,
        },
      })
      toast.success('Feina d’indexació de URL creada!')
      setUrlTitle('')
      setUrlValue('')
      refreshJobs()
    } catch (error) {
      console.error('Error creant feina de URL:', error)
      toast.error('No s’ha pogut encolar la URL.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleAddConnector = async () => {
    if (!selectedAgent) {
      toast.error('Selecciona un agent.')
      return
    }
    if (!connectorName.trim()) {
      toast.error('Introdueix un nom per al connector.')
      return
    }
    try {
      setSubmitting(true)
      const response = await api.post('/api/convhi/knowledge/connectors', {
        agent_id: selectedAgent,
        name: connectorName,
        connector_type: connectorType,
        config: {},
      })
      toast.success('Connector afegit!')
      setConnectorName('')
      setConnectors((prev) => [...prev, response.data.connector])
    } catch (error) {
      console.error('Error afegint connector:', error)
      toast.error('No s’ha pogut afegir el connector.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleDeleteConnector = async (connectorId) => {
    if (!selectedAgent) return
    try {
      await api.delete(`/api/convhi/knowledge/agent/${selectedAgent}/connectors/${connectorId}`)
      setConnectors((prev) => prev.filter((c) => c.id !== connectorId))
      toast.success('Connector eliminat.')
    } catch (error) {
      console.error('Error eliminant connector:', error)
      toast.error('No s’ha pogut eliminar.')
    }
  }

  const handleSyncConnector = async (connectorId) => {
    if (!selectedAgent) return
    try {
      await api.post('/api/convhi/knowledge/jobs', {
        agent_id: selectedAgent,
        source_type: 'connector',
        payload: { connector_id: connectorId },
      })
      toast.success('Sincronització del connector en marxa.')
      refreshJobs()
    } catch (error) {
      console.error('Error sincronitzant connector:', error)
      toast.error('No s’ha pogut sincronitzar.')
    }
  }

  const updateRagConfig = async () => {
    if (!selectedAgent) return
    try {
      await api.put(`/api/convhi/knowledge/agent/${selectedAgent}/rag-config`, ragConfig)
      toast.success('Configuració RAG actualitzada!')
    } catch (error) {
      console.error('Error updating RAG config:', error)
      toast.error('Error actualitzant configuració RAG')
    }
  }

  const testRagQuery = async () => {
    if (!selectedAgent) return
    const testQuery = prompt('Introdueix una consulta de prova:')
    if (!testQuery) return
    
    try {
      const response = await api.post(`/api/convhi/knowledge/agent/${selectedAgent}/search`, {
        query: testQuery,
        top_k: ragConfig.top_k,
        similarity_threshold: ragConfig.similarity_threshold
      })
      
      const results = response.data.results || []
      if (results.length > 0) {
        alert(`Trobats ${results.length} resultats:\n\n${results.map(r => `- ${r.title} (${r.score.toFixed(3)})`).join('\n')}`)
      } else {
        alert('No s\'han trobat resultats per aquesta consulta.')
      }
    } catch (error) {
      console.error('Error testing RAG:', error)
      toast.error('Error provant consulta RAG')
    }
  }

  const filteredItems = useMemo(() => knowledgeItems.slice(0, 20), [knowledgeItems])

  if (agents.length === 0 && loading) {
    return (
      <div className="flex items-center justify-center py-20 text-neutral-500 gap-2">
        <Loader2 className="w-5 h-5 animate-spin" />
        Carregant…
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-primary-500" />
            Knowledge Base
          </h1>
          <p className="text-sm text-neutral-600">
            Gestiona textos, URLs i connectors assignats a cada agent ConvHi.
          </p>
        </div>
        <select
          className="input-field w-56"
          value={selectedAgent}
          onChange={(event) => setSelectedAgent(event.target.value)}
        >
          {agents.map((agent) => (
            <option key={agent.id} value={agent.id}>
              {agent.name || agent.id}
            </option>
          ))}
        </select>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="card space-y-3">
            <h2 className="text-lg font-semibold text-neutral-900">Afegir text manual</h2>
            <input
              className="input-field"
              placeholder="Títol (opcional)"
              value={textTitle}
              onChange={(event) => setTextTitle(event.target.value)}
            />
            <textarea
              className="input-field min-h-[140px]"
              placeholder="Contingut..."
              value={textContent}
              onChange={(event) => setTextContent(event.target.value)}
            />
            <button onClick={handleTextIngest} className="btn-primary inline-flex items-center gap-2">
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              Encolar text
            </button>
          </div>

          <div className="card space-y-3">
            <h2 className="text-lg font-semibold text-neutral-900">Afegir URL</h2>
            <input
              className="input-field"
              placeholder="Títol (opcional)"
              value={urlTitle}
              onChange={(event) => setUrlTitle(event.target.value)}
            />
            <input
              className="input-field"
              placeholder="https://..."
              value={urlValue}
              onChange={(event) => setUrlValue(event.target.value)}
            />
            <button onClick={handleUrlIngest} className="btn-primary inline-flex items-center gap-2">
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Link2 className="w-4 h-4" />}
              Encolar URL
            </button>
          </div>

          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-neutral-900">Coneixement indexat</h2>
              <span className="text-xs text-neutral-500">{knowledgeItems.length} elements</span>
            </div>
            {loading ? (
              <div className="flex items-center gap-2 text-sm text-neutral-500">
                <Loader2 className="w-4 h-4 animate-spin" />
                Carregant elements…
              </div>
            ) : filteredItems.length === 0 ? (
              <p className="text-sm text-neutral-500">Encara no hi ha coneixement per aquest agent.</p>
            ) : (
              <ul className="space-y-3">
                {filteredItems.map((item) => (
                  <li key={item.id} className="border border-neutral-200 rounded-lg p-3">
                    <p className="text-sm font-semibold text-neutral-900">{item.title}</p>
                    <p className="text-xs text-neutral-500">
                      {item.content_type} · {new Date(item.created_at).toLocaleString()}
                    </p>
                    <p className="mt-2 text-sm text-neutral-700 line-clamp-2">{item.content}</p>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-neutral-900">Connectors</h2>
              <span className="text-xs text-neutral-500">{connectors.length} configurats</span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <input
                className="input-field"
                placeholder="Nom del connector"
                value={connectorName}
                onChange={(event) => setConnectorName(event.target.value)}
              />
              <select
                className="input-field"
                value={connectorType}
                onChange={(event) => setConnectorType(event.target.value)}
              >
                <option value="notion">Notion</option>
                <option value="sharepoint">SharePoint</option>
                <option value="gmail">Gmail</option>
                <option value="custom">Custom</option>
              </select>
            </div>
            <button onClick={handleAddConnector} className="btn-primary inline-flex items-center gap-2">
              {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
              Afegir connector
            </button>

            {connectors.length === 0 ? (
              <p className="text-sm text-neutral-500">Cap connector configurat.</p>
            ) : (
              <div className="space-y-2">
                {connectors.map((connector) => (
                  <div key={connector.id} className="border border-neutral-200 rounded-lg p-3 text-sm">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-neutral-900">{connector.name}</p>
                        <p className="text-xs text-neutral-500">
                          {connector.connector_type} · {connector.status}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <button
                          onClick={() => handleSyncConnector(connector.id)}
                          className="text-xs text-primary-600 hover:underline inline-flex items-center gap-1"
                        >
                          <RefreshCw className="w-4 h-4" />
                          Sync
                        </button>
                        <button
                          onClick={() => handleDeleteConnector(connector.id)}
                          className="text-xs text-red-500 hover:underline inline-flex items-center gap-1"
                        >
                          <Trash2 className="w-4 h-4" />
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="card space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-neutral-900">Feines d'ingestió</h2>
              <div className="flex items-center gap-2">
                <span className="text-xs text-neutral-500">
                  {jobs.filter(j => j.status === 'processing').length} processant
                </span>
                <button onClick={refreshJobs} className="btn-secondary text-xs inline-flex items-center gap-2">
                  <RefreshCw className="w-3 h-3" />
                  Actualitzar
                </button>
              </div>
            </div>
            
            {jobs.length === 0 ? (
              <p className="text-sm text-neutral-500">Encara no hi ha feines programades.</p>
            ) : (
              <div className="space-y-2 max-h-64 overflow-y-auto">
                {jobs.map((job) => (
                  <div key={job.id} className="border border-neutral-200 rounded-lg p-3">
                    <div className="flex items-center justify-between text-sm mb-2">
                      <div className="flex items-center gap-2">
                        {job.status === 'processing' ? (
                          <Loader2 className="w-4 h-4 animate-spin text-blue-500" />
                        ) : job.status === 'completed' ? (
                          <CheckCircle2 className="w-4 h-4 text-green-500" />
                        ) : job.status === 'failed' ? (
                          <AlertCircle className="w-4 h-4 text-red-500" />
                        ) : (
                          <Clock className="w-4 h-4 text-neutral-500" />
                        )}
                        <span className="font-medium">
                          {job.source_type === 'text' ? 'Text manual' : 
                           job.source_type === 'url' ? 'URL' : 
                           job.source_type === 'connector' ? 'Connector' : job.source_type}
                        </span>
                        <span className="text-neutral-500">
                          · {new Date(job.created_at).toLocaleTimeString()}
                        </span>
                      </div>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          job.status === 'completed'
                            ? 'bg-emerald-100 text-emerald-700'
                            : job.status === 'processing'
                            ? 'bg-blue-100 text-blue-600'
                            : job.status === 'failed'
                            ? 'bg-red-100 text-red-700'
                            : 'bg-neutral-100 text-neutral-600'
                        }`}
                      >
                        {job.status}
                      </span>
                    </div>
                    
                    {job.payload && (
                      <div className="text-xs text-neutral-600 mb-1">
                        {job.payload.title && <div>Títol: {job.payload.title}</div>}
                        {job.payload.url && <div>URL: {job.payload.url}</div>}
                      </div>
                    )}
                    
                    {job.error && (
                      <div className="text-xs text-red-500 bg-red-50 p-2 rounded mt-1">
                        <AlertCircle className="w-3 h-3 inline mr-1" />
                        {job.error}
                      </div>
                    )}
                    
                    {job.result && job.result.knowledge_item && (
                      <div className="text-xs text-green-600 bg-green-50 p-2 rounded mt-1">
                        <CheckCircle2 className="w-3 h-3 inline mr-1" />
                        Indexat: {job.result.knowledge_item.title}
                      </div>
                    )}
                    
                    {job.progress && job.progress.percentage && (
                      <div className="mt-2">
                        <div className="flex justify-between text-xs text-neutral-600 mb-1">
                          <span>Progrés</span>
                          <span>{job.progress.percentage}%</span>
                        </div>
                        <div className="w-full bg-neutral-200 rounded-full h-1">
                          <div 
                            className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                            style={{ width: `${job.progress.percentage}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Estadístiques i configuració RAG */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Estadístiques */}
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-primary-500" />
            Estadístiques de Knowledge Base
          </h3>
          
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.total_items || 0}</div>
              <div className="text-sm text-blue-700">Elements indexats</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.successful_jobs || 0}</div>
              <div className="text-sm text-green-700">Jobs exitosos</div>
            </div>
            <div className="text-center p-3 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{stats.total_jobs || 0}</div>
              <div className="text-sm text-orange-700">Jobs totals</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{stats.failed_jobs || 0}</div>
              <div className="text-sm text-red-700">Jobs fallits</div>
            </div>
          </div>

          {stats.last_indexed && (
            <div className="text-sm text-neutral-600">
              <Clock className="w-4 h-4 inline mr-1" />
              Última indexació: {new Date(stats.last_indexed).toLocaleString()}
            </div>
          )}

          {stats.avg_processing_time > 0 && (
            <div className="text-sm text-neutral-600 mt-2">
              <Activity className="w-4 h-4 inline mr-1" />
              Temps mitjà de processament: {stats.avg_processing_time.toFixed(1)}s
            </div>
          )}
        </div>

        {/* Configuració RAG */}
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Settings className="w-5 h-5 text-primary-500" />
            Configuració RAG
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={ragConfig.enabled}
                onChange={(e) => setRagConfig(prev => ({ ...prev, enabled: e.target.checked }))}
                className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
              />
              <label className="text-sm text-neutral-700">Activar RAG per aquest agent</label>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Top K</label>
                <input
                  type="number"
                  min="1"
                  max="20"
                  className="input-field"
                  value={ragConfig.top_k}
                  onChange={(e) => setRagConfig(prev => ({ ...prev, top_k: parseInt(e.target.value) }))}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Umbral de similitud</label>
                <input
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  className="input-field"
                  value={ragConfig.similarity_threshold}
                  onChange={(e) => setRagConfig(prev => ({ ...prev, similarity_threshold: parseFloat(e.target.value) }))}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Màx. tokens</label>
                <input
                  type="number"
                  min="100"
                  max="4000"
                  className="input-field"
                  value={ragConfig.max_tokens}
                  onChange={(e) => setRagConfig(prev => ({ ...prev, max_tokens: parseInt(e.target.value) }))}
                />
              </div>
              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Mida de chunk</label>
                <input
                  type="number"
                  min="100"
                  max="2000"
                  className="input-field"
                  value={ragConfig.chunk_size}
                  onChange={(e) => setRagConfig(prev => ({ ...prev, chunk_size: parseInt(e.target.value) }))}
                />
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={updateRagConfig}
                className="btn-primary text-sm flex-1"
              >
                Guardar configuració
              </button>
              <button
                onClick={testRagQuery}
                className="btn-secondary text-sm flex-1"
              >
                Provar consulta
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default KnowledgePanel
