from __future__ import annotations

from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import os

router = APIRouter(prefix="/api/asr", tags=["ASR"])


class ASRResponse(BaseModel):
    text: str
    language: str
    created_at: str


# Determine max upload from server or env
try:
    from backend.server import MAX_UPLOAD_SIZE_MB as _MAX
except Exception:
    try:
        from server import MAX_UPLOAD_SIZE_MB as _MAX  # type: ignore
    except Exception:
        _MAX = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "20"))


@router.post("/transcribe", response_model=ASRResponse)
async def transcribe(file: UploadFile = File(...), language: Optional[str] = "ca"):
    """ASR placeholder que devuelve metadatos, para mantener contrato.
    En producción se conecta a Whisper/Faster-Whisper.
    """
    try:
        # No procesamos audio real si el backend no tiene whisper instalado.
        # Validamos tamaño básico y extensión.
        data = await file.read()
        if len(data) > _MAX * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")
        # Eco de nombre
        return ASRResponse(text=f"[transcript of {file.filename}]", language=language or "ca", created_at=datetime.utcnow().isoformat())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


