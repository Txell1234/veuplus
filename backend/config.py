import os
from typing import List, Dict, Any
from pathlib import Path


def get_env(name: str, default: str = "") -> str:
    """Obtener variable de entorno con valor por defecto"""
    return os.environ.get(name, default)


def get_bool_env(name: str, default: bool = False) -> bool:
    """Obtener variable de entorno booleana"""
    value = get_env(name, str(default)).lower()
    return value in ("1", "true", "yes", "on")


def get_int_env(name: str, default: int = 0) -> int:
    """Obtener variable de entorno entera con manejo de errores"""
    try:
        return int(get_env(name, str(default)))
    except ValueError:
        return default


# Application Settings
APP_NAME: str = get_env("APP_NAME", "VeuPlus")
APP_VERSION: str = get_env("APP_VERSION", "2.1.0")
DEBUG_MODE: bool = get_bool_env("DEBUG_MODE", False)

# Cache Settings
MAX_CACHE_ITEMS: int = get_int_env("MAX_CACHE_ITEMS", 100)
CACHE_TTL_SECONDS: int = get_int_env("CACHE_TTL_SECONDS", 3600)

# Datasets (comma-separated)
CATALAN_DATASETS_ENV = get_env("CATALAN_DATASETS", "projecte-aina/openslr-slr69-ca-trimmed-denoised,projecte-aina/4catac")
CATALAN_DATASETS: List[str] = [s.strip() for s in CATALAN_DATASETS_ENV.split(",") if s.strip()]

# Multi-Provider LLM Configuration
LLM_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "openai": {
        "name": "OpenAI",
        "api_key_env": "OPENAI_API_KEY",
        "base_url": get_env("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        "models": ["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini"],
        "default_model": "gpt-4o-mini",
        "supports_streaming": True,
        "supports_functions": True
    },
    "gemini": {
        "name": "Google Gemini",
        "api_key_env": "GEMINI_API_KEY",
        "base_url": get_env("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta"),
        "models": ["gemini-pro", "gemini-pro-vision", "gemini-1.5-pro", "gemini-1.5-flash"],
        "default_model": "gemini-1.5-flash",
        "supports_streaming": True,
        "supports_functions": True
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "api_key_env": "ANTHROPIC_API_KEY",
        "base_url": get_env("ANTHROPIC_BASE_URL", "https://api.anthropic.com"),
        "models": ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
        "default_model": "claude-3-5-sonnet-20241022",
        "supports_streaming": True,
        "supports_functions": True
    },
    "azure": {
        "name": "Azure OpenAI",
        "api_key_env": "AZURE_OPENAI_API_KEY",
        "base_url": get_env("AZURE_OPENAI_ENDPOINT", ""),
        "models": ["gpt-4", "gpt-35-turbo", "gpt-4-turbo"],
        "default_model": "gpt-35-turbo",
        "supports_streaming": True,
        "supports_functions": True,
        "additional_config": {
            "api_version": get_env("AZURE_OPENAI_API_VERSION", "2024-02-15-preview"),
            "deployment_name": get_env("AZURE_OPENAI_DEPLOYMENT_NAME", "")
        }
    },
    "ollama": {
        "name": "Ollama (Local)",
        "api_key_env": "",  # No API key needed
        "base_url": get_env("OLLAMA_BASE_URL", "http://localhost:11434"),
        "models": ["llama2", "llama3", "mistral", "codellama", "phi3"],
        "default_model": "llama3",
        "supports_streaming": True,
        "supports_functions": False
    },
    "local": {
        "name": "Local Transformers",
        "api_key_env": "",
        "base_url": "",
        "models": ["openai/gpt-oss-20b", "microsoft/DialoGPT-medium", "distilgpt2"],
        "default_model": "distilgpt2",
        "supports_streaming": True,
        "supports_functions": False
    },
    "vllm": {
        "name": "vLLM Server",
        "api_key_env": "",
        "base_url": get_env("VLLM_BASE_URL", "http://localhost:8000"),
        "models": ["openai/gpt-oss-20b"],
        "default_model": "openai/gpt-oss-20b",
        "supports_streaming": True,
        "supports_functions": False
    },
    "alia": {
        "name": "ALIA Kit (BSC)",
        "api_key_env": "",  # No API key needed - open source
        "base_url": "",  # Local HuggingFace models
        "models": ["BSC-LT/salamandra-7b", "BSC-LT/alia-40b"],
        "default_model": "BSC-LT/salamandra-7b",
        "supports_streaming": True,
        "supports_functions": False,
        "languages": ["es", "ca", "eu", "gl"],
        "official_bsc": True,
        "description": "Modelos multilingües oficiales ALIA Kit del Barcelona Supercomputing Center"
    }
}

