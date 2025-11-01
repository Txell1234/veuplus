#!/usr/bin/env python3
"""
ConvHi WebRTC bootstrap endpoints (token + config)
Provides minimal, production-safe endpoints to allow browser widgets to obtain
STUN/TURN configuration and a signed token to initiate calls.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import hmac
import hashlib
import base64
import json
import logging

logger = logging.getLogger("veuplus.convhi_webrtc")

webrtc_router = APIRouter(prefix="/api/convhi/webrtc", tags=["ConvHi WebRTC"])


class TokenRequest(BaseModel):
    agent_id: str
    ttl_seconds: int = 3600
    origins: Optional[List[str]] = None


class TokenResponse(BaseModel):
    token: str
    expires_at: str


class WebRTCConfig(BaseModel):
    stun_servers: List[str] = []
    turn_servers: List[Dict[str, Any]] = []
    region: str = "eu"


def _sign(payload: Dict[str, Any], secret: str) -> str:
    # Compact JWS-like token (header.payload.signature base64)
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = base64.urlsafe_b64encode(json.dumps(header).encode()).rstrip(b"=")
    p_b64 = base64.urlsafe_b64encode(json.dumps(payload).encode()).rstrip(b"=")
    sig = hmac.new(secret.encode(), h_b64 + b"." + p_b64, hashlib.sha256).digest()
    s_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=")
    return (h_b64 + b"." + p_b64 + b"." + s_b64).decode()


@webrtc_router.post("/token", response_model=TokenResponse)
async def issue_token(req: TokenRequest):
    """Issue a short-lived token for initiating a WebRTC session."""
    try:
        secret = os.environ.get("WEBRTC_TOKEN_SECRET", "dev-secret-change-me")
        exp = datetime.utcnow() + timedelta(seconds=max(60, min(req.ttl_seconds, 24*3600)))
        payload = {
            "agent_id": req.agent_id,
            "exp": int(exp.timestamp()),
            "origins": req.origins or [],
        }
        token = _sign(payload, secret)
        return TokenResponse(token=token, expires_at=exp.isoformat() + "Z")
    except Exception as e:
        logger.error(f"WebRTC token error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@webrtc_router.get("/config", response_model=WebRTCConfig)
async def get_webrtc_config():
    """Return STUN/TURN configuration from environment variables."""
    try:
        stun = [s.strip() for s in os.environ.get("WEBRTC_STUN", "stun:stun.l.google.com:19302").split(",") if s.strip()]
        # TURN format: url|username|password per entry, comma-separated
        turn_raw = [s.strip() for s in os.environ.get("WEBRTC_TURN", "").split(",") if s.strip()]
        turn = []
        for item in turn_raw:
            parts = item.split("|")
            if len(parts) >= 3:
                turn.append({"urls": parts[0], "username": parts[1], "credential": parts[2]})
        region = os.environ.get("WEBRTC_REGION", "eu")
        return WebRTCConfig(stun_servers=stun, turn_servers=turn, region=region)
    except Exception as e:
        logger.error(f"WebRTC config error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["webrtc_router"]

