# AT Hub - VeuPlus Platform v2.1.0

**Actualizado:** 10 de octubre de 2025

Plataforma completa i professional per a TTS catala, chatbots/voicebots i entrenament de veus, desenvolupada dins de AT Hub - Grup Amb Tu. Backend en FastAPI (SQLite) i frontend en React. Soporta multiples LLMs: OpenAI, Gemini, Claude, Ollama, vLLM i mes.

## Identitat AT Hub

- Logo: frontend/src/assets/ambtu-logo.svg (versio UI optimitzada)
- Paleta principal: blau navy #0f1f68, blau profund #07144a, accent taronja #ff6537
- Fons recomanats: primary-50 per pantalles generals i primary-100 per seccions destacades

Quan preparis documents, demos o material onboarding, utilitza aquesta paleta i el logotip AT Hub.



## 🎉 Novedades en v2.1.0

- ✅ **Dependencias actualizadas:** FastAPI 0.115, PyTorch 2.5, Transformers 4.46, React 18.3, Vite 5.4
- ⚙️ **Configuración mejorada:** Más de 20 nuevas variables de entorno configurables
- 📚 **Documentación completa:** Nuevas guías de instalación, compatibilidad y changelog
- 🔐 **Seguridad mejorada:** Todas las dependencias con parches de seguridad actualizados
- 🚀 **Mejor rendimiento:** Timeouts optimizados y cache configurable
- 🌟 **NUEVO: Integración ALIA Kit (BSC)** - Modelos oficiales multilingües del Barcelona Supercomputing Center

Ver [CHANGELOG_v2.1.0.md](CHANGELOG_v2.1.0.md) para detalles completos.

## 🌟 ALIA Kit Integration (NUEVO)

VeuPlus ahora integra **ALIA Kit**, la infraestructura oficial de IA del Barcelona Supercomputing Center (BSC):

- 🗣️ **Voces profesionales BSC** para catalán, español, euskera y gallego
- 🤖 **LLMs multilingües** (Salamandra 7B, ALIA 40B)
- ↔️ **Traducción automática** entre lenguas cooficiales  
- 📊 **Datasets curados** por el BSC con MareNostrum

**Estado:** Fase 1 completada (estructura implementada)  
**Docs:** [INTEGRACION_ALIA_KIT.md](INTEGRACION_ALIA_KIT.md)  
**Fuente oficial:** [https://langtech-bsc.gitbook.io/alia-kit](https://langtech-bsc.gitbook.io/alia-kit)

## 🚀 Inicio Rápido

### Con Docker (Recomendado)

```bash
docker compose up --build -d
# Abre http://localhost:8080
```

Nginx sirve el frontend en el puerto 8080 y hace proxy de `/api` hacia Uvicorn (backend).

### Manual (Desarrollo)

```bash
# 1. Configurar entorno
cp config.example.env .env

# 2. Backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
cd backend && python server.py

# 3. Frontend (otra terminal)
cd frontend
npm install
npm run dev
```

Ver [GUIA_INSTALACION_ACTUALIZADA.md](GUIA_INSTALACION_ACTUALIZADA.md) para instrucciones detalladas.

Environment flags (opcional):
- `WARMUP_TTS=1` precarga XTTS v2
- `PRELOAD_AINA_DATASET=1` cachea una muestra de datasets Projecte AINA
- `CATALAN_DATASET_PATH=/data/catalan` usa WAVs locales como referencia de locutor

## Variables de entorno frontend
- `REACT_APP_BACKEND_URL` (en produccion, fijar al dominio publico abans del build)

## Variables de entorno ConvHi
- `CONVHI_WIDGET_SECRET`: clau per signar URLs del widget (obligatori en produccio).
- `CONVHI_WIDGET_ALLOWLIST`: llista de dominis autoritzats per carregar l'embed (separats per comes).
- `CONVHI_WEBHOOK_SECRET`: secret HMAC per validar les sol licituds entrants.
- `CONVHI_WEBHOOK_STORE`: opcional, si es defineix `false` desactiva la persistencia local dels events.

- `REACT_APP_BACKEND_URL` (en producción, fijar al dominio público antes de build)

## Entrenamiento XTTS
```bash
bash voicebots/training/xtts_catalan_base/train.sh
```
Configurable con variables `PYTHON`, `CONFIG_PATH`, `OUT_PATH`.

### Dataset multi-locutor para catalán (Projecte AINA)

Este proyecto puede utilizar, de forma optativa, el corpus `projecte-aina/matxa-tts-cat-multispeaker` publicado en Hugging Face para enriquecer las voces catalanas (multi‑locutor). No se redistribuye el dataset; se accede dinámicamente desde Hugging Face mediante la librería `datasets` y se generan manifiestos locales para entrenamiento/validación.

- Dataset: `https://huggingface.co/projecte-aina/matxa-tts-cat-multispeaker`
- Uso: únicamente para entrenamiento/validación dentro de tu entorno (no se copia en el repositorio)
- Atribución: Projecte AINA / Generalitat de Catalunya (consulte la tarjeta del dataset para licencia y condiciones exactas)

En el pipeline (`backend/voice_training_pipeline.py`) se generan `manifest.csv` y `speakers.json` durante el preprocesado, respetando la licencia del dataset al no realizar ninguna redistribución del contenido original.

## LLMs soportados

### a) gpt‑oss‑20b (local) con vLLM (recomendado)

1) Iniciar todo con un clic en Windows:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./start_veuplus_vllm.ps1
```

Esto levanta vLLM (`openai/gpt-oss-20b`) en `http://localhost:8000`, el backend en `http://localhost:8001` y el frontend en `http://localhost:3000`.

