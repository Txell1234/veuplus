import React, { useState, useRef, useEffect } from 'react'
import { 
  Play, 
  Pause, 
  Square, 
  Download, 
  Volume2, 
  Loader2,
  Radio,
  Search
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const EdgeTTSStandardSimple = () => {
  const [text, setText] = useState('Hola, aquesta és una prova de síntesi de veu.')
  const [selectedVoice, setSelectedVoice] = useState('')
  const [availableVoices, setAvailableVoices] = useState([])
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState(null)
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
      console.log('🔍 Carregant veus Edge-TTS...')
      const response = await api.get('/api/edge-tts/voices')
      console.log('✅ Veus rebudes:', response.data)
      
      const voices = response.data.voices || response.data.edge_voices || []
      
      if (Array.isArray(voices) && voices.length > 0) {
        setAvailableVoices(voices)
        setSelectedVoice(voices[0].id)
        toast.success(`${voices.length} veus Edge-TTS carregades`)
        console.log(`✅ ${voices.length} veus disponibles`)
      } else {
        console.warn('⚠️ No s\'han rebut veus')
        toast.error('No s\'han pogut carregar les veus')
      }
    } catch (error) {
      console.error('Error carregant veus:', error)
      toast.error('Error al carregar veus Edge-TTS')
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
      console.log('🎯 Generant amb veu:', selectedVoice)
      
      const response = await api.post('/api/edge-tts/synthesize', {
        text,
        voice_id: selectedVoice
      })

      console.log('✅ Resposta Edge-TTS:', response.data)

      if (response.data.success && response.data.audio_base64) {
        const mimeType = response.data.mime_type || 'audio/mpeg'
        const audioData = {
          id: Date.now().toString(),
          text,
          voice: selectedVoice,
          audioUrl: `data:${mimeType};base64,${response.data.audio_base64}`,
          timestamp: new Date().toISOString()
        }

        setCurrentAudio(audioData)
        toast.success('Audio Edge-TTS generat!')
        
        // Configurar àudio per reproducció
        if (audioRef.current) {
          audioRef.current.src = audioData.audioUrl
          audioRef.current.load()
          
          // Esperar que l'àudio es carregui
          audioRef.current.oncanplaythrough = () => {
            console.log('✅ Àudio carregat i llest per reproduir')
            toast.success('Àudio llest per reproduir!')
          }
          
          audioRef.current.onerror = (error) => {
            console.error('❌ Error carregant àudio:', error)
            toast.error('Error carregant àudio')
          }
        }
      } else {
        console.error('❌ Resposta invàlida:', response.data)
        toast.error('Error generant àudio: ' + (response.data.error || 'Resposta invàlida'))
      }
    } catch (error) {
      console.error('Error:', error)
      toast.error('Error al generar audio Edge-TTS')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePlayPause = async () => {
    if (audioRef.current && currentAudio) {
      try {
        if (isPlaying) {
          audioRef.current.pause()
          setIsPlaying(false)
        } else {
          // Assegurar que l'àudio estigui carregat
          if (audioRef.current.readyState < 2) {
            audioRef.current.load()
            await new Promise((resolve) => {
              audioRef.current.oncanplaythrough = resolve
            })
          }
          
          await audioRef.current.play()
          setIsPlaying(true)
          toast.success('Reproduint àudio!')
        }
      } catch (error) {
        console.error('Error reproduint àudio:', error)
        toast.error('Error reproduint àudio: ' + error.message)
        setIsPlaying(false)
      }
    } else {
      toast.error('No hi ha àudio disponible per reproduir')
    }
  }

  const handleStop = () => {
    if (audioRef.current) {
      audioRef.current.pause()
      audioRef.current.currentTime = 0
      setIsPlaying(false)
    }
  }

  // Filtrar veus
  const filteredVoices = availableVoices.filter(voice => {
    const matchesSearch = voice.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (voice.description && voice.description.toLowerCase().includes(searchTerm.toLowerCase()))
    const matchesLanguage = filterLanguage === 'all' || voice.language === filterLanguage
    return matchesSearch && matchesLanguage
  })

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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Panel */}
        <div className="lg:col-span-2 space-y-6">
          {/* Text Input */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Text a Sintetitzar</h2>
            
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Escriu el text que vols sintetitzar..."
              className="w-full h-32 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent resize-none"
            />
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
                    className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  />
                </div>
              </div>
              <div className="sm:w-48">
                <select
                  value={filterLanguage}
                  onChange={(e) => setFilterLanguage(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
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
            
            {/* Llista de veus */}
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filteredVoices.map((voice) => (
                <div
                  key={voice.id}
                  className={`p-3 border-2 rounded-lg cursor-pointer transition-all ${
                    selectedVoice === voice.id
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => setSelectedVoice(voice.id)}
                >
                  <div className="flex items-center space-x-3">
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

          {/* Controls */}
          <div className="card">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Controls</h2>

            <div className="flex items-center space-x-4">
              <button
                onClick={handleGenerateSpeech}
                disabled={isGenerating || !text.trim() || isLoadingVoices}
                className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
              >
                {isGenerating ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Radio className="w-5 h-5" />
                )}
                <span>{isGenerating ? 'Generant...' : 'Generar Audio'}</span>
              </button>

              {currentAudio && (
                <>
                  <button
                    onClick={handlePlayPause}
                    className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center space-x-2"
                  >
                    {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  </button>

                  <button
                    onClick={handleStop}
                    className="px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 flex items-center space-x-2"
                  >
                    <Square className="w-5 h-5" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        {/* Audio Player */}
        <div className="space-y-6">
          {currentAudio && (
            <div className="card">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Audio Generat</h2>
              <div className="space-y-4">
                <div className="bg-gradient-to-r from-primary-50 to-secondary-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-700">{currentAudio.text}</p>
                </div>
                
                <audio
                  ref={audioRef}
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                  onEnded={() => setIsPlaying(false)}
                  className="w-full"
                  controls
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default EdgeTTSStandardSimple
