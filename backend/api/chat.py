from __future__ import annotations

from typing import List
from fastapi import APIRouter
from pydantic import BaseModel, field_validator
from starlette.responses import StreamingResponse
import time

try:
    # local module when running from repository root
    from transformers_service import stream_response, DEFAULT_MODEL, MAX_LENGTH
except Exception:
    try:
        # when packaged under backend
        from backend.transformers_service import stream_response, DEFAULT_MODEL, MAX_LENGTH
    except Exception:
        # ultra-light fallback for CI: define a stub stream_response
        DEFAULT_MODEL = "gpt2"
        MAX_LENGTH = 256
        def stream_response(**kwargs):  # type: ignore
            yield "data: {\"type\": \"token\", \"data\": {\"text\": \"hola\"}}\n\n"
            yield "data: {\"type\": \"done\", \"data\": {}}\n\n"

try:
    from core.metrics import record_event, record_chat_request, observe_chat_duration
except Exception:
    # no-op fallback
    def record_event(name: str, value: float | int = 1) -> None:  # type: ignore
        return
    def record_chat_request() -> None:  # type: ignore
        return
    def observe_chat_duration(seconds: float) -> None:  # type: ignore
        return


router = APIRouter(prefix="/api/chat", tags=["Chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatStreamRequest(BaseModel):
    messages: List[ChatMessage]
    model: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None

    @field_validator("messages")
    @classmethod
    def _validate_messages(cls, v: List[ChatMessage]):
        if not v:
            raise ValueError("messages cannot be empty")
        if len(v) > 64:
            raise ValueError("too many messages (max 64)")
        total_len = sum(len(m.content) for m in v)
        if total_len > 8000:
            raise ValueError("messages too long (max 8000 chars)")
        return v


@router.post("/stream")
async def chat_stream(req: ChatStreamRequest) -> StreamingResponse:
    start = time.perf_counter()
    record_chat_request()

    def iterator():
        for chunk in stream_response(
            messages=[{"role": m.role, "content": m.content} for m in req.messages],
            model_name=req.model or DEFAULT_MODEL,
            max_tokens=req.max_tokens or MAX_LENGTH,
            temperature=req.temperature or 0.7,
        ):
            yield chunk

    # simple metric
    record_event("chat.stream.requests", 1)

    async def _gen():
        for part in iterator():
            yield part
        duration = time.perf_counter() - start
        record_event("chat.stream.duration_ms", duration * 1000)
        observe_chat_duration(duration)

    return StreamingResponse(_gen(), media_type="text/event-stream")


