#!/usr/bin/env python3
"""
LLM Configuration System - Sistema complet de configuració d'APIs LLM
Permet configurar qualsevol API LLM de manera dinàmica
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Union
import logging
import json
import os
from datetime import datetime
import asyncio
import aiohttp

logger = logging.getLogger("veuplus.llm_config")

router = APIRouter(prefix="/api/llm-config", tags=["LLM Configuration"])

# Models
class LLMProviderConfig(BaseModel):
    id: str
    name: str
    provider_type: str  # openai, gemini, claude, alia, ollama, vllm, custom
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = []
    default_model: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    enabled: bool = True
    config: Dict[str, Any] = {}
    created_at: str
    updated_at: str

class LLMTestRequest(BaseModel):
    provider_id: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    test_message: str = "Hola! Com estàs?"

class LLMTestResponse(BaseModel):
    success: bool
    provider_id: str
    model: str
    response: Optional[str] = None
    error: Optional[str] = None
    response_time: float
    tokens_used: Optional[int] = None

# In-memory storage (en producció usar base de dades)
llm_configs = {}

class LLMConfigManager:
    def __init__(self):
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Inicialitzar configuracions per defecte"""
        
        # OpenAI
        openai_config = LLMProviderConfig(
            id="openai_default",
            name="OpenAI Default",
            provider_type="openai",
            api_key=os.getenv("OPENAI_API_KEY", ""),
            models=[
                "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4-turbo", 
                "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-3.5-turbo"
            ],
            default_model="gpt-4o-mini",
            max_tokens=4096,
            temperature=0.7,
            enabled=bool(os.getenv("OPENAI_API_KEY")),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Google Gemini
        gemini_config = LLMProviderConfig(
            id="gemini_default",
            name="Google Gemini Default",
            provider_type="gemini",
            api_key=os.getenv("GEMINI_API_KEY", ""),
            models=[
                "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash",
                "gemini-2.0-flash-lite", "gemini-2.5-flash"
            ],
            default_model="gemini-1.5-flash",
            max_tokens=8192,
            temperature=0.7,
            enabled=bool(os.getenv("GEMINI_API_KEY")),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Anthropic Claude
        claude_config = LLMProviderConfig(
            id="claude_default",
            name="Anthropic Claude Default",
            provider_type="claude",
            api_key=os.getenv("CLAUDE_API_KEY", ""),
            models=[
                "claude-sonnet-4", "claude-3-7-sonnet", "claude-3-5-sonnet",
                "claude-3-5-sonnet-v1", "claude-3-0-haiku"
            ],
            default_model="claude-3-5-sonnet",
            max_tokens=4096,
            temperature=0.7,
            enabled=bool(os.getenv("CLAUDE_API_KEY")),
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # ALIA Kit
        alia_config = LLMProviderConfig(
            id="alia_default",
            name="ALIA Kit BSC",
            provider_type="alia",
            base_url="http://localhost:8001",
            models=[
                "alia-llm-multilingual", "alia-llm-catalan", "alia-llm-spanish"
            ],
            default_model="alia-llm-multilingual",
            max_tokens=2048,
            temperature=0.7,
            enabled=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Ollama
        ollama_config = LLMProviderConfig(
            id="ollama_default",
            name="Ollama Local",
            provider_type="ollama",
            base_url="http://localhost:11434",
            models=[
                "llama3.1", "llama3.1:8b", "llama3.1:70b",
                "mistral", "codellama", "phi3", "qwen2.5"
            ],
            default_model="llama3.1:8b",
            max_tokens=2048,
            temperature=0.7,
            enabled=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # vLLM
        vllm_config = LLMProviderConfig(
            id="vllm_default",
            name="vLLM Local",
            provider_type="vllm",
            base_url="http://localhost:8000",
            models=[
                "meta-llama/Llama-3.1-8B-Instruct",
                "microsoft/Phi-3-mini-4k-instruct",
                "Qwen/Qwen2.5-7B-Instruct"
            ],
            default_model="meta-llama/Llama-3.1-8B-Instruct",
            max_tokens=2048,
            temperature=0.7,
            enabled=True,
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        # Guardar configuracions
        configs = [openai_config, gemini_config, claude_config, alia_config, ollama_config, vllm_config]
        for config in configs:
            llm_configs[config.id] = config.dict()
        
        logger.info(f"✅ {len(configs)} configuracions LLM inicialitzades")
    
    async def create_custom_provider(self, config: LLMProviderConfig) -> bool:
        """Crear proveïdor personalitzat"""
        try:
            config.created_at = datetime.now().isoformat()
            config.updated_at = datetime.now().isoformat()
            
            llm_configs[config.id] = config.dict()
            
            logger.info(f"✅ Proveïdor LLM personalitzat creat: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error creant proveïdor personalitzat: {e}")
            return False
    
    async def update_provider(self, provider_id: str, updates: Dict[str, Any]) -> bool:
        """Actualitzar proveïdor"""
        try:
            if provider_id not in llm_configs:
                return False
            
            config = llm_configs[provider_id]
            config.update(updates)
            config["updated_at"] = datetime.now().isoformat()
            
            llm_configs[provider_id] = config
            
            logger.info(f"✅ Proveïdor LLM actualitzat: {provider_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualitzant proveïdor: {e}")
            return False
    
    async def test_provider(self, request: LLMTestRequest) -> LLMTestResponse:
        """Provar connexió amb proveïdor"""
        start_time = datetime.now()
        
        try:
            # Obtenir configuració
            if request.provider_id not in llm_configs:
                raise ValueError(f"Proveïdor {request.provider_id} no trobat")
            
            config_data = llm_configs[request.provider_id]
            config = LLMProviderConfig(**config_data)
            
            # Usar API key i base_url de la petició si es proporcionen
            api_key = request.api_key or config.api_key
            base_url = request.base_url or config.base_url
            
            if not api_key and config.provider_type in ["openai", "gemini", "claude"]:
                raise ValueError(f"API key requerida per {config.provider_type}")
            
            # Generar resposta segons el tipus
            response_text = await self._test_provider_connection(
                config.provider_type, request.model, api_key, base_url, request.test_message
            )
            
            response_time = (datetime.now() - start_time).total_seconds()
            
            return LLMTestResponse(
                success=True,
                provider_id=request.provider_id,
                model=request.model,
                response=response_text,
                response_time=response_time
            )
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error provant proveïdor {request.provider_id}: {e}")
            
            return LLMTestResponse(
                success=False,
                provider_id=request.provider_id,
                model=request.model,
                error=str(e),
                response_time=response_time
            )
    
    async def _test_provider_connection(self, provider_type: str, model: str, api_key: str, base_url: str, test_message: str) -> str:
        """Provar connexió amb proveïdor específic"""
        async with aiohttp.ClientSession() as session:
            
            if provider_type == "openai":
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": test_message}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
                
                async with session.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_data = await response.json()
                        raise Exception(f"OpenAI API error: {error_data}")
            
            elif provider_type == "gemini":
                # Convertir a format Gemini
                payload = {
                    "contents": [{
                        "role": "user",
                        "parts": [{"text": test_message}]
                    }],
                    "generationConfig": {
                        "maxOutputTokens": 50,
                        "temperature": 0.7
                    }
                }
                
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
                
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        error_data = await response.json()
                        raise Exception(f"Gemini API error: {error_data}")
            
            elif provider_type == "claude":
                headers = {
                    "x-api-key": api_key,
                    "Content-Type": "application/json",
                    "anthropic-version": "2023-06-01"
                }
                
                payload = {
                    "model": model,
                    "max_tokens": 50,
                    "temperature": 0.7,
                    "messages": [
                        {"role": "user", "content": test_message}
                    ]
                }
                
                async with session.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["content"][0]["text"]
                    else:
                        error_data = await response.json()
                        raise Exception(f"Claude API error: {error_data}")
            
            elif provider_type == "ollama":
                # Format Ollama
                payload = {
                    "model": model,
                    "prompt": f"User: {test_message}\n\nAssistant:",
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "num_predict": 50
                    }
                }
                
                url = f"{base_url}/api/generate"
                
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        error_data = await response.text()
                        raise Exception(f"Ollama API error: {error_data}")
            
            elif provider_type == "vllm":
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": test_message}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7,
                    "stream": False
                }
                
                url = f"{base_url}/v1/chat/completions"
                
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_data = await response.text()
                        raise Exception(f"vLLM API error: {error_data}")
            
            elif provider_type == "alia":
                headers = {"Content-Type": "application/json"}
                
                payload = {
                    "model": model,
                    "messages": [
                        {"role": "user", "content": test_message}
                    ],
                    "max_tokens": 50,
                    "temperature": 0.7
                }
                
                url = f"{base_url}/api/llm/generate"
                
                async with session.post(
                    url,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("response", "")
                    else:
                        error_data = await response.text()
                        raise Exception(f"ALIA API error: {error_data}")
            
            else:
                raise ValueError(f"Tipus de proveïdor {provider_type} no suportat")
    
    def get_all_providers(self) -> List[LLMProviderConfig]:
        """Obtenir tots els proveïdors"""
        return [LLMProviderConfig(**config) for config in llm_configs.values()]
    
    def get_provider(self, provider_id: str) -> Optional[LLMProviderConfig]:
        """Obtenir proveïdor específic"""
        if provider_id in llm_configs:
            return LLMProviderConfig(**llm_configs[provider_id])
        return None
    
    def delete_provider(self, provider_id: str) -> bool:
        """Eliminar proveïdor"""
        try:
            if provider_id in llm_configs:
                del llm_configs[provider_id]
                logger.info(f"✅ Proveïdor LLM eliminat: {provider_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminant proveïdor: {e}")
            return False

# Instància global
llm_config_manager = LLMConfigManager()

# Endpoints
@router.get("/providers")
async def get_all_providers():
    """Obtenir tots els proveïdors LLM"""
    try:
        providers = llm_config_manager.get_all_providers()
        
        return {
            "success": True,
            "providers": [provider.dict() for provider in providers],
            "total": len(providers)
        }
        
    except Exception as e:
        logger.error(f"Error obtenint proveïdors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/{provider_id}")
async def get_provider(provider_id: str):
    """Obtenir proveïdor específic"""
    try:
        provider = llm_config_manager.get_provider(provider_id)
        
        if provider:
            return {
                "success": True,
                "provider": provider.dict()
            }
        else:
            raise HTTPException(status_code=404, detail="Proveïdor no trobat")
        
    except Exception as e:
        logger.error(f"Error obtenint proveïdor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/providers")
async def create_provider(config: LLMProviderConfig):
    """Crear nou proveïdor LLM"""
    try:
        success = await llm_config_manager.create_custom_provider(config)
        
        if success:
            return {
                "success": True,
                "message": f"Proveïdor {config.name} creat correctament",
                "provider": config.dict()
            }
        else:
            raise HTTPException(status_code=400, detail="Error creant proveïdor")
        
    except Exception as e:
        logger.error(f"Error creant proveïdor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/providers/{provider_id}")
async def update_provider(provider_id: str, updates: Dict[str, Any]):
    """Actualitzar proveïdor"""
    try:
        success = await llm_config_manager.update_provider(provider_id, updates)
        
        if success:
            return {
                "success": True,
                "message": f"Proveïdor {provider_id} actualitzat correctament"
            }
        else:
            raise HTTPException(status_code=404, detail="Proveïdor no trobat")
        
    except Exception as e:
        logger.error(f"Error actualitzant proveïdor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/providers/{provider_id}")
async def delete_provider(provider_id: str):
    """Eliminar proveïdor"""
    try:
        success = llm_config_manager.delete_provider(provider_id)
        
        if success:
            return {
                "success": True,
                "message": f"Proveïdor {provider_id} eliminat correctament"
            }
        else:
            raise HTTPException(status_code=404, detail="Proveïdor no trobat")
        
    except Exception as e:
        logger.error(f"Error eliminant proveïdor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def test_provider(request: LLMTestRequest):
    """Provar connexió amb proveïdor"""
    try:
        result = await llm_config_manager.test_provider(request)
        
        return {
            "success": result.success,
            "provider_id": result.provider_id,
            "model": result.model,
            "response": result.response,
            "error": result.error,
            "response_time": result.response_time,
            "tokens_used": result.tokens_used
        }
        
    except Exception as e:
        logger.error(f"Error provant proveïdor: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def llm_config_health():
    """Health check del sistema de configuració LLM"""
    return {
        "status": "ok",
        "message": "Sistema de configuració LLM funcionant",
        "stats": {
            "total_providers": len(llm_configs),
            "enabled_providers": len([c for c in llm_configs.values() if c.get("enabled", False)])
        }
    }
