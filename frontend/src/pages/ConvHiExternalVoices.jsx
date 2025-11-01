import React, { useEffect, useState } from 'react'
import api from '../config/api'

export default function ConvHiExternalVoices() {
  const [voices, setVoices] = useState([])
  const [form, setForm] = useState({ id: '', provider: 'http_generic', api_base_url: '', method: 'POST' })
  const [loading, setLoading] = useState(false)

  const load = async () => {
    try {
      setLoading(true)
      const r = await api.get('/api/convhi/voices/external')
      setVoices(r.data.voices || [])
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])
  const setField = (k,v) => setForm(prev => ({ ...prev, [k]: v }))

  const create = async () => {
    if(!form.id){ alert('ID requerit'); return }
    try {
      await api.post('/api/convhi/voices/external', form)
      setForm({ id:'', provider:'http_generic', api_base_url:'', method:'POST' })
      await load()
    } catch(e) {
      alert('Error creant veu: '+(e.response?.data?.detail || e.message))
    }
  }

  const remove = async (vid) => {
    try {
      await api.delete(`/api/convhi/voices/external/${vid}`)
      await load()
    } catch(e) {
      alert('Error esborrant veu: '+(e.response?.data?.detail || e.message))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">ConvHi — Veus externes</h1>
        <p className="text-gray-600">Gestiona el registre de veus externes (ID + API) per usar-les als agents.</p>
      </div>

      <div className="card p-6 space-y-3">
        <h3 className="text-lg font-semibold">Afegir veu externa</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="input-field" placeholder="id" value={form.id} onChange={e=>setField('id', e.target.value)}/>
          <select className="input-field" value={form.provider} onChange={e=>setField('provider', e.target.value)}>
            <option value="http_generic">HTTP generic</option>
            <option value="aws_polly">AWS Polly (proxy)</option>
          </select>
          <input className="input-field" placeholder="api_base_url (opcional si tens proxy)" value={form.api_base_url} onChange={e=>setField('api_base_url', e.target.value)}/>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="input-field" placeholder="method" value={form.method} onChange={e=>setField('method', e.target.value)} />
          <button className="btn-primary" onClick={create}>Afegir</button>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="text-lg font-semibold mb-3">Veus registrades</h3>
        {loading && <div className="text-sm text-gray-600">Carregant...</div>}
        {!loading && voices.length===0 && <div className="text-sm text-gray-600">No hi ha veus externes</div>}
        {!loading && voices.length>0 && (
          <ul className="text-sm list-disc ml-5">
            {voices.map(v => (
              <li key={v.id}>
                {v.id} — {v.provider} {v.api_base_url ? `(${v.api_base_url})` : ''}
                <button className="btn-secondary ml-2" onClick={()=>remove(v.id)}>Esborrar</button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}