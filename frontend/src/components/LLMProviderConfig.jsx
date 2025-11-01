import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import api from '../config/api';

const LLMProviderConfig = () => {
  const [providers, setProviders] = useState({});
  const [apiKeys, setApiKeys] = useState({
    OPENAI_API_KEY: '',
    GEMINI_API_KEY: '',
    ANTHROPIC_API_KEY: '',
    AZURE_OPENAI_API_KEY: '',
    AZURE_OPENAI_ENDPOINT: '',
    AZURE_OPENAI_DEPLOYMENT_NAME: ''
  });
  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState({});

  useEffect(() => {
    fetchProviders();
  }, []);

  const fetchProviders = async () => {
    try {
      const response = await api.get('/api/llm/providers');
      setProviders(response.data.providers || {});
    } catch (error) {
      console.error('Error fetching providers:', error);
      toast.error('Error cargando proveedores LLM');
      // Set mock data for demo purposes
      setProviders({
        openai: { available: false, models: ['gpt-3.5-turbo', 'gpt-4'] },
        gemini: { available: false, models: ['gemini-pro'] },
        anthropic: { available: false, models: ['claude-3-sonnet'] },
        azure: { available: false, models: ['gpt-35-turbo'] },
        ollama: { available: true, models: ['llama2', 'codellama'] },
        local: { available: true, models: ['gpt-oss-20b'] }
      });
    }
  };

  const testProvider = async (providerId) => {
    setLoading(true);
    try {
      const response = await api.post('/api/llm/test', { provider: providerId });
      const result = response.data;
      
      setTestResults(prev => ({
        ...prev,
        [providerId]: result
      }));

      if (result.success) {
        toast.success(`✅ ${providerConfigs[providerId]?.name} funcionando correctamente`);
      } else {
        toast.error(`❌ Error en ${providerConfigs[providerId]?.name}: ${result.error}`);
      }
    } catch (error) {
      console.error('Error testing provider:', error);
      toast.error('Error probando proveedor');
      setTestResults(prev => ({
        ...prev,
        [providerId]: { success: false, error: error.message }
      }));
    } finally {
      setLoading(false);
    }
  };

  const providerConfigs = {
    openai: {
      name: 'OpenAI',
      icon: '🤖',
      description: 'GPT-4, GPT-3.5-turbo y otros modelos de OpenAI',
      keyFields: ['OPENAI_API_KEY'],
      instructions: 'Obtén tu API key en https://platform.openai.com/api-keys'
    },
    gemini: {
      name: 'Google Gemini',
      icon: '🔮',
      description: 'Gemini Pro, Gemini 1.5 Pro/Flash de Google',
      keyFields: ['GEMINI_API_KEY'],
      instructions: 'Obtén tu API key en https://makersuite.google.com/app/apikey'
    },
    anthropic: {
      name: 'Anthropic Claude',
      icon: '🧠',
      description: 'Claude 3.5 Sonnet, Claude 3 Haiku/Opus',
      keyFields: ['ANTHROPIC_API_KEY'],
      instructions: 'Obtén tu API key en https://console.anthropic.com/'
    },
    azure: {
      name: 'Azure OpenAI',
      icon: '☁️',
      description: 'Modelos OpenAI en Azure Cloud',
      keyFields: ['AZURE_OPENAI_API_KEY', 'AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_DEPLOYMENT_NAME'],
      instructions: 'Configura tu instancia de Azure OpenAI'
    },
    ollama: {
      name: 'Ollama (Local)',
      icon: '🏠',
      description: 'Modelos locales con Ollama',
      keyFields: [],
      instructions: 'Instala Ollama en tu sistema: https://ollama.ai'
    },
    local: {
      name: 'Local Transformers',
      icon: '💻',
      description: 'Modelos Hugging Face locales',
      keyFields: [],
      instructions: 'No requiere configuración adicional'
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Configuración de Proveedores LLM</h2>
        <p className="text-gray-600 mt-2">
          Configura las API keys para usar diferentes proveedores de modelos de lenguaje
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {Object.entries(providerConfigs).map(([providerId, config]) => {
          const provider = providers[providerId];
          const isAvailable = provider?.available || false;
          const testResult = testResults[providerId];

          return (
            <div key={providerId} className="bg-white rounded-lg shadow-md p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{config.icon}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{config.name}</h3>
                    <p className="text-sm text-gray-600">{config.description}</p>
                  </div>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                  isAvailable 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {isAvailable ? 'Disponible' : 'No configurado'}
                </div>
              </div>

              {/* Campos de configuración */}
              {config.keyFields.length > 0 && (
                <div className="space-y-3 mb-4">
                  {config.keyFields.map(field => (
                    <div key={field}>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        {field.replace(/_/g, ' ')}
                      </label>
                      <input
                        type={field.includes('KEY') ? 'password' : 'text'}
                        value={apiKeys[field]}
                        onChange={(e) => setApiKeys({
                          ...apiKeys,
                          [field]: e.target.value
                        })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder={`Introduce tu ${field.toLowerCase()}`}
                      />
                    </div>
                  ))}
                </div>
              )}

              {/* Instrucciones */}
              <div className="text-sm text-gray-600 mb-4">
                💡 {config.instructions}
              </div>

              {/* Modelos disponibles */}
              {provider && (
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Modelos disponibles:</h4>
                  <div className="flex flex-wrap gap-1">
                    {provider.models.map(model => (
                      <span
                        key={model}
                        className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full"
                      >
                        {model}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Botón de prueba */}
              <button
                onClick={() => testProvider(providerId)}
                disabled={loading || !isAvailable}
                className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                  isAvailable
                    ? 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50'
                    : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white inline-block mr-2"></div>
                    Probando...
                  </>
                ) : (
                  'Probar Conexión'
                )}
              </button>

              {/* Resultado de la prueba */}
              {testResult && (
                <div className={`mt-3 p-3 rounded-lg text-sm ${
                  testResult.success
                    ? 'bg-green-50 text-green-800'
                    : 'bg-red-50 text-red-800'
                }`}>
                  {testResult.success ? (
                    <>
                      ✅ Conexión exitosa
                      <div className="mt-1 text-xs">
                        Modelo: {testResult.model}
                      </div>
                    </>
                  ) : (
                    <>
                      ❌ Error: {testResult.error}
                    </>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Instrucciones de configuración */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">
          📋 Instrucciones de Configuración
        </h3>
        
        <div className="space-y-4 text-sm text-blue-800">
          <div>
            <strong>1. Variables de Entorno (Recomendado):</strong>
            <div className="mt-2 bg-blue-100 p-3 rounded font-mono text-xs">
              # Para OpenAI<br/>
              export OPENAI_API_KEY="sk-..."<br/><br/>
              
              # Para Gemini<br/>
              export GEMINI_API_KEY="AI..."<br/><br/>
              
              # Para Anthropic<br/>
              export ANTHROPIC_API_KEY="sk-ant-..."<br/><br/>
              
              # Para Azure OpenAI<br/>
              export AZURE_OPENAI_API_KEY="..."<br/>
              export AZURE_OPENAI_ENDPOINT="https://tu-recurso.openai.azure.com/"<br/>
              export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-35-turbo"
            </div>
          </div>
          
          <div>
            <strong>2. Reinicia el servidor</strong> después de configurar las variables de entorno.
          </div>
          
          <div>
            <strong>3. Los proveedores locales</strong> (Local Transformers, Ollama) no requieren API keys.
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMProviderConfig;