2) Variables relevantes (ya las fija el script):
- `TRANSFORMERS_PROVIDER=vllm`
- `VLLM_BASE_URL=http://localhost:8000`
- `TRANSFORMERS_MODEL=openai/gpt-oss-20b`

3) Streaming token‑a‑token: endpoint `/api/transformers/stream` (SSE). El modal de test en UI permite “Stream”.

### b) OpenAI (API)

1) Define la clave y ejecuta el script:

```powershell
$env:OPENAI_API_KEY = "sk-..."
./start_veuplus_openai.ps1
```

2) En la UI, crea el chatbot con `Proveedor LLM: OpenAI`.

### c) HF local (sin vLLM)

No recomendado en Windows (bitsandbytes). Usar WSL2/Linux. Variables:

```powershell
$env:TRANSFORMERS_PROVIDER = "local"
$env:TRANSFORMERS_MODEL = "openai/gpt-oss-20b"
# Opcional GPU Linux/WSL2
# $env:TRANSFORMERS_LOAD_IN_4BIT = "1"
```

## Configuración (backend/config.py)

- `MAX_CACHE_ITEMS` (por defecto 100)
- `CATALAN_DATASETS` (lista separada por comas)
- `TRANSFORMERS_MODEL`, `TRANSFORMERS_PROVIDER`, `TRANSFORMERS_LOAD_IN_4BIT`, `VLLM_BASE_URL`
- `API_CORS_ORIGINS` (por defecto `*`)
- `MAX_UPLOAD_SIZE_MB` (límite en `/voices/import`)
- `OPENAI_TIMEOUT_SEC`, `TTS_TIMEOUT_SEC`

## Endpoints principales

- Salud: `GET /api/health`
- Chat LLM: `POST /api/transformers/chat`
- Streaming: `POST /api/transformers/stream` (SSE)
- Chatbots: `POST/GET /api/chatbots`, `POST /api/chatbots/chat`
- Voicebots: `POST/GET /api/voicebots`, `POST /api/voicebots/chat`
- TTS: `POST /api/synthesis` y `GET /api/audio/{id}`
- Voces: `GET/DELETE /api/voices`, `POST /api/voices/import`, `POST /api/voices/train`
- Knowledge: `POST/GET/DELETE /api/knowledge-base`
- Entrenamiento: `POST /api/training/start`, `GET /api/training/jobs`, `WS /api/training/ws/{job_id}`

## Seguridad y rendimiento

- ZIP seguro en `/voices/import` (protección contra path traversal)
- SQLite en hilos (`asyncio.to_thread`) para no bloquear el event loop
- CORS configurable por env

## UI/UX

- i18n básico (ca/es) con `react-i18next` (archivo `src/i18n.js`)
- Errores de API visuales (alert) en acciones clave
- Streaming token‑a‑token en el modal de test del chatbot

## Tests

- Carpeta `tests/` (placeholder inicial). Recomendado añadir casos: health, chatbots CRUD, chat transformers, TTS y knowledge‑base.

## 📋 Requisitos del Sistema

### Mínimos
- **Python:** 3.10 o superior (3.11+ recomendado)
- **Node.js:** 18.x o superior
- **RAM:** 8 GB mínimo
- **Disco:** 5 GB libres

### Recomendados
- **Python:** 3.11 (mejor rendimiento)
- **RAM:** 16 GB
- **GPU:** NVIDIA con CUDA 11.8+ (para LLMs locales)
- **Disco:** 10 GB libres (para modelos)

Ver [COMPATIBILIDAD_PYTHON.md](COMPATIBILIDAD_PYTHON.md) para detalles completos.

## 📚 Documentación Completa

- **[GUIA_INSTALACION_ACTUALIZADA.md](GUIA_INSTALACION_ACTUALIZADA.md)** - Guía completa de instalación paso a paso
- **[CHANGELOG_v2.1.0.md](CHANGELOG_v2.1.0.md)** - Cambios y novedades en v2.1.0
- **[COMPATIBILIDAD_PYTHON.md](COMPATIBILIDAD_PYTHON.md)** - Compatibilidad con versiones de Python
- **[config.example.env](config.example.env)** - Archivo de configuración de ejemplo
- **[RESUMEN_VEUPLUS.md](RESUMEN_VEUPLUS.md)** - Estado funcional del sistema
- **[CATALOGO_VOCES_VEUPLUS.md](CATALOGO_VOCES_VEUPLUS.md)** - Catálogo completo de voces
- **[BACKEND_README.md](BACKEND_README.md)** - Documentación técnica del backend
- **[docs/HYPERREALISTIC_SETUP.md](docs/HYPERREALISTIC_SETUP.md)** - Pasos per activar les veus hiperrealistes quan disposem de GPU


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

