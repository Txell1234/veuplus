#!/usr/bin/env python3
"""
Utility engine for hyperrealistic (mock) voices.

Until GPU-based inference is available we reuse the locally processed
recordings from `backend/training_data/<voice_id>/processed.wav`.
This allows the platform to serve catalogued Catalan voices without
falling back to Edge-TTS.
"""
from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


BACKEND_DIR = Path(__file__).resolve().parent
TRAINING_DATA_DIR = BACKEND_DIR / "training_data"
VOICE_MODELS_DIR = BACKEND_DIR / "voice_models"


def _safe_read(path: Path) -> Optional[bytes]:
    try:
        return path.read_bytes()
    except FileNotFoundError:
        return None


def _load_json(path: Path) -> Optional[Dict]:
    try:
        import json
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def _listdir(path: Path) -> Iterable[Path]:
    if path.exists():
        yield from path.iterdir()
    else:
        return []


@dataclass
class VoiceInfo:
    voice_id: str
    name: str
    description: str
    gender: Optional[str]
    source: str  # training_data or voice_models
    audio_path: Path
    mime_type: str
    metadata: Dict
    mock: bool = True
    notes: Optional[str] = None


class HyperVoiceEngine:
    """
    Minimal engine that serves prerecorded audio for hyperrealistic voices.
    Designed to be replaced by a neural inference backend once GPU models
    are available.
    """

    def __init__(self) -> None:
        self._voices: Dict[str, VoiceInfo] = {}
        self.refresh()

    @staticmethod
    def _clean_voice_id(voice_id: str) -> str:
        cleaned = voice_id.replace("trained_trained_", "").replace("trained_", "")
        return cleaned.strip()

    def refresh(self) -> None:
        self._voices = {}
        self._load_training_data()
        self._load_voice_models()

    # Inventory building -------------------------------------------------
    def _load_training_data(self) -> None:
        for voice_dir in _listdir(TRAINING_DATA_DIR):
            if not voice_dir.is_dir():
                continue

            metadata = _load_json(voice_dir / "metadata.json") or {}
            voice_id = self._clean_voice_id(metadata.get("id") or voice_dir.name)

            audio_path = voice_dir / "processed.wav"
            if not audio_path.exists():
                continue

            info = VoiceInfo(
                voice_id=voice_id,
                name=(metadata.get("description") or voice_id).split("(")[0].strip(),
                description=metadata.get("description")
                or "Mostra enregistrada (mock).",
                gender=metadata.get("gender"),
                source="training_data",
                audio_path=audio_path,
                mime_type="audio/wav",
                metadata=metadata,
                mock=True,
                notes="Utilitza enregistrament processat. El text d'entrada s'ignora fins que hi hagi model XTTS.",
            )
            self._voices[voice_id] = info

    def _load_voice_models(self) -> None:
        """
        Some experiments guardaven mostres dins `backend/voice_models/<uuid>/sample.wav`.
        Les carreguem com a veus addicionals només si no hi ha veu homònima a training_data.
        """
        for voice_dir in _listdir(VOICE_MODELS_DIR):
            if not voice_dir.is_dir():
                continue

            sample = next(
                (p for p in list(voice_dir.glob("*.wav")) + list(voice_dir.glob("*.mp3"))),
                None,
            )
            if not sample:
                continue

            metadata = _load_json(voice_dir / "metadata.json") or {}
            voice_id = self._clean_voice_id(metadata.get("id") or voice_dir.name)

            if voice_id in self._voices:
                # Prefer training_data version
                continue

            mime = "audio/mpeg" if sample.suffix.lower() == ".mp3" else "audio/wav"
            info = VoiceInfo(
                voice_id=voice_id,
                name=metadata.get("name") or voice_id,
                description=metadata.get("description")
                or "Mostra importada de voice_models (mock).",
                gender=metadata.get("gender"),
                source="voice_models",
                audio_path=sample,
                mime_type=mime,
                metadata=metadata,
                mock=True,
                notes="Mostra extreta de voice_models. Ajustar quan hi hagi model neuronal.",
            )
            self._voices[voice_id] = info

    # Public API ---------------------------------------------------------
    def list_voices(self) -> List[Dict]:
        return [
            {
                "id": info.voice_id,
                "name": info.name,
                "description": info.description,
                "gender": info.gender,
                "source": info.source,
                "mock": info.mock,
                "notes": info.notes,
                "duration": info.metadata.get("duration"),
                "sample_rate": info.metadata.get("sample_rate"),
            }
            for info in self._voices.values()
        ]

    def synthesize(self, voice_id: str) -> Dict:
        cleaned = self._clean_voice_id(voice_id)
        info = self._voices.get(cleaned)
        if not info:
            return {"success": False, "error": f"Voice '{voice_id}' not found"}

        audio_bytes = _safe_read(info.audio_path)
        if not audio_bytes:
            return {
                "success": False,
                "error": f"Audio file missing for '{cleaned}'",
            }

        return {
            "success": True,
            "audio_base64": base64.b64encode(audio_bytes).decode("utf-8"),
            "mime_type": info.mime_type,
            "voice_id": cleaned,
            "mock": info.mock,
            "source": info.source,
            "metadata": info.metadata,
            "notes": info.notes,
        }


# Helper for scripts -----------------------------------------------------
def build_inventory() -> Dict[str, List[Dict]]:
    engine = HyperVoiceEngine()
    training = []
    for voice in engine.list_voices():
        entry = voice.copy()
        if engine._voices.get(voice["id"]):
            info = engine._voices[voice["id"]]
            entry.update(
                {
                    "audio_path": str(info.audio_path),
                    "mock": info.mock,
                    "source": info.source,
                }
            )
        training.append(entry)

    # Also include extra voice model files for reference
    extras = []
    for voice_dir in _listdir(VOICE_MODELS_DIR):
        data = {
            "name": voice_dir.name,
            "path": str(voice_dir),
            "files": [p.name for p in voice_dir.glob("*")],
        }
        extras.append(data)

    return {
        "voices": training,
        "voice_model_files": extras,
    }


__all__ = ["HyperVoiceEngine", "build_inventory"]
