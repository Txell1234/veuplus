#!/usr/bin/env python3
"""
ConvHi webhook endpoint.
Persist incoming call events and feed analytics dashboards.
"""

import hmac
import hashlib
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

try:
    from backend.database_sql import db as sql_db  # type: ignore
except ImportError:  # pragma: no cover - local execution fallback
    from database_sql import db as sql_db  # type: ignore

try:
    from backend.api.convhi_analytics import analytics_engine  # type: ignore
except ImportError:  # pragma: no cover
    from api.convhi_analytics import analytics_engine  # type: ignore

router = APIRouter(prefix="/api/convhi/webhooks", tags=["ConvHi Webhooks"])

WEBHOOK_SECRET = os.environ.get("CONVHI_WEBHOOK_SECRET", "dev-webhook-secret")
STORE_EVENTS = os.environ.get("CONVHI_WEBHOOK_STORE", "true").lower() != "false"

EVENT_STATUS_MAP = {
    "call.completed": "completed",
    "call.failed": "failed",
    "call.ended": "completed",
    "call.started": "active",
    "call.in_progress": "active",
    "call.ringing": "queued",
    "call.queued": "queued",
}

INTERACTION_EVENTS = {
    "turn.completed",
    "turn.failed",
    "segment.completed",
    "segment.failed",
}


def _verify_signature(request_body: bytes, signature_header: str) -> bool:
    """Validate ElevenLabs-style HMAC header."""
    try:
        parts = signature_header.split(",")
        if len(parts) < 2:
            return False
        timestamp_part = parts[0].split("=")
        if len(timestamp_part) != 2:
            return False
        timestamp = timestamp_part[1]
        payload = request_body.decode("utf-8")
        message = f"{timestamp}.{payload}".encode()
        expected = "v0=" + hmac.new(WEBHOOK_SECRET.encode(), message, hashlib.sha256).hexdigest()
        candidate = parts[1]
        return hmac.compare_digest(candidate, expected)
    except Exception:
        return False


def _safe_iso(timestamp: Optional[str]) -> str:
    """Ensure we always return a parseable ISO timestamp."""
    if not timestamp:
        return datetime.utcnow().isoformat()
    try:
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        return timestamp
    except Exception:
        return datetime.utcnow().isoformat()


def _extract_meta(payload: Dict[str, Any]) -> Dict[str, Optional[str]]:
    """Pull common identifiers from webhook payload."""
    call = payload.get("call") or {}
    session = payload.get("session") or {}
    agent = payload.get("agent") or {}

    return {
        "call_id": payload.get("call_id") or call.get("id") or session.get("id"),
        "agent_id": payload.get("agent_id") or agent.get("id") or session.get("agent_id"),
        "customer_id": payload.get("customer_id") or session.get("customer_id"),
        "language": payload.get("language") or payload.get("locale") or call.get("language"),
        "llm_provider": payload.get("llm_provider") or agent.get("llm_provider"),
        "voice_system": payload.get("voice_system") or agent.get("voice_system"),
        "timestamp": payload.get("timestamp") or payload.get("created_at"),
    }


async def _dispatch_analytics(event_type: str, payload: Dict[str, Any], meta: Dict[str, Optional[str]]) -> None:
    """Send data to analytics engine so dashboards stay fresh."""
    status = EVENT_STATUS_MAP.get(event_type)
    metrics = payload.get("metrics") or {}
    duration = metrics.get("duration") or metrics.get("call_duration") or payload.get("duration") or 0

    if status:
        conversation_payload = {
            "id": meta["call_id"] or f"call_{datetime.utcnow().timestamp()}",
            "agent_id": meta["agent_id"],
            "user_id": meta["customer_id"] or "anonymous",
            "start_time": _safe_iso(
                payload.get("started_at") or payload.get("start_time") or meta.get("timestamp")
            ),
            "end_time": _safe_iso(
                payload.get("ended_at") or payload.get("end_time") or meta.get("timestamp")
            ),
            "duration": duration or 0,
            "status": status,
            "total_messages": payload.get("turn_count") or metrics.get("turns") or 0,
            "language": meta["language"] or "unknown",
            "satisfaction_score": metrics.get("satisfaction"),
            "knowledge_used": metrics.get("knowledge_hits") or 0,
            "llm_provider": meta["llm_provider"],
            "voice_system": meta["voice_system"],
            "metadata": {"raw_event": event_type, "source": "convhi_webhook"},
        }
        await analytics_engine.log_conversation(conversation_payload)

    if event_type in INTERACTION_EVENTS:
        interaction_payload = {
            "conversation_id": meta["call_id"],
            "agent_id": meta["agent_id"],
            "timestamp": _safe_iso(meta.get("timestamp")),
            "message_type": payload.get("message_type") or "audio",
            "user_message": payload.get("user_transcript") or "",
            "agent_response": payload.get("agent_transcript") or "",
            "response_time": metrics.get("response_time") or payload.get("response_time") or 0,
            "success": event_type.endswith("completed"),
            "knowledge_used": metrics.get("knowledge_hits") or 0,
            "llm_tokens": metrics.get("llm_tokens") or payload.get("llm_tokens") or 0,
            "audio_duration": metrics.get("audio_duration") or payload.get("audio_duration") or duration or 0,
        }
        await analytics_engine.log_interaction(interaction_payload)


def _persist_event(event_type: str, payload: Dict[str, Any], meta: Dict[str, Optional[str]]) -> int:
    """Store raw webhook in SQLite for historical analytics."""
    if not STORE_EVENTS:
        return -1
    try:
        return sql_db.log_convhi_event(
            event_type=event_type,
            payload=payload,
            call_id=meta["call_id"],
            agent_id=meta["agent_id"],
            status=EVENT_STATUS_MAP.get(event_type),
        )
    except Exception as exc:  # pragma: no cover - DB failures should not block webhook processing
        logger = getattr(sql_db, "logger", None)
        if logger:
            logger.error(f"ConvHi webhook persistence failed: {exc}")
        return -1


@router.post("/post-call")
async def post_call_webhook(request: Request):
    try:
        raw = await request.body()
        signature = request.headers.get("ElevenLabs-Signature") or request.headers.get("X-Signature") or ""

        if WEBHOOK_SECRET and not _verify_signature(raw, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        data: Dict[str, Any] = json.loads(raw.decode("utf-8"))
        event_type = data.get("type", "unknown")
        meta = _extract_meta(data)

        record_id = _persist_event(event_type, data, meta)
        await _dispatch_analytics(event_type, data, meta)

        return JSONResponse(
            {
                "received": True,
                "type": event_type,
                "event_id": record_id if record_id != -1 else None,
                "call_id": meta["call_id"],
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))
