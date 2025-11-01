"""
Motor ASR real usando Faster-Whisper para VeuPlus
Reemplaza el sistema placeholder con implementación funcional
"""
import os
import logging
import tempfile
from pathlib import Path
from typing import Optional, Dict, Any, Union
import torch
import torchaudio
import numpy as np
from datetime import datetime

logger = logging.getLogger("veuplus.asr")

class ASRModel:
    """Clase para gestionar modelo ASR de Faster-Whisper"""
    
    def __init__(self, model_name: str = "base"):
        self.model = None
        self.model_name = model_name
        self.is_loaded = False
        
    def load_model(self, model_name: Optional[str] = None):
        """Cargar modelo ASR"""
        try:
            if model_name:
                self.model_name = model_name
            
            # Intentar cargar Faster-Whisper
            from faster_whisper import WhisperModel
            
            # Usar GPU si está disponible
            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = "float16" if device == "cuda" else "int8"
            
            self.model = WhisperModel(
                self.model_name, 
                device=device, 
                compute_type=compute_type
            )
            
            self.is_loaded = True
            logger.info(f"Modelo ASR Whisper cargado: {self.model_name} en {device}")
            return True
            
        except ImportError as e:
            logger.error(f"Faster-Whisper no está instalado: {e}")
            return False
        except Exception as e:
            logger.error(f"Error cargando modelo ASR: {e}")
            return False
    
    def transcribe(self, audio_path: str, language: str = "ca") -> Dict[str, Any]:
        """Transcribir archivo de audio a texto"""
        if not self.is_loaded or not self.model:
            logger.error("Modelo ASR no está cargado")
            return {"text": "", "language": language, "confidence": 0.0}
        
        try:
            # Mapear códigos de idioma a códigos de Whisper
            lang_map = {
                "ca": "ca",  # Catalán
                "es": "es",  # Español  
                "en": "en",  # Inglés
                "fr": "fr",  # Francés
                "pt": "pt",  # Portugués
                "auto": None  # Detección automática
            }
            
            target_lang = lang_map.get(language.lower(), None)
            
            # Transcribir
            segments, info = self.model.transcribe(
                audio_path, 
                language=target_lang,
                beam_size=5,
                best_of=5,
                temperature=0.0,
                condition_on_previous_text=True
            )
            
            # Combinar segmentos
            full_text = ""
            total_confidence = 0.0
            segment_count = 0
            
            for segment in segments:
                full_text += segment.text
                total_confidence += segment.avg_logprob
                segment_count += 1
            
            # Calcular confianza promedio
            avg_confidence = total_confidence / max(segment_count, 1)
            
            # Detectar idioma si no se especificó
            detected_language = info.language if target_lang is None else language
            
            result = {
                "text": full_text.strip(),
                "language": detected_language,
                "confidence": max(0.0, min(1.0, (avg_confidence + 1) / 2)),  # Normalizar a 0-1
                "segments": segment_count,
                "detected_language": info.language
            }
            
            logger.info(f"Transcripción completada: {len(full_text)} caracteres, confianza: {result['confidence']:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error en transcripción: {e}")
            return {
                "text": f"[Error en transcripción: {str(e)}]",
                "language": language,
                "confidence": 0.0,
                "error": str(e)
            }

class VeuPlusASREngine:
    """Motor ASR principal para VeuPlus"""
    
    def __init__(self):
        self.asr_model = ASRModel()
        self.is_initialized = False
        
    def initialize(self):
        """Inicializar el motor ASR"""
        try:
            success = self.asr_model.load_model()
            if success:
                self.is_initialized = True
                logger.info("Motor ASR VeuPlus inicializado correctamente")
            else:
                logger.warning("Motor ASR no pudo inicializarse, usando modo fallback")
            return success
        except Exception as e:
            logger.error(f"Error inicializando motor ASR: {e}")
            return False
    
    def transcribe_audio(self, audio_data: bytes, filename: str, language: str = "ca") -> Dict[str, Any]:
        """Transcribir audio a texto"""
        
        # Si no está inicializado, devolver placeholder
        if not self.is_initialized:
            logger.warning("ASR no inicializado, devolviendo placeholder")
            return self._generate_placeholder_transcription(filename, language)
        
        try:
            # Guardar audio en archivo temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                # Transcribir
                result = self.asr_model.transcribe(temp_path, language)
                result.update({
                    "created_at": datetime.utcnow().isoformat(),
                    "real_asr": True,
                    "filename": filename
                })
                
                logger.info(f"Transcripción real completada: '{result['text'][:50]}...'")
                return result
                
            finally:
                # Limpiar archivo temporal
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error en transcripción: {e}")
            return self._generate_placeholder_transcription(filename, language, str(e))
    
    def _generate_placeholder_transcription(self, filename: str, language: str, error: Optional[str] = None) -> Dict[str, Any]:
        """Generar transcripción placeholder como fallback"""
        placeholder_text = f"[Transcripción de {filename}]"
        if error:
            placeholder_text += f" - Error: {error}"
            
        return {
            "text": placeholder_text,
            "language": language,
            "created_at": datetime.utcnow().isoformat(),
            "real_asr": False,
            "fallback_reason": "ASR engine not available",
            "filename": filename
        }
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Obtener idiomas soportados"""
        return {
            "supported_languages": ["ca", "es", "en", "fr", "pt", "auto"],
            "language_names": {
                "ca": "Catalán",
                "es": "Español", 
                "en": "Inglés",
                "fr": "Francés",
                "pt": "Portugués",
                "auto": "Detección automática"
            },
            "asr_engine": "Faster-Whisper" if self.is_initialized else "Placeholder",
            "model_name": self.asr_model.model_name if self.is_initialized else "none"
        }

# Instancia global del motor ASR
asr_engine = VeuPlusASREngine()

