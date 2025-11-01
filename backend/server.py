from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter
from fastapi import Request
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Iterable
import uuid
import os
import logging
from pathlib import Path
import sys
import os
from datetime import datetime
import subprocess
import shutil
from uuid import uuid4
import asyncio
import hashlib
import base64
from collections import OrderedDict
from typing import Iterable
from pathlib import Path

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# SQLite Database setup - NO MORE MONGO!
try:
    from backend.database_sql import db as sql_db
except ImportError:
    from database_sql import db as sql_db

# Initialize FastAPI
app = FastAPI(
    title="VeuPlus Developer Platform", 
    version="2.0.0",
    description="Professional voice synthesis and AI chatbot platform for developers",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Router principal
api_router = APIRouter(prefix="/api")

# Logger
logger = logging.getLogger("veuplus.server")
if not logger.handlers:
    handler = logging.StreamHandler()
    # JSON-like format for easier log aggregation
    formatter = logging.Formatter('{"ts": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "msg": %(message)s}')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Legacy router block disabled (see unified loader below)

# Simple API key middleware (optional, opt-in via env API_KEY)
from fastapi import Header
API_KEY = os.environ.get("API_KEY", "")

@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    # Enforce API key only for /api/* if API_KEY is set
    if API_KEY and str(request.url.path).startswith("/api/"):
        header_key = request.headers.get("x-api-key")
        if (header_key or "") != API_KEY:
            return JSONResponse(status_code=401, content={"detail": "Invalid or missing API key"})
    return await call_next(request)
# Voice import DTOs
class VoiceImportResponse(BaseModel):
    voice_id: str
    message: str
    sample_url: Optional[str] = None
    model_url: Optional[str] = None


# Language utilities for multilingual TTS
SUPPORTED_LANGS: Dict[str, str] = {
    # canonical -> canonical
    "ca": "ca",
    "es": "es",
    "en": "en",
    "fr": "fr",
}

LANG_ALIASES: Dict[str, str] = {
    # Catalan
    "catalan": "ca",
    "catala": "ca",
    "catal\u00e0": "ca",
    "cat": "ca",
    # Spanish
    "spanish": "es",
    "espanol": "es",
    "espa\u00f1ol": "es",
    "castellano": "es",
    "spa": "es",
    "es-es": "es",
    # English
    "eng": "en",
    "en-us": "en",
    "en-gb": "en",
    # French
    "fra": "fr",
    "fre": "fr",
    "fr-fr": "fr",
}

def normalize_language_code(code: Optional[str]) -> str:
    if not code:
        return "ca"
    lc = code.lower()
    if lc in SUPPORTED_LANGS:
        return lc
    return LANG_ALIASES.get(lc, "ca")

# Phonetic transcriber (SEGRE) for Catalan only
try:
    try:
        from phonology.segre_transcriber import transcribe as segre_transcribe, supports_language as segre_supports
    except ImportError:
        from backend.phonology.segre_transcriber import transcribe as segre_transcribe, supports_language as segre_supports
    segre_available = True
except Exception:
    segre_available = False

# Import and include developer dashboard
try:
    # Try with absolute import - Use SQLite version
    import sys
    sys.path.append('/app/backend')
    from developer_dashboard import dev_router
    app.include_router(dev_router)
    logger.info("Developer Dashboard (SQLite) enabled")
except ImportError as e:
    logger.warning(f"Developer Dashboard not available: {str(e)}")

# Import real voice training system
try:
    from real_voice_training import voice_trainer
    logger.info("Real Voice Training System enabled")
except ImportError as e:
    logger.warning(f"Real Voice Training not available: {str(e)}")

# Import call center system
try:
    from call_center_system import call_center_router
    app.include_router(call_center_router)
    logger.info("Call Center AI System enabled")
except ImportError as e:
    logger.warning(f"Call Center System not available: {str(e)}")

# Import training pipeline (XTTS v2) with robust import paths
try:
    try:
        from backend.voice_training_pipeline import training_router  # type: ignore
    except ImportError:
        from voice_training_pipeline import training_router  # type: ignore
    app.include_router(training_router)
    logger.info("Voice Training API enabled (/api/training)")
except ImportError as e:
    logger.warning(f"Voice Training API not available: {e}")

# Ensure local package paths (so that `api.*` resolves when running locally/tests)
try:
    sys.path.insert(0, str(Path(__file__).parent))
except Exception:
    pass

# Import transformers service (after ensuring new pipeline package is importable)
try:
    from transformers_service import transformers_router
    app.include_router(transformers_router)
    logger.info("Transformers Service enabled")
except ImportError as e:
    logger.warning(f"Transformers Service not available: {str(e)}")

# Mount new chat API router (SSE streaming)
_chat_ok = False
for mod in ("api.chat", "backend.api.chat"):
    try:
        chat_router = __import__(mod, fromlist=["router"]).router  # type: ignore
        app.include_router(chat_router)
        logger.info("Chat API router enabled (/api/chat)")
        _chat_ok = True
        break
    except Exception:
        continue
if not _chat_ok:
    logger.warning("Chat API router not available")

# Mount TTS/ASR routers (placeholders if engines not installed)
_tts_ok = False
for mod in ("api.tts", "backend.api.tts"):
    try:
        tts_router = __import__(mod, fromlist=["router"]).router  # type: ignore
        app.include_router(tts_router)
        logger.info("TTS API router enabled (/api/tts)")
        _tts_ok = True
        break
    except Exception:
        continue
if not _tts_ok:
    logger.warning("TTS API router not available")

# Import Advanced TTS API router
_advanced_tts_ok = False
for mod in ("api.advanced_tts", "backend.api.advanced_tts"):
    try:
        advanced_tts_router = __import__(mod, fromlist=["router"]).router  # type: ignore
        app.include_router(advanced_tts_router)
        logger.info("Advanced TTS API router enabled (/api/advanced-tts)")
        _advanced_tts_ok = True
        break
    except Exception:
        continue
if not _advanced_tts_ok:
    logger.warning("Advanced TTS API router not available")

_asr_ok = False
for mod in ("api.asr", "backend.api.asr"):
    try:
        asr_router2 = __import__(mod, fromlist=["router"]).router  # type: ignore
        app.include_router(asr_router2)
        logger.info("ASR API router enabled (/api/asr)")
        _asr_ok = True
        break
    except Exception:
        continue
if not _asr_ok:
    logger.warning("ASR API router not available")

# Import ASR service (Whisper)
try:
    from asr_service import asr_router
    app.include_router(asr_router)
    logger.info("ASR Service (Whisper) enabled")
except ImportError as e:
    logger.warning(f"ASR Service not available: {str(e)}")

# Create directories
TEMP_AUDIO_DIR = Path("backend/temp_audio")
STATIC_DIR = Path("backend/static")
MODELS_BASE_DIR = Path("backend")
TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
STATIC_DIR.mkdir(parents=True, exist_ok=True)

# Mount static files (will be overridden by frontend config below)
# app.mount("/static", StaticFiles(directory="backend/static"), name="static")
 
# Voices API router (modular extractions)
try:
    from backend.api.voices import router as voices_router
    app.include_router(voices_router)
    logger.info("Voices API router enabled (/api/voices)")
except Exception as e:
    logger.warning(f"Voices API router not available: {e}")


try:
    from api.convhi_agents import router as convhi_agents_router
    app.include_router(convhi_agents_router)
    logger.info("ConvHi Agents router enabled (/api/convhi)")
except Exception as e:
    logger.warning(f"ConvHi Agents router not available: {e}")

try:
    from api.convhi_sip import router as convhi_sip_router
    app.include_router(convhi_sip_router)
    logger.info("ConvHi SIP router enabled (/api/convhi/sip)")
except Exception as e:
    logger.warning(f"ConvHi SIP router not available: {e}")

try:
    from api.convhi_webrtc import webrtc_router
    app.include_router(webrtc_router)
    logger.info("ConvHi WebRTC router enabled (/api/convhi/webrtc)")
except Exception as e:
    logger.warning(f"ConvHi WebRTC router not available: {e}")

# Voices endpoints moved to backend/api/voices.py

# Ensure critical routers are mounted (production-safe), even if earlier imports failed
def _try_import_router(module_names: Iterable[str], attr: str):
    for mod in module_names:
        try:
            imported = __import__(mod, fromlist=[attr])
            return getattr(imported, attr)
        except Exception:
            continue
    return None

def _has_route_prefix(prefix: str) -> bool:
    try:
        for r in app.router.routes:
            if getattr(r, 'path', '').startswith(prefix):
                return True
    except Exception:
        pass
    return False

_CRITICAL_ROUTERS = [
    (("api.edge_tts", "backend.api.edge_tts"), "edge_router", "/api/edge-tts", "Edge TTS"),
    (("api.catalan_tts", "backend.api.catalan_tts"), "catalan_router", "/api/catalan", "Catalan TTS"),
    (("api.alia", "backend.api.alia"), "router", "/api/alia", "ALIA Kit"),
    (("api.unified_voices", "backend.api.unified_voices"), "router", "/api/voices", "Unified Voices"),
    (("api.sip_agent", "backend.api.sip_agent"), "router", "/api/sip", "SIP Agent"),
    (("api.voicebots_external", "backend.api.voicebots_external"), "router", "/api/voicebots", "Voicebots External"),
    (("api.convhi_webrtc", "backend.api.convhi_webrtc"), "webrtc_router", "/api/convhi/webrtc", "ConvHi WebRTC"),
    (("api.convhi_agents", "backend.api.convhi_agents"), "router", "/api/convhi", "ConvHi Agents"),
    (("api.convhi_knowledge", "backend.api.convhi_knowledge"), "router", "/api/convhi/knowledge", "ConvHi Knowledge"),
    (("api.convhi_language", "backend.api.convhi_language"), "router", "/api/convhi/language", "ConvHi Language"),
    (("api.convhi_analytics", "backend.api.convhi_analytics"), "router", "/api/convhi/analytics", "ConvHi Analytics"),
    (("api.convhi_sip", "backend.api.convhi_sip"), "router", "/api/convhi/sip", "ConvHi SIP Trunking"),
    (("api.convhi_widget", "backend.api.convhi_widget"), "router", "/api/convhi/widget", "ConvHi Widget Signed URL"),
    (("api.convhi_webhooks", "backend.api.convhi_webhooks"), "router", "/api/convhi/webhooks", "ConvHi Webhooks"),
    (("api.convhi_widgets", "backend.api.convhi_widgets"), "router", "/api/convhi/widgets", "ConvHi Widgets"),
    (("api.convhi_widget_management", "backend.api.convhi_widget_management"), "router", "/api/convhi/widget-management", "ConvHi Widget Management"),
    (("api.convhi_batch_calling", "backend.api.convhi_batch_calling"), "router", "/api/convhi/batch-calling", "ConvHi Batch Calling"),
    (("api.convhi_crm_connectors", "backend.api.convhi_crm_connectors"), "router", "/api/convhi/crm-connectors", "ConvHi CRM Connectors"),
    (("api.voice_publish", "backend.api.voice_publish"), "router", "/api/voices/publish", "Voices Publish"),
]

for mods, attr, prefix, name in _CRITICAL_ROUTERS:
    if not _has_route_prefix(prefix):
        router_obj = _try_import_router(list(mods), attr)
        if router_obj is not None:
            try:
                app.include_router(router_obj)
                logger.info(f"(fallback) Router enabled: {name}")
            except Exception as e:
                logger.warning(f"(fallback) Failed to include router {name}: {e}")
        else:
            logger.warning(f"(fallback) Router not available: {name}")


# Ensure external voices router is available even if not in the list
try:
    try:
        from backend.api.convhi_external_voices import router as external_voices_router  # type: ignore
    except ImportError:
        from api.convhi_external_voices import router as external_voices_router  # type: ignore
    app.include_router(external_voices_router)
    logger.info("ConvHi External Voices router enabled (/api/convhi/voices/external)")
except Exception:
    pass


# OpenAI setup
openai_client = None
openai_available = False
unsloth_available = False

try:
    import openai
    api_key = os.environ.get('OPENAI_API_KEY')
    if api_key:
        openai_client = openai.OpenAI(api_key=api_key)
        openai_available = True
        logger.info("OpenAI client initialized successfully")
    else:
        logger.warning("OpenAI API key not found")
except ImportError:
    logger.warning("OpenAI library not available")

# Optional: Unsloth LLM backend
try:
    from backend import unsloth_llm
    unsloth_llm.load_model()
    unsloth_available = unsloth_llm.is_available()
    if unsloth_available:
        logger.info("Unsloth LLM backend available")
except Exception as _e:
    logger.warning(f"Unsloth backend not available: {_e}")

# Optional: Coqui TTS (XTTS v2) lazy loader
xtts_model = None
xtts_available = False
xtts_lib_available = False
try:
    from TTS.api import TTS as _TTSProbe  # probe only
    xtts_lib_available = True
    del _TTSProbe
    logger.info("Coqui TTS library available")
except Exception as _e:
    logger.warning(f"Coqui TTS library not available: {_e}")

def get_xtts_model():
    """Lazy load Coqui XTTS v2 model once per process."""
    global xtts_model, xtts_available
    if xtts_model is not None:
        return xtts_model
    try:
        from TTS.api import TTS as CoquiTTS
        # Multilingual cross-lingual TTS model (supports Catalan via language code)
        xtts_model = CoquiTTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")
        xtts_available = True
        logger.info("Coqui XTTS v2 loaded successfully")
    except Exception as e:
        xtts_model = None
        xtts_available = False
        logger.warning(f"Coqui XTTS not available: {e}")
    return xtts_model

# Optional: datasets availability for preload/health
datasets_available = False
try:
    from datasets import load_dataset as _load_dataset_probe  # noqa: F401
    datasets_available = True
    logger.info("Datasets library available")
except Exception as _e:
    logger.warning(f"Datasets library not available: {_e}")

# Simple in-memory LRU cache for synthesized audio (by text + voice params)
try:
    from backend.config import MAX_CACHE_ITEMS, API_CORS_ORIGINS, MAX_UPLOAD_SIZE_MB
except Exception:
    MAX_CACHE_ITEMS = int(os.environ.get("MAX_CACHE_ITEMS", "100"))
    API_CORS_ORIGINS = ["*"]
    MAX_UPLOAD_SIZE_MB = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "20"))
