import React, { useState, useEffect } from 'react';
import axios from 'axios';

const VoiceSelectionModal = ({ isOpen, onClose, onSelect, selectedVoiceId = null }) => {
  const [voices, setVoices] = useState([]);
  const [loading, setLoading] = useState(false);
  const [playingVoice, setPlayingVoice] = useState(null);
  const [audio, setAudio] = useState(null);

  const getApiBase = () => {
    const envUrl = process.env.REACT_APP_BACKEND_URL;
    if (envUrl && envUrl.trim() !== '') return `${envUrl.replace(/\/$/, '')}`;
    if (typeof window !== 'undefined' && window.location && window.location.port === '3000') {
      return 'http://localhost:8001';
    }
    return '';
  };
  const API = getApiBase();

  useEffect(() => {
    if (isOpen) {
      loadVoices();
    }
  }, [isOpen]);

  useEffect(() => {
    // Cleanup audio when component unmounts
    return () => {
      if (audio) {
        audio.pause();
        audio.src = '';
      }
    };
  }, [audio]);

  const loadVoices = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/api/voices`);
      setVoices(response.data.voices || []);
    } catch (error) {
      console.error('Error loading voices:', error);
    } finally {
      setLoading(false);
    }
  };

  const playVoiceSample = async (voice) => {
    try {
      // Stop current audio if playing
      if (audio) {
        audio.pause();
        audio.src = '';
      }

      setPlayingVoice(voice.id);

      // Check if voice has a sample
      if (voice.sample_audio) {
        // Play existing sample
        const newAudio = new Audio(`${API}/api/audio/${voice.id}_sample`);
        setAudio(newAudio);
        
        newAudio.onended = () => {
          setPlayingVoice(null);
        };
        
        newAudio.onerror = () => {
          console.warn('Sample audio not found, generating preview...');
          generateVoicePreview(voice);
        };
        
        await newAudio.play();
      } else {
        // Generate preview
        await generateVoicePreview(voice);
      }
    } catch (error) {
      console.error('Error playing voice sample:', error);
      setPlayingVoice(null);
    }
  };

  const generateVoicePreview = async (voice) => {
    try {
      const previewText = voice.language === 'ca' 
        ? `Hola, sóc ${voice.name}, una veu ${voice.dialect} de VeuPlus.`
        : voice.language === 'es'
        ? `Hola, soy ${voice.name}, una voz ${voice.dialect} de VeuPlus.`
        : voice.language === 'fr'
        ? `Bonjour, je suis ${voice.name}, une voix ${voice.dialect} de VeuPlus.`
        : `Hello, I'm ${voice.name}, a ${voice.dialect} voice from VeuPlus.`;

      const response = await axios.post(`${API}/api/synthesis`, {
        text: previewText,
        voice_model_id: voice.id,
        language: voice.language
      });

      if (response.data.audio_url) {
        const newAudio = new Audio(`${API}${response.data.audio_url}`);
        setAudio(newAudio);
        
        newAudio.onended = () => {
          setPlayingVoice(null);
        };
        
        await newAudio.play();
      }
    } catch (error) {
      console.error('Error generating voice preview:', error);
      setPlayingVoice(null);
    }
  };

  const stopVoicePlayback = () => {
    if (audio) {
      audio.pause();
      audio.src = '';
    }
    setPlayingVoice(null);
  };

  const handleVoiceSelect = (voice) => {
    stopVoicePlayback();
    onSelect(voice);
    onClose();
  };

  const getVoiceQualityBadge = (voice) => {
    const quality = voice.quality || voice.training_quality;
    
    if (quality === 'hyperrealistic' || quality === 'hyperrealistic_catalan') {
      return (
        <span className="px-2 py-1 text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-full">
          🎭 Hyperrealistic
        </span>
      );
    } else if (quality === 'enhanced') {
      return (
        <span className="px-2 py-1 text-xs bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-full">
          ✨ Enhanced
        </span>
      );
    } else {
      return (
        <span className="px-2 py-1 text-xs bg-gradient-to-r from-gray-500 to-gray-600 text-white rounded-full">
          🔊 Standard
        </span>
      );
    }
  };

  const getLanguageFlag = (language) => {
    const flags = {
      'ca': '🏴󠁥󠁳󠁣󠁴󠁿',
      'es': '🇪🇸',
      'fr': '🇫🇷',
      'en': '🇬🇧',
      'pt': '🇵🇹'
    };
    return flags[language] || '🌍';
  };

  const getLanguageName = (language) => {
    const names = {
      'ca': 'Català',
      'es': 'Español',
      'fr': 'Français',
      'en': 'English',
      'pt': 'Português'
    };
    return names[language] || language.toUpperCase();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-3xl p-8 max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">Select Voice Model</h2>
            <p className="text-gray-600">Choose a trained voice for your bot</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl font-bold w-8 h-8 flex items-center justify-center"
          >
            ×
          </button>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading available voices...</p>
          </div>
        ) : voices.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🎤</div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Voices Available</h3>
            <p className="text-gray-600 mb-6">
              You need to train at least one voice model before creating bots.
            </p>
            <button
              onClick={onClose}
              className="bg-purple-500 text-white px-6 py-3 rounded-xl hover:bg-purple-600"
            >
              Train Your First Voice
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {voices.map((voice) => (
              <div
                key={voice.id}
                className={`p-6 border-2 rounded-2xl cursor-pointer transition-all duration-300 transform hover:scale-105 ${
                  selectedVoiceId === voice.id
                    ? 'border-purple-500 bg-purple-50 shadow-lg'
                    : 'border-gray-200 hover:border-gray-300 hover:shadow-md'
                }`}
                onClick={() => handleVoiceSelect(voice)}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-2">
                    <span className="text-2xl">{getLanguageFlag(voice.language)}</span>
                    <div>
                      <h3 className="font-semibold text-gray-900">{voice.name}</h3>
                      <p className="text-sm text-gray-500">
                        {getLanguageName(voice.language)} - {voice.dialect}
                      </p>
                    </div>
                  </div>
                  {selectedVoiceId === voice.id && (
                    <div className="text-purple-500">
                      <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  )}
                </div>

                <div className="mb-4">
                  {getVoiceQualityBadge(voice)}
                </div>

                <div className="space-y-2 text-sm text-gray-600 mb-4">
                  <div className="flex justify-between">
                    <span>Status:</span>
                    <span className={`font-medium ${
                      voice.status === 'ready' ? 'text-green-600' : 
                      voice.status === 'training' ? 'text-blue-600' : 'text-gray-600'
                    }`}>
                      {voice.status}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span>Created:</span>
                    <span>{new Date(voice.created_at).toLocaleDateString()}</span>
                  </div>
                  {voice.real_model && (
                    <div className="flex justify-between">
                      <span>Type:</span>
                      <span className="text-purple-600 font-medium">Real Model</span>
                    </div>
                  )}
                </div>

                <div className="flex space-x-2">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (playingVoice === voice.id) {
                        stopVoicePlayback();
                      } else {
                        playVoiceSample(voice);
                      }
                    }}
                    disabled={voice.status !== 'ready'}
                    className={`flex-1 py-2 px-4 rounded-xl text-sm font-medium transition-colors ${
                      voice.status === 'ready'
                        ? playingVoice === voice.id
                          ? 'bg-red-500 text-white hover:bg-red-600'
                          : 'bg-blue-500 text-white hover:bg-blue-600'
                        : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }`}
                  >
                    {playingVoice === voice.id ? (
                      <span className="flex items-center justify-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        Stop
                      </span>
                    ) : (
                      <span className="flex items-center justify-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                        </svg>
                        Preview
                      </span>
                    )}
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleVoiceSelect(voice);
                    }}
                    className={`flex-1 py-2 px-4 rounded-xl text-sm font-medium transition-colors ${
                      selectedVoiceId === voice.id
                        ? 'bg-purple-500 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {selectedVoiceId === voice.id ? 'Selected' : 'Select'}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-8 flex justify-between items-center">
          <div className="text-sm text-gray-500">
            {voices.length} voice{voices.length !== 1 ? 's' : ''} available
          </div>
          <div className="flex space-x-3">
            <button
              onClick={onClose}
              className="px-6 py-3 border border-gray-300 rounded-xl text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            {selectedVoiceId && (
              <button
                onClick={() => {
                  const selectedVoice = voices.find(v => v.id === selectedVoiceId);
                  if (selectedVoice) {
                    handleVoiceSelect(selectedVoice);
                  }
                }}
                className="px-6 py-3 bg-purple-500 text-white rounded-xl hover:bg-purple-600"
              >
                Use Selected Voice
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VoiceSelectionModal;