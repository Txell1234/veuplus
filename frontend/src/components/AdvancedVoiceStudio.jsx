import React, { useState, useEffect } from 'react';
import { 
  Mic, 
  MicOff, 
  Play, 
  Pause, 
  Download, 
  Upload, 
  Settings, 
  Zap, 
  Star, 
  Heart,
  Share2,
  BarChart3,
  Activity,
  Waveform,
  Volume2,
  Clock,
  CheckCircle,
  AlertCircle,
  Info
} from 'lucide-react';
import VoiceControlPanel from './VoiceControlPanel';
import VoiceVisualization from './VoiceVisualization';
import VoiceTrainingInterface from './VoiceTrainingInterface';
import api from '../config/api';

const AdvancedVoiceStudio = () => {
  const [activeTab, setActiveTab] = useState('synthesis');
  const [currentVoice, setCurrentVoice] = useState(null);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [audioHistory, setAudioHistory] = useState([]);
  const [voiceSettings, setVoiceSettings] = useState({
    rate: 0,
    pitch: 0,
    volume: 0,
    emotion: 'neutral',
    accent: 'neutral',
    quality: 'high'
  });
  const [systemStatus, setSystemStatus] = useState({});
  const [voiceStatistics, setVoiceStatistics] = useState({});

  const tabs = [
    { id: 'synthesis', name: 'Síntesis de Voz', icon: <Mic className="w-4 h-4" /> },
    { id: 'cloning', name: 'Clonación', icon: <Zap className="w-4 h-4" /> },
    { id: 'training', name: 'Entrenamiento', icon: <Activity className="w-4 h-4" /> },
    { id: 'mixing', name: 'Mezcla', icon: <BarChart3 className="w-4 h-4" /> },
    { id: 'tuning', name: 'Ajuste Fino', icon: <Settings className="w-4 h-4" /> },
    { id: 'management', name: 'Gestión', icon: <Star className="w-4 h-4" /> }
  ];

  useEffect(() => {
    loadSystemStatus();
    loadAvailableVoices();
    loadVoiceStatistics();
  }, []);

  const loadSystemStatus = async () => {
    try {
      const response = await api.get('/advanced-tts/status');
      setSystemStatus(response.data);
    } catch (error) {
      console.error('Error cargando estado del sistema:', error);
    }
  };

  const loadAvailableVoices = async () => {
    try {
      const response = await api.get('/advanced-tts/voice-management/voices');
      setAvailableVoices(response.data.voices || []);
      
      // Seleccionar primera voz por defecto
      if (response.data.voices && response.data.voices.length > 0) {
        setCurrentVoice(response.data.voices[0]);
      }
    } catch (error) {
      console.error('Error cargando voces:', error);
    }
  };

  const loadVoiceStatistics = async () => {
    try {
      const response = await api.get('/advanced-tts/voice-management/statistics');
      setVoiceStatistics(response.data);
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
    }
  };

  const handleGenerateSpeech = async (text, settings = {}) => {
    if (!text.trim()) return;
    
    setIsGenerating(true);
    try {
      const response = await api.post('/advanced-tts/parameter-tuning/synthesize', {
        voice_id: currentVoice?.id,
        text: text,
        tuning_profile_id: 'default',
        language: 'ca',
        custom_overrides: { ...voiceSettings, ...settings }
      });
      
      if (response.data.success) {
        const audioData = {
          id: Date.now(),
          text: text,
          audio_base64: response.data.audio_base64,
          voice: currentVoice,
          settings: { ...voiceSettings, ...settings },
          timestamp: new Date().toISOString()
        };
        
        setCurrentAudio(audioData);
        setAudioHistory(prev => [audioData, ...prev.slice(0, 9)]); // Mantener últimos 10
      }
    } catch (error) {
      console.error('Error generando audio:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlayPause = () => {
    if (currentAudio) {
      if (isPlaying) {
        // Pausar audio
        setIsPlaying(false);
      } else {
        // Reproducir audio
        const audio = new Audio(`data:audio/wav;base64,${currentAudio.audio_base64}`);
        audio.play();
        setIsPlaying(true);
        
        audio.onended = () => setIsPlaying(false);
        audio.onerror = () => setIsPlaying(false);
      }
    }
  };

  const handleDownloadAudio = async (audio) => {
    try {
      const link = document.createElement('a');
      link.href = `data:audio/wav;base64,${audio.audio_base64}`;
      link.download = `veuplus_audio_${audio.id}.wav`;
      link.click();
    } catch (error) {
      console.error('Error descargando audio:', error);
    }
  };

  const handleShareAudio = async (audio) => {
    try {
      if (navigator.share) {
        await navigator.share({
          title: 'Audio generado con VeuPlus',
          text: `Escucha este audio: "${audio.text}"`,
          url: window.location.href
        });
      } else {
        // Fallback: copiar al portapapeles
        await navigator.clipboard.writeText(`Audio generado con VeuPlus: "${audio.text}"`);
        alert('Enlace copiado al portapapeles');
      }
    } catch (error) {
      console.error('Error compartiendo audio:', error);
    }
  };

  const handleFavoriteAudio = async (audioId, isFavorited) => {
    try {
      // Implementar lógica de favoritos
      console.log(`Audio ${audioId} ${isFavorited ? 'añadido a' : 'eliminado de'} favoritos`);
    } catch (error) {
      console.error('Error gestionando favoritos:', error);
    }
  };

  const getSystemStatusIcon = (system) => {
    if (system.available) {
      return <CheckCircle className="w-4 h-4 text-green-500" />;
    } else {
      return <AlertCircle className="w-4 h-4 text-red-500" />;
    }
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 'synthesis':
        return (
          <div className="space-y-6">
            <VoiceControlPanel
              currentVoice={currentVoice}
              onVoiceChange={setCurrentVoice}
              onGenerateSpeech={handleGenerateSpeech}
              isGenerating={isGenerating}
              audioHistory={audioHistory}
              onPlayAudio={handlePlayPause}
              onDownloadAudio={handleDownloadAudio}
              onShareAudio={handleShareAudio}
              onFavoriteAudio={handleFavoriteAudio}
            />
            
            {currentAudio && (
              <VoiceVisualization
                audioData={`data:audio/wav;base64,${currentAudio.audio_base64}`}
                isPlaying={isPlaying}
                currentTime={0}
                duration={0}
                voiceSettings={voiceSettings}
              />
            )}
          </div>
        );
      
      case 'cloning':
        return (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Clonación de Voz</h2>
            <div className="text-center py-12">
              <Zap className="w-16 h-16 text-blue-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Sistema de Clonación de Voz</h3>
              <p className="text-gray-600 mb-4">
                Sube muestras de audio para crear una voz personalizada
              </p>
              <button className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
                <Upload className="w-4 h-4 inline mr-2" />
                Subir Muestras de Audio
              </button>
            </div>
          </div>
        );
      
      case 'training':
        return <VoiceTrainingInterface />;
      
      case 'mixing':
        return (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Mezcla de Voces</h2>
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-purple-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Sistema de Mezcla de Voces</h3>
              <p className="text-gray-600 mb-4">
                Combina diferentes voces para crear sonidos únicos
              </p>
              <button className="px-6 py-3 bg-purple-500 text-white rounded-lg hover:bg-purple-600 transition-colors">
                Crear Voz Mezclada
              </button>
            </div>
          </div>
        );
      
      case 'tuning':
        return (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Ajuste Fino de Parámetros</h2>
            <div className="text-center py-12">
              <Settings className="w-16 h-16 text-orange-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-700 mb-2">Sistema de Ajuste Fino</h3>
              <p className="text-gray-600 mb-4">
                Ajusta finamente los parámetros de síntesis de voz
              </p>
              <button className="px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
                Configurar Parámetros
              </button>
            </div>
          </div>
        );
      
      case 'management':
        return (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">Gestión de Voces</h2>
            
            {/* Estadísticas */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-blue-600">
                  {voiceStatistics.total_voices || 0}
                </div>
                <div className="text-sm text-gray-600">Total de Voces</div>
              </div>
              <div className="bg-green-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-green-600">
                  {voiceStatistics.by_category?.edge_tts || 0}
                </div>
                <div className="text-sm text-gray-600">Edge-TTS</div>
              </div>
              <div className="bg-purple-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-purple-600">
                  {voiceStatistics.by_category?.cloned || 0}
                </div>
                <div className="text-sm text-gray-600">Clonadas</div>
              </div>
              <div className="bg-orange-50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-orange-600">
                  {voiceStatistics.by_category?.trained || 0}
                </div>
                <div className="text-sm text-gray-600">Entrenadas</div>
              </div>
            </div>
            
            {/* Lista de voces */}
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-700">Voces Disponibles</h3>
              {availableVoices.map((voice) => (
                <div key={voice.id} className="flex items-center justify-between bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                      <Volume2 className="w-5 h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="font-medium text-gray-700">{voice.name}</div>
                      <div className="text-sm text-gray-500">
                        {voice.language} • {voice.quality} • {voice.category}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button className="p-2 text-gray-400 hover:text-blue-500 transition-colors">
                      <Play className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-green-500 transition-colors">
                      <Download className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                      <Heart className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-800">VeuPlus Advanced Voice Studio</h1>
            </div>
            
            {/* Estado del sistema */}
            <div className="flex items-center space-x-4">
              {Object.entries(systemStatus).map(([key, system]) => (
                <div key={key} className="flex items-center space-x-1">
                  {getSystemStatusIcon(system)}
                  <span className="text-sm text-gray-600 capitalize">
                    {key.replace('_', ' ')}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.icon}
                <span>{tab.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Contenido */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {renderTabContent()}
      </div>
    </div>
  );
};

export default AdvancedVoiceStudio;



















