import React, { useState, useEffect, useRef } from 'react';
import { Upload, Play, Pause, Mic, MicOff, Download, Settings, CheckCircle, AlertCircle, Clock, Zap } from 'lucide-react';
import api from '../config/api';

const VoiceTrainingInterface = () => {
  const [trainingStep, setTrainingStep] = useState(1);
  const [isTraining, setIsTraining] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState(0);
  const [trainingStatus, setTrainingStatus] = useState('idle');
  const [isRecording, setIsRecording] = useState(false);
  const [recordedAudio, setRecordedAudio] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [trainingConfig, setTrainingConfig] = useState({
    name: '',
    language: 'ca',
    dialect: 'central',
    quality: 'high',
    epochs: 50,
    batchSize: 8,
    learningRate: 0.0001
  });

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const fileInputRef = useRef(null);

  const trainingSteps = [
    { id: 1, title: 'Configuración', description: 'Configurar parámetros de entrenamiento' },
    { id: 2, title: 'Datos de Entrenamiento', description: 'Subir o grabar muestras de audio' },
    { id: 3, title: 'Validación', description: 'Validar calidad de los datos' },
    { id: 4, title: 'Entrenamiento', description: 'Entrenar el modelo de voz' },
    { id: 5, title: 'Evaluación', description: 'Evaluar y probar el modelo' }
  ];

  const handleConfigChange = (field, value) => {
    setTrainingConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files);
    const audioFiles = files.filter(file => file.type.startsWith('audio/'));
    
    setUploadedFiles(prev => [...prev, ...audioFiles]);
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        
        setRecordedAudio(prev => [...prev, {
          id: Date.now(),
          blob: audioBlob,
          url: audioUrl,
          duration: 0, // Se calcularía con Web Audio API
          timestamp: new Date().toISOString()
        }]);
        
        stream.getTracks().forEach(track => track.stop());
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error iniciando grabación:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  const removeAudio = (id, type) => {
    if (type === 'recorded') {
      setRecordedAudio(prev => prev.filter(audio => audio.id !== id));
    } else {
      setUploadedFiles(prev => prev.filter((_, index) => index !== id));
    }
  };

  const validateTrainingData = async () => {
    try {
      setTrainingStatus('validating');
      
      // Simular validación
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const totalSamples = recordedAudio.length + uploadedFiles.length;
      const totalDuration = recordedAudio.reduce((sum, audio) => sum + audio.duration, 0);
      
      if (totalSamples < 10) {
        setTrainingStatus('validation_failed');
        return false;
      }
      
      if (totalDuration < 30) {
        setTrainingStatus('validation_failed');
        return false;
      }
      
      setTrainingStatus('validation_success');
      return true;
    } catch (error) {
      console.error('Error validando datos:', error);
      setTrainingStatus('validation_failed');
      return false;
    }
  };

  const startTraining = async () => {
    try {
      setIsTraining(true);
      setTrainingProgress(0);
      setTrainingStatus('training');
      
      // Simular progreso de entrenamiento
      const interval = setInterval(() => {
        setTrainingProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            setTrainingStatus('completed');
            setIsTraining(false);
            return 100;
          }
          return prev + 2;
        });
      }, 100);
      
    } catch (error) {
      console.error('Error en entrenamiento:', error);
      setTrainingStatus('training_failed');
      setIsTraining(false);
    }
  };

  const getStepIcon = (step) => {
    if (step < trainingStep) {
      return <CheckCircle className="w-5 h-5 text-green-500" />;
    } else if (step === trainingStep) {
      return <Clock className="w-5 h-5 text-blue-500" />;
    } else {
      return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />;
    }
  };

  const getStatusIcon = () => {
    switch (trainingStatus) {
      case 'validation_success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'validation_failed':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'training':
        return <Zap className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      default:
        return null;
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-bold text-gray-800">Entrenamiento de Voz Personalizada</h1>
          <div className="flex items-center space-x-2">
            {getStatusIcon()}
            <span className="text-sm text-gray-600">
              {trainingStatus === 'idle' && 'Listo para comenzar'}
              {trainingStatus === 'validating' && 'Validando datos...'}
              {trainingStatus === 'validation_success' && 'Datos válidos'}
              {trainingStatus === 'validation_failed' && 'Error en validación'}
              {trainingStatus === 'training' && 'Entrenando modelo...'}
              {trainingStatus === 'completed' && 'Entrenamiento completado'}
            </span>
          </div>
        </div>

        {/* Indicador de pasos */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {trainingSteps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className="flex items-center space-x-2">
                  {getStepIcon(step.id)}
                  <div className="text-center">
                    <div className="text-sm font-medium text-gray-700">{step.title}</div>
                    <div className="text-xs text-gray-500">{step.description}</div>
                  </div>
                </div>
                {index < trainingSteps.length - 1 && (
                  <div className="flex-1 h-0.5 bg-gray-200 mx-4" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Contenido del paso actual */}
        {trainingStep === 1 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">Configuración del Entrenamiento</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nombre del Modelo
                </label>
                <input
                  type="text"
                  value={trainingConfig.name}
                  onChange={(e) => handleConfigChange('name', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Mi Voz Personalizada"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Idioma
                </label>
                <select
                  value={trainingConfig.language}
                  onChange={(e) => handleConfigChange('language', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="ca">Català</option>
                  <option value="es">Español</option>
                  <option value="en">English</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Dialecto
                </label>
                <select
                  value={trainingConfig.dialect}
                  onChange={(e) => handleConfigChange('dialect', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="central">Central</option>
                  <option value="valencian">Valencià</option>
                  <option value="balearic">Balear</option>
                  <option value="andorran">Andorrà</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Calidad
                </label>
                <select
                  value={trainingConfig.quality}
                  onChange={(e) => handleConfigChange('quality', e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="standard">Estándar</option>
                  <option value="high">Alta</option>
                  <option value="ultra_high">Ultra Alta</option>
                </select>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Épocas de Entrenamiento
                </label>
                <input
                  type="number"
                  value={trainingConfig.epochs}
                  onChange={(e) => handleConfigChange('epochs', parseInt(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="10"
                  max="200"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tamaño de Lote
                </label>
                <input
                  type="number"
                  value={trainingConfig.batchSize}
                  onChange={(e) => handleConfigChange('batchSize', parseInt(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="1"
                  max="32"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Tasa de Aprendizaje
                </label>
                <input
                  type="number"
                  step="0.0001"
                  value={trainingConfig.learningRate}
                  onChange={(e) => handleConfigChange('learningRate', parseFloat(e.target.value))}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  min="0.0001"
                  max="0.01"
                />
              </div>
            </div>
          </div>
        )}

        {trainingStep === 2 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">Datos de Entrenamiento</h2>
            
            {/* Grabación de audio */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Grabar Audio</h3>
              <div className="flex items-center space-x-4">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`p-4 rounded-full transition-colors ${
                    isRecording 
                      ? 'bg-red-500 text-white hover:bg-red-600' 
                      : 'bg-blue-500 text-white hover:bg-blue-600'
                  }`}
                >
                  {isRecording ? <MicOff className="w-6 h-6" /> : <Mic className="w-6 h-6" />}
                </button>
                <div>
                  <div className="text-sm text-gray-600">
                    {isRecording ? 'Grabando...' : 'Haz clic para grabar'}
                  </div>
                  <div className="text-xs text-gray-500">
                    Mínimo 30 segundos de audio de alta calidad
                  </div>
                </div>
              </div>
            </div>
            
            {/* Subida de archivos */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-medium text-gray-700 mb-4">Subir Archivos de Audio</h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-2">Arrastra archivos de audio aquí o haz clic para seleccionar</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="audio/*"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Seleccionar Archivos
                </button>
              </div>
            </div>
            
            {/* Lista de archivos */}
            {(recordedAudio.length > 0 || uploadedFiles.length > 0) && (
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-gray-700">Archivos de Entrenamiento</h3>
                
                {/* Audio grabado */}
                {recordedAudio.map((audio) => (
                  <div key={audio.id} className="flex items-center justify-between bg-white p-4 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      <Play className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium text-gray-700">Audio grabado</div>
                        <div className="text-xs text-gray-500">
                          {new Date(audio.timestamp).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => removeAudio(audio.id, 'recorded')}
                      className="text-red-500 hover:text-red-700"
                    >
                      Eliminar
                    </button>
                  </div>
                ))}
                
                {/* Archivos subidos */}
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="flex items-center justify-between bg-white p-4 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      <Play className="w-5 h-5 text-gray-400" />
                      <div>
                        <div className="text-sm font-medium text-gray-700">{file.name}</div>
                        <div className="text-xs text-gray-500">
                          {(file.size / 1024 / 1024).toFixed(2)} MB
                        </div>
                      </div>
                    </div>
                    <button
                      onClick={() => removeAudio(index, 'uploaded')}
                      className="text-red-500 hover:text-red-700"
                    >
                      Eliminar
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {trainingStep === 3 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">Validación de Datos</h2>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-center">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Validando Calidad de Datos</h3>
                <p className="text-gray-600 mb-4">
                  Verificando que los archivos de audio cumplan con los requisitos de calidad
                </p>
                
                {trainingStatus === 'validation_success' && (
                  <div className="text-green-600">
                    <CheckCircle className="w-12 h-12 mx-auto mb-2" />
                    <p className="font-medium">¡Datos válidos! Listo para entrenar</p>
                  </div>
                )}
                
                {trainingStatus === 'validation_failed' && (
                  <div className="text-red-600">
                    <AlertCircle className="w-12 h-12 mx-auto mb-2" />
                    <p className="font-medium">Error en validación</p>
                    <p className="text-sm">Se requieren al menos 10 muestras y 30 segundos de audio</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {trainingStep === 4 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">Entrenamiento del Modelo</h2>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-center">
                <div className="text-6xl mb-4">🤖</div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">Entrenando Modelo de Voz</h3>
                <p className="text-gray-600 mb-4">
                  Esto puede tomar varios minutos dependiendo de la calidad seleccionada
                </p>
                
                {/* Barra de progreso */}
                <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                  <div 
                    className="bg-blue-500 h-4 rounded-full transition-all duration-300"
                    style={{ width: `${trainingProgress}%` }}
                  />
                </div>
                
                <div className="text-sm text-gray-600">
                  {trainingProgress}% completado
                </div>
              </div>
            </div>
          </div>
        )}

        {trainingStep === 5 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold text-gray-800">Evaluación del Modelo</h2>
            
            <div className="bg-gray-50 rounded-lg p-6">
              <div className="text-center">
                <div className="text-6xl mb-4">🎉</div>
                <h3 className="text-lg font-medium text-gray-700 mb-2">¡Entrenamiento Completado!</h3>
                <p className="text-gray-600 mb-4">
                  Tu modelo de voz personalizada está listo para usar
                </p>
                
                <div className="space-y-4">
                  <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                    Probar Modelo
                  </button>
                  <button className="px-6 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors ml-4">
                    <Download className="w-4 h-4 inline mr-2" />
                    Descargar Modelo
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Botones de navegación */}
        <div className="flex justify-between mt-8">
          <button
            onClick={() => setTrainingStep(Math.max(1, trainingStep - 1))}
            disabled={trainingStep === 1}
            className="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Anterior
          </button>
          
          <div className="flex space-x-4">
            {trainingStep === 2 && (
              <button
                onClick={validateTrainingData}
                className="px-6 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 transition-colors"
              >
                Validar Datos
              </button>
            )}
            
            {trainingStep === 3 && trainingStatus === 'validation_success' && (
              <button
                onClick={startTraining}
                className="px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
              >
                Iniciar Entrenamiento
              </button>
            )}
            
            {trainingStep < 5 && (
              <button
                onClick={() => setTrainingStep(Math.min(5, trainingStep + 1))}
                disabled={trainingStep === 2 && (recordedAudio.length === 0 && uploadedFiles.length === 0)}
                className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Siguiente
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceTrainingInterface;
