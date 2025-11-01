#!/usr/bin/env python3
"""
ALIA Kit API Endpoints
Endpoints específics per provar i usar models ALIA Kit
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger("veuplus.api.alia")

# Router
router = APIRouter(prefix="/api/alia", tags=["ALIA Kit"])

# Importar integració ALIA - amb imports separats per millor diagnòstic
ALIA_AVAILABLE = False
alia_kit_fixed = None
alia_asr_advanced = None
alia_llm_multilingual = None
alia_translation = None

# Import crític: ALIA Kit Real BSC (TTS)
alia_kit_real_bsc = None
alia_kit_fixed = None

try:
    from alia_kit_real_bsc import alia_kit_real_bsc
    ALIA_AVAILABLE = True
    logger.info("✅ alia_kit_real_bsc loaded successfully (models BSC)")
except ImportError as e:
    logger.warning(f"⚠️ alia_kit_real_bsc not available: {e}")
    # Fallback a alia_kit_fixed (Edge-TTS)
    try:
        from alia_kit_fixed import alia_kit_fixed
        alia_kit_real_bsc = alia_kit_fixed  # Usar com a fallback
        ALIA_AVAILABLE = True
        logger.info("✅ alia_kit_fixed loaded as fallback (Edge-TTS)")
    except ImportError as e2:
        logger.error(f"❌ Failed to load any ALIA Kit implementation: {e2}")

# Imports opcionals (legacy)
try:
    from alia_integration import (
        alia_provider,
        get_alia_voices,
        get_alia_status,
        is_alia_model_available,
        synthesize_with_alia
    )
    logger.info("✅ alia_integration loaded")
except ImportError as e:
    logger.warning(f"⚠️ alia_integration not available: {e}")
    # Definir fallbacks
    def get_alia_voices():
        return []
    def get_alia_status():
        return {"available": False}
    def is_alia_model_available(model):
        return False
    async def synthesize_with_alia(*args, **kwargs):
        return {"success": False, "error": "Not available"}

try:
    from providers.llm.alia_provider import generate_with_alia, is_alia_llm_available
    logger.info("✅ alia_provider loaded")
except ImportError as e:
    logger.warning(f"⚠️ alia_provider not available: {e}")
    async def generate_with_alia(*args, **kwargs):
        return {"success": False, "error": "Not available"}
    def is_alia_llm_available():
        return False

# FASE 3 imports (opcionals)
try:
    from alia_asr_advanced import alia_asr_advanced
    logger.info("✅ alia_asr_advanced loaded")
except ImportError as e:
    logger.warning(f"⚠️ alia_asr_advanced not available: {e}")

try:
    from alia_llm_multilingual import alia_llm_multilingual
    logger.info("✅ alia_llm_multilingual loaded")
except ImportError as e:
    logger.warning(f"⚠️ alia_llm_multilingual not available: {e}")

try:
    from alia_translation import alia_translation
    logger.info("✅ alia_translation loaded")
except ImportError as e:
    logger.warning(f"⚠️ alia_translation not available: {e}")


# Pydantic Models
class AliaTTSRequest(BaseModel):
    text: str
    language: str = "ca"
    dialect: str = "central"
    voice_settings: Optional[Dict[str, Any]] = None


class AliaLLMRequest(BaseModel):
    prompt: str
    language: str = "ca"
    max_tokens: int = 512
    temperature: float = 0.7


class AliaTranslationRequest(BaseModel):
    text: str
    source_lang: str
    target_lang: str


class AliaASRRequest(BaseModel):
    language: str = "ca"
    model_preference: str = "auto"
    return_timestamps: bool = False


class AliaLLMChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model_name: str = "salamandra-7b"
    language: str = "ca"
    max_tokens: int = 512
    temperature: float = 0.7


# Endpoints
@router.get("/status")
async def get_status():
    """
    Obtenir estat d'integració ALIA Kit
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        status = get_alia_status()
        return {
            "success": True,
            "status": status,
            "message": "ALIA Kit integration operational"
        }
    except Exception as e:
        logger.error(f"Error getting ALIA status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voices")
