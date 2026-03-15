"""EventBus — central event collection with ring buffer and WebSocket fan-out."""

from __future__ import annotations

import asyncio
import logging
import uuid
from collections import deque
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("taco.monitor")

# Maximum items per subscriber queue before dropping events
_SUBSCRIBER_QUEUE_MAX = 500


def make_event(
    *,
    kind: str,
    method: str = "",
    direction: str = "internal",
    summary: str = "",
    payload: Any = None,
    duration_ms: float | None = None,
    error: str | None = None,
    task_id: str | None = None,
    task_type: str | None = None,
    agent_name: str | None = None,
) -> dict[str, Any]:
    """Build a monitor event dict with standard fields."""
    return {
        "id": str(uuid.uuid4()),
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": kind,
        "method": method,
        "direction": direction,
        "summary": summary,
        "payload": payload,
        "duration_ms": duration_ms,
        "error": error,
        "task_id": task_id,
        "task_type": task_type,
        "agent_name": agent_name,
    }


class EventBus:
    """Async-safe event store with subscriber fan-out.

    Events are stored in a fixed-size ring buffer (``deque(maxlen=N)``).
    WebSocket consumers subscribe via async queues and receive events in
    real time.  If a consumer falls behind, events are dropped for that
    consumer (no back-pressure on emitters).
    """

    def __init__(self, max_events: int = 2000) -> None:
        self._events: deque[dict[str, Any]] = deque(maxlen=max_events)
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()

    def emit(self, event: dict[str, Any]) -> None:
        """Record an event and fan out to all subscribers.

        This is intentionally **synchronous** so it can be called from
        both sync middleware and async handlers without awaiting.
        """
        self._events.append(event)

        for queue in list(self._subscribers):
            try:
                queue.put_nowait(event)
            except asyncio.QueueFull:
                logger.debug("Dropping monitor event for slow subscriber")

    def get_history(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        """Return stored events (oldest first).

        Args:
            limit: Maximum number of events to return.
            offset: Number of events to skip from the start.
        """
        events = list(self._events)
        return events[offset : offset + limit] if limit else events[offset:]

    def subscribe(self) -> asyncio.Queue[dict[str, Any]]:
        """Create and register a subscriber queue."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(
            maxsize=_SUBSCRIBER_QUEUE_MAX,
        )
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        """Remove a subscriber queue."""
        self._subscribers.discard(queue)

    def clear(self) -> None:
        """Clear all stored events."""
        self._events.clear()

    @property
    def event_count(self) -> int:
        return len(self._events)

    @property
    def max_events(self) -> int:
        return self._events.maxlen or 0
