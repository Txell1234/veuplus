from __future__ import annotations

from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

try:
    from backend.storage import store_model_artifact, store_audio_sample
    from backend.database_sql import db as sql_db
except Exception:
    from storage import store_model_artifact, store_audio_sample  # type: ignore
    from database_sql import db as sql_db  # type: ignore


router = APIRouter(prefix="/api", tags=["Voices"])


class VoiceImportResponse(BaseModel):
    voice_id: str
    message: str
    sample_url: Optional[str] = None
    model_url: Optional[str] = None


@router.post("/voices/import", response_model=VoiceImportResponse)
async def import_voice_model(file: UploadFile, name: str = "", language: str = "ca", dialect: str = "central"):
    """Import a voice model package (zip) with final_model.json, training_config.json, sample.wav, metadata.json"""
    try:
        from uuid import uuid4
        import zipfile, tempfile

        voice_id = str(uuid4())
        data = await file.read()
        if len(data) > int(sql_db.config.get("MAX_UPLOAD_SIZE_MB", 20)) * 1024 * 1024:
            raise HTTPException(status_code=413, detail="File too large")

        tmp_dir = Path(tempfile.mkdtemp(prefix="veuplus_import_"))
        tmp_zip = tmp_dir / "model.zip"
        tmp_zip.write_bytes(data)

        with zipfile.ZipFile(tmp_zip, 'r') as z:
            members = z.namelist()
            required = {"final_model.json", "training_config.json", "sample.wav"}
            if not required.issubset(set(members)):
                missing = required - set(members)
                raise HTTPException(status_code=400, detail=f"Missing files: {', '.join(missing)}")
            z.extractall(tmp_dir)

        model_url = store_model_artifact(voice_id, tmp_dir)
        sample_url = store_audio_sample(voice_id, tmp_dir / "sample.wav")

        sql_db.create_voice_model({
            "id": voice_id,
            "name": name or f"Imported Voice {voice_id[:8]}",
            "language": language,
            "dialect": dialect,
            "status": "ready",
            "progress": 100,
            "model_path": str(Path("backend") / f"models/{voice_id}"),
            "sample_audio": sample_url,
            "quality": "imported",
            "real_model": True,
            "config": {"source": "import"},
            "created_at": datetime.utcnow().isoformat()
        })

        return VoiceImportResponse(voice_id=voice_id, message="Voice model imported", sample_url=sample_url, model_url=model_url)
    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid ZIP file")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {e}")


@router.get("/voices")
async def list_voices() -> Dict[str, Any]:
    try:
        # Use the Integrated Voice System (functional and realistic)
        try:
            from backend.integrated_voice_system import get_integrated_voices
            integrated_voices = get_integrated_voices()
            print(f"✅ Integrated voice system loaded: {len(integrated_voices['voices'])} voices")
            return integrated_voices
        except ImportError as e:
            print(f"⚠️ Integrated voice system not available: {e}")
            
        # Fallback to basic system
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices') or []
            
            basic_voices = []
            for voice in voices:
                name = getattr(voice, 'name', 'Unknown')
                voice_id = getattr(voice, 'id', '')
                langs = getattr(voice, 'languages', [])
                
                basic_voices.append({
                    "id": f"basic_{voice_id.split('\\')[-1] if '\\' in voice_id else voice_id}",
                    "name": f"{name} (Basic)",
                    "language": "unknown",
                    "dialect": "standard",
                    "status": "ready",
                    "progress": 100,
                    "quality": "basic",
                    "real_model": True,
                    "type": "basic_system",
                    "system_id": voice_id,
                    "created_at": datetime.utcnow().isoformat()
                })
            
            return {"voices": basic_voices}
            
        except Exception as e:
            print(f"Error in fallback voices: {e}")
            return {"voices": []}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: str):
    try:
        ok = sql_db.delete_voice_model(voice_id)
        return {"deleted": bool(ok)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


