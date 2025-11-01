"""
ALIA Kit ASR Advanced - Reconeixement de veu avançat
Integra Whisper + models ALIA per ASR multilingüe
"""

import os
import logging
import tempfile
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

# Verificar disponibilitat de llibreries
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    logger.warning("Whisper not available")

try:
    from transformers import pipeline, AutoModelForSpeechSeq2Seq, AutoProcessor
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available")

try:
    import librosa
    import soundfile as sf
    AUDIO_LIBS_AVAILABLE = True
except ImportError:
    AUDIO_LIBS_AVAILABLE = False
    logger.warning("Audio libraries not available")


class AliaASRAdvanced:
    """
    ASR avançat amb models ALIA Kit i Whisper
    """
    
    def __init__(self):
        self.name = "ALIA ASR Advanced"
        self.whisper_model = None
        self.alia_asr_pipeline = None
        self.device = "cuda" if torch.cuda.is_available() and TRANSFORMERS_AVAILABLE else "cpu"
        logger.info(f"✅ ALIA ASR Advanced initialized on {self.device}")
    
    def get_alia_asr_models(self, language: str) -> List[str]:
        """
        Obtenir models ASR d'ALIA Kit per idioma
        """
        models_by_language = {
            "ca": [
                "projecte-aina/whisper-large-v3-ca",  # Whisper català
                "BSC-LT/alia-asr-ca",  # Model ALIA ASR català (si existeix)
            ],
            "es": [
                "openai/whisper-large-v3",  # Whisper multilingüe
            ],
            "eu": [
                "openai/whisper-large-v3",
            ],
            "gl": [
                "openai/whisper-large-v3",
            ],
            "multi": [
                "openai/whisper-large-v3",  # Model multilingüe
            ]
        }
        
        return models_by_language.get(language, models_by_language["multi"])
    
    async def transcribe_audio(
        self,
        audio_file: bytes,
        language: str = "ca",
        model_preference: str = "auto",
        return_timestamps: bool = False
    ) -> Dict[str, Any]:
        """
        Transcriure àudio amb models ALIA/Whisper
        """
        try:
            logger.info(f"🎯 ALIA ASR: Transcribing audio in {language}")
            
            # Guardar àudio temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_file)
            
            # Intentar models ALIA primer
            if model_preference in ["auto", "alia"] and TRANSFORMERS_AVAILABLE:
                result = await self._try_alia_asr(temp_path, language, return_timestamps)
                if result.get("success"):
                    os.unlink(temp_path)
                    return result
            
            # Fallback a Whisper
            if WHISPER_AVAILABLE:
                result = await self._whisper_asr(temp_path, language, return_timestamps)
                os.unlink(temp_path)
                return result
            
            os.unlink(temp_path)
            return {
                "success": False,
                "error": "No ASR models available"
            }
            
        except Exception as e:
            logger.error(f"ALIA ASR failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _try_alia_asr(
        self,
        audio_path: str,
        language: str,
        return_timestamps: bool
    ) -> Dict[str, Any]:
        """
        Intentar transcripció amb models ALIA
        """
        models = self.get_alia_asr_models(language)
        
        for model_id in models:
            try:
                logger.info(f"🔄 Provant model ASR: {model_id}")
                
                # Carregar pipeline ASR
                if self.alia_asr_pipeline is None:
                    try:
                        self.alia_asr_pipeline = pipeline(
                            "automatic-speech-recognition",
                            model=model_id,
                            device=0 if self.device == "cuda" else -1,
                            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                        )
                        logger.info(f"✅ Model ASR carregat: {model_id}")
                    except Exception as load_error:
                        logger.warning(f"No es pot carregar {model_id}: {load_error}")
                        continue
                
                # Transcriure
                result = self.alia_asr_pipeline(
                    audio_path,
                    return_timestamps=return_timestamps,
                    generate_kwargs={"language": language}
                )
                
                text = result.get("text", "")
                if not text:
                    continue
                
                logger.info(f"✅ ALIA ASR exitós: {text[:50]}...")
                
                return {
                    "success": True,
                    "text": text,
                    "language": language,
                    "model_used": model_id,
                    "method": "alia_asr",
                    "timestamps": result.get("chunks", []) if return_timestamps else None,
                    "confidence": 0.95  # Estimat
                }
                
            except Exception as model_error:
                logger.warning(f"Model {model_id} fallà: {model_error}")
                continue
        
        return {"success": False, "error": "No ALIA ASR models available"}
    
    async def _whisper_asr(
        self,
        audio_path: str,
        language: str,
        return_timestamps: bool
    ) -> Dict[str, Any]:
        """
        Transcripció amb Whisper (fallback)
        """
        try:
            logger.info(f"🔄 Whisper ASR fallback")
            
            # Carregar model Whisper si no està carregat
            if self.whisper_model is None:
                model_size = "base"  # Usar base per velocitat
                self.whisper_model = whisper.load_model(model_size)
                logger.info(f"✅ Whisper model loaded: {model_size}")
            
            # Transcriure
            result = self.whisper_model.transcribe(
                audio_path,
                language=language if language != "multi" else None,
                task="transcribe",
                verbose=False
            )
            
            text = result.get("text", "").strip()
            
            if not text:
                return {
                    "success": False,
                    "error": "Whisper returned empty transcription"
                }
            
            logger.info(f"✅ Whisper ASR exitós: {text[:50]}...")
            
            return {
                "success": True,
                "text": text,
                "language": result.get("language", language),
                "model_used": "openai/whisper-base",
                "method": "whisper_fallback",
                "segments": result.get("segments", []) if return_timestamps else None,
                "confidence": 0.90  # Estimat
            }
            
        except Exception as e:
            logger.error(f"Whisper ASR failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def detect_language(self, audio_file: bytes) -> Dict[str, Any]:
        """
        Detectar idioma de l'àudio
        """
        try:
            if not WHISPER_AVAILABLE:
                return {
                    "success": False,
                    "error": "Whisper not available for language detection"
                }
            
            # Guardar àudio temporal
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
                temp_file.write(audio_file)
            
            # Carregar model Whisper
            if self.whisper_model is None:
                self.whisper_model = whisper.load_model("base")
            
            # Detectar idioma
            audio = whisper.load_audio(temp_path)
            audio = whisper.pad_or_trim(audio)
            mel = whisper.log_mel_spectrogram(audio).to(self.whisper_model.device)
            _, probs = self.whisper_model.detect_language(mel)
            
            detected_language = max(probs, key=probs.get)
            confidence = probs[detected_language]
            
            os.unlink(temp_path)
            
            logger.info(f"✅ Language detected: {detected_language} ({confidence:.2%})")
            
            return {
                "success": True,
                "language": detected_language,
                "confidence": confidence,
                "all_probabilities": dict(sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5])
            }
            
        except Exception as e:
            logger.error(f"Language detection failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Instància global
alia_asr_advanced = AliaASRAdvanced()

