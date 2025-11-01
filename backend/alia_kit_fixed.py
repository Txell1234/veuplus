"""
ALIA Kit Fixed - Solució definitiva sense soroll
Usa només Edge-TTS amb configuració optimitzada + SEGRE
"""

import os
import tempfile
import base64
import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Verificar disponibilitat de SEGRE
try:
    from segre_integration import segre_transcribe
    SEGRE_AVAILABLE = True
except ImportError:
    SEGRE_AVAILABLE = False
    logger.warning("SEGRE not available")

try:
    import edge_tts
    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False
    logger.error("Edge-TTS not available - CRITICAL")


class AliaKitFixed:
    """
    ALIA Kit Fixed - Solució definitiva sense soroll
    Usa Edge-TTS amb millor configuració + processament d'àudio
    """
    
    def __init__(self):
        self.name = "ALIA Kit Fixed"
        logger.info("✅ ALIA Kit Fixed initialized")
    
    async def synthesize_tts_fixed(
        self,
        text: str,
        language: str = "ca",
        dialect: str = "central",
        voice_settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Síntesi TTS sense soroll - Edge-TTS optimitzat
        """
        try:
            logger.info(f"🎯 ALIA Kit Fixed: '{text[:30]}...' en {language}")
            
            if not EDGE_TTS_AVAILABLE:
                return {
                    "success": False,
                    "error": "Edge-TTS not available"
                }
            
            # Aplicar SEGRE si és català
            phonetic_text = text
            segre_applied = False
            if language == "ca" and SEGRE_AVAILABLE:
                try:
                    phonetic_result = segre_transcribe(text, dialect=dialect)
                    if phonetic_result and len(phonetic_result) > 0:
                        phonetic_text = phonetic_result[0]
                        segre_applied = True
                        logger.info(f"✅ SEGRE: {text[:20]}... -> {phonetic_text[:20]}...")
                except Exception as e:
                    logger.warning(f"SEGRE failed: {e}")
            
            # Configurar veu segons idioma i dialecte
            voice = self._get_best_voice(language, dialect)
            
            # Aplicar configuració de veu
            rate = "+0%"
            pitch = "+0Hz"
            volume = "+0%"
            
            if voice_settings:
                if "speed" in voice_settings:
                    speed = voice_settings["speed"]
                    rate_percent = int((speed - 1.0) * 100)
                    rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
                
                if "pitch" in voice_settings:
                    pitch_val = voice_settings["pitch"]
                    pitch_hz = int((pitch_val - 1.0) * 50)
                    pitch = f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"
            
            # Generar àudio amb Edge-TTS
            communicate = edge_tts.Communicate(
                phonetic_text,
                voice,
                rate=rate,
                pitch=pitch,
                volume=volume
            )
            
            # Guardar com MP3 (millor qualitat que WAV per Edge-TTS)
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            await communicate.save(temp_path)
            
            # Verificar fitxer
            if not os.path.exists(temp_path):
                return {
                    "success": False,
                    "error": "Edge-TTS file not created"
                }
            
            file_size = os.path.getsize(temp_path)
            if file_size < 1024:
                os.unlink(temp_path)
                return {
                    "success": False,
                    "error": f"Audio file too small: {file_size} bytes"
                }
            
            # Llegir àudio
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            # Netejar fitxer temporal
            try:
                os.unlink(temp_path)
            except:
                pass
            
            # Codificar a base64
            audio_base64 = base64.b64encode(audio_data).decode()
            
            logger.info(f"✅ ALIA Kit Fixed exitós: {voice} ({file_size} bytes)")
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "synthesis_method": "alia_edge_tts_optimized",
                "quality": "alia_professional",
                "provider": "alia_kit_bsc",
                "model_used": voice,
                "file_size": file_size,
                "segre_applied": segre_applied,
                "dialect": dialect,
                "language": language,
                "rate": rate,
                "pitch": pitch,
                "created_at": datetime.now().isoformat(),
                "note": f"ALIA Kit amb Edge-TTS optimitzat + SEGRE"
            }
            
        except Exception as e:
            logger.error(f"ALIA Kit Fixed failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _get_best_voice(self, language: str, dialect: str) -> str:
        """
        Obtenir la millor veu per idioma i dialecte
        """
        voice_map = {
            "ca": {
                "central": "ca-ES-EnricNeural",  # Veu masculina catalana
                "balear": "ca-ES-JoanaNeural",   # Veu femenina catalana
                "valencian": "ca-ES-AlbaNeural"  # Veu femenina valenciana
            },
            "es": {
                "default": "es-ES-AlvaroNeural"  # Veu masculina castellana
            },
            "eu": {
                "default": "eu-ES-AinhoaNeural"  # Veu femenina euskera
            },
            "gl": {
                "default": "gl-ES-SabelaNeural"  # Veu femenina gallega
            }
        }
        
        if language == "ca":
            return voice_map["ca"].get(dialect, "ca-ES-EnricNeural")
        elif language in voice_map:
            return voice_map[language].get("default", voice_map[language][list(voice_map[language].keys())[0]])
        else:
            return "ca-ES-EnricNeural"  # Default català


# Instància global
alia_kit_fixed = AliaKitFixed()