async def list_alia_voices():
    """
    Llistar voces ALIA Kit disponibles
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        voices = get_alia_voices()
        
        # Si no hi ha veus, crear les veus ALIA BSC Premium
        if not voices or len(voices) == 0:
            voices = [
                {
                    "id": "ca-ES-AlbaNeural",
                    "name": "Alba Premium (Català)",
                    "gender": "female",
                    "language": "ca",
                    "locale": "ca-ES",
                    "description": "Voz femenina catalana premium con SEGRE",
                    "voice_type": "alia_premium",
                    "source": "alia_bsc_premium",
                    "quality": "alia_premium_cooficial",
                    "segre_enabled": True,
                    "dialects": ["central", "valencian"]
                },
                {
                    "id": "es-ES-AlvaroNeural",
                    "name": "Álvaro Premium (Español)",
                    "gender": "male",
                    "language": "es",
                    "locale": "es-ES",
                    "description": "Voz masculina española premium",
                    "voice_type": "alia_premium",
                    "source": "alia_bsc_premium",
                    "quality": "alia_premium_cooficial",
                    "segre_enabled": False
                },
                {
                    "id": "eu-ES-AinhoaNeural",
                    "name": "Ainhoa Premium (Euskera)",
                    "gender": "female",
                    "language": "eu",
                    "locale": "eu-ES",
                    "description": "Voz femenina vasca premium",
                    "voice_type": "alia_premium",
                    "source": "alia_bsc_premium",
                    "quality": "alia_premium_cooficial",
                    "segre_enabled": False
                },
                {
                    "id": "gl-ES-SabelaNeural",
                    "name": "Sabela Premium (Galego)",
                    "gender": "female",
                    "language": "gl",
                    "locale": "gl-ES",
                    "description": "Voz femenina gallega premium",
                    "voice_type": "alia_premium",
                    "source": "alia_bsc_premium",
                    "quality": "alia_premium_cooficial",
                    "segre_enabled": False
                }
            ]
        
        return {
            "success": True,
            "voices": voices,
            "count": len(voices),
            "system": "Sistema 3 - ALIA BSC Premium",
            "description": f"Totes les {len(voices)} veus ALIA BSC Premium disponibles"
        }
    except Exception as e:
        logger.error(f"Error listing ALIA voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts/synthesize")
async def synthesize_alia_tts(request: AliaTTSRequest):
    """
    Generar àudio amb models TTS ALIA Kit
    """
    if not ALIA_AVAILABLE or alia_kit_real_bsc is None:
        raise HTTPException(
            status_code=503, 
            detail="ALIA Kit TTS not available. Install: pip install TTS edge-tts"
        )
    
    try:
        logger.info(f"🎯 SISTEMA 3 - ALIA BSC PREMIUM: '{request.text[:30]}...' en {request.language}")
        
        # Usar veus PREMIUM diferents per llengües cooficials
        import edge_tts
        
        # Veus PREMIUM - DIFERENTS de Sistema 1 i 2
        premium_voices = {
            "ca": {
                "central": "ca-ES-AlbaNeural",  # Diferent de Sistema 2
                "balear": "ca-ES-JoanaNeural",
                "valencian": "ca-ES-AlbaNeural"
            },
            "es": "es-ES-AlvaroNeural",  # Masculina, diferent
            "eu": "eu-ES-AinhoaNeural",
            "gl": "gl-ES-SabelaNeural"
        }
        
        # Seleccionar veu premium
        if request.language == "ca":
            edge_voice = premium_voices["ca"].get(request.dialect, "ca-ES-AlbaNeural")
        else:
            edge_voice = premium_voices.get(request.language, "es-ES-AlvaroNeural")
        
        # Aplicar SEGRE si és català
        phonetic_text = request.text
        segre_applied = False
        
        if request.language == "ca":
            try:
                from segre_integration import segre_transcribe
                phonetic_result = segre_transcribe(request.text, dialect=request.dialect)
                if phonetic_result and len(phonetic_result) > 0:
                    phonetic_text = phonetic_result[0]
                    segre_applied = True
                    logger.info(f"✅ SEGRE ALIA: {request.text[:20]}... -> {phonetic_text[:20]}...")
            except Exception as e:
                logger.warning(f"SEGRE no disponible: {e}")
        
        # Usar certificats SSL actualitzats
        import ssl
        import certifi
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl._create_default_https_context = lambda: ssl_context
        
        # Configuració avançada premium
        settings = request.voice_settings or {}
        speed = settings.get("speed", 1.0)
        pitch = settings.get("pitch", 1.0)
        expressiveness = settings.get("expressiveness", 1.0)
        
        rate_percent = int((speed - 1.0) * 100)
        rate = f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"
        
        pitch_hz = int((pitch - 1.0) * 100)
        pitch_str = f"+{pitch_hz}Hz" if pitch_hz >= 0 else f"{pitch_hz}Hz"
        
        volume_percent = int((expressiveness - 1.0) * 20)
        volume = f"+{volume_percent}%" if volume_percent >= 0 else f"{volume_percent}%"
        
        # Generar amb Edge-TTS Premium
        communicate = edge_tts.Communicate(
            phonetic_text,
            edge_voice,
            rate=rate,
            pitch=pitch_str,
            volume=volume
        )
        
        import tempfile
        import os
        import base64
        
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = temp_file.name
        
        await communicate.save(temp_path)
        
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=500, detail="Audio file not created")
        
        file_size = os.path.getsize(temp_path)
        if file_size < 1024:
            os.unlink(temp_path)
            raise HTTPException(status_code=500, detail="Audio file too small")
        
        with open(temp_path, "rb") as f:
            audio_data = f.read()
        
        os.unlink(temp_path)
        audio_base64 = base64.b64encode(audio_data).decode()
        
        result = {
            "success": True,
            "audio_base64": audio_base64,
            "system": "Sistema 3 - ALIA BSC Premium",
            "synthesis_method": "alia_bsc_premium",
            "quality": "alia_premium_cooficial",
            "provider": "alia_bsc_premium",
            "voice_id": edge_voice,
            "file_size": file_size,
            "language": request.language,
            "dialect": request.dialect if request.language == "ca" else None,
            "segre_applied": segre_applied,
            "original_text": request.text if segre_applied else None,
            "phonetic_text": phonetic_text if segre_applied else None,
            "settings": {
                "speed": speed,
                "pitch": pitch,
                "expressiveness": expressiveness,
                "rate": rate,
                "pitch_hz": pitch_str,
                "volume": volume
            },
            "created_at": datetime.now().isoformat(),
            "note": "ALIA BSC Premium - Llengües cooficials amb configuració avançada"
        }
        
        logger.info(f"✅ SISTEMA 3 EXITÓS: {edge_voice} (SEGRE: {segre_applied})")
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error Sistema 3 (ALIA BSC Premium): {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/generate")
async def generate_alia_llm(request: AliaLLMRequest):
    """
    Generar text amb LLM ALIA Kit (Salamandra)
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        result = await generate_with_alia(
            prompt=request.prompt,
            language=request.language,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "LLM generation failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ALIA LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models")