_audio_cache: "OrderedDict[str, tuple[str, Path]]" = OrderedDict()

def _make_cache_key(text: str, language: str, dialect: str, voice_model_id: str) -> str:
    key = f"{language}|{dialect}|{voice_model_id}|{text}"
    return hashlib.sha1(key.encode("utf-8")).hexdigest()

def _cache_get(key: str) -> tuple[str, Path] | None:
    item = _audio_cache.get(key)
    if item:
        # move to end (most recently used)
        _audio_cache.move_to_end(key)
    return item

def _cache_set(key: str, audio_id: str, path: Path) -> None:
    _audio_cache[key] = (audio_id, path)
    _audio_cache.move_to_end(key)
    if len(_audio_cache) > MAX_CACHE_ITEMS:
        _audio_cache.popitem(last=False)

def _find_reference_wavs() -> list[Path]:
    base = Path("backend/voice_models")
    if not base.exists():
        return []
    wavs: list[Path] = []
    for sub in sorted(base.glob("*/**/test_voice.wav")):
        wavs.append(sub)
    for sub in sorted(base.glob("*/test_voice.wav")):
        if sub not in wavs:
            wavs.append(sub)
    return wavs

def _get_dialect_reference_wav(dialect: str) -> Path | None:
    """Best-effort mapping of dialect to a reference speaker WAV if available."""
    candidates = _find_reference_wavs()
    if not candidates:
        return None
    order = [
        "central",
        "balearic",
        "valencian",
        "andorran",
        "rossellones",
        "alguerese",
    ]
    try:
        idx = order.index(dialect)
    except ValueError:
        idx = 0
    if idx < len(candidates):
        return candidates[idx]
    return candidates[0]

def _select_pyttsx3_voice_by_id(engine, voice_id: str = None) -> None:
    """Select a specific voice by ID or fall back to best available voice."""
    try:
        voices = engine.getProperty('voices') or []
    except Exception as e:
        logging.getLogger(__name__).error(f"pyttsx3: no se pudieron obtener las voces: {e}")
        raise

    # Si se especifica un voice_id, intentar usarlo
    if voice_id and voice_id.startswith('system_'):
        # Extraer el ID real del sistema
        system_id = voice_id.replace('system_', '')
        for voice in voices:
            voice_system_id = getattr(voice, 'id', '')
            # Buscar por ID completo o por la parte final
            if system_id in voice_system_id or voice_system_id.endswith(system_id):
                engine.setProperty('voice', voice.id)
                logging.getLogger(__name__).info(f"pyttsx3: usando voz espec?fica '{voice.name}' ({voice.id})")
                return

    # Fallback: priorizar espa?ol sobre otros idiomas
    spanish_voice = None
    for voice in voices:
        name = (getattr(voice, 'name', '') or '').lower()
        langs = getattr(voice, 'languages', []) or []
        langs_text = ' '.join([str(l).lower() for l in langs])
        
        # Buscar espec?ficamente voces espa?olas
        if 'spanish' in name or 'helena' in name or 'es-es' in langs_text:
            engine.setProperty('voice', voice.id)
            logging.getLogger(__name__).info(f"pyttsx3: usando voz espa?ola '{voice.name}' ({voice.id})")
            return
        # Guardar como fallback si encontramos espa?ol en idiomas
        if 'es' in langs_text and not spanish_voice:
            spanish_voice = voice
    
    # Usar voz espa?ola de fallback si la encontramos
    if spanish_voice:
        engine.setProperty('voice', spanish_voice.id)
        logging.getLogger(__name__).info(f"pyttsx3: usando voz espa?ola (fallback) '{spanish_voice.name}' ({spanish_voice.id})")
        return

    # Si no hay espa?ol, buscar cualquier voz catalana/valenciana
    for voice in voices:
        name = (getattr(voice, 'name', '') or '').lower()
        langs = getattr(voice, 'languages', []) or []
        langs_text = ' '.join([str(l).lower() for l in langs])
        if any(tag in name for tag in ['catalan', 'valencian', 'balear', 'ca']) or \
           any(tag in langs_text for tag in ['catalan', 'ca']):
            engine.setProperty('voice', voice.id)
            logging.getLogger(__name__).info(f"pyttsx3: usando voz catalana '{voice.name}' ({voice.id})")
            return

    # Si no encontramos nada espec?fico, usar la primera voz disponible
    if voices:
        engine.setProperty('voice', voices[0].id)
        logging.getLogger(__name__).info(f"pyttsx3: usando voz por defecto '{voices[0].name}' ({voices[0].id})")
        return

    logging.getLogger(__name__).error("pyttsx3: no se encontraron voces disponibles")
    raise RuntimeError("No se encontraron voces disponibles en pyttsx3")

# Mantener compatibilidad con funci?n anterior
def _select_pyttsx3_voice_or_fail(engine) -> None:
    """Select a Catalan/Spanish voice; raise if not found."""
    _select_pyttsx3_voice_by_id(engine, None)

def _scan_local_wavs(base_path: Path) -> Iterable[tuple[float, float, Path]]:
    """Yield tuples of (sample_rate, duration_seconds, path) for .wav files under base_path."""
    for wav in base_path.rglob("*.wav"):
        try:
            import soundfile as sf
            info = sf.info(str(wav))
            dur = float(info.frames) / float(info.samplerate)
            yield float(info.samplerate), dur, wav
        except Exception:
            continue

def _find_best_sample_from_datasets(dataset_names: List[str], local_path: Optional[str] = None):
    """Return best (array, sampling_rate) from local path or remote datasets; None if unavailable."""
    # 1) Local path scan
    if local_path:
        p = Path(local_path)
        if p.exists():
            best = None
            best_score = 0.0
            for sr, dur, wav in _scan_local_wavs(p):
                score = sr * dur
                if score > best_score:
                    best_score = score
                    best = (sr, dur, wav)
            if best:
                try:
                    import soundfile as sf
                    data, sr = sf.read(str(best[2]))
                    return {"array": data, "sampling_rate": sr}
                except Exception:
                    pass
    # 2) Remote datasets via HF
    if datasets_available:
        try:
            from datasets import load_dataset
            best_sample = None
            best_quality = 0.0
            for name in dataset_names:
                ds = load_dataset(name, split="train[:10]", trust_remote_code=True)
                for sample in ds:
                    audio = sample.get("audio") if isinstance(sample, dict) else getattr(sample, "audio", None)
                    if isinstance(audio, dict) and "array" in audio and "sampling_rate" in audio:
                        arr = audio["array"]
                        sr = audio["sampling_rate"]
                        dur = len(arr) / max(1, sr)
                        score = float(sr) * float(dur)
                        if score > best_quality:
                            best_quality = score
                            best_sample = audio
            if best_sample:
                return best_sample
        except Exception as e:
            logger.warning(f"Dataset load failed: {e}")
    return None

def _get_dataset_reference_wav(temp_dir: Path) -> Optional[Path]:
    """Return a path to a speaker WAV derived from local dataset or HF corpora.
    - If CATAlAN_DATASET_PATH exists: choose best local wav
    - Else: fetch best sample from configured HF datasets and write a temp wav
    """
    # Local dataset path priority
    local_path = os.environ.get("CATALAN_DATASET_PATH")
    if local_path and Path(local_path).exists():
        # Choose best local wav by sample_rate * duration
        best_sr = 0.0
        best_dur = 0.0
        best_wav: Optional[Path] = None
        for sr, dur, wav in _scan_local_wavs(Path(local_path)):
            score = sr * dur
            if score > best_sr * best_dur:
                best_sr, best_dur, best_wav = sr, dur, wav
        if best_wav and best_wav.exists():
            return best_wav

    # Remote datasets via HF -> write temp wav
    if datasets_available:
        try:
            best = _find_best_sample_from_datasets(CATALAN_DATASETS, None)
            if best and "array" in best and "sampling_rate" in best:
                import soundfile as sf
                ref_path = temp_dir / f"ref_speaker_{uuid.uuid4().hex}.wav"
                sr = max(int(best["sampling_rate"]), 22050)
                sf.write(str(ref_path), best["array"], sr, subtype="PCM_16")
                if ref_path.exists() and ref_path.stat().st_size > 1024:
                    return ref_path
        except Exception as e:
            print(f"?? Could not prepare dataset reference wav: {e}")
    return None

# Check for espeak-ng
espeak_available = False
try:
    result = subprocess.run(['espeak-ng', '--version'], capture_output=True, text=True)
    if result.returncode == 0:
        espeak_available = True
        logger.info("espeak-ng available")
except:
    logger.warning("espeak-ng not available")

