#!/usr/bin/env python3
"""
API ESPECÍFICA PARA VOCES EDGE-TTS ESTÁNDAR
Separado completamente del sistema catalán hiperrealista
"""
import logging
import tempfile
import base64
import asyncio
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger("veuplus.edge_tts")

# Router específico para voces Edge-TTS estándar
edge_router = APIRouter(prefix="/api/edge-tts", tags=["Edge-TTS Standard Voices"])

class EdgeTTSEngine:
    """Engine específico para Edge-TTS estándar"""
    
    async def initialize(self):
        """Inicializar Edge-TTS"""
        try:
            import edge_tts
            self.edge_tts = edge_tts
            return True
        except ImportError:
            raise Exception("Edge-TTS not available")
    
    async def synthesize_speech(self, text: str, voice_id: str, language: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesis using Edge-TTS"""
        try:
            if not hasattr(self, 'edge_tts'):
                await self.initialize()

            raw_rate = settings.get("speed", 1.0)
            try:
                rate_percent = int((float(raw_rate) - 1.0) * 100)
            except Exception:
                rate_percent = 0

            logger.info("[Edge-TTS] Generating voice '%s' at %+d%% rate", voice_id, rate_percent)

            import ssl
            import certifi
            ssl_context = ssl.create_default_context(cafile=certifi.where())
            ssl._create_default_https_context = lambda: ssl_context

            rate_str = f"{rate_percent:+.0f}%"
            communicate = self.edge_tts.Communicate(text, voice_id, rate=rate_str)

            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
                temp_path = temp_file.name

            await communicate.save(temp_path)

            with open(temp_path, "rb") as f:
                audio_data = f.read()

            audio_base64 = base64.b64encode(audio_data).decode()
            Path(temp_path).unlink(missing_ok=True)

            return {
                "success": True,
                "audio_base64": audio_base64,
                "text": text,
                "voice_id": voice_id,
                "language": language,
                "size": len(audio_data),
                "mime_type": "audio/mpeg"
            }

        except Exception as e:
            logger.error("Edge-TTS synthesis failed: %s", e)
            return {"success": False, "error": str(e)}



@edge_router.post("/synthesize")
async def synthesize_edge_voice(request: Request):
    """
    📡 SÍNTESIS EXCLUSIVA PARA VOCES EDGE-TTS ESTÁNDAR
    
    Usa únicamente:
    - Microsoft Edge-TTS neural
    - Voces estándar multiidioma
    - Síntesis comercial neural
    
    NO usa sistema catalán hiperrealista
    """
    try:
        data = await request.json()
        text = data.get("text", "")
        voice_id = data.get("voice_id", "")
        language = data.get("language", "en")
        voice_settings = data.get("voice_settings", {})
        
        # Permitir TODAS las voces Edge-TTS, incluidas catalanas
        logger.info(f"📡 EDGE-TTS: '{text[:30]}...' con voz '{voice_id}'")
        
        # USAR ÚNICAMENTE EDGE-TTS
        edge_engine = EdgeTTSEngine()
        result = await edge_engine.synthesize_speech(text, voice_id, language, voice_settings)
        
        if result.get("success", False):
            logger.info(f"✅ SÍNTESIS EDGE-TTS EXITOSA con voz: {voice_id}")
            return result
        else:
            logger.error(f"❌ Síntesis Edge-TTS falló: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=f"Error en Edge-TTS: {result.get('error')}"
            )
            
    except Exception as e:
        logger.error(f"Error en endpoint Edge-TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@edge_router.get("/voices")
async def get_edge_voices():
    """Obtener voces Edge-TTS estándar disponibles"""
    
    try:
        import edge_tts
        import ssl
        import os
        
        # Deshabilitar verificació SSL per evitar problemes
        os.environ['PYTHONHTTPSVERIFY'] = '0'
        ssl._create_default_https_context = ssl._create_unverified_context
        
        try:
            all_voices = await edge_tts.list_voices()
            logger.info(f"✅ Obtingudes {len(all_voices)} veus directament d'Edge-TTS")
        except Exception as ssl_error:
            logger.warning(f"Error SSL amb Edge-TTS: {ssl_error}")
            # Usar veus per defecte si hi ha problemes SSL
            all_voices = [
                {
                    "ShortName": "es-ES-ElviraNeural",
                    "DisplayName": "Elvira (Español)",
                    "Gender": "Female",
                    "Locale": "es-ES"
                },
                {
                    "ShortName": "es-ES-AlvaroNeural", 
                    "DisplayName": "Alvaro (Español)",
                    "Gender": "Male",
                    "Locale": "es-ES"
                },
                {
                    "ShortName": "en-US-AriaNeural",
                    "DisplayName": "Aria (English)",
                    "Gender": "Female", 
                    "Locale": "en-US"
                },
                {
                    "ShortName": "en-US-GuyNeural",
                    "DisplayName": "Guy (English)",
                    "Gender": "Male",
                    "Locale": "en-US"
                },
                {
                    "ShortName": "ca-ES-AlbaNeural",
                    "DisplayName": "Alba (Català)",
                    "Gender": "Female",
                    "Locale": "ca-ES"
                },
                {
                    "ShortName": "ca-ES-JoanaNeural",
                    "DisplayName": "Joana (Català)", 
                    "Gender": "Female",
                    "Locale": "ca-ES"
                }
            ]
            logger.info(f"✅ Usant {len(all_voices)} veus per defecte Edge-TTS")
        
        # Carregar TOTES les veus disponibles (sense filtrar)
        all_available_voices = all_voices
        
        # Organizar por idioma
        voices_by_language = {}
        for voice in all_available_voices:
            locale = voice['Locale']
            if locale not in voices_by_language:
                voices_by_language[locale] = []

            # Marcar explícitament si és veu catalana
            try:
                is_catalan = str(voice.get('Locale', '')).lower().startswith('ca')
            except Exception:
                is_catalan = False

            voices_by_language[locale].append({
                "id": voice['ShortName'],
                "name": voice['DisplayName'] or voice['ShortName'],
                "gender": voice['Gender'],
                "language": voice['Locale'].split('-')[0],  # Afegir camp language
                "locale": voice['Locale'],
                "is_catalan": is_catalan,
                "description": f"{voice['DisplayName'] or voice['ShortName']} - {voice['Locale']}",
                "channel": "edge_tts_exclusivo",
                "provider": "microsoft_edge",
                "quality": "neural_estándar_comercial"
            })
        
        # Crear llista plana per al frontend
        flat_voices = []
        for locale_voices in voices_by_language.values():
            flat_voices.extend(locale_voices)
        
        return {
            "success": True,
            "voices": flat_voices,
            "edge_voices": flat_voices,
            "total": len(flat_voices),
            "total_edge": len(flat_voices),
            "voice_type": "edge_standard",
            "system": "Sistema 1 - Edge-TTS Standard",
            "description": f"Totes les {len(flat_voices)} voces Edge-TTS disponibles"
        }
        
    except Exception as e:
        logger.error(f"Error getting Edge-TTS voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@edge_router.get("/health")
async def edge_health():
    """Health check específico para Edge-TTS"""
    
    try:
        import edge_tts
        edge_available = True
        
        # Verificar voces disponibles
        all_voices = await edge_tts.list_voices()
        edge_voices_count = len(all_voices)
        
        return {
            "status": "healthy",
            "edge_tts_available": edge_available,
            "voices_available": edge_voices_count,
            "channel": "edge_tts_exclusivo",
            "separated_from_catalan": True,
            "provider": "microsoft_edge_tts",
            "description": "Sistema Edge-TTS estándar completamente separado"
        }
        
    except ImportError:
        return {
            "status": "unhealthy",
            "error": "Edge-TTS no disponible",
            "channel": "edge_tts_exclusivo"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "channel": "edge_tts_exclusivo"
        }