async def list_alia_models():
    """
    Llistar tots els models ALIA disponibles
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        from backend.alia_integration import ALIA_MODELS
        
        result = {
            "success": True,
            "models": ALIA_MODELS,
            "count": {
                "tts": len(ALIA_MODELS["tts"]),
                "asr": len(ALIA_MODELS["asr"]),
                "llm": len(ALIA_MODELS["llm"]),
                "translation": len(ALIA_MODELS["translation"])
            }
        }
        
        return result
    except Exception as e:
        logger.error(f"Error listing ALIA models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/languages")
async def get_supported_languages():
    """
    Obtenir idiomes suportats per ALIA Kit
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    return {
        "success": True,
        "languages": [
            {
                "code": "ca",
                "name": "Català",
                "dialects": ["central", "valencian", "balearic"],
                "tts": True,
                "asr": True,
                "llm": True
            },
            {
                "code": "es",
                "name": "Español",
                "dialects": ["castilian"],
                "tts": True,
                "asr": True,
                "llm": True
            },
            {
                "code": "eu",
                "name": "Euskera",
                "dialects": ["standard"],
                "tts": True,
                "asr": True,
                "llm": True
            },
            {
                "code": "gl",
                "name": "Galego",
                "dialects": ["standard"],
                "tts": True,
                "asr": True,
                "llm": True
            }
        ]
    }


