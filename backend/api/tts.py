from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional, List, Dict, Any
import base64
import os
from datetime import datetime

router = APIRouter(prefix="/api/tts", tags=["TTS"])


class TTSRequest(BaseModel):
    text: str
    voice_model_id: Optional[str] = None
    language: Optional[str] = "ca"
    speaker_id: Optional[str] = None

    @field_validator("text")
    @classmethod
    def _validate_text(cls, v: str):
        if not v or not v.strip():
            raise ValueError("text cannot be empty")
        if len(v) > 1000:
            raise ValueError("text too long (max 1000 chars)")
        return v


@router.post("/synthesize")
async def synthesize(req: TTSRequest):
    """Placeholder TTS endpoint compatible con la API existente.
    Genera una respuesta simulada (silencio) cuando no hay motor TTS instalado,
    manteniendo el contrato de la ruta. En producción se sustituye por XTTS/Coqui.
    """
    try:
        # Si no hay motor TTS, devolvemos un wav vacío de 1s a 16kHz
        sr = 16000
        duration = 1
        num_samples = sr * duration
        pcm_bytes = b"\x00\x00" * num_samples
        import wave
        from io import BytesIO

        buf = BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sr)
            wf.writeframes(pcm_bytes)

        audio_b64 = base64.b64encode(buf.getvalue()).decode()
        return {
            "audio_base64": audio_b64,
            "mime": "audio/wav",
            "voice_model_id": req.voice_model_id or "placeholder",
            "speaker_id": req.speaker_id or "unknown",
            "created_at": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/voices")
async def list_voices() -> Dict[str, Any]:
    """Lista voces/locutores detectados tras preprocesado.
    Busca `speakers.json` en `backend/preprocessed_data/*/audio/` y agrega conteos.
    """
    try:
        import glob
        from pathlib import Path
        base = Path("backend/preprocessed_data")
        voices: Dict[str, int] = {}
        for path in base.glob("*/audio/speakers.json"):
            try:
                import json
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for spk, cnt in data.get("speakers", {}).items():
                    voices[spk] = voices.get(spk, 0) + int(cnt)
            except Exception:
                continue
        # Attach preview URLs if exist under /static/voices/<speaker_id>_sample.wav
        from pathlib import Path
        static_dir = Path("backend/static/voices")
        items = []
        for k, v in sorted(voices.items(), key=lambda kv: kv[0]):
            preview_file = static_dir / f"{k}_sample.wav"
            sample_url = f"/static/voices/{k}_sample.wav" if preview_file.exists() else None
            items.append({"speaker_id": k, "samples": v, "sample_url": sample_url})
        return {"voices": items, "total": len(items)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