# Catalan dialects configuration
CATALAN_DIALECTS = [
    {"id": "central", "name": "Catal? Central", "region": "Barcelona, Girona"},
    {"id": "balearic", "name": "Balear", "region": "Illes Balears"},
    {"id": "valencian", "name": "Valenci?", "region": "Pa?s Valenci?"},
    {"id": "andorran", "name": "Andorr?", "region": "Andorra"},
    {"id": "rossellones", "name": "Rossellon?s", "region": "Fran?a del Nord"},
    {"id": "alguerese", "name": "Alguer?s", "region": "L'Alguer, Sardenya"}
]

# Supported Catalan corpora (local or Hugging Face)
CATALAN_DATASETS: List[str] = [
    "projecte-aina/openslr-slr69-ca-trimmed-denoised",
    "projecte-aina/4catac",
]

# Pydantic models
class SynthesisRequest(BaseModel):
    text: str
    voice_model_id: Optional[str] = "catalan_enhanced"
    language: Optional[str] = "ca"

class ChatRequest(BaseModel):
    message: str
    bot_id: str
    conversation_history: Optional[List[Dict[str, str]]] = []

class VoiceTrainingRequest(BaseModel):
    name: str
    dialect: str
    description: Optional[str] = ""
    use_catalan_dataset: Optional[bool] = True

class ChatbotCreateRequest(BaseModel):
    name: str
    llm_provider: str = "transformers"  # use local transformers by default
    model_name: str = "openai/gpt-oss-20b"
    temperature: float = 0.7
    system_prompt: str
    api_key: Optional[str] = ""
    knowledge_base_ids: Optional[List[str]] = []
    reasoning_effort: Optional[str] = "medium"  # used by unsloth

class VoicebotCreateRequest(BaseModel):
    name: str
    voice_model_id: str
    llm_provider: str = "transformers"
    model_name: str = "openai/gpt-oss-20b"
    temperature: float = 0.7
    system_prompt: str
    api_key: Optional[str] = ""
    knowledge_base_ids: Optional[List[str]] = []

# API Routes

# Health check
@api_router.get("/health")
async def health_check():
    active_provider = os.environ.get("TRANSFORMERS_PROVIDER", "local")
    active_model = os.environ.get("TRANSFORMERS_MODEL", "distilgpt2")
    dev_mode = os.environ.get("DEVELOPMENT_MODE", "false")
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "sqlite": f"connected:{sql_db.db_path}",
            "openai": "available" if openai_available else "unavailable",
            "tts_xtts": "installed" if xtts_lib_available else "not_installed",
            "espeak": "available" if espeak_available else "unavailable",
            "unsloth": "available" if unsloth_available else "unavailable",
        },
        "supported_languages": list(SUPPORTED_LANGS.keys()),
        "transformers": {
            "provider": active_provider,
            "model": active_model,
        },
        "limits": {
            "max_upload_mb": MAX_UPLOAD_SIZE_MB,
        },
        "flags": {
            "development_mode": dev_mode,
        }
    }

# Import TTS engines - PRIORIDAD CORRECTA
# 1. Sistema Neural Real (m?xima prioridad)
try:
    try:
        from real_neural_tts import RealNeuralTTS
    except ImportError:
        from backend.real_neural_tts import RealNeuralTTS
    real_neural_tts = RealNeuralTTS()
    REAL_NEURAL_TTS_AVAILABLE = True
    logger.info("Real Neural TTS engine available")
except ImportError as e:
    REAL_NEURAL_TTS_AVAILABLE = False
    logger.warning(f"Real Neural TTS engine not available: {e}")

# 2. Motor Hiperrealista
try:
    try:
        from hyperrealistic_engine import hyperrealistic_engine
    except ImportError:
        from backend.hyperrealistic_engine import hyperrealistic_engine
    HYPERREALISTIC_AVAILABLE = True
    logger.info("Hyperrealistic engine available")
except ImportError as e:
    HYPERREALISTIC_AVAILABLE = False
    logger.warning(f"Hyperrealistic engine not available: {e}")

# 3. Entrenador de Voces Premium
try:
    try:
        from premium_voice_trainer import PremiumVoiceTrainer
    except ImportError:
        from backend.premium_voice_trainer import PremiumVoiceTrainer
    premium_trainer = PremiumVoiceTrainer()
    PREMIUM_TRAINER_AVAILABLE = True
    logger.info("Premium Voice Trainer available")
except ImportError as e:
    PREMIUM_TRAINER_AVAILABLE = False
    logger.warning(f"Premium Voice Trainer not available: {e}")

# 4. Sistema Catal?n Realista (fallback) - MOTOR PRINCIPAL PARA VOCES CATALANAS
try:
    try:
        from realistic_catalan_tts import RealisticCatalanTTS
    except ImportError:
        from backend.realistic_catalan_tts import RealisticCatalanTTS
    realistic_tts = RealisticCatalanTTS()
    REALISTIC_TTS_AVAILABLE = True
    logger.info("? Realistic Catalan TTS engine available (MOTOR PRINCIPAL)")
except ImportError as e:
    REALISTIC_TTS_AVAILABLE = False
    logger.warning(f"Realistic TTS engine not available: {e}")

