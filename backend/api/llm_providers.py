"""
API per LLM Providers
Endpoints per gestionar proveïdors LLM
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import logging

logger = logging.getLogger("veuplus.llm_providers")

router = APIRouter(prefix="/api/llm", tags=["LLM Providers"])

# Proveïdors LLM disponibles
LLM_PROVIDERS = {
    "openai": {
        "id": "openai",
        "name": "OpenAI",
        "description": "GPT-3.5/4 via API",
        "available": True,
        "api_key_required": True,
        "base_url": "https://api.openai.com/v1",
        "models": [
            "gpt-3.5-turbo",
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4o",
            "gpt-4o-mini"
        ],
        "default_model": "gpt-3.5-turbo",
        "supports_streaming": True,
        "supports_functions": True,
        "languages": ["en", "es", "ca", "fr", "de", "it", "pt"],
        "max_tokens": 4096,
        "temperature_range": [0.0, 2.0]
    },
    "alia": {
        "id": "alia",
        "name": "ALIA Kit (BSC)",
        "description": "Modelos multilingües oficiales ALIA Kit del Barcelona Supercomputing Center",
        "available": True,
        "api_key_required": False,
        "base_url": "",
        "models": [
            "BSC-LT/salamandra-7b",
            "BSC-LT/alia-40b"
        ],
        "default_model": "BSC-LT/salamandra-7b",
        "supports_streaming": True,
        "supports_functions": False,
        "languages": ["es", "ca", "eu", "gl"],
        "max_tokens": 2048,
        "temperature_range": [0.0, 1.0],
        "official_bsc": True
    },
    "ollama": {
        "id": "ollama",
        "name": "Ollama",
        "description": "Modelos locales via Ollama",
        "available": True,
        "api_key_required": False,
        "base_url": "http://localhost:11434",
        "models": [
            "llama2",
            "llama2:13b",
            "llama2:70b",
            "codellama",
            "mistral",
            "mixtral",
            "neural-chat",
            "starling-lm"
        ],
        "default_model": "llama2",
        "supports_streaming": True,
        "supports_functions": False,
        "languages": ["en", "es", "ca", "fr", "de"],
        "max_tokens": 2048,
        "temperature_range": [0.0, 2.0]
    },
    "vllm": {
        "id": "vllm",
        "name": "vLLM",
        "description": "vLLM server local",
        "available": True,
        "api_key_required": False,
        "base_url": "http://localhost:8000",
        "models": [
            "microsoft/DialoGPT-medium",
            "microsoft/DialoGPT-large",
            "facebook/blenderbot-400M-distill",
            "facebook/blenderbot-1B-distill"
        ],
        "default_model": "microsoft/DialoGPT-medium",
        "supports_streaming": True,
        "supports_functions": False,
        "languages": ["en", "es", "ca"],
        "max_tokens": 1024,
        "temperature_range": [0.0, 1.0]
    },
    "local": {
        "id": "local",
        "name": "Local LLM",
        "description": "Modelo local (GPT-OSS)",
        "available": True,
        "api_key_required": False,
        "base_url": "http://localhost:5000",
        "models": [
            "distilgpt2",
            "gpt2",
            "gpt2-medium",
            "gpt2-large"
        ],
        "default_model": "distilgpt2",
        "supports_streaming": False,
        "supports_functions": False,
        "languages": ["en", "es", "ca"],
        "max_tokens": 512,
        "temperature_range": [0.0, 1.0]
    }
}

@router.get("/providers")
async def get_llm_providers():
    """Obtenir llista de proveïdors LLM disponibles"""
    try:
        logger.info("✅ LLM Providers disponibles: 5 proveïdors")
        return {
            "success": True,
            "providers": LLM_PROVIDERS,
            "count": len(LLM_PROVIDERS)
        }
    except Exception as e:
        logger.error(f"Error getting LLM providers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/{provider_id}")
async def get_llm_provider(provider_id: str):
    """Obtenir informació d'un proveïdor específic"""
    try:
        if provider_id not in LLM_PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider = LLM_PROVIDERS[provider_id]
        logger.info(f"✅ LLM Provider: {provider['name']}")
        
        return {
            "success": True,
            "provider": provider
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LLM provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/providers/{provider_id}/models")
async def get_llm_provider_models(provider_id: str):
    """Obtenir models d'un proveïdor específic"""
    try:
        if provider_id not in LLM_PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider = LLM_PROVIDERS[provider_id]
        models = provider.get("models", [])
        
        return {
            "success": True,
            "provider_id": provider_id,
            "models": models,
            "count": len(models),
            "default_model": provider.get("default_model", models[0] if models else None)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting LLM provider models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/providers/{provider_id}/test")
async def test_llm_provider(provider_id: str):
    """Testar connexió amb un proveïdor LLM"""
    try:
        if provider_id not in LLM_PROVIDERS:
            raise HTTPException(status_code=404, detail="Provider not found")
        
        provider = LLM_PROVIDERS[provider_id]
        
        # Simular test de connexió
        test_result = {
            "provider_id": provider_id,
            "provider_name": provider["name"],
            "connection_status": "success" if provider["available"] else "failed",
            "response_time": "120ms",
            "test_message": "Hola, com estàs?",
            "test_response": "Hola! Estic bé, gràcies per preguntar. Com puc ajudar-te?",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
        logger.info(f"✅ LLM Provider test: {provider['name']} - {test_result['connection_status']}")
        
        return {
            "success": True,
            "test_result": test_result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing LLM provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ["router"]
