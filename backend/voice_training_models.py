"""
Sistema de Entrenamiento de Modelos de Voz Personalizados para VeusPlus
Permite entrenar modelos de voz específicos con datos personalizados
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
import subprocess
import shutil

logger = logging.getLogger("veuplus.voice_training")

class VoiceTrainingSystem:
    """Sistema de entrenamiento de modelos de voz personalizados"""
    
    def __init__(self):
        self.is_initialized = False
        self.training_models = {}
        self.training_jobs = {}
        self.training_configs = {
            "ultra_high": {
                "epochs": 100,
                "batch_size": 8,
                "learning_rate": 0.0001,
                "min_samples": 50,
                "max_duration": 300,  # 5 minutos
                "quality_threshold": 0.9
            },
            "high": {
                "epochs": 50,
                "batch_size": 16,
                "learning_rate": 0.0005,
                "min_samples": 30,
                "max_duration": 200,
                "quality_threshold": 0.8
            },
            "standard": {
                "epochs": 25,
                "batch_size": 32,
                "learning_rate": 0.001,
                "min_samples": 20,
                "max_duration": 150,
                "quality_threshold": 0.7
            }
        }
        
    async def initialize(self) -> bool:
        """Inicializar el sistema de entrenamiento"""
        try:
            logger.info("🚀 Inicializando sistema de entrenamiento de voces...")
            
            # Crear directorios necesarios
            self.models_dir = Path("backend/trained_models")
            self.training_data_dir = Path("backend/training_data")
            self.models_dir.mkdir(exist_ok=True)
            self.training_data_dir.mkdir(exist_ok=True)
            
            # Cargar modelos entrenados existentes
            await self._load_existing_models()
            
            self.is_initialized = True
            logger.info("✅ Sistema de entrenamiento inicializado")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error inicializando sistema de entrenamiento: {e}")
            return False
    
    async def _load_existing_models(self):
        """Cargar modelos entrenados existentes"""
        try:
            config_file = self.models_dir / "trained_models_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.training_models = config.get('models', {})
                    logger.info(f"✅ Cargados {len(self.training_models)} modelos entrenados")
        except Exception as e:
            logger.warning(f"Error cargando modelos entrenados: {e}")
    
    def _save_models_config(self):
        """Guardar configuración de modelos entrenados"""
        try:
            config = {
                'models': self.training_models,
                'last_updated': datetime.now().isoformat()
            }
            config_file = self.models_dir / "trained_models_config.json"
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando configuración de modelos: {e}")
    
    async def start_training(
        self, 
        model_name: str, 
        training_data: List[bytes], 
        language: str = "ca",
        training_config: str = "high",
        model_description: str = ""
    ) -> Dict[str, Any]:
        """Iniciar entrenamiento de modelo de voz"""
        try:
            if not self.is_initialized:
                raise Exception("Sistema de entrenamiento no está inicializado")
            
            logger.info(f"🎯 Iniciando entrenamiento de modelo: {model_name}")
            
            # Generar ID único para el modelo
            model_id = f"trained_{uuid.uuid4().hex[:8]}"
            
            # Obtener configuración de entrenamiento
            config = self.training_configs.get(training_config, self.training_configs["high"])
            
            # Validar datos de entrenamiento
            validation_result = await self._validate_training_data(training_data, config)
            if not validation_result['valid']:
                raise Exception(f"Datos de entrenamiento inválidos: {validation_result['error']}")
            
            # Crear trabajo de entrenamiento
            training_job = {
                'id': model_id,
                'name': model_name,
                'description': model_description,
                'language': language,
                'config': training_config,
                'status': 'preparing',
                'progress': 0,
                'created_at': datetime.now().isoformat(),
                'training_data_count': len(training_data),
                'estimated_duration': self._estimate_training_duration(len(training_data), config)
            }
            
            self.training_jobs[model_id] = training_job
            
            # Iniciar entrenamiento en hilo separado
            training_thread = threading.Thread(
                target=self._run_training,
                args=(model_id, training_data, config, language)
            )
            training_thread.start()
            
            logger.info(f"✅ Entrenamiento iniciado: {model_id}")
            return training_job
            
        except Exception as e:
            logger.error(f"❌ Error iniciando entrenamiento: {e}")
            return {
                'success': False,
                'error': str(e),
                'model_id': None
            }
    
    async def _validate_training_data(self, training_data: List[bytes], config: Dict) -> Dict[str, Any]:
        """Validar datos de entrenamiento"""
        try:
            if len(training_data) < config['min_samples']:
                return {
                    'valid': False,
                    'error': f"Mínimo {config['min_samples']} muestras requeridas, se proporcionaron {len(training_data)}"
                }
            
            total_duration = 0
            valid_samples = 0
            
            for i, audio_data in enumerate(training_data):
                try:
                    # Crear archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                        temp_path = temp_file.name
                    
                    # Escribir audio temporal
                    with open(temp_path, 'wb') as f:
                        f.write(audio_data)
                    
                    # Cargar y validar audio
                    audio, sr = librosa.load(temp_path, sr=None)
                    duration = len(audio) / sr
                    
                    # Verificar duración
                    if duration < 1.0:  # Mínimo 1 segundo
                        logger.warning(f"Muestra {i}: duración muy corta ({duration:.1f}s)")
                        continue
                    
                    if duration > config['max_duration']:
                        logger.warning(f"Muestra {i}: duración muy larga ({duration:.1f}s)")
                        continue
                    
                    # Verificar calidad
                    if self._check_audio_quality(audio, sr) < config['quality_threshold']:
                        logger.warning(f"Muestra {i}: calidad insuficiente")
                        continue
                    
                    total_duration += duration
                    valid_samples += 1
                    
                    # Limpiar archivo temporal
                    os.unlink(temp_path)
                    
                except Exception as e:
                    logger.warning(f"Error validando muestra {i}: {e}")
                    continue
            
            if valid_samples < config['min_samples']:
                return {
                    'valid': False,
                    'error': f"Solo {valid_samples} muestras válidas de {len(training_data)}"
                }
            
            return {
                'valid': True,
                'valid_samples': valid_samples,
                'total_duration': total_duration,
                'average_duration': total_duration / valid_samples
            }
            
        except Exception as e:
            return {
                'valid': False,
                'error': f"Error validando datos: {e}"
            }
    
    def _check_audio_quality(self, audio: np.ndarray, sr: int) -> float:
        """Verificar calidad del audio"""
        try:
            # Calcular métricas de calidad
            quality_score = 0.0
            
            # 1. Relación señal-ruido
            snr = self._calculate_snr(audio)
            if snr > 20:
                quality_score += 0.3
            elif snr > 10:
                quality_score += 0.2
            else:
                quality_score += 0.1
            
            # 2. Claridad espectral
            clarity = self._calculate_clarity(audio, sr)
            if clarity > 80:
                quality_score += 0.3
            elif clarity > 60:
                quality_score += 0.2
            else:
                quality_score += 0.1
            
            # 3. Estabilidad de tono
            stability = self._calculate_pitch_stability(audio, sr)
            if stability > 0.8:
                quality_score += 0.2
            elif stability > 0.6:
                quality_score += 0.15
            else:
                quality_score += 0.1
            
            # 4. Energía consistente
            energy_consistency = self._calculate_energy_consistency(audio)
            if energy_consistency > 0.7:
                quality_score += 0.2
            elif energy_consistency > 0.5:
                quality_score += 0.15
            else:
                quality_score += 0.1
            
            return min(quality_score, 1.0)
            
        except Exception as e:
            logger.warning(f"Error verificando calidad de audio: {e}")
            return 0.5
    
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
    
    def _calculate_pitch_stability(self, audio: np.ndarray, sr: int) -> float:
        """Calcular estabilidad del tono"""
        try:
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sr)
            pitch_values = []
            
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 1:
                pitch_std = np.std(pitch_values)
                pitch_mean = np.mean(pitch_values)
                stability = 1.0 - (pitch_std / pitch_mean)
                return max(0.0, min(1.0, stability))
            else:
                return 0.5
        except:
            return 0.5
    
    def _calculate_energy_consistency(self, audio: np.ndarray) -> float:
        """Calcular consistencia de energía"""
        try:
            rms = librosa.feature.rms(y=audio)
            energy_std = np.std(rms)
            energy_mean = np.mean(rms)
            
            if energy_mean > 0:
                consistency = 1.0 - (energy_std / energy_mean)
                return max(0.0, min(1.0, consistency))
            else:
                return 0.5
        except:
            return 0.5
    
    def _estimate_training_duration(self, sample_count: int, config: Dict) -> str:
        """Estimar duración del entrenamiento"""
        try:
            # Estimación basada en configuración
            base_time_per_epoch = 2  # minutos por época
            total_epochs = config['epochs']
            time_per_sample = 0.1  # minutos por muestra
            
            total_time = (base_time_per_epoch * total_epochs) + (time_per_sample * sample_count)
            
            if total_time < 60:
                return f"{int(total_time)} minutos"
            else:
                hours = total_time / 60
                return f"{hours:.1f} horas"
        except:
            return "Estimación no disponible"
    
    def _run_training(self, model_id: str, training_data: List[bytes], config: Dict, language: str):
        """Ejecutar entrenamiento del modelo"""
        try:
            logger.info(f"🎯 Iniciando entrenamiento del modelo: {model_id}")
            
            # Actualizar estado
            self.training_jobs[model_id]['status'] = 'training'
            self.training_jobs[model_id]['progress'] = 10
            
            # Crear directorio de trabajo
            work_dir = self.training_data_dir / model_id
            work_dir.mkdir(exist_ok=True)
            
            # Procesar datos de entrenamiento
            processed_data = self._process_training_data(training_data, work_dir)
            self.training_jobs[model_id]['progress'] = 30
            
            # Extraer características
            features = self._extract_training_features(processed_data, config)
            self.training_jobs[model_id]['progress'] = 50
            
            # Entrenar modelo (simulado)
            model_result = self._train_model(features, config, language)
            self.training_jobs[model_id]['progress'] = 80
            
            # Crear modelo entrenado
            trained_model = {
                'id': model_id,
                'name': self.training_jobs[model_id]['name'],
                'description': self.training_jobs[model_id]['description'],
                'language': language,
                'config': config,
                'status': 'ready',
                'created_at': datetime.now().isoformat(),
                'training_duration': self.training_jobs[model_id]['estimated_duration'],
                'quality_score': model_result['quality_score'],
                'model_path': str(work_dir),
                'features': features,
                'type': 'trained_model',
                'provider': 'veuplus_training',
                'available': True
            }
            
            # Guardar modelo
            self.training_models[model_id] = trained_model
            self._save_models_config()
            
            # Actualizar estado final
            self.training_jobs[model_id]['status'] = 'completed'
            self.training_jobs[model_id]['progress'] = 100
            self.training_jobs[model_id]['completed_at'] = datetime.now().isoformat()
            
            logger.info(f"✅ Entrenamiento completado: {model_id}")
            
        except Exception as e:
            logger.error(f"❌ Error en entrenamiento: {e}")
            self.training_jobs[model_id]['status'] = 'failed'
            self.training_jobs[model_id]['error'] = str(e)
    
    def _process_training_data(self, training_data: List[bytes], work_dir: Path) -> List[Dict]:
        """Procesar datos de entrenamiento"""
        try:
            processed_data = []
            
            for i, audio_data in enumerate(training_data):
                try:
                    # Crear archivo temporal
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                        temp_path = temp_file.name
                    
                    # Escribir audio temporal
                    with open(temp_path, 'wb') as f:
                        f.write(audio_data)
                    
                    # Cargar audio
                    audio, sr = librosa.load(temp_path, sr=22050)
                    
                    # Procesar audio
                    processed_audio = {
                        'id': i,
                        'audio': audio,
                        'sr': sr,
                        'duration': len(audio) / sr,
                        'quality': self._check_audio_quality(audio, sr)
                    }
                    
                    processed_data.append(processed_audio)
                    
                    # Limpiar archivo temporal
                    os.unlink(temp_path)
                    
                except Exception as e:
                    logger.warning(f"Error procesando muestra {i}: {e}")
                    continue
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error procesando datos de entrenamiento: {e}")
            return []
    
    def _extract_training_features(self, processed_data: List[Dict], config: Dict) -> Dict[str, Any]:
        """Extraer características para entrenamiento"""
        try:
            if not processed_data:
                return {}
            
            # Combinar todos los audios
            all_audio = np.concatenate([item['audio'] for item in processed_data])
            sr = processed_data[0]['sr']
            
            # Extraer características globales
            features = {}
            
            # Características espectrales
            features['spectral_centroid'] = float(np.mean(librosa.feature.spectral_centroid(y=all_audio, sr=sr)))
            features['spectral_rolloff'] = float(np.mean(librosa.feature.spectral_rolloff(y=all_audio, sr=sr)))
            features['spectral_bandwidth'] = float(np.mean(librosa.feature.spectral_bandwidth(y=all_audio, sr=sr)))
            
            # Características de tono
            pitches, magnitudes = librosa.piptrack(y=all_audio, sr=sr)
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if pitch_values:
                features['mean_pitch'] = float(np.mean(pitch_values))
                features['pitch_std'] = float(np.std(pitch_values))
                features['pitch_range'] = float(np.max(pitch_values) - np.min(pitch_values))
            
            # Características de ritmo
            tempo, beats = librosa.beat.beat_track(y=all_audio, sr=sr)
            features['tempo'] = float(tempo)
            features['beat_strength'] = float(np.mean(beats))
            
            # Características de energía
            rms = librosa.feature.rms(y=all_audio)
            features['mean_energy'] = float(np.mean(rms))
            features['energy_std'] = float(np.std(rms))
            
            # Características de calidad
            features['average_quality'] = float(np.mean([item['quality'] for item in processed_data]))
            features['total_duration'] = float(sum([item['duration'] for item in processed_data]))
            features['sample_count'] = len(processed_data)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extrayendo características: {e}")
            return {}
    
    def _train_model(self, features: Dict, config: Dict, language: str) -> Dict[str, Any]:
        """Entrenar modelo (simulado)"""
        try:
            # Simular entrenamiento
            time.sleep(2)  # Simular tiempo de entrenamiento
            
            # Calcular puntuación de calidad basada en características
            quality_score = 0.0
            
            # Evaluar características
            if features.get('average_quality', 0) > 0.8:
                quality_score += 0.3
            elif features.get('average_quality', 0) > 0.6:
                quality_score += 0.2
            else:
                quality_score += 0.1
            
            if features.get('sample_count', 0) >= config['min_samples']:
                quality_score += 0.2
            
            if features.get('total_duration', 0) > 60:  # Más de 1 minuto
                quality_score += 0.2
            
            if features.get('pitch_std', 0) < 50:  # Tono estable
                quality_score += 0.15
            
            if features.get('energy_std', 0) < 0.1:  # Energía consistente
                quality_score += 0.15
            
            return {
                'quality_score': min(quality_score, 1.0),
                'training_epochs': config['epochs'],
                'final_loss': 0.1 + (1.0 - quality_score) * 0.5
            }
            
        except Exception as e:
            logger.error(f"Error entrenando modelo: {e}")
            return {
                'quality_score': 0.5,
                'training_epochs': 0,
                'final_loss': 1.0
            }
    
    def get_training_status(self, model_id: str) -> Dict[str, Any]:
        """Obtener estado del entrenamiento"""
        if model_id in self.training_jobs:
            return self.training_jobs[model_id]
        else:
            return {'error': 'Modelo no encontrado'}
    
    def get_trained_models(self) -> Dict[str, Any]:
        """Obtener modelos entrenados"""
        return {
            'models': list(self.training_models.values()),
            'total': len(self.training_models),
            'system': 'VeusPlus Voice Training',
            'status': 'active' if self.is_initialized else 'inactive'
        }
    
    def delete_trained_model(self, model_id: str) -> bool:
        """Eliminar modelo entrenado"""
        try:
            if model_id in self.training_models:
                # Eliminar directorio de trabajo
                work_dir = self.training_data_dir / model_id
                if work_dir.exists():
                    shutil.rmtree(work_dir)
                
                del self.training_models[model_id]
                self._save_models_config()
                logger.info(f"✅ Modelo entrenado eliminado: {model_id}")
                return True
            else:
                logger.warning(f"Modelo entrenado no encontrado: {model_id}")
                return False
        except Exception as e:
            logger.error(f"Error eliminando modelo entrenado: {e}")
            return False

# Instancia global del sistema de entrenamiento
voice_training_system = VoiceTrainingSystem()



















