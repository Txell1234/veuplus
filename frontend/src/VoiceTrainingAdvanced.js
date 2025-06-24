import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

const VoiceTrainingAdvanced = () => {
  const [activeStep, setActiveStep] = useState(1);
  const [trainingSessions, setTrainingSessions] = useState([]);
  const [currentJob, setCurrentJob] = useState(null);
  const [trainingProgress, setTrainingProgress] = useState({});
  const [systemStatus, setSystemStatus] = useState({});
  const [supportedLanguages, setSupportedLanguages] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const wsRef = useRef(null);

  const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

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
      const [sessionsRes, statusRes, languagesRes] = await Promise.all([
        axios.get(`${API}/api/training/jobs`),
        axios.get(`${API}/api/training/system/status`),
        axios.get(`${API}/api/training/languages`)
      ]);
      
      setTrainingSessions(sessionsRes.data.jobs || []);
      setSystemStatus(statusRes.data || {});
      setSupportedLanguages(languagesRes.data.supported_languages || {});
      
      console.log('Loaded data:', {
        sessions: sessionsRes.data.jobs?.length || 0,
        status: statusRes.data,
        languages: Object.keys(languagesRes.data.supported_languages || {})
      });
      
    } catch (error) {
      console.error('Error loading training data:', error);
      // Try alternative endpoint structure
      try {
        const languagesRes = await axios.get(`${API}/api/training/languages`);
        setSupportedLanguages(languagesRes.data.supported_languages || {});
      } catch (altError) {
        console.error('Alternative load failed:', altError);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const connectWebSocket = (jobId) => {
    if (wsRef.current) {
      wsRef.current.close();
    }

    // Use the same domain but switch to WebSocket protocol
    const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/training/ws/${jobId}`;
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
      const response = await axios.post(`${API}/training/start`, trainingForm);
      const jobId = response.data.job_id;
      
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
      await axios.delete(`${API}/training/jobs/${jobId}`);
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

  const renderLanguageSelection = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-900">Select Language & Dialect</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(supportedLanguages).map(([langCode, langData]) => (
          <div
            key={langCode}
            onClick={() => setTrainingForm(prev => ({ ...prev, language: langCode }))}
            className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
              trainingForm.language === langCode
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="text-lg font-semibold mb-2">
              {langData.name}
            </div>
            <div className="text-sm text-gray-600">
              {langData.dialects?.length || 0} dialects supported
            </div>
            {langCode === 'ca' && (
              <div className="mt-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                Hyperrealistic Quality
              </div>
            )}
          </div>
        ))}
      </div>

      {trainingForm.language && supportedLanguages[trainingForm.language]?.dialects && (
        <div className="mt-6">
          <h4 className="text-lg font-medium mb-3">Select Dialect</h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {supportedLanguages[trainingForm.language].dialects.map((dialect) => (
              <button
                key={dialect}
                onClick={() => setTrainingForm(prev => ({ ...prev, dialect }))}
                className={`p-3 text-sm rounded-lg border transition-all ${
                  trainingForm.dialect === dialect
                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {dialect.charAt(0).toUpperCase() + dialect.slice(1)}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="flex justify-between mt-8">
        <button
          onClick={() => setActiveStep(1)}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={() => setActiveStep(3)}
          disabled={!trainingForm.language}
          className="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50"
        >
          Next: Configuration
        </button>
      </div>
    </div>
  );

  const renderTrainingConfiguration = () => (
    <div className="space-y-6">
      <h3 className="text-xl font-semibold text-gray-900">Training Configuration</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Voice Model Name
          </label>
          <input
            type="text"
            value={trainingForm.name}
            onChange={(e) => setTrainingForm(prev => ({ ...prev, name: e.target.value }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            placeholder="My Custom Voice Model"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Training Epochs
          </label>
          <select
            value={trainingForm.training_config.num_epochs}
            onChange={(e) => setTrainingForm(prev => ({
              ...prev,
              training_config: { ...prev.training_config, num_epochs: parseInt(e.target.value) }
            }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="25">25 epochs (Quick - 15 min)</option>
            <option value="50">50 epochs (Standard - 30 min)</option>
            <option value="100">100 epochs (High Quality - 60 min)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Batch Size
          </label>
          <select
            value={trainingForm.training_config.batch_size}
            onChange={(e) => setTrainingForm(prev => ({
              ...prev,
              training_config: { ...prev.training_config, batch_size: parseInt(e.target.value) }
            }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="2">2 (Low GPU Memory)</option>
            <option value="4">4 (Recommended)</option>
            <option value="8">8 (High GPU Memory)</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Learning Rate
          </label>
          <select
            value={trainingForm.training_config.learning_rate}
            onChange={(e) => setTrainingForm(prev => ({
              ...prev,
              training_config: { ...prev.training_config, learning_rate: parseFloat(e.target.value) }
            }))}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
          >
            <option value="0.00005">0.00005 (Conservative)</option>
            <option value="0.0001">0.0001 (Recommended)</option>
            <option value="0.0002">0.0002 (Aggressive)</option>
          </select>
        </div>
      </div>

      {trainingForm.language === 'ca' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="text-blue-500 text-xl mr-3">🇪🇸</div>
            <div>
              <h4 className="font-semibold text-blue-900">Catalan Dataset Integration</h4>
              <p className="text-blue-700 text-sm mt-1">
                Using projecte-aina/openslr-slr69-ca-trimmed-denoised for hyperrealistic Catalan voices.
                This dataset provides native pronunciation patterns for the {trainingForm.dialect} dialect.
              </p>
              <div className="mt-3 flex items-center">
                <input
                  type="checkbox"
                  id="use_catalan_dataset"
                  checked={trainingForm.use_catalan_dataset}
                  onChange={(e) => setTrainingForm(prev => ({ ...prev, use_catalan_dataset: e.target.checked }))}
                  className="mr-2"
                />
                <label htmlFor="use_catalan_dataset" className="text-sm text-blue-700">
                  Use Catalan dataset for enhanced quality
                </label>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* System Requirements Check */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-3">System Status</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              systemStatus.gpu_available ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span>GPU: {systemStatus.gpu_available ? 'Available' : 'Not Available'}</span>
          </div>
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              systemStatus.active_training_jobs < 2 ? 'bg-green-500' : 'bg-yellow-500'
            }`}></div>
            <span>Queue: {systemStatus.active_training_jobs || 0}/2</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full mr-2 bg-blue-500"></div>
            <span>GPU Usage: {systemStatus.gpu_utilization || 0}%</span>
          </div>
          <div className="flex items-center">
            <div className={`w-3 h-3 rounded-full mr-2 ${
              systemStatus.system_ready ? 'bg-green-500' : 'bg-red-500'
            }`}></div>
            <span>Status: {systemStatus.system_ready ? 'Ready' : 'Busy'}</span>
          </div>
        </div>
      </div>

      <div className="flex justify-between mt-8">
        <button
          onClick={() => setActiveStep(2)}
          className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
        >
          Back
        </button>
        <button
          onClick={startTraining}
          disabled={!trainingForm.name || !systemStatus.system_ready || isLoading}
          className="px-8 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600 disabled:opacity-50 flex items-center"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
              Starting Training...
            </>
          ) : (
            'Start Training'
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
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Training in Progress</h3>
          <p className="text-gray-600">Creating your hyperrealistic voice model...</p>
        </div>

        {progress && (
          <div className="bg-white border border-gray-200 rounded-lg p-6">
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
                  <div className="text-green-500 text-xl mr-3">✅</div>
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
              className="px-6 py-2 border border-red-300 text-red-600 rounded-lg hover:bg-red-50"
            >
              Cancel Training
            </button>
          )}
          <button
            onClick={() => setActiveStep(1)}
            className="px-6 py-2 bg-purple-500 text-white rounded-lg hover:bg-purple-600"
          >
            Start New Training
          </button>
        </div>
      </div>
    );
  };

  const renderTrainingHistory = () => (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h3 className="text-xl font-semibold text-gray-900">Training History</h3>
        <button
          onClick={loadInitialData}
          className="px-4 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200"
        >
          Refresh
        </button>
      </div>

      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Model Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Language
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Progress
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Created
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
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
                      View Progress
                    </button>
                  )}
                  {session.status !== 'completed' && session.status !== 'failed' && (
                    <button
                      onClick={() => cancelTraining(session.job_id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Cancel
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
    { id: 1, name: 'Overview', icon: '📋' },
    { id: 2, name: 'Language', icon: '🌍' },
    { id: 3, name: 'Configuration', icon: '⚙️' },
    { id: 4, name: 'Training', icon: '🚀' },
    { id: 5, name: 'History', icon: '📊' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            XTTS v2 Voice Training
          </h1>
          <p className="text-gray-600">
            Create hyperrealistic voice models with advanced AI training
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
              <div className="text-6xl mb-4">🎤</div>
              <h2 className="text-2xl font-bold text-gray-900">
                Professional Voice Training
              </h2>
              <p className="text-gray-600 max-w-2xl mx-auto">
                Train hyperrealistic voice models using XTTS v2 technology. 
                Support for 5 languages with specialized Catalan dataset integration.
              </p>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
                <div className="p-6 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-3">🇪🇸</div>
                  <h3 className="font-semibold mb-2">Catalan Excellence</h3>
                  <p className="text-sm text-gray-600">
                    Native support for 6 Catalan dialects with hyperrealistic quality
                  </p>
                </div>
                <div className="p-6 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-3">🌍</div>
                  <h3 className="font-semibold mb-2">Multi-Language</h3>
                  <p className="text-sm text-gray-600">
                    Spanish, French, English, Portuguese support
                  </p>
                </div>
                <div className="p-6 border border-gray-200 rounded-lg">
                  <div className="text-3xl mb-3">⚡</div>
                  <h3 className="font-semibold mb-2">Fast Training</h3>
                  <p className="text-sm text-gray-600">
                    GPU-accelerated training in 15-60 minutes
                  </p>
                </div>
              </div>

              <button
                onClick={() => setActiveStep(2)}
                className="mt-8 px-8 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 text-lg font-medium"
              >
                Start Training
              </button>
            </div>
          )}
          {activeStep === 2 && renderLanguageSelection()}
          {activeStep === 3 && renderTrainingConfiguration()}
          {activeStep === 4 && renderTrainingProgress()}
          {activeStep === 5 && renderTrainingHistory()}
        </div>
      </div>
    </div>
  );
};

export default VoiceTrainingAdvanced;