# Legacy support - will be deprecated
TRANSFORMERS_MODEL = get_env("TRANSFORMERS_MODEL", "openai/gpt-oss-20b")
TRANSFORMERS_PROVIDER = get_env("TRANSFORMERS_PROVIDER", "local")  # local | vllm
TRANSFORMERS_LOAD_IN_4BIT = get_env("TRANSFORMERS_LOAD_IN_4BIT", "0") == "1"
VLLM_BASE_URL = get_env("VLLM_BASE_URL", "http://localhost:8000")

# Default LLM Configuration
DEFAULT_LLM_PROVIDER = get_env("DEFAULT_LLM_PROVIDER", "local")
DEFAULT_LLM_MODEL = get_env("DEFAULT_LLM_MODEL", "")  # If empty, uses provider's default

# CORS / API
API_CORS_ORIGINS = [s.strip() for s in get_env("API_CORS_ORIGINS", "*").split(",") if s.strip()]

# Server Settings
SERVER_HOST: str = get_env("SERVER_HOST", "0.0.0.0")
SERVER_PORT: int = get_int_env("SERVER_PORT", 8001)
SERVER_WORKERS: int = get_int_env("SERVER_WORKERS", 1)
SERVER_RELOAD: bool = get_bool_env("SERVER_RELOAD", False)

# Limits / Timeouts
MAX_UPLOAD_SIZE_MB: int = get_int_env("MAX_UPLOAD_SIZE_MB", 20)
MAX_REQUEST_SIZE_MB: int = get_int_env("MAX_REQUEST_SIZE_MB", 50)
OPENAI_TIMEOUT_SEC: int = get_int_env("OPENAI_TIMEOUT_SEC", 60)
TTS_TIMEOUT_SEC: int = get_int_env("TTS_TIMEOUT_SEC", 120)
GEMINI_TIMEOUT_SEC: int = get_int_env("GEMINI_TIMEOUT_SEC", 60)
ANTHROPIC_TIMEOUT_SEC: int = get_int_env("ANTHROPIC_TIMEOUT_SEC", 60)
AZURE_TIMEOUT_SEC: int = get_int_env("AZURE_TIMEOUT_SEC", 60)
OLLAMA_TIMEOUT_SEC: int = get_int_env("OLLAMA_TIMEOUT_SEC", 120)

# Database Settings
DB_PATH: str = get_env("DB_PATH", "backend/veuplus.db")
DB_BACKUP_ENABLED: bool = get_bool_env("DB_BACKUP_ENABLED", True)
DB_BACKUP_INTERVAL_HOURS: int = get_int_env("DB_BACKUP_INTERVAL_HOURS", 24)

# Logging Settings
LOG_LEVEL: str = get_env("LOG_LEVEL", "INFO")
LOG_FORMAT: str = get_env("LOG_FORMAT", "json")  # json or text
LOG_FILE: str = get_env("LOG_FILE", "")

# Function to get available providers
def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """Get available LLM providers based on environment configuration"""
    available = {}
    
    for provider_id, config in LLM_PROVIDERS.items():
        api_key_env = config.get("api_key_env")
        
        # Check if provider is available
        if not api_key_env:  # No API key needed (local providers)
            available[provider_id] = config
        elif os.environ.get(api_key_env):  # API key is set
            available[provider_id] = config
    
    return available

# Function to get provider config
def get_provider_config(provider_id: str) -> Dict[str, Any]:
    """Get configuration for a specific provider"""
    if provider_id not in LLM_PROVIDERS:
        raise ValueError(f"Unknown provider: {provider_id}")
    
    config = LLM_PROVIDERS[provider_id].copy()
    
    # Add API key if available
    api_key_env = config.get("api_key_env")
    if api_key_env:
        config["api_key"] = os.environ.get(api_key_env)
    
    return config


