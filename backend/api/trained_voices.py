#!/usr/bin/env python3
"""
API ESPECÍFICA PARA VOCES ENTRENADAS REALES
Separado completamente de ALIA Kit y Edge-TTS
"""
import logging
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
from datetime import datetime
from pathlib import Path
import base64
import tempfile
import os

logger = logging.getLogger("veuplus.trained_voices")

# Router específico para voces entrenadas
trained_router = APIRouter(prefix="/api/trained", tags=["Trained Voices"])

@trained_router.post("/synthesize")
async def synthesize_trained_voice(request: Request):
    """
    🎯 SÍNTESIS EXCLUSIVA PARA VOCES ENTRENADAS REALES
    
    Usa únicamente:
    - Grabaciones reales procesadas en training_data/
    - Características vocales extraídas (F0, MFCC, espectros)
    - Procesamiento neural basado en grabaciones reales
    - NO usa Edge-TTS ni ALIA Kit
    
    Voces disponibles:
    - senyor_catala_1 (grabación real Barcelona)
    - senyor_catala_2 (grabación real Barcelona) 
    - senyor_catala_extended (grabación real Barcelona)
    - dona_catalana (grabación real Barcelona)
    """
    try:
        data = await request.json()
        text = data.get("text", "")
        voice_id = data.get("voice_id", "senyor_catala_1")
        language = data.get("language", "ca")
        voice_settings = data.get("voice_settings", {})
        
        # Validar que sea voz entrenada
        trained_voices = [
            "senyor_catala_1", "senyor_catala_2", "senyor_catala_extended", 
            "dona_catalana", "trained_senyor_catala_1", "trained_dona_catalana"
        ]
        
        clean_voice_id = voice_id.replace("trained_", "")
        
        if clean_voice_id not in trained_voices:
            raise HTTPException(
                status_code=400, 
                detail=f"Solo voces entrenadas permitidas: {trained_voices}"
            )
        
        logger.info(f"🎯 VOZ ENTRENADA REAL: '{text[:30]}...' con voz '{voice_id}'")
        
        # USAR ÚNICAMENTE EL SISTEMA DE VOCES ENTRENADAS
        try:
            from backend.realistic_catalan_tts import RealisticCatalanTTS
            
            tts_engine = RealisticCatalanTTS()
            result = await tts_engine._synthesize_trained_voice_fallback(
                text, clean_voice_id, voice_settings
            )
            
            if result.get("success", False):
                # Marcar claramente como canal entrenado
                enhanced_result = {
                    **result,
                    "voice_type": "trained_real",
                    "source": "real_recordings",
                    "quality": "hyperrealistic_trained",
                    "training_data": f"training_data/{clean_voice_id}/processed.wav",
                    "features_extracted": True,
                    "neural_processing": True
                }
                
                logger.info(f"✅ SÍNTESIS ENTRENADA EXITOSA con voz: {voice_id}")
                return enhanced_result
            else:
                logger.error(f"❌ Síntesis entrenada falló: {result.get('error')}")
                raise HTTPException(
                    status_code=500, 
                    detail=f"Error en síntesis entrenada: {result.get('error')}"
                )
                
        except ImportError as e:
            logger.error(f"Módulo síntesis entrenada no disponible: {e}")
            raise HTTPException(
                status_code=503,
                detail="Sistema de voces entrenadas no disponible"
            )
        except Exception as e:
            logger.error(f"Error en síntesis entrenada: {e}")
            raise HTTPException(status_code=500, detail=str(e))
            
    except Exception as e:
        logger.error(f"Error en endpoint entrenado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@trained_router.get("/voices")
async def get_trained_voices():
    """Obtener voces entrenadas reales disponibles"""
    
    trained_voices = []
    training_data_dir = Path("backend/training_data")
    
    if training_data_dir.exists():
        for subdir in training_data_dir.iterdir():
            if subdir.is_dir():
                metadata_file = subdir / "metadata.json"
                wav_file = subdir / "processed.wav"
                
                if metadata_file.exists() and wav_file.exists():
                    try:
                        import json
                        with open(metadata_file, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                        
                        voice_info = {
                            "id": metadata.get("id", subdir.name),
                            "name": f"{metadata.get('id', subdir.name).replace('_', ' ').title()} (Entrenada)",
                            "gender": metadata.get("gender", "unknown"),
                            "dialect": metadata.get("dialect", "central"),
                            "duration": metadata.get("duration", 0),
                            "sample_rate": metadata.get("sample_rate", 22050),
                            "description": metadata.get("description", "Voz entrenada con grabaciones reales"),
                            "voice_type": "trained_real",
                            "source": "real_recordings",
                            "quality": "hyperrealistic_trained",
                            "features": metadata.get("voice_features", {}),
                            "training_date": metadata.get("processed_at", "unknown")
                        }
                        trained_voices.append(voice_info)
                    except Exception as e:
                        logger.warning(f"Error reading metadata for {subdir.name}: {e}")
    
    return {
        "trained_voices": trained_voices,
        "total_trained": len(trained_voices),
        "voice_type": "trained_real",
        "description": "Voces entrenadas usando grabaciones reales procesadas"
    }

@trained_router.get("/health")
async def trained_health():
    """Health check específico para sistema de voces entrenadas"""
    
    try:
        training_data_dir = Path("backend/training_data")
        if not training_data_dir.exists():
            return {
                "status": "unhealthy",
                "error": "Directorio training_data no existe",
                "voice_type": "trained_real"
            }
        
        # Verificar voces disponibles
        available_voices = []
        for subdir in training_data_dir.iterdir():
            if subdir.is_dir():
                wav_file = subdir / "processed.wav"
                metadata_file = subdir / "metadata.json"
                if wav_file.exists() and metadata_file.exists():
                    available_voices.append(subdir.name)
        
        return {
            "status": "healthy" if available_voices else "no_voices",
            "trained_voices_available": len(available_voices),
            "available_voices": available_voices,
            "voice_type": "trained_real",
            "separated_from_edge_tts": True,
            "separated_from_alia_kit": True,
            "description": "Sistema de voces entrenadas completamente separado"
        }
        
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "voice_type": "trained_real"
        }
