import axios from 'axios'

// Configuración de la URL base del API
const getApiBaseUrl = () => {
  // En desarrollo, usar proxy de Vite
  if (import.meta.env.DEV) {
    return ''  // Vite proxy manejará las rutas /api
  }
  
  // En producción, usar variable de entorno o default (8080 por backend)
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'
}

// Crear instancia de axios configurada
const api = axios.create({
  baseURL: getApiBaseUrl(),
  timeout: 30000,  // 30 segundos
  headers: {
    'Content-Type': 'application/json',
  }
})

// Interceptor para requests
api.interceptors.request.use(
  (config) => {
    // Agregar timestamp para evitar cache
    if (config.method === 'get') {
      config.params = {
        ...config.params,
        _t: Date.now()
      }
    }
    
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Interceptor para responses
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data)
    
    // Manejar errores comunes
    if (error.response?.status === 404) {
      console.warn('Endpoint no encontrado:', error.config.url)
    } else if (error.response?.status >= 500) {
      console.error('Error del servidor:', error.response.data)
    }
    
    return Promise.reject(error)
  }
)

export default api