## Notas para fine‑tuning con GPT‑OSS y estado del TTS

- Objetivo: mantener separado el pipeline de LLM (GPT‑OSS) del pipeline de TTS. El backend ya soporta LLMs abiertos (vLLM/Unsloth/local), y la integración TTS en catalán se ha preparado para trabajo multi‑locutor sin redistribuir datasets.
- Estado actual (TTS):
  - TTS/ASR en `api/tts.py` y `api/asr.py` son placeholders funcionales (contrato estable) para no bloquear el desarrollo.
  - El pipeline de entrenamiento en `backend/voice_training_pipeline.py` genera `manifest.csv` y `speakers.json` usando datasets de Hugging Face (incl. `projecte-aina/matxa-tts-cat-multispeaker`) cuando el idioma es catalán.
  - Endpoint auxiliar: `GET /api/tts/voices` agrega locutores detectados a partir de `speakers.json`.
- Licencia/atribución de datos:
  - Los datasets (p. ej. Projecte AINA) no se incluyen en este repositorio; se consumen dinámicamente desde Hugging Face mediante `datasets`, respetando sus licencias. Revisa la card del dataset antes de uso en producción.

### Activar entrenamiento TTS real (Coqui/XTTS) más adelante

Para pasar de modo simulado a entrenamiento real de TTS multi‑locutor usando los manifests generados:

1) Preparar entorno
   - Instalar dependencias de Coqui/XTTS y utilidades de audio (PyTorch con CUDA, ffmpeg, soundfile, librosa, etc.).
   - Confirmar GPU con drivers y CUDA disponibles.

2) Script/wrapper de entrenamiento
   - Ya existe un placeholder: `scripts/train_coqui_xtts.py` que imprime `epoch=X/Y loss=Z` (parseable por el pipeline). Sustituir su lógica por la llamada real a Coqui/XTTS.
   - Consume `preprocessed_data/<job_id>/audio/manifest.csv` y parámetros: `--out`, `--epochs`, `--batch-size`, `--lr`.

3) Interruptor de modo
   - Ya incorporado: `trainer` en `TrainingRequest` admite `simulate` o `coqui_xtts`.
   - Si `trainer == "coqui_xtts"`, el pipeline lanza el script y parsea progreso para actualizar el WebSocket.

4) Inferencia multi‑locutor
   - Extender el motor TTS de producción para aceptar `speaker_id` (ya expuesto en la request de `/api/tts/synthesize`) o una referencia de audio, usando embeddings precalculados cuando sea posible.

5) Validación
   - Añadir pruebas que aseguren la presencia de `manifest.csv`, la agregación de `speakers.json` y la disponibilidad de `GET /api/tts/voices`.

Con este enfoque, el fine‑tuning de GPT‑OSS y el entrenamiento TTS avanzan en paralelo, con responsabilidades separadas y un contrato de datos claro basado en `manifest.csv`.

## Ejemplos de uso de la API (cURL)

Base URL por defecto: `http://localhost:8001`

Notas:
- Si configuraste `API_KEY`, añade la cabecera `-H "x-api-key: $API_KEY"` a las peticiones.
- Cambia el contenido según tus necesidades.

### 1) Iniciar entrenamiento (trainer=coqui_xtts)

```bash
curl -X POST "http://localhost:8001/api/training/start" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ca_multispeaker_v1",
    "language": "ca",
    "dialect": "central",
    "use_catalan_dataset": true,
    "dataset_names": ["projecte-aina/matxa-tts-cat-multispeaker"],
    "training_config": {
      "num_epochs": 50,
      "batch_size": 4,
      "learning_rate": 0.0001
    },
    "trainer": "coqui_xtts"
  }'
```

Para monitorizar progreso en tiempo real:
- WebSocket: `ws://localhost:8001/api/training/ws/<job_id>`
- Listado jobs: `GET http://localhost:8001/api/training/jobs`

### 2) Listar voces (multi‑locutor)

```bash
curl "http://localhost:8001/api/tts/voices"
```

### 3) Síntesis de TTS con `speaker_id`

```bash
curl -X POST "http://localhost:8001/api/tts/synthesize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Bon dia, això és una prova.",
    "language": "ca",
    "speaker_id": "SPEAKER_ID"
  }'
```

`SPEAKER_ID` se obtiene de `GET /api/tts/voices`. La respuesta incluye `audio_base64` (WAV) y metadatos.

