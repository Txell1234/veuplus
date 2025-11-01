import React, { useState, useEffect, useRef } from 'react';
import api from './config/api';

const VoiceTrainingAdvanced = () => {
  const [activeStep, setActiveStep] = useState(1);
  const [trainingSessions, setTrainingSessions] = useState([]);
  const [currentJob, setCurrentJob] = useState(null);
  const [trainingProgress, setTrainingProgress] = useState({});
  const [systemStatus, setSystemStatus] = useState({});
  const [supportedLanguages, setSupportedLanguages] = useState({});
  const [publishedIds, setPublishedIds] = useState([]);
  const [promptText, setPromptText] = useState('Catalan male, warm and expressive, Barceloní accent');
  const [generatingSpec, setGeneratingSpec] = useState(false);
  const [trainedVoices, setTrainedVoices] = useState([]);
  const [catalanVoices, setCatalanVoices] = useState([]);
  const [selectedVoiceId, setSelectedVoiceId] = useState('');
  const [testText, setTestText] = useState('Hola, aquesta és una prova de veu hiperrealista.');
  const [testAudioUrl, setTestAudioUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef(null);

  // Usar configuración centralizada de API
  const ax = api;

  // Training form state
  const [trainingForm, setTrainingForm] = useState({
    name: '',
    language: 'ca',
    dialect: 'central',
    use_catalan_dataset: true,
    custom_audio_files: [],
    training_config: {
      num_epochs: 50,
      batch_size: 4,
      learning_rate: 0.0001
    }
  });

  useEffect(() => {
    loadInitialData();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  useEffect(() => {
    // Debug log to check if supportedLanguages is loading
    console.log('Supported Languages:', supportedLanguages);
  }, [supportedLanguages]);

  const loadInitialData = async () => {
    try {
      setIsLoading(true);
      
      // Load all dashboard data in parallel
      const [sessionsRes, statusRes, languagesRes, trainedRes, caVoicesRes] = await Promise.all([
        ax.get(`/api/training/jobs`),
        ax.get(`/api/training/system/status`),
        ax.get(`/api/training/languages`),
        ax.get(`/api/trained/voices`).catch(() => ({ data: { trained_voices: [] }})),
        ax.get(`/api/catalan/voices/all`).catch(() => ({ data: { voices: [] }})),
      ]);
      
      setTrainingSessions(sessionsRes.data.jobs || []);
      setSystemStatus(statusRes.data || {});
      setSupportedLanguages(languagesRes.data.supported_languages || {});
      setTrainedVoices(trainedRes.data.trained_voices || []);
      setCatalanVoices(caVoicesRes.data.voices || []);
      try {
        const pub = await ax.get(`/api/voices/publish`);
        setPublishedIds(pub.data.published || []);
      } catch (e) {
        console.warn("Publish list not available");
      }
      if (!selectedVoiceId) {
        const first = (trainedRes.data.trained_voices || [])[0]?.id || (caVoicesRes.data.voices || [])[0]?.id || '';
        setSelectedVoiceId(first);
      }
      
      console.log('Loaded data:', {
        sessions: sessionsRes.data.jobs?.length || 0,
        status: statusRes.data,
        languages: Object.keys(languagesRes.data.supported_languages || {}),
        trained: (trainedRes.data.trained_voices || []).length,
        catalanVoices: (caVoicesRes.data.voices || []).length,
      });
      
    } catch (error) {
      console.error('Error loading training data:', error);
      // Try alternative endpoint structure
      try {
      const languagesRes = await ax.get(`/api/training/languages`);
        setSupportedLanguages(languagesRes.data.supported_languages || {});
      } catch (altError) {
        console.error('Alternative load failed:', altError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  
  const publishSelected = async () => {
    if (!selectedVoiceId) return;
    try {
      const res = await ax.post(/api/voices/publish/);
      setPublishedIds(res.data.published || []);
    } catch (e) {
      console.error('Publish error:', e);
      alert('No s\u2019ha pogut publicar la veu');
    }
  };

  const unpublishSelected = async () => {
    if (!selectedVoiceId) return;
    try {
      const res = await ax.delete(/api/voices/publish/);
      setPublishedIds(res.data.published || []);
    } catch (e) {
      console.error('Unpublish error:', e);
      alert('No s\u2019ha pogut despublicar la veu');
    }
  };

  const generateSpecFromPrompt = async () => {
    setGeneratingSpec(true);
    try {
      const res = await ax.post('/api/training/prompt-spec', {
        prompt: promptText,
        language: trainingForm.language,
      });
      const spec = res.data || {};
      setTrainingForm(prev => ({
        ...prev,
        name: spec.name || prev.name,
        language: spec.language || prev.language,
        dialect: spec.dialect || prev.dialect,
        use_catalan_dataset: !!spec.use_catalan_dataset,
        training_config: { ...(prev.training_config||{}), ...(spec.training_config||{}) },
      }));
      setActiveStep(3);
    } catch (e) {
      console.error('Prompt-spec error:', e);
      alert('No s\u2019ha pogut generar l\u2019especificació');
    } finally {
      setGeneratingSpec(false);
    }
  };const synthesizeHyperrealistic = async () => {
    if (!selectedVoiceId) {
      alert('Selecciona una veu');
      return;
    }
    setIsLoading(true);
    setTestAudioUrl('');
    try {
      // If selected voice exists in trained voices, use trained endpoint
      const isTrained = trainedVoices.some(v => v.id === selectedVoiceId);
      const endpoint = isTrained ? '/api/trained/synthesize' : '/api/catalan/synthesize';
      const body = {
        text: testText,
        voice_id: selectedVoiceId,
        language: 'ca',
        voice_settings: { stability: 0.75, similarity_boost: 0.8 }
      };
      const res = await ax.post(endpoint, body);
      const b64 = res.data.audio_base64;
      if (!b64) throw new Error('No audio returned');
      const url = `data:${res.data.mime_type || 'audio/wav'};base64,${b64}`;
      setTestAudioUrl(url);
    } catch (e) {
      console.error('Hyperrealistic synth error:', e);
      alert('Error en síntesi: ' + (e.response?.data?.detail || e.message));
    } finally {
      setIsLoading(false);
    }
  };

  const connectWebSocket = (jobId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Construir URL WebSocket segura según la base de API
    const baseURL = ax?.defaults?.baseURL || '';
    let httpOrigin = baseURL;
    if (!httpOrigin) {
      // En dev con proxy Vite, usar el origen actual
      httpOrigin = window.location.origin;
    }
    const wsScheme = httpOrigin.startsWith('https') ? 'wss' : 'ws';
    const wsBase = httpOrigin.replace(/^https?/i, wsScheme);
    const wsUrl = `${wsBase}/api/training/ws/${jobId}`;
    console.log('Connecting to WebSocket:', wsUrl);
    
    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setTrainingProgress(prev => ({
        ...prev,
        [jobId]: data
      }));
      console.log('WebSocket progress:', data);
    };

    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    wsRef.current.onclose = () => {
      console.log('WebSocket connection closed');
    };

    wsRef.current.onopen = () => {
      console.log('WebSocket connection opened');
    };
  };

  const startTraining = async () => {
    if (!trainingForm.name) {
      alert('Please enter a voice model name');
      return;
    }

    setIsLoading(true);
    try {
      console.log('Starting training with data:', trainingForm);
      const response = await ax.post(`/api/training/start`, trainingForm);
      const jobId = response.data.job_id;
      
      console.log('Training started with job ID:', jobId);
      setCurrentJob(jobId);
      connectWebSocket(jobId);
      
      // Refresh training sessions
      loadInitialData();
      
      // Move to progress step
      setActiveStep(4);
      
    } catch (error) {
      console.error('Error starting training:', error);
      alert('Failed to start training: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  const cancelTraining = async (jobId) => {
    try {
      await ax.delete(`/api/training/jobs/${jobId}`);
      loadInitialData();
      
      if (currentJob === jobId) {
        setCurrentJob(null);
        if (wsRef.current) {
          wsRef.current.close();
        }
      }
    } catch (error) {
      console.error('Error cancelling training:', error);
      alert('Failed to cancel training');
    }
  };

  const getDialectInfo = (dialect, language) => {
    const dialectMap = {
      ca: {
        central: {
          name: "Central",
          description: "Dialecto estándar de Barcelona y área metropolitana",
          features: ["Pronunciación neutra", "Entonación equilibrada", "Vocabulario estándar"]
        },
        balearic: {
          name: "Balear",
          description: "Dialecto de las Islas Baleares (Mallorca, Menorca, Ibiza)",
          features: ["Pronunciación característica", "Influencia insular", "Vocabulario local"]
        },
        valencian: {
          name: "Valenciano",
          description: "Dialecto de la Comunidad Valenciana",
          features: ["Pronunciación valenciana", "Entonación distintiva", "Tradición literaria"]
        },
        andorran: {
          name: "Andorrano",
          description: "Dialecto de Andorra con influencias francesas",
          features: ["Influencia francesa", "Pronunciación única", "Vocabulario mixto"]
        },
        rossellones: {
          name: "Rosellonés",
          description: "Dialecto del Rosellón (Cataluña Norte)",
          features: ["Influencia francesa", "Pronunciación histórica", "Tradición cultural"]
        },
        alguerese: {
          name: "Alguerés",
          description: "Dialecto de Alguer (Cerdeña)",
          features: ["Influencia italiana", "Pronunciación única", "Comunidad histórica"]
        }
      },
      es: {
        castilian: {
          name: "Castellano",
          description: "Español estándar de España",
          features: ["Pronunciación neutra", "Entonación estándar"]
        },
        andalusian: {
          name: "Andaluz",
          description: "Dialecto del sur de España",
          features: ["Pronunciación característica", "Entonación musical"]
        },
        mexican: {
          name: "Mexicano",
          description: "Español de México",
          features: ["Pronunciación mexicana", "Vocabulario local"]
        },
        argentinian: {
          name: "Argentino",
          description: "Español de Argentina",
          features: ["Pronunciación rioplatense", "Entonación distintiva"]
        }
      },
      fr: {
        metropolitan: {
          name: "Metropolitano",
          description: "Francés estándar de Francia",
          features: ["Pronunciación estándar", "Entonación neutra"]
        },
        canadian: {
          name: "Canadiense",
          description: "Francés de Quebec",
          features: ["Pronunciación quebequense", "Vocabulario local"]
        },
        belgian: {
          name: "Belga",
          description: "Francés de Bélgica",
          features: ["Pronunciación belga", "Influencias locales"]
        }
      },
      en: {
        american: {
          name: "Americano",
          description: "Inglés americano estándar",
          features: ["Pronunciación americana", "Entonación característica"]
        },
        british: {
          name: "Británico",
          description: "Inglés británico estándar",
          features: ["Pronunciación británica", "Entonación distintiva"]
        },
        australian: {
          name: "Australiano",
          description: "Inglés australiano",
          features: ["Pronunciación australiana", "Vocabulario local"]
        },
        canadian: {
          name: "Canadiense",
          description: "Inglés canadiense",
          features: ["Pronunciación canadiense", "Influencias mixtas"]
        }
      },
      pt: {
        brazilian: {
          name: "Brasileño",
          description: "Portugués de Brasil",
          features: ["Pronunciación brasileña", "Entonación musical"]
        },
        european: {
          name: "Europeo",
          description: "Portugués de Portugal",
          features: ["Pronunciación portuguesa", "Entonación característica"]
        }
      }
    };

    return dialectMap[language]?.[dialect] || {
      name: dialect.charAt(0).toUpperCase() + dialect.slice(1),
      description: `Dialecto ${dialect}`,
      features: ["Pronunciación estándar"]
    };
  };

  const renderLanguageSelection = () => {
    // Enhanced language data with hyperrealistic quality indicators
    const fallbackLanguages = {
      "ca": {
        "name": "Catalan Dataset (OpenSLR)",
        "dialects": ["central", "balearic", "valencian", "andorran", "rossellones", "alguerese"],
        "sample_rate": 22050,
        "lang_code": "ca",
        "hyperrealistic": true,
        "quality_score": 95,
        "dataset_size": "50K+ samples",
        "features": ["Native pronunciation", "Emotional range", "Natural intonation", "Dialect accuracy"]
      },
      "es": {
        "name": "Spanish Dataset",
        "dialects": ["castilian", "andalusian", "mexican", "argentinian"],
        "sample_rate": 16000,
        "lang_code": "es",
        "hyperrealistic": false,
        "quality_score": 85,
        "dataset_size": "30K+ samples",
        "features": ["Standard pronunciation", "Clear articulation"]
      },
      "fr": {
        "name": "French Dataset", 
        "dialects": ["metropolitan", "canadian", "belgian"],
        "sample_rate": 16000,
        "lang_code": "fr",
        "hyperrealistic": false,
        "quality_score": 80,
        "dataset_size": "25K+ samples",
        "features": ["Standard pronunciation", "Clear articulation"]
      },
      "en": {
        "name": "English Dataset",
        "dialects": ["american", "british", "australian", "canadian"],
        "sample_rate": 16000,
        "lang_code": "en",
        "hyperrealistic": false,
        "quality_score": 82,
        "dataset_size": "40K+ samples",
        "features": ["Standard pronunciation", "Clear articulation"]
      },
      "pt": {
        "name": "Portuguese Dataset",
        "dialects": ["brazilian", "european"],
        "sample_rate": 16000,
        "lang_code": "pt",
        "hyperrealistic": false,
        "quality_score": 78,
        "dataset_size": "20K+ samples",
        "features": ["Standard pronunciation", "Clear articulation"]
      }
    };

    const languages = Object.keys(supportedLanguages).length > 0 ? supportedLanguages : fallbackLanguages;
    
    return (
      <div className="space-y-6">
        <h3 className="text-xl font-semibold">Select Language & Dialect</h3>
        
        {Object.keys(languages).length === 0 ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading supported languages...</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {Object.entries(languages).map(([langCode, langData]) => (
              <div
                key={langCode}
                onClick={() => setTrainingForm(prev => ({ ...prev, language: langCode }))}
                className={`card p-4 cursor-pointer transition-all relative ${
                  trainingForm.language === langCode ? 'ring-2 ring-purple-500 bg-purple-50' : 'hover:scale-[1.02] hover:shadow-lg'
                } ${langData.hyperrealistic ? 'border-2 border-gradient-to-r from-purple-400 to-pink-400' : ''}`}
              >
                {/* Hyperrealistic Badge */}
                {langData.hyperrealistic && (
                  <div className="absolute -top-2 -right-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs px-3 py-1 rounded-full font-bold shadow-lg">
                    ? HIPERREALISTA
                  </div>
                )}
                
                <div className="text-lg font-semibold mb-2 flex items-center">
                  {langData.name}
                  {langData.hyperrealistic && (
                    <span className="ml-2 text-purple-500">??</span>
                  )}
                </div>
                
                {/* Quality Score */}
                <div className="flex items-center mb-2">
                  <span className="text-sm text-gray-600 mr-2">Calidad:</span>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${
                        langData.hyperrealistic ? 'bg-gradient-to-r from-purple-500 to-pink-500' : 'bg-blue-500'
                      }`}
                      style={{ width: `${langData.quality_score}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium ml-2">{langData.quality_score}%</span>
                </div>
                
                <div className="text-sm text-gray-600 mb-2">
                  {langData.dialects?.length || 0} dialectos • {langData.dataset_size}
                </div>
                
                {/* Features */}
                <div className="space-y-1">
                  {langData.features?.slice(0, 2).map((feature, idx) => (
                    <div key={idx} className="text-xs text-gray-500 flex items-center">
                      <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                      {feature}
                    </div>
                  ))}
                  {langData.features?.length > 2 && (
                    <div className="text-xs text-gray-400">
                      +{langData.features.length - 2} más características
                    </div>
                  )}
                </div>
                
                {/* Special Catalan Features */}
                {langCode === 'ca' && (
                  <div className="mt-3 p-2 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                    <div className="text-xs font-medium text-purple-800 mb-1">
                      ???? Dataset Especializado
                    </div>
                    <div className="text-xs text-purple-700">
                      Pronunciación nativa con patrones emocionales naturales
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {trainingForm.language && languages[trainingForm.language]?.dialects && (
          <div className="mt-6">
            <h4 className="text-lg font-medium mb-3">
              Selecciona Dialecto {trainingForm.language === 'ca' && 'Catalán'}
            </h4>
            
            {/* Special info for Catalan */}
            {trainingForm.language === 'ca' && (
              <div className="mb-4 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
                <div className="flex items-start">
                  <div className="text-purple-500 text-xl mr-3">??</div>
                  <div>
                    <h5 className="font-semibold text-purple-900 mb-1">Precisión Dialectal Hiperrealista</h5>
                    <p className="text-purple-700 text-sm">
                      Cada dialecto catalán tiene patrones únicos de pronunciación, entonación y vocabulario. 
                      Nuestro sistema especializado captura estas sutilezas para crear voces auténticamente nativas.
                    </p>
                  </div>
                </div>
              </div>
            )}
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {languages[trainingForm.language].dialects.map((dialect) => {
                const dialectInfo = getDialectInfo(dialect, trainingForm.language);
                return (
                  <button
                    key={dialect}
                    onClick={() => setTrainingForm(prev => ({ ...prev, dialect }))}
                    className={`p-4 text-sm rounded-lg border transition-all text-left ${
                      trainingForm.dialect === dialect 
                        ? 'ring-2 ring-purple-500 bg-purple-50 border-purple-300' 
                        : 'hover:scale-[1.02] hover:shadow-md border-gray-200'
                    } ${trainingForm.language === 'ca' ? 'bg-white' : 'bg-gray-50'}`}
                  >
                    <div className="font-medium mb-1">
                      {dialectInfo.name}
                    </div>
                    <div className="text-xs text-gray-600 mb-2">
                      {dialectInfo.description}
                    </div>
                    {dialectInfo.features && (
                      <div className="space-y-1">
                        {dialectInfo.features.slice(0, 2).map((feature, idx) => (
                          <div key={idx} className="text-xs text-gray-500 flex items-center">
                            <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                            {feature}
                          </div>
                        ))}
                      </div>
                    )}
                    {trainingForm.language === 'ca' && (
                      <div className="mt-2 text-xs px-2 py-1 rounded-full bg-purple-100 text-purple-700 inline-block">
                        ?? Hiperrealista
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="flex justify-between mt-8">
          <button
            onClick={() => setActiveStep(1)}
            className="btn-secondary"
          >
            ? Atrás
          </button>
          <button
            onClick={() => setActiveStep(3)}
            disabled={!trainingForm.language}
            className="btn-primary disabled:opacity-50"
          >
            Siguiente: Configuración ?
          </button>
        </div>
      </div>
    );
  };

  const renderTrainingConfiguration = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-900">Configuración de Entrenamiento</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nombre del Modelo de Voz
          </label>
          <input
            type="text"
            value={trainingForm.name}
            onChange={(e) => setTrainingForm(prev => ({ ...prev, name: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="Mi Modelo de Voz Personalizado"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Épocas de Entrenamiento
          </label>
          <select
            value={trainingForm.training_config.num_epochs}
            onChange={(e) => setTrainingForm(prev => ({
              ...prev,
              training_config: { ...prev.training_config, num_epochs: parseInt(e.target.value) }
            }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="25">25 épocas (Rápido - 15 min)</option>
            <option value="50">50 épocas (Estándar - 30 min)</option>
            <option value="100">100 épocas (Alta Calidad - 60 min)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tamaño de Lote
          </label>
          <select
            value={trainingForm.training_config.batch_size}
            onChange={(e) => setTrainingForm(prev => ({
              ...prev,
              training_config: { ...prev.training_config, batch_size: parseInt(e.target.value) }
            }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="2">2 (Memoria GPU Baja)</option>
            <option value="4">4 (Recomendado)</option>
            <option value="8">8 (Memoria GPU Alta)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Tasa de Aprendizaje
          </label>
          <select
            value={trainingForm.training_config.learning_rate}
            onChange={(e) => setTrainingForm(prev => ({
              ...prev,
              training_config: { ...prev.training_config, learning_rate: parseFloat(e.target.value) }
            }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="0.00005">0.00005 (Conservador)</option>
            <option value="0.0001">0.0001 (Recomendado)</option>
            <option value="0.0002">0.0002 (Agresivo)</option>
          </select>
        </div>
      </div>

      {trainingForm.language === 'ca' && (
        <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-lg p-6">
          <div className="flex items-start">
            <div className="text-purple-500 text-2xl mr-4">??</div>
            <div className="flex-1">
              <div className="flex items-center mb-2">
                <h4 className="font-bold text-purple-900 text-lg">Dataset Catalán Hiperrealista</h4>
                <span className="ml-3 px-3 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs rounded-full font-bold">
                  ? CALIDAD PREMIUM
                </span>
              </div>
              <p className="text-purple-800 text-sm mb-4">
                Utilizando <strong>projecte-aina/openslr-slr69-ca-trimmed-denoised</strong> para voces catalanas hiperrealistas.
                Este dataset especializado proporciona patrones de pronunciación nativos auténticos para el dialecto <strong>{trainingForm.dialect}</strong>.
              </p>
              
              {/* Quality Features */}
              <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="flex items-center text-sm text-purple-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  Pronunciación nativa auténtica
                </div>
                <div className="flex items-center text-sm text-purple-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  Patrones emocionales naturales
                </div>
                <div className="flex items-center text-sm text-purple-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  Entonación dialectal precisa
                </div>
                <div className="flex items-center text-sm text-purple-700">
                  <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                  Vocabulario regional específico
                </div>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="use_catalan_dataset"
                    checked={trainingForm.use_catalan_dataset}
                    onChange={(e) => setTrainingForm(prev => ({ ...prev, use_catalan_dataset: e.target.checked }))}
                    className="mr-3 w-5 h-5 text-purple-600 rounded focus:ring-purple-500"
                  />
                  <label htmlFor="use_catalan_dataset" className="text-sm font-medium text-purple-800">
                    Activar dataset catalán para calidad hiperrealista
                  </label>
                </div>
                <div className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded">
                  +95% calidad
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Requirements Check */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-3">Estado del Sistema</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              systemStatus.gpu_available ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span>GPU: {systemStatus.gpu_available ? 'Disponible' : 'No Disponible'}</span>
          </div>
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              systemStatus.active_training_jobs < 2 ? 'bg-green-500' : 'bg-yellow-500'
            }`}></div>
            <span>Cola: {systemStatus.active_training_jobs || 0}/2</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full mr-2 bg-blue-500"></div>
            <span>Uso GPU: {systemStatus.gpu_utilization || 0}%</span>
          </div>
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              systemStatus.system_ready ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span>Estado: {systemStatus.system_ready ? 'Listo' : 'Ocupado'}</span>
          </div>
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button
          onClick={() => setActiveStep(2)}
          className="btn-secondary"
        >
          ? Atrás
        </button>
        <button
          onClick={startTraining}
          disabled={!trainingForm.name || !systemStatus.system_ready || isLoading}
          className="btn-primary disabled:opacity-50 flex items-center bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Iniciando Entrenamiento...
            </>
          ) : (
            '?? Iniciar Entrenamiento Hiperrealista'
          )}
        </button>
      </div>
    </div>
  );

  const renderTrainingProgress = () => {
    const progress = currentJob ? trainingProgress[currentJob] : null;
    
    return (
      <div className="space-y-6">
        <div className="text-center">
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Entrenamiento en Progreso</h3>
          <p className="text-gray-600">Creando tu modelo de voz hiperrealista...</p>
          {trainingForm.language === 'ca' && (
            <div className="mt-2 text-sm text-purple-600 font-medium">
              ?? Calidad catalana premium en proceso
            </div>
          )}
        </div>

        {progress && (
          <div className="card p-6">
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-medium text-gray-700">
                Progress: {progress.progress}%
              </span>
              <span className="text-sm text-gray-500">
                Status: {progress.status}
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
              <div
                className="bg-purple-500 h-3 rounded-full transition-all duration-500"
                style={{ width: `${progress.progress}%` }}
              ></div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span className="text-gray-500">Epoch:</span>
                <span className="ml-1 font-medium">{progress.epoch}</span>
              </div>
              <div>
                <span className="text-gray-500">Loss:</span>
                <span className="ml-1 font-medium">{progress.loss?.toFixed(4) || '0.0000'}</span>
              </div>
              <div>
                <span className="text-gray-500">GPU:</span>
                <span className="ml-1 font-medium">{progress.gpu_utilization}%</span>
              </div>
              <div>
                <span className="text-gray-500">ETA:</span>
                <span className="ml-1 font-medium">
                  {progress.progress > 0 ? `${Math.max(1, Math.round((100 - progress.progress) * 0.5))} min` : '~30 min'}
                </span>
              </div>
            </div>

            {progress.message && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded text-sm text-blue-700">
                {progress.message}
              </div>
            )}

            {progress.progress === 100 && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded">
                <div className="flex items-center">
                  <div className="text-green-500 text-xl mr-3">?</div>
                  <div>
                    <h4 className="font-semibold text-green-900">Training Completed!</h4>
                    <p className="text-green-700 text-sm">
                      Your voice model is ready for synthesis. You can now use it in the Speech Synthesis section.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="flex justify-center space-x-4">
          {currentJob && progress?.status !== 'completed' && (
            <button
              onClick={() => cancelTraining(currentJob)}
              className="btn-danger"
            >
              Cancelar Entrenamiento
            </button>
          )}
          <button
            onClick={() => setActiveStep(1)}
            className="btn-primary bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
          >
            ?? Nuevo Entrenamiento Hiperrealista
          </button>
        </div>
      </div>
    );
  };


  const renderHyperrealisticTester = () => (
    <div className="card p-6">\
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Prueba de S?ntesis Hiperrealista (Neural)</h3>\
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">\
        <div>\
          <label className="block text-sm font-medium text-gray-700 mb-1">Voz</label>\
          <select value={selectedVoiceId} onChange={(e)=>setSelectedVoiceId(e.target.value)} className="input-field w-full">\
            {[...trainedVoices, ...catalanVoices].map(v => (
              <option key={v.id} value={v.id}>{v.name || v.id}</option>\
            ))}\
          </select>\
          <p className="text-xs text-gray-500 mt-1">Incluye voces entrenadas + catalanas base</p>\
        </div>\
        <div className="md:col-span-2">\
          <label className="block text-sm font-medium text-gray-700 mb-1">Texto</label>\
          <textarea value={testText} onChange={(e)=>setTestText(e.target.value)} className="input-field w-full" rows={2} />\
        </div>\
      </div>\
      <div className="mt-4 flex items-center space-x-3">\
        <button onClick={synthesizeHyperrealistic} className="btn-primary">Generar Audio Hiperrealista</button>\
        {testAudioUrl && <audio controls src={testAudioUrl} className="ml-2"/>}\
      </div>\
      <p className="text-xs text-gray-500 mt-2">Motor: XTTS v2 (entrenado) o Catal?n hiperrealista, salida neural</p>\
    </div>\
  );

  
  const renderPromptSpecPanel = () => (
    <div className=\"card p-6 mt-6\">
      <h3 className=\"text-lg font-semibold text-gray-900 mb-4\">Crear configuración desde prompt</h3>
      <p className=\"text-sm text-gray-600 mb-3\">Describe la voz (idioma, dialecto, tono, estilo) y generaremos una configuración inicial.</p>
      <div className=\"grid grid-cols-1 md:grid-cols-4 gap-3 items-end\">
        <div className=\"md:col-span-3\">
          <textarea className=\"input-field w-full\" rows={2} value={promptText} onChange={(e)=>setPromptText(e.target.value)} />
        </div>
        <div className=\"md:col-span-1\">
          <button onClick={generateSpecFromPrompt} disabled={generatingSpec} className=\"btn-primary w-full\">{generatingSpec ? 'Generando...' : 'Generar'}</button>
        </div>
      </div>
      <p className=\"text-xs text-gray-500 mt-2\">Sugerencias: “Catalán masculino cálido y expresivo (barcelonés)”</p>
    </div>
  );const renderTrainingHistory = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-900">Historial de Entrenamientos</h3>
        <button
          onClick={loadInitialData}
          className="btn-secondary text-sm"
        >
          Actualizar
        </button>
      </div>

      {renderHyperrealisticTester()}


              <div className="card overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Nombre del Modelo
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Idioma
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Estado
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progreso
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Creado
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Acciones
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {trainingSessions.map((session) => (
              <tr key={session.job_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{session.name}</div>
                  <div className="text-sm text-gray-500">{session.dialect}</div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="text-sm text-gray-900">{session.language.toUpperCase()}</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    session.status === 'completed' ? 'bg-green-100 text-green-800' :
                    session.status === 'failed' ? 'bg-red-100 text-red-800' :
                    session.status === 'training' ? 'bg-blue-100 text-blue-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {session.status}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {session.progress}%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(session.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  {session.status === 'training' && (
                    <button
                      onClick={() => {
                        setCurrentJob(session.job_id);
                        connectWebSocket(session.job_id);
                        setActiveStep(4);
                      }}
                      className="text-purple-600 hover:text-purple-900 mr-3"
                    >
                      Ver Progreso
                    </button>
                  )}
                  {session.status !== 'completed' && session.status !== 'failed' && (
                    <button
                      onClick={() => cancelTraining(session.job_id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Cancelar
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const steps = [
    { id: 1, name: 'Resumen', icon: '??' },
    { id: 2, name: 'Idioma', icon: '??' },
    { id: 3, name: 'Configuración', icon: '??' },
    { id: 4, name: 'Entrenamiento', icon: '??' },
    { id: 5, name: 'Historial', icon: '??' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <h1 className="text-4xl font-bold text-gray-900 mr-4">
              Entrenamiento XTTS v2
            </h1>
            <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-sm px-4 py-2 rounded-full font-bold">
              ? HIPERREALISTA
            </div>
          </div>
          <p className="text-gray-600 text-lg max-w-3xl mx-auto">
            Crea modelos de voz hiperrealistas con entrenamiento avanzado de IA. 
            <strong className="text-purple-600"> Especializado en catalán</strong> con datasets nativos de máxima calidad.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <nav className="flex justify-center">
            <ol className="flex items-center space-x-4">
              {steps.map((step) => (
                <li key={step.id} className="flex items-center">
                  <button
                    onClick={() => setActiveStep(step.id)}
                    className={`flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all ${
                      activeStep === step.id
                        ? 'border-purple-500 bg-purple-500 text-white'
                        : activeStep > step.id
                        ? 'border-green-500 bg-green-500 text-white'
                        : 'border-gray-300 text-gray-400'
                    }`}
                  >
                    <span className="text-sm">{step.icon}</span>
                  </button>
                  <span className={`ml-2 text-sm font-medium ${
                    activeStep === step.id ? 'text-purple-600' : 'text-gray-500'
                  }`}>
                    {step.name}
                  </span>
                  {step.id < steps.length && (
                    <div className={`w-8 h-px mx-4 ${
                      activeStep > step.id ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                  )}
                </li>
              ))}
            </ol>
          </nav>
        </div>

        {/* Content */}
        <div className="bg-white rounded-xl shadow-sm p-8">
          {activeStep === 1 && (
            <div className="text-center space-y-6">
              <div className="relative">
                <div className="text-6xl mb-4">??</div>
                <div className="absolute -top-2 -right-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs px-3 py-1 rounded-full font-bold">
                  ? HIPERREALISTA
                </div>
              </div>
              <h2 className="text-3xl font-bold text-gray-900">
                Entrenamiento de Voces Profesionales
              </h2>
              <p className="text-gray-600 max-w-3xl mx-auto text-lg">
                Crea modelos de voz hiperrealistas usando tecnología XTTS v2. 
                <strong className="text-purple-600"> Soporte especializado para catalán</strong> con datasets nativos de alta calidad.
              </p>
              
              {/* Catalan Highlight */}
              <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6 mt-6">
                <div className="flex items-center justify-center mb-4">
                  <span className="text-4xl mr-3">????</span>
                  <h3 className="text-xl font-bold text-purple-900">Catalán Hiperrealista</h3>
                </div>
                <p className="text-purple-800 mb-4">
                  Nuestro sistema especializado utiliza el dataset <strong>projecte-aina/openslr-slr69-ca-trimmed-denoised</strong> 
                  para crear voces catalanas con pronunciación nativa auténtica y patrones emocionales naturales.
                </p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div className="flex items-center text-purple-700">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                    6 dialectos nativos
                  </div>
                  <div className="flex items-center text-purple-700">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                    50K+ muestras
                  </div>
                  <div className="flex items-center text-purple-700">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                    95% calidad
                  </div>
                  <div className="flex items-center text-purple-700">
                    <span className="w-2 h-2 bg-purple-500 rounded-full mr-2"></span>
                    Pronunciación auténtica
                  </div>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="p-6 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="text-3xl mb-3">????</div>
                  <h3 className="font-semibold mb-2">Excelencia Catalana</h3>
                  <p className="text-sm text-gray-600">
                    Soporte nativo para 6 dialectos catalanes con calidad hiperrealista y pronunciación auténtica
                  </p>
                </div>
                <div className="p-6 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="text-3xl mb-3">??</div>
                  <h3 className="font-semibold mb-2">Multi-Idioma</h3>
                  <p className="text-sm text-gray-600">
                    Español, francés, inglés y portugués con datasets especializados
                  </p>
                </div>
                <div className="p-6 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="text-3xl mb-3">?</div>
                  <h3 className="font-semibold mb-2">Entrenamiento Rápido</h3>
                  <p className="text-sm text-gray-600">
                    Entrenamiento acelerado por GPU en 15-60 minutos con resultados profesionales
                  </p>
                </div>
              </div>

              <button
                onClick={() => setActiveStep(2)}
                className="btn-primary mt-8 text-lg px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600"
              >
                ?? Comenzar Entrenamiento Hiperrealista
              </button>
            </div>
          )}
          {activeStep === 2 && renderLanguageSelection()}
          {activeStep === 3 && renderTrainingConfiguration()}\n          {activeStep === 3 && renderPromptSpecPanel()}
          {activeStep === 4 && renderTrainingProgress()}
          {activeStep === 5 && renderTrainingHistory()}
        </div>
      </div>
    </div>
  );
};

export default VoiceTrainingAdvanced;

