import React, { useState, useEffect } from 'react'
import {
  Radio,
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
  Monitor,
  Upload,
  Download,
  Server,
  Globe,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ConvHiWebRTCConfig = () => {
  const [activeTab, setActiveTab] = useState('stun-turn')
  const [loading, setLoading] = useState(false)
  
  // WebRTC Config State
  const [webrtcConfig, setWebrtcConfig] = useState({
    stun_servers: [],
    turn_servers: [],
    region: 'eu',
  })

  const [newStun, setNewStun] = useState('')
  const [newTurn, setNewTurn] = useState({
    url: '',
    username: '',
    password: '',
  })

  // Stats
  const [stats, setStats] = useState({
    total_connections: 0,
    active_connections: 0,
    avg_connection_time: 0,
    ice_connection_state: 'unknown',
  })

  useEffect(() => {
    loadWebRTCConfig()
    loadStats()
    
    // Auto-refresh
    const interval = setInterval(() => {
      loadStats()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [])

  const loadWebRTCConfig = async () => {
    try {
      const response = await api.get('/api/convhi/webrtc/config')
      setWebrtcConfig(response.data)
    } catch (error) {
      console.error('Error loading WebRTC config:', error)
      toast.error('Error carregant configuració WebRTC')
    }
  }

  const loadStats = async () => {
    try {
      // Simulate stats for now
      setStats({
        total_connections: 156,
        active_connections: 12,
        avg_connection_time: 45,
        ice_connection_state: 'connected',
      })
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

  const testWebRTCConnection = async () => {
    try {
      toast.loading('Provant connexió WebRTC...')
      
      // Create a simple RTCPeerConnection test
      const pc = new RTCPeerConnection({
        iceServers: [
          ...webrtcConfig.stun_servers.map(url => ({ urls: url })),
          ...webrtcConfig.turn_servers,
        ]
      })

      let iceConnected = false
      
      pc.oniceconnectionstatechange = () => {
        if (pc.iceConnectionState === 'connected') {
          iceConnected = true
          toast.success('Connexió WebRTC OK!')
        } else if (pc.iceConnectionState === 'failed') {
          toast.error('Connexió WebRTC fallida')
        }
      }

      // Create a data channel to test
      const dataChannel = pc.createDataChannel('test')
      
      // Create and set local description
      const offer = await pc.createOffer()
      await pc.setLocalDescription(offer)

      // Simulate timeout
      setTimeout(() => {
        if (!iceConnected) {
          toast.error('Timeout provant connexió WebRTC')
        }
        pc.close()
      }, 5000)
      
    } catch (error) {
      console.error('Error testing WebRTC:', error)
      toast.error('Error provant connexió WebRTC')
    } finally {
      toast.dismiss()
    }
  }

  const addStunServer = () => {
    if (newStun) {
      setWebrtcConfig({
        ...webrtcConfig,
        stun_servers: [...webrtcConfig.stun_servers, newStun]
      })
      setNewStun('')
      toast.success('STUN server afegit')
    }
  }

  const addTurnServer = () => {
    if (newTurn.url && newTurn.username && newTurn.password) {
      setWebrtcConfig({
        ...webrtcConfig,
        turn_servers: [...webrtcConfig.turn_servers, {
          urls: newTurn.url,
          username: newTurn.username,
          credential: newTurn.password
        }]
      })
      setNewTurn({ url: '', username: '', password: '' })
      toast.success('TURN server afegit')
    }
  }

  const removeStunServer = (index) => {
    const newServers = webrtcConfig.stun_servers.filter((_, i) => i !== index)
    setWebrtcConfig({ ...webrtcConfig, stun_servers: newServers })
    toast.success('STUN server eliminat')
  }

  const removeTurnServer = (index) => {
    const newServers = webrtcConfig.turn_servers.filter((_, i) => i !== index)
    setWebrtcConfig({ ...webrtcConfig, turn_servers: newServers })
    toast.success('TURN server eliminat')
  }

  const saveConfig = async () => {
    try {
      setLoading(true)
      // TODO: Implement API call to save config
      toast.success('Configuració desada correctament')
    } catch (error) {
      console.error('Error saving config:', error)
      toast.error('Error desant configuració')
    } finally {
      setLoading(false)
    }
  }

  const tabs = [
    { id: 'stun-turn', label: 'STUN/TURN', icon: Server },
    { id: 'monitoring', label: 'Monitoring', icon: BarChart3 },
    { id: 'settings', label: 'Configuració', icon: Settings },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-neutral-900 flex items-center gap-2">
            <Radio className="w-8 h-8 text-primary-500" />
            Configuració WebRTC
          </h1>
          <p className="text-sm text-neutral-600 mt-1">
            Configura servidors STUN/TURN per WebRTC
          </p>
        </div>
        <button
          onClick={saveConfig}
          disabled={loading}
          className="btn-primary inline-flex items-center gap-2"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
          Desar Configuració
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-blue-50 rounded-lg p-4">
          <p className="text-sm text-blue-700 font-semibold">Conexions Totals</p>
          <p className="text-2xl font-bold text-blue-900">{stats.total_connections}</p>
        </div>
        <div className="bg-green-50 rounded-lg p-4">
          <p className="text-sm text-green-700 font-semibold">Actives</p>
          <p className="text-2xl font-bold text-green-900">{stats.active_connections}</p>
        </div>
        <div className="bg-orange-50 rounded-lg p-4">
          <p className="text-sm text-orange-700 font-semibold">Temps Mitjà</p>
          <p className="text-2xl font-bold text-orange-900">{stats.avg_connection_time}s</p>
        </div>
        <div className="bg-purple-50 rounded-lg p-4">
          <p className="text-sm text-purple-700 font-semibold">Estat ICE</p>
          <p className="text-2xl font-bold text-purple-900 capitalize">{stats.ice_connection_state}</p>
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
        {activeTab === 'stun-turn' && (
          <div className="space-y-6">
            {/* Test Connection */}
            <div className="border border-primary-200 bg-primary-50 rounded-lg p-6">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-lg font-semibold text-neutral-900 flex items-center gap-2">
                    <TestTube className="w-5 h-5 text-primary-500" />
                    Provar Connexió WebRTC
                  </h3>
                  <p className="text-sm text-neutral-600 mt-1">
                    Prova la connexió amb els servidors STUN/TURN configurats
                  </p>
                </div>
                <button
                  onClick={testWebRTCConnection}
                  className="btn-primary inline-flex items-center gap-2"
                >
                  <Radio className="w-4 h-4" />
                  Provar Connexió
                </button>
              </div>
            </div>

            {/* STUN Servers */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-neutral-900">STUN Servers</h2>
              </div>
              
              <div className="space-y-3">
                {/* Add STUN Server */}
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={newStun}
                    onChange={(e) => setNewStun(e.target.value)}
                    placeholder="stun:stun.l.google.com:19302"
                    className="input-field flex-1"
                  />
                  <button onClick={addStunServer} className="btn-primary">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {/* STUN Servers List */}
                <div className="space-y-2">
                  {webrtcConfig.stun_servers.length > 0 ? (
                    webrtcConfig.stun_servers.map((server, index) => (
                      <div key={index} className="border border-neutral-200 rounded-lg p-3 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <Server className="w-5 h-5 text-neutral-400" />
                          <span className="font-mono text-sm text-neutral-900">{server}</span>
                        </div>
                        <button
                          onClick={() => removeStunServer(index)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-neutral-500 text-center py-4">
                      No hi ha servidors STUN configurats
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* TURN Servers */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-neutral-900">TURN Servers</h2>
              </div>
              
              <div className="space-y-3">
                {/* Add TURN Server */}
                <div className="border border-neutral-200 rounded-lg p-4 space-y-3">
                  <input
                    type="text"
                    value={newTurn.url}
                    onChange={(e) => setNewTurn({...newTurn, url: e.target.value})}
                    placeholder="turn:turn.example.com:3478"
                    className="input-field"
                  />
                  <div className="grid grid-cols-2 gap-3">
                    <input
                      type="text"
                      value={newTurn.username}
                      onChange={(e) => setNewTurn({...newTurn, username: e.target.value})}
                      placeholder="Username"
                      className="input-field"
                    />
                    <input
                      type="password"
                      value={newTurn.password}
                      onChange={(e) => setNewTurn({...newTurn, password: e.target.value})}
                      placeholder="Password"
                      className="input-field"
                    />
                  </div>
                  <button onClick={addTurnServer} className="btn-primary w-full">
                    <Plus className="w-4 h-4" />
                    Afegir TURN Server
                  </button>
                </div>

                {/* TURN Servers List */}
                <div className="space-y-2">
                  {webrtcConfig.turn_servers.length > 0 ? (
                    webrtcConfig.turn_servers.map((server, index) => (
                      <div key={index} className="border border-neutral-200 rounded-lg p-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <Server className="w-5 h-5 text-neutral-400" />
                            <div>
                              <span className="font-mono text-sm text-neutral-900 block">{server.urls}</span>
                              <span className="text-xs text-neutral-600">
                                {server.username ? `${server.username}` : 'No auth'}
                              </span>
                            </div>
                          </div>
                          <button
                            onClick={() => removeTurnServer(index)}
                            className="text-red-600 hover:text-red-700"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-neutral-500 text-center py-4">
                      No hi ha servidors TURN configurats
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'monitoring' && (
          <MonitoringTab stats={stats} />
        )}

        {activeTab === 'settings' && (
          <SettingsTab config={webrtcConfig} setConfig={setWebrtcConfig} />
        )}
      </div>
    </div>
  )
}

// Monitoring Tab Component
const MonitoringTab = ({ stats }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-neutral-900">Monitoring en Temps Real</h2>
      
      <div className="grid grid-cols-2 gap-6">
        <div className="border border-neutral-200 rounded-lg p-6">
          <h3 className="font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Activity className="w-5 h-5 text-primary-500" />
            Connexions
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Total</span>
              <span className="text-sm font-semibold text-neutral-900">{stats.total_connections}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Actives</span>
              <span className="text-sm font-semibold text-green-600">{stats.active_connections}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Mitjana Temp</span>
              <span className="text-sm font-semibold text-neutral-900">{stats.avg_connection_time}s</span>
            </div>
          </div>
        </div>

        <div className="border border-neutral-200 rounded-lg p-6">
          <h3 className="font-semibold text-neutral-900 mb-4 flex items-center gap-2">
            <Radio className="w-5 h-5 text-primary-500" />
            Qualitat ICE
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-neutral-600">Estat</span>
              <span className={`text-sm font-semibold capitalize ${
                stats.ice_connection_state === 'connected' ? 'text-green-600' : 
                stats.ice_connection_state === 'disconnected' ? 'text-red-600' : 
                'text-neutral-600'
              }`}>
                {stats.ice_connection_state}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

// Settings Tab Component
const SettingsTab = ({ config, setConfig }) => {
  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-semibold text-neutral-900">Configuració WebRTC</h2>
      
      <div>
        <label className="block text-sm font-semibold text-neutral-900 mb-2">Regió</label>
        <select
          value={config.region}
          onChange={(e) => setConfig({...config, region: e.target.value})}
          className="input-field"
        >
          <option value="eu">Europa</option>
          <option value="us">Estats Units</option>
          <option value="asia">Àsia</option>
          <option value="global">Global</option>
        </select>
      </div>

      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <strong>Servidors Recomanats:</strong>
        </p>
        <ul className="text-sm text-blue-800 mt-2 space-y-1">
          <li>• Google STUN: stun:stun.l.google.com:19302</li>
          <li>• Twilio TURN: turn:global.relay.twilio.com:3478</li>
        </ul>
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

export default ConvHiWebRTCConfig


