import React, { useState, useRef, useEffect } from 'react'
import { 
  Mic, 
  Play, 
  Pause, 
  Square, 
  Download, 
  Volume2, 
  Settings,
  Loader2,
  Copy,
  Trash2,
  Radio
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'
import AudioTest from '../components/AudioTest'

const EdgeTTSStandard = () => {
  const [text, setText] = useState('')
  const [selectedVoice, setSelectedVoice] = useState('')
  const [availableVoices, setAvailableVoices] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState(null)
  const [audioHistory, setAudioHistory] = useState([])
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false)
  const [settings, setSettings] = useState({
    speed: 1.0,
    volume: 1.0,
  })
  const [isLoadingVoices, setIsLoadingVoices] = useState(false)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterLanguage, setFilterLanguage] = useState('all')
  
  const audioRef = useRef(null)

  // Fetch Edge-TTS voices
  useEffect(() => {
    fetchEdgeVoices()
  }, [])

  const fetchEdgeVoices = async () => {
    try {
      setIsLoadingVoices(true)
      console.log('🔍 Sistema 1: Obtenint totes les veus Edge-TTS...')
      const response = await api.get('/api/edge-tts/voices')
      console.log('✅ Sistema 1: Veus rebudes:', response.data)
      
      // Processar veus rebudes - suportar múltiples formats
      const edgeVoices = response.data.voices || response.data.edge_voices || []
      
      if (Array.isArray(edgeVoices) && edgeVoices.length > 0) {
        setAvailableVoices(edgeVoices)
        setSelectedVoice(edgeVoices[0].id)
        toast.success(`${edgeVoices.length} veus Edge-TTS carregades`)
        console.log(`✅ ${edgeVoices.length} veus disponibles`)
      } else {
        console.warn('⚠️ No s\'han rebut veus, usant per defecte')
        throw new Error('No voices received')
      }
    } catch (error) {
      console.error('Error obteniendo voces Edge-TTS:', error)
      toast.error('Error al carregar veus Edge-TTS')
      
      // Voces por defecto
      const defaultVoices = [
        { id: 'es-ES-ElviraNeural', name: 'Elvira (Español)', locale: 'es-ES', gender: 'Female', language: 'es', description: 'Femenina - España' },
        { id: 'es-ES-AlvaroNeural', name: 'Alvaro (Español)', locale: 'es-ES', gender: 'Male', language: 'es', description: 'Masculina - España' },
        { id: 'en-US-AriaNeural', name: 'Aria (English)', locale: 'en-US', gender: 'Female', language: 'en', description: 'Female - US' },
        { id: 'en-US-GuyNeural', name: 'Guy (English)', locale: 'en-US', gender: 'Male', language: 'en', description: 'Male - US' }
      ]
      setAvailableVoices(defaultVoices)
      setSelectedVoice(defaultVoices[0].id)
    } finally {
      setIsLoadingVoices(false)
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
      console.log('🎯 Sistema 1: Generant amb veu:', selectedVoice)
      
      const response = await api.post('/api/edge-tts/synthesize', {
        text,
        voice_id: selectedVoice,
        language: availableVoices.find(v => v.id === selectedVoice)?.language || 'es',
        voice_settings: settings
      })

      console.log('✅ Respuesta Edge-TTS:', response.data)

      const audioData = {
        id: Date.now().toString(),
        text,
        voice: selectedVoice,
        audioUrl: `data:audio/wav;base64,${response.data.audio_base64}`,
        timestamp: new Date().toISOString(),
        channel: 'edge_tts_standard',
        quality: response.data.quality
      }

      setCurrentAudio(audioData)
      setAudioHistory(prev => [audioData, ...prev].slice(0, 50))
      toast.success('Audio Edge-TTS generat!')
      
      // Configurar àudio per reproducció manual
      if (audioRef.current) {
        audioRef.current.src = audioData.audioUrl
        audioRef.current.load() // Forçar recàrrega
        
        // Configurar events d'àudio
        audioRef.current.oncanplaythrough = () => {
          console.log('✅ Àudio carregat i llest per reproduir')
        }
        
        audioRef.current.onplay = () => {
          setIsPlaying(true)
          console.log('✅ Àudio reproduint')
        }
        
        audioRef.current.onpause = () => {
          setIsPlaying(false)
          console.log('⏸️ Àudio pausat')
        }
        
        audioRef.current.onended = () => {
          setIsPlaying(false)
          console.log('⏹️ Àudio acabat')
        }
        
        // Gestió d'errors de càrrega
        audioRef.current.onerror = (error) => {
          console.error('❌ Error carregant àudio:', error)
          toast.error('Error carregant àudio. Format no compatible.')
        }
      }
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar audio Edge-TTS')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePlayPause = async () => {
    if (audioRef.current) {
      try {
        if (isPlaying) {
          audioRef.current.pause()
        } else {
          await audioRef.current.play()
        }
      } catch (error) {
        console.error('❌ Error reproduint àudio:', error)
        toast.error('Error reproduint àudio. Prova de refrescar la pàgina.')
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
    link.download = `veuplus_edge_${audioData.id}.wav`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Audio descarregat')
  }

  const presetTexts = [
    "Hello, welcome to VeuPlus!",
    "Hola, bienvenido a VeuPlus!",
    "Bonjour, bienvenue à VeuPlus!",
    "Ciao, benvenuto a VeuPlus!"
  ]

  // Filtrar veus
  const filteredVoices = availableVoices.filter(voice => {
    const matchesSearch = voice.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (voice.description && voice.description.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesLanguage = filterLanguage === 'all' || voice.language === filterLanguage
    return matchesSearch && matchesLanguage
  })

  // Agrupar voces por idioma
  const voicesByLanguage = filteredVoices.reduce((acc, voice) => {
    const lang = voice.language
    if (!acc[lang]) acc[lang] = []
    acc[lang].push(voice)
    return acc
  }, {})

  // Obtenir idiomes únics
  const uniqueLanguages = [...new Set(availableVoices.map(voice => voice.language))].filter(Boolean)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center space-x-3">
          <Radio className="w-8 h-8 text-primary-500" />
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Veus Edge-TTS Estàndard</h1>
            <p className="mt-2 text-gray-600">
              Síntesi de veu multiidioma amb Microsoft Edge-TTS Neural
            </p>
          </div>
        </div>
      </div>

      {/* Audio Test Component */}
      <AudioTest />

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
              placeholder="Escriu el text que vols sintetitzar en qualsevol idioma..."
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
            
            {/* Preset Texts */}
            <div className="mt-4">
              <p className="text-sm text-gray-600 mb-2">Exemples multiidioma:</p>
              <div className="flex flex-wrap gap-2">
                {presetTexts.map((preset, index) => (
                  <button
                    key={index}
                    onClick={() => setText(preset)}
                    className="px-3 py-1 text-xs bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                  >
                    {preset}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Voice Selection */}
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Seleccionar Veu Edge-TTS</h2>
              {isLoadingVoices && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
            </div>
            
            {/* Filtres de cerca */}
            <div className="flex flex-col sm:flex-row gap-4 mb-6">
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Cercar veus per nom..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="input-field pl-10"
                  />
                </div>
              </div>
              <div className="sm:w-48">
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
            
            {/* Voces agrupadas por idioma */}
            <div className="space-y-4">
              {Object.entries(voicesByLanguage).map(([lang, voices]) => (
                <div key={lang} className="space-y-2">
                  <h3 className="text-sm font-medium text-gray-700 uppercase">{lang}</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {voices.map((voice) => (
                      <div
                        key={voice.id}
                        className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                          selectedVoice === voice.id
                            ? 'border-primary-500 bg-primary-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                        onClick={() => setSelectedVoice(voice.id)}
                      >
                        <div className="flex items-center space-x-2">
                          <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center">
                            <Radio className="w-4 h-4 text-white" />
                          </div>
                          <div>
                            <h4 className="font-medium text-sm text-gray-900">{voice.name}</h4>
                            <p className="text-xs text-gray-500">{voice.description}</p>
                          </div>
                        </div>
                      </div>
                    ))}
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
                disabled={isGenerating || !text.trim() || isLoadingVoices}
                className="btn-primary flex items-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGenerating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Radio className="w-5 h-5" />
                )}
                <span>{isGenerating ? 'Generant...' : 'Generar Audio Edge-TTS'}</span>
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
                <div className="bg-gradient-to-r from-primary-50 to-secondary-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-700 line-clamp-3">{currentAudio.text}</p>
                </div>
                
                <audio
                  ref={audioRef}
                  className="w-full"
                  controls
                  preload="auto"
                />
                
                <div className="flex items-center justify-between text-xs text-gray-500">
                  <span className="flex items-center space-x-1">
                    <Radio className="w-3 h-3 text-primary-500" />
                    <span>Edge-TTS</span>
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
                  <Radio className="w-8 h-8 mx-auto mb-2 opacity-50" />
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

export default EdgeTTSStandard
