"""
Integració SIP Trunk - VeuPlus per sistemes telefònics
Suport per Asterisk, FreeSWITCH, i altres PBX
"""

import logging
import asyncio
import tempfile
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path

logger = logging.getLogger(__name__)

class SIPTrunkIntegration:
    """
    Integració SIP Trunk per VeuPlus
    """
    
    def __init__(self):
        self.name = "SIP Trunk Integration"
        self.audio_cache_dir = Path("backend/sip_audio_cache")
        self.audio_cache_dir.mkdir(exist_ok=True)
        logger.info("✅ SIP Trunk Integration initialized")
    
    async def handle_incoming_call(
        self,
        caller_id: str,
        called_number: str,
        language: str = "ca",
        voice_system: str = "catalan",
        greeting_text: str = None
    ) -> Dict[str, Any]:
        """
        Gestionar trucada entrant
        """
        try:
            logger.info(f"📞 Trucada entrant: {caller_id} -> {called_number}")
            
            # Text de benvinguda personalitzat
            if not greeting_text:
                if language == "ca":
                    greeting_text = f"Hola, gràcies per trucar. Com puc ajudar-te avui?"
                elif language == "es":
                    greeting_text = f"Hola, gracias por llamar. ¿Cómo puedo ayudarte hoy?"
                else:
                    greeting_text = f"Hello, thank you for calling. How can I help you today?"
            
            # Generar àudio de benvinguda
            greeting_audio = await self._generate_greeting_audio(
                text=greeting_text,
                language=language,
                voice_system=voice_system
            )
            
            if not greeting_audio.get("success"):
                return {
                    "success": False,
                    "error": "Failed to generate greeting audio"
                }
            
            # Guardar àudio per SIP
            audio_path = await self._save_audio_for_sip(
                audio_base64=greeting_audio["audio_base64"],
                call_id=f"{caller_id}_{called_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            return {
                "success": True,
                "call_id": f"{caller_id}_{called_number}",
                "greeting_audio_path": audio_path,
                "language": language,
                "voice_system": voice_system,
                "greeting_text": greeting_text,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"SIP call handling failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_voice_input(
        self,
        call_id: str,
        audio_file_path: str,
        language: str = "ca",
        voice_system: str = "catalan"
    ) -> Dict[str, Any]:
        """
        Processar entrada de veu (ASR + LLM + TTS)
        """
        try:
            logger.info(f"🎤 Processant entrada de veu: {call_id}")
            
            # 1. Transcriure àudio (ASR)
            transcription = await self._transcribe_audio(audio_file_path, language)
            
            if not transcription.get("success"):
                return {
                    "success": False,
                    "error": "Speech recognition failed"
                }
            
            user_text = transcription["text"]
            logger.info(f"👤 Usuari va dir: {user_text}")
            
            # 2. Processar amb LLM (Agent intel·ligent)
            llm_response = await self._process_with_llm(
                user_input=user_text,
                call_id=call_id,
                language=language
            )
            
            if not llm_response.get("success"):
                return {
                    "success": False,
                    "error": "LLM processing failed"
                }
            
            agent_text = llm_response["response"]
            logger.info(f"🤖 Agent respon: {agent_text}")
            
            # 3. Generar àudio de resposta (TTS)
            response_audio = await self._generate_response_audio(
                text=agent_text,
                language=language,
                voice_system=voice_system
            )
            
            if not response_audio.get("success"):
                return {
                    "success": False,
                    "error": "TTS generation failed"
                }
            
            # 4. Guardar àudio per SIP
            audio_path = await self._save_audio_for_sip(
                audio_base64=response_audio["audio_base64"],
                call_id=call_id
            )
            
            return {
                "success": True,
                "call_id": call_id,
                "user_input": user_text,
                "agent_response": agent_text,
                "response_audio_path": audio_path,
                "language": language,
                "voice_system": voice_system,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Voice processing failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _generate_greeting_audio(
        self,
        text: str,
        language: str,
        voice_system: str
    ) -> Dict[str, Any]:
        """Generar àudio de benvinguda"""
        try:
            from voicebots_integration import voicebot_integration
            
            # Seleccionar veu segons idioma
            voice_id = self._get_voice_for_language(language, voice_system)
            
            result = await voicebot_integration.generate_voice_response(
                text=text,
                voice_id=voice_id,
                system=voice_system,
                language=language
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Greeting audio generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _transcribe_audio(self, audio_file_path: str, language: str) -> Dict[str, Any]:
        """Transcriure àudio amb ASR"""
        try:
            # Usar Whisper o ALIA ASR
            try:
                from alia_asr_advanced import alia_asr_advanced
                
                with open(audio_file_path, "rb") as f:
                    audio_data = f.read()
                
                result = await alia_asr_advanced.transcribe_audio(
                    audio_file=audio_data,
                    language=language,
                    model_preference="auto"
                )
                
                return result
                
            except ImportError:
                # Fallback a Whisper
                import whisper
                
                model = whisper.load_model("base")
                result = model.transcribe(audio_file_path, language=language)
                
                return {
                    "success": True,
                    "text": result["text"],
                    "language": result["language"],
                    "confidence": 0.9
                }
                
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _process_with_llm(
        self,
        user_input: str,
        call_id: str,
        language: str
    ) -> Dict[str, Any]:
        """Processar amb LLM (Agent intel·ligent)"""
        try:
            from llm_service import LLMService
            
            # Crear prompt contextual
            context_prompt = self._create_context_prompt(user_input, language)
            
            # Generar resposta amb LLM
            llm_service = LLMService()
            
            result = await llm_service.generate_response(
                prompt=context_prompt,
                provider="openai",  # o "alia", "ollama", etc.
                model="gpt-3.5-turbo",
                max_tokens=200,
                temperature=0.7
            )
            
            if result.get("success"):
                return {
                    "success": True,
                    "response": result["response"],
                    "provider": result.get("provider", "openai"),
                    "model": result.get("model", "gpt-3.5-turbo")
                }
            else:
                return {"success": False, "error": result.get("error")}
                
        except Exception as e:
            logger.error(f"LLM processing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _generate_response_audio(
        self,
        text: str,
        language: str,
        voice_system: str
    ) -> Dict[str, Any]:
        """Generar àudio de resposta"""
        try:
            from voicebots_integration import voicebot_integration
            
            voice_id = self._get_voice_for_language(language, voice_system)
            
            result = await voicebot_integration.generate_voice_response(
                text=text,
                voice_id=voice_id,
                system=voice_system,
                language=language
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Response audio generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_voice_for_language(self, language: str, voice_system: str) -> str:
        """Obtenir veu per idioma"""
        voices = {
            "ca": {
                "catalan": "ca-ES-EnricNeural",
                "edge-tts": "ca-ES-EnricNeural",
                "alia": "ca-ES-AlbaNeural"
            },
            "es": {
                "catalan": "es-ES-AlvaroNeural",
                "edge-tts": "es-ES-AlvaroNeural",
                "alia": "es-ES-AlvaroNeural"
            },
            "en": {
                "catalan": "en-US-AriaNeural",
                "edge-tts": "en-US-AriaNeural",
                "alia": "en-US-AriaNeural"
            },
            "fr": {
                "catalan": "fr-FR-DeniseNeural",
                "edge-tts": "fr-FR-DeniseNeural",
                "alia": "fr-FR-DeniseNeural"
            }
        }
        
        return voices.get(language, {}).get(voice_system, "en-US-AriaNeural")
    
    def _create_context_prompt(self, user_input: str, language: str) -> str:
        """Crear prompt contextual per LLM"""
        if language == "ca":
            return f"""Ets un assistent virtual professional que atén trucades telefòniques. 
Respon de manera amable, professional i útil en català.

Usuari: {user_input}

Resposta (màxim 2 frases, ton professional):"""
        
        elif language == "es":
            return f"""Eres un asistente virtual profesional que atiende llamadas telefónicas.
Responde de manera amable, profesional y útil en español.

Usuario: {user_input}

Respuesta (máximo 2 frases, tono profesional):"""
        
        else:
            return f"""You are a professional virtual assistant handling phone calls.
Respond in a friendly, professional and helpful manner in English.

User: {user_input}

Response (maximum 2 sentences, professional tone):"""
    
    async def _save_audio_for_sip(
        self,
        audio_base64: str,
        call_id: str
    ) -> str:
        """Guardar àudio per SIP (format WAV)"""
        try:
            # Decodificar àudio
            audio_data = base64.b64decode(audio_base64)
            
            # Guardar com WAV (format SIP estàndard)
            audio_path = self.audio_cache_dir / f"{call_id}_response.wav"
            
            with open(audio_path, "wb") as f:
                f.write(audio_data)
            
            logger.info(f"✅ Àudio guardat per SIP: {audio_path}")
            return str(audio_path)
            
        except Exception as e:
            logger.error(f"Audio save failed: {e}")
            return ""
    
    def get_sip_configuration(self) -> Dict[str, Any]:
        """Obtenir configuració SIP"""
        return {
            "sip_server": "veuplus.local",
            "sip_port": 5060,
            "audio_format": "wav",
            "audio_path": str(self.audio_cache_dir),
            "supported_languages": ["ca", "es", "en", "fr"],
            "voice_systems": ["catalan", "edge-tts", "alia"],
            "max_call_duration": 300,  # 5 minuts
            "greeting_timeout": 10,    # 10 segons
            "silence_timeout": 5       # 5 segons
        }


# Instància global
sip_trunk_integration = SIPTrunkIntegration()
