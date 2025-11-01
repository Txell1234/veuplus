#!/usr/bin/env python3
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger("veuplus.convhi_external_voices")

router = APIRouter(prefix="/api/convhi/voices/external", tags=["ConvHi External Voices"])

STORE = Path("backend/convhi_external_voices.json")
STORE.parent.mkdir(parents=True, exist_ok=True)


class ExternalVoice(BaseModel):
    id: str
    provider: str  # e.g., aws_polly, http_generic
    api_base_url: Optional[str] = None
    method: str = "POST"
    headers: Dict[str, str] = {}
    params: Dict[str, Any] = {}
    region: Optional[str] = None
    voice_name: Optional[str] = None
    created_at: Optional[str] = None


def _load() -> List[Dict[str, Any]]:
    if STORE.exists():
        try:
            with open(STORE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict) and "items" in data:
                    return list(data.get("items", []))
        except Exception as e:
            logger.warning(f"Failed reading external voice store: {e}")
    return []


def _save(items: List[Dict[str, Any]]):
    with open(STORE, "w", encoding="utf-8") as f:
        json.dump({"items": items}, f, ensure_ascii=False, indent=2)


@router.get("")
async def list_external_voices() -> Dict[str, Any]:
    items = _load()
    return {"success": True, "voices": items, "count": len(items)}


@router.get("/{voice_id}")
async def get_external_voice(voice_id: str) -> Dict[str, Any]:
    items = _load()
    for it in items:
        if it.get("id") == voice_id:
            return {"success": True, "voice": it}
    raise HTTPException(status_code=404, detail="External voice not found")


@router.post("")
async def create_external_voice(voice: ExternalVoice) -> Dict[str, Any]:
    items = _load()
    if any(it.get("id") == voice.id for it in items):
        raise HTTPException(status_code=409, detail="External voice id already exists")
    items.append(voice.dict())
    _save(items)
    return {"success": True, "voice": voice.dict()}


@router.delete("/{voice_id}")
async def delete_external_voice(voice_id: str) -> Dict[str, Any]:
    items = _load()
    new_items = [it for it in items if it.get("id") != voice_id]
    if len(new_items) == len(items):
        raise HTTPException(status_code=404, detail="External voice not found")
    _save(new_items)
    return {"success": True, "deleted": voice_id}

