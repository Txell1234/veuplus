"""
Universal LLM Service for VeuPlus
Supports multiple providers: OpenAI, Gemini, Anthropic, Azure, Ollama, Local
"""

import os
import asyncio
import httpx
import json
import logging
from typing import Dict, List, Any, Optional, AsyncGenerator, Union
from datetime import datetime

# Import configurations
try:
    from backend.config import LLM_PROVIDERS, get_provider_config, get_available_providers
except ImportError:
    from config import LLM_PROVIDERS, get_provider_config, get_available_providers

logger = logging.getLogger(__name__)

class LLMService:
    """Universal LLM service supporting multiple providers"""
    
    def __init__(self):
        self.providers = {}
        self.initialize_providers()
    
    def initialize_providers(self):
        """Initialize available providers"""
        available = get_available_providers()
        logger.info(f"Initializing LLM providers: {list(available.keys())}")
        
        for provider_id, config in available.items():
            try:
                if provider_id == "openai":
                    self.providers[provider_id] = OpenAIProvider(config)
                elif provider_id == "gemini":
                    self.providers[provider_id] = GeminiProvider(config)
                elif provider_id == "anthropic":
                    self.providers[provider_id] = AnthropicProvider(config)
                elif provider_id == "azure":
                    self.providers[provider_id] = AzureProvider(config)
                elif provider_id == "ollama":
                    self.providers[provider_id] = OllamaProvider(config)
                elif provider_id == "alia":
                    # NUEVO: Provider ALIA Kit (BSC)
                    try:
                        from backend.providers.llm.alia_provider import AliaLLMProvider
                        self.providers[provider_id] = AliaLLMProvider()
                        logger.info("✅ ALIA Kit provider initialized (BSC)")
                    except ImportError as e:
                        logger.warning(f"ALIA provider not available: {e}")
                elif provider_id in ["local", "vllm"]:
                    self.providers[provider_id] = LocalProvider(config)
                
                logger.info(f"✅ Provider {provider_id} initialized")
            except Exception as e:
                logger.warning(f"⚠️ Failed to initialize provider {provider_id}: {e}")
    
    def get_provider(self, provider_id: str) -> Optional['BaseProvider']:
        """Get a specific provider"""
        return self.providers.get(provider_id)
    
    def list_providers(self) -> Dict[str, Dict[str, Any]]:
        """List all available providers with their capabilities"""
        result = {}
        for provider_id, provider in self.providers.items():
            config = get_provider_config(provider_id)
            result[provider_id] = {
                "name": config["name"],
                "models": config["models"],
                "default_model": config["default_model"],
                "supports_streaming": config["supports_streaming"],
                "supports_functions": config["supports_functions"],
                "available": provider.is_available()
            }
        return result
    
    async def chat(
        self, 
        provider_id: str, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], AsyncGenerator[Dict[str, Any], None]]:
        """Universal chat method"""
        provider = self.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider {provider_id} not available")
        
        if stream:
            return provider.chat_stream(messages, model, temperature, max_tokens, **kwargs)
        else:
            return await provider.chat(messages, model, temperature, max_tokens, **kwargs)

