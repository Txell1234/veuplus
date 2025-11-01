"""
API per Integració Externa - Voicebots
Endpoints per webs, telefons, SIP, IoT
"""

from fastapi import APIRouter, HTTPException, Request, File, UploadFile
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger("veuplus.voicebots_external")

router = APIRouter(prefix="/api/voicebots", tags=["Voicebots External"])

# Import integració voicebots
try:
    from voicebots_integration import voicebot_integration
    VOICEBOT_AVAILABLE = True
except ImportError as e:
    logger.error(f"Voicebot integration not available: {e}")
    VOICEBOT_AVAILABLE = False


class VoicebotRequest(BaseModel):
    text: str
    voice_id: str
    system: str = "edge-tts"  # edge-tts, catalan, alia
    language: str = "ca"
    settings: Optional[Dict[str, Any]] = None


class VoicebotWebhookRequest(BaseModel):
    text: str
    voice_id: str
    system: str = "edge-tts"
    language: str = "ca"
    callback_url: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


@router.post("/synthesize")
async def voicebot_synthesize(request: VoicebotRequest):
    """
    Síntesi per voicebots externs
    Ús: Webs, apps, sistemes externs
    """
    if not VOICEBOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voicebot integration not available")
    
    try:
        logger.info(f"🎤 Voicebot External: '{request.text[:30]}...' amb {request.voice_id}")
        
        result = await voicebot_integration.generate_voice_response(
            text=request.text,
            voice_id=request.voice_id,
            system=request.system,
            language=request.language,
            settings=request.settings
        )
        
        if result.get("success"):
            logger.info(f"✅ Voicebot synthesis successful")
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voicebot synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/webhook")
async def voicebot_webhook(request: VoicebotWebhookRequest):
    """
    Webhook per sistemes externs
    Ús: Call centers, SIP, integracions automàtiques
    """
    if not VOICEBOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voicebot integration not available")
    
    try:
        logger.info(f"🔗 Voicebot Webhook: '{request.text[:30]}...'")
        
        result = await voicebot_integration.generate_voice_response(
            text=request.text,
            voice_id=request.voice_id,
            system=request.system,
            language=request.language,
            settings=request.settings
        )
        
        # Si hi ha callback_url, enviar resultat
        if request.callback_url and result.get("success"):
            try:
                import requests
                requests.post(request.callback_url, json=result, timeout=10)
                logger.info(f"✅ Callback sent to {request.callback_url}")
            except Exception as callback_error:
                logger.warning(f"Callback failed: {callback_error}")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voicebot webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def get_voicebot_voices(system: str = "all"):
    """
    Obtenir TOTES les veus disponibles per voicebots
    """
    try:
        all_voices = []
        
        # Sistema 1: Edge-TTS
        if system in ["all", "edge-tts"]:
            try:
                import edge_tts
                edge_voices = await edge_tts.list_voices()
                
                for voice in edge_voices:
                    all_voices.append({
                        "id": voice.get("ShortName", ""),
                        "name": voice.get("DisplayName", voice.get("ShortName", "")),
                        "gender": voice.get("Gender", "Unknown"),
                        "language": voice.get("Locale", "").split("-")[0] if voice.get("Locale") else "unknown",
                        "locale": voice.get("Locale", ""),
                        "system": "edge-tts",
                        "system_name": "Edge-TTS Standard",
                        "description": f"{voice.get('DisplayName', '')} - {voice.get('Locale', '')}",
                        "quality": "neural_standard"
                    })
            except Exception as e:
                logger.warning(f"Error carregant veus Edge-TTS: {e}")
        
        # Sistema 2: Català Hiperrealista
        if system in ["all", "catalan"]:
            catalan_voices = [
                {
                    "id": "senyor_catala_1",
                    "name": "Senyor Catala Hiperrealista 1",
                    "gender": "male",
                    "language": "ca",
                    "locale": "ca-ES",
                    "system": "catalan",
                    "system_name": "Català Hiperrealista",
                    "description": "Voz masculina catalana natural, acento Barcelona",
                    "quality": "hiperrealistic"
                },
                {
                    "id": "dona_catalana",
                    "name": "Dona Catalana Hiperrealista",
                    "gender": "female",
                    "language": "ca",
                    "locale": "ca-ES",
                    "system": "catalan",
                    "system_name": "Català Hiperrealista",
                    "description": "Voz femenina catalana natural, acento Barcelona",
                    "quality": "hiperrealistic"
                }
            ]
            all_voices.extend(catalan_voices)
        
        # Sistema 3: ALIA BSC Premium
        if system in ["all", "alia"]:
            alia_voices = [
                {
                    "id": "ca-ES-AlbaNeural",
                    "name": "Alba Premium (Català)",
                    "gender": "female",
                    "language": "ca",
                    "locale": "ca-ES",
                    "system": "alia",
                    "system_name": "ALIA BSC Premium",
                    "description": "Voz femenina catalana premium",
                    "quality": "premium"
                },
                {
                    "id": "es-ES-AlvaroNeural",
                    "name": "Álvaro Premium (Español)",
                    "gender": "male",
                    "language": "es",
                    "locale": "es-ES",
                    "system": "alia",
                    "system_name": "ALIA BSC Premium",
                    "description": "Voz masculina española premium",
                    "quality": "premium"
                }
            ]
            all_voices.extend(alia_voices)
        
        return {
            "success": True,
            "voices": all_voices,
            "total": len(all_voices),
            "system": system,
            "systems_available": {
                "edge-tts": len([v for v in all_voices if v["system"] == "edge-tts"]),
                "catalan": len([v for v in all_voices if v["system"] == "catalan"]),
                "alia": len([v for v in all_voices if v["system"] == "alia"])
            },
            "note": f"Totes les {len(all_voices)} veus disponibles per voicebots"
        }
    except Exception as e:
        logger.error(f"Error getting voicebot voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/train")