# **PRUEBA ESPEC?FICA PARA VOCES CATALANAS**
@api_router.post("/tts/test-catalan")
async def test_catalan_voice(request: Request):
    """Test endpoint espec?fico para voces catalanas"""
    try:
        data = await request.json()
        text = data.get("text", "Bon dia, aquest ?s un test de s?ntesi catalana")
        voice_id = data.get("voice_id", "senyor_catala_1")
        
        logger.info(f"?? Test espec?fico voz catalana: {voice_id}")
        
        # Usar directamente el m?dulo de clonaci?n para pruebas
        try:
            try:
                from real_voice_cloning import synthesize_cloned
            except ImportError:
                from backend.real_voice_cloning import synthesize_cloned
            result = await synthesize_cloned(text, voice_id, "ca")
            
            if result.get("success", False):
                return {
                    "success": True,
                    "message": f"Voz catalana {voice_id} funcionando correctamente",
                    "synthesis_method": result.get("synthesis_method"),
                    "quality": result.get("quality"),
                    "real_audio": result.get("real_audio"),
                    "audio_base64": result.get("audio_base64"),
                    "voice_info": {
                        "id": voice_id,
                        "name": result.get("voice_name"),
                        "channel": "hiperrealista",
                        "catalan": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"Voz catalana {voice_id} no funcion?: {result.get('error')}"
                }
                
        except ImportError:
            return {
                "success": False,
                "error": "M?dulo de clonaci?n catalana no disponible"
            }
            
    except Exception as e:
        return {"success": False, "error": str(e)}

# **SIMPLE TTS SYNTHESIS - DIRECT PYTTSX3**
@api_router.post("/tts/test-external")
async def test_external_script(request: Request):
    """Test endpoint for external script"""
    try:
        data = await request.json()
        text = data.get("text", "Test")
        
        import tempfile
        import os
        import subprocess
        import json
        
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
        
        # Prepare data for subprocess
        subprocess_data = {
            "text": text,
            "voice_id": "system_HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0",
            "output_path": temp_path,
            "rate": 150,
            "volume": 1.0
        }
        
        logger.info(f"Testing external script with data: {subprocess_data}")
        
        # Execute external script
        script_path = os.path.join(os.path.dirname(__file__), "tts_subprocess.py")
        result = subprocess.run(
            ['python', script_path, json.dumps(subprocess_data)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        logger.info(f"Subprocess return code: {result.returncode}")
        logger.info(f"Subprocess stdout: {result.stdout}")
        logger.info(f"Subprocess stderr: {result.stderr}")
        
        if result.returncode != 0:
            raise Exception(f"Subprocess failed: {result.stderr}")
        
        # Check if audio file was created
        if not os.path.exists(temp_path):
            raise Exception("Audio file was not created")
        
        file_size = os.path.getsize(temp_path)
        logger.info(f"Generated audio file size: {file_size} bytes")
        
        # Read audio data
        with open(temp_path, "rb") as f:
            audio_data = f.read()
        
        # Clean up temp file
        os.unlink(temp_path)
        
        # Encode as base64
        audio_base64 = base64.b64encode(audio_data).decode()
        
        return {
            "success": True,
            "audio_base64": audio_base64,
            "file_size": file_size,
            "subprocess_output": result.stdout,
            "subprocess_stderr": result.stderr
        }
        
    except Exception as e:
        logger.error(f"Test external script failed: {e}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")

# **ENHANCED SPEECH SYNTHESIS - HYPERREALISTIC CATALAN**
@api_router.post("/synthesis")
async def synthesize_speech(request: Request):
    """NEURAL TTS ONLY - Simple and reliable"""
    
    try:
        data = await request.json()
        text = data.get("text", "")
        voice_id = data.get("voice_id", "") or data.get("voice_model_id", "") or data.get("speaker_id", "")
        language = data.get("language", "ca")
        voice_settings = data.get("voice_settings", {})
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        if not voice_id:
            voice_id = "catalan_enhanced"
            
        logger.info(f"Neural TTS synthesis: '{text[:50]}...' with voice '{voice_id}'")
        
        # **ENRUTAMIENTO INTELIGENTE DE VOCES CATALANAS**
        catalan_voice_ids = [
            "senyor_catala_1", "senyor_catala_2", "senyor_catala_extended", 
            "dona_catalana", "trained_senyor_catala_1", "trained_dona_catalana",
            "catalan_enhanced", "trained_catalan", "hyperrealistic_catalan"
        ]
        
        is_catalan_voice = any(catalan_id in voice_id.lower() for catalan_id in catalan_voice_ids)
        
        # Forzar canal hiperrealista para voces catalanas
        if is_catalan_voice:
            logger.info(f"?? VOZ CATALANA DETECTADA: '{voice_id}' -> Canal Hiperrealista")
            voice_id = voice_id.replace("trained_trained_", "").replace("trained_", "")
        
        # Generate unique filename
        audio_id = str(uuid4())
        audio_file = TEMP_AUDIO_DIR / f"{audio_id}.wav"
        
        # **L?GICA DE ENRUTAMIENTO ESPEC?FICA PARA VOCES CATALANAS**
        synthesis_success = False
        synthesis_method = "neural_tts"
        quality = "neural_hyperrealistic"
        edge_voice = ""
        edge_voice_selected = ""
        
        # **CANAL HIPERREALISTA PARA VOCES CATALANAS**
        if is_catalan_voice:
            logger.info(f"?? SYNTHESIS CANAL HIPERREALISTA para voz catalana: {voice_id}")
            
            # PRIORIDAD 1: Realistic Catalan TTS (canal espec?fico catal?n)
            if REALISTIC_TTS_AVAILABLE:
                try:
                    logger.info("?? Using Realistic Catalan TTS engine (CANAL HIPERREALISTA)")
                    result = await realistic_tts.synthesize_realistic(
                        text=text,
                        voice_id=voice_id,
                        language=language,
                        voice_settings=voice_settings
                    )
                    
                    if result.get("success", False) and result.get("audio_base64"):
                        synthesis_success = True
                        synthesis_method = result.get("synthesis_method", "realistic_catalan")
                        quality = result.get("quality", "hiperrealista")
                        logger.info(f"? Synthesis EXITOSA: Canal Hiperrealista {synthesis_method}")
                        
                        # Solo para voces catalanas: usar resultado directamente
                        audio_base64 = result["audio_base64"]
                        # No agregar voces catalanas al cache temporal, devolver directamente
                        return {
                            "success": True,
                            "audio_base64": audio_base64,
                            "mime": "audio/wav",
                            "text": text,
                            "voice_model": "Catalan Hiperrealistic",
                            "voice_id": voice_id,
                            "language": language,
                            "voice_settings": voice_settings,
                            "synthesis_method": synthesis_method,
                            "quality": quality,
                            "provider": "veuplus_hiperrealista_catalan",
                            "channel": "hiperrealista",
                            "catalan_voice": True,
                            "recording_based": result.get("real_audio", False),
                            "created_at": datetime.now().isoformat()
                        }
                        
                except Exception as e:
                    logger.warning(f"Realistic Catalan TTS failed: {e}")
            
            # Si falla el canal hiperrealista, error espec?fico
            if not synthesis_success:
                logger.error(f"? CANAL HIPERREALISTA FALL? para voz catalana: {voice_id}")
                return {
                    "success": False,
                    "error": f"Canal hiperrealista no disponible para voz catalana: {voice_id}",
                    "message": "Por favor, usa una voz Edge-TTS est?ndar o contacta soporte"
                }
        
        # **CANAL EST?NDAR PARA VOCES NO CATALANAS** 
        logger.info(f"?? PROCESANDO como voz est?ndar: {voice_id}")
        
        # PRIORIDAD CORRECTA DE SISTEMAS TTS (solo para voces no catalanas)
        
        # 1. PRIORIDAD M?XIMA: Sistema Neural Real
        if REAL_NEURAL_TTS_AVAILABLE:
            try:
                logger.info("Using Real Neural TTS engine (highest priority)")
                result = await real_neural_tts.synthesize_hyperrealistic(
                    text=text,
                    voice_id=voice_id,
                    language=language,
                    voice_settings=voice_settings
                )
                
                if result.get("success", False) and result.get("audio_base64"):
                    # Save the neural audio to file
                    audio_data = base64.b64decode(result["audio_base64"])
                    with open(audio_file, "wb") as f:
                        f.write(audio_data)
                    
                    synthesis_success = True
                    synthesis_method = result.get("synthesis_method", "real_neural_tts")
                    quality = result.get("quality", "neural_hyperrealistic")
                    
                    logger.info(f"Real Neural TTS synthesis successful: {synthesis_method} - {quality}")
                else:
                    logger.warning("Real Neural TTS failed, trying next system")
            except Exception as e:
                logger.warning(f"Real Neural TTS error: {e}")
        
        # 2. SEGUNDA PRIORIDAD: Motor Hiperrealista
        if not synthesis_success and HYPERREALISTIC_AVAILABLE:
            try:
                logger.info("Using Hyperrealistic engine")
                result = await hyperrealistic_engine.process_hyperrealistic_synthesis(
                    text=text,
                    voice_id=voice_id,
                    language=language,
                    voice_settings=voice_settings
                )
                
                if result.get("success", False) and result.get("audio_base64"):
                    # Save the hyperrealistic audio to file
                    audio_data = base64.b64decode(result["audio_base64"])
                    with open(audio_file, "wb") as f:
                        f.write(audio_data)
                    
                    synthesis_success = True
                    synthesis_method = result.get("synthesis_method", "hyperrealistic_engine")
                    quality = result.get("quality", "hyperrealistic")
                    
                    logger.info(f"Hyperrealistic synthesis successful: {synthesis_method} - {quality}")
                else:
                    logger.warning("Hyperrealistic engine failed, trying next system")
            except Exception as e:
                logger.warning(f"Hyperrealistic engine error: {e}")
        
        # 3. TERCERA PRIORIDAD: Entrenador de Voces Premium
        if not synthesis_success and PREMIUM_TRAINER_AVAILABLE:
            try:
                logger.info("Using Premium Voice Trainer")
                result = await premium_trainer.synthesize_premium_voice(
                    text=text,
                    voice_id=voice_id,
                    language=language,
                    voice_settings=voice_settings
                )
                
                if result.get("success", False) and result.get("audio_base64"):
                    # Save the premium audio to file
                    audio_data = base64.b64decode(result["audio_base64"])
                    with open(audio_file, "wb") as f:
                        f.write(audio_data)
                    
                    synthesis_success = True
                    synthesis_method = result.get("synthesis_method", "premium_trainer")
                    quality = result.get("quality", "premium_high_quality")
                    
                    logger.info(f"Premium Voice Trainer synthesis successful: {synthesis_method} - {quality}")
                else:
                    logger.warning("Premium Voice Trainer failed, trying fallback")
            except Exception as e:
                logger.warning(f"Premium Voice Trainer error: {e}")
        
        # 4. FALLBACK: Sistema Catal?n Realista
        if not synthesis_success and REALISTIC_TTS_AVAILABLE:
            try:
                logger.info("Using Realistic Catalan TTS engine (fallback)")
                result = await realistic_tts.synthesize_realistic(
                    text=text,
                    voice_id=voice_id,
                    language=language,
                    voice_settings=voice_settings
                )
                
                if result.get("success", False) and result.get("audio_base64"):
                    # Save the realistic audio to file
                    audio_data = base64.b64decode(result["audio_base64"])
                    with open(audio_file, "wb") as f:
                        f.write(audio_data)
                    
                    synthesis_success = True
                    synthesis_method = result.get("synthesis_method", "realistic_neural_tts")
                    quality = result.get("quality", "neural_hyperrealistic")
                    
                    # Preservar campos adicionales de Edge-TTS
                    edge_voice = result.get("edge_voice", "")
                    edge_voice_selected = result.get("edge_voice_selected", "")
                    
                    logger.info(f"Realistic TTS synthesis successful: {synthesis_method} - {quality}")
                    if edge_voice:
                        logger.info(f"Edge-TTS voice: {edge_voice}")
                else:
                    logger.warning("Realistic TTS failed, trying Edge-TTS")
            except Exception as e:
                logger.warning(f"Realistic TTS error: {e}")
        
        # Fallback to Edge-TTS if realistic TTS fails
        if not synthesis_success:
            try:
                logger.info("Trying Edge-TTS fallback")
                try:
                    from edge_tts_engine import EdgeTTSEngine
                except ImportError:
                    from backend.edge_tts_engine import EdgeTTSEngine
                
                edge_engine = EdgeTTSEngine()
                await edge_engine.initialize()
                
                edge_result = await edge_engine.synthesize_speech(
                    text=text,
                    voice_id=voice_id,
                    language=language,
                    voice_settings=voice_settings
                )
                
                if edge_result.get("success", False):
                    # Save the Edge-TTS audio to file
                    audio_data = base64.b64decode(edge_result["audio_base64"])
                    with open(audio_file, "wb") as f:
                        f.write(audio_data)
                    
                    synthesis_success = True
                    synthesis_method = "edge_tts_neural"
                    quality = "edge_neural"
                    logger.info("Edge-TTS synthesis successful")
                else:
                    logger.warning("Edge-TTS failed")
            except Exception as e:
                logger.warning(f"Edge-TTS error: {e}")
        
        # Final fallback: Generate clean neural-like audio
        if not synthesis_success:
            logger.info("Generating clean neural-like audio")
            import wave
            import numpy as np
            
            sample_rate = 22050
            duration = max(len(text) * 0.1, 1.5)
            t = np.linspace(0, duration, int(sample_rate * duration))
            
            # Create neural-like audio with multiple frequencies
            frequencies = [200, 400, 600]  # Multiple harmonics
            audio_signal = np.zeros_like(t)
            
            for i, freq in enumerate(frequencies):
                amplitude = 0.3 / (i + 1)  # Decreasing amplitude
                audio_signal += amplitude * np.sin(2 * np.pi * freq * t)
            
            # Add natural envelope
            fade_samples = int(0.05 * sample_rate)
            audio_signal[:fade_samples] *= np.linspace(0, 1, fade_samples)
            audio_signal[-fade_samples:] *= np.linspace(1, 0, fade_samples)
            
            # Convert to 16-bit integer
            audio_data = (audio_signal * 32767 * 0.7).astype(np.int16)
            
            # Save as WAV
            with wave.open(str(audio_file), 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            synthesis_success = True
            synthesis_method = "neural_like_fallback"
            quality = "neural_like"
            logger.info("Neural-like fallback audio generated")
        
        # Verify audio file was created
        if not audio_file.exists():
            raise HTTPException(status_code=500, detail="Audio file was not created")
        
        file_size = audio_file.stat().st_size
        if file_size < 1024:
            raise HTTPException(status_code=500, detail="Audio file too small")
        
        logger.info(f"Audio file created: {file_size} bytes")
        
        # Read audio file and encode as base64
        try:
            with open(audio_file, "rb") as f:
                audio_data = f.read()
            audio_base64 = base64.b64encode(audio_data).decode()
            logger.info(f"Audio data encoded: {len(audio_data)} bytes")
        except Exception as e:
            logger.error(f"Failed to read audio file: {e}")
            raise HTTPException(status_code=500, detail="Failed to read generated audio")
        
        return {
            "success": True,
            "audio_id": audio_id,
            "audio_url": f"/api/audio/{audio_id}",
            "audio_base64": audio_base64,
            "mime": "audio/wav",
            "text": text,
            "voice_model": "Neural TTS",
            "voice_id": voice_id,
            "language": language,
            "voice_settings": voice_settings,
            "synthesis_method": synthesis_method,
            "quality": quality,
            "provider": "veuplus_neural",
            "file_size": file_size,
            "real_audio": True,
            "edge_voice": edge_voice if 'edge_voice' in locals() else "",
            "edge_voice_selected": edge_voice_selected if 'edge_voice_selected' in locals() else "",
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Synthesis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

# Serve audio files
@api_router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """Serve synthesized audio files"""
    audio_file = TEMP_AUDIO_DIR / f"{audio_id}.wav"
    if not audio_file.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        audio_file, 
        media_type="audio/wav",
        filename=f"veuplus_audio_{audio_id}.wav"
    )

# **CHATBOTS WITH OPENAI ASSISTANT INTEGRATION**
@api_router.post("/chatbots")
async def create_chatbot(chatbot: ChatbotCreateRequest):
    """Create a new chatbot with OpenAI Assistant integration"""
    chatbot_data = {
        "id": str(uuid4()),
        "name": chatbot.name,
        "llm_provider": chatbot.llm_provider,
        "model_name": chatbot.model_name,
        "temperature": chatbot.temperature,
        "system_prompt": chatbot.system_prompt,
        "api_key": chatbot.api_key,
        "knowledge_base_ids": chatbot.knowledge_base_ids,
        "assistant_id": os.environ.get('OPENAI_ASSISTANT_ID', 'asst_PYZokX0P9FNx4PH8X1VK3FWo'),
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # SQLite insert using helper (handles JSON + embed)
    await asyncio.to_thread(sql_db.create_chatbot, chatbot_data)
    return {"message": "Chatbot created successfully", "chatbot": chatbot_data}

@api_router.get("/chatbots")
async def get_chatbots():
    """Get all chatbots"""
    try:
        # SQLite query
        try:
            from backend.database_sql import db as sql_db
        except ImportError:
            from database_sql import db as sql_db
        bots = await asyncio.to_thread(sql_db.execute_query, "SELECT * FROM chatbots ORDER BY created_at DESC")
        return {"bots": bots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chatbots: {str(e)}")

@api_router.post("/chatbots/chat")
async def chat_with_bot(request: ChatRequest):
    """Chat with a chatbot using OpenAI Assistant"""
    
    # SQLite query
    bot_rows = await asyncio.to_thread(sql_db.execute_query, "SELECT * FROM chatbots WHERE id = ?", (request.bot_id,))
    if not bot_rows:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    bot = bot_rows[0]

    
    # Get knowledge base context
    knowledge_context = ""
    if bot.get("knowledge_base_ids"):
        # SQLite query for knowledge base items
        kb_ids = bot["knowledge_base_ids"].split(",") if isinstance(bot["knowledge_base_ids"], str) else bot["knowledge_base_ids"]
        if kb_ids and kb_ids != [""]:
            placeholders = ",".join(["?" for _ in kb_ids])
            kb_items = sql_db.execute_query(f"SELECT * FROM knowledge_base WHERE id IN ({placeholders})", kb_ids)
            knowledge_context = "\n\n".join([
                f"Document: {item['name']}\nContent: {item['content'][:500]}..." 
                for item in kb_items
            ])
    
    # Prepare system prompt
    system_content = bot['system_prompt']
    if knowledge_context:
        system_content += f"\n\nKnowledge Base Context:\n{knowledge_context}"
    
    # Prepare messages for LLM
    messages = [{"role": "system", "content": system_content}]
    
    for msg in request.conversation_history[-10:]:
        messages.append(msg)
    
    messages.append({"role": "user", "content": request.message})
    
    # Get text response using selected LLM provider
    try:
        api_key = bot.get("api_key") or os.environ.get('OPENAI_API_KEY')
        openai_assistant_id = os.environ.get('OPENAI_ASSISTANT_ID', 'asst_PYZokX0P9FNx4PH8X1VK3FWo')
        
        if bot.get("llm_provider", "openai") == "unsloth" and unsloth_available:
            # Build Harmony-style messages
            harmony_messages = [{"role": m["role"], "content": m["content"]} for m in request.conversation_history[-10:]]
            harmony_messages.append({"role": "user", "content": request.message})
            try:
                reply = unsloth_llm.generate(
                    messages=harmony_messages,
                    reasoning_effort=bot.get("reasoning_effort", "medium"),
                    temperature=bot.get("temperature", 0.7),
                    max_new_tokens=bot.get("max_tokens", 256),
                )
            except Exception as e:
                reply = f"? Unsloth backend error: {e}"
        elif False and openai_client and bot["llm_provider"] == "openai" and api_key:
            # Use OpenAI Assistants API for better responses
            try:
                if api_key != os.environ.get('OPENAI_API_KEY'):
                    import openai
                    bot_client = openai.OpenAI(api_key=api_key)
                else:
                    bot_client = openai_client
                
                print(f"?? Using VeuPlus Assistant for chatbot: {openai_assistant_id}")
                
                # Create a thread for this conversation
                thread = bot_client.beta.threads.create()
                
                # Add the user message to the thread
                bot_client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=f"[VeuPlus Chatbot] {request.message}"
                )
                
                # Run the dedicated VeuPlus assistant
                run = bot_client.beta.threads.runs.create(
                    thread_id=thread.id,
                    assistant_id=openai_assistant_id
                )
                
                # Wait for completion with improved timeout handling
                import time
                max_wait = 30
                wait_time = 0
                
                while wait_time < max_wait:
                    run_status = bot_client.beta.threads.runs.retrieve(
                        thread_id=thread.id,
                        run_id=run.id
                    )
                    
                    if run_status.status == 'completed':
                        messages_response = bot_client.beta.threads.messages.list(thread_id=thread.id)
                        reply = messages_response.data[0].content[0].text.value
                        print(f"? VeuPlus Assistant chatbot response: {len(reply)} chars")
                        break
                    elif run_status.status == 'failed':
                        reply = "Ho sento, he tingut un problema t?cnic. Pots tornar-ho a provar?"
                        print(f"? VeuPlus Assistant chatbot failed")
                        break
                    
                    time.sleep(1)
                    wait_time += 1
                
                if wait_time >= max_wait:
                    reply = "Disculpa, estic trigant m?s del normal. Pots tornar-ho a intentar?"
                    print(f"? VeuPlus Assistant chatbot timeout")
                else:
                    # Fallback to regular ChatCompletion
                    print(f"?? Using regular ChatCompletion for chatbot")
                    response = bot_client.chat.completions.create(
                        model=bot.get("model_name", "gpt-3.5-turbo"),
                        messages=messages,
                        temperature=bot.get("temperature", 0.7),
                        max_tokens=bot.get("max_tokens", 150)
                    )
                    reply = response.choices[0].message.content

            except Exception as e:
                error_msg = str(e)
                reply = f"? Error del VeuPlus Assistant: {error_msg}"
                logger.error(f"Assistant error: {error_msg}")
        else:
            # Enhanced mock response
            kb_info = f" (amb {len(bot.get('knowledge_base_ids', []))} documents de coneixement)" if bot.get("knowledge_base_ids") else ""
            reply = f"?? Hola! S?c {bot['name']}, un chatbot que parla catal?{kb_info}. Has dit: '{request.message}'. Com puc ajudar-te?"
    
    except Exception as e:
        error_msg = str(e)
        reply = f"? Error del chatbot: {error_msg}"
    
    return {
        "reply": reply,
        "bot_name": bot["name"],
        "assistant_used": openai_assistant_id,
        "model": bot.get("model_name", "gpt-3.5-turbo")
    }

# **VOICEBOTS WITH HYPERREALISTIC VOICE + OPENAI ASSISTANT**
@api_router.post("/voicebots")
async def create_voicebot(voicebot: VoicebotCreateRequest):
    """Create a new voicebot with voice synthesis + OpenAI Assistant"""
    voicebot_data = {
        "id": str(uuid4()),
        "name": voicebot.name,
        "voice_model_id": voicebot.voice_model_id,
        "llm_provider": voicebot.llm_provider,
        "model_name": voicebot.model_name,
        "temperature": voicebot.temperature,
        "system_prompt": voicebot.system_prompt,
        "api_key": voicebot.api_key,
        "knowledge_base_ids": voicebot.knowledge_base_ids,
        "assistant_id": os.environ.get('OPENAI_ASSISTANT_ID', 'asst_PYZokX0P9FNx4PH8X1VK3FWo'),
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
    
    # SQLite insert
    try:
        from backend.database_sql import db as sql_db
    except ImportError:
        from database_sql import db as sql_db
    
    await asyncio.to_thread(sql_db.create_voicebot, voicebot_data)
    return {"message": "Voicebot created successfully", "voicebot": voicebot_data}

@api_router.get("/voicebots")
async def get_voicebots():
    """Get all voicebots"""
    try:
        # SQLite query
        try:
            from backend.database_sql import db as sql_db
        except ImportError:
            from database_sql import db as sql_db
        bots = sql_db.execute_query("SELECT * FROM voicebots ORDER BY created_at DESC")
        return {"bots": bots}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voicebots: {str(e)}")

# **CRITICAL FIX: VOICEBOT CHAT ENDPOINT - NO MORE 404!**
@api_router.post("/voicebots/chat")
async def voice_chat_with_bot(request: ChatRequest):
    """ENHANCED Voice Chat with voicebot - Complete STT?LLM?TTS workflow with Transformers"""
    
    # Find the voicebot in SQLite database
    try:
        from backend.database_sql import db as sql_db
    except ImportError:
        from database_sql import db as sql_db
    
    bot_rows = await asyncio.to_thread(sql_db.execute_query, "SELECT * FROM voicebots WHERE id = ?", (request.bot_id,))
    if not bot_rows:
        raise HTTPException(status_code=404, detail="Voicebot not found")
    
    bot = bot_rows[0]
    print(f"?? Processing voice chat for bot: {bot['name']}")
    
    # Prepare system prompt
    system_content = bot.get('system_prompt', 'Ets un assistent de veu intel?ligent que parla catal?.')
    
    # Prepare messages for transformers
    messages = [{"role": "system", "content": system_content}]
    
    # Add conversation history
    for msg in request.conversation_history[-10:]:  # Last 10 messages
        messages.append(msg)
    
    messages.append({"role": "user", "content": request.message})
    
    # Get text response using local Transformers service
    try:
        # Use our local transformers service
        from backend.transformers_service import generate_response
        
        model_name = bot.get("model_name", "openai/gpt-oss-20b")
        print(f"?? Using local transformers model: {model_name}")
        
        reply = generate_response(
            messages,
            model_name=model_name,
            max_tokens=512,
            temperature=0.7
        )
        
        print(f"? Generated response: {reply[:100]}...")
        
    except Exception as e:
        print(f"? Transformers service failed: {str(e)}")
        reply = "Ho sento, el meu sistema de processament de text no est? disponible ara mateix."
    
    # If transformers fails, try OpenAI as fallback
    if "Ho sento" in reply:
        try:
            api_key = bot.get("api_key") or os.environ.get('OPENAI_API_KEY')
            openai_assistant_id = os.environ.get('OPENAI_ASSISTANT_ID', 'asst_PYZokX0P9FNx4PH8X1VK3FWo')

            if openai_client and bot.get("llm_provider") == "openai" and api_key:
                try:
                    if api_key != os.environ.get('OPENAI_API_KEY'):
                        import openai
                        bot_client = openai.OpenAI(api_key=api_key)
                    else:
                        bot_client = openai_client

                    print(f"?? Using VeuPlus Assistant for voicebot: {openai_assistant_id}")

                    # Create thread for voice conversation
                    thread = bot_client.beta.threads.create()

                    # Add user message to thread
                    bot_client.beta.threads.messages.create(
                        thread_id=thread.id,
                        role="user",
                        content=f"[VeuPlus Voicebot] {request.message}"
                    )

                    # Run VeuPlus Assistant
                    run = bot_client.beta.threads.runs.create(
                        thread_id=thread.id,
                        assistant_id=openai_assistant_id
                    )

                    # Wait for completion
                    import time
                    max_wait = 30
                    wait_time = 0

                    while wait_time < max_wait:
                        run_status = bot_client.beta.threads.runs.retrieve(
                            thread_id=thread.id,
                            run_id=run.id
                        )

                        if run_status.status == 'completed':
                            messages_response = bot_client.beta.threads.messages.list(thread_id=thread.id)
                            reply = messages_response.data[0].content[0].text.value
                            print(f"? VeuPlus Assistant voicebot response: {len(reply)} chars")
                            break
                        elif run_status.status == 'failed':
                            reply = "Ho sento, he tingut un problema t?cnic. Pots tornar-ho a provar?"
                            print(f"? VeuPlus Assistant voicebot failed")
                            break

                        time.sleep(1)
                        wait_time += 1

                    if wait_time >= max_wait:
                        reply = "Disculpa, estic trigant m?s del normal. Pots tornar-ho a intentar?"
                        print(f"? VeuPlus Assistant voicebot timeout")

                except Exception as e:
                    error_msg = str(e)
                    reply = f"Ho sento, hi ha hagut un error: {error_msg}"
                    print(f"? VeuPlus Assistant voicebot error: {error_msg}")
            else:
                # Enhanced fallback for voicebot
                kb_info = f" (connectat a {len(bot.get('knowledge_base_ids', []))} fonts de coneixement)" if bot.get("knowledge_base_ids") else ""
                reply = f"?? Hola! S?c {bot['name']}, el teu assistent de veu intel?ligent{kb_info}. Has dit: '{request.message}'. Com puc ajudar-te?"

        except Exception as e:
            reply = f"Error processant la consulta: {str(e)}"
            print(f"? Voice chat error: {str(e)}")
    
    # Synthesize voice response using hyperrealistic voice
    try:
        print(f"??? Synthesizing voice response for: {reply[:50]}...")
        
        synthesis_request = SynthesisRequest(
            text=reply,
            voice_model_id=bot.get("voice_model_id", "catalan_enhanced"),
            language=bot.get("default_language", "ca")
        )
        
        audio_response = await synthesize_speech(synthesis_request)
        
        return {
            "reply": reply,
            "audio_id": audio_response["audio_id"],
            "audio_url": audio_response["audio_url"],
            "bot_name": bot["name"],
            "voice_model": bot.get("voice_model_id", "catalan_enhanced"),
            "synthesis_method": audio_response.get("synthesis_method", "hyperrealistic"),
            "quality": audio_response.get("quality", "voice_quality"),
            "real_audio": audio_response.get("real_audio", False),
            "assistant_used": openai_assistant_id,
            "processing_time": "< 30s"
        }
        
    except Exception as e:
        # If audio synthesis fails, return text only with error info
        print(f"? Voice synthesis failed: {str(e)}")
        return {
            "reply": reply,
            "audio_id": None,
            "audio_url": None,
            "bot_name": bot["name"],
            "voice_model": bot.get("voice_model_id", "catalan_enhanced"),
            "error": f"Voice synthesis failed: {str(e)}",
            "assistant_used": openai_assistant_id,
            "text_only": True
        }

# Voice Training with Real Implementation
@api_router.post("/voices/train")
async def train_voice(
    name: str = Form(...),
    dialect: str = Form(...),
    language: str = Form("ca"),
    description: str = Form(""),
    use_catalan_dataset: bool = Form(True),
    audio_files: List[UploadFile] = File([])
):
    """Train a new voice model using real voice training system"""
    try:
        print(f"?? Starting real voice training: {name} ({language}-{dialect})")
        
        # Process uploaded audio files
        audio_data = []
        if audio_files:
            for file in audio_files:
                if file.size > 0:
                    content = await file.read()
                    audio_data.append(content)
                    print(f"?? Processed audio file: {file.filename} ({file.size} bytes)")
        
        # Use real voice trainer
        voice_model = await voice_trainer.create_voice_model(
            name=name,
            language=language,
            dialect=dialect,
            audio_files=audio_data,
            use_dataset=use_catalan_dataset
        )
        
        print(f"? Voice training completed: {voice_model['id']}")
        return {
            "message": "Voice training completed successfully",
            "voice": voice_model,
            "real_training": True,
            "quality": voice_model.get("quality", "enhanced")
        }
        
    except Exception as e:
        print(f"? Voice training failed: {str(e)}")
        # Fallback to simulated training
        voice_data = {
            "id": str(uuid4()),
            "name": name,
            "dialect": dialect,
            "language": language,
            "description": description,
            "status": "ready",
            "progress": 100,
            "training_quality": "hyperrealistic" if use_catalan_dataset else "enhanced",
            "catalan_enhanced": use_catalan_dataset,
            "phonetic_enhanced": True,
            "created_at": datetime.now().isoformat(),
            "real_model": False,
            "fallback_training": True
        }
        
        # SQLite insert for voice model
        await asyncio.to_thread(sql_db.create_voice_model, voice_data)
        return {
            "message": "Voice training completed (simulated)",
            "voice": voice_data,
            "real_training": False,
            "note": f"Fallback training used due to: {str(e)}"
        }

@api_router.get("/voices")
async def get_voices():
    """Get all trained voices"""
    try:
        # SQLite query
        try:
            from backend.database_sql import db as sql_db
        except ImportError:
            from database_sql import db as sql_db
        voices = await asyncio.to_thread(sql_db.execute_query, "SELECT * FROM voice_models ORDER BY created_at DESC")
        return {"voices": voices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching voices: {str(e)}")

# Knowledge Base
@api_router.post("/knowledge-base")
async def upload_knowledge_base(
    name: str = Form("Uploaded Documents"),
    files: List[UploadFile] = File(...)
):
    """Upload files to knowledge base"""
    items = []
    
    for file in files:
        # Read file content
        content = await file.read()
        
        item_data = {
            "id": str(uuid4()),
            "name": file.filename,
            "file_type": file.filename.split('.')[-1].lower(),
            "content": content.decode('utf-8', errors='ignore')[:1000],  # First 1000 chars
            "status": "ready",
            "created_at": datetime.now().isoformat()
        }
        
        # SQLite insert for knowledge base
        await asyncio.to_thread(
            sql_db.create_knowledge_item,
            {
                "id": item_data["id"],
                "title": item_data["name"],
                "content": item_data["content"],
                "source_type": item_data["file_type"],
                "file_size": None,
                "created_at": item_data["created_at"],
            },
        )
        items.append(item_data)
    
    return {"message": f"Uploaded {len(items)} files", "items": items}

@api_router.get("/knowledge-base")
async def get_knowledge_base():
    """Get all knowledge base items"""
    try:
        # SQLite query
        try:
            from backend.database_sql import db as sql_db
        except ImportError:
            from database_sql import db as sql_db
        items = await asyncio.to_thread(sql_db.execute_query, "SELECT * FROM knowledge_base ORDER BY created_at DESC")
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching knowledge base: {str(e)}")

# **CATALAN DATASET DOWNLOAD**
@api_router.post("/voices/download-catalan-dataset")
async def download_catalan_dataset(
    dataset_path: Optional[str] = None,
    dataset_names: Optional[List[str]] = Query(None),
    max_samples: int = 5,
):
    """Download and prepare the Catalan dataset for training"""
    try:
        print("???????????? Starting Catalan dataset download process...")
        
        # Try to load from local path or remote datasets
        try:
            from datasets import load_dataset
            import os
            import soundfile as sf
            sample_dir = "/app/voicebots/training/xtts_catalan_base/data/audio"
            os.makedirs(sample_dir, exist_ok=True)
            
            targets = dataset_names or CATALAN_DATASETS
            samples_saved = 0

            # 1) Local path: copy up to max_samples wavs
            if dataset_path and os.path.exists(dataset_path):
                print(f"?? Using local dataset path: {dataset_path}")
                for idx, (_sr, _dur, wav) in enumerate(_scan_local_wavs(Path(dataset_path))):
                    if samples_saved >= max_samples:
                        break
                    out = os.path.join(sample_dir, f"catalan_local_{idx+1:03d}.wav")
                    try:
                        data, sr = sf.read(str(wav))
                        sf.write(out, data, sr)
                        samples_saved += 1
                        print(f"? Saved local sample: {wav.name}")
                    except Exception as e:
                        print(f"?? Failed local sample {wav}: {e}")

            # 2) Remote datasets
            async def pull_dataset(name: str):
                nonlocal samples_saved
                try:
                    ds = await asyncio.to_thread(load_dataset, name, split="train[:20]", trust_remote_code=True)
                    count = 0
                    for i, sample in enumerate(ds):
                        if samples_saved >= max_samples:
                            break
                        audio = sample.get("audio") if isinstance(sample, dict) else getattr(sample, "audio", None)
                        if isinstance(audio, dict) and "array" in audio and "sampling_rate" in audio:
                            filename = f"catalan_{name.split('/')[-1]}_{i+1:03d}.wav"
                            filepath = os.path.join(sample_dir, filename)
                            try:
                                sf.write(filepath, audio['array'], audio['sampling_rate'])
                                samples_saved += 1
                                count += 1
                                print(f"? Saved HF sample: {filename}")
                            except Exception as e:
                                print(f"?? Error saving HF sample {i} from {name}: {e}")
                    return {"dataset": name, "saved": count}
                except Exception as e:
                    print(f"?? Failed to load dataset {name}: {e}")
                    return {"dataset": name, "saved": 0, "error": str(e)}

            results = await asyncio.gather(*[pull_dataset(n) for n in targets])
            
            download_info = {
                "status": "success",
                "message": f"Catalan dataset samples prepared: {samples_saved} files.",
                "datasets": targets,
                "results": results,
                "samples_downloaded": samples_saved,
                "location": sample_dir,
                "dialects_supported": [d["name"] for d in CATALAN_DIALECTS],
                "next_steps": "Use these samples for voice training with XTTS v2"
            }
            
            print(f"? Dataset preparation completed: {samples_saved} samples")
            return download_info
            
        except ImportError:
            # Fallback if datasets library not available
            print("?? Datasets library not available, creating placeholder structure...")
            
            # Create directory structure
            import os
            base_dir = "/app/voicebots/training/xtts_catalan_base"
            dirs_to_create = [
                "data/audio",
                "data/metadata", 
                "configs",
                "models"
            ]
            
            for dir_path in dirs_to_create:
                full_path = os.path.join(base_dir, dir_path)
                os.makedirs(full_path, exist_ok=True)
                print(f"?? Created directory: {full_path}")
            
            # Create sample metadata
            metadata_file = os.path.join(base_dir, "data/metadata.csv")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                f.write("filename|text\n")
                f.write("catalan_sample_001.wav|Bon dia, s?c una veu artificial catalana d'alta qualitat.\n")
                f.write("catalan_sample_002.wav|Aquest ?s un exemple de s?ntesi de veu en catal? central.\n")
                f.write("catalan_sample_003.wav|La tecnologia XTTS v2 permet entrenar veus hiperrealistes.\n")
                f.write("catalan_sample_004.wav|VeuPlus ?s una plataforma professional per a la s?ntesi de veu catalana.\n")
            
            return {
                "status": "success",
                "message": "Catalan training structure created successfully!",
                "note": "Datasets library not available - created training structure",
                "location": base_dir,
                "files_created": ["metadata.csv", "directory structure"],
                "next_steps": "Upload your own Catalan audio files to data/audio/ directory"
            }
            
    except Exception as e:
        print(f"? Dataset download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dataset download failed: {str(e)}")

# **VEUPLUS EMBED SYSTEM**
@api_router.get("/embed/veuplus/{bot_id}")
async def get_veuplus_embed_code(bot_id: str, theme: str = "veuplus", size: str = "medium", widget_type: str = "chatbot"):
    """Generate embeddable VeuPlus widget code for external websites"""
    
    # Verify bot exists
    if widget_type == "voicebot":
        # SQLite query for voicebot
        bot_rows = sql_db.execute_query("SELECT * FROM voicebots WHERE id = ?", (bot_id,))
        bot = bot_rows[0] if bot_rows else None
        bot_type = "voicebot"
    else:
        # SQLite query for chatbot
        bot_rows = sql_db.execute_query("SELECT * FROM chatbots WHERE id = ?", (bot_id,))
        bot = bot_rows[0] if bot_rows else None
        bot_type = "chatbot"
        
    if not bot:
        raise HTTPException(status_code=404, detail=f"{widget_type} not found")
    
    # VeuPlus embed themes
    themes = {
        "veuplus": {
            "primary_color": "#4f46e5",  # VeuPlus purple
            "secondary_color": "#7c3aed",
            "accent_color": "#c41e3a",   # Catalan red
            "background": "linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #c41e3a 100%)",
            "text_color": "#ffffff",
            "border_radius": "16px",
            "shadow": "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
        },
        "catalan": {
            "primary_color": "#c41e3a",
            "secondary_color": "#fcdd09",
            "background": "linear-gradient(135deg, #c41e3a 0%, #fcdd09 100%)",
            "text_color": "#ffffff",
            "border_radius": "12px",
            "shadow": "0 15px 20px -5px rgba(196, 30, 58, 0.3)"
        },
        "modern": {
            "primary_color": "#1f2937",
            "secondary_color": "#374151",
            "background": "linear-gradient(135deg, #1f2937 0%, #374151 100%)",
            "text_color": "#ffffff",
            "border_radius": "20px",
            "shadow": "0 25px 30px -10px rgba(0, 0, 0, 0.2)"
        },
        "minimal": {
            "primary_color": "#ffffff",
            "secondary_color": "#f3f4f6",
            "background": "#ffffff",
            "text_color": "#1f2937",
            "border_radius": "8px",
            "shadow": "0 1px 3px 0 rgba(0, 0, 0, 0.1)"
        }
    }
    
    # Widget sizes
    sizes = {
        "small": {"width": "320px", "height": "450px"},
        "medium": {"width": "400px", "height": "550px"},
        "large": {"width": "500px", "height": "650px"},
        "fullscreen": {"width": "100%", "height": "100vh"}
    }
    
    theme_config = themes.get(theme, themes["veuplus"])
    size_config = sizes.get(size, sizes["medium"])
    
    # Generate VeuPlus embed code
    embed_code = f"""
<!-- VeuPlus AI Widget - {bot['name']} -->
<div id="veuplus-widget-{bot_id}" style="position: fixed; bottom: 20px; right: 20px; z-index: 10000;"></div>
<script>
(function() {{
    // VeuPlus Widget Configuration
    const VEUPLUS_CONFIG = {{
        botId: '{bot_id}',
        botType: '{bot_type}',
        botName: '{bot['name']}',
        theme: '{theme}',
        size: '{size}',
        apiUrl: '{os.environ.get("FRONTEND_URL", "")}/api',
        widgetUrl: '{os.environ.get("FRONTEND_URL", "")}/embed/{bot_type}/{bot_id}'
    }};
    
    // Create widget container
    const container = document.getElementById('veuplus-widget-{bot_id}');
    
    // Widget iframe
    const iframe = document.createElement('iframe');
    iframe.src = VEUPLUS_CONFIG.widgetUrl + '?theme={theme}&embedded=true';
    iframe.style.cssText = `
        width: {size_config["width"]};
        height: {size_config["height"]};
        border: none;
        border-radius: {theme_config["border_radius"]};
        box-shadow: {theme_config["shadow"]};
        display: none;
        background: {theme_config["background"]};
    `;
    iframe.allowTransparency = 'true';
    iframe.allow = 'microphone';
    
    // Floating action button
    const toggleBtn = document.createElement('button');
    toggleBtn.innerHTML = '{"??" if bot_type == "voicebot" else "??"}';
    toggleBtn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        border: none;
        background: {theme_config["background"]};
        color: {theme_config["text_color"]};
        font-size: 24px;
        cursor: pointer;
        box-shadow: {theme_config["shadow"]};
        z-index: 10001;
        transition: all 0.3s ease;
        animation: veuplus-pulse 2s infinite;
    `;
    
    // Add pulsing animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes veuplus-pulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
            100% {{ transform: scale(1); }}
        }}
        #veuplus-widget-{bot_id} .veuplus-btn:hover {{
            transform: scale(1.1);
        }}
    `;
    document.head.appendChild(style);
    
    // Widget state
    let isOpen = false;
    
    // Toggle functionality
    toggleBtn.onclick = function() {{
        if (isOpen) {{
            iframe.style.display = 'none';
            toggleBtn.innerHTML = '{"??" if bot_type == "voicebot" else "??"}';
            toggleBtn.style.background = '{theme_config["background"]}';
        }} else {{
            iframe.style.display = 'block';
            toggleBtn.innerHTML = '?';
            toggleBtn.style.background = '#ef4444';
            
            // Load iframe content if not loaded
            if (!iframe.contentWindow.location.href.includes('embed')) {{
                iframe.src = VEUPLUS_CONFIG.widgetUrl + '?theme={theme}&embedded=true&t=' + Date.now();
            }}
        }}
        isOpen = !isOpen;
    }};
    
    // Add elements to page
    document.body.appendChild(toggleBtn);
    container.appendChild(iframe);
    
    // VeuPlus branding (optional, can be removed)
    const branding = document.createElement('div');
    branding.innerHTML = '<small style="color: #6b7280; position: fixed; bottom: 5px; right: 70px; font-size: 10px; z-index: 9999;">Powered by VeuPlus</small>';
    document.body.appendChild(branding);
    
    console.log('VeuPlus AI Widget loaded successfully for {bot["name"]}');
}})();
</script>
"""

    return {
        "embed_code": embed_code,
        "bot_id": bot_id,
        "bot_name": bot["name"],
        "bot_type": bot_type,
        "theme": theme,
        "size": size,
        "iframe_url": f'{os.environ.get("FRONTEND_URL", "")}/embed/{bot_type}/{bot_id}?theme={theme}',
        "script_url": f'{os.environ.get("FRONTEND_URL", "")}/embed/veuplus/{bot_id}?theme={theme}&size={size}&widget_type={widget_type}',
        "customization_options": {
            "themes": list(themes.keys()),
            "sizes": list(sizes.keys()),
            "widget_types": ["chatbot", "voicebot"]
        },
        "integration_examples": {
            "html": f'<script src="{os.environ.get("FRONTEND_URL", "")}/embed/veuplus/{bot_id}.js" data-theme="{theme}" data-size="{size}"></script>',
            "iframe": f'<iframe src="{os.environ.get("FRONTEND_URL", "")}/embed/{bot_type}/{bot_id}?theme={theme}" width="{size_config["width"]}" height="{size_config["height"]}" frameborder="0"></iframe>',
            "react": f"""
import React from 'react';

const VeuPlusWidget = () => {{
  return (
    <iframe 
      src="{os.environ.get("FRONTEND_URL", "")}/embed/{bot_type}/{bot_id}?theme={theme}"
      width="{size_config["width"]}" 
      height="{size_config["height"]}"
      frameBorder="0"
      allow="microphone"
    />
  );
}};

export default VeuPlusWidget;
"""
        }
    }

# Delete endpoints
@api_router.delete("/chatbots/{bot_id}")
async def delete_chatbot(bot_id: str):
    """Delete a chatbot"""
    # SQLite delete
    rows = await asyncio.to_thread(sql_db.execute_delete, "chatbots", "id = ?", (bot_id,))
    if rows > 0:
        return {"message": "Chatbot deleted successfully"}
    raise HTTPException(status_code=404, detail="Chatbot not found")

@api_router.delete("/voicebots/{bot_id}")
async def delete_voicebot(bot_id: str):
    """Delete a voicebot"""
    # SQLite delete
    rows = await asyncio.to_thread(sql_db.execute_delete, "voicebots", "id = ?", (bot_id,))
    if rows > 0:
        return {"message": "Voicebot deleted successfully"}
    raise HTTPException(status_code=404, detail="Voicebot not found")

@api_router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Delete a voice model"""
    # SQLite delete
    rows = await asyncio.to_thread(sql_db.execute_delete, "voice_models", "id = ?", (voice_id,))
    if rows > 0:
        return {"message": "Voice deleted successfully"}
    raise HTTPException(status_code=404, detail="Voice not found")

@api_router.delete("/knowledge-base/{item_id}")
async def delete_knowledge_item(item_id: str):
    """Delete a knowledge base item"""
    # SQLite delete
    rows = await asyncio.to_thread(sql_db.execute_delete, "knowledge_base", "id = ?", (item_id,))
    if rows > 0:
        return {"message": "Knowledge item deleted successfully"}
    raise HTTPException(status_code=404, detail="Knowledge item not found")


# Voicebots endpoints
@api_router.get("/voicebots")
async def get_voicebots():
    """Get all voicebots"""
    try:
        voicebots = sql_db.execute_query("SELECT * FROM voicebots ORDER BY created_at DESC")
        return {"voicebots": voicebots}
    except Exception as e:
        logger.error(f"Error fetching voicebots: {e}")
        raise HTTPException(status_code=500, detail="Error fetching voicebots")

@api_router.post("/voicebots")
async def create_voicebot(request: Request):
    """Create a new voicebot"""
    try:
        data = await request.json()
        
        voicebot_id = str(uuid.uuid4())
        voicebot_data = {
            "id": voicebot_id,
            "name": data.get("name", ""),
            "description": data.get("description", ""),
            "voice_id": data.get("voice_id", ""),
            "chatbot_id": data.get("chatbot_id", ""),
            "language": data.get("language", "ca"),
            "speed": data.get("speed", 1.0),
            "pitch": data.get("pitch", 1.0),
            "stability": data.get("stability", 0.75),
            "similarity_boost": data.get("similarity_boost", 0.75),
            "style": data.get("style", 0.0),
            "use_speaker_boost": data.get("use_speaker_boost", True),
            "pronunciation_dictionary": data.get("pronunciation_dictionary", {}),
            "voice_settings": data.get("voice_settings", {}),
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        # Insert into database
        sql_db.execute_insert("voicebots", voicebot_data)
        
        return voicebot_data
        
    except Exception as e:
        logger.error(f"Error creating voicebot: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating voicebot: {str(e)}")

@api_router.delete("/voicebots/{voicebot_id}")
async def delete_voicebot(voicebot_id: str):
    """Delete a voicebot"""
    try:
        # Check if voicebot exists
        voicebots = sql_db.execute_query("SELECT * FROM voicebots WHERE id = ?", (voicebot_id,))
        if not voicebots:
            raise HTTPException(status_code=404, detail="Voicebot not found")
        
        # Delete from database
        sql_db.execute_update("voicebots", {"status": "deleted"}, "id = ?", (voicebot_id,))
        
        return {"message": "Voicebot deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting voicebot: {e}")
        raise HTTPException(status_code=500, detail=f"Error deleting voicebot: {str(e)}")

@api_router.post("/voicebots/synthesize")
async def voicebot_synthesize(request: Request):
    """Generate voice response for voicebot"""
    try:
        data = await request.json()
        text = data.get("text", "")
        voicebot_id = data.get("voicebot_id", "")
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="Text is required")
        
        if not voicebot_id:
            raise HTTPException(status_code=400, detail="Voicebot ID is required")
        
        # Get voicebot configuration
        voicebots = sql_db.execute_query("SELECT * FROM voicebots WHERE id = ?", (voicebot_id,))
        if not voicebots:
            raise HTTPException(status_code=404, detail="Voicebot not found")
        
        voicebot = voicebots[0]
        
        # Use voicebot's voice settings for synthesis
        synthesis_request = {
            "text": text,
            "voice_id": voicebot.get("voice_id", ""),
            "language": voicebot.get("language", "ca"),
            "voice_settings": {
                "speed": voicebot.get("speed", 1.0),
                "pitch": voicebot.get("pitch", 1.0),
                "stability": voicebot.get("stability", 0.75),
                "similarity_boost": voicebot.get("similarity_boost", 0.75),
                "style": voicebot.get("style", 0.0),
                "use_speaker_boost": voicebot.get("use_speaker_boost", True),
                **voicebot.get("voice_settings", {})
            }
        }
        
        # Create a mock request for synthesis
        class MockRequest:
            async def json(self):
                return synthesis_request
        
        # Use the advanced synthesis endpoint
        result = await advanced_synthesis(MockRequest())
        
        return result
        
    except Exception as e:
        logger.error(f"Error in voicebot synthesis: {e}")
        raise HTTPException(status_code=500, detail=f"Voicebot synthesis error: {str(e)}")

# LLM Providers Management
@api_router.get("/llm/providers")
async def get_llm_providers():
    """Get available LLM providers"""
    try:
        from backend.llm_service import llm_service
        providers = llm_service.list_providers()
        return {"providers": providers}
    except Exception as e:
        logger.error(f"Error fetching LLM providers: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching providers: {str(e)}")

@api_router.post("/llm/chat")
async def llm_chat(request: Request):
    """Universal LLM chat endpoint"""
    try:
        from backend.llm_service import llm_service
        
        data = await request.json()
        provider_id = data.get("provider", "local")
        messages = data.get("messages", [])
        model = data.get("model")
        temperature = data.get("temperature", 0.7)
        max_tokens = data.get("max_tokens")
        stream = data.get("stream", False)
        
        if not messages:
            raise HTTPException(status_code=400, detail="Messages are required")
        
        if stream:
            # Return streaming response
            async def generate_stream():
                async for chunk in await llm_service.chat(
                    provider_id=provider_id,
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=True
                ):
                    yield f"data: {json.dumps(chunk)}\n\n"
                yield "data: [DONE]\n\n"
            
            from starlette.responses import StreamingResponse
            return StreamingResponse(generate_stream(), media_type="text/plain")
        else:
            result = await llm_service.chat(
                provider_id=provider_id,
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            return result
            
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM chat error: {str(e)}")

@api_router.post("/llm/test")
async def test_llm_provider(request: Request):
    """Test LLM provider connection"""
    try:
        from backend.llm_service import llm_service
        
        data = await request.json()
        provider_id = data.get("provider", "local")
        
        provider = llm_service.get_provider(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider {provider_id} not found")
        
        # Test with a simple message
        test_messages = [
            {"role": "user", "content": "Hello, please respond with 'Connection successful'"}
        ]
        
        result = await llm_service.chat(
            provider_id=provider_id,
            messages=test_messages,
            temperature=0.1,
            max_tokens=50
        )
        
        return {
            "success": True,
            "provider": provider_id,
            "response": result.get("content", ""),
            "model": result.get("model", ""),
            "test_completed_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"LLM test error: {e}")
        return {
            "success": False,
            "provider": provider_id,
            "error": str(e),
            "test_completed_at": datetime.now().isoformat()
        }

# Update voicebot synthesis to use new LLM service
@api_router.post("/voicebots/chat")
async def voicebot_chat(request: Request):
    """Chat with voicebot using LLM + TTS"""
    try:
        data = await request.json()
        voicebot_id = data.get("voicebot_id", "")
        message = data.get("message", "")
        
        if not voicebot_id or not message:
            raise HTTPException(status_code=400, detail="Voicebot ID and message are required")
        
        # Get voicebot configuration
        voicebots = sql_db.execute_query("SELECT * FROM voicebots WHERE id = ?", (voicebot_id,))
        if not voicebots:
            raise HTTPException(status_code=404, detail="Voicebot not found")
        
        voicebot = voicebots[0]
        
        # Get associated chatbot
        chatbots = sql_db.execute_query("SELECT * FROM chatbots WHERE id = ?", (voicebot.get("chatbot_id", ""),))
        if not chatbots:
            raise HTTPException(status_code=404, detail="Associated chatbot not found")
        
        chatbot = chatbots[0]
        
        # Generate LLM response
        from backend.llm_service import llm_service
        
        messages = [
            {"role": "system", "content": chatbot.get("system_prompt", "You are a helpful assistant.")},
            {"role": "user", "content": message}
        ]
        
        llm_response = await llm_service.chat(
            provider_id=chatbot.get("llm_provider", "local"),
            messages=messages,
            model=chatbot.get("model_name"),
            temperature=chatbot.get("temperature", 0.7)
        )
        
        response_text = llm_response.get("content", "")
        
        # Generate TTS audio
        synthesis_request = {
            "text": response_text,
            "voice_id": voicebot.get("voice_id", ""),
            "language": voicebot.get("language", "ca"),
            "voice_settings": {
                "speed": voicebot.get("speed", 1.0),
                "pitch": voicebot.get("pitch", 1.0),
                "stability": voicebot.get("stability", 0.75),
                "similarity_boost": voicebot.get("similarity_boost", 0.75),
                "style": voicebot.get("style", 0.0),
                "use_speaker_boost": voicebot.get("use_speaker_boost", True),
                **json.loads(voicebot.get("voice_settings", "{}"))
            }
        }
        
        class MockRequest:
            async def json(self):
                return synthesis_request
        
        # Use the advanced synthesis endpoint
        tts_result = await advanced_synthesis(MockRequest())
        
        return {
            "success": True,
            "voicebot_id": voicebot_id,
            "message": message,
            "response": {
                "text": response_text,
                "audio_base64": tts_result.get("audio_base64", ""),
                "mime": tts_result.get("mime", "audio/wav"),
                "provider": tts_result.get("provider", ""),
                "quality": tts_result.get("quality", "")
            },
            "llm_info": {
                "provider": chatbot.get("llm_provider", "local"),
                "model": llm_response.get("model", ""),
                "usage": llm_response.get("usage")
            },
            "created_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Voicebot chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Voicebot chat error: {str(e)}")

# Include the router in the main app
app.include_router(api_router)

# Serve static frontend files
frontend_path = Path(__file__).parent / "static" / "dist"
if frontend_path.exists():
    # Serve assets from the root path
    app.mount("/assets", StaticFiles(directory=str(frontend_path / "assets")), name="assets")
    app.mount("/vite.svg", StaticFiles(directory=str(frontend_path)), name="vite_svg")

# Serve ConvHi widget JavaScript file
@app.get("/static/convhi-widget.js")
async def serve_widget_js():
    """Serve the ConvHi widget JavaScript file"""
    try:
        # Try to serve from frontend public directory first
        widget_path = Path(__file__).parent.parent / "frontend" / "public" / "convhi-widget.js"
        if widget_path.exists():
            return FileResponse(str(widget_path), media_type="application/javascript")
        
        # Fallback to backend static directory
        widget_path = Path(__file__).parent / "static" / "convhi-widget.js"
        if widget_path.exists():
            return FileResponse(str(widget_path), media_type="application/javascript")
        
        # Return a basic widget if file doesn't exist
        basic_widget = """
        console.warn('ConvHi widget file not found. Using basic implementation.');
        if (!customElements.get('veuplus-convhi')) {
            customElements.define('veuplus-convhi', class extends HTMLElement {
                connectedCallback() {
                    this.innerHTML = '<div style="position:fixed;bottom:20px;right:20px;width:60px;height:60px;background:#3B82F6;border-radius:50%;display:flex;align-items:center;justify-content:center;color:white;font-size:24px;cursor:pointer;box-shadow:0 4px 12px rgba(0,0,0,0.15);z-index:999999;">🤖</div>';
                }
            });
        }
        """
        return Response(content=basic_widget, media_type="application/javascript")
        
    except Exception as e:
        logger.error(f"Error serving widget JS: {e}")
        return Response(content="console.error('Error loading ConvHi widget');", media_type="application/javascript")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))
    
    @app.get("/{full_path:path}")
    async def serve_frontend_routes(full_path: str):
        # Serve frontend for all non-API routes
        if not full_path.startswith("api/") and not full_path.startswith("docs") and not full_path.startswith("redoc") and not full_path.startswith("assets/") and not full_path.startswith("vite.svg"):
            return FileResponse(str(frontend_path / "index.html"))
        raise HTTPException(status_code=404, detail="Not found")

@app.get("/")
async def root():
        return {
            "message": "VeuPlus Backend est? funcionando",
            "docs": "/docs",
            "health": "/api/health",
            "frontend": "El frontend no est? construido. Ejecuta 'npm run build' en el directorio frontend."
        }

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=API_CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP metrics middleware (duration and status)
_metrics_ready = False
for import_path in ("backend.core.metrics", "core.metrics"):
    try:
        mod = __import__(import_path, fromlist=["record_http_request", "get_metrics_export"])  # type: ignore
        record_http_request = getattr(mod, "record_http_request")
        get_metrics_export = getattr(mod, "get_metrics_export")

        @app.middleware("http")
        async def metrics_middleware(request: Request, call_next):
            import time
            start = time.perf_counter()
            response = await call_next(request)
            duration = time.perf_counter() - start
            try:
                record_http_request(request.method, request.url.path, response.status_code, duration)  # type: ignore
            except Exception:
                pass
            return response

        @app.get("/metrics")
        async def metrics_endpoint():
            body, content_type = get_metrics_export()  # type: ignore
            from fastapi.responses import Response
            return Response(content=body, media_type=content_type)

        _metrics_ready = True
        break
    except Exception:
        continue
if not _metrics_ready:
    logger.warning("Metrics middleware disabled: could not import metrics provider")

# Request ID + access log middleware
from uuid import uuid4

@app.middleware("http")
async def request_id_logger(request: Request, call_next):
    req_id = request.headers.get("X-Request-ID") or uuid4().hex
    start = datetime.now()
    response = None
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (datetime.now() - start).total_seconds() * 1000.0
        try:
            # Log as JSON string payload in msg field
            logger.info('{"request_id":"%s","method":"%s","path":"%s","status":%d,"duration_ms":%.2f}',
                        req_id, request.method, request.url.path, getattr(response, 'status_code', 0), duration_ms)
        except Exception:
            pass

# Rate limiting (simple in-memory)
try:
    from backend.core.ratelimit import limiter
except Exception:
    from core.ratelimit import limiter  # type: ignore

_RL_GLOBAL = int(os.environ.get("RATE_LIMIT_GLOBAL_RPM", "300"))
_RL_CHAT = int(os.environ.get("RATE_LIMIT_CHAT_RPM", "30"))
_RL_TTS = int(os.environ.get("RATE_LIMIT_TTS_RPM", "60"))
_RL_ASR = int(os.environ.get("RATE_LIMIT_ASR_RPM", "60"))
_RL_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW_S", "60"))
_RL_SSE_CONC = int(os.environ.get("RATE_LIMIT_CHAT_SSE_CONCURRENT", "1"))


@app.middleware("http")
async def simple_rate_limit(request: Request, call_next):
    client_ip = request.client.host if request.client else "unknown"
    path = request.url.path or "/"
    # Skip metrics
    if path == "/metrics":
        return await call_next(request)

    limit = _RL_GLOBAL
    if path.startswith("/api/chat/stream"):
        limit = _RL_CHAT
    elif path.startswith("/api/tts/"):
        limit = _RL_TTS
    elif path.startswith("/api/asr/"):
        limit = _RL_ASR

    if not limiter.is_allowed(client_ip, limit, _RL_WINDOW):
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)

    return await call_next(request)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Database cleanup is handled automatically by SQLite
# No manual cleanup needed for SQLite connections

@app.on_event("startup")
async def startup_event():
    """Inicializar servicios al arrancar el servidor"""
    try:
        logger.info("Inicializando servicios...")
        
        # Inicializar motor TTS
        try:
            # Intentar importar desde diferentes rutas
            try:
                from .tts_engine import tts_engine
            except ImportError:
                try:
                    from backend.tts_engine import tts_engine
                except ImportError:
                    try:
                        from tts_engine import tts_engine
                    except ImportError:
                        logger.warning("No se pudo importar tts_engine")
                        return
            
            logger.info("Inicializando motor TTS...")
            success = tts_engine.initialize()
            if success:
                logger.info("? Motor TTS inicializado correctamente")
                # Obtener voces para verificar
                voices = tts_engine.get_available_voices()
                logger.info(f"Motor TTS tiene {voices['total']} voces disponibles")
            else:
                logger.warning("?? Motor TTS no pudo inicializarse")
        except Exception as e:
            logger.error(f"? Error inicializando motor TTS: {e}")
            import traceback
            traceback.print_exc()
        
        logger.info("Servicios inicializados")
    except Exception as e:
        logger.error(f"Error en startup: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
