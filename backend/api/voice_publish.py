#!/usr/bin/env python3
"""
Publish/unpublish trained voices into Unified Voices
Stores published IDs in backend/voice_models/published.json
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
from pathlib import Path
import json
import logging

logger = logging.getLogger("veuplus.voice_publish")

router = APIRouter(prefix="/api/voices", tags=["Voices Publish"])

PUBLISH_FILE = Path("backend/voice_models/published.json")
PUBLISH_FILE.parent.mkdir(parents=True, exist_ok=True)


def _read_published() -> List[str]:
    if PUBLISH_FILE.exists():
        try:
            with open(PUBLISH_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return [str(x) for x in data]
                if isinstance(data, dict) and "published" in data:
                    return [str(x) for x in data.get("published", [])]
        except Exception as e:
            logger.warning(f"Failed to read published.json: {e}")
    return []


def _write_published(ids: List[str]) -> None:
    try:
        with open(PUBLISH_FILE, "w", encoding="utf-8") as f:
            json.dump({"published": ids}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Failed to write published.json: {e}")
        raise


@router.get("/publish")
async def list_published() -> Dict[str, Any]:
    try:
        published = _read_published()
        return {"success": True, "published": published, "count": len(published)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class PublishRequest(BaseModel):
    voice_id: str


@router.post("/publish/{voice_id}")
async def publish_voice(voice_id: str) -> Dict[str, Any]:
    try:
        published = _read_published()
        if voice_id not in published:
            published.append(voice_id)
            _write_published(published)
        return {"success": True, "published": published}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/publish/{voice_id}")
async def unpublish_voice(voice_id: str) -> Dict[str, Any]:
    try:
        published = _read_published()
        if voice_id in published:
            published = [v for v in published if v != voice_id]
            _write_published(published)
        return {"success": True, "published": published}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]

