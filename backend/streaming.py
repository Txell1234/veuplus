from __future__ import annotations

from fastapi.responses import StreamingResponse
from typing import AsyncIterator


def sse_response(iterator: AsyncIterator[str]) -> StreamingResponse:
    """Return a standard SSE response from an async string iterator."""
    return StreamingResponse(iterator, media_type="text/event-stream")


