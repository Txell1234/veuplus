from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os
import logging

# Importar motor ASR real
try:
    from backend.asr_engine import asr_engine
    ASR_ENGINE_AVAILABLE = True
except ImportError:
    ASR_ENGINE_AVAILABLE = False

router = APIRouter(prefix="/api/asr", tags=["ASR"])
logger = logging.getLogger("veuplus.api.asr")


class ASRResponse(BaseModel):
    text: str
    language: str
    created_at: str


# Determine max upload from server or env
try:
    from backend.server import MAX_UPLOAD_SIZE_MB as _MAX
except Exception:
    try:
        from server import MAX_UPLOAD_SIZE_MB as _MAX  # type: ignore
    except Exception:
        _MAX = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "20"))


@router.post("/transcribe")
async def transcribe(file: UploadFile = File(...), language: Optional[str] = "ca"):
    """Endpoint ASR funcional usando Faster-Whisper.
    Transcribe audio real a texto cuando está disponible, fallback a placeholder.
    """
    try:
        logger.info(f"Solicitud ASR: archivo '{file.filename}' en {language}")
        
        # Validar tamaño del archivo
        data = await file.read()
        if len(data) > _MAX * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        
        # Inicializar motor ASR si no está inicializado
        if ASR_ENGINE_AVAILABLE and not asr_engine.is_initialized:
            logger.info("Inicializando motor ASR...")
            asr_engine.initialize()
        
        # Usar motor ASR real si está disponible
        if ASR_ENGINE_AVAILABLE and asr_engine.is_initialized:
            result = asr_engine.transcribe_audio(data, file.filename or "audio.wav", language or "ca")
            logger.info(f"ASR real completado: {result.get('real_asr', False)}")
            return result
        else:
            # Fallback a placeholder si ASR no está disponible
            logger.warning("ASR no disponible, usando placeholder")
            return ASRResponse(
                text=f"[Transcripción de {file.filename}]",
                language=language or "ca", 
                created_at=datetime.utcnow().isoformat()
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error en transcripción ASR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_supported_languages():
    """Obtener idiomas soportados por el motor ASR"""
    try:
        # Inicializar motor ASR si no está inicializado
        if ASR_ENGINE_AVAILABLE and not asr_engine.is_initialized:
            asr_engine.initialize()
        
        if ASR_ENGINE_AVAILABLE and asr_engine.is_initialized:
            return asr_engine.get_supported_languages()
        else:
            return {
                "supported_languages": ["ca", "es", "en", "fr", "pt"],
                "language_names": {
                    "ca": "Catalán",
                    "es": "Español",
                    "en": "Inglés", 
                    "fr": "Francés",
                    "pt": "Portugués"
                },
                "asr_engine": "Placeholder",
                "model_name": "none"
            }
    except Exception as e:
        logger.error(f"Error obteniendo idiomas soportados: {e}")
        raise HTTPException(status_code=500, detail=str(e))


