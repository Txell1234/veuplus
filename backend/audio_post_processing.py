"""
Sistema de Post-procesamiento de Audio para VeusPlus
Mejora la calidad del audio generado con técnicas avanzadas
"""

import asyncio
import logging
import os
import tempfile
import uuid
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import base64
import json
from datetime import datetime
import threading
import time

logger = logging.getLogger("veuplus.audio_post_processing")

class AudioPostProcessingSystem:
    """Sistema de post-procesamiento de audio"""
    
    def __init__(self):
        self.is_initialized = False
        self.processing_profiles = {
            "ultra_high": {
                "noise_reduction": True,
                "clarity_enhancement": True,
                "dynamic_range_compression": True,
                "equalization": True,
                "reverb_control": True,
                "stereo_enhancement": False,
                "quality_boost": True
            },
            "high": {
                "noise_reduction": True,
                "clarity_enhancement": True,
                "dynamic_range_compression": True,
                "equalization": False,
                "reverb_control": False,
                "stereo_enhancement": False,
                "quality_boost": True
            },
            "standard": {
                "noise_reduction": True,
                "clarity_enhancement": False,
                "dynamic_range_compression": False,
                "equalization": False,
                "reverb_control": False,
                "stereo_enhancement": False,
                "quality_boost": False
            }
        }
        
        # Parámetros de procesamiento
        self.processing_parameters = {
            "noise_reduction": {
                "threshold": 0.01,
                "aggressiveness": 0.5,
                "preserve_speech": True
            },
            "clarity_enhancement": {
                "high_freq_boost": 1.2,
                "mid_freq_balance": 1.0,
                "low_freq_cutoff": 80
            },
            "dynamic_range_compression": {
                "ratio": 3.0,
                "threshold": -20,
                "attack": 0.003,
                "release": 0.1
            },
            "equalization": {
                "bass_boost": 1.1,
                "mid_balance": 1.0,
                "treble_boost": 1.15
            }
        }
        
    async def initialize(self) -> bool:
        """Inicializar el sistema de post-procesamiento"""
        try:
            logger.info("🚀 Inicializando sistema de post-procesamiento de audio...")
            
            # Crear directorios necesarios
            self.processing_dir = Path("backend/audio_processing")
            self.processing_dir.mkdir(exist_ok=True)
            
            self.is_initialized = True
            logger.info("✅ Sistema de post-procesamiento inicializado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema de post-procesamiento: {e}")
            return False
    
    async def process_audio(
        self, 
        audio_base64: str, 
        processing_profile: str = "high",
        custom_parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Procesar audio con mejoras de calidad"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de post-procesamiento no está inicializado")
            
            logger.info(f"🎵 Procesando audio con perfil: {processing_profile}")
            
            # Decodificar audio
            audio_data = base64.b64decode(audio_base64)
            
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_path = temp_file.name
            
            # Escribir audio temporal
            with open(temp_path, 'wb') as f:
                f.write(audio_data)
            
            # Cargar audio
            audio, sr = librosa.load(temp_path, sr=None)
            
            # Obtener perfil de procesamiento
            profile = self.processing_profiles.get(processing_profile, self.processing_profiles["high"])
            
            # Aplicar parámetros personalizados
            if custom_parameters:
                profile.update(custom_parameters)
            
            # Procesar audio
            processed_audio = await self._apply_audio_processing(audio, sr, profile)
            
            # Guardar audio procesado
            processed_path = temp_path.replace('.wav', '_processed.wav')
            sf.write(processed_path, processed_audio, sr)
            
            # Leer audio procesado
            with open(processed_path, 'rb') as f:
                processed_audio_data = f.read()
            
            # Limpiar archivos temporales
            os.unlink(temp_path)
            os.unlink(processed_path)
            
            # Codificar en base64
            processed_audio_base64 = base64.b64encode(processed_audio_data).decode()
            
            return {
                'success': True,
                'processed_audio_base64': processed_audio_base64,
                'original_audio_base64': audio_base64,
                'processing_profile': processing_profile,
                'processing_parameters': profile,
                'quality_improvement': self._calculate_quality_improvement(audio, processed_audio, sr),
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error procesando audio: {e}")
            return {
                'success': False,
                'error': str(e),
                'processed_audio_base64': None
            }
    
    async def _apply_audio_processing(
        self, 
        audio: np.ndarray, 
        sr: int, 
        profile: Dict
    ) -> np.ndarray:
        """Aplicar procesamiento de audio"""
        try:
            processed_audio = audio.copy()
            
            # 1. Reducción de ruido
            if profile.get('noise_reduction', False):
                processed_audio = self._reduce_noise(processed_audio, sr)
            
            # 2. Mejora de claridad
            if profile.get('clarity_enhancement', False):
                processed_audio = self._enhance_clarity(processed_audio, sr)
            
            # 3. Compresión de rango dinámico
            if profile.get('dynamic_range_compression', False):
                processed_audio = self._apply_dynamic_compression(processed_audio, sr)
            
            # 4. Ecualización
            if profile.get('equalization', False):
                processed_audio = self._apply_equalization(processed_audio, sr)
            
            # 5. Control de reverb
            if profile.get('reverb_control', False):
                processed_audio = self._control_reverb(processed_audio, sr)
            
            # 6. Mejora de calidad
            if profile.get('quality_boost', False):
                processed_audio = self._boost_quality(processed_audio, sr)
            
            # Normalizar audio final
            processed_audio = librosa.util.normalize(processed_audio)
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en procesamiento de audio: {e}")
            return audio
    
    def _reduce_noise(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Reducir ruido del audio"""
        try:
            # Aplicar filtro de reducción de ruido
            # Filtro pasa-bajos para reducir ruido de alta frecuencia
            from scipy import signal
            
            # Diseñar filtro Butterworth
            nyquist = sr / 2
            low_cutoff = 8000  # Hz
            
            # Filtro pasa-bajos
            b, a = signal.butter(4, low_cutoff / nyquist, btype='low')
            filtered_audio = signal.filtfilt(b, a, audio)
            
            # Aplicar reducción de ruido espectral
            stft = librosa.stft(filtered_audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Estimar ruido
            noise_threshold = np.percentile(magnitude, 10)
            noise_mask = magnitude < noise_threshold
            
            # Reducir ruido
            magnitude[noise_mask] *= 0.1
            
            # Reconstruir audio
            processed_stft = magnitude * np.exp(1j * phase)
            processed_audio = librosa.istft(processed_stft)
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en reducción de ruido: {e}")
            return audio
    
    def _enhance_clarity(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Mejorar claridad del audio"""
        try:
            # Aplicar mejora de claridad espectral
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Mejorar frecuencias altas (claridad)
            freqs = librosa.fft_frequencies(sr=sr)
            high_freq_mask = freqs > 2000  # Frecuencias altas
            
            # Aumentar energía en frecuencias altas
            magnitude[high_freq_mask, :] *= 1.2
            
            # Reconstruir audio
            processed_stft = magnitude * np.exp(1j * phase)
            processed_audio = librosa.istft(processed_stft)
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en mejora de claridad: {e}")
            return audio
    
    def _apply_dynamic_compression(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Aplicar compresión de rango dinámico"""
        try:
            # Aplicar compresión dinámica
            # Calcular envolvente
            envelope = np.abs(audio)
            
            # Aplicar compresión
            threshold = 0.1  # Umbral de compresión
            ratio = 3.0  # Ratio de compresión
            
            # Compresión suave
            compressed_envelope = np.where(
                envelope > threshold,
                threshold + (envelope - threshold) / ratio,
                envelope
            )
            
            # Aplicar envolvente comprimida
            processed_audio = audio * (compressed_envelope / (envelope + 1e-8))
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en compresión dinámica: {e}")
            return audio
    
    def _apply_equalization(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Aplicar ecualización"""
        try:
            # Aplicar ecualización
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Obtener frecuencias
            freqs = librosa.fft_frequencies(sr=sr)
            
            # Ecualización
            # Graves (0-250 Hz)
            bass_mask = freqs <= 250
            magnitude[bass_mask, :] *= 1.1
            
            # Medios (250-4000 Hz)
            mid_mask = (freqs > 250) & (freqs <= 4000)
            magnitude[mid_mask, :] *= 1.0
            
            # Agudos (4000+ Hz)
            treble_mask = freqs > 4000
            magnitude[treble_mask, :] *= 1.15
            
            # Reconstruir audio
            processed_stft = magnitude * np.exp(1j * phase)
            processed_audio = librosa.istft(processed_stft)
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en ecualización: {e}")
            return audio
    
    def _control_reverb(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Controlar reverb del audio"""
        try:
            # Aplicar control de reverb
            # Reducir reverb existente
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Aplicar filtro de reverb
            # Reducir energía en frecuencias de reverb
            freqs = librosa.fft_frequencies(sr=sr)
            reverb_freqs = (freqs > 1000) & (freqs < 8000)
            magnitude[reverb_freqs, :] *= 0.9
            
            # Reconstruir audio
            processed_stft = magnitude * np.exp(1j * phase)
            processed_audio = librosa.istft(processed_stft)
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en control de reverb: {e}")
            return audio
    
    def _boost_quality(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """Mejorar calidad general del audio"""
        try:
            # Aplicar mejoras de calidad
            # 1. Normalización
            audio = librosa.util.normalize(audio)
            
            # 2. Mejora de contraste espectral
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            phase = np.angle(stft)
            
            # Aumentar contraste
            magnitude = np.power(magnitude, 0.9)
            
            # 3. Mejora de definición
            # Aumentar energía en frecuencias de voz
            freqs = librosa.fft_frequencies(sr=sr)
            voice_freqs = (freqs >= 300) & (freqs <= 3400)
            magnitude[voice_freqs, :] *= 1.05
            
            # Reconstruir audio
            processed_stft = magnitude * np.exp(1j * phase)
            processed_audio = librosa.istft(processed_stft)
            
            # 4. Normalización final
            processed_audio = librosa.util.normalize(processed_audio)
            
            return processed_audio
            
        except Exception as e:
            logger.warning(f"Error en mejora de calidad: {e}")
            return audio
    
    def _calculate_quality_improvement(
        self, 
        original_audio: np.ndarray, 
        processed_audio: np.ndarray, 
        sr: int
    ) -> Dict[str, float]:
        """Calcular mejora de calidad"""
        try:
            # Calcular métricas de calidad
            original_snr = self._calculate_snr(original_audio)
            processed_snr = self._calculate_snr(processed_audio)
            
            original_clarity = self._calculate_clarity(original_audio, sr)
            processed_clarity = self._calculate_clarity(processed_audio, sr)
            
            original_energy = np.mean(original_audio ** 2)
            processed_energy = np.mean(processed_audio ** 2)
            
            return {
                'snr_improvement': processed_snr - original_snr,
                'clarity_improvement': processed_clarity - original_clarity,
                'energy_ratio': processed_energy / (original_energy + 1e-8),
                'overall_improvement': (processed_snr + processed_clarity) - (original_snr + original_clarity)
            }
            
        except Exception as e:
            logger.warning(f"Error calculando mejora de calidad: {e}")
            return {
                'snr_improvement': 0.0,
                'clarity_improvement': 0.0,
                'energy_ratio': 1.0,
                'overall_improvement': 0.0
            }
    
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """Calcular relación señal-ruido"""
        try:
            energy = np.abs(audio)
            signal_threshold = np.percentile(energy, 20)
            signal_mask = energy > signal_threshold
            
            signal_power = np.mean(energy[signal_mask] ** 2)
            noise_power = np.mean(energy[~signal_mask] ** 2)
            
            if noise_power > 0:
                snr = 10 * np.log10(signal_power / noise_power)
                return float(snr)
            else:
                return 50.0
        except:
            return 30.0
    
    def _calculate_clarity(self, audio: np.ndarray, sr: int) -> float:
        """Calcular claridad del audio"""
        try:
            stft = librosa.stft(audio)
            magnitude = np.abs(stft)
            freqs = librosa.fft_frequencies(sr=sr)
            
            voice_mask = (freqs >= 300) & (freqs <= 3400)
            voice_energy = np.mean(magnitude[voice_mask, :])
            total_energy = np.mean(magnitude)
            
            if total_energy > 0:
                clarity = voice_energy / total_energy
                return float(clarity * 100)
            else:
                return 0.0
        except:
            return 50.0
    
    def get_processing_profiles(self) -> Dict[str, Any]:
        """Obtener perfiles de procesamiento disponibles"""
        return {
            'profiles': self.processing_profiles,
            'parameters': self.processing_parameters,
            'total_profiles': len(self.processing_profiles),
            'system': 'VeusPlus Audio Post-Processing',
            'status': 'active' if self.is_initialized else 'inactive'
        }
    
    def create_custom_profile(
        self, 
        profile_name: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Crear perfil de procesamiento personalizado"""
        try:
            profile_id = f"custom_{uuid.uuid4().hex[:8]}"
            
            custom_profile = {
                'id': profile_id,
                'name': profile_name,
                'parameters': parameters,
                'created_at': datetime.now().isoformat(),
                'type': 'custom_processing_profile'
            }
            
            self.processing_profiles[profile_id] = custom_profile
            
            logger.info(f"✅ Perfil de procesamiento personalizado creado: {profile_id}")
            return custom_profile
            
        except Exception as e:
            logger.error(f"Error creando perfil personalizado: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Instancia global del sistema de post-procesamiento
audio_post_processing = AudioPostProcessingSystem()
