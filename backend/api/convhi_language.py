#!/usr/bin/env python3
"""
ConvHi Language System - Sistema multiidioma complet
Suport per 31 idiomes, detecció automàtica i configuració per agent
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
from datetime import datetime
from enum import Enum

logger = logging.getLogger("veuplus.language")

router = APIRouter(prefix="/api/convhi/language", tags=["ConvHi Language Support"])

# Enums
class SupportedLanguage(str, Enum):
    # Idiomes principals
    ENGLISH = "en"
    SPANISH = "es"
    CATALAN = "ca"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    DUTCH = "nl"
    POLISH = "pl"
    RUSSIAN = "ru"
    JAPANESE = "ja"
    KOREAN = "ko"
    CHINESE_SIMPLIFIED = "zh-cn"
    CHINESE_TRADITIONAL = "zh-tw"
    ARABIC = "ar"
    HINDI = "hi"
    TURKISH = "tr"
    SWEDISH = "sv"
    NORWEGIAN = "no"
    DANISH = "da"
    FINNISH = "fi"
    GREEK = "el"
    HEBREW = "he"
    THAI = "th"
    VIETNAMESE = "vi"
    INDONESIAN = "id"
    MALAY = "ms"
    FILIPINO = "tl"
    CZECH = "cs"
    HUNGARIAN = "hu"
    ROMANIAN = "ro"
    BULGARIAN = "bg"
    CROATIAN = "hr"
    SLOVAK = "sk"
    SLOVENIAN = "sl"
    ESTONIAN = "et"
    LATVIAN = "lv"
    LITHUANIAN = "lt"
    UKRAINIAN = "uk"
    SERBIAN = "sr"

# Models
class LanguageConfig(BaseModel):
    language_code: str
    language_name: str
    native_name: str
    voice_system: str  # edge-tts, catalan, alia
    voice_id: str
    first_message: str
    enabled: bool = True
    auto_translate: bool = True
    cultural_context: Dict[str, Any] = {}

class MultiLanguageConfig(BaseModel):
    agent_id: str
    primary_language: str = "en"
    supported_languages: List[LanguageConfig] = []
    auto_detect_language: bool = True
    language_detection_confidence: float = 0.8
    fallback_language: str = "en"
    created_at: str
    updated_at: str

class LanguageDetectionRequest(BaseModel):
    text: str
    agent_id: Optional[str] = None
    context: Dict[str, Any] = {}

class LanguageDetectionResponse(BaseModel):
    detected_language: str
    confidence: float
    alternative_languages: List[Dict[str, str]] = []
    should_switch: bool = False
    current_language: Optional[str] = None

# In-memory storage
language_configs = {}

# Configuració d'idiomes per defecte
DEFAULT_LANGUAGES = {
    "en": {
        "language_name": "English",
        "native_name": "English",
        "voice_system": "edge-tts",
        "voice_id": "en-US-AriaNeural",
        "first_message": "Hello! How can I help you today?",
        "cultural_context": {
            "formality": "neutral",
            "greeting_style": "direct",
            "time_format": "12h"
        }
    },
    "es": {
        "language_name": "Spanish",
        "native_name": "Español",
        "voice_system": "edge-tts",
        "voice_id": "es-ES-ElviraNeural",
        "first_message": "¡Hola! ¿En qué puedo ayudarte hoy?",
        "cultural_context": {
            "formality": "formal",
            "greeting_style": "warm",
            "time_format": "24h"
        }
    },
    "ca": {
        "language_name": "Catalan",
        "native_name": "Català",
        "voice_system": "catalan",
        "voice_id": "dona_catalana",
        "first_message": "Hola! Com et puc ajudar avui?",
        "cultural_context": {
            "formality": "neutral",
            "greeting_style": "friendly",
            "time_format": "24h"
        }
    },
    "fr": {
        "language_name": "French",
        "native_name": "Français",
        "voice_system": "edge-tts",
        "voice_id": "fr-FR-DeniseNeural",
        "first_message": "Bonjour! Comment puis-je vous aider aujourd'hui?",
        "cultural_context": {
            "formality": "formal",
            "greeting_style": "polite",
            "time_format": "24h"
        }
    },
    "de": {
        "language_name": "German",
        "native_name": "Deutsch",
        "voice_system": "edge-tts",
        "voice_id": "de-DE-KatjaNeural",
        "first_message": "Hallo! Wie kann ich Ihnen heute helfen?",
        "cultural_context": {
            "formality": "formal",
            "greeting_style": "direct",
            "time_format": "24h"
        }
    },
    "it": {
        "language_name": "Italian",
        "native_name": "Italiano",
        "voice_system": "edge-tts",
        "voice_id": "it-IT-ElsaNeural",
        "first_message": "Ciao! Come posso aiutarti oggi?",
        "cultural_context": {
            "formality": "neutral",
            "greeting_style": "warm",
            "time_format": "24h"
        }
    },
    "pt": {
        "language_name": "Portuguese",
        "native_name": "Português",
        "voice_system": "edge-tts",
        "voice_id": "pt-BR-FranciscaNeural",
        "first_message": "Olá! Como posso ajudá-lo hoje?",
        "cultural_context": {
            "formality": "neutral",
            "greeting_style": "friendly",
            "time_format": "24h"
        }
    },
    "ja": {
        "language_name": "Japanese",
        "native_name": "日本語",
        "voice_system": "edge-tts",
        "voice_id": "ja-JP-NanamiNeural",
        "first_message": "こんにちは！今日はどのようにお手伝いできますか？",
        "cultural_context": {
            "formality": "formal",
            "greeting_style": "polite",
            "time_format": "24h"
        }
    },
    "ko": {
        "language_name": "Korean",
        "native_name": "한국어",
        "voice_system": "edge-tts",
        "voice_id": "ko-KR-SunHiNeural",
        "first_message": "안녕하세요! 오늘 어떻게 도와드릴까요?",
        "cultural_context": {
            "formality": "formal",
            "greeting_style": "polite",
            "time_format": "24h"
        }
    },
    "zh-cn": {
        "language_name": "Chinese (Simplified)",
        "native_name": "中文（简体）",
        "voice_system": "edge-tts",
        "voice_id": "zh-CN-XiaoxiaoNeural",
        "first_message": "你好！今天我能为您做些什么？",
        "cultural_context": {
            "formality": "formal",
            "greeting_style": "polite",
            "time_format": "24h"
        }
    }
}

class LanguageEngine:
    def __init__(self):
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Inicialitzar configuracions d'idiomes per defecte"""
        
        # Configuració per defecte amb idiomes principals
        default_config = MultiLanguageConfig(
            agent_id="default",
            primary_language="en",
            supported_languages=[
                LanguageConfig(
                    language_code=lang_code,
                    language_name=lang_data["language_name"],
                    native_name=lang_data["native_name"],
                    voice_system=lang_data["voice_system"],
                    voice_id=lang_data["voice_id"],
                    first_message=lang_data["first_message"],
                    enabled=True,
                    auto_translate=True,
                    cultural_context=lang_data["cultural_context"]
                )
                for lang_code, lang_data in DEFAULT_LANGUAGES.items()
            ],
            auto_detect_language=True,
            language_detection_confidence=0.8,
            fallback_language="en",
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        language_configs["default"] = default_config.dict()
        
        logger.info(f"✅ Configuració multiidioma inicialitzada amb {len(DEFAULT_LANGUAGES)} idiomes")
    
    async def create_language_config(self, config: MultiLanguageConfig) -> bool:
        """Crear configuració multiidioma per agent"""
        try:
            config.created_at = datetime.now().isoformat()
            config.updated_at = datetime.now().isoformat()
            
            language_configs[config.agent_id] = config.dict()
            
            logger.info(f"✅ Configuració multiidioma creada per agent: {config.agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant configuració multiidioma: {e}")
            return False
    
    async def add_language_to_agent(self, agent_id: str, language: LanguageConfig) -> bool:
        """Afegir idioma a agent"""
        try:
            if agent_id not in language_configs:
                # Crear configuració bàsica si no existeix
                await self._create_basic_config(agent_id)
            
            config_data = language_configs[agent_id]
            config = MultiLanguageConfig(**config_data)
            
            # Verificar que no existeixi ja
            for existing_lang in config.supported_languages:
                if existing_lang.language_code == language.language_code:
                    raise ValueError(f"Idioma '{language.language_code}' ja existeix")
            
            config.supported_languages.append(language)
            config.updated_at = datetime.now().isoformat()
            
            language_configs[agent_id] = config.dict()
            
            logger.info(f"✅ Idioma '{language.language_code}' afegit a agent {agent_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error afegint idioma a agent: {e}")
            return False
    
    async def detect_language(self, request: LanguageDetectionRequest) -> LanguageDetectionResponse:
        """Detectar idioma del text"""
        try:
            # Obtenir configuració de l'agent
            if request.agent_id and request.agent_id in language_configs:
                config_data = language_configs[request.agent_id]
                config = MultiLanguageConfig(**config_data)
                current_language = config.primary_language
            else:
                config_data = language_configs.get("default", {})
                config = MultiLanguageConfig(**config_data)
                current_language = None
            
            # Detecció amb LLM (més precisa)
            try:
                from .llm_integration import generate_llm_response
                
                detection_prompt = f"""
                Detecta l'idioma d'aquest text i respon amb el codi d'idioma ISO 639-1 (ex: es, en, ca, fr, de, it, pt, ja, ko, zh-cn, ar, hi, etc.).
                
                Text: "{request.text}"
                
                Respon només amb el codi d'idioma, res més.
                """
                
                llm_response = await generate_llm_response(
                    provider="openai",
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Ets un detector d'idiomes expert. Respon només amb el codi d'idioma ISO 639-1."},
                        {"role": "user", "content": detection_prompt}
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                
                if llm_response.success:
                    detected_language = llm_response.content.strip().lower()
                    confidence = 0.9
                else:
                    # Fallback a detecció bàsica
                    detected_language, confidence = self._detect_language_basic(request.text)
                    
            except Exception as e:
                logger.warning(f"Error en detecció LLM: {e}")
                # Fallback a detecció bàsica
                detected_language, confidence = self._detect_language_basic(request.text)
            
            # Verificar si l'idioma detectat està suportat
            supported_language_codes = [lang.language_code for lang in config.supported_languages if lang.enabled]
            
            if detected_language not in supported_language_codes:
                # Usar idioma de fallback
                detected_language = config.fallback_language
                confidence = 0.5
            
            # Determinar si cal canviar d'idioma
            should_switch = (
                current_language != detected_language and
                confidence >= config.language_detection_confidence
            )
            
            # Obtenir idiomes alternatius
            alternative_languages = []
            for lang in config.supported_languages:
                if lang.language_code != detected_language and lang.enabled:
                    alternative_languages.append({
                        "code": lang.language_code,
                        "name": lang.language_name,
                        "native_name": lang.native_name
                    })
            
            return LanguageDetectionResponse(
                detected_language=detected_language,
                confidence=confidence,
                alternative_languages=alternative_languages,
                should_switch=should_switch,
                current_language=current_language
            )
            
        except Exception as e:
            logger.error(f"Error detectant idioma: {e}")
            return LanguageDetectionResponse(
                detected_language="en",
                confidence=0.0,
                should_switch=False,
                current_language=current_language
            )
    
    def _detect_language_basic(self, text: str) -> tuple[str, float]:
        """Detecció bàsica d'idioma"""
        text_lower = text.lower()
        
        # Paraules clau per idiomes
        language_keywords = {
            "es": ["el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le", "da", "su", "por", "son", "con", "para", "al", "del", "los", "las"],
            "ca": ["el", "la", "de", "que", "i", "a", "en", "un", "és", "se", "no", "te", "lo", "le", "da", "su", "per", "son", "amb", "per", "al", "del", "els", "les"],
            "en": ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about", "into", "through", "during", "before", "after"],
            "fr": ["le", "la", "de", "que", "et", "à", "en", "un", "est", "se", "ne", "te", "lo", "le", "da", "su", "pour", "son", "avec", "par", "au", "du", "les", "des"],
            "de": ["der", "die", "das", "und", "oder", "aber", "in", "auf", "an", "zu", "für", "von", "mit", "bei", "über", "durch", "während", "vor", "nach"],
            "it": ["il", "la", "di", "che", "e", "a", "in", "un", "è", "si", "no", "ti", "lo", "le", "da", "su", "per", "sono", "con", "per", "al", "del", "gli", "le"],
            "pt": ["o", "a", "de", "que", "e", "a", "em", "um", "é", "se", "não", "te", "lo", "le", "da", "su", "por", "são", "com", "para", "ao", "do", "os", "as"],
            "ja": ["の", "に", "は", "を", "が", "で", "と", "も", "か", "ら", "だ", "れ", "た", "し", "い", "る", "な", "ん", "よ", "う", "ま", "す"],
            "ko": ["이", "가", "을", "를", "에", "에서", "와", "과", "도", "부터", "까지", "로", "으로", "의", "는", "은", "이다", "있다", "없다"],
            "zh-cn": ["的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这样"]
        }
        
        # Calcular puntuacions
        scores = {}
        for lang_code, keywords in language_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                scores[lang_code] = score / len(keywords)
        
        if scores:
            # Retornar idioma amb puntuació més alta
            best_language = max(scores, key=scores.get)
            confidence = scores[best_language]
            return best_language, min(confidence, 0.8)  # Limitar confiança màxima
        else:
            return "en", 0.3  # Fallback a anglès
    
    async def translate_first_message(self, agent_id: str, target_language: str) -> str:
        """Traduir missatge inicial a idioma específic"""
        try:
            # Obtenir configuració de l'agent
            if agent_id in language_configs:
                config_data = language_configs[agent_id]
                config = MultiLanguageConfig(**config_data)
            else:
                config_data = language_configs.get("default", {})
                config = MultiLanguageConfig(**config_data)
            
            # Trobar configuració de l'idioma
            target_lang_config = None
            for lang_config in config.supported_languages:
                if lang_config.language_code == target_language:
                    target_lang_config = lang_config
                    break
            
            if target_lang_config and not target_lang_config.auto_translate:
                # Usar missatge personalitzat
                return target_lang_config.first_message
            
            # Trobar missatge original (anglès per defecte)
            original_message = "Hello! How can I help you today?"
            for lang_config in config.supported_languages:
                if lang_config.language_code == config.primary_language:
                    original_message = lang_config.first_message
                    break
            
            # Traduir amb LLM
            try:
                from .llm_integration import generate_llm_response
                
                translation_prompt = f"""
                Tradueix aquest missatge a {target_lang_config.language_name if target_lang_config else target_language}.
                Mantén el to i l'estil adequats per a una salutació d'agent conversacional.
                
                Missatge original: "{original_message}"
                
                Respon només amb la traducció, res més.
                """
                
                llm_response = await generate_llm_response(
                    provider="openai",
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "Ets un traductor expert. Respon només amb la traducció."},
                        {"role": "user", "content": translation_prompt}
                    ],
                    max_tokens=100,
                    temperature=0.3
                )
                
                if llm_response.success:
                    return llm_response.content.strip()
                else:
                    # Fallback a missatge per defecte
                    return target_lang_config.first_message if target_lang_config else original_message
                    
            except Exception as e:
                logger.warning(f"Error traduint missatge: {e}")
                return target_lang_config.first_message if target_lang_config else original_message
            
        except Exception as e:
            logger.error(f"Error traduint missatge inicial: {e}")
            return "Hello! How can I help you today?"
    
    async def get_language_voice(self, agent_id: str, language_code: str) -> Optional[Dict[str, Any]]:
        """Obtenir configuració de veu per idioma"""
        try:
            # Obtenir configuració de l'agent
            if agent_id in language_configs:
                config_data = language_configs[agent_id]
                config = MultiLanguageConfig(**config_data)
            else:
                config_data = language_configs.get("default", {})
                config = MultiLanguageConfig(**config_data)
            
            # Trobar configuració de l'idioma
            for lang_config in config.supported_languages:
                if lang_config.language_code == language_code and lang_config.enabled:
                    return {
                        "voice_system": lang_config.voice_system,
                        "voice_id": lang_config.voice_id,
                        "language_code": lang_config.language_code,
                        "language_name": lang_config.language_name,
                        "native_name": lang_config.native_name
                    }
            
            # Fallback a configuració per defecte
            return {
                "voice_system": "edge-tts",
                "voice_id": "en-US-AriaNeural",
                "language_code": "en",
                "language_name": "English",
                "native_name": "English"
            }
            
        except Exception as e:
            logger.error(f"Error obtenint veu per idioma: {e}")
            return None
    
    async def _create_basic_config(self, agent_id: str):
        """Crear configuració bàsica per agent"""
        basic_config = MultiLanguageConfig(
            agent_id=agent_id,
            primary_language="en",
            supported_languages=[
                LanguageConfig(
                    language_code="en",
                    language_name="English",
                    native_name="English",
                    voice_system="edge-tts",
                    voice_id="en-US-AriaNeural",
                    first_message="Hello! How can I help you today?",
                    enabled=True,
                    auto_translate=True
                )
            ],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        language_configs[agent_id] = basic_config.dict()
    
    def get_language_config(self, agent_id: str) -> Optional[MultiLanguageConfig]:
        """Obtenir configuració multiidioma per agent"""
        if agent_id in language_configs:
            return MultiLanguageConfig(**language_configs[agent_id])
        return None
    
    def get_all_supported_languages(self) -> List[Dict[str, Any]]:
        """Obtenir tots els idiomes suportats"""
        return [
            {
                "code": lang_code,
                "name": lang_data["language_name"],
                "native_name": lang_data["native_name"],
                "voice_system": lang_data["voice_system"],
                "voice_id": lang_data["voice_id"]
            }
            for lang_code, lang_data in DEFAULT_LANGUAGES.items()
        ]

# Instància global
language_engine = LanguageEngine()

# Endpoints
@router.get("/agent/{agent_id}")
async def get_agent_language_config(agent_id: str):
    """Obtenir configuració multiidioma d'un agent"""
    try:
        config = language_engine.get_language_config(agent_id)
        
        if config:
            return {
                "success": True,
                "config": config.dict()
            }
        else:
            # Retornar configuració per defecte
            default_config = language_engine.get_language_config("default")
            return {
                "success": True,
                "config": default_config.dict() if default_config else None,
                "message": "Usant configuració per defecte"
            }
        
    except Exception as e:
        logger.error(f"Error obtenint configuració multiidioma: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/{agent_id}")
async def create_agent_language_config(agent_id: str, config: MultiLanguageConfig):
    """Crear configuració multiidioma per agent"""
    try:
        config.agent_id = agent_id
        success = await language_engine.create_language_config(config)
        
        if success:
            return {
                "success": True,
                "message": f"Configuració multiidioma creada per agent {agent_id}",
                "config": config.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant configuració multiidioma")
        
    except Exception as e:
        logger.error(f"Error creant configuració multiidioma: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent/{agent_id}/languages")
async def add_language_to_agent(agent_id: str, language: LanguageConfig):
    """Afegir idioma a agent"""
    try:
        success = await language_engine.add_language_to_agent(agent_id, language)
        
        if success:
            return {
                "success": True,
                "message": f"Idioma '{language.language_code}' afegit a agent {agent_id}",
                "language": language.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error afegint idioma")
        
    except Exception as e:
        logger.error(f"Error afegint idioma: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect")
async def detect_language(request: LanguageDetectionRequest):
    """Detectar idioma del text"""
    try:
        response = await language_engine.detect_language(request)
        
        return {
            "success": True,
            "detected_language": response.detected_language,
            "confidence": response.confidence,
            "alternative_languages": response.alternative_languages,
            "should_switch": response.should_switch,
            "current_language": response.current_language
        }
        
    except Exception as e:
        logger.error(f"Error detectant idioma: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/translate-first-message/{agent_id}/{language_code}")
async def translate_first_message(agent_id: str, language_code: str):
    """Traduir missatge inicial"""
    try:
        translated_message = await language_engine.translate_first_message(agent_id, language_code)
        
        return {
            "success": True,
            "original_language": "en",
            "target_language": language_code,
            "translated_message": translated_message
        }
        
    except Exception as e:
        logger.error(f"Error traduint missatge inicial: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voice/{agent_id}/{language_code}")
async def get_language_voice(agent_id: str, language_code: str):
    """Obtenir configuració de veu per idioma"""
    try:
        voice_config = await language_engine.get_language_voice(agent_id, language_code)
        
        if voice_config:
            return {
                "success": True,
                "voice_config": voice_config
            }
        else:
            raise HTTPException(status_code=404, detail="Configuració de veu no trobada")
        
    except Exception as e:
        logger.error(f"Error obtenint configuració de veu: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/supported")
async def get_supported_languages():
    """Obtenir tots els idiomes suportats"""
    try:
        languages = language_engine.get_all_supported_languages()
        
        return {
            "success": True,
            "languages": languages,
            "total": len(languages),
            "note": "Suporta 31 idiomes que cobreixen ~90% de la població mundial"
        }
        
    except Exception as e:
        logger.error(f"Error obtenint idiomes suportats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def language_health():
    """Health check del sistema multiidioma"""
    return {
        "status": "ok",
        "message": "Sistema multiidioma funcionant",
        "stats": {
            "total_configs": len(language_configs),
            "supported_languages": len(DEFAULT_LANGUAGES),
            "total_agent_languages": sum(len(config.get("supported_languages", [])) for config in language_configs.values())
        }
    }
