#!/usr/bin/env python3
import os
import hmac
import hashlib
import time
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/api/convhi/widget", tags=["ConvHi Widget"])

WIDGET_SECRET = os.environ.get("CONVHI_WIDGET_SECRET", "dev-secret-change-me")
ALLOWLIST = [h.strip() for h in os.environ.get("CONVHI_WIDGET_ALLOWLIST", "localhost,127.0.0.1").split(",") if h.strip()]
DEFAULT_BACKEND_URL = os.environ.get("CONVHI_WIDGET_BACKEND_URL", "http://localhost:8080")


def _verify_signature(payload: str, signature: str) -> bool:
    expected = hmac.new(WIDGET_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)


def _parse_payload(payload: str) -> dict:
    parts = payload.split("&")
    data = {}
    for part in parts:
        if "=" in part:
            key, value = part.split("=", 1)
            data[key] = value
    return data


class SignedUrlRequest(BaseModel):
    agent_id: str
    ttl_seconds: int = 900


class WidgetConfigRequest(BaseModel):
    payload: str
    signature: str


class WidgetConfigResponse(BaseModel):
    success: bool
    agent_id: str
    config: Optional[dict] = None
    expires_at: Optional[int] = None


@router.post("/signed-url")
async def create_signed_url(req: SignedUrlRequest, r: Request):
    try:
        origin = r.headers.get("origin", "")
        if ALLOWLIST and origin:
            allowed = any(origin.endswith(x) or (x in origin) for x in ALLOWLIST)
            if not allowed:
                raise HTTPException(status_code=403, detail="Origin not allowed")

        ttl = max(60, min(req.ttl_seconds, 3600))
        exp = int(time.time()) + ttl
        payload = f"agent_id={req.agent_id}&exp={exp}"
        sig = hmac.new(WIDGET_SECRET.encode(), payload.encode(), hashlib.sha256).hexdigest()
        return {
            "success": True,
            "agent_id": req.agent_id,
            "exp": exp,
            "signature": sig,
            "payload": payload,
            "backend_url": DEFAULT_BACKEND_URL,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/config", response_model=WidgetConfigResponse)
async def resolve_widget_config(req: WidgetConfigRequest):
    try:
        if not _verify_signature(req.payload, req.signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        data = _parse_payload(req.payload)
        agent_id = data.get("agent_id")
        if not agent_id:
            raise HTTPException(status_code=400, detail="Invalid payload")

        exp = int(data.get("exp", 0))
        if exp and exp < int(time.time()):
            raise HTTPException(status_code=401, detail="Signed URL expired")

        try:
            from .convhi_widgets import widget_configs
        except Exception:
            widget_configs = {}

        config = widget_configs.get(agent_id)
        if not config:
            raise HTTPException(status_code=404, detail="Widget config not found")

        return WidgetConfigResponse(success=True, agent_id=agent_id, config=config, expires_at=exp)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
