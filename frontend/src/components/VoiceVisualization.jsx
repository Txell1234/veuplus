import React, { useState, useEffect, useRef } from 'react';
import { Waveform, BarChart3, Activity, Zap } from 'lucide-react';

const VoiceVisualization = ({ 
  audioData, 
  isPlaying, 
  currentTime, 
  duration,
  voiceSettings = {},
  onTimeUpdate
}) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const [visualizationType, setVisualizationType] = useState('waveform');
  const [audioContext, setAudioContext] = useState(null);
  const [analyser, setAnalyser] = useState(null);
  const [dataArray, setDataArray] = useState(null);

  useEffect(() => {
    if (audioData) {
      initializeAudioContext();
    }
    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
      if (audioContext) {
        audioContext.close();
      }
    };
  }, [audioData]);

  const initializeAudioContext = async () => {
    try {
      const audio = new Audio(audioData);
      const context = new (window.AudioContext || window.webkitAudioContext)();
      const source = context.createMediaElementSource(audio);
      const analyserNode = context.createAnalyser();
      
      analyserNode.fftSize = 256;
      const bufferLength = analyserNode.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      
      source.connect(analyserNode);
      analyserNode.connect(context.destination);
      
      setAudioContext(context);
      setAnalyser(analyserNode);
      setDataArray(dataArray);
      
      // Iniciar visualización
      drawVisualization();
    } catch (error) {
      console.error('Error inicializando contexto de audio:', error);
    }
  };

  const drawVisualization = () => {
    if (!analyser || !dataArray) return;

    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;

    const draw = () => {
      analyser.getByteFrequencyData(dataArray);
      
      ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
      ctx.fillRect(0, 0, width, height);
      
      switch (visualizationType) {
        case 'waveform':
          drawWaveform(ctx, width, height, dataArray);
          break;
        case 'spectrum':
          drawSpectrum(ctx, width, height, dataArray);
          break;
        case 'bars':
          drawBars(ctx, width, height, dataArray);
          break;
        case 'particles':
          drawParticles(ctx, width, height, dataArray);
          break;
        default:
          drawWaveform(ctx, width, height, dataArray);
      }
      
      animationRef.current = requestAnimationFrame(draw);
    };
    
    draw();
  };

  const drawWaveform = (ctx, width, height, dataArray) => {
    ctx.strokeStyle = '#3B82F6';
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    const sliceWidth = width / dataArray.length;
    let x = 0;
    
    for (let i = 0; i < dataArray.length; i++) {
      const v = dataArray[i] / 255.0;
      const y = (v * height) / 2;
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
      
      x += sliceWidth;
    }
    
    ctx.stroke();
  };

  const drawSpectrum = (ctx, width, height, dataArray) => {
    const barWidth = width / dataArray.length;
    
    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = (dataArray[i] / 255) * height;
      const x = i * barWidth;
      const y = height - barHeight;
      
      // Crear gradiente de color
      const gradient = ctx.createLinearGradient(0, y, 0, height);
      gradient.addColorStop(0, '#3B82F6');
      gradient.addColorStop(1, '#1E40AF');
      
      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, barWidth, barHeight);
    }
  };

  const drawBars = (ctx, width, height, dataArray) => {
    const barWidth = width / dataArray.length;
    const maxBarHeight = height * 0.8;
    
    for (let i = 0; i < dataArray.length; i++) {
      const barHeight = (dataArray[i] / 255) * maxBarHeight;
      const x = i * barWidth;
      const y = height - barHeight;
      
      // Color basado en la frecuencia
      const hue = (i / dataArray.length) * 360;
      ctx.fillStyle = `hsl(${hue}, 70%, 50%)`;
      ctx.fillRect(x, y, barWidth - 1, barHeight);
    }
  };

  const drawParticles = (ctx, width, height, dataArray) => {
    const particles = [];
    const particleCount = 50;
    
    for (let i = 0; i < particleCount; i++) {
      const x = (i / particleCount) * width;
      const y = height / 2 + Math.sin(Date.now() * 0.001 + i) * 50;
      const size = (dataArray[i % dataArray.length] / 255) * 10;
      
      ctx.beginPath();
      ctx.arc(x, y, size, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(59, 130, 246, ${size / 10})`;
      ctx.fill();
    }
  };

  const getVisualizationIcon = (type) => {
    switch (type) {
      case 'waveform':
        return <Waveform className="w-4 h-4" />;
      case 'spectrum':
        return <BarChart3 className="w-4 h-4" />;
      case 'bars':
        return <BarChart3 className="w-4 h-4" />;
      case 'particles':
        return <Activity className="w-4 h-4" />;
      default:
        return <Waveform className="w-4 h-4" />;
    }
  };

  const getVisualizationName = (type) => {
    switch (type) {
      case 'waveform':
        return 'Ondas';
      case 'spectrum':
        return 'Espectro';
      case 'bars':
        return 'Barras';
      case 'particles':
        return 'Partículas';
      default:
        return 'Ondas';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-700">Visualización de Audio</h3>
        <div className="flex items-center space-x-2">
          {['waveform', 'spectrum', 'bars', 'particles'].map((type) => (
            <button
              key={type}
              onClick={() => setVisualizationType(type)}
              className={`p-2 rounded-lg transition-colors ${
                visualizationType === type
                  ? 'bg-blue-100 text-blue-600'
                  : 'text-gray-400 hover:text-blue-600 hover:bg-blue-50'
              }`}
              title={getVisualizationName(type)}
            >
              {getVisualizationIcon(type)}
            </button>
          ))}
        </div>
      </div>

      {/* Canvas de visualización */}
      <div className="relative">
        <canvas
          ref={canvasRef}
          width={800}
          height={200}
          className="w-full h-48 bg-gray-900 rounded-lg"
        />
        
        {/* Indicador de tiempo */}
        {duration > 0 && (
          <div className="absolute bottom-2 left-2 right-2">
            <div className="bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded">
              {Math.floor(currentTime / 60)}:{(currentTime % 60).toFixed(0).padStart(2, '0')} / {Math.floor(duration / 60)}:{(duration % 60).toFixed(0).padStart(2, '0')}
            </div>
          </div>
        )}
      </div>

      {/* Información de la voz */}
      <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-600">
            {Math.round((voiceSettings.rate || 0) * 100)}%
          </div>
          <div className="text-sm text-gray-500">Velocidad</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {Math.round((voiceSettings.pitch || 0) * 100)}Hz
          </div>
          <div className="text-sm text-gray-500">Tono</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-purple-600">
            {Math.round((voiceSettings.volume || 0) * 100)}%
          </div>
          <div className="text-sm text-gray-500">Volumen</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-orange-600">
            {voiceSettings.emotion || 'neutral'}
          </div>
          <div className="text-sm text-gray-500">Emoción</div>
        </div>
      </div>

      {/* Análisis de audio en tiempo real */}
      {dataArray && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Análisis en Tiempo Real</h4>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-lg font-semibold text-blue-600">
                {Math.round(dataArray.reduce((a, b) => a + b, 0) / dataArray.length)}
              </div>
              <div className="text-xs text-gray-500">Energía Promedio</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-green-600">
                {Math.max(...dataArray)}
              </div>
              <div className="text-xs text-gray-500">Pico Máximo</div>
            </div>
            <div>
              <div className="text-lg font-semibold text-purple-600">
                {dataArray.filter(x => x > 128).length}
              </div>
              <div className="text-xs text-gray-500">Frecuencias Altas</div>
            </div>
          </div>
        </div>
      )}

      {/* Indicador de calidad */}
      <div className="mt-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-medium text-gray-700">Calidad de Audio</span>
          <span className="text-sm text-gray-500">
            {voiceSettings.quality || 'high'}
          </span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className="bg-gradient-to-r from-green-400 to-blue-500 h-2 rounded-full transition-all duration-300"
            style={{ 
              width: `${(voiceSettings.quality === 'ultra_high' ? 100 : 
                       voiceSettings.quality === 'high' ? 80 : 
                       voiceSettings.quality === 'standard' ? 60 : 40)}%` 
            }}
          />
        </div>
      </div>
    </div>
  );
};

export default VoiceVisualization;
