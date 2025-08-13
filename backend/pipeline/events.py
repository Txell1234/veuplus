from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Dict
from datetime import datetime


EventType = Literal[
    "token",
    "message",
    "partial_transcript",
    "audio_chunk",
    "error",
    "done",
]


@dataclass(slots=True)
class Event:
    """Uniform event used across streaming APIs.

    This intentionally mirrors the style of event-driven frameworks
    (inspiration: Pipecat) to make VeuPlus pipelines composable and
    observable.
    """

    type: EventType
    data: Dict[str, Any]
    ts: str = datetime.utcnow().isoformat()

    def to_sse(self) -> str:
        """Render as Server-Sent Event line (data-only for simplicity)."""
        import json

        payload = {"type": self.type, "ts": self.ts, "data": self.data}
        return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


