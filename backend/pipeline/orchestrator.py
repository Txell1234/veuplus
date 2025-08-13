from __future__ import annotations

import asyncio
from typing import AsyncIterator, Awaitable, Callable
from .events import Event


class Orchestrator:
    """Minimal async orchestrator passing events through an async queue.

    - `producer` pushes Event instances into `queue`.
    - `consumer` pulls events and yields them for streaming (SSE/WS).
    """

    def __init__(self, max_queue_size: int = 512) -> None:
        self.queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=max_queue_size)

    async def run_producer(self, producer: Callable[[asyncio.Queue[Event]], Awaitable[None]]) -> None:
        await producer(self.queue)
        # When producer finishes, signal termination
        await self.queue.put(Event(type="done", data={}))

    async def stream(self) -> AsyncIterator[str]:
        while True:
            event = await self.queue.get()
            yield event.to_sse()
            if event.type == "done":
                break


