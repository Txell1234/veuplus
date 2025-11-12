import React, { useEffect, useState, useRef } from 'react'
import {
  Phone,
  Upload,
  Play,
  Pause,
  Square,
  BarChart3,
  Users,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Download,
  FileText,
  Settings,
  RefreshCw,
  Trash2,
  Eye,
  Calendar,
  Zap,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ConvHiBatchCalling = () => {
  const [agents, setAgents] = useState([])
  const [selectedAgent, setSelectedAgent] = useState('')
  const [batches, setBatches] = useState([])
  const [selectedBatch, setSelectedBatch] = useState(null)
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [fileInputRef, setFileInputRef] = useState(null)

  // Formulari de creació de batch
  const [batchForm, setBatchForm] = useState({
    batch_name: '',
    description: '',
    max_concurrent_calls: 5,
    retry_attempts: 2,
    retry_delay_seconds: 30,
    scheduled_time: '',
    dynamic_variables: {},
  })

  // Manual records
  const [manualRecords, setManualRecords] = useState([
    { phone_number: '', name: '', variables: {} }
  ])

  // Progress tracking
  const [progressData, setProgressData] = useState({})
  const [progressInterval, setProgressInterval] = useState(null)

  useEffect(() => {
    loadAgents()
    loadBatches()
  }, [])

  useEffect(() => {
    if (selectedBatch) {
      startProgressTracking(selectedBatch.id)
    }
    return () => {
      if (progressInterval) {
        clearInterval(progressInterval)
      }
    }
  }, [selectedBatch])

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

  const loadBatches = async () => {
    try {
      const response = await api.get('/api/convhi/batch-calling/batches')
      setBatches(response.data.batches || [])
    } catch (error) {
      console.error('Error carregant batches:', error)
      toast.error('No s\'han pogut carregar les trucades massives')
    }
  }

  const startProgressTracking = (batchId) => {
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/api/convhi/batch-calling/progress/${batchId}`)
        setProgressData(prev => ({
          ...prev,
          [batchId]: response.data
        }))
      } catch (error) {
        console.error('Error tracking progress:', error)
      }
    }, 2000)

    setProgressInterval(interval)
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    if (!file.name.endsWith('.csv')) {
      toast.error('Només es permeten fitxers CSV')
      return
    }

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('agent_id', selectedAgent)
      formData.append('batch_name', batchForm.batch_name || file.name.replace('.csv', ''))
      formData.append('description', batchForm.description)
      formData.append('max_concurrent_calls', batchForm.max_concurrent_calls.toString())
      formData.append('retry_attempts', batchForm.retry_attempts.toString())

      const response = await api.post('/api/convhi/batch-calling/upload-csv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      if (response.data.success) {
        toast.success(`Fitxer processat: ${response.data.valid_records} registres vàlids`)
        loadBatches()
        resetForm()
      }
    } catch (error) {
      console.error('Error uploading file:', error)
      toast.error('Error pujant fitxer CSV')
    } finally {
      setUploading(false)
    }
  }

  const createManualBatch = async () => {
    if (!selectedAgent) {
      toast.error('Selecciona un agent primer')
      return
    }

    if (!batchForm.batch_name.trim()) {
      toast.error('Introdueix un nom per al batch')
      return
    }

    const validRecords = manualRecords.filter(r => r.phone_number.trim())
    if (validRecords.length === 0) {
      toast.error('Afegeix almenys un número de telèfon')
      return
    }

    try {
      setLoading(true)
      const response = await api.post('/api/convhi/batch-calling/create', {
        agent_id: selectedAgent,
        batch_name: batchForm.batch_name,
        description: batchForm.description,
        max_concurrent_calls: batchForm.max_concurrent_calls,
        retry_attempts: batchForm.retry_attempts,
        retry_delay_seconds: batchForm.retry_delay_seconds,
        scheduled_time: batchForm.scheduled_time || null,
        dynamic_variables: batchForm.dynamic_variables,
        call_settings: {}
      }, {
        params: { records: validRecords }
      })

      if (response.data.success) {
        toast.success(`Batch creat: ${response.data.valid_records} trucades programades`)
        loadBatches()
        resetForm()
      }
    } catch (error) {
      console.error('Error creating batch:', error)
      toast.error('Error creant batch de trucades')
    } finally {
      setLoading(false)
    }
  }

  const startBatch = async (batchId) => {
    try {
      const response = await api.post(`/api/convhi/batch-calling/start/${batchId}`)
      if (response.data.success) {
        toast.success('Batch de trucades iniciat')
        loadBatches()
        if (selectedBatch?.id === batchId) {
          startProgressTracking(batchId)
        }
      }
    } catch (error) {
      console.error('Error starting batch:', error)
      toast.error('Error iniciant batch de trucades')
    }
  }

  const cancelBatch = async (batchId) => {
    if (!confirm('Estàs segur que vols cancel·lar aquest batch de trucades?')) {
      return
    }

    try {
      const response = await api.post(`/api/convhi/batch-calling/cancel/${batchId}`)
      if (response.data.success) {
        toast.success('Batch de trucades cancel·lat')
        loadBatches()
      }
    } catch (error) {
      console.error('Error cancelling batch:', error)
      toast.error('Error cancel·lant batch de trucades')
    }
  }

  const addManualRecord = () => {
    setManualRecords(prev => [...prev, { phone_number: '', name: '', variables: {} }])
  }

  const removeManualRecord = (index) => {
    setManualRecords(prev => prev.filter((_, i) => i !== index))
  }

  const updateManualRecord = (index, field, value) => {
    setManualRecords(prev => prev.map((record, i) => 
      i === index ? { ...record, [field]: value } : record
    ))
  }

  const resetForm = () => {
    setBatchForm({
      batch_name: '',
      description: '',
      max_concurrent_calls: 5,
      retry_attempts: 2,
      retry_delay_seconds: 30,
      scheduled_time: '',
      dynamic_variables: {},
    })
    setManualRecords([{ phone_number: '', name: '', variables: {} }])
  }

  const downloadTemplate = () => {
    const csvContent = 'phone_number,name,email,company\n+34123456789,Joan Garcia,joan@example.com,Empresa A\n+34987654321,Maria Lopez,maria@example.com,Empresa B'
    const blob = new Blob([csvContent], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'template_batch_calling.csv'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast.success('Plantilla CSV descarregada')
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'created': return <Clock className="w-4 h-4 text-blue-500" />
      case 'running': return <Play className="w-4 h-4 text-green-500" />
      case 'completed': return <CheckCircle2 className="w-4 h-4 text-emerald-500" />
      case 'failed': return <XCircle className="w-4 h-4 text-red-500" />
      case 'cancelled': return <Square className="w-4 h-4 text-gray-500" />
      default: return <AlertCircle className="w-4 h-4 text-orange-500" />
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'created': return 'bg-blue-100 text-blue-700'
      case 'running': return 'bg-green-100 text-green-700'
      case 'completed': return 'bg-emerald-100 text-emerald-700'
      case 'failed': return 'bg-red-100 text-red-700'
      case 'cancelled': return 'bg-gray-100 text-gray-700'
      default: return 'bg-orange-100 text-orange-700'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <Phone className="w-6 h-6 text-primary-500" />
            Trucades Massives ConvHi
          </h1>
          <p className="text-sm text-neutral-600">
            Programa i gestiona trucades massives amb agents ConvHi.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={downloadTemplate}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Plantilla CSV
          </button>
          <button
            onClick={loadBatches}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Actualitzar
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

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Crear batch */}
        <div className="space-y-6">
          {/* Configuració del batch */}
          <div className="card">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-primary-500" />
              Configuració del batch
            </h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Nom del batch</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="Trucades clients Q1 2024"
                  value={batchForm.batch_name}
                  onChange={(e) => setBatchForm(prev => ({ ...prev, batch_name: e.target.value }))}
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Descripció</label>
                <textarea
                  className="input-field min-h-[80px]"
                  placeholder="Descripció del batch de trucades..."
                  value={batchForm.description}
                  onChange={(e) => setBatchForm(prev => ({ ...prev, description: e.target.value }))}
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-semibold text-neutral-800 mb-1">Trucades concurrents</label>
                  <input
                    type="number"
                    min="1"
                    max="20"
                    className="input-field"
                    value={batchForm.max_concurrent_calls}
                    onChange={(e) => setBatchForm(prev => ({ ...prev, max_concurrent_calls: parseInt(e.target.value) }))}
                  />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-neutral-800 mb-1">Reintentos</label>
                  <input
                    type="number"
                    min="0"
                    max="5"
                    className="input-field"
                    value={batchForm.retry_attempts}
                    onChange={(e) => setBatchForm(prev => ({ ...prev, retry_attempts: parseInt(e.target.value) }))}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-neutral-800 mb-1">Programar per (opcional)</label>
                <input
                  type="datetime-local"
                  className="input-field"
                  value={batchForm.scheduled_time}
                  onChange={(e) => setBatchForm(prev => ({ ...prev, scheduled_time: e.target.value }))}
                />
              </div>
            </div>
          </div>

          {/* Pujar CSV */}
          <div className="card">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
              <Upload className="w-5 h-5 text-primary-500" />
              Pujar fitxer CSV
            </h3>
            
            <div className="space-y-4">
              <div className="border-2 border-dashed border-neutral-300 rounded-lg p-6 text-center">
                <FileText className="w-8 h-8 text-neutral-400 mx-auto mb-2" />
                <p className="text-sm text-neutral-600 mb-3">
                  Arrossega un fitxer CSV o fes clic per seleccionar
                </p>
                <input
                  ref={setFileInputRef}
                  type="file"
                  accept=".csv"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef?.click()}
                  disabled={uploading || !selectedAgent}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  {uploading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin" />
                      Pujant...
                    </>
                  ) : (
                    <>
                      <Upload className="w-4 h-4" />
                      Seleccionar CSV
                    </>
                  )}
                </button>
              </div>

              <div className="text-xs text-neutral-500">
                <p><strong>Format CSV:</strong> phone_number, name, email, company</p>
                <p><strong>Exemple:</strong> +34123456789, Joan Garcia, joan@example.com, Empresa A</p>
              </div>
            </div>
          </div>

          {/* Registres manuals */}
          <div className="card">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
              <Users className="w-5 h-5 text-primary-500" />
              Afegir registres manuals
            </h3>
            
            <div className="space-y-3">
              {manualRecords.map((record, index) => (
                <div key={index} className="border border-neutral-200 rounded-lg p-3">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-neutral-700">Registre {index + 1}</span>
                    {manualRecords.length > 1 && (
                      <button
                        onClick={() => removeManualRecord(index)}
                        className="p-1 text-red-500 hover:bg-red-50 rounded"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                  
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="tel"
                      className="input-field text-sm"
                      placeholder="Número de telèfon"
                      value={record.phone_number}
                      onChange={(e) => updateManualRecord(index, 'phone_number', e.target.value)}
                    />
                    <input
                      type="text"
                      className="input-field text-sm"
                      placeholder="Nom (opcional)"
                      value={record.name}
                      onChange={(e) => updateManualRecord(index, 'name', e.target.value)}
                    />
                  </div>
                </div>
              ))}
              
              <button
                onClick={addManualRecord}
                className="btn-secondary text-sm w-full"
              >
                Afegir registre
              </button>
              
              <button
                onClick={createManualBatch}
                disabled={loading || !selectedAgent}
                className="btn-primary w-full inline-flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <RefreshCw className="w-4 h-4 animate-spin" />
                    Creant batch...
                  </>
                ) : (
                  <>
                    <Phone className="w-4 h-4" />
                    Crear batch de trucades
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Llista de batches */}
        <div className="space-y-4">
          <div className="card">
            <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-primary-500" />
              Batches de trucades
            </h3>
            
            {batches.length === 0 ? (
              <p className="text-sm text-neutral-500 text-center py-8">
                No hi ha batches de trucades creats
              </p>
            ) : (
              <div className="space-y-3">
                {batches.map((batch) => {
                  const progress = progressData[batch.batch_call.id]
                  return (
                    <div
                      key={batch.batch_call.id}
                      className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                        selectedBatch?.id === batch.batch_call.id
                          ? 'border-primary-300 bg-primary-50'
                          : 'border-neutral-200 hover:border-neutral-300'
                      }`}
                      onClick={() => setSelectedBatch(batch.batch_call)}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(batch.batch_call.status)}
                          <span className="font-medium text-neutral-900">
                            {batch.batch_call.batch_name}
                          </span>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-semibold ${getStatusColor(batch.batch_call.status)}`}>
                          {batch.batch_call.status}
                        </span>
                      </div>
                      
                      <div className="text-sm text-neutral-600 mb-3">
                        <div className="flex items-center gap-4">
                          <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" />
                            {batch.batch_call.total_calls} trucades
                          </span>
                          <span className="flex items-center gap-1">
                            <Zap className="w-3 h-3" />
                            {batch.batch_call.max_concurrent_calls} concurrents
                          </span>
                          {batch.batch_call.success_rate > 0 && (
                            <span className="flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              {batch.batch_call.success_rate.toFixed(1)}% èxit
                            </span>
                          )}
                        </div>
                      </div>

                      {progress && (
                        <div className="mb-3">
                          <div className="flex justify-between text-xs text-neutral-600 mb-1">
                            <span>Progrés</span>
                            <span>{progress.progress_percentage.toFixed(1)}%</span>
                          </div>
                          <div className="w-full bg-neutral-200 rounded-full h-2">
                            <div
                              className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                              style={{ width: `${progress.progress_percentage}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      <div className="flex items-center gap-2">
                        {batch.batch_call.status === 'created' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              startBatch(batch.batch_call.id)
                            }}
                            className="btn-primary text-xs"
                          >
                            <Play className="w-3 h-3 mr-1" />
                            Iniciar
                          </button>
                        )}
                        
                        {['created', 'running'].includes(batch.batch_call.status) && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation()
                              cancelBatch(batch.batch_call.id)
                            }}
                            className="btn-secondary text-xs"
                          >
                            <Square className="w-3 h-3 mr-1" />
                            Cancel·lar
                          </button>
                        )}
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            setSelectedBatch(batch.batch_call)
                          }}
                          className="btn-secondary text-xs"
                        >
                          <Eye className="w-3 h-3 mr-1" />
                          Detalls
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Detalls del batch seleccionat */}
      {selectedBatch && (
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Eye className="w-5 h-5 text-primary-500" />
            Detalls del batch: {selectedBatch.batch_name}
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="text-center p-3 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{selectedBatch.total_calls}</div>
              <div className="text-sm text-blue-700">Trucades totals</div>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{selectedBatch.completed_calls}</div>
              <div className="text-sm text-green-700">Completades</div>
            </div>
            <div className="text-center p-3 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">{selectedBatch.failed_calls}</div>
              <div className="text-sm text-red-700">Fallides</div>
            </div>
          </div>

          <div className="text-sm text-neutral-600">
            <p><strong>Agent:</strong> {selectedBatch.agent_id}</p>
            <p><strong>Creat:</strong> {new Date(selectedBatch.created_at).toLocaleString()}</p>
            {selectedBatch.started_at && (
              <p><strong>Iniciat:</strong> {new Date(selectedBatch.started_at).toLocaleString()}</p>
            )}
            {selectedBatch.completed_at && (
              <p><strong>Completat:</strong> {new Date(selectedBatch.completed_at).toLocaleString()}</p>
            )}
            {selectedBatch.description && (
              <p><strong>Descripció:</strong> {selectedBatch.description}</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ConvHiBatchCalling



