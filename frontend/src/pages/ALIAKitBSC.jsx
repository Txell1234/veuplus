import React, { useState, useRef, useEffect } from 'react'
import { 
  Brain, 
  Play, 
  Pause, 
  Square, 
  Download, 
  Volume2, 
  Settings,
  Loader2,
  Copy,
  Trash2,
  Zap,
  Globe,
  Award,
  Database,
  Search
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const ALIAKitBSC = () => {
  const [text, setText] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState(null)
  const [audioHistory, setAudioHistory] = useState([])
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [settings, setSettings] = useState({
    speed: 1.0,
    volume: 1.0,
  })
  const [aliaStatus, setAliaStatus] = useState(null)
  const [aliaVoices, setAliaVoices] = useState([])
  const [isLoadingVoices, setIsLoadingVoices] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  
  const audioRef = useRef(null)

  useEffect(() => {
    fetchAliaVoices()
    checkAliaStatus()
  }, [])

  const fetchAliaVoices = async () => {
    try {
      setIsLoadingVoices(true)
      console.log('🔍 Sistema 3: Obtenint veus ALIA BSC Premium...')
      const response = await api.get('/api/alia/voices')
      console.log('✅ Sistema 3: Veus rebudes:', response.data)
      
      // Processar veus rebudes
      const voices = response.data.voices || []
      
      if (Array.isArray(voices) && voices.length > 0) {
        setAliaVoices(voices)
        setSelectedVoice(voices[0].id)
        toast.success(`${voices.length} veus ALIA BSC carregades`)
        console.log(`✅ ${voices.length} veus ALIA disponibles`)
      } else {
        console.warn('⚠️ No s\'han rebut veus ALIA, usant per defecte')
        throw new Error('No ALIA voices received')
      }
    } catch (error) {
      console.error('Error obteniendo voces ALIA:', error)
      toast.error('Error al carregar veus ALIA BSC')
      
      // Voces por defecto
      const defaultVoices = [
        {
          id: 'ca-ES-AlbaNeural',
          name: 'Alba Premium (Català)',
          gender: 'female',
          description: 'Voz femenina catalana premium con SEGRE',
          dialect: 'central',
          source: 'Barcelona Supercomputing Center'
        },
        {
          id: 'es-ES-AlvaroNeural',
          name: 'Álvaro Premium (Español)',
          gender: 'male',
          description: 'Voz masculina española premium',
          dialect: 'central',
          source: 'Barcelona Supercomputing Center'
        },
        {
          id: 'eu-ES-AinhoaNeural',
          name: 'Ainhoa Premium (Euskera)',
          gender: 'female',
          description: 'Voz femenina vasca premium',
          dialect: 'central',
          source: 'Barcelona Supercomputing Center'
        },
        {
          id: 'gl-ES-SabelaNeural',
          name: 'Sabela Premium (Galego)',
          gender: 'female',
          description: 'Voz femenina gallega premium',
          dialect: 'central',
          source: 'Barcelona Supercomputing Center'
        }
      ]
      setAliaVoices(defaultVoices)
      setSelectedVoice(defaultVoices[0].id)
    } finally {
      setIsLoadingVoices(false)
    }
  }

  const checkAliaStatus = async () => {
    try {
      const response = await api.get('/api/alia/status')
      setAliaStatus(response.data)
    } catch (error) {
      console.error('Error checking ALIA status:', error)
      setAliaStatus({ status: 'unavailable', error: 'ALIA Kit no disponible' })
    }
  }

  const handleGenerateSpeech = async () => {
    if (!text.trim()) {
      toast.error('Introdueix text per sintetitzar')
      return
    }

    if (!selectedVoice) {
      toast.error('Selecciona una veu')
      return
    }

    try {
      setIsGenerating(true)
      console.log('🎯 Generando con ALIA Kit BSC:', selectedVoice)
      
      // Determinar dialecte segons la veu seleccionada
      const selectedVoiceData = aliaVoices.find(v => v.id === selectedVoice)
      const dialect = selectedVoiceData?.dialect || 'central'
      const language = selectedVoiceData?.id.includes('spanish') ? 'es' : 
                      selectedVoiceData?.id.includes('basque') ? 'eu' :
                      selectedVoiceData?.id.includes('galician') ? 'gl' : 'ca'

      const response = await api.post('/api/alia/tts/synthesize', {
        text,
        language: language,
        dialect: dialect,
        voice_settings: settings
      })

      console.log('✅ Respuesta ALIA Kit:', response.data)

      const audioData = {
        id: Date.now().toString(),
        text,
        voice: selectedVoice,
        audioUrl: `data:audio/wav;base64,${response.data.audio_base64}`,
        timestamp: new Date().toISOString(),
        channel: 'alia_kit_bsc',
        quality: response.data.quality,
        provider: response.data.provider,
        source: 'Barcelona Supercomputing Center'
      }

      setCurrentAudio(audioData)
      setAudioHistory(prev => [audioData, ...prev].slice(0, 50))
      toast.success('Audio ALIA Kit BSC generat!')
      
      // Auto-play amb millor gestió d'errors
      if (audioRef.current) {
        audioRef.current.src = audioData.audioUrl
        audioRef.current.load() // Forçar recàrrega
        
        // Esperar que l'àudio es carregui
        audioRef.current.oncanplaythrough = async () => {
          try {
            await audioRef.current.play()
            setIsPlaying(true)
            console.log('✅ Àudio ALIA reproduint correctament')
          } catch (playError) {
            console.error('❌ Error reproduint àudio ALIA:', playError)
            toast.error('Error reproduint àudio. Prova de clicar Play manualment.')
          }
        }
        
        // Gestió d'errors de càrrega
        audioRef.current.onerror = (error) => {
          console.error('❌ Error carregant àudio ALIA:', error)
          toast.error('Error carregant àudio. Format no compatible.')
        }
      }
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar audio ALIA Kit BSC')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        audioRef.current.play()
        setIsPlaying(true)
      }
    }
  }

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsPlaying(false)
    }
  }

  const handleDownload = (audioData) => {
    if (!audioData) return
    
    const link = document.createElement('a')
    link.href = audioData.audioUrl
    link.download = `alia_kit_${audioData.id}.wav`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Audio descarregat')
  }

  const presetTexts = [
    "Bon dia, benvinguts a ALIA Kit del Barcelona Supercomputing Center!",
    "Aquesta és una prova de síntesi amb models oficials BSC.",
    "Les nostres veus utilitzen models MareNostrum per màxima qualitat.",
    "Gràcies per utilitzar ALIA Kit.",
    "Hola, bienvenidos a ALIA Kit del Barcelona Supercomputing Center!",
    "Kaixo, ALIA Kit-eko Barcelona Supercomputing Center-era ongi etorri!",
    "Ola, benvidos ao ALIA Kit do Barcelona Supercomputing Center!"
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3">
          <Brain className="w-8 h-8 text-blue-600" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ALIA Kit BSC</h1>
            <p className="mt-2 text-gray-600">
              Síntesi de veu oficial del Barcelona Supercomputing Center amb models MareNostrum
            </p>
          </div>
        </div>
        
        {/* ALIA Status */}
        {aliaStatus && (
          <div className={`mt-4 p-3 rounded-lg ${
            aliaStatus.status === 'active' ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'
          }`}>
            <div className="flex items-center space-x-2">
              <Award className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium">
                ALIA Kit: {aliaStatus.status === 'active' ? 'Disponible' : 'En desenvolupament'}
              </span>
            </div>
            {aliaStatus.status !== 'active' && (
              <p className="text-xs text-gray-600 mt-1">
                Models BSC en desenvolupament. Estructura implementada.
              </p>
            )}
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Text Input */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Text a Sintetitzar</h2>
              <div className="flex space-x-2">
                <button
                  onClick={() => navigator.clipboard.writeText(text)}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Copiar"
                >
                  <Copy className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setText('')}
                  className="p-2 text-gray-400 hover:text-gray-600"
                  title="Esborrar"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
            
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Escriu el text que vols sintetitzar amb ALIA Kit BSC..."
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            />
            
            {/* Preset Texts */}
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-2">Exemples multilingües:</p>
              <div className="flex flex-wrap gap-2">
                {presetTexts.map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => setText(preset)}
                    className="px-3 py-1 text-xs bg-blue-100 hover:bg-blue-200 rounded-full transition-colors"
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Voice Selection */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Seleccionar Veu ALIA Kit BSC</h2>
            
            {/* Filtre de cerca */}
            <div className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Cercar veus ALIA..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="input-field pl-10"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {aliaVoices.filter(voice => 
                voice.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                (voice.description && voice.description.toLowerCase().includes(searchTerm.toLowerCase()))
              ).map((voice) => (
                <div
                  key={voice.id}
                  className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedVoice === voice.id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedVoice(voice.id)}
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center">
                      <Brain className="w-5 h-5 text-white" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{voice.name}</h3>
                      <p className="text-sm text-gray-500">{voice.gender === 'male' ? 'Masculina' : 'Femenina'}</p>
                      <p className="text-xs text-gray-400 mt-1">{voice.description}</p>
                      <div className="flex items-center space-x-1 mt-1">
                        <Database className="w-3 h-3 text-blue-500" />
                        <span className="text-xs text-blue-600">{voice.source}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Controls */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Controls</h2>

            <div className="flex items-center space-x-4">
              <button
                onClick={handleGenerateSpeech}
                disabled={isGenerating || !text.trim()}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Brain className="w-5 h-5" />
                )}
                <span>{isGenerating ? 'Generant...' : 'Generar Audio ALIA Kit'}</span>
              </button>

              {currentAudio && (
                <>
                  <button
                    onClick={handlePlayPause}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>

                  <button
                    onClick={handleStop}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <Square className="w-5 h-5" />
                  </button>

                  <button
                    onClick={() => handleDownload(currentAudio)}
                    className="btn-secondary flex items-center space-x-2"
                  >
                    <Download className="w-5 h-5" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Audio Player & History */}
        <div className="space-y-6">
          {/* Current Audio */}
          {currentAudio && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Audio Actual</h2>
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-3 rounded-lg">
                  <p className="text-sm text-gray-700 line-clamp-3">{currentAudio.text}</p>
                </div>
                
                <audio
                  ref={audioRef}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onEnded={() => setIsPlaying(false)}
                  className="w-full"
                  controls
                />
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Brain className="w-3 h-3 text-blue-600" />
                    <span>ALIA Kit BSC</span>
                  </span>
                  <span>{new Date(currentAudio.timestamp).toLocaleString()}</span>
                </div>
              </div>
            </div>
          )}

          {/* History */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Historial</h2>
              <span className="text-sm text-gray-500">{audioHistory.length} audios</span>
            </div>
            
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {audioHistory.map((audio) => (
                <div key={audio.id} className="p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-700 line-clamp-2 mb-2">{audio.text}</p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-gray-500">
                      {new Date(audio.timestamp).toLocaleString()}
                    </span>
                    <div className="flex space-x-2">
                      <button
                        onClick={() => {
                          setCurrentAudio(audio)
                          if (audioRef.current) {
                            audioRef.current.src = audio.audioUrl
                            audioRef.current.play()
                            setIsPlaying(true)
                          }
                        }}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Reproduir"
                      >
                        <Play className="w-3 h-3" />
                      </button>
                      <button
                        onClick={() => handleDownload(audio)}
                        className="p-1 text-gray-400 hover:text-gray-600"
                        title="Descarregar"
                      >
                        <Download className="w-3 h-3" />
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              
              {audioHistory.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">No hi ha audios generats</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ALIAKitBSC