async def train_voice_voicebot(
    voice_name: str,
    language: str = "ca",
    quality_level: str = "senyor_catala_extended",
    audio_files: List[UploadFile] = File(...)
):
    """
    Entrenar nova veu per voicebots
    """
    if not VOICEBOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voicebot integration not available")
    
    try:
        logger.info(f"🎓 Entrenant veu per voicebot: {voice_name}")
        
        # Llegir fitxers d'àudio
        audio_data_list = []
        for audio_file in audio_files:
            audio_data = await audio_file.read()
            audio_data_list.append(audio_data)
        
        # Entrenar veu
        from voice_training_advanced import voice_training_advanced
        
        result = await voice_training_advanced.train_new_voice(
            voice_name=voice_name,
            audio_files=audio_data_list,
            language=language,
            quality_level=quality_level
        )
        
        if result.get("success"):
            logger.info(f"✅ Veu entrenada per voicebot: {voice_name}")
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Voice training error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trained")
async def get_trained_voices():
    """
    Llistar veus entrenades per voicebots
    """
    if not VOICEBOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voicebot integration not available")
    
    try:
        from voice_training_advanced import voice_training_advanced
        trained_voices = voice_training_advanced.list_trained_voices()
        
        return {
            "success": True,
            "trained_voices": trained_voices,
            "count": len(trained_voices)
        }
    except Exception as e:
        logger.error(f"Error getting trained voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/synthesize-trained")
async def synthesize_trained_voice(request: VoicebotRequest):
    """
    Sintetitzar amb veu entrenada
    """
    if not VOICEBOT_AVAILABLE:
        raise HTTPException(status_code=503, detail="Voicebot integration not available")
    
    try:
        from voice_training_advanced import voice_training_advanced
        
        result = await voice_training_advanced.synthesize_trained_voice(
            text=request.text,
            voice_id=request.voice_id,
            language=request.language,
            settings=request.settings
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("error"))
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trained voice synthesis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]