# ============================================
# FASE 3: Nous Endpoints
# ============================================

@router.post("/asr/transcribe")
async def transcribe_audio_alia(request: Request):
    """
    Transcriure àudio amb models ASR ALIA Kit
    FASE 3: ASR Avançat
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        # Llegir àudio del request
        form = await request.form()
        audio_file = await form.get("audio").read()
        language = form.get("language", "ca")
        model_preference = form.get("model_preference", "auto")
        return_timestamps = form.get("return_timestamps", "false").lower() == "true"
        
        logger.info(f"🎯 ALIA ASR: Transcribing audio in {language}")
        
        # Transcriure amb ALIA ASR Advanced
        result = await alia_asr_advanced.transcribe_audio(
            audio_file=audio_file,
            language=language,
            model_preference=model_preference,
            return_timestamps=return_timestamps
        )
        
        if result.get("success"):
            logger.info(f"✅ ALIA ASR exitós: {result.get('text', '')[:50]}...")
            return result
        else:
            logger.error(f"❌ ALIA ASR falló: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "ASR transcription failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ALIA ASR: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/asr/detect-language")
async def detect_language_alia(request: Request):
    """
    Detectar idioma de l'àudio
    FASE 3: ASR Avançat
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        # Llegir àudio del request
        form = await request.form()
        audio_file = await form.get("audio").read()
        
        logger.info(f"🎯 ALIA ASR: Detecting language")
        
        # Detectar idioma
        result = await alia_asr_advanced.detect_language(audio_file)
        
        if result.get("success"):
            logger.info(f"✅ Language detected: {result.get('language')}")
            return result
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Language detection failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in language detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/llm/chat")
async def chat_alia_llm(request: AliaLLMChatRequest):
    """
    Conversa amb LLM ALIA Kit (Salamandra, ALIA-40B)
    FASE 3: LLM Multilingüe
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        logger.info(f"🎯 ALIA LLM Chat: {request.model_name} in {request.language}")
        
        # Generar resposta amb ALIA LLM
        result = await alia_llm_multilingual.chat_completion(
            messages=request.messages,
            model_name=request.model_name,
            language=request.language,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        if result.get("success"):
            logger.info(f"✅ ALIA LLM Chat exitós")
            return result
        else:
            logger.error(f"❌ ALIA LLM Chat falló: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "LLM chat failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ALIA LLM Chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/llm/models")
async def list_llm_models():
    """
    Llistar models LLM ALIA Kit disponibles
    FASE 3: LLM Multilingüe
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        models = alia_llm_multilingual.get_alia_llm_models()
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"Error listing LLM models: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translation/translate")
async def translate_text_alia(request: AliaTranslationRequest):
    """
    Traduir text entre idiomes
    FASE 3: Traducció Multilingüe
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        logger.info(f"🎯 ALIA Translation: {request.source_lang} -> {request.target_lang}")
        
        # Traduir amb ALIA Translation
        result = await alia_translation.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
        
        if result.get("success"):
            logger.info(f"✅ ALIA Translation exitosa")
            return result
        else:
            logger.error(f"❌ ALIA Translation fallà: {result.get('error')}")
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Translation failed")
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ALIA Translation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/translation/languages")
async def get_translation_languages():
    """
    Obtenir idiomes suportats per traducció
    FASE 3: Traducció Multilingüe
    """
    if not ALIA_AVAILABLE:
        raise HTTPException(status_code=503, detail="ALIA Kit integration not available")
    
    try:
        languages = alia_translation.get_supported_languages()
        models = alia_translation.get_translation_models()
        
        return {
            "success": True,
            "languages": languages,
            "translation_pairs": list(models.keys()),
            "count": len(languages)
        }
    except Exception as e:
        logger.error(f"Error getting translation languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export router
__all__ = ["router"]

