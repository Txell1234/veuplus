from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
import base64
import os
from datetime import datetime
import logging

# Importar motor TTS real
try:
    from ..tts_engine import tts_engine
    TTS_ENGINE_AVAILABLE = True
except ImportError:
    try:
        from backend.tts_engine import tts_engine
        TTS_ENGINE_AVAILABLE = True
    except ImportError:
        try:
            from tts_engine import tts_engine
            TTS_ENGINE_AVAILABLE = True
        except ImportError:
            TTS_ENGINE_AVAILABLE = False

router = APIRouter(prefix="/api/tts", tags=["TTS"])
logger = logging.getLogger("veuplus.api.tts")


class TTSRequest(BaseModel):
    text: str
    voice_model_id: Optional[str] = None
    language: Optional[str] = "ca"
    speaker_id: Optional[str] = None

    @field_validator("text")
    @classmethod
    def _validate_text(cls, v: str):
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        if len(v) > 1000:
            raise ValueError("text too long (max 1000 chars)")
        return v


@router.post("/synthesize")
async def synthesize(req: TTSRequest):
    """Endpoint TTS funcional usando Coqui XTTS v2.
    Sintetiza texto real a audio cuando está disponible, fallback a placeholder.
    """
    try:
        logger.info(f"Solicitud TTS: '{req.text[:50]}...' en {req.language}")
        
        # Inicializar motor TTS si no está inicializado
        if TTS_ENGINE_AVAILABLE and not tts_engine.is_initialized:
            logger.info("Inicializando motor TTS...")
            tts_engine.initialize()
        
        # Usar motor TTS real si está disponible
        if TTS_ENGINE_AVAILABLE and tts_engine.is_initialized:
            result = tts_engine.synthesize_speech(
                text=req.text,
                language=req.language or "ca",
                speaker_id=req.speaker_id,
                voice_model_id=req.voice_model_id
            )
            logger.info(f"TTS real generado: {result.get('real_tts', False)}")
            return result
        else:
            # Fallback a placeholder si TTS no está disponible
            logger.warning("TTS no disponible, usando placeholder")
            return _generate_placeholder_audio(req.text, req.voice_model_id, req.speaker_id)
            
    except Exception as e:
        logger.error(f"Error en síntesis TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_placeholder_audio(text: str, voice_model_id: Optional[str], speaker_id: Optional[str]) -> Dict[str, Any]:
    """Generar audio placeholder como fallback"""
    try:
        # Generar silencio de 1 segundo a 16kHz
        sr = 16000
        duration = 1
        num_samples = sr * duration
        pcm_bytes = b"\x00\x00" * num_samples
        import wave
        from io import BytesIO

        buf = BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm_bytes)

        audio_b64 = base64.b64encode(buf.getvalue()).decode()
        return {
            "audio_base64": audio_b64,
            "mime": "audio/wav",
            "voice_model_id": voice_model_id or "placeholder",
            "speaker_id": speaker_id or "unknown",
            "created_at": datetime.utcnow().isoformat(),
            "real_tts": False,
            "fallback_reason": "TTS engine not available"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando placeholder: {str(e)}")

@router.get("/voices")
async def list_voices() -> Dict[str, Any]:
    """Lista voces/locutores disponibles desde el motor TTS y datasets preprocesados.
    Combina voces del motor TTS real con voces de datasets entrenados.
    """
    try:
        # Inicializar motor TTS si no está inicializado
        if TTS_ENGINE_AVAILABLE and not tts_engine.is_initialized:
            logger.info("Inicializando motor TTS para obtener voces...")
            tts_engine.initialize()
        
        # Obtener voces del motor TTS si está disponible
        if TTS_ENGINE_AVAILABLE and tts_engine.is_initialized:
            tts_voices = tts_engine.get_available_voices()
            logger.info(f"Motor TTS disponible con {tts_voices['total']} voces")
        else:
            # Intentar inicializar el motor TTS
            if TTS_ENGINE_AVAILABLE:
                try:
                    logger.info("Inicializando motor TTS para obtener voces...")
                    tts_engine.initialize()
                    if tts_engine.is_initialized:
                        tts_voices = tts_engine.get_available_voices()
                        logger.info(f"Motor TTS inicializado con {tts_voices['total']} voces")
                    else:
                        tts_voices = {"voices": [], "total": 0}
                        logger.warning("Motor TTS no pudo inicializarse")
                except Exception as e:
                    logger.error(f"Error inicializando motor TTS: {e}")
                    tts_voices = {"voices": [], "total": 0}
            else:
                tts_voices = {"voices": [], "total": 0}
                logger.info("Motor TTS no disponible, solo voces de datasets")
        
        # Forzar obtención de voces de Edge-TTS si no hay voces
        if tts_voices.get("total", 0) == 0:
            try:
                logger.info("Forzando obtención de voces de Edge-TTS...")
                from backend.edge_tts_engine import edge_tts_engine
                if edge_tts_engine.is_initialized:
                    edge_voices = edge_tts_engine.get_available_voices()
                    if edge_voices.get("total", 0) > 0:
                        tts_voices = edge_voices
                        logger.info(f"Voces de Edge-TTS obtenidas: {tts_voices['total']}")
            except Exception as e:
                logger.error(f"Error obteniendo voces de Edge-TTS: {e}")
        
        # Buscar voces de datasets preprocesados
        import glob
        from pathlib import Path
        base = Path("backend/preprocessed_data")
        dataset_voices: Dict[str, int] = {}
        
        for path in base.glob("*/audio/speakers.json"):
            try:
                import json
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for spk, cnt in data.get("speakers", {}).items():
                    dataset_voices[spk] = dataset_voices.get(spk, 0) + int(cnt)
            except Exception:
                continue
        
        # Combinar voces de TTS y datasets
        all_voices = list(tts_voices["voices"])
        
        # Agregar voces de datasets
        static_dir = Path("backend/static/voices")
        for spk, count in sorted(dataset_voices.items(), key=lambda kv: kv[0]):
            preview_file = static_dir / f"{spk}_sample.wav"
            sample_url = f"/static/voices/{spk}_sample.wav" if preview_file.exists() else None
            
            # Evitar duplicados
            if not any(v.get("speaker_id") == spk for v in all_voices):
                all_voices.append({
                    "speaker_id": spk, 
                    "samples": count, 
                    "sample_url": sample_url,
                    "source": "dataset"
                })
        
        return {
            "voices": all_voices, 
            "total": len(all_voices),
            "tts_engine": tts_voices.get("tts_engine", "Not available"),
            "engine_status": "active" if (TTS_ENGINE_AVAILABLE and tts_engine.is_initialized) else "inactive"
        }
        
    except Exception as e:
        logger.error(f"Error listando voces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

