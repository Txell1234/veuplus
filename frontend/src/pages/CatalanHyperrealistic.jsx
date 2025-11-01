import React, { useState, useEffect, useRef } from 'react'
import {
  Play,
  Pause,
  Square,
  Loader2,
  Download,
  Zap,
  Search,
} from 'lucide-react'
import toast from 'react-hot-toast'
import api from '../config/api'

const DEFAULT_SAMPLE_TEXT =
  'Hola, aquesta és una prova de síntesi hiperrealista catalana amb VeuPlus.'

const getBadge = (source, mock) => {
  if (mock) return { label: 'Mock local', classes: 'bg-purple-100 text-purple-700' }
  if (source === 'edge_tts')
    return { label: 'Edge fallback', classes: 'bg-orange-100 text-orange-700' }
  return { label: 'Local', classes: 'bg-emerald-100 text-emerald-700' }
}

const CatalanHyperrealistic = () => {
  const [text, setText] = useState(DEFAULT_SAMPLE_TEXT)
  const [voices, setVoices] = useState([])
  const [selectedVoice, setSelectedVoice] = useState('')
  const [search, setSearch] = useState('')
  const [isLoadingVoices, setIsLoadingVoices] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentAudio, setCurrentAudio] = useState(null)
  const [history, setHistory] = useState([])

  const audioRef = useRef(null)

  useEffect(() => {
    const fetchVoices = async () => {
      try {
        setIsLoadingVoices(true)
        const response = await api.get('/api/catalan/voices')
        const rawVoices = response.data.voices || []
        if (!Array.isArray(rawVoices) || rawVoices.length === 0) {
          throw new Error('No voices retrieved')
        }
        const normalized = rawVoices.map((voice) => ({
          id: voice.id,
          name: voice.name || voice.id,
          description: voice.description || '',
          gender: voice.gender || 'unknown',
          source: voice.source || 'hyperlocal',
          mock: voice.mock ?? true,
          notes: voice.notes || '',
        }))
        setVoices(normalized)
        setSelectedVoice(normalized[0].id)
        toast.success(`${normalized.length} veus locals carregades`)
      } catch (error) {
        console.error('Error carregant veus catalanes:', error)
        toast.error('Error carregant veus catalanes, usant llista per defecte')
        const fallback = [
          {
            id: 'senyor_catala_1',
            name: 'Senyor Català 1',
            description: 'Gravació local (mock)',
            gender: 'male',
            source: 'fallback',
            mock: true,
          },
          {
            id: 'dona_catalana',
            name: 'Dona Catalana',
            description: 'Gravació local (mock)',
            gender: 'female',
            source: 'fallback',
            mock: true,
          },
        ]
        setVoices(fallback)
        setSelectedVoice(fallback[0].id)
      } finally {
        setIsLoadingVoices(false)
      }
    }

    fetchVoices()
  }, [])

  const handleGenerate = async () => {
    if (!selectedVoice) {
      toast.error('Selecciona una veu')
      return
    }
    if (!text.trim()) {
      toast.error('Introdueix text per sintetitzar')
      return
    }

    try {
      setIsGenerating(true)
      const response = await api.post('/api/catalan/synthesize', {
        text,
        voice_id: selectedVoice,
        language: 'ca',
        voice_settings: {},
      })

      if (!response.data?.audio_base64) {
        throw new Error(response.data?.error || 'Resposta invàlida')
      }

      const mimeType = response.data.mime_type || 'audio/mpeg'
      const audioPayload = {
        id: Date.now().toString(),
        voice: selectedVoice,
        text,
        audioUrl: `data:${mimeType};base64,${response.data.audio_base64}`,
        mimeType,
        timestamp: new Date().toISOString(),
        mock: response.data.mock ?? false,
        source: response.data.source || 'hyperlocal',
        notes: response.data.notes || '',
      }

      setCurrentAudio(audioPayload)
      setHistory((prev) => [audioPayload, ...prev].slice(0, 25))
      toast.success('Àudio català generat!')

      if (audioRef.current) {
        audioRef.current.src = audioPayload.audioUrl
        await audioRef.current.play()
        setIsPlaying(true)
      }
    } catch (error) {
      console.error('Error generant àudio hiperrealista:', error)
      toast.error('Error generant àudio hiperrealista')
    } finally {
      setIsGenerating(false)
    }
  }

  const handlePlayPause = async () => {
    if (!audioRef.current || !currentAudio) return
    try {
      if (isPlaying) {
        audioRef.current.pause()
        setIsPlaying(false)
      } else {
        await audioRef.current.play()
        setIsPlaying(true)
      }
    } catch (error) {
      console.error('Error reproduint àudio:', error)
      toast.error('No s’ha pogut reproduir l’àudio')
    }
  }

  const handleStop = () => {
    if (!audioRef.current) return
    audioRef.current.pause()
    audioRef.current.currentTime = 0
    setIsPlaying(false)
  }

  const handleDownload = (audioData) => {
    if (!audioData) return
    const ext = audioData.mimeType === 'audio/mpeg' ? 'mp3' : 'wav'
    const link = document.createElement('a')
    link.href = audioData.audioUrl
    link.download = `veuplus_catalan_${audioData.id}.${ext}`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    toast.success('Àudio descarregat')
  }

  const filteredVoices = voices.filter((voice) => {
    const query = search.trim().toLowerCase()
    if (!query) return true
    return (
      voice.name.toLowerCase().includes(query) ||
      (voice.description && voice.description.toLowerCase().includes(query))
    )
  })

  const currentBadge = currentAudio
    ? getBadge(currentAudio.source, currentAudio.mock)
    : null

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900 flex items-center gap-2">
            <Zap className="w-6 h-6 text-accent-500" />
            Veus Catalanes Hiperrealistes (mock)
          </h1>
          <p className="text-sm text-gray-600">
            Fins que disposem de GPU utilitzem les gravacions locals processades.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 space-y-4">
          <div className="card space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">Seleccionar veu</h2>
              {isLoadingVoices && <Loader2 className="w-4 h-4 animate-spin text-gray-400" />}
            </div>

            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Cercar veus..."
                className="w-full pl-10 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div className="space-y-2 max-h-72 overflow-y-auto">
              {filteredVoices.map((voice) => {
                const badge = getBadge(voice.source, voice.mock)
                const isActive = selectedVoice === voice.id
                return (
                  <button
                    key={voice.id}
                    onClick={() => setSelectedVoice(voice.id)}
                    className={`w-full text-left p-3 border-2 rounded-lg transition ${
                      isActive ? 'border-accent-500 bg-accent-50' : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <p className="font-medium text-gray-900">{voice.name}</p>
                        <p className="text-xs text-gray-500">{voice.description}</p>
                      </div>
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${badge.classes}`}>
                        {badge.label}
                      </span>
                    </div>
                  </button>
                )
              })}

              {filteredVoices.length === 0 && (
                <p className="text-sm text-gray-500">No s’han trobat veus</p>
              )}
            </div>
          </div>

          <div className="card space-y-3">
            <h2 className="text-lg font-semibold text-gray-900">Text a sintetitzar</h2>
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={4}
              className="input-field min-h-[120px]"
              placeholder="Escriu aquí el text en català..."
            />
            <button
              onClick={handleGenerate}
              disabled={isGenerating || !selectedVoice}
              className="btn-primary flex items-center gap-2 justify-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isGenerating ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
              <span>{isGenerating ? 'Generant...' : 'Generar àudio'}</span>
            </button>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          {currentAudio ? (
            <div className="card space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-semibold text-gray-900">Reproductor</h2>
                {currentBadge && (
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${currentBadge.classes}`}>
                    {currentBadge.label}
                  </span>
                )}
              </div>

              <div className="bg-gradient-to-r from-accent-50 to-primary-50 p-3 rounded-lg">
                <p className="text-sm text-gray-700 line-clamp-3">{currentAudio.text}</p>
              </div>

              <audio
                ref={audioRef}
                controls
                className="w-full"
                src={currentAudio.audioUrl}
                onPlay={() => setIsPlaying(true)}
                onPause={() => setIsPlaying(false)}
                onEnded={() => setIsPlaying(false)}
              />

              <div className="flex items-center gap-2">
                <button onClick={handlePlayPause} className="btn-secondary flex items-center gap-2">
                  {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
                  <span>{isPlaying ? 'Pausa' : 'Reprodueix'}</span>
                </button>
                <button onClick={handleStop} className="btn-secondary flex items-center gap-2">
                  <Square className="w-5 h-5" />
                  <span>Atura</span>
                </button>
                <button onClick={() => handleDownload(currentAudio)} className="btn-secondary flex items-center gap-2">
                  <Download className="w-5 h-5" />
                  <span>Descarrega</span>
                </button>
              </div>

              <div className="text-xs text-gray-500 flex items-center justify-between">
                <span>{new Date(currentAudio.timestamp).toLocaleString()}</span>
                <span>{currentAudio.mimeType}</span>
              </div>

              {currentAudio.notes && (
                <p className="text-xs text-gray-400">
                  {currentAudio.notes}
                </p>
              )}
            </div>
          ) : (
            <div className="card text-center text-gray-500">
              <Zap className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>Genera un àudio per veure el reproductor.</p>
            </div>
          )}

          <div className="card">
            <div className="flex items-center justify-between mb-3">
              <h2 className="text-lg font-semibold text-gray-900">Historial</h2>
              <span className="text-sm text-gray-500">{history.length} audios</span>
            </div>

            <div className="space-y-3 max-h-80 overflow-y-auto">
              {history.map((audio) => {
                const badge = getBadge(audio.source, audio.mock)
                return (
                  <div key={audio.id} className="p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-start justify-between">
                      <p className="text-sm text-gray-700 line-clamp-2 w-3/4">{audio.text}</p>
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${badge.classes}`}>
                        {badge.label}
                      </span>
                    </div>
                    <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                      <span>{new Date(audio.timestamp).toLocaleString()}</span>
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setCurrentAudio(audio)
                            if (audioRef.current) {
                              audioRef.current.src = audio.audioUrl
                              audioRef.current.play().catch(() => setIsPlaying(false))
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
                    {audio.notes && <p className="text-xs text-gray-400 mt-1">{audio.notes}</p>}
                  </div>
                )
              })}

              {history.length === 0 && (
                <div className="text-center text-gray-500 py-8">
                  <Zap className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p>No hi ha audios generats.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default CatalanHyperrealistic
