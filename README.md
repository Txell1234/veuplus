# VeuPlus Platform - Dev/Run Guide

## Run locally (Docker)

```bash
docker compose up --build -d
# Open http://localhost:8080
```

Nginx sirve el frontend en el puerto 8080 y hace proxy de `/api` hacia Uvicorn (backend).

Environment flags (opcional):
- `WARMUP_TTS=1` precarga XTTS v2
- `PRELOAD_AINA_DATASET=1` cachea una muestra de datasets Projecte AINA
- `CATALAN_DATASET_PATH=/data/catalan` usa WAVs locales como referencia de locutor

## Variables de entorno frontend
- `REACT_APP_BACKEND_URL` (en producción, fijar al dominio público antes de build)

## Entrenamiento XTTS
```bash
bash voicebots/training/xtts_catalan_base/train.sh
```
Configurable con variables `PYTHON`, `CONFIG_PATH`, `OUT_PATH`.

## Backend opcional: Unsloth gpt-oss

Para habilitar un proveedor LLM abierto (Unsloth):

1) Instalar dependencias en el entorno del backend

```bash
pip install --upgrade --no-cache-dir unsloth unsloth_zoo
```

2) Variables de entorno (opcionales)

- `UNSLOTH_MODEL` (por defecto `unsloth/gpt-oss-20b`)
- `UNSLOTH_MAX_SEQ` (por defecto `16384`)
- `UNSLOTH_4BIT=1` para cargar en 4bit
- `UNSLOTH_DEVICE_MAP` (por ejemplo `balanced`)
- `UNSLOTH_REASONING=low|medium|high`

3) Seleccionar el proveedor en el chatbot

Al crear un chatbot, usa `llm_provider="unsloth"` y (opcional) `reasoning_effort`.

4) GGUF (CPU/GPU con llama.cpp/Ollama)

Consulta los modelos GGUF en:
- 20B: unsloth/gpt-oss-20b-GGUF
- 120B: unsloth/gpt-oss-120b-GGUF

Notas:
- En `llama.cpp`, usa `--ctx-size 16384`, `--temp 1.0`, `--top-p 1.0`, `--top-k 0`.
- Para GPU, ajustar `--n-gpu-layers` y opciones de offloading según VRAM.

