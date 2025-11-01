"""
API Simple per Chatbots i Voicebots
Endpoints bàsics per funcionar amb el frontend
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import logging

logger = logging.getLogger("veuplus.simple_chatbots")

router = APIRouter(prefix="/api", tags=["Simple Chatbots & Voicebots"])

# Dades per defecte
DEFAULT_CHATBOTS = [
    {
        "id": "default-catalan",
        "name": "Assistent Català",
        "description": "Assistent intel·ligent en català",
        "system_prompt": "Ets un assistent útil i amigable. Respon sempre en català.",
        "llm_provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "voice_id": "ca-ES-EnricNeural",
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": "default-spanish",
        "name": "Asistente Español",
        "description": "Asistente inteligente en español",
        "system_prompt": "Eres un asistente útil y amigable. Responde siempre en español.",
        "llm_provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "voice_id": "es-ES-AlvaroNeural",
        "created_at": "2024-01-15T10:00:00Z"
    }
]

DEFAULT_VOICEBOTS = [
    {
        "id": "default-catalan-voicebot",
        "name": "Voicebot Català",
        "description": "Voicebot intel·ligent en català amb veu",
        "system_prompt": "Ets un assistent de veu útil i amigable. Respon sempre en català.",
        "llm_provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "voice_id": "senyor_catala_1",
        "voice_system": "catalan",
        "tts_enabled": True,
        "asr_enabled": True,
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": "default-spanish-voicebot",
        "name": "Voicebot Español",
        "description": "Voicebot inteligente en español con voz",
        "system_prompt": "Eres un asistente de voz útil y amigable. Responde siempre en español.",
        "llm_provider": "openai",
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "max_tokens": 1000,
        "voice_id": "es-ES-AlvaroNeural",
        "voice_system": "edge-tts",
        "tts_enabled": True,
        "asr_enabled": True,
        "created_at": "2024-01-15T10:00:00Z"
    },
    {
        "id": "default-alia-voicebot",
        "name": "Voicebot ALIA Premium",
        "description": "Voicebot con veus premium ALIA BSC",
        "system_prompt": "Eres un asistente premium con voz de alta calidad. Responde de manera profesional.",
        "llm_provider": "alia",
        "model": "BSC-LT/salamandra-7b",
        "temperature": 0.7,
        "max_tokens": 1000,
        "voice_id": "ca-ES-AlbaNeural",
        "voice_system": "alia",
        "tts_enabled": True,
        "asr_enabled": True,
        "created_at": "2024-01-15T10:00:00Z"
    }
]

@router.get("/chatbots")
async def get_chatbots():
    """Obtenir llista de chatbots"""
    try:
        logger.info("✅ Chatbots disponibles: 2 per defecte")
        return {
            "success": True,
            "chatbots": DEFAULT_CHATBOTS,
            "count": len(DEFAULT_CHATBOTS)
        }
    except Exception as e:
        logger.error(f"Error getting chatbots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voicebots")
async def get_voicebots():
    """Obtenir llista de voicebots"""
    try:
        logger.info("✅ Voicebots disponibles: 2 per defecte")
        return {
            "success": True,
            "voicebots": DEFAULT_VOICEBOTS,
            "count": len(DEFAULT_VOICEBOTS)
        }
    except Exception as e:
        logger.error(f"Error getting voicebots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chatbots")
async def create_chatbot(chatbot_data: Dict[str, Any]):
    """Crear nou chatbot"""
    try:
        logger.info(f"✅ Chatbot creat: {chatbot_data.get('name', 'Unknown')}")
        return {
            "success": True,
            "message": "Chatbot creat correctament",
            "chatbot": chatbot_data
        }
    except Exception as e:
        logger.error(f"Error creating chatbot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voicebots")
async def create_voicebot(voicebot_data: Dict[str, Any]):
    """Crear nou voicebot"""
    try:
        logger.info(f"✅ Voicebot creat: {voicebot_data.get('name', 'Unknown')}")
        return {
            "success": True,
            "message": "Voicebot creat correctament",
            "voicebot": voicebot_data
        }
    except Exception as e:
        logger.error(f"Error creating voicebot: {e}")
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["router"]
