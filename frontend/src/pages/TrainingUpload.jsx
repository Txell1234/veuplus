import React, { useState } from 'react'
import api from '../config/api'

export default function TrainingUpload() {
  const [voiceId, setVoiceId] = useState('my_catalan_voice')
  const [files, setFiles] = useState([])
  const [jobId, setJobId] = useState('')
  const [log, setLog] = useState('')

  const onFiles = (e) => setFiles(Array.from(e.target.files || []))

  const upload = async () => {
    if (!voiceId || files.length === 0) return alert('Select voice id and files')
    const form = new FormData()
    for (const f of files) form.append('files', f)
    form.append('voice_id', voiceId)
    try {
      setLog('Uploading samples...')
      await fetch('/api/advanced-tts/voice-cloning/upload-samples', { method: 'POST', body: form })
      setLog('Samples uploaded. Starting training...')
      const resp = await api.post('/api/training/start', {
        name: voiceId,
        language: 'ca',
        dialect: 'central',
        use_catalan_dataset: false,
        custom_audio_files: []
      })
      setJobId(resp.data.job_id)
      setLog('Training started. Open Entrenament page to see progress.')
    } catch (e) {
      setLog('Error: ' + (e.response?.data?.detail || e.message))
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Entrenament — Pujar mostres</h1>
        <p className="text-gray-600">Puja arxius d’àudio (WAV/MP3/FLAC), després inicia l’entrenament.</p>
      </div>

      <div className="card p-6 space-y-4 max-w-2xl">
        <label className="block text-sm font-medium text-gray-700">Identificador de veu</label>
        <input className="input-field" value={voiceId} onChange={e=>setVoiceId(e.target.value)} placeholder="my_catalan_voice" />

        <label className="block text-sm font-medium text-gray-700">Arxius d’àudio</label>
        <input type="file" multiple accept=".wav,.mp3,.flac" onChange={onFiles} />
        <div className="text-xs text-gray-500">{files.length} fitxers seleccionats</div>

        <button className="btn-primary" onClick={upload}>Pujar i entrenar</button>
        {jobId && (
          <div className="text-sm text-gray-700">Job ID: <code>{jobId}</code></div>
        )}
        {log && <div className="text-sm text-gray-600 whitespace-pre-wrap">{log}</div>}
      </div>
    </div>
  )
}

