#!/usr/bin/env python3
"""
Endpoints de test per verificar que tot funciona
"""
from fastapi import APIRouter
import logging

logger = logging.getLogger("veuplus.test")

router = APIRouter(prefix="/api/test", tags=["Test Endpoints"])

@router.get("/health")
async def test_health():
    """Test básico de salud"""
    return {
        "status": "ok",
        "message": "Backend funcionando correctamente",
        "timestamp": "2025-10-15"
    }

@router.get("/voices/simple")
async def test_voices_simple():
    """Test simple de veus"""
    try:
        import edge_tts
        voices = await edge_tts.list_voices()
        
        # Retornar només les primeres 10 veus per test
        test_voices = []
        for voice in voices[:10]:
            test_voices.append({
                "id": voice.get("ShortName", "unknown"),
                "name": voice.get("DisplayName", "Unknown Voice"),
                "language": voice.get("Locale", "unknown"),
                "gender": voice.get("Gender", "Unknown")
            })
        
        return {
            "success": True,
            "total_voices": len(voices),
            "test_voices": test_voices,
            "message": f"Edge-TTS funciona! {len(voices)} veus disponibles"
        }
    except Exception as e:
        logger.error(f"Error test voices: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Error obtenint veus Edge-TTS"
        }

__all__ = ["router"]
