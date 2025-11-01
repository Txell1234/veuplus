import React, { useState, useEffect } from 'react'
import api from '../config/api'

const DebugInfo = () => {
  const [debugInfo, setDebugInfo] = useState({
    apiStatus: 'checking',
    voices: [],
    error: null
  })

  useEffect(() => {
    const checkAPI = async () => {
      try {
        // Test health endpoint
        const healthResponse = await api.get('/api/health')
        console.log('Health response:', healthResponse.data)
        
        // Test voices endpoint
        const voicesResponse = await api.get('/api/tts/voices')
        console.log('Voices response:', voicesResponse.data)
        
        setDebugInfo({
          apiStatus: 'connected',
          voices: voicesResponse.data.voices || [],
          error: null
        })
      } catch (error) {
        console.error('API Error:', error)
        setDebugInfo({
          apiStatus: 'error',
          voices: [],
          error: error.message
        })
      }
    }

    checkAPI()
  }, [])

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Debug Info</h2>
      
      <div className="space-y-4">
        <div>
          <strong>API Status:</strong> 
          <span className={`ml-2 px-2 py-1 rounded text-sm ${
            debugInfo.apiStatus === 'connected' ? 'bg-green-100 text-green-800' :
            debugInfo.apiStatus === 'error' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {debugInfo.apiStatus}
          </span>
        </div>
        
        {debugInfo.error && (
          <div>
            <strong>Error:</strong> 
            <span className="ml-2 text-red-600">{debugInfo.error}</span>
          </div>
        )}
        
        <div>
          <strong>Voices Count:</strong> 
          <span className="ml-2">{debugInfo.voices.length}</span>
        </div>
        
        {debugInfo.voices.length > 0 && (
          <div>
            <strong>First Voice:</strong>
            <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-auto">
              {JSON.stringify(debugInfo.voices[0], null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  )
}

export default DebugInfo
