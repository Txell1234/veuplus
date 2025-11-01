"""
ALIA Kit Real BSC - Models TTS reals del Barcelona Supercomputing Center
Sense Edge-TTS - Només models oficials BSC
"""

import os
import tempfile
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Verificar disponibilitat
try:
    from TTS.api import TTS
    COQUI_TTS_AVAILABLE = True
except ImportError:
    COQUI_TTS_AVAILABLE = False
    logger.warning("Coqui TTS not available")

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch not available")

try:
    from segre_integration import segre_transcribe
    SEGRE_AVAILABLE = True
except ImportError:
    SEGRE_AVAILABLE = False
    logger.warning("SEGRE not available")


class AliaKitRealBSC:
    """
    ALIA Kit amb models TTS reals del BSC
    """
    
    def __init__(self):
        self.name = "ALIA Kit Real BSC"
        self.tts_model = None
        self.device = "cuda" if TORCH_AVAILABLE and torch.cuda.is_available() else "cpu"
        logger.info(f"✅ ALIA Kit Real BSC initialized on {self.device}")
    
    def get_bsc_tts_model(self, language: str = "ca") -> Optional[str]:
        """
        Obtenir millor model TTS BSC per idioma
        """
        # Models oficials del projecte AINA i BSC
        models = {
            "ca": "tts_models/ca/custom/vits",  # Model català de Coqui TTS
        }
        return models.get(language)
    
    async def synthesize_tts_real_bsc(
        self,
        text: str,
        language: str = "ca",
        dialect: str = "central",
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Síntesi TTS amb models BSC reals
        """
        try:
            logger.info(f"🎯 ALIA Kit Real BSC: '{text[:30]}...' en {language}")
            
            # Aplicar SEGRE si és català
            phonetic_text = text
            segre_applied = False
            if language == "ca" and SEGRE_AVAILABLE:
                try:
                    phonetic_result = segre_transcribe(text, dialect=dialect)
                    if phonetic_result:
                        phonetic_text = phonetic_result[0]
                        segre_applied = True
                        logger.info(f"✅ SEGRE: {text[:20]}... -> {phonetic_text[:20]}...")
                except Exception as e:
                    logger.warning(f"SEGRE failed: {e}")
            
            # Intentar síntesi amb Coqui TTS
            if COQUI_TTS_AVAILABLE:
                result = await self._synthesize_with_coqui(
                    phonetic_text,
                    language,
                    dialect,
                    segre_applied
                )
                if result.get("success"):
                    return result
            
            # Si no hi ha Coqui TTS, retornar error amb instruccions
            return {
                "success": False,
                "error": "ALIA Kit requires Coqui TTS. Install: pip install TTS",
                "note": "Per usar models BSC reals, instal·la Coqui TTS",
                "alternative": "Usa /api/edge-tts/synthesize per veus estàndard"
            }
            
        except Exception as e:
            logger.error(f"ALIA Kit Real BSC failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _synthesize_with_coqui(
        self,
        text: str,
        language: str,
        dialect: str,
        segre_applied: bool
    ) -> Dict[str, Any]:
        """
        Síntesi amb Coqui TTS (models BSC/AINA)
        """
        try:
            logger.info(f"🔄 Sintetitzant amb Coqui TTS")
            
            # Carregar model si no està carregat
            if self.tts_model is None:
                model_name = self.get_bsc_tts_model(language)
                if not model_name:
                    return {
                        "success": False,
                        "error": f"No BSC model for language: {language}"
                    }
                
                logger.info(f"📥 Carregant model Coqui TTS: {model_name}")
                self.tts_model = TTS(model_name, gpu=(self.device == "cuda"))
                logger.info(f"✅ Model carregat: {model_name}")
            
            # Generar àudio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_path = temp_file.name
            
            self.tts_model.tts_to_file(text=text, file_path=temp_path)
            
            # Verificar fitxer
            if not os.path.exists(temp_path):
                return {
                    "success": False,
                    "error": "TTS file not created"
                }
            
            file_size = os.path.getsize(temp_path)
            if file_size < 1024:
                os.unlink(temp_path)
                return {
                    "success": False,
                    "error": f"TTS audio too small: {file_size} bytes"
                }
            
            # Llegir àudio
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            os.unlink(temp_path)
            audio_base64 = base64.b64encode(audio_data).decode()
            
            logger.info(f"✅ ALIA Kit BSC exitós ({file_size} bytes)")
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "synthesis_method": "alia_kit_bsc_real",
                "quality": "alia_professional_bsc",
                "provider": "alia_kit_bsc",
                "model_used": self.get_bsc_tts_model(language),
                "file_size": file_size,
                "segre_applied": segre_applied,
                "dialect": dialect,
                "language": language,
                "device": self.device,
                "created_at": datetime.now().isoformat(),
                "note": "Model BSC real via Coqui TTS"
            }
            
        except Exception as e:
            logger.error(f"Coqui TTS synthesis failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Instància global
alia_kit_real_bsc = AliaKitRealBSC()

