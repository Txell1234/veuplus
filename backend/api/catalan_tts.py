#!/usr/bin/env python3
"""
Catalan hyperrealistic (Sistema 2) synthesis API.

For now we serve locally recorded samples (mock inference) so the system
does not depend on Edge-TTS. When neural models are available we can plug
them into HyperVoiceEngine without touching the API contract.
"""
from __future__ import annotations

import base64
import logging
import os
import tempfile
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request

try:
    from backend.hyperrealistic_engine import HyperVoiceEngine, build_inventory
except Exception:  # pragma: no cover - local execution fallback
    from hyperrealistic_engine import HyperVoiceEngine, build_inventory  # type: ignore

logger = logging.getLogger("veuplus.catalan_tts")

catalan_router = APIRouter(prefix="/api/catalan", tags=["Catalan Hyperrealistic TTS"])
hyper_engine = HyperVoiceEngine()

EDGE_VOICE_MAPPING = {
    "senyor_catala_1": "ca-ES-AlbaNeural",
    "dona_catalana": "ca-ES-JoanaNeural",
    "senyor_catala_2": "ca-ES-AlbaNeural",
    "senyor_catala_extended": "ca-ES-AlbaNeural",
}


def _normalize_voice_id(voice_id: str) -> str:
    return voice_id.replace("trained_trained_", "").replace("trained_", "").strip()


@catalan_router.post("/synthesize")
async def synthesize_catalan_voice(request: Request):
    """
    Synthesise Catalan speech using local resources (mock) with SEGRE support.
    Falls back to Edge-TTS only when no local asset is available.
    """
    data = await request.json()
    text = data.get("text", "")
    voice_id = data.get("voice_id", "senyor_catala_1")
    language = data.get("language", "ca")
    voice_settings = data.get("voice_settings", {})

    if not text:
        raise HTTPException(status_code=400, detail="Text buit")

    clean_voice_id = _normalize_voice_id(voice_id)

    # Optional SEGRE phonetic processing
    phonetic_text = text
    segre_applied = False
    try:
        from backend.segre_integration import segre_transcribe  # type: ignore

        dialect = voice_settings.get("dialect", "central")
        segre_result = segre_transcribe(text, dialect=dialect)
        if segre_result and len(segre_result) > 0:
            phonetic_text = segre_result[0]
            segre_applied = True
            logger.info("[SEGRE] %s -> %s", text[:30], phonetic_text[:30])
    except Exception as segre_error:
        logger.warning("[SEGRE] no disponible: %s", segre_error)

    # Attempt local hyperrealistic mock
    local_result = hyper_engine.synthesize(clean_voice_id)
    if local_result.get("success"):
        logger.info(
            "[HyperLocal] Veu %s servida des de %s (mock=%s)",
            clean_voice_id,
            local_result.get("source"),
            local_result.get("mock"),
        )
        return {
            "success": True,
            "audio_base64": local_result["audio_base64"],
            "voice_id": voice_id,
            "text": text,
            "phonetic_text": phonetic_text,
            "segre_applied": segre_applied,
            "size": len(base64.b64decode(local_result["audio_base64"])),
            "mime_type": local_result.get("mime_type", "audio/wav"),
            "system": "catalan_hyperlocal",
            "mock": local_result.get("mock", True),
            "source": local_result.get("source"),
            "notes": local_result.get("notes"),
            "metadata": local_result.get("metadata"),
        }

    # No local sample -> fallback to Edge-TTS
    logger.warning(
        "[HyperLocal] Veu %s no disponible localment (%s). Fent fallback a Edge.",
        clean_voice_id,
        local_result.get("error"),
    )
    edge_voice = EDGE_VOICE_MAPPING.get(clean_voice_id, "ca-ES-AlbaNeural")

    try:
        import edge_tts
        import ssl
        import certifi

        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl._create_default_https_context = lambda: ssl_context

        communicate = edge_tts.Communicate(phonetic_text, edge_voice)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_file:
            await communicate.save(tmp_file.name)
            with open(tmp_file.name, "rb") as audio_file:
                audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        try:
            os.unlink(tmp_file.name)
        except Exception:
            pass

        logger.info(
            "[EdgeFallback] Veu %s -> %s bytes (edge voice %s)",
            clean_voice_id,
            len(audio_data),
            edge_voice,
        )

        return {
            "success": True,
            "audio_base64": audio_base64,
            "voice_id": voice_id,
            "text": text,
            "phonetic_text": phonetic_text,
            "segre_applied": segre_applied,
            "size": len(audio_data),
            "mime_type": "audio/mpeg",
            "system": "catalan_edge_fallback",
            "mock": False,
            "source": "edge_tts",
            "notes": "Fallback Edge-TTS per manca de model local.",
        }
    except Exception as edge_error:
        logger.error("[EdgeFallback] Error en síntesi catalana: %s", edge_error)
        raise HTTPException(
            status_code=500,
            detail=f"Error de connexió amb Edge-TTS: {edge_error}",
        )


@catalan_router.get("/voices")
async def get_catalan_voices():
    """Return available hyperlocal voices."""
    try:
        hyper_engine.refresh()
        voices = hyper_engine.list_voices()
        return {
            "success": True,
            "voices": voices,
            "total": len(voices),
            "system": "Sistema 2 - Hyperlocal (mock sense GPU)",
            "description": "Veus catalanes basades en enregistraments locals.",
        }
    except Exception as error:
        logger.error("Error obtenint veus locals: %s", error)
        raise HTTPException(status_code=500, detail=str(error))


@catalan_router.get("/voices/all")
async def get_catalan_voices_all():
    """Detailed inventory of available resources."""
    try:
        inventory = build_inventory()
        return {
            "success": True,
            "inventory": inventory,
            "generated_at": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as error:
        logger.error("Error generant inventari de veus: %s", error)
        raise HTTPException(status_code=500, detail=str(error))


@catalan_router.get("/health")
async def catalan_health():
    """Health check for the hyperlocal system."""
    try:
        hyper_engine.refresh()
        voices = hyper_engine.list_voices()
        return {
            "status": "healthy" if voices else "degraded",
            "available_voices": len(voices),
            "edge_fallback_enabled": True,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as error:
        return {
            "status": "unhealthy",
            "error": str(error),
            "edge_fallback_enabled": True,
        }
