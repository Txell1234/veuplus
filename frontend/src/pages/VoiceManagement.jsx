import React, { useState, useEffect } from 'react'
import { 
  Volume2, 
  Play, 
  Pause, 
  Search,
  Filter,
  Radio,
  Zap,
  Brain,
  Loader2
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const VoiceManagement = () => {
  const [allVoices, setAllVoices] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [filterSystem, setFilterSystem] = useState('all')
  const [filterLanguage, setFilterLanguage] = useState('all')
  const [isLoading, setIsLoading] = useState(true)
  const [isPlaying, setIsPlaying] = useState(null)
  const [audioElement, setAudioElement] = useState(null)

  // Carregar totes les veus dels 3 sistemes
  useEffect(() => {
    fetchAllVoices()
  }, [])

  const fetchAllVoices = async () => {
    try {
      setIsLoading(true)
      console.log('🔍 Carregant totes les veus dels 3 sistemes...')
      
      // Obtenir veus de cada sistema
      const [edgeResponse, catalanResponse, aliaResponse] = await Promise.all([
        api.get('/api/edge-tts/voices'),
        api.get('/api/catalan/voices'),
        api.get('/api/alia/voices')
      ])

      const edgeVoices = edgeResponse.data.voices || []
      const catalanVoices = catalanResponse.data.voices || []
      const aliaVoices = aliaResponse.data.voices || []

      // Afegir informació del sistema a cada veu
      const voicesWithSystem = [
        ...edgeVoices.map(voice => ({ ...voice, system: 'edge-tts', systemName: 'Edge-TTS Standard' })),
        ...catalanVoices.map(voice => ({ ...voice, system: 'catalan', systemName: 'Català Hiperrealista' })),
        ...aliaVoices.map(voice => ({ ...voice, system: 'alia', systemName: 'ALIA BSC Premium' }))
      ]

      setAllVoices(voicesWithSystem)
      console.log(`✅ Carregades ${voicesWithSystem.length} veus totals`)
      toast.success(`${voicesWithSystem.length} veus carregades de 3 sistemes`)
    } catch (error) {
      console.error('Error carregant veus:', error)
      toast.error('Error carregant veus')
    } finally {
      setIsLoading(false)
    }
  }

  // Filtrar veus
  const filteredVoices = allVoices.filter(voice => {
    const matchesSearch = voice.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (voice.description && voice.description.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesSystem = filterSystem === 'all' || voice.system === filterSystem
    const matchesLanguage = filterLanguage === 'all' || voice.language === filterLanguage
    return matchesSearch && matchesSystem && matchesLanguage
  })

  // Reproduir àudio
  const handleVoicePlay = async (voice) => {
    if (isPlaying === voice.id) {
      if (audioElement) {
        audioElement.pause()
        setIsPlaying(null)
      }
      return
    }

    if (audioElement) {
      audioElement.pause()
    }

    try {
      let response
      const testText = 'Hola, aquesta és una prova de la meva veu.'

      if (voice.system === 'edge-tts') {
        response = await api.post('/api/edge-tts/synthesize', {
          text: testText,
          voice_id: voice.id,
          language: voice.language || 'es'
        })
      } else if (voice.system === 'catalan') {
        response = await api.post('/api/catalan/synthesize', {
          text: testText,
          voice_id: voice.id,
          language: 'ca'
        })
      } else if (voice.system === 'alia') {
        response = await api.post('/api/alia/tts/synthesize', {
          text: testText,
          language: voice.language || 'ca'
        })
      }

      if (response.data.success) {
        const audioUrl = `data:audio/wav;base64,${response.data.audio_base64}`
        const audio = new Audio(audioUrl)
        
        audio.oncanplaythrough = () => {
          audio.play()
          setAudioElement(audio)
          setIsPlaying(voice.id)
          toast.success(`Reproduint: ${voice.name}`)
        }
        
        audio.onended = () => setIsPlaying(null)
        audio.onerror = () => {
          toast.error('Error reproduint àudio')
          setIsPlaying(null)
        }
      }
    } catch (error) {
      console.error('Error generant àudio:', error)
      toast.error('Error generant àudio')
    }
  }

  // Obtenir idiomes únics
  const uniqueLanguages = [...new Set(allVoices.map(voice => voice.language))].filter(Boolean)

  // Obtenir icona del sistema
  const getSystemIcon = (system) => {
    switch (system) {
      case 'edge-tts': return Radio
      case 'catalan': return Zap
      case 'alia': return Brain
      default: return Volume2
    }
  }

  // Obtenir color del sistema
  const getSystemColor = (system) => {
    switch (system) {
      case 'edge-tts': return 'from-blue-500 to-blue-600'
      case 'catalan': return 'from-yellow-500 to-orange-600'
      case 'alia': return 'from-purple-500 to-purple-600'
      default: return 'from-gray-500 to-gray-600'
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3">
          <Volume2 className="w-8 h-8 text-primary-500" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Gestió de Veus</h1>
            <p className="mt-2 text-gray-600">
              Administra i prova totes les veus dels 3 sistemes: Edge-TTS, Català Hiperrealista i ALIA BSC
            </p>
          </div>
        </div>
      </div>

      {/* Estadístiques */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
              <Radio className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Edge-TTS</p>
              <p className="text-lg font-semibold text-gray-900">
                {allVoices.filter(v => v.system === 'edge-tts').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-yellow-500 to-orange-600 rounded-lg flex items-center justify-center">
              <Zap className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Català</p>
              <p className="text-lg font-semibold text-gray-900">
                {allVoices.filter(v => v.system === 'catalan').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Brain className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">ALIA BSC</p>
              <p className="text-lg font-semibold text-gray-900">
                {allVoices.filter(v => v.system === 'alia').length}
              </p>
            </div>
          </div>
        </div>
        
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-lg flex items-center justify-center">
              <Volume2 className="w-5 h-5 text-white" />
            </div>
            <div>
              <p className="text-sm text-gray-600">Total</p>
              <p className="text-lg font-semibold text-gray-900">{allVoices.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="card">
        <div className="flex flex-col lg:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Cercar veus per nom o descripció..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="input-field pl-10"
              />
            </div>
          </div>
          
          <div className="lg:w-48">
            <div className="relative">
              <Filter className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <select
                value={filterSystem}
                onChange={(e) => setFilterSystem(e.target.value)}
                className="input-field pl-10 appearance-none"
              >
                <option value="all">Tots els sistemes</option>
                <option value="edge-tts">Edge-TTS Standard</option>
                <option value="catalan">Català Hiperrealista</option>
                <option value="alia">ALIA BSC Premium</option>
              </select>
            </div>
          </div>
          
          <div className="lg:w-48">
            <select
              value={filterLanguage}
              onChange={(e) => setFilterLanguage(e.target.value)}
              className="input-field"
            >
              <option value="all">Tots els idiomes</option>
              {uniqueLanguages.map(lang => (
                <option key={lang} value={lang}>
                  {lang.toUpperCase()}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Llista de veus */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="card text-center py-12">
            <Loader2 className="w-8 h-8 mx-auto mb-4 animate-spin text-primary-500" />
            <p className="text-gray-600">Carregant veus...</p>
          </div>
        ) : filteredVoices.length === 0 ? (
          <div className="card text-center py-12">
            <Volume2 className="w-12 h-12 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm || filterSystem !== 'all' || filterLanguage !== 'all' 
                ? 'No s\'han trobat veus' 
                : 'No hi ha veus disponibles'
              }
            </h3>
            <p className="text-gray-500">
              {searchTerm || filterSystem !== 'all' || filterLanguage !== 'all'
                ? 'Prova d\'ajustar els filtres de cerca.'
                : 'Les veus es carregaran automàticament.'
              }
            </p>
          </div>
        ) : (
          filteredVoices.map((voice) => {
            const SystemIcon = getSystemIcon(voice.system)
            const systemColor = getSystemColor(voice.system)
            
            return (
              <div key={`${voice.system}-${voice.id}`} className="card hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 bg-gradient-to-br ${systemColor} rounded-full flex items-center justify-center`}>
                      <SystemIcon className="w-6 h-6 text-white" />
                    </div>
                    
                    <div>
                      <h3 className="font-semibold text-gray-900">{voice.name}</h3>
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <span className="font-medium">{voice.systemName}</span>
                        <span>•</span>
                        <span className="uppercase">{voice.language || 'unknown'}</span>
                        {voice.gender && (
                          <>
                            <span>•</span>
                            <span>{voice.gender}</span>
                          </>
                        )}
                      </div>
                      {voice.description && (
                        <p className="text-sm text-gray-600 mt-1">{voice.description}</p>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleVoicePlay(voice)}
                      className="p-3 text-gray-400 hover:text-primary-600 transition-colors"
                      title="Reproduir mostra"
                    >
                      {isPlaying === voice.id ? (
                        <Pause className="w-5 h-5" />
                      ) : (
                        <Play className="w-5 h-5" />
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

export default VoiceManagement