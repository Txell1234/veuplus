import React, { useState, useRef } from 'react';
import { Play, Pause, Square } from 'lucide-react';

const AudioTest = () => {
  const [audioUrl, setAudioUrl] = useState('');
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState('');
  const audioRef = useRef(null);

  const testAudio = async () => {
    try {
      setError('');
      
      // Test amb un àudio simple
      const response = await fetch('/api/edge-tts/synthesize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: 'Hola, aquesta és una prova.',
          voice_id: 'ca-ES-EnricNeural'
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.audio_base64) {
        const url = `data:audio/wav;base64,${data.audio_base64}`;
        setAudioUrl(url);
        console.log('✅ Àudio generat:', url.substring(0, 50) + '...');
      } else {
        throw new Error(data.error || 'Error generant àudio');
      }
    } catch (err) {
      console.error('❌ Error:', err);
      setError(err.message);
    }
  };

  const playAudio = async () => {
    if (audioRef.current && audioUrl) {
      try {
        audioRef.current.src = audioUrl;
        audioRef.current.load();
        
        // Esperar que l'àudio es carregui
        await new Promise((resolve, reject) => {
          audioRef.current.oncanplaythrough = resolve;
          audioRef.current.onerror = reject;
        });
        
        // Reproduir àudio
        await audioRef.current.play();
        setIsPlaying(true);
        console.log('✅ Àudio reproduint');
        
      } catch (err) {
        console.error('❌ Error reproduint:', err);
        setError('Error reproduint àudio: ' + err.message);
        setIsPlaying(false);
      }
    }
  };

  const stopAudio = () => {
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-gray-50">
      <h3 className="text-lg font-semibold mb-4">Test d'Àudio</h3>
      
      <div className="space-y-4">
        <button
          onClick={testAudio}
          className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Generar Àudio de Test
        </button>
        
        {audioUrl && (
          <div className="space-y-2">
            <p className="text-sm text-green-600">✅ Àudio generat correctament</p>
            <div className="flex space-x-2">
              <button
                onClick={playAudio}
                disabled={isPlaying}
                className="px-3 py-1 bg-green-500 text-white rounded text-sm disabled:opacity-50"
              >
                <Play className="w-4 h-4 inline mr-1" />
                Reproduir
              </button>
              <button
                onClick={stopAudio}
                className="px-3 py-1 bg-red-500 text-white rounded text-sm"
              >
                <Square className="w-4 h-4 inline mr-1" />
                Aturar
              </button>
            </div>
          </div>
        )}
        
        {error && (
          <p className="text-sm text-red-600">❌ Error: {error}</p>
        )}
        
        <audio 
          ref={audioRef} 
          style={{ display: 'none' }}
          onended={() => setIsPlaying(false)}
          onerror={(err) => {
            console.error('❌ Error àudio:', err);
            setError('Error carregant àudio');
            setIsPlaying(false);
          }}
        />
      </div>
    </div>
  );
};

export default AudioTest;

