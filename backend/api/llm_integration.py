#!/usr/bin/env python3
"""
LLM Integration System - Suport complet per TOTS els LLMs
Integració amb: OpenAI, Gemini, Claude, ALIA, Ollama, vLLM, Custom APIs
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import os
from datetime import datetime

logger = logging.getLogger("veuplus.llm")

class LLMProvider(BaseModel):
    name: str
    provider_type: str  # openai, gemini, claude, alia, ollama, vllm, custom
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    models: List[str] = []
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30
    enabled: bool = True
    config: Optional[Dict[str, Any]] = None

class LLMRequest(BaseModel):
    provider: str
    model: str
    messages: List[Dict[str, str]]
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    custom_params: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    success: bool
    content: str
    provider: str
    model: str
    tokens_used: Optional[int] = None
    response_time: float
    error: Optional[str] = None

class LLMIntegrationSystem:
    def __init__(self):
        self.providers = {}
        self.session = None
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicialitzar tots els proveïdors LLM disponibles"""
        try:
            # Carregar configuracions des del sistema de configuració
            from .llm_config import llm_config_manager
            
            configs = llm_config_manager.get_all_providers()
            
            for config in configs:
                provider = LLMProvider(
                    name=config.name,
                    provider_type=config.provider_type,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    models=config.models,
                    max_tokens=config.max_tokens,
                    temperature=config.temperature,
                    timeout=30,
                    enabled=config.enabled,
                    config=config.config
                )
                
                self.providers[config.id] = provider
            
            logger.info(f"✅ LLM Integration inicialitzat amb {len(self.providers)} proveïdors des de configuració")
            
        except Exception as e:
            logger.warning(f"Error carregant configuracions LLM: {e}")
            # Fallback a configuracions bàsiques
            self._initialize_fallback_providers()
    
    def _initialize_fallback_providers(self):
        """Inicialitzar proveïdors bàsics com a fallback"""
        # OpenAI
        self.providers["openai"] = LLMProvider(
            name="OpenAI",
            provider_type="openai",
            api_key=os.getenv("OPENAI_API_KEY"),
            models=[
                "gpt-4o", "gpt-4o-mini", "gpt-4", "gpt-4-turbo", 
                "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-3.5-turbo"
            ],
            max_tokens=4096,
            temperature=0.7,
            enabled=bool(os.getenv("OPENAI_API_KEY"))
        )
        
        # Google Gemini
        self.providers["gemini"] = LLMProvider(
            name="Google Gemini",
            provider_type="gemini",
            api_key=os.getenv("GEMINI_API_KEY"),
            models=[
                "gemini-1.5-pro", "gemini-1.5-flash", "gemini-2.0-flash",
                "gemini-2.0-flash-lite", "gemini-2.5-flash"
            ],
            max_tokens=8192,
            temperature=0.7,
            enabled=bool(os.getenv("GEMINI_API_KEY"))
        )
        
        logger.info(f"✅ LLM Integration inicialitzat amb {len(self.providers)} proveïdors fallback")
    
    async def get_session(self):
        """Obtenir sessió HTTP reutilitzable"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close_session(self):
        """Tancar sessió HTTP"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generar resposta amb el proveïdor especificat"""
        start_time = datetime.now()
        
        try:
            if request.provider not in self.providers:
                raise ValueError(f"Proveïdor {request.provider} no disponible")
            
            provider = self.providers[request.provider]
            
            if not provider.enabled:
                raise ValueError(f"Proveïdor {request.provider} deshabilitat")
            
            # Generar resposta segons el tipus de proveïdor
            if provider.provider_type == "openai":
                return await self._generate_openai(provider, request, start_time)
            elif provider.provider_type == "gemini":
                return await self._generate_gemini(provider, request, start_time)
            elif provider.provider_type == "claude":
                return await self._generate_claude(provider, request, start_time)
            elif provider.provider_type == "alia":
                return await self._generate_alia(provider, request, start_time)
            elif provider.provider_type == "ollama":
                return await self._generate_ollama(provider, request, start_time)
            elif provider.provider_type == "vllm":
                return await self._generate_vllm(provider, request, start_time)
            elif provider.provider_type == "custom":
                return await self._generate_custom(provider, request, start_time)
            else:
                raise ValueError(f"Tipus de proveïdor {provider.provider_type} no suportat")
                
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Error generant resposta LLM: {e}")
            return LLMResponse(
                success=False,
                content="",
                provider=request.provider,
                model=request.model,
                response_time=response_time,
                error=str(e)
            )
    
    async def _generate_openai(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb OpenAI"""
        session = await self.get_session()
        
        headers = {
            "Authorization": f"Bearer {provider.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature or provider.temperature,
            "max_tokens": request.max_tokens or provider.max_tokens,
            "stream": request.stream
        }
        
        if request.custom_params:
            payload.update(request.custom_params)
        
        async with session.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="openai",
                    model=request.model,
                    tokens_used=tokens_used,
                    response_time=response_time
                )
            else:
                raise Exception(f"OpenAI API error: {data}")
    
    async def _generate_gemini(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb Google Gemini"""
        session = await self.get_session()
        
        # Convertir messages a format Gemini
        contents = []
        for msg in request.messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": request.temperature or provider.temperature,
                "maxOutputTokens": request.max_tokens or provider.max_tokens
            }
        }
        
        if request.custom_params:
            payload["generationConfig"].update(request.custom_params)
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{request.model}:generateContent?key={provider.api_key}"
        
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="gemini",
                    model=request.model,
                    response_time=response_time
                )
            else:
                raise Exception(f"Gemini API error: {data}")
    
    async def _generate_claude(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb Anthropic Claude"""
        session = await self.get_session()
        
        headers = {
            "x-api-key": provider.api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Convertir messages a format Claude
        messages = []
        system_message = ""
        
        for msg in request.messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": request.model,
            "max_tokens": request.max_tokens or provider.max_tokens,
            "temperature": request.temperature or provider.temperature,
            "messages": messages
        }
        
        if system_message:
            payload["system"] = system_message
        
        if request.custom_params:
            payload.update(request.custom_params)
        
        async with session.post(
            "https://api.anthropic.com/v1/messages",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data["content"][0]["text"]
                tokens_used = data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0)
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="claude",
                    model=request.model,
                    tokens_used=tokens_used,
                    response_time=response_time
                )
            else:
                raise Exception(f"Claude API error: {data}")
    
    async def _generate_alia(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb ALIA Kit"""
        session = await self.get_session()
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature or provider.temperature,
            "max_tokens": request.max_tokens or provider.max_tokens
        }
        
        if request.custom_params:
            payload.update(request.custom_params)
        
        url = f"{provider.base_url}/api/llm/generate"
        
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data.get("response", "")
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="alia",
                    model=request.model,
                    response_time=response_time
                )
            else:
                raise Exception(f"ALIA API error: {data}")
    
    async def _generate_ollama(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb Ollama"""
        session = await self.get_session()
        
        # Convertir messages a format Ollama
        prompt = ""
        for msg in request.messages:
            if msg["role"] == "system":
                prompt += f"System: {msg['content']}\n\n"
            elif msg["role"] == "user":
                prompt += f"User: {msg['content']}\n\n"
            elif msg["role"] == "assistant":
                prompt += f"Assistant: {msg['content']}\n\n"
        
        prompt += "Assistant: "
        
        payload = {
            "model": request.model,
            "prompt": prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature or provider.temperature,
                "num_predict": request.max_tokens or provider.max_tokens
            }
        }
        
        if request.custom_params:
            payload["options"].update(request.custom_params)
        
        url = f"{provider.base_url}/api/generate"
        
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data.get("response", "")
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="ollama",
                    model=request.model,
                    response_time=response_time
                )
            else:
                raise Exception(f"Ollama API error: {data}")
    
    async def _generate_vllm(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb vLLM"""
        session = await self.get_session()
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature or provider.temperature,
            "max_tokens": request.max_tokens or provider.max_tokens,
            "stream": request.stream
        }
        
        if request.custom_params:
            payload.update(request.custom_params)
        
        url = f"{provider.base_url}/v1/chat/completions"
        
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data["choices"][0]["message"]["content"]
                tokens_used = data.get("usage", {}).get("total_tokens", 0)
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="vllm",
                    model=request.model,
                    tokens_used=tokens_used,
                    response_time=response_time
                )
            else:
                raise Exception(f"vLLM API error: {data}")
    
    async def _generate_custom(self, provider: LLMProvider, request: LLMRequest, start_time: datetime) -> LLMResponse:
        """Generar resposta amb API personalitzada"""
        session = await self.get_session()
        
        payload = {
            "model": request.model,
            "messages": request.messages,
            "temperature": request.temperature or provider.temperature,
            "max_tokens": request.max_tokens or provider.max_tokens
        }
        
        if request.custom_params:
            payload.update(request.custom_params)
        
        url = f"{provider.base_url}/generate"
        
        async with session.post(
            url,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=provider.timeout)
        ) as response:
            data = await response.json()
            
            if response.status == 200:
                content = data.get("response", data.get("content", ""))
                response_time = (datetime.now() - start_time).total_seconds()
                
                return LLMResponse(
                    success=True,
                    content=content,
                    provider="custom",
                    model=request.model,
                    response_time=response_time
                )
            else:
                raise Exception(f"Custom API error: {data}")
    
    def get_available_providers(self) -> Dict[str, Any]:
        """Obtenir llista de proveïdors disponibles"""
        available = {}
        for name, provider in self.providers.items():
            available[name] = {
                "name": provider.name,
                "enabled": provider.enabled,
                "models": provider.models,
                "max_tokens": provider.max_tokens,
                "temperature": provider.temperature
            }
        return available
    
    def add_custom_provider(self, provider: LLMProvider):
        """Afegir proveïdor personalitzat"""
        self.providers[provider.name.lower()] = provider
        logger.info(f"✅ Proveïdor personalitzat afegit: {provider.name}")
    
    def update_provider_config(self, provider_name: str, config: Dict[str, Any]):
        """Actualitzar configuració de proveïdor"""
        if provider_name in self.providers:
            provider = self.providers[provider_name]
            for key, value in config.items():
                if hasattr(provider, key):
                    setattr(provider, key, value)
            logger.info(f"✅ Configuració actualitzada per {provider_name}")

# Instància global
llm_system = LLMIntegrationSystem()

# Funcions d'utilitat
async def generate_llm_response(provider: str, model: str, messages: List[Dict[str, str]], **kwargs) -> LLMResponse:
    """Funció d'utilitat per generar resposta LLM"""
    request = LLMRequest(
        provider=provider,
        model=model,
        messages=messages,
        **kwargs
    )
    return await llm_system.generate_response(request)

def get_llm_providers() -> Dict[str, Any]:
    """Obtenir llista de proveïdors LLM disponibles"""
    return llm_system.get_available_providers()
