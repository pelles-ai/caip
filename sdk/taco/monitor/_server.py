"""MonitorServer — mount-based monitor UI for live A2A tracing."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from ._event_bus import EventBus

logger = logging.getLogger("taco.monitor")


class MonitorServer:
    """Monitor web UI that mounts onto the agent's existing FastAPI app.

    Instead of running a separate uvicorn server, call :meth:`mount_on`
    to attach the monitor routes under a prefix (default ``/monitor``).
    """

    def __init__(
        self,
        event_bus: EventBus,
        *,
        agent_name: str = "TACO Agent",
    ) -> None:
        self.event_bus = event_bus
        self.agent_name = agent_name

    def build_app(self) -> FastAPI:
        """Create the FastAPI application with all monitor routes."""
        from ._ui import HTML_UI

        app = FastAPI(title=f"{self.agent_name} Monitor")
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        bus = self.event_bus
        agent_name = self.agent_name

        @app.get("/", response_class=HTMLResponse)
        async def index() -> HTMLResponse:
            return HTMLResponse(HTML_UI)

        @app.get("/api/events")
        async def get_events(limit: int = 200, offset: int = 0) -> JSONResponse:
            return JSONResponse(bus.get_history(limit, offset))

        @app.get("/api/info")
        async def get_info() -> JSONResponse:
            return JSONResponse(
                {
                    "agentName": agent_name,
                    "eventCount": bus.event_count,
                    "maxEvents": bus.max_events,
                }
            )

        @app.post("/api/clear")
        async def clear_events() -> JSONResponse:
            bus.clear()
            return JSONResponse({"status": "ok"})

        @app.websocket("/ws")
        async def ws_endpoint(websocket: WebSocket) -> None:
            await websocket.accept()
            queue: asyncio.Queue[dict[str, Any]] = bus.subscribe()
            try:
                while True:
                    event = await queue.get()
                    await websocket.send_json(event)
            except WebSocketDisconnect:
                pass
            except Exception:
                logger.debug("WebSocket error", exc_info=True)
            finally:
                bus.unsubscribe(queue)

        return app

    def mount_on(self, parent_app: FastAPI, prefix: str = "/monitor") -> None:
        """Mount the monitor UI onto an existing FastAPI application."""
        parent_app.mount(prefix, self.build_app())
        logger.info("Monitor UI mounted at %s", prefix)
