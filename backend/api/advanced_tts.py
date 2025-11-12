"""
API Avanzada de TTS para VeusPlus
Integra todos los sistemas de voz personalizada
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
import asyncio
import threading
import base64
from datetime import datetime

logger = logging.getLogger("veuplus.advanced_tts")

# Crear router
router = APIRouter(prefix="/api/advanced-tts", tags=["Advanced TTS"])

# Importar sistemas
try:
    from ..voice_cloning_system import voice_cloning_system
    VOICE_CLONING_AVAILABLE = True
except ImportError:
    VOICE_CLONING_AVAILABLE = False

try:
    from ..voice_training_models import voice_training_system
    VOICE_TRAINING_AVAILABLE = True
except ImportError:
    VOICE_TRAINING_AVAILABLE = False

try:
    from ..voice_mixing_system import voice_mixing_system
    VOICE_MIXING_AVAILABLE = True
except ImportError:
    VOICE_MIXING_AVAILABLE = False

try:
    from ..voice_parameter_tuning import voice_parameter_tuning
    VOICE_TUNING_AVAILABLE = True
except ImportError:
    VOICE_TUNING_AVAILABLE = False

try:
    from ..audio_post_processing import audio_post_processing
    AUDIO_POST_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_POST_PROCESSING_AVAILABLE = False

try:
    from ..voice_management_system import voice_management_system
    VOICE_MANAGEMENT_AVAILABLE = True
except ImportError:
    VOICE_MANAGEMENT_AVAILABLE = False

# Modelos Pydantic
class VoiceCloningRequest(BaseModel):
    name: str
    description: str = ""
    language: str = "ca"
    quality: str = "high"

class VoiceTrainingRequest(BaseModel):
    name: str
    language: str = "ca"
    dialect: str = "central"
    quality: str = "high"
    epochs: int = 50
    batch_size: int = 8
    learning_rate: float = 0.0001

class VoiceMixingRequest(BaseModel):
    name: str
    description: str = ""
    base_voice_id: str
    mix_voice_id: str
    mix_ratio: float = 0.5
    language: str = "ca"

class ParameterTuningRequest(BaseModel):
    voice_id: str
    text: str
    tuning_profile_id: str
    language: str = "ca"
    custom_overrides: Optional[Dict] = None

class AudioProcessingRequest(BaseModel):
    audio_base64: str
    processing_profile: str = "high"
    custom_parameters: Optional[Dict] = None

class VoiceManagementRequest(BaseModel):
    category: Optional[str] = None
    language: Optional[str] = None
    quality: Optional[str] = None
    search_query: Optional[str] = None

# Endpoints de clonación de voz
@router.post("/voice-cloning/upload-samples")
async def upload_voice_samples(
    background_tasks: BackgroundTasks,
    name: str = Form(...),
    description: str = Form(""),
    language: str = Form("ca"),
    quality: str = Form("high"),
    files: List[UploadFile] = File(...)
):
    """Subir muestras de audio para clonación de voz"""
    try:
        if not VOICE_CLONING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de clonación de voz no disponible")
        
        # Procesar archivos en background
        background_tasks.add_task(
            process_voice_samples,
            name, description, language, quality, files
        )
        
        return {
            "success": True,
            "message": "Muestras de voz subidas correctamente",
            "name": name,
            "files_count": len(files),
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error subiendo muestras de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_voice_samples(name: str, description: str, language: str, quality: str, files: List[UploadFile]):
    """Procesar muestras de voz en background"""
    try:
        # Aquí se procesarían los archivos de audio
        logger.info(f"Procesando {len(files)} muestras para voz: {name}")
        # Implementar lógica de procesamiento
    except Exception as e:
        logger.error(f"Error procesando muestras: {e}")

@router.get("/voice-cloning/voices")
async def get_cloned_voices():
    """Obtener voces clonadas disponibles"""
    try:
        if not VOICE_CLONING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de clonación de voz no disponible")
        
        result = voice_cloning_system.get_cloned_voices()
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo voces clonadas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de entrenamiento de voces
@router.post("/voice-training/start")
async def start_voice_training(
    background_tasks: BackgroundTasks,
    request: VoiceTrainingRequest
):
    """Iniciar entrenamiento de modelo de voz"""
    try:
        if not VOICE_TRAINING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de entrenamiento de voces no disponible")
        
        # Iniciar entrenamiento en background
        background_tasks.add_task(
            train_voice_model,
            request.dict()
        )
        
        return {
            "success": True,
            "message": "Entrenamiento de voz iniciado",
            "model_name": request.name,
            "status": "training_started"
        }
        
    except Exception as e:
        logger.error(f"Error iniciando entrenamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def train_voice_model(config: Dict):
    """Entrenar modelo de voz en background"""
    try:
        logger.info(f"Iniciando entrenamiento de modelo: {config['name']}")
        # Implementar lógica de entrenamiento
    except Exception as e:
        logger.error(f"Error entrenando modelo: {e}")

@router.get("/voice-training/models")
async def get_trained_models():
    """Obtener modelos de voz entrenados"""
    try:
        if not VOICE_TRAINING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de entrenamiento de voces no disponible")
        
        result = voice_training_system.get_trained_models()
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo modelos entrenados: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de mezcla de voces
@router.post("/voice-mixing/create")
async def create_mixed_voice(request: VoiceMixingRequest):
    """Crear voz mezclada"""
    try:
        if not VOICE_MIXING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de mezcla de voces no disponible")
        
        result = await voice_mixing_system.create_mixed_voice(
            request.name,
            request.description,
            request.base_voice_id,
            request.mix_voice_id,
            request.mix_ratio,
            request.language
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creando voz mezclada: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice-mixing/voices")
async def get_mixed_voices():
    """Obtener voces mezcladas disponibles"""
    try:
        if not VOICE_MIXING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de mezcla de voces no disponible")
        
        result = voice_mixing_system.get_mixed_voices()
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo voces mezcladas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de ajuste fino de parámetros
@router.post("/parameter-tuning/create-profile")
async def create_tuning_profile(
    profile_name: str,
    base_preset: str = "natural",
    custom_parameters: Optional[Dict] = None,
    description: str = ""
):
    """Crear perfil de ajuste fino"""
    try:
        if not VOICE_TUNING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de ajuste fino no disponible")
        
        result = await voice_parameter_tuning.create_tuning_profile(
            profile_name, base_preset, custom_parameters, description
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error creando perfil de ajuste: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/parameter-tuning/synthesize")
async def synthesize_with_tuning(request: ParameterTuningRequest):
    """Sintetizar con ajuste fino de parámetros"""
    try:
        if not VOICE_TUNING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de ajuste fino no disponible")
        
        result = await voice_parameter_tuning.tune_voice_parameters(
            request.voice_id,
            request.text,
            request.tuning_profile_id,
            request.language,
            request.custom_overrides
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error en síntesis con ajuste fino: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/parameter-tuning/profiles")
async def get_tuning_profiles():
    """Obtener perfiles de ajuste fino"""
    try:
        if not VOICE_TUNING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de ajuste fino no disponible")
        
        result = voice_parameter_tuning.get_tuning_profiles()
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo perfiles de ajuste: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de post-procesamiento de audio
@router.post("/audio-processing/process")
async def process_audio(request: AudioProcessingRequest):
    """Procesar audio con mejoras de calidad"""
    try:
        if not AUDIO_POST_PROCESSING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de post-procesamiento no disponible")
        
        result = await audio_post_processing.process_audio(
            request.audio_base64,
            request.processing_profile,
            request.custom_parameters
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error procesando audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio-processing/profiles")
async def get_processing_profiles():
    """Obtener perfiles de procesamiento disponibles"""
    try:
        if not AUDIO_POST_PROCESSING_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de post-procesamiento no disponible")
        
        result = audio_post_processing.get_processing_profiles()
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo perfiles de procesamiento: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoints de gestión de voces
@router.get("/voice-management/voices")
async def get_all_voices(request: VoiceManagementRequest):
    """Obtener todas las voces con filtros"""
    try:
        if not VOICE_MANAGEMENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de gestión de voces no disponible")
        
        result = await voice_management_system.get_all_voices(
            request.category,
            request.language,
            request.quality,
            request.search_query
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo voces: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice-management/voice/{voice_id}")
async def get_voice_details(voice_id: str):
    """Obtener detalles de una voz específica"""
    try:
        if not VOICE_MANAGEMENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de gestión de voces no disponible")
        
        result = await voice_management_system.get_voice_details(voice_id)
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo detalles de voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-management/voice/{voice_id}/rate")
async def rate_voice(voice_id: str, rating: int):
    """Calificar una voz"""
    try:
        if not VOICE_MANAGEMENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de gestión de voces no disponible")
        
        if rating < 1 or rating > 5:
            raise HTTPException(status_code=400, detail="La calificación debe estar entre 1 y 5")
        
        result = await voice_management_system.rate_voice(voice_id, rating)
        
        return {
            "success": result,
            "voice_id": voice_id,
            "rating": rating
        }
        
    except Exception as e:
        logger.error(f"Error calificando voz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/voice-management/voice/{voice_id}/tag")
async def add_voice_tag(voice_id: str, tag: str):
    """Añadir etiqueta a una voz"""
    try:
        if not VOICE_MANAGEMENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de gestión de voces no disponible")
        
        result = await voice_management_system.add_voice_tag(voice_id, tag)
        
        return {
            "success": result,
            "voice_id": voice_id,
            "tag": tag
        }
        
    except Exception as e:
        logger.error(f"Error añadiendo etiqueta: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice-management/statistics")
async def get_voice_statistics():
    """Obtener estadísticas de voces"""
    try:
        if not VOICE_MANAGEMENT_AVAILABLE:
            raise HTTPException(status_code=503, detail="Sistema de gestión de voces no disponible")
        
        result = await voice_management_system.get_voice_statistics()
        return result
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint de estado del sistema
@router.get("/status")
async def get_system_status():
    """Obtener estado de todos los sistemas"""
    return {
        "voice_cloning": {
            "available": VOICE_CLONING_AVAILABLE,
            "status": "active" if VOICE_CLONING_AVAILABLE else "unavailable"
        },
        "voice_training": {
            "available": VOICE_TRAINING_AVAILABLE,
            "status": "active" if VOICE_TRAINING_AVAILABLE else "unavailable"
        },
        "voice_mixing": {
            "available": VOICE_MIXING_AVAILABLE,
            "status": "active" if VOICE_MIXING_AVAILABLE else "unavailable"
        },
        "parameter_tuning": {
            "available": VOICE_TUNING_AVAILABLE,
            "status": "active" if VOICE_TUNING_AVAILABLE else "unavailable"
        },
        "audio_processing": {
            "available": AUDIO_POST_PROCESSING_AVAILABLE,
            "status": "active" if AUDIO_POST_PROCESSING_AVAILABLE else "unavailable"
        },
        "voice_management": {
            "available": VOICE_MANAGEMENT_AVAILABLE,
            "status": "active" if VOICE_MANAGEMENT_AVAILABLE else "unavailable"
        },
        "timestamp": datetime.now().isoformat()
    }



















