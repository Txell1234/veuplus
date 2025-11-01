import React, { useEffect, useMemo, useState } from 'react'
import {
  Bot,
  CheckCircle2,
  Circle,
  Code,
  Globe,
  Loader2,
  Server,
  Settings,
  Shield,
  Volume2,
  Voicemail,
  Upload,
  Plus,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const wizardSteps = [
  { id: 'general', title: 'Identitat' },
  { id: 'llm', title: 'LLM & apis' },
  { id: 'voice', title: 'Veu & idioma' },
  { id: 'knowledge', title: 'Knowledge Base' },
  { id: 'asr', title: 'ASR & Tools' },
  { id: 'personalization', title: 'Personalització' },
  { id: 'telephony', title: 'Telefonia & revisió' },
]

const defaultAgentState = {
  name: '',
  description: '',
  llmProvider: 'openai',
  llmModel: 'gpt-4o-mini',
  apiKey: '',
  knowledgeBaseEnabled: true,
  turnTakingEnabled: true,
  monitoringEnabled: true,
  asrEnabled: true,
  voiceSystem: 'edge-tts',
  language: 'ca',
  voiceId: '',
  dynamicVariables: {},
  overrides: {},
  ragEnabled: true,
  ragTopK: 5,
  sipEnabled: false,
  sipNumber: '',
  sipTransport: 'tcp',
}

const ConvHiAgentWizard = () => {
  const [stepIndex, setStepIndex] = useState(0)
  const [formState, setFormState] = useState(defaultAgentState)
  const [availableVoices, setAvailableVoices] = useState({
    'edge-tts': [],
    catalan: [],
    alia: [],
  })
  const [llmProviders, setLlmProviders] = useState({})
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [resultAgentId, setResultAgentId] = useState('')
  const [uploadingDoc, setUploadingDoc] = useState(false)
  const [uploadingUrl, setUploadingUrl] = useState(false)
  const [knowledgeItems, setKnowledgeItems] = useState([])
  const [knowledgeUrl, setKnowledgeUrl] = useState('')

  useEffect(() => {
    const bootstrap = async () => {
      try {
        await Promise.all([fetchVoices(), fetchProviders()])
      } catch (error) {
        console.error('Error inicialitzant dades ConvHi:', error)
        toast.error('No s’han pogut carregar totes les dades, intenta-ho de nou.')
      } finally {
        setLoading(false)
      }
    }
    bootstrap()
  }, [])

  const fetchProviders = async () => {
    const response = await api.get('/api/convhi/llm-providers')
    setLlmProviders(response.data.providers || {})
  }

  const fetchVoices = async () => {
    const [edge, catalan, alia] = await Promise.all([
      api.get('/api/edge-tts/voices').catch(() => ({ data: { voices: [] } })),
      api.get('/api/catalan/voices').catch(() => ({ data: { voices: [] } })),
      api.get('/api/alia/voices').catch(() => ({ data: { voices: [] } })),
    ])
    setAvailableVoices({
      'edge-tts': edge.data.voices || [],
      catalan: catalan.data.voices || [],
      alia: alia.data.voices || [],
    })
  }

  const llmOptions = useMemo(() => Object.entries(llmProviders || {}), [llmProviders])

  const currentVoices = availableVoices[formState.voiceSystem] || []

  useEffect(() => {
    if (currentVoices.length > 0 && !formState.voiceId) {
      const firstVoice = currentVoices[0]
      setFormState((prev) => ({ ...prev, voiceId: firstVoice.id || firstVoice.voice_id || '' }))
    }
  }, [currentVoices, formState.voiceId])

  const updateState = (key, value) => {
    setFormState((prev) => ({ ...prev, [key]: value }))
  }

  const updateDynamicVariables = (draft) => updateState('dynamicVariables', draft)
  const updateOverrides = (draft) => updateState('overrides', draft)

  // Funcions per gestionar Knowledge Base al wizard
  const handleUploadFile = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    setUploadingDoc(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('agent_id', 'temp_wizard')

      toast.loading('Pujant document...')
      await api.post('/api/convhi/knowledge/file', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      toast.dismiss()
      toast.success('Document pujat correctament!')
      setKnowledgeItems((prev) => [...prev, { type: 'file', name: file.name, file }])
    } catch (error) {
      toast.dismiss()
      toast.error('Error pujant document: ' + (error.response?.data?.detail || 'Desconegut'))
      console.error('Error upload:', error)
    } finally {
      setUploadingDoc(false)
    }
  }

  const handleAddURL = async (e) => {
    e.preventDefault()
    if (!knowledgeUrl) return

    setUploadingUrl(true)
    try {
      toast.loading('Afegint URL...')
      await api.post('/api/convhi/knowledge/url', {
        agent_id: 'temp_wizard',
        url: knowledgeUrl
      })
      
      toast.dismiss()
      toast.success('URL afegida correctament!')
      setKnowledgeItems((prev) => [...prev, { type: 'url', url: knowledgeUrl }])
      setKnowledgeUrl('')
    } catch (error) {
      toast.dismiss()
      toast.error('Error afegint URL: ' + (error.response?.data?.detail || 'Desconegut'))
      console.error('Error URL:', error)
    } finally {
      setUploadingUrl(false)
    }
  }

  const removeKnowledgeItem = (index) => {
    setKnowledgeItems((prev) => prev.filter((_, i) => i !== index))
  }

  const nextStep = () => setStepIndex((prev) => Math.min(prev + 1, wizardSteps.length - 1))
  const previousStep = () => setStepIndex((prev) => Math.max(prev - 1, 0))

  const handleCreateAgent = async () => {
    setSubmitting(true)
    try {
      const payload = {
        name: formState.name,
        description: formState.description,
        llm_provider: formState.llmProvider,
        llm_model: formState.llmModel,
        api_key: formState.apiKey,
        knowledge_base_enabled: formState.knowledgeBaseEnabled,
        turn_taking_enabled: formState.turnTakingEnabled,
        monitoring_enabled: formState.monitoringEnabled,
        asr_enabled: formState.asrEnabled,
        voice_system: formState.voiceSystem,
        language: formState.language,
        voice_id: formState.voiceId,
        dynamic_variables: formState.dynamicVariables,
        overrides: formState.overrides,
        rag_enabled: formState.ragEnabled,
        rag_top_k: formState.ragTopK,
      }

      if (formState.sipEnabled && formState.sipNumber) {
        payload.sip_config = {
          enabled: true,
          phone_number: formState.sipNumber,
          transport: formState.sipTransport,
        }
      }

      console.log('📤 Creant agent amb payload:', payload)
      const response = await api.post('/api/convhi/agents', payload)
      console.log('✅ Resposta del servidor:', response.data)
      
      const agentId = response.data.agent?.id || response.data.id || `convhi_${Date.now()}`
      setResultAgentId(agentId)
      
      toast.success('Agent creat correctament!')
      
      // Redirect a llista d'agents després de 1.5 segons
      setTimeout(() => {
        window.location.href = '/convhi-agents'
      }, 1500)
    } catch (error) {
      console.error('❌ Error creant agent:', error)
      console.error('Error response:', error.response?.data)
      const errorMsg = error.response?.data?.detail || error.message || 'Error desconegut'
      toast.error(`Error: ${errorMsg}`)
    } finally {
      setSubmitting(false)
    }
  }

  const renderGeneralStep = () => (
    <div className="space-y-4">
      <p className="text-sm text-neutral-600">
        Dona-li un nom i descriu breument què ha de fer aquest agent (suport, vendes, billing...). Això ajuda el teu
        equip a identificar-lo més endavant.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Nom de l’agent</label>
          <input
            className="input-field mt-1"
            placeholder="AT Hub - Suport Català"
            value={formState.name}
            onChange={(event) => updateState('name', event.target.value)}
          />
        </div>
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Descripció</label>
          <input
            className="input-field mt-1"
            placeholder="Atenció al client inbound per productes digitals"
            value={formState.description}
            onChange={(event) => updateState('description', event.target.value)}
          />
        </div>
      </div>
    </div>
  )

  const renderLlmStep = () => (
    <div className="space-y-4">
      <p className="text-sm text-neutral-600">
        Tria el proveïdor i model que utilitzarà l’agent. Necessitaràs la clau API corresponent.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Proveïdor LLM</label>
          <select
            className="input-field mt-1"
            value={formState.llmProvider}
            onChange={(event) => updateState('llmProvider', event.target.value)}
          >
            {llmOptions.length === 0 && <option value="openai">openai</option>}
            {llmOptions.map(([key, provider]) => (
              <option key={key} value={key}>
                {provider.label || key}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Model</label>
          <select
            className="input-field mt-1"
            value={formState.llmModel}
            onChange={(event) => updateState('llmModel', event.target.value)}
          >
            {(llmOptions.find(([key]) => key === formState.llmProvider)?.[1]?.models || [
              'gpt-4o-mini',
              'gpt-4o',
            ]).map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>
        <div className="md:col-span-2">
          <label className="block text-sm font-semibold text-neutral-800">Clau API</label>
          <input
            type="password"
            className="input-field mt-1"
            placeholder="sk-..."
            value={formState.apiKey}
            onChange={(event) => updateState('apiKey', event.target.value)}
          />
          <p className="text-xs text-neutral-500 mt-1">
            Pots deixar-ho buit i afegir la clau més tard a <strong>Configuració → Credencials</strong>.
          </p>
        </div>
      </div>
      <div className="rounded-lg border border-neutral-200 bg-white p-3 text-xs text-neutral-500">
        <p className="font-semibold text-neutral-700">Consells</p>
        <ul className="list-disc list-inside space-y-1 mt-1">
          <li>Utilitza comptes de servei amb permisos limitats.</li>
          <li>Revisa les polítiques de privacitat de cada proveïdor.</li>
        </ul>
      </div>
    </div>
  )

  const renderVoiceStep = () => (
    <div className="space-y-4">
      <p className="text-sm text-neutral-600">Selecciona el sistema de veu i l’idioma principal de l’agent.</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Sistema de veu</label>
          <select
            className="input-field mt-1"
            value={formState.voiceSystem}
            onChange={(event) => updateState('voiceSystem', event.target.value)}
          >
            <option value="edge-tts">Edge-TTS (multi idiomes)</option>
            <option value="catalan">Hiperrealista (mock)</option>
            <option value="alia">ALIA Kit</option>
          </select>
          <p className="text-xs text-neutral-500 mt-1">
            El mode hiperrealista utilitza les gravacions locals mentre no hi ha GPU.
          </p>
        </div>
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Idioma</label>
          <select
            className="input-field mt-1"
            value={formState.language}
            onChange={(event) => updateState('language', event.target.value)}
          >
            <option value="ca">Català</option>
            <option value="es">Castellà</option>
            <option value="en">Anglès</option>
            <option value="fr">Francès</option>
            <option value="de">Alemany</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-semibold text-neutral-800">Veu</label>
          <select
            className="input-field mt-1"
            value={formState.voiceId}
            onChange={(event) => updateState('voiceId', event.target.value)}
          >
            {currentVoices.map((voice) => {
              const id = voice.id || voice.voice_id
              const label = voice.name || voice.DisplayName || id
              return (
                <option key={id} value={id}>
                  {label}
                </option>
              )
            })}
          </select>
        </div>
      </div>
      <div className="rounded-lg border border-neutral-200 bg-white p-3 text-xs text-neutral-500">
        <p className="font-semibold text-neutral-700">Volume i idiomes addicionals</p>
        <p>
          Pots canviar la veu en temps real des del panell ConvHi &gt; Agents. Quan disposis de GPU podràs crear veus
          neuronals pròpies.
        </p>
      </div>
    </div>
  )

  const renderKnowledgeStep = () => (
    <div className="space-y-6">
      <p className="text-sm text-neutral-600">
        Configura la base de coneixement de l'agent. Pots pujar documents, afegir URLs o escrit text manualment.
      </p>

      {/* Upload Documents */}
      <div className="border border-neutral-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-neutral-900 mb-3">Pujar Documents</h3>
        <div className="border-2 border-dashed border-neutral-300 rounded-lg p-6 text-center">
          <input
            type="file"
            id="kb-file-upload"
            accept=".pdf,.txt,.doc,.docx,.md"
            className="hidden"
            onChange={handleUploadFile}
            disabled={uploadingDoc}
          />
          <label 
            htmlFor="kb-file-upload" 
            className={`cursor-pointer btn-secondary inline-flex items-center gap-2 ${uploadingDoc ? 'opacity-50 cursor-not-allowed' : ''}`}
          >
            {uploadingDoc ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
            {uploadingDoc ? 'Pujant...' : 'Seleccionar Document'}
          </label>
          <p className="text-xs text-neutral-500 mt-2">Suporta PDF, TXT, DOC, DOCX, MD</p>
        </div>
      </div>

      {/* Add URL */}
      <div className="border border-neutral-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-neutral-900 mb-3">Afegir URL</h3>
        <form className="flex gap-2" onSubmit={handleAddURL}>
          <input
            type="url"
            placeholder="https://example.com/document"
            className="input-field flex-1"
            value={knowledgeUrl}
            onChange={(e) => setKnowledgeUrl(e.target.value)}
            disabled={uploadingUrl}
          />
          <button 
            type="submit" 
            className="btn-primary inline-flex items-center gap-2"
            disabled={uploadingUrl || !knowledgeUrl}
          >
            {uploadingUrl ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
          </button>
        </form>
      </div>

      {/* Knowledge Items List */}
      {knowledgeItems.length > 0 && (
        <div className="border border-neutral-200 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-neutral-900 mb-3">Documents/URLs afegits</h3>
          <div className="space-y-2">
            {knowledgeItems.map((item, index) => (
              <div key={index} className="flex items-center justify-between bg-neutral-50 p-2 rounded">
                <span className="text-sm text-neutral-700">
                  {item.type === 'file' ? `📄 ${item.name}` : `🔗 ${item.url}`}
                </span>
                <button
                  onClick={() => removeKnowledgeItem(index)}
                  className="text-xs text-red-600 hover:text-red-700"
                >
                  Eliminar
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Enable RAG */}
      <div className="border border-neutral-200 rounded-lg p-4">
        <h3 className="text-sm font-semibold text-neutral-900 mb-3">RAG (Recuperació Augmentada de Coneixement)</h3>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={formState.ragEnabled}
            onChange={(e) => updateState('ragEnabled', e.target.checked)}
            className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
          />
          <span className="text-sm text-neutral-700">Activar RAG per aquest agent</span>
        </label>
        {formState.ragEnabled && (
          <div className="mt-3 flex items-center gap-3">
            <span className="text-sm text-neutral-600">Top K:</span>
            <input
              type="number"
              min={1}
              max={10}
              value={formState.ragTopK}
              className="input-field w-20"
              onChange={(e) => updateState('ragTopK', Number(e.target.value))}
            />
          </div>
        )}
      </div>
    </div>
  )

  const renderAsrStep = () => (
    <div className="space-y-6">
      <p className="text-sm text-neutral-600">
        Configura ASR (transcripció d'àudio) i les eines disponibles per l'agent.
      </p>

      {/* ASR Configuration */}
      <div className="border border-neutral-200 rounded-lg p-4 space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-neutral-900">Activar ASR</h3>
            <p className="text-xs text-neutral-600">Transcripció automàtica d'àudio a text amb Whisper</p>
          </div>
          <label className="relative inline-flex items-center cursor-pointer">
            <input
              type="checkbox"
              checked={formState.asrEnabled}
              onChange={(e) => updateState('asrEnabled', e.target.checked)}
              className="sr-only peer"
            />
            <div className="w-14 h-7 bg-neutral-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-neutral-300 after:border after:rounded-full after:h-6 after:w-6 after:transition-all peer-checked:bg-primary-600"></div>
          </label>
        </div>
      </div>

      {/* Tools Configuration */}
      <div className="border border-neutral-200 rounded-lg p-4 space-y-3">
        <h3 className="text-sm font-semibold text-neutral-900">Eines Disponibles</h3>
        
        {[
          { key: 'knowledgeBaseEnabled', label: 'Knowledge Base' },
          { key: 'turnTakingEnabled', label: 'Turn Taking en temps real' },
          { key: 'monitoringEnabled', label: 'Monitoring & logs' },
        ].map((tool) => (
          <label key={tool.key} className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formState[tool.key]}
              onChange={(e) => updateState(tool.key, e.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="text-sm text-neutral-700">{tool.label}</span>
          </label>
        ))}
      </div>
    </div>
  )

  const renderPersonalizationStep = () => {
    const dynamicPairs = Object.entries(formState.dynamicVariables || {})
    const overrideEntries = Object.entries(formState.overrides || {})

    return (
      <div className="space-y-6">
        <p className="text-sm text-neutral-600">
          Afegeix variables dinàmiques (ex. <span className="font-mono">user_name</span>) i overrides per idioma o
          missatge inicial.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="rounded-lg border border-neutral-200 bg-white p-4 space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
              <Code className="w-4 h-4 text-primary-500" />
              Variables dinàmiques
            </h3>
            <p className="text-xs text-neutral-500">
              S’utilitzen dins del prompt: <span className="font-mono">{'{'}{'{'}user_name{'}'}{'}'}</span>
            </p>
            <div className="space-y-2">
              {dynamicPairs.map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  <input
                    className="input-field flex-1 text-xs"
                    value={`${key}`}
                    onChange={(event) => {
                      const newDynamic = { ...formState.dynamicVariables }
                      const newKey = event.target.value.trim()
                      if (newKey && newKey !== key) {
                        delete newDynamic[key]
                        newDynamic[newKey] = value
                        updateDynamicVariables(newDynamic)
                      }
                    }}
                  />
                  <input
                    className="input-field flex-1 text-xs"
                    value={`${value}`}
                    onChange={(event) => {
                      const newDynamic = { ...formState.dynamicVariables, [key]: event.target.value }
                      updateDynamicVariables(newDynamic)
                    }}
                  />
                  <button
                    onClick={() => {
                      const newDynamic = { ...formState.dynamicVariables }
                      delete newDynamic[key]
                      updateDynamicVariables(newDynamic)
                    }}
                    className="text-xs text-red-500 hover:underline"
                  >
                    Eliminar
                  </button>
                </div>
              ))}
              <button
                onClick={() => updateDynamicVariables({ ...formState.dynamicVariables, [`variable_${dynamicPairs.length + 1}`]: '' })}
                className="btn-secondary text-xs"
              >
                Afegir variable
              </button>
            </div>
          </div>

          <div className="rounded-lg border border-neutral-200 bg-white p-4 space-y-3">
            <h3 className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
              <Globe className="w-4 h-4 text-primary-500" />
              Overrides
            </h3>
            <p className="text-xs text-neutral-500">Idioma, veu o missatge inicial específic per agent/campanya.</p>
            <div className="space-y-2">
              {overrideEntries.map(([key, value]) => (
                <div key={key} className="flex items-center gap-2">
                  <input
                    className="input-field flex-1 text-xs"
                    value={`${key}`}
                    onChange={(event) => {
                      const newOverrides = { ...formState.overrides }
                      const newKey = event.target.value.trim()
                      if (newKey && newKey !== key) {
                        delete newOverrides[key]
                        newOverrides[newKey] = value
                        updateOverrides(newOverrides)
                      }
                    }}
                  />
                  <input
                    className="input-field flex-1 text-xs"
                    value={`${value}`}
                    onChange={(event) => {
                      const newOverrides = { ...formState.overrides, [key]: event.target.value }
                      updateOverrides(newOverrides)
                    }}
                  />
                  <button
                    onClick={() => {
                      const newOverrides = { ...formState.overrides }
                      delete newOverrides[key]
                      updateOverrides(newOverrides)
                    }}
                    className="text-xs text-red-500 hover:underline"
                  >
                    Eliminar
                  </button>
                </div>
              ))}
              <button
                onClick={() => updateOverrides({ ...formState.overrides, [`override_${overrideEntries.length + 1}`]: '' })}
                className="btn-secondary text-xs"
              >
                Afegir override
              </button>
            </div>
          </div>
        </div>

        <div className="rounded-lg border border-neutral-200 bg-white p-3 text-xs text-neutral-500">
          <p className="font-semibold text-neutral-700">RAG</p>
          <label className="flex items-center gap-2 mt-2">
            <input
              type="checkbox"
              checked={formState.ragEnabled}
              onChange={(event) => updateState('ragEnabled', event.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            Activar recuperació de coneixement (RAG)
          </label>
          {formState.ragEnabled && (
            <div className="mt-2 flex items-center gap-3">
              <span>Top K:</span>
              <input
                type="number"
                min={1}
                max={10}
                value={formState.ragTopK}
                className="input-field w-20"
                onChange={(event) => updateState('ragTopK', Number(event.target.value))}
              />
            </div>
          )}
        </div>
      </div>
    )
  }

  const renderTelephonyStep = () => (
    <div className="space-y-4">
      <p className="text-sm text-neutral-600">
        Activa telefonia o revisa el resum abans de crear l’agent. Pots deixar-ho per més endavant.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="rounded-lg border border-neutral-200 bg-white p-4 space-y-3">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
            <Voicemail className="w-4 h-4 text-primary-500" />
            Telefonia (opcional)
          </h3>
          <label className="flex items-center gap-2 text-neutral-600 text-sm">
            <input
              type="checkbox"
              checked={formState.sipEnabled}
              onChange={(event) => updateState('sipEnabled', event.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary-600 focus:ring-primary-500"
            />
            Assignar número de telèfon via SIP
          </label>
          {formState.sipEnabled && (
            <div className="space-y-2">
              <input
                className="input-field"
                placeholder="+34933123456"
                value={formState.sipNumber}
                onChange={(event) => updateState('sipNumber', event.target.value)}
              />
              <select
                className="input-field"
                value={formState.sipTransport}
                onChange={(event) => updateState('sipTransport', event.target.value)}
              >
                <option value="tcp">TCP</option>
                <option value="tls">TLS</option>
              </select>
            </div>
          )}
        </div>
        <div className="rounded-lg border border-neutral-200 bg-white p-4 space-y-2 text-sm text-neutral-600">
          <h3 className="flex items-center gap-2 text-sm font-semibold text-neutral-900">
            <Server className="w-4 h-4 text-primary-500" />
            Resum ràpid
          </h3>
          <ul className="list-disc list-inside space-y-1 text-xs">
            <li>
              Nom: <strong>{formState.name || 'Sense nom'}</strong>
            </li>
            <li>Veu: {formState.voiceId || 'per assignar'}</li>
            <li>LLM: {formState.llmProvider} · {formState.llmModel}</li>
            <li>RAG: {formState.ragEnabled ? `actiu (top ${formState.ragTopK})` : 'desactivat'}</li>
            <li>
              Telefonia:{' '}
              {formState.sipEnabled ? `${formState.sipNumber || 'per assignar'} (${formState.sipTransport.toUpperCase()})` : 'no'}
            </li>
          </ul>
          {resultAgentId && (
            <p className="text-xs text-emerald-600">
              Agent {resultAgentId} creat! Pots revisar-lo a ConvHi &gt; Agents.
            </p>
          )}
        </div>
      </div>
    </div>
  )

  const renderStepContent = () => {
    const stepId = wizardSteps[stepIndex].id
    if (stepId === 'general') return renderGeneralStep()
    if (stepId === 'llm') return renderLlmStep()
    if (stepId === 'voice') return renderVoiceStep()
    if (stepId === 'knowledge') return renderKnowledgeStep()
    if (stepId === 'asr') return renderAsrStep()
    if (stepId === 'personalization') return renderPersonalizationStep()
    return renderTelephonyStep()
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="flex items-center gap-3 text-neutral-600">
          <Loader2 className="w-5 h-5 animate-spin" /> Carregant assistent…
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <Bot className="w-6 h-6 text-primary-500" />
            Nou agent ConvHi
          </h1>
          <p className="text-sm text-neutral-600">
            Assistència pas a pas per crear un agent consistent sense deixar-te cap configuració important.
          </p>
        </div>
        <span className="text-xs text-neutral-500 uppercase tracking-wide">
          Pas {stepIndex + 1} de {wizardSteps.length}
        </span>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          {wizardSteps.map((step, index) => {
            const active = index === stepIndex
            const completed = index < stepIndex
            return (
              <div
                key={step.id}
                className={`flex items-center gap-2 text-xs font-semibold uppercase ${
                  active ? 'text-primary-600' : 'text-neutral-400'
                }`}
              >
                <div
                  className={`flex h-6 w-6 items-center justify-center rounded-full border ${
                    completed
                      ? 'bg-primary-600 text-white border-primary-600'
                      : active
                      ? 'border-primary-500 text-primary-600'
                      : 'border-neutral-300 text-neutral-400'
                  }`}
                >
                  {completed ? <CheckCircle2 className="w-4 h-4" /> : index + 1}
                </div>
                <span>{step.title}</span>
              </div>
            )
          })}
        </div>
        <div className="card space-y-6">{renderStepContent()}</div>
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={previousStep}
          disabled={stepIndex === 0}
          className="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Enrere
        </button>
        {stepIndex === wizardSteps.length - 1 ? (
          <button
            onClick={handleCreateAgent}
            disabled={submitting}
            className="btn-primary inline-flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {submitting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Settings className="w-4 h-4" />}
            <span>{submitting ? 'Creant...' : 'Crear agent'}</span>
          </button>
        ) : (
          <button onClick={nextStep} className="btn-primary">
            Continuar
          </button>
        )}
      </div>
    </div>
  )
}

export default ConvHiAgentWizard
