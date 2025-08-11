import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import tempfile

asr_router = APIRouter(prefix="/api/asr", tags=["ASR"])

_WHISPER_AVAILABLE = False
_MODEL = None

MODEL_NAME = os.environ.get("ASR_MODEL", "small")

def _load_whisper():
    global _WHISPER_AVAILABLE, _MODEL
    if _WHISPER_AVAILABLE:
        return
    try:
        from faster_whisper import WhisperModel
        device = "cuda" if os.environ.get("ASR_DEVICE", "cuda") == "cuda" else "cpu"
        compute_type = os.environ.get("ASR_COMPUTE_TYPE", "float16" if device == "cuda" else "int8")
        _MODEL = WhisperModel(MODEL_NAME, device=device, compute_type=compute_type)
        _WHISPER_AVAILABLE = True
    except Exception:
        _WHISPER_AVAILABLE = False


class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None


@asr_router.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), language: Optional[str] = None):
    _load_whisper()
    if not _WHISPER_AVAILABLE:
        raise HTTPException(status_code=503, detail="ASR backend not available")

    from faster_whisper import WhisperModel  # noqa: F401

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        data = await file.read()
        tmp.write(data)
        tmp.flush()
        path = tmp.name

    segments, info = _MODEL.transcribe(path, language=language)
    text = " ".join([seg.text for seg in segments]).strip()
    return TranscriptionResponse(text=text, language=info.language)




