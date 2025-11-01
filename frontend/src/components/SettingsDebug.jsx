import React, { useState, useEffect } from 'react'
import api from '../config/api'

const SettingsDebug = () => {
  const [debugInfo, setDebugInfo] = useState({
    apiStatus: 'checking',
    providers: {},
    error: null
  })

  useEffect(() => {
    const checkAPI = async () => {
      try {
        // Test health endpoint
        const healthResponse = await api.get('/api/health')
        console.log('Health response:', healthResponse.data)
        
        // Test providers endpoint
        const providersResponse = await api.get('/api/llm/providers')
        console.log('Providers response:', providersResponse.data)
        
        setDebugInfo({
          apiStatus: 'connected',
          providers: providersResponse.data.providers || {},
          error: null
        })
      } catch (error) {
        console.error('API Error:', error)
        setDebugInfo({
          apiStatus: 'error',
          providers: {},
          error: error.message
        })
      }
    }

    checkAPI()
  }, [])

  return (
    <div className="card">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Debug Settings</h2>
      
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
          <strong>Providers Count:</strong> 
          <span className="ml-2">{Object.keys(debugInfo.providers).length}</span>
        </div>
        
        {Object.keys(debugInfo.providers).length > 0 && (
          <div>
            <strong>Available Providers:</strong>
            <div className="mt-2 space-y-1">
              {Object.entries(debugInfo.providers).map(([key, provider]) => (
                <div key={key} className="flex items-center space-x-2">
                  <span className={`w-2 h-2 rounded-full ${
                    provider.available ? 'bg-green-500' : 'bg-gray-400'
                  }`}></span>
                  <span className="text-sm">{key}: {provider.available ? 'Available' : 'Not Available'}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default SettingsDebug
