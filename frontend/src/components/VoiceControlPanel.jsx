import React, { useState, useEffect } from 'react';
import { Play, Pause, Volume2, Settings, Download, Share2, Heart, Star } from 'lucide-react';
import api from '../config/api';

const VoiceControlPanel = ({ 
  currentVoice, 
  onVoiceChange, 
  onGenerateSpeech, 
  isGenerating,
  audioHistory = [],
  onPlayAudio,
  onDownloadAudio,
  onShareAudio,
  onFavoriteAudio
}) => {
  const [voiceSettings, setVoiceSettings] = useState({
    rate: 0,
    pitch: 0,
    volume: 0,
    emotion: 'neutral',
    accent: 'neutral',
    quality: 'high'
  });

  const [isPlaying, setIsPlaying] = useState(false);
  const [currentAudio, setCurrentAudio] = useState(null);
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [favorites, setFavorites] = useState([]);

  // Cargar favoritos del localStorage
  useEffect(() => {
    const savedFavorites = localStorage.getItem('veuplus_favorites');
    if (savedFavorites) {
      setFavorites(JSON.parse(savedFavorites));
    }
  }, []);

  // Guardar favoritos en localStorage
  const saveFavorites = (newFavorites) => {
    setFavorites(newFavorites);
    localStorage.setItem('veuplus_favorites', JSON.stringify(newFavorites));
  };

  const handleVoiceSettingChange = (setting, value) => {
    const newSettings = { ...voiceSettings, [setting]: value };
    setVoiceSettings(newSettings);
    
    // Aplicar cambios en tiempo real si hay audio actual
    if (currentAudio) {
      applyVoiceSettings(newSettings);
    }
  };

  const applyVoiceSettings = async (settings) => {
    try {
      // Aquí se aplicarían los ajustes de voz en tiempo real
      console.log('Aplicando ajustes de voz:', settings);
    } catch (error) {
      console.error('Error aplicando ajustes de voz:', error);
    }
  };

  const handleGenerateSpeech = async (text) => {
    if (!text.trim()) return;
    
    try {
      const result = await onGenerateSpeech(text, {
        ...voiceSettings,
        voice_id: currentVoice?.id
      });
      
      if (result) {
        setCurrentAudio(result);
      }
    } catch (error) {
      console.error('Error generando audio:', error);
    }
  };

  const handlePlayPause = () => {
    if (currentAudio) {
      if (isPlaying) {
        currentAudio.pause();
        setIsPlaying(false);
      } else {
        currentAudio.play();
        setIsPlaying(true);
      }
    }
  };

  const handleFavorite = (audioId) => {
    const isFavorited = favorites.includes(audioId);
    let newFavorites;
    
    if (isFavorited) {
      newFavorites = favorites.filter(id => id !== audioId);
    } else {
      newFavorites = [...favorites, audioId];
    }
    
    saveFavorites(newFavorites);
    onFavoriteAudio?.(audioId, !isFavorited);
  };

  const handleShare = async (audioId) => {
    try {
      const audio = audioHistory.find(a => a.id === audioId);
      if (audio) {
        await onShareAudio?.(audio);
      }
    } catch (error) {
      console.error('Error compartiendo audio:', error);
    }
  };

  const handleDownload = async (audioId) => {
    try {
      const audio = audioHistory.find(a => a.id === audioId);
      if (audio) {
        await onDownloadAudio?.(audio);
      }
    } catch (error) {
      console.error('Error descargando audio:', error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Panel de Control de Voz</h2>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
            className="p-2 text-gray-600 hover:text-blue-600 transition-colors"
            title="Configuración avanzada"
          >
            <Settings className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Controles principales */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        {/* Control de reproducción */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">Reproducción</h3>
          <div className="flex items-center space-x-3">
            <button
              onClick={handlePlayPause}
              disabled={!currentAudio}
              className="p-3 bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            </button>
            <div className="flex-1">
              <div className="flex items-center space-x-2">
                <Volume2 className="w-4 h-4 text-gray-500" />
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={voiceSettings.volume * 100}
                  onChange={(e) => handleVoiceSettingChange('volume', e.target.value / 100)}
                  className="flex-1"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Control de velocidad */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">Velocidad</h3>
          <div className="space-y-3">
            <input
              type="range"
              min="-50"
              max="50"
              value={voiceSettings.rate * 100}
              onChange={(e) => handleVoiceSettingChange('rate', e.target.value / 100)}
              className="w-full"
            />
            <div className="text-center text-sm text-gray-600">
              {voiceSettings.rate > 0 ? '+' : ''}{Math.round(voiceSettings.rate * 100)}%
            </div>
          </div>
        </div>

        {/* Control de tono */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-700 mb-3">Tono</h3>
          <div className="space-y-3">
            <input
              type="range"
              min="-50"
              max="50"
              value={voiceSettings.pitch * 100}
              onChange={(e) => handleVoiceSettingChange('pitch', e.target.value / 100)}
              className="w-full"
            />
            <div className="text-center text-sm text-gray-600">
              {voiceSettings.pitch > 0 ? '+' : ''}{Math.round(voiceSettings.pitch * 100)}Hz
            </div>
          </div>
        </div>
      </div>

      {/* Configuración avanzada */}
      {showAdvancedSettings && (
        <div className="bg-gray-50 rounded-lg p-4 mb-6">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Configuración Avanzada</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Control de emoción */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Emoción</label>
              <select
                value={voiceSettings.emotion}
                onChange={(e) => handleVoiceSettingChange('emotion', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="neutral">Neutral</option>
                <option value="happy">Alegre</option>
                <option value="sad">Triste</option>
                <option value="excited">Emocionado</option>
                <option value="calm">Tranquilo</option>
                <option value="urgent">Urgente</option>
              </select>
            </div>

            {/* Control de acento */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Acento</label>
              <select
                value={voiceSettings.accent}
                onChange={(e) => handleVoiceSettingChange('accent', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="neutral">Neutral</option>
                <option value="central">Central</option>
                <option value="valencian">Valenciano</option>
                <option value="balearic">Balear</option>
                <option value="andorran">Andorrano</option>
              </select>
            </div>

            {/* Control de calidad */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Calidad</label>
              <select
                value={voiceSettings.quality}
                onChange={(e) => handleVoiceSettingChange('quality', e.target.value)}
                className="w-full p-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="standard">Estándar</option>
                <option value="high">Alta</option>
                <option value="ultra_high">Ultra Alta</option>
                <option value="neural">Neural</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Historial de audio */}
      {audioHistory.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="text-lg font-semibold text-gray-700 mb-4">Historial de Audio</h3>
          <div className="space-y-3 max-h-64 overflow-y-auto">
            {audioHistory.map((audio) => (
              <div key={audio.id} className="flex items-center justify-between bg-white rounded-lg p-3 shadow-sm">
                <div className="flex-1">
                  <p className="text-sm text-gray-600 truncate">{audio.text}</p>
                  <p className="text-xs text-gray-500">
                    {new Date(audio.timestamp).toLocaleString()}
                  </p>
                </div>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => handleFavorite(audio.id)}
                    className={`p-2 rounded-full transition-colors ${
                      favorites.includes(audio.id)
                        ? 'text-red-500 bg-red-50'
                        : 'text-gray-400 hover:text-red-500 hover:bg-red-50'
                    }`}
                    title="Añadir a favoritos"
                  >
                    <Heart className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleShare(audio.id)}
                    className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-full transition-colors"
                    title="Compartir"
                  >
                    <Share2 className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDownload(audio.id)}
                    className="p-2 text-gray-400 hover:text-green-500 hover:bg-green-50 rounded-full transition-colors"
                    title="Descargar"
                  >
                    <Download className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Presets rápidos */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-gray-700 mb-3">Presets Rápidos</h3>
        <div className="flex flex-wrap gap-2">
          {[
            { name: 'Natural', settings: { rate: 0, pitch: 0, volume: 0, emotion: 'neutral' } },
            { name: 'Expresivo', settings: { rate: 0.05, pitch: 0.02, volume: 0.02, emotion: 'excited' } },
            { name: 'Profesional', settings: { rate: -0.02, pitch: 0.01, volume: 0, emotion: 'neutral' } },
            { name: 'Casual', settings: { rate: 0.03, pitch: 0, volume: 0.01, emotion: 'happy' } },
            { name: 'Dramático', settings: { rate: 0.08, pitch: 0.05, volume: 0.05, emotion: 'excited' } }
          ].map((preset) => (
            <button
              key={preset.name}
              onClick={() => setVoiceSettings({ ...voiceSettings, ...preset.settings })}
              className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors text-sm"
            >
              {preset.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default VoiceControlPanel;
