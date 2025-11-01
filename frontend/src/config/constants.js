// Configuración centralizada de URLs y constantes
export const API_CONFIG = {
  // URLs del backend
  BACKEND_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080',
  BACKEND_API_URL: `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080'}/api`,
  
  // URLs de servicios externos
  VLLM_URL: 'http://localhost:8000',
  OLLAMA_URL: 'http://localhost:11434',
  
  // WebSocket URLs
  WS_URL: `ws://${import.meta.env.VITE_WS_HOST || 'localhost'}:${import.meta.env.VITE_WS_PORT || '8080'}`,
  
  // Timeouts
  REQUEST_TIMEOUT: 30000,
  WS_TIMEOUT: 10000,
}

// Configuración de proveedores LLM
export const LLM_PROVIDERS = {
  OPENAI: {
    name: 'OpenAI',
    icon: '🤖',
    description: 'GPT-4, GPT-3.5-turbo y otros modelos de OpenAI',
    keyFields: ['OPENAI_API_KEY'],
    instructions: 'Obtén tu API key en https://platform.openai.com/api-keys'
  },
  GEMINI: {
    name: 'Google Gemini',
    icon: '🔮',
    description: 'Gemini Pro, Gemini 1.5 Pro/Flash de Google',
    keyFields: ['GEMINI_API_KEY'],
    instructions: 'Obtén tu API key en https://makersuite.google.com/app/apikey'
  },
  ANTHROPIC: {
    name: 'Anthropic Claude',
    icon: '🧠',
    description: 'Claude 3.5 Sonnet, Claude 3 Haiku/Opus',
    keyFields: ['ANTHROPIC_API_KEY'],
    instructions: 'Obtén tu API key en https://console.anthropic.com/'
  },
  AZURE: {
    name: 'Azure OpenAI',
    icon: '☁️',
    description: 'Modelos OpenAI en Azure Cloud',
    keyFields: ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_DEPLOYMENT_NAME'],
    instructions: 'Configura tu instancia de Azure OpenAI'
  },
  OLLAMA: {
    name: 'Ollama (Local)',
    icon: '🏠',
    description: 'Modelos locales con Ollama',
    keyFields: [],
    instructions: 'Instala Ollama en tu sistema: https://ollama.ai'
  },
  LOCAL: {
    name: 'Local Transformers',
    icon: '💻',
    description: 'Modelos Hugging Face locales',
    keyFields: [],
    instructions: 'No requiere configuración adicional'
  }
}

// Configuración de idiomas
export const LANGUAGES = {
  CA: { code: 'ca', name: 'Català', flag: '🇪🇸' },
  ES: { code: 'es', name: 'Español', flag: '🇪🇸' },
  EN: { code: 'en', name: 'English', flag: '🇺🇸' },
  FR: { code: 'fr', name: 'Français', flag: '🇫🇷' }
}

// Configuración de temas
export const THEMES = {
  LIGHT: { code: 'light', name: 'Claro', icon: '☀️' },
  DARK: { code: 'dark', name: 'Oscuro', icon: '🌙' },
  AUTO: { code: 'auto', name: 'Automático', icon: '🔄' }
}

// Configuración de logs
export const LOG_LEVELS = {
  DEBUG: { code: 'debug', name: 'Debug', color: 'text-gray-600' },
  INFO: { code: 'info', name: 'Info', color: 'text-blue-600' },
  WARNING: { code: 'warning', name: 'Warning', color: 'text-yellow-600' },
  ERROR: { code: 'error', name: 'Error', color: 'text-red-600' }
}

// Configuración de audio
export const AUDIO_CONFIG = {
  DEFAULT_SPEED: 1.0,
  DEFAULT_PITCH: 1.0,
  DEFAULT_VOLUME: 1.0,
  MIN_SPEED: 0.5,
  MAX_SPEED: 2.0,
  MIN_PITCH: 0.5,
  MAX_PITCH: 2.0,
  MIN_VOLUME: 0.1,
  MAX_VOLUME: 1.0
}

// Configuración de chatbot
export const CHATBOT_CONFIG = {
  DEFAULT_MODEL: 'gpt-3.5-turbo',
  DEFAULT_TEMPERATURE: 0.7,
  DEFAULT_MAX_TOKENS: 1000,
  MIN_TEMPERATURE: 0,
  MAX_TEMPERATURE: 2,
  MIN_TOKENS: 100,
  MAX_TOKENS: 4000
}

// Configuración del sistema
export const SYSTEM_CONFIG = {
  DEFAULT_MAX_AUDIO_HISTORY: 50,
  MIN_AUDIO_HISTORY: 10,
  MAX_AUDIO_HISTORY: 200,
  DEFAULT_AUTO_CLEANUP: true,
  DEFAULT_LOG_LEVEL: 'info'
}