class BaseProvider:
    """Base class for LLM providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = config["name"]
        self.models = config["models"]
        self.default_model = config["default_model"]
        self.base_url = config["base_url"]
        self.api_key = config.get("api_key")
        self.supports_streaming = config["supports_streaming"]
        self.supports_functions = config["supports_functions"]
    
    def is_available(self) -> bool:
        """Check if provider is available"""
        return True
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Chat with the provider"""
        raise NotImplementedError
    
    async def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream chat with the provider"""
        raise NotImplementedError

class OpenAIProvider(BaseProvider):
    """OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        if self.api_key:
            try:
                import openai
                self.client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                logger.warning("OpenAI library not available")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("OpenAI client not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "provider": "openai",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"OpenAI chat error: {e}")
            raise
    
    async def chat_stream(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self.client:
            raise RuntimeError("OpenAI client not available")
        
        try:
            stream = await self.client.chat.completions.create(
                model=model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield {
                        "content": chunk.choices[0].delta.content,
                        "model": chunk.model,
                        "provider": "openai",
                        "type": "chunk"
                    }
        except Exception as e:
            logger.error(f"OpenAI stream error: {e}")
            raise

class GeminiProvider(BaseProvider):
    """Google Gemini provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai
            except ImportError:
                logger.warning("Google Generative AI library not available")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Gemini client not available")
        
        try:
            # Convert messages to Gemini format
            prompt = self._convert_messages_to_prompt(messages)
            
            model_instance = self.client.GenerativeModel(model or self.default_model)
            
            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }
            
            response = await asyncio.to_thread(
                model_instance.generate_content,
                prompt,
                generation_config=generation_config
            )
            
            return {
                "content": response.text,
                "model": model or self.default_model,
                "provider": "gemini",
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Gemini prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"Instructions: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n\n".join(prompt_parts)

class AnthropicProvider(BaseProvider):
    """Anthropic Claude provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        if self.api_key:
            try:
                import anthropic
                self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                logger.warning("Anthropic library not available")
    
    def is_available(self) -> bool:
        return self.client is not None
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Anthropic client not available")
        
        try:
            # Separate system message from other messages
            system_message = ""
            chat_messages = []
            
            for msg in messages:
                if msg["role"] == "system":
                    system_message = msg["content"]
                else:
                    chat_messages.append(msg)
            
            response = await self.client.messages.create(
                model=model or self.default_model,
                max_tokens=max_tokens or 1000,
                temperature=temperature,
                system=system_message,
                messages=chat_messages,
                **kwargs
            )
            
            return {
                "content": response.content[0].text,
                "model": response.model,
                "provider": "anthropic",
                "usage": {
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens
                },
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Anthropic chat error: {e}")
            raise

class AzureProvider(BaseProvider):
    """Azure OpenAI provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.client = None
        additional_config = config.get("additional_config", {})
        self.api_version = additional_config.get("api_version")
        self.deployment_name = additional_config.get("deployment_name")
        
        if self.api_key and self.base_url:
            try:
                import openai
                self.client = openai.AsyncAzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=self.base_url,
                    api_version=self.api_version
                )
            except ImportError:
                logger.warning("OpenAI library not available for Azure")
    
    def is_available(self) -> bool:
        return self.client is not None and self.deployment_name
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        if not self.client:
            raise RuntimeError("Azure OpenAI client not available")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment_name or model or self.default_model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return {
                "content": response.choices[0].message.content,
                "model": response.model,
                "provider": "azure",
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                } if response.usage else None,
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Azure OpenAI chat error: {e}")
            raise

class OllamaProvider(BaseProvider):
    """Ollama local provider implementation"""
    
    def is_available(self) -> bool:
        try:
            import httpx
            # Test connection to Ollama
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient() as client:
                # Convert messages to prompt
                prompt = self._convert_messages_to_prompt(messages)
                
                response = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": model or self.default_model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens or -1
                        }
                    },
                    timeout=60
                )
                
                result = response.json()
                
                return {
                    "content": result["response"],
                    "model": result["model"],
                    "provider": "ollama",
                    "created_at": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"Ollama chat error: {e}")
            raise
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"Human: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

class LocalProvider(BaseProvider):
    """Local transformers provider implementation"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pipeline = None
        
    def is_available(self) -> bool:
        try:
            from transformers import pipeline
            return True
        except ImportError:
            return False
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            if not self.pipeline:
                from transformers import pipeline
                self.pipeline = pipeline(
                    "text-generation",
                    model=model or self.default_model,
                    device_map="auto" if self._has_gpu() else None
                )
            
            # Convert messages to prompt
            prompt = self._convert_messages_to_prompt(messages)
            
            result = await asyncio.to_thread(
                self.pipeline,
                prompt,
                max_length=max_tokens or 512,
                temperature=temperature,
                do_sample=True,
                pad_token_id=self.pipeline.tokenizer.eos_token_id
            )
            
            generated_text = result[0]["generated_text"]
            # Extract only the new part
            response = generated_text[len(prompt):].strip()
            
            return {
                "content": response,
                "model": model or self.default_model,
                "provider": "local",
                "created_at": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Local provider chat error: {e}")
            raise
    
    def _has_gpu(self) -> bool:
        try:
            import torch
            return torch.cuda.is_available()
        except:
            return False
    
    def _convert_messages_to_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to prompt"""
        prompt_parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                prompt_parts.append(content)
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        prompt_parts.append("Assistant:")
        return "\n\n".join(prompt_parts)

# Global LLM service instance
llm_service = LLMService()
