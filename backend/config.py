import os
from typing import List


def get_env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


MAX_CACHE_ITEMS: int = int(get_env("MAX_CACHE_ITEMS", "100"))

# Datasets (comma-separated)
CATALAN_DATASETS_ENV = get_env("CATALAN_DATASETS", "projecte-aina/openslr-slr69-ca-trimmed-denoised,projecte-aina/4catac")
CATALAN_DATASETS: List[str] = [s.strip() for s in CATALAN_DATASETS_ENV.split(",") if s.strip()]

# OpenAI / Transformers
TRANSFORMERS_MODEL = get_env("TRANSFORMERS_MODEL", "openai/gpt-oss-20b")
TRANSFORMERS_PROVIDER = get_env("TRANSFORMERS_PROVIDER", "local")  # local | vllm
TRANSFORMERS_LOAD_IN_4BIT = get_env("TRANSFORMERS_LOAD_IN_4BIT", "0") == "1"
VLLM_BASE_URL = get_env("VLLM_BASE_URL", "http://localhost:8000")

# CORS / API
API_CORS_ORIGINS = [s.strip() for s in get_env("API_CORS_ORIGINS", "*").split(",") if s.strip()]

# Limits / Timeouts
MAX_UPLOAD_SIZE_MB: int = int(get_env("MAX_UPLOAD_SIZE_MB", "20"))
OPENAI_TIMEOUT_SEC: int = int(get_env("OPENAI_TIMEOUT_SEC", "30"))
TTS_TIMEOUT_SEC: int = int(get_env("TTS_TIMEOUT_SEC", "60"))


