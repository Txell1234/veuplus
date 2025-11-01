import React, { useEffect, useState } from 'react'
import api from '../config/api'

const Card = ({ title, children }) => (
  <div className="card p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
    {children}
  </div>
)

export default function SystemsHub() {
  const [edgeVoices, setEdgeVoices] = useState([])
  const [caVoices, setCaVoices] = useState([])
  const [aliaModels, setAliaModels] = useState([])
  const [text, setText] = useState('Hola! Això és una prova de síntesi.')
  const [voiceId, setVoiceId] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [filterEdge, setFilterEdge] = useState('')
  const [filterCa, setFilterCa] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    (async () => {
      try {
        setLoading(true)
        const [edge, ca, alia] = await Promise.all([
          api.get('/api/edge-tts/voices'),
          api.get('/api/catalan/voices/all').catch(() => api.get('/api/catalan/voices')),
          api.get('/api/alia/models').catch(() => ({ data: { models: [] } }))
        ])
        const ev = (edge.data.voices || edge.data.edge_voices || []).slice(0, 20)
        const cv = (ca.data.voices || ca.data.catalan_voices || [])
        const am = alia.data.models || []
        setEdgeVoices(ev)
        setCaVoices(cv)
        setAliaModels(am)
        if (!voiceId) setVoiceId(ev[0]?.id || cv[0]?.id || '')
      } catch (e) {
        // ignore, cards will still render
      } finally { setLoading(false) }
    })()
  }, [])

  const synth = async (system) => {
    try {
      setAudioUrl('')
      let res
      if (system === 'edge') {
        res = await api.post('/api/edge-tts/synthesize', { text, voice_id: voiceId, language: 'ca', voice_settings: { speed: 1.0 } })
      } else if (system === 'catalan') {
        res = await api.post('/api/catalan/synthesize', { text, voice_id: voiceId, language: 'ca', voice_settings: {} })
      } else {
        // ALIA TTS synth if exposed; fallback to LLM generate as a demo
        res = await api.post('/api/alia/llm/generate', { messages: [{ role: 'user', content: text }] })
      }
      const b64 = res.data.audio_base64
      if (b64) setAudioUrl(`data:${res.data.mime_type || 'audio/wav'};base64,${b64}`)
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Sistemes de Veu</h1>
        <p className="text-gray-600">Prova ràpida dels 3 sistemes: Edge‑TTS, Català Hiperrealista i ALIA.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card title="Edge‑TTS (Multiidioma)">
          <input className="input-field w-full mb-2" placeholder="Cerca" value={filterEdge} onChange={e=>setFilterEdge(e.target.value)} />
          <select className="input-field w-full mb-3" value={voiceId} onChange={e=>setVoiceId(e.target.value)}>
            {edgeVoices.filter(v=> (v.name||v.id).toLowerCase().includes(filterEdge.toLowerCase())).map(v => <option key={v.id} value={v.id}>{v.name || v.id}</option>)}
          </select>
          <textarea className="input-field w-full mb-3" rows={2} value={text} onChange={e=>setText(e.target.value)} />
          <button className="btn-primary" onClick={()=>synth('edge')}>Sintetitza</button>
        </Card>

        <Card title="Català Hiperrealista">
          <input className="input-field w-full mb-2" placeholder="Cerca" value={filterCa} onChange={e=>setFilterCa(e.target.value)} />
          <select className="input-field w-full mb-3" value={voiceId} onChange={e=>setVoiceId(e.target.value)}>
            {caVoices.filter(v=> (v.name||v.id).toLowerCase().includes(filterCa.toLowerCase())).map(v => <option key={v.id} value={v.id}>{v.name || v.id}</option>)}
          </select>
          <textarea className="input-field w-full mb-3" rows={2} value={text} onChange={e=>setText(e.target.value)} />
          <button className="btn-primary" onClick={()=>synth('catalan')}>Sintetitza</button>
        </Card>

        <Card title="ALIA Kit (LLM/TTS)">
          <div className="text-sm text-gray-600 mb-2">Models: {(aliaModels||[]).length}</div>
          <textarea className="input-field w-full mb-3" rows={2} value={text} onChange={e=>setText(e.target.value)} />
          <button className="btn-primary" onClick={()=>synth('alia')}>Genera</button>
        </Card>
      </div>

      {loading && (
        <div className="text-sm text-gray-600">Carregant dades...</div>
      )}

      {audioUrl && (
        <div className="card p-4">
          <h4 className="font-semibold text-gray-900 mb-2">Resultat</h4>
          <audio controls src={audioUrl} />
        </div>
      )}
    </div>
  )
}
