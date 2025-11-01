"""
Integració Voicebots - Sistema per integrar VeuPlus en voicebots
Suport per web, telefònic, mòbil, IoT
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)

class VoicebotIntegration:
    """
    Integració per voicebots amb VeuPlus
    """
    
    def __init__(self):
        self.name = "Voicebot Integration"
        logger.info("✅ Voicebot Integration initialized")
    
    async def generate_voice_response(
        self,
        text: str,
        voice_id: str,
        system: str = "edge-tts",
        language: str = "ca",
        settings: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generar resposta de veu per voicebots
        """
        try:
            logger.info(f"🎤 Voicebot: '{text[:30]}...' amb {voice_id}")
            
            # Seleccionar sistema segons configuració
            if system == "edge-tts":
                return await self._generate_edge_tts(text, voice_id, language, settings)
            elif system == "catalan":
                return await self._generate_catalan(text, voice_id, language, settings)
            elif system == "alia":
                return await self._generate_alia(text, voice_id, language, settings)
            else:
                return await self._generate_edge_tts(text, voice_id, language, settings)
                
        except Exception as e:
            logger.error(f"Voicebot generation failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_edge_tts(
        self,
        text: str,
        voice_id: str,
        language: str,
        settings: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generar amb Sistema 1 (Edge-TTS)"""
        try:
            from api.edge_tts_only import edge_router
            
            # Simular crida interna
            import edge_tts
            import tempfile
            import os
            import base64
            
            communicate = edge_tts.Communicate(text, voice_id)
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            await communicate.save(temp_path)
            
            if not os.path.exists(temp_path):
                return {"success": False, "error": "Audio not generated"}
            
            file_size = os.path.getsize(temp_path)
            if file_size < 1024:
                os.unlink(temp_path)
                return {"success": False, "error": "Audio too small"}
            
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            os.unlink(temp_path)
            audio_base64 = base64.b64encode(audio_data).decode()
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "system": "edge-tts",
                "voice_id": voice_id,
                "file_size": file_size,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_catalan(
        self,
        text: str,
        voice_id: str,
        language: str,
        settings: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generar amb Sistema 2 (Català+SEGRE)"""
        try:
            import edge_tts
            import tempfile
            import os
            import base64
            
            # Aplicar SEGRE si disponible
            phonetic_text = text
            segre_applied = False
            
            try:
                from segre_integration import segre_transcribe
                dialect = settings.get("dialect", "central") if settings else "central"
                phonetic_result = segre_transcribe(text, dialect=dialect)
                if phonetic_result and len(phonetic_result) > 0:
                    phonetic_text = phonetic_result[0]
                    segre_applied = True
            except:
                pass
            
            # Veus catalanes
            catalan_voices = {
                "senyor_catala_1": "ca-ES-EnricNeural",
                "senyor_catala_2": "ca-ES-EnricNeural",
                "dona_catalana": "ca-ES-JoanaNeural",
                "senyor_catala_extended": "ca-ES-EnricNeural"
            }
            
            edge_voice = catalan_voices.get(voice_id, "ca-ES-EnricNeural")
            
            communicate = edge_tts.Communicate(phonetic_text, edge_voice)
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            await communicate.save(temp_path)
            
            if not os.path.exists(temp_path):
                return {"success": False, "error": "Audio not generated"}
            
            file_size = os.path.getsize(temp_path)
            if file_size < 1024:
                os.unlink(temp_path)
                return {"success": False, "error": "Audio too small"}
            
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            os.unlink(temp_path)
            audio_base64 = base64.b64encode(audio_data).decode()
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "system": "catalan",
                "voice_id": edge_voice,
                "segre_applied": segre_applied,
                "file_size": file_size,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _generate_alia(
        self,
        text: str,
        voice_id: str,
        language: str,
        settings: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generar amb Sistema 3 (ALIA Premium)"""
        try:
            import edge_tts
            import tempfile
            import os
            import base64
            
            # Veus premium
            premium_voices = {
                "ca": {
                    "central": "ca-ES-AlbaNeural",
                    "balear": "ca-ES-JoanaNeural",
                    "valencian": "ca-ES-AlbaNeural"
                },
                "es": "es-ES-AlvaroNeural",
                "eu": "eu-ES-AinhoaNeural",
                "gl": "gl-ES-SabelaNeural"
            }
            
            # Seleccionar veu
            if language == "ca":
                dialect = settings.get("dialect", "central") if settings else "central"
                edge_voice = premium_voices["ca"].get(dialect, "ca-ES-AlbaNeural")
            else:
                edge_voice = premium_voices.get(language, "es-ES-AlvaroNeural")
            
            # Aplicar SEGRE si català
            phonetic_text = text
            segre_applied = False
            
            if language == "ca":
                try:
                    from segre_integration import segre_transcribe
                    dialect = settings.get("dialect", "central") if settings else "central"
                    phonetic_result = segre_transcribe(text, dialect=dialect)
                    if phonetic_result and len(phonetic_result) > 0:
                        phonetic_text = phonetic_result[0]
                        segre_applied = True
                except:
                    pass
            
            # Configuració avançada
            speed = settings.get("speed", 1.0) if settings else 1.0
            pitch = settings.get("pitch", 1.0) if settings else 1.0
            expressiveness = settings.get("expressiveness", 1.0) if settings else 1.0
            
            rate_percent = int((speed - 1.0) * 100)
            rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
            
            pitch_hz = int((pitch - 1.0) * 100)
            pitch_str = f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"
            
            volume_percent = int((expressiveness - 1.0) * 20)
            volume = f"+{volume_percent}%" if volume_percent >= 0 else f"{volume_percent}%"
            
            communicate = edge_tts.Communicate(
                phonetic_text,
                edge_voice,
                rate=rate,
                pitch=pitch_str,
                volume=volume
            )
            
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name
            
            await communicate.save(temp_path)
            
            if not os.path.exists(temp_path):
                return {"success": False, "error": "Audio not generated"}
            
            file_size = os.path.getsize(temp_path)
            if file_size < 1024:
                os.unlink(temp_path)
                return {"success": False, "error": "Audio too small"}
            
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            os.unlink(temp_path)
            audio_base64 = base64.b64encode(audio_data).decode()
            
            return {
                "success": True,
                "audio_base64": audio_base64,
                "system": "alia",
                "voice_id": edge_voice,
                "segre_applied": segre_applied,
                "file_size": file_size,
                "settings": {
                    "speed": speed,
                    "pitch": pitch,
                    "expressiveness": expressiveness
                },
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_available_voices(self, system: str = "all") -> Dict[str, List[Dict[str, Any]]]:
        """
        Obtenir veus disponibles per sistema
        """
        voices = {
            "edge-tts": [
                {"id": "en-US-AriaNeural", "name": "Aria (English)", "language": "en", "gender": "Female"},
                {"id": "es-ES-AlvaroNeural", "name": "Álvaro (Español)", "language": "es", "gender": "Male"},
                {"id": "fr-FR-DeniseNeural", "name": "Denise (Français)", "language": "fr", "gender": "Female"},
                {"id": "de-DE-KatjaNeural", "name": "Katja (Deutsch)", "language": "de", "gender": "Female"},
                {"id": "ca-ES-EnricNeural", "name": "Enric (Català)", "language": "ca", "gender": "Male"},
                {"id": "ca-ES-JoanaNeural", "name": "Joana (Català)", "language": "ca", "gender": "Female"},
            ],
            "catalan": [
                {"id": "senyor_catala_1", "name": "Senyor Català 1", "language": "ca", "gender": "Male"},
                {"id": "senyor_catala_2", "name": "Senyor Català 2", "language": "ca", "gender": "Male"},
                {"id": "dona_catalana", "name": "Dona Catalana", "language": "ca", "gender": "Female"},
                {"id": "senyor_catala_extended", "name": "Senyor Català Extended", "language": "ca", "gender": "Male"},
            ],
            "alia": [
                {"id": "ca-ES-AlbaNeural", "name": "Alba Premium (Català)", "language": "ca", "gender": "Female"},
                {"id": "es-ES-AlvaroNeural", "name": "Álvaro Premium (Español)", "language": "es", "gender": "Male"},
                {"id": "eu-ES-AinhoaNeural", "name": "Ainhoa Premium (Euskera)", "language": "eu", "gender": "Female"},
                {"id": "gl-ES-SabelaNeural", "name": "Sabela Premium (Galego)", "language": "gl", "gender": "Female"},
            ]
        }
        
        if system == "all":
            return voices
        else:
            return {system: voices.get(system, [])}


# Instància global
voicebot_integration = VoicebotIntegration()

