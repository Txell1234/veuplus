import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Settings, Eye } from 'lucide-react'
import api from '../config/api'

export default function ConvHiAgents() {
  const navigate = useNavigate()
  const [agent, setAgent] = useState({
    id: 'agent_demo',
    name: 'Agent Demo',
    description: 'Agent de prova',
    llm_provider: 'openai',
    llm_model: 'gpt-4o-mini',
    voice_system: 'edge-tts',
    voice_id: 'en-US-AriaNeural',
    external_voice_api: '',
    language: 'ca'
  })
  const [message, setMessage] = useState('Hola! Com et puc ajudar?')
  const [response, setResponse] = useState('')
  const [audioUrl, setAudioUrl] = useState('')
  const [list, setList] = useState([])

  const loadAgents = async () => {
    try {
      const r = await api.get('/api/convhi/agents')
      setList(r.data.agents || [])
    } catch (e) {}
  }

  useEffect(() => { loadAgents() }, [])

  const setField = (k,v) => setAgent(prev => ({ ...prev, [k]: v }))

  const create = async () => {
    try {
      await api.post('/api/convhi/agents', agent)
      await loadAgents()
      alert('Agent creat')
    } catch (e) {
      alert('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  const testChat = async () => {
    try {
      const r = await api.post(`/api/convhi/agents/${agent.id}/chat`, { message })
      const data = r.data || {}
      // Try common shapes: {response: {text, audio_base64, mime}} or flat
      const respObj = data.response || data
      const txt = respObj.text || data.text || JSON.stringify(data)
      setResponse(txt)
      const b64 = respObj.audio_base64 || data.audio_base64
      const mime = respObj.mime || data.mime || 'audio/wav'
      if (b64) {
        setAudioUrl(`data:${mime};base64,${b64}`)
      } else {
        setAudioUrl('')
      }
    } catch (e) {
      setResponse('Error: ' + (e.response?.data?.detail || e.message))
      setAudioUrl('')
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ConvHi — Agents complets</h1>
        <p className="text-gray-600">Crea agents, afegeix veus externes (ID + API) i prova converses.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-6 space-y-3">
          <h3 className="text-lg font-semibold">Crear / Actualitzar Agent</h3>
          <input className="input-field" placeholder="id" value={agent.id} onChange={e=>setField('id', e.target.value)} />
          <input className="input-field" placeholder="nom" value={agent.name} onChange={e=>setField('name', e.target.value)} />
          <input className="input-field" placeholder="descripció" value={agent.description} onChange={e=>setField('description', e.target.value)} />
          <div className="grid grid-cols-2 gap-3">
            <input className="input-field" placeholder="llm_provider (openai)" value={agent.llm_provider} onChange={e=>setField('llm_provider', e.target.value)} />
            <input className="input-field" placeholder="llm_model" value={agent.llm_model} onChange={e=>setField('llm_model', e.target.value)} />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <select className="input-field" value={agent.voice_system} onChange={e=>setField('voice_system', e.target.value)}>
              <option value="edge-tts">edge-tts</option>
              <option value="catalan">catalan</option>
              <option value="alia">alia</option>
              <option value="external">external</option>
            </select>
            <input className="input-field" placeholder="voice_id" value={agent.voice_id} onChange={e=>setField('voice_id', e.target.value)} />
            <input className="input-field" placeholder="external_voice_api (si external)" value={agent.external_voice_api} onChange={e=>setField('external_voice_api', e.target.value)} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <input className="input-field" placeholder="language (ca/es/en)" value={agent.language} onChange={e=>setField('language', e.target.value)} />
          </div>
          <button className="btn-primary" onClick={create}>Guardar agent</button>
        </div>

        <div className="card p-6 space-y-3">
          <h3 className="text-lg font-semibold">Provar conversa</h3>
          <textarea className="input-field" rows={3} value={message} onChange={e=>setMessage(e.target.value)} />
          <button className="btn-primary" onClick={testChat}>Enviar</button>
          {audioUrl && (
            <div className="mt-2">
              <audio controls src={audioUrl} />
            </div>
          )}
          <pre className="text-xs text-gray-700 bg-gray-50 p-3 rounded overflow-auto">{response}</pre>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-3">Agents Existents</h3>
        <div className="space-y-2">
          {list.map(a => (
            <div key={a.id} className="flex items-center justify-between p-3 border border-neutral-200 rounded-lg hover:border-primary-300 transition">
              <div>
                <p className="font-semibold text-neutral-900">{a.name || a.id}</p>
                <p className="text-sm text-neutral-600">{a.description || 'Sense descripció'}</p>
              </div>
              <button
                onClick={() => navigate(`/convhi-agents/config/${a.id}`)}
                className="btn-secondary inline-flex items-center gap-2"
              >
                <Settings className="w-4 h-4" />
                Configurar
              </button>
            </div>
          ))}
        </div>
        {list.length === 0 && (
          <p className="text-sm text-neutral-500 text-center py-4">No hi ha agents creats encara</p>
        )}
      </div>
    </div>
  )
}
