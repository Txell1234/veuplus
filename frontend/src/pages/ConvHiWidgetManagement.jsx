import React, { useEffect, useState } from 'react'
import {
  Globe,
  Shield,
  BarChart3,
  Plus,
  Trash2,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  RefreshCw,
  Download,
  Upload,
  Settings,
  Eye,
  EyeOff,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ConvHiWidgetManagement = () => {
  const [allowlist, setAllowlist] = useState([])
  const [newDomain, setNewDomain] = useState('')
  const [stats, setStats] = useState({
    total_widgets: 0,
    active_domains: 0,
    total_requests: 0,
    last_24h_requests: 0,
    requests_by_domain: {}
  })
  const [loading, setLoading] = useState(false)
  const [showAddForm, setShowAddForm] = useState(false)
  const [bulkDomains, setBulkDomains] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      const [allowlistResponse, statsResponse] = await Promise.all([
        api.get('/api/convhi/widget-management/allowlist'),
        api.get('/api/convhi/widget-management/stats/detailed')
      ])

      setAllowlist(allowlistResponse.data.domains || [])
      setStats(statsResponse.data.stats || {})
    } catch (error) {
      console.error('Error loading data:', error)
      toast.error('Error carregant dades')
    } finally {
      setLoading(false)
    }
  }

  const addDomain = async () => {
    if (!newDomain.trim()) {
      toast.error('Introdueix un domini vàlid')
      return
    }

    try {
      const response = await api.post('/api/convhi/widget-management/allowlist', {
        domains: [newDomain.trim()],
        action: 'add'
      })

      if (response.data.success) {
        setAllowlist(response.data.domains)
        setNewDomain('')
        setShowAddForm(false)
        toast.success('Domini afegit correctament')
      }
    } catch (error) {
      console.error('Error adding domain:', error)
      toast.error('Error afegint domini')
    }
  }

  const removeDomain = async (domain) => {
    try {
      const response = await api.post('/api/convhi/widget-management/allowlist', {
        domains: [domain],
        action: 'remove'
      })

      if (response.data.success) {
        setAllowlist(response.data.domains)
        toast.success('Domini eliminat correctament')
      }
    } catch (error) {
      console.error('Error removing domain:', error)
      toast.error('Error eliminant domini')
    }
  }

  const addBulkDomains = async () => {
    if (!bulkDomains.trim()) {
      toast.error('Introdueix dominis vàlids')
      return
    }

    const domains = bulkDomains
      .split('\n')
      .map(d => d.trim())
      .filter(d => d)

    if (domains.length === 0) {
      toast.error('No hi ha dominis vàlids')
      return
    }

    try {
      const response = await api.post('/api/convhi/widget-management/allowlist', {
        domains: domains,
        action: 'add'
      })

      if (response.data.success) {
        setAllowlist(response.data.domains)
        setBulkDomains('')
        toast.success(`${domains.length} dominis afegits correctament`)
      }
    } catch (error) {
      console.error('Error adding bulk domains:', error)
      toast.error('Error afegint dominis')
    }
  }

  const replaceAllowlist = async () => {
    if (!bulkDomains.trim()) {
      toast.error('Introdueix dominis vàlids')
      return
    }

    const domains = bulkDomains
      .split('\n')
      .map(d => d.trim())
      .filter(d => d)

    if (domains.length === 0) {
      toast.error('No hi ha dominis vàlids')
      return
    }

    if (!confirm(`Estàs segur que vols reemplaçar tots els dominis permesos? Això eliminarà ${allowlist.length} dominis actuals.`)) {
      return
    }

    try {
      const response = await api.post('/api/convhi/widget-management/allowlist', {
        domains: domains,
        action: 'replace'
      })

      if (response.data.success) {
        setAllowlist(response.data.domains)
        setBulkDomains('')
        toast.success(`Allowlist reemplaçada amb ${domains.length} dominis`)
      }
    } catch (error) {
      console.error('Error replacing allowlist:', error)
      toast.error('Error reemplaçant allowlist')
    }
  }

  const exportAllowlist = () => {
    const data = {
      domains: allowlist,
      exported_at: new Date().toISOString(),
      total_domains: allowlist.length
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `convhi-allowlist-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast.success('Allowlist exportada correctament')
  }

  const importAllowlist = (event) => {
    const file = event.target.files[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result)
        const domains = data.domains || []
        
        if (domains.length === 0) {
          toast.error('El fitxer no conté dominis vàlids')
          return
        }

        setBulkDomains(domains.join('\n'))
        toast.success(`${domains.length} dominis carregats del fitxer`)
      } catch (error) {
        console.error('Error parsing file:', error)
        toast.error('Error llegint el fitxer')
      }
    }
    reader.readAsText(file)
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-neutral-900 flex items-center gap-2">
            <Shield className="w-6 h-6 text-primary-500" />
            Gestió de Widgets ConvHi
          </h1>
          <p className="text-sm text-neutral-600">
            Gestiona dominis permesos, estadístiques i configuració de widgets.
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          <button
            onClick={loadData}
            disabled={loading}
            className="btn-secondary inline-flex items-center gap-2"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            Actualitzar
          </button>
        </div>
      </div>

      {/* Estadístiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-blue-100">
              <Globe className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Dominis Actius</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.active_domains}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-green-100">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Peticions Totals</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total_requests}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-orange-100">
              <RefreshCw className="w-6 h-6 text-orange-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Últimes 24h</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.last_24h_requests}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center">
            <div className="p-3 rounded-lg bg-purple-100">
              <Settings className="w-6 h-6 text-purple-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Widgets Totals</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.total_widgets}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Gestió d'allowlist */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Llista de dominis */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-neutral-900">Dominis Permesos</h3>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowAddForm(!showAddForm)}
                className="btn-primary text-sm inline-flex items-center gap-1"
              >
                <Plus className="w-4 h-4" />
                Afegir
              </button>
              <button
                onClick={exportAllowlist}
                className="btn-secondary text-sm inline-flex items-center gap-1"
              >
                <Download className="w-4 h-4" />
                Exportar
              </button>
            </div>
          </div>

          {/* Formulari d'afegir domini */}
          {showAddForm && (
            <div className="mb-4 p-4 bg-neutral-50 rounded-lg">
              <div className="flex items-center gap-2">
                <input
                  type="text"
                  className="input-field flex-1"
                  placeholder="example.com"
                  value={newDomain}
                  onChange={(e) => setNewDomain(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addDomain()}
                />
                <button
                  onClick={addDomain}
                  className="btn-primary text-sm"
                >
                  Afegir
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="btn-secondary text-sm"
                >
                  Cancel·lar
                </button>
              </div>
            </div>
          )}

          {/* Llista de dominis */}
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {allowlist.length === 0 ? (
              <p className="text-sm text-neutral-500 text-center py-4">
                No hi ha dominis configurats
              </p>
            ) : (
              allowlist.map((domain, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 bg-white border border-neutral-200 rounded-lg"
                >
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-sm font-medium text-neutral-900">{domain}</span>
                  </div>
                  <button
                    onClick={() => removeDomain(domain)}
                    className="p-1 text-red-500 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Gestió massiva */}
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Gestió Massiva</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-neutral-800 mb-2">
                Importar/Editar Dominis
              </label>
              <textarea
                className="input-field min-h-[200px]"
                placeholder="example.com&#10;subdomain.example.com&#10;localhost:3000"
                value={bulkDomains}
                onChange={(e) => setBulkDomains(e.target.value)}
              />
              <p className="text-xs text-neutral-500 mt-1">
                Un domini per línia. Pots importar des d'un fitxer JSON.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="file"
                accept=".json"
                onChange={importAllowlist}
                className="hidden"
                id="import-file"
              />
              <label
                htmlFor="import-file"
                className="btn-secondary text-sm inline-flex items-center gap-1 cursor-pointer"
              >
                <Upload className="w-4 h-4" />
                Importar JSON
              </label>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={addBulkDomains}
                disabled={!bulkDomains.trim()}
                className="btn-primary text-sm flex-1"
              >
                Afegir Dominis
              </button>
              <button
                onClick={replaceAllowlist}
                disabled={!bulkDomains.trim()}
                className="btn-secondary text-sm flex-1"
              >
                Reemplaçar Tot
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Estadístiques per domini */}
      {Object.keys(stats.requests_by_domain || {}).length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-neutral-900 mb-4">Peticions per Domini</h3>
          <div className="space-y-2">
            {Object.entries(stats.requests_by_domain || {})
              .sort(([,a], [,b]) => b - a)
              .map(([domain, count]) => (
                <div
                  key={domain}
                  className="flex items-center justify-between p-3 bg-white border border-neutral-200 rounded-lg"
                >
                  <div className="flex items-center gap-2">
                    <Globe className="w-4 h-4 text-neutral-500" />
                    <span className="text-sm font-medium text-neutral-900">{domain}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-sm text-neutral-600">{count} peticions</span>
                    <div className={`w-2 h-2 rounded-full ${
                      allowlist.includes(domain) ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Informació de seguretat */}
      <div className="card bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-blue-600 mt-0.5" />
          <div>
            <h4 className="text-sm font-semibold text-blue-800 mb-1">Informació de Seguretat</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Només els dominis de l'allowlist poden carregar widgets ConvHi</li>
              <li>• Els widgets utilitzen URLs signades per seguretat</li>
              <li>• Les peticions es registren per auditoria</li>
              <li>• Revisa regularment l'allowlist per mantenir la seguretat</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ConvHiWidgetManagement
