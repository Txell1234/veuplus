#!/usr/bin/env python3
"""
ConvHi Voice Configuration System - Sistema multi-veu i multiidioma
Suport per múltiples veus, idiomes i configuracions per agent
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger("veuplus.voice_config")

router = APIRouter(prefix="/api/convhi/voice-config", tags=["ConvHi Voice Configuration"])

# Enums
class VoiceSystem(str, Enum):
    EDGE_TTS = "edge-tts"
    CATALAN = "catalan"
    ALIA = "alia"

class VoiceModel(str, Enum):
    TURBO = "turbo"
    FLASH = "flash"
    MULTILINGUAL = "multilingual"
    SAME_AS_AGENT = "same_as_agent"

# Models
class VoiceConfiguration(BaseModel):
    label: str  # Identificador únic (ex: "narrator", "spanish", "happy")
    voice_system: VoiceSystem
    voice_id: str
    model_family: VoiceModel = VoiceModel.SAME_AS_AGENT
    language: Optional[str] = None  # Override idioma
    description: str = ""
    enabled: bool = True
    speed: float = 1.0  # 0.7x a 1.2x
    pitch: float = 1.0  # Modificació de to
    volume: float = 1.0  # Volum relatiu

class MultiVoiceConfig(BaseModel):
    agent_id: str
    default_voice: VoiceConfiguration
    supported_voices: List[VoiceConfiguration] = []
    max_voices: int = 10
    auto_detect_language: bool = True
    fallback_voice: Optional[str] = None
    created_at: str
    updated_at: str

class VoiceSwitchRequest(BaseModel):
    agent_id: str
    text: str
    voice_labels: Optional[List[str]] = None
    context: Dict[str, Any] = {}

class VoiceSwitchResponse(BaseModel):
    success: bool
    audio_segments: List[Dict[str, Any]] = []
    total_audio_base64: Optional[str] = None
    voice_switches: int = 0
    error: Optional[str] = None

# In-memory storage
voice_configs = {}

class VoiceConfigEngine:
    def __init__(self):
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Inicialitzar configuracions de veu per defecte"""
        
        # Configuració per defecte per agent
        default_config = MultiVoiceConfig(
            agent_id="default",
            default_voice=VoiceConfiguration(
                label="default",
                voice_system=VoiceSystem.EDGE_TTS,
                voice_id="es-ES-ElviraNeural",
                model_family=VoiceModel.SAME_AS_AGENT,
                language="es",
                description="Veu per defecte en espanyol",
                enabled=True
            ),
            supported_voices=[
                VoiceConfiguration(
                    label="catalan",
                    voice_system=VoiceSystem.CATALAN,
                    voice_id="dona_catalana",
                    model_family=VoiceModel.MULTILINGUAL,
                    language="ca",
                    description="Per paraules o frases en català",
                    enabled=True
                ),
                VoiceConfiguration(
                    label="english",
                    voice_system=VoiceSystem.EDGE_TTS,
                    voice_id="en-US-AriaNeural",
                    model_family=VoiceModel.FLASH,
                    language="en",
                    description="Per paraules o frases en anglès",
                    enabled=True
                ),
                VoiceConfiguration(
                    label="narrator",
                    voice_system=VoiceSystem.EDGE_TTS,
                    voice_id="es-ES-AlvaroNeural",
                    model_family=VoiceModel.TURBO,
                    language="es",
                    description="Per narracions i descripcions",
                    enabled=True,
                    speed=0.9,
                    pitch=0.8
                )
            ],
            auto_detect_language=True,
            fallback_voice="default",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        voice_configs["default"] = default_config.dict()
        
        logger.info("✅ Configuracions de veu per defecte inicialitzades")
    
    async def create_voice_config(self, config: MultiVoiceConfig) -> bool:
        """Crear configuració de veu per agent"""
        try:
            config.created_at = datetime.now().isoformat()
            config.updated_at = datetime.now().isoformat()
            
            voice_configs[config.agent_id] = config.dict()
            
            logger.info(f"✅ Configuració de veu creada per agent: {config.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant configuració de veu: {e}")
            return False
    
    async def add_voice_to_agent(self, agent_id: str, voice: VoiceConfiguration) -> bool:
        """Afegir veu a agent"""
        try:
            if agent_id not in voice_configs:
                # Crear configuració bàsica si no existeix
                await self._create_basic_config(agent_id)
            
            config_data = voice_configs[agent_id]
            config = MultiVoiceConfig(**config_data)
            
            # Verificar que no existeixi ja
            for existing_voice in config.supported_voices:
                if existing_voice.label == voice.label:
                    raise ValueError(f"Veu amb label '{voice.label}' ja existeix")
            
            # Verificar límit de veus
            if len(config.supported_voices) >= config.max_voices:
                raise ValueError(f"Màxim de {config.max_voices} veus per agent")
            
            config.supported_voices.append(voice)
            config.updated_at = datetime.now().isoformat()
            
            voice_configs[agent_id] = config.dict()
            
            logger.info(f"✅ Veu '{voice.label}' afegida a agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error afegint veu a agent: {e}")
            return False
    
    async def remove_voice_from_agent(self, agent_id: str, voice_label: str) -> bool:
        """Eliminar veu de agent"""
        try:
            if agent_id not in voice_configs:
                return False
            
            config_data = voice_configs[agent_id]
            config = MultiVoiceConfig(**config_data)
            
            # No permetre eliminar la veu per defecte
            if voice_label == "default":
                raise ValueError("No es pot eliminar la veu per defecte")
            
            # Eliminar veu
            config.supported_voices = [v for v in config.supported_voices if v.label != voice_label]
            config.updated_at = datetime.now().isoformat()
            
            voice_configs[agent_id] = config.dict()
            
            logger.info(f"✅ Veu '{voice_label}' eliminada de agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error eliminant veu de agent: {e}")
            return False
    
    async def switch_voices(self, request: VoiceSwitchRequest) -> VoiceSwitchResponse:
        """Canviar veus en text amb XML markup"""
        try:
            if request.agent_id not in voice_configs:
                # Usar configuració per defecte
                config_data = voice_configs.get("default", {})
            else:
                config_data = voice_configs[request.agent_id]
            
            config = MultiVoiceConfig(**config_data)
            
            # Processar text amb XML markup
            audio_segments = await self._process_voice_switching(request.text, config, request.context)
            
            # Combinar segments d'àudio
            total_audio = await self._combine_audio_segments(audio_segments)
            
            return VoiceSwitchResponse(
                success=True,
                audio_segments=audio_segments,
                total_audio_base64=total_audio,
                voice_switches=len(audio_segments)
            )
            
        except Exception as e:
            logger.error(f"Error canviant veus: {e}")
            return VoiceSwitchResponse(
                success=False,
                error=str(e)
            )
    
    async def _process_voice_switching(self, text: str, config: MultiVoiceConfig, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Processar canvis de veu en text"""
        import re
        
        # Trobar tots els tags de veu
        voice_pattern = r'<([^>]+)>(.*?)</\1>'
        matches = re.findall(voice_pattern, text, re.DOTALL)
        
        audio_segments = []
        
        if not matches:
            # No hi ha tags de veu, usar veu per defecte
            audio_data = await self._synthesize_with_voice(text, config.default_voice, context)
            audio_segments.append({
                "text": text,
                "voice_label": "default",
                "voice_config": config.default_voice.dict(),
                "audio_base64": audio_data
            })
        else:
            # Processar cada segment
            last_end = 0
            
            for voice_label, voice_text in matches:
                # Processar text abans del tag
                if last_end > 0:
                    before_text = text[last_end:text.find(f'<{voice_label}>')]
                    if before_text.strip():
                        audio_data = await self._synthesize_with_voice(before_text, config.default_voice, context)
                        audio_segments.append({
                            "text": before_text,
                            "voice_label": "default",
                            "voice_config": config.default_voice.dict(),
                            "audio_base64": audio_data
                        })
                
                # Processar text del tag
                voice_config = self._get_voice_config(config, voice_label)
                if voice_config:
                    audio_data = await self._synthesize_with_voice(voice_text, voice_config, context)
                    audio_segments.append({
                        "text": voice_text,
                        "voice_label": voice_label,
                        "voice_config": voice_config.dict(),
                        "audio_base64": audio_data
                    })
                else:
                    # Usar veu per defecte si no es troba la veu
                    audio_data = await self._synthesize_with_voice(voice_text, config.default_voice, context)
                    audio_segments.append({
                        "text": voice_text,
                        "voice_label": "default",
                        "voice_config": config.default_voice.dict(),
                        "audio_base64": audio_data
                    })
                
                last_end = text.find(f'</{voice_label}>') + len(f'</{voice_label}>')
            
            # Processar text després de l'últim tag
            if last_end < len(text):
                after_text = text[last_end:]
                if after_text.strip():
                    audio_data = await self._synthesize_with_voice(after_text, config.default_voice, context)
                    audio_segments.append({
                        "text": after_text,
                        "voice_label": "default",
                        "voice_config": config.default_voice.dict(),
                        "audio_base64": audio_data
                    })
        
        return audio_segments
    
    def _get_voice_config(self, config: MultiVoiceConfig, voice_label: str) -> Optional[VoiceConfiguration]:
        """Obtenir configuració de veu per label"""
        for voice in config.supported_voices:
            if voice.label == voice_label and voice.enabled:
                return voice
        return None
    
    async def _synthesize_with_voice(self, text: str, voice_config: VoiceConfiguration, context: Dict[str, Any]) -> str:
        """Sintetitzar text amb veu específica"""
        try:
            if voice_config.voice_system == VoiceSystem.EDGE_TTS:
                return await self._synthesize_edge_tts(text, voice_config, context)
            elif voice_config.voice_system == VoiceSystem.CATALAN:
                return await self._synthesize_catalan(text, voice_config, context)
            elif voice_config.voice_system == VoiceSystem.ALIA:
                return await self._synthesize_alia(text, voice_config, context)
            else:
                raise ValueError(f"Sistema de veu {voice_config.voice_system} no suportat")
                
        except Exception as e:
            logger.error(f"Error sintetitzant amb veu {voice_config.label}: {e}")
            return ""
    
    async def _synthesize_edge_tts(self, text: str, voice_config: VoiceConfiguration, context: Dict[str, Any]) -> str:
        """Sintetitzar amb Edge-TTS"""
        try:
            import edge_tts
            import base64
            import tempfile
            
            communicate = edge_tts.Communicate(text, voice_config.voice_id)
            
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                temp_path = tmp_file.name
            
            await communicate.save(temp_path)
            
            with open(temp_path, "rb") as f:
                audio_data = f.read()
            
            audio_base64 = base64.b64encode(audio_data).decode()
            
            # Netejar fitxer temporal
            import os
            os.unlink(temp_path)
            
            return audio_base64
            
        except Exception as e:
            logger.error(f"Error sintetitzant Edge-TTS: {e}")
            return ""
    
    async def _synthesize_catalan(self, text: str, voice_config: VoiceConfiguration, context: Dict[str, Any]) -> str:
        """Sintetitzar amb sistema català"""
        try:
            # TODO: Implementar integració amb sistema català
            logger.warning("Sistema català no implementat encara")
            return ""
            
        except Exception as e:
            logger.error(f"Error sintetitzant català: {e}")
            return ""
    
    async def _synthesize_alia(self, text: str, voice_config: VoiceConfiguration, context: Dict[str, Any]) -> str:
        """Sintetitzar amb ALIA"""
        try:
            # TODO: Implementar integració amb ALIA
            logger.warning("Sistema ALIA no implementat encara")
            return ""
            
        except Exception as e:
            logger.error(f"Error sintetitzant ALIA: {e}")
            return ""
    
    async def _combine_audio_segments(self, audio_segments: List[Dict[str, Any]]) -> str:
        """Combinar segments d'àudio"""
        try:
            if not audio_segments:
                return ""
            
            if len(audio_segments) == 1:
                return audio_segments[0]["audio_base64"]
            
            # TODO: Implementar combinació d'àudio
            # Per ara, retornar el primer segment
            return audio_segments[0]["audio_base64"]
            
        except Exception as e:
            logger.error(f"Error combinant segments d'àudio: {e}")
            return ""
    
    async def _create_basic_config(self, agent_id: str):
        """Crear configuració bàsica per agent"""
        basic_config = MultiVoiceConfig(
            agent_id=agent_id,
            default_voice=VoiceConfiguration(
                label="default",
                voice_system=VoiceSystem.EDGE_TTS,
                voice_id="es-ES-ElviraNeural",
                model_family=VoiceModel.SAME_AS_AGENT,
                language="es",
                description="Veu per defecte",
                enabled=True
            ),
            supported_voices=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        voice_configs[agent_id] = basic_config.dict()
    
    def get_voice_config(self, agent_id: str) -> Optional[MultiVoiceConfig]:
        """Obtenir configuració de veu per agent"""
        if agent_id in voice_configs:
            return MultiVoiceConfig(**voice_configs[agent_id])
        return None
    
    def get_all_voice_configs(self) -> List[MultiVoiceConfig]:
        """Obtenir totes les configuracions de veu"""
        return [MultiVoiceConfig(**config) for config in voice_configs.values()]

# Instància global
voice_config_engine = VoiceConfigEngine()

# Endpoints
@router.get("/agent/{agent_id}")
async def get_agent_voice_config(agent_id: str):
    """Obtenir configuració de veu d'un agent"""
    try:
        config = voice_config_engine.get_voice_config(agent_id)
        
        if config:
            return {
                "success": True,
                "config": config.dict()
            }
        else:
            # Retornar configuració per defecte
            default_config = voice_config_engine.get_voice_config("default")
            return {
                "success": True,
                "config": default_config.dict() if default_config else None,
                "message": "Usant configuració per defecte"
            }
        
    except Exception as e:
        logger.error(f"Error obtenint configuració de veu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/{agent_id}")
async def create_agent_voice_config(agent_id: str, config: MultiVoiceConfig):
    """Crear configuració de veu per agent"""
    try:
        config.agent_id = agent_id
        success = await voice_config_engine.create_voice_config(config)
        
        if success:
            return {
                "success": True,
                "message": f"Configuració de veu creada per agent {agent_id}",
                "config": config.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant configuració de veu")
        
    except Exception as e:
        logger.error(f"Error creant configuració de veu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/{agent_id}/voices")
async def add_voice_to_agent(agent_id: str, voice: VoiceConfiguration):
    """Afegir veu a agent"""
    try:
        success = await voice_config_engine.add_voice_to_agent(agent_id, voice)
        
        if success:
            return {
                "success": True,
                "message": f"Veu '{voice.label}' afegida a agent {agent_id}",
                "voice": voice.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error afegint veu")
        
    except Exception as e:
        logger.error(f"Error afegint veu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/agent/{agent_id}/voices/{voice_label}")
async def remove_voice_from_agent(agent_id: str, voice_label: str):
    """Eliminar veu de agent"""
    try:
        success = await voice_config_engine.remove_voice_from_agent(agent_id, voice_label)
        
        if success:
            return {
                "success": True,
                "message": f"Veu '{voice_label}' eliminada de agent {agent_id}"
            }
        else:
            raise HTTPException(status_code=404, detail="Veu no trobada")
        
    except Exception as e:
        logger.error(f"Error eliminant veu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/switch-voices")
async def switch_voices(request: VoiceSwitchRequest):
    """Canviar veus en text"""
    try:
        response = await voice_config_engine.switch_voices(request)
        
        return {
            "success": response.success,
            "audio_segments": response.audio_segments,
            "total_audio_base64": response.total_audio_base64,
            "voice_switches": response.voice_switches,
            "error": response.error
        }
        
    except Exception as e:
        logger.error(f"Error canviant veus: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available-voices")
async def get_available_voices():
    """Obtenir veus disponibles per sistema"""
    try:
        # Obtenir veus Edge-TTS
        edge_voices = []
        try:
            import edge_tts
            all_voices = await edge_tts.list_voices()
            edge_voices = [
                {
                    "id": voice["ShortName"],
                    "name": voice["DisplayName"],
                    "language": voice["Locale"].split("-")[0],
                    "locale": voice["Locale"],
                    "gender": voice["Gender"],
                    "system": "edge-tts"
                }
                for voice in all_voices[:50]  # Limitar per rendiment
            ]
        except Exception as e:
            logger.warning(f"Error obtenint veus Edge-TTS: {e}")
        
        # Veus catalanes
        catalan_voices = [
            {
                "id": "senyor_catala_1",
                "name": "Senyor Català Hiperrealista 1",
                "language": "ca",
                "locale": "ca-ES",
                "gender": "male",
                "system": "catalan"
            },
            {
                "id": "dona_catalana",
                "name": "Dona Catalana Hiperrealista",
                "language": "ca",
                "locale": "ca-ES",
                "gender": "female",
                "system": "catalan"
            }
        ]
        
        # Veus ALIA
        alia_voices = [
            {
                "id": "ca-ES-AlbaNeural",
                "name": "Alba Premium (Català)",
                "language": "ca",
                "locale": "ca-ES",
                "gender": "female",
                "system": "alia"
            },
            {
                "id": "es-ES-AlvaroNeural",
                "name": "Álvaro Premium (Español)",
                "language": "es",
                "locale": "es-ES",
                "gender": "male",
                "system": "alia"
            }
        ]
        
        return {
            "success": True,
            "voices": {
                "edge-tts": edge_voices,
                "catalan": catalan_voices,
                "alia": alia_voices
            },
            "total": len(edge_voices) + len(catalan_voices) + len(alia_voices)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint veus disponibles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def voice_config_health():
    """Health check del sistema de configuració de veu"""
    return {
        "status": "ok",
        "message": "Sistema de configuració de veu funcionant",
        "stats": {
            "total_configs": len(voice_configs),
            "total_voices": sum(len(config.get("supported_voices", [])) for config in voice_configs.values())
        }
    }








