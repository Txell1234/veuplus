import React, { useState, useEffect } from 'react'
import {
  Phone,
  Plus,
  Settings,
  TestTube,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Trash2,
  Edit,
  Eye,
  Clock,
  BarChart3,
  Activity,
  ExternalLink,
  Monitor,
  Upload,
  Download,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ConvHiSIPConfig = () => {
  const [activeTab, setActiveTab] = useState('trunks')
  const [loading, setLoading] = useState(false)
  
  // SIP Trunks State
  const [trunks, setTrunks] = useState([])
  const [activeCalls, setActiveCalls] = useState([])
  const [showCreateTrunk, setShowCreateTrunk] = useState(false)
  const [editingTrunk, setEditingTrunk] = useState(null)

  // New Trunk Form State
  const [trunkForm, setTrunkForm] = useState({
    label: '',
    phone_number: '',
    outbound_address: '',
    transport_type: 'tcp',
    outbound_transport: 'tcp',
    auth_type: 'digest',
    username: '',
    password: '',
    max_concurrent_calls: 10,
    call_timeout: 300,
    codec_preference: ['G711', 'G722'],
  })

  // Stats
  const [stats, setStats] = useState({
    total_trunks: 0,
    active_trunks: 0,
    total_calls: 0,
    active_calls: 0,
  })

  useEffect(() => {
    loadTrunks()
    loadActiveCalls()
    loadStats()
    
    // Auto-refresh every 5 seconds
    const interval = setInterval(() => {
      loadActiveCalls()
      loadStats()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [])

  const loadTrunks = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/convhi/sip/trunks')
      setTrunks(response.data.trunks || [])
    } catch (error) {
      console.error('Error loading trunks:', error)
      toast.error('Error carregant trunks')
    } finally {
      setLoading(false)
    }
  }

  const loadActiveCalls = async () => {
    try {
      const response = await api.get('/api/convhi/sip/calls')
      setActiveCalls(response.data.calls || [])
    } catch (error) {
      console.error('Error loading calls:', error)
    }
  }

  const loadStats = async () => {
    try {
      const trunks = await api.get('/api/convhi/sip/trunks')
      const calls = await api.get('/api/convhi/sip/calls')
      
      setStats({
        total_trunks: trunks.data.trunks?.length || 0,
        active_trunks: trunks.data.trunks?.filter(t => t.status === 'active').length || 0,
        total_calls: calls.data.total || 0,
        active_calls: calls.data.calls?.length || 0,
      })
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const testTrunk = async (trunkId) => {
    try {
      toast.loading('Provant trunk...')
      const response = await api.post(`/api/convhi/sip/trunks/${trunkId}/test`)
      
      if (response.data.success) {
        toast.success(`Trunk OK! Latència: ${response.data.latency}ms`)
      } else {
        toast.error(`Error: ${response.data.error}`)
      }
    } catch (error) {
      console.error('Error testing trunk:', error)
      toast.error('Error provant trunk')
    } finally {
      toast.dismiss()
    }
  }

  const createTrunk = async () => {
    try {
      setLoading(true)
      const response = await api.post('/api/convhi/sip/trunks', trunkForm)
      
      toast.success('Trunk SIP creat correctament')
      setShowCreateTrunk(false)
      resetForm()
      await loadTrunks()
    } catch (error) {
      console.error('Error creating trunk:', error)
      toast.error(error.response?.data?.detail || 'Error creant trunk')
    } finally {
      setLoading(false)
    }
  }

  const updateTrunk = async () => {
    try {
      setLoading(true)
      await api.put(`/api/convhi/sip/trunks/${editingTrunk.id}`, trunkForm)
      
      toast.success('Trunk actualitzat correctament')
      setEditingTrunk(null)
      resetForm()
      await loadTrunks()
    } catch (error) {
      console.error('Error updating trunk:', error)
      toast.error('Error actualitzant trunk')
    } finally {
      setLoading(false)
    }
  }

  const deleteTrunk = async (trunkId) => {
    if (!confirm('Segur que vols eliminar aquest trunk?')) return
    
    try {
      await api.delete(`/api/convhi/sip/trunks/${trunkId}`)
      toast.success('Trunk eliminat')
      await loadTrunks()
    } catch (error) {
      console.error('Error deleting trunk:', error)
      toast.error('Error eliminant trunk')
    }
  }

  const resetForm = () => {
    setTrunkForm({
      label: '',
      phone_number: '',
      outbound_address: '',
      transport_type: 'tcp',
      outbound_transport: 'tcp',
      auth_type: 'digest',
      username: '',
      password: '',
      max_concurrent_calls: 10,
      call_timeout: 300,
      codec_preference: ['G711', 'G722'],
    })
  }

  const startEdit = (trunk) => {
    setEditingTrunk(trunk)
    setTrunkForm({
      label: trunk.label || '',
      phone_number: trunk.phone_number || '',
      outbound_address: trunk.outbound_address || '',
      transport_type: trunk.transport_type || 'tcp',
      outbound_transport: trunk.outbound_transport || 'tcp',
      auth_type: trunk.auth_type || 'digest',
      username: trunk.username || '',
      password: '', // Don't fill password
      max_concurrent_calls: trunk.max_concurrent_calls || 10,
      call_timeout: trunk.call_timeout || 300,
      codec_preference: trunk.codec_preference || ['G711', 'G722'],
    })
    setShowCreateTrunk(true)
  }

  const tabs = [
    { id: 'trunks', label: 'SIP Trunks', icon: Phone },
    { id: 'calls', label: 'Trucades Actives', icon: Activity },
    { id: 'monitoring', label: 'Monitoring', icon: BarChart3 },
    { id: 'settings', label: 'Configuració', icon: Settings },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-2">
            <Phone className="w-8 h-8 text-primary-500" />
            Configuració SIP Trunking
          </h1>
          <p className="text-sm text-neutral-600 mt-1">
            Gestiona trunks SIP, configuració i monitoring
          </p>
        </div>
        <button
          onClick={() => {
            resetForm()
            setEditingTrunk(null)
            setShowCreateTrunk(true)
          }}
          className="btn-primary inline-flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Crear Trunk
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-sm text-blue-700 font-semibold">Total Trunks</p>
          <p className="text-2xl font-bold text-blue-900">{stats.total_trunks}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-sm text-green-700 font-semibold">Actius</p>
          <p className="text-2xl font-bold text-green-900">{stats.active_trunks}</p>
        </div>
        <div className="bg-orange-50 rounded-lg p-4">
          <p className="text-sm text-orange-700 font-semibold">Total Trucades</p>
          <p className="text-2xl font-bold text-orange-900">{stats.total_calls}</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <p className="text-sm text-purple-700 font-semibold">Actives</p>
          <p className="text-2xl font-bold text-purple-900">{stats.active_calls}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-neutral-200">
        <div className="flex gap-1">
          {tabs.map((tab) => {
            const Icon = tab.icon
            const isActive = activeTab === tab.id
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-3 font-semibold border-b-2 transition ${
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
        {activeTab === 'trunks' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-semibold text-neutral-900">SIP Trunks</h2>
              <button onClick={loadTrunks} className="btn-secondary inline-flex items-center gap-2">
                <RefreshCw className="w-4 h-4" />
                Actualitzar
              </button>
            </div>

            {/* Trunks List */}
            {trunks.length > 0 ? (
              <div className="space-y-3">
                {trunks.map((trunk) => (
                  <div key={trunk.id} className="border border-neutral-200 rounded-lg p-4 hover:border-primary-300 transition">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-neutral-900">{trunk.label || trunk.id}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${
                            trunk.status === 'active' 
                              ? 'bg-green-100 text-green-700' 
                              : 'bg-neutral-100 text-neutral-700'
                          }`}>
                            {trunk.status || 'active'}
                          </span>
                        </div>
                        <div className="mt-2 space-y-1 text-sm text-neutral-600">
                          <p><strong>Número:</strong> {trunk.phone_number}</p>
                          <p><strong>Outbound:</strong> {trunk.outbound_address}</p>
                          <p><strong>Transport:</strong> {trunk.transport_type?.toUpperCase()}</p>
                          <p><strong>Max trucades:</strong> {trunk.max_concurrent_calls}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => testTrunk(trunk.id)}
                          className="btn-secondary inline-flex items-center gap-2"
                        >
                          <TestTube className="w-4 h-4" />
                          Provar
                        </button>
                        <button
                          onClick={() => startEdit(trunk)}
                          className="btn-secondary inline-flex items-center gap-2"
                        >
                          <Edit className="w-4 h-4" />
                          Editar
                        </button>
                        <button
                          onClick={() => deleteTrunk(trunk.id)}
                          className="btn-secondary inline-flex items-center gap-2 text-red-600"
                        >
                          <Trash2 className="w-4 h-4" />
                          Eliminar
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-neutral-500 text-center py-8">
                No hi ha trunks SIP creats. Crea un per començar.
              </p>
            )}
          </div>
        )}

        {activeTab === 'calls' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-semibold text-neutral-900">Trucades Actives</h2>
            
            {activeCalls.length > 0 ? (
              <div className="space-y-3">
                {activeCalls.map((call) => (
                  <div key={call.call_id} className="border border-neutral-200 rounded-lg p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3">
                          <h3 className="font-semibold text-neutral-900">Trucada {call.call_id.substring(0, 8)}</h3>
                          <span className="px-2 py-1 rounded text-xs font-semibold bg-blue-100 text-blue-700">
                            {call.status || 'active'}
                          </span>
                        </div>
                        <div className="mt-2 space-y-1 text-sm text-neutral-600">
                          <p><strong>De:</strong> {call.from_number}</p>
                          <p><strong>A:</strong> {call.to_number}</p>
                          <p><strong>Agent:</strong> {call.agent_id}</p>
                          <p><strong>RTP Port:</strong> {call.rtp_port}</p>
                        </div>
                      </div>
                      <button className="btn-secondary inline-flex items-center gap-2">
                        <Eye className="w-4 h-4" />
                        Veure Detalls
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-neutral-500 text-center py-8">
                No hi ha trucades actives
              </p>
            )}
          </div>
        )}

        {activeTab === 'monitoring' && (
          <MonitoringTab />
        )}

        {activeTab === 'settings' && (
          <SettingsTab />
        )}
      </div>

      {/* Create/Edit Trunk Modal */}
      {showCreateTrunk && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-semibold text-neutral-900">
                {editingTrunk ? 'Editar Trunk' : 'Crear Trunk SIP'}
              </h2>
              <button
                onClick={() => {
                  setShowCreateTrunk(false)
                  setEditingTrunk(null)
                  resetForm()
                }}
                className="text-neutral-600 hover:text-neutral-900"
              >
                <XCircle className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-neutral-900 mb-2">Nom del Trunk</label>
                <input
                  type="text"
                  value={trunkForm.label}
                  onChange={(e) => setTrunkForm({...trunkForm, label: e.target.value})}
                  placeholder="Ex: Trunk Principal"
                  className="input-field"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-neutral-900 mb-2">Número Telèfon</label>
                  <input
                    type="text"
                    value={trunkForm.phone_number}
                    onChange={(e) => setTrunkForm({...trunkForm, phone_number: e.target.value})}
                    placeholder="+34933123456"
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-neutral-900 mb-2">Transport</label>
                  <select
                    value={trunkForm.transport_type}
                    onChange={(e) => setTrunkForm({...trunkForm, transport_type: e.target.value})}
                    className="input-field"
                  >
                    <option value="tcp">TCP</option>
                    <option value="tls">TLS</option>
                    <option value="udp">UDP</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-neutral-900 mb-2">Outbound Address</label>
                <input
                  type="text"
                  value={trunkForm.outbound_address}
                  onChange={(e) => setTrunkForm({...trunkForm, outbound_address: e.target.value})}
                  placeholder="sip.provider.com"
                  className="input-field"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-neutral-900 mb-2">Max Trucades Concurrents</label>
                  <input
                    type="number"
                    value={trunkForm.max_concurrent_calls}
                    onChange={(e) => setTrunkForm({...trunkForm, max_concurrent_calls: parseInt(e.target.value)})}
                    className="input-field"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-neutral-900 mb-2">Timeout (segons)</label>
                  <input
                    type="number"
                    value={trunkForm.call_timeout}
                    onChange={(e) => setTrunkForm({...trunkForm, call_timeout: parseInt(e.target.value)})}
                    className="input-field"
                  />
                </div>
              </div>

              {trunkForm.auth_type === 'digest' && (
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-neutral-900 mb-2">Username</label>
                    <input
                      type="text"
                      value={trunkForm.username}
                      onChange={(e) => setTrunkForm({...trunkForm, username: e.target.value})}
                      className="input-field"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-neutral-900 mb-2">Password</label>
                    <input
                      type="password"
                      value={trunkForm.password}
                      onChange={(e) => setTrunkForm({...trunkForm, password: e.target.value})}
                      className="input-field"
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-3 pt-4">
                <button
                  onClick={editingTrunk ? updateTrunk : createTrunk}
                  disabled={loading || !trunkForm.label || !trunkForm.phone_number}
                  className="btn-primary flex-1"
                >
                  {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                  {editingTrunk ? 'Actualitzar' : 'Crear'} Trunk
                </button>
                <button
                  onClick={() => {
                    setShowCreateTrunk(false)
                    setEditingTrunk(null)
                    resetForm()
                  }}
                  className="btn-secondary"
                >
                  Cancel·lar
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// Monitoring Tab Component
const MonitoringTab = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-neutral-900">Monitoring en Temps Real</h2>
      
      <div className="grid grid-cols-2 gap-6">
        <div className="border border-neutral-200 rounded-lg p-6">
          <h3 className="font-semibold text-neutral-900 mb-4">Rendiment</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">CPU Usage</span>
              <span className="text-sm font-semibold text-neutral-900">45%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Memory</span>
              <span className="text-sm font-semibold text-neutral-900">1.2 GB</span>
            </div>
          </div>
        </div>

        <div className="border border-neutral-200 rounded-lg p-6">
          <h3 className="font-semibold text-neutral-900 mb-4">Qualitat</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Jitter Mitjà</span>
              <span className="text-sm font-semibold text-neutral-900">5 ms</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Packet Loss</span>
              <span className="text-sm font-semibold text-green-600">0.01%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Settings Tab Component
const SettingsTab = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-neutral-900">Configuració Asterisk</h2>
      
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Ubicació Configuració:</strong> /etc/asterisk/extensions.conf
        </p>
        <p className="text-sm text-blue-800 mt-2">
          Pots exportar la configuració actual o importar una nova configuració.
        </p>
      </div>

      <div className="flex gap-3">
        <button className="btn-primary inline-flex items-center gap-2">
          <Download className="w-4 h-4" />
          Exportar Config
        </button>
        <button className="btn-secondary inline-flex items-center gap-2">
          <Upload className="w-4 h-4" />
          Importar Config
        </button>
      </div>
    </div>
  )
}

export default ConvHiSIPConfig

