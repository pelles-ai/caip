"""Lightweight A2A-compliant server base class.

Each TACO agent creates an A2AServer with an AgentCard and registers
async handlers for TACO task types. The server provides:

- GET  /.well-known/agent.json   — A2A Agent Card discovery
- POST /                          — JSON-RPC 2.0 dispatch

When ``enable_admin=True``:

- POST /admin/skills              — dynamic skill registration
- DELETE /admin/skills/{skill_id} — remove a skill
- GET  /admin/skills              — list current skills

Internally wraps the official A2A SDK server infrastructure
(``A2AFastAPIApplication``, ``DefaultRequestHandler``, etc.).
"""

from __future__ import annotations

import json as _json
import logging
import uuid
from collections.abc import AsyncIterator, Callable, Coroutine
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from a2a.server.agent_execution import AgentExecutor
from a2a.server.apps import A2AFastAPIApplication
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore

from .types import (
    AgentCard,
    AgentSkill,
    Artifact,
    DataPart,
    Message,
    Part,
    Role,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
)
from ._compat import (
    extract_structured_data,
    make_artifact,
    make_data_part,
    make_message,
    make_text_part,
)

logger = logging.getLogger("a2a")

TaskHandler = Callable[[Task, dict], Coroutine[Any, Any, Artifact]]
StreamingTaskHandler = Callable[[Task, dict], AsyncIterator[Part]]


class _TacoAgentExecutor(AgentExecutor):
    """Bridge between TACO task handlers and the A2A SDK AgentExecutor ABC."""

    def __init__(self) -> None:
        self._handlers: dict[str, TaskHandler] = {}
        self._streaming_handlers: dict[str, StreamingTaskHandler] = {}

    def _resolve_task_type(self, metadata: dict[str, Any] | None) -> str:
        """Determine task_type from request metadata, or auto-select sole handler."""
        task_type = (metadata or {}).get("taskType")
        if task_type:
            return task_type
        all_handlers = set(self._handlers) | set(self._streaming_handlers)
        if len(all_handlers) == 1:
            task_type = next(iter(all_handlers))
            logger.info(
                "No taskType specified; using sole registered handler: %s",
                task_type,
            )
            return task_type
        available = sorted(all_handlers)
        raise ValueError(
            f"Missing metadata.taskType. Available: {available}"
        )

    def _extract_input(self, message: Message) -> dict[str, Any]:
        """Extract structured data from the first DataPart in a message."""
        for part in message.parts:
            data = extract_structured_data(part)
            if data is not None:
                return data
        return {}

    async def execute(self, context, event_queue: EventQueue) -> None:
        """Dispatch to the registered TACO handler for this task type."""
        metadata = context.metadata
        message = context.message
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())

        try:
            task_type = self._resolve_task_type(metadata)
        except ValueError as exc:
            # No valid task type — send error as message
            error_msg = Message(
                role=Role.agent,
                parts=[make_text_part(str(exc))],
                message_id=str(uuid.uuid4()),
            )
            await event_queue.enqueue_event(error_msg)
            return

        input_data = self._extract_input(message) if message else {}

        # Build a TACO-style Task object for the handler
        task = context.current_task
        if task is None:
            task = Task(
                id=task_id,
                context_id=context_id,
                status=TaskStatus(state=TaskState.working),
                metadata={"taskType": task_type},
            )

        # Check if it's a streaming-only handler called via send
        is_streaming = task_type in self._streaming_handlers
        is_regular = task_type in self._handlers

        if is_regular:
            try:
                artifact = await self._handlers[task_type](task, input_data)
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        task_id=task_id,
                        context_id=context_id,
                        artifact=artifact,
                        append=False,
                    )
                )
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id,
                        context_id=context_id,
                        status=TaskStatus(state=TaskState.completed),
                        final=True,
                    )
                )
            except Exception:
                logger.exception("Task handler failed for %s", task_type)
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id,
                        context_id=context_id,
                        status=TaskStatus(
                            state=TaskState.failed,
                            message=Message(
                                role=Role.agent,
                                parts=[make_text_part(
                                    f"Task handler failed for type '{task_type}'"
                                )],
                                message_id=str(uuid.uuid4()),
                            ),
                        ),
                        final=True,
                    )
                )
        elif is_streaming:
            try:
                collected_parts: list[Part] = []
                handler = self._streaming_handlers[task_type]
                async for part in handler(task, input_data):
                    collected_parts.append(part)
                    await event_queue.enqueue_event(
                        TaskArtifactUpdateEvent(
                            task_id=task_id,
                            context_id=context_id,
                            artifact=make_artifact(
                                parts=[part],
                                name=f"{task_type}-stream-chunk",
                            ),
                            append=True,
                        )
                    )

                if collected_parts:
                    await event_queue.enqueue_event(
                        TaskArtifactUpdateEvent(
                            task_id=task_id,
                            context_id=context_id,
                            artifact=make_artifact(
                                parts=collected_parts,
                                name=f"{task_type}-stream-result",
                            ),
                            append=False,
                        )
                    )
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id,
                        context_id=context_id,
                        status=TaskStatus(state=TaskState.completed),
                        final=True,
                    )
                )
            except Exception as exc:
                logger.exception("Streaming handler error for %s", task_type)
                await event_queue.enqueue_event(
                    TaskStatusUpdateEvent(
                        task_id=task_id,
                        context_id=context_id,
                        status=TaskStatus(
                            state=TaskState.failed,
                            message=Message(
                                role=Role.agent,
                                parts=[make_text_part(str(exc))],
                                message_id=str(uuid.uuid4()),
                            ),
                        ),
                        final=True,
                    )
                )
        else:
            error_msg = Message(
                role=Role.agent,
                parts=[make_text_part(f"No handler for task type: {task_type}")],
                message_id=str(uuid.uuid4()),
            )
            await event_queue.enqueue_event(error_msg)

    async def cancel(self, context, event_queue: EventQueue) -> None:
        """Handle task cancellation."""
        task_id = context.task_id or str(uuid.uuid4())
        context_id = context.context_id or str(uuid.uuid4())
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task_id,
                context_id=context_id,
                status=TaskStatus(state=TaskState.canceled),
                final=True,
            )
        )


class A2AServer:
    """Reusable FastAPI application implementing the A2A protocol.

    Wraps the official A2A SDK server infrastructure while maintaining
    TACO's handler registration API.
    """

    def __init__(
        self,
        agent_card: AgentCard,
        *,
        cors_origins: list[str] | None = None,
        enable_admin: bool = False,
    ) -> None:
        self.agent_card = agent_card
        self._executor = _TacoAgentExecutor()

        # Convert TACO AgentCard to A2A SDK AgentCard for the app
        self._a2a_card = self._to_a2a_sdk_card(agent_card)

        task_store = InMemoryTaskStore()
        request_handler = DefaultRequestHandler(
            agent_executor=self._executor,
            task_store=task_store,
        )
        self._a2a_app = A2AFastAPIApplication(
            agent_card=self._a2a_card,
            http_handler=request_handler,
        )

        self.app = self._a2a_app.build(
            agent_card_url="/.well-known/agent.json",
        )
        self.app.title = agent_card.name

        if cors_origins is None:
            cors_origins = ["*"]
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Also serve the new standard path
        self.app.get("/.well-known/agent-card.json")(self._serve_agent_card)

        # Admin endpoints (opt-in)
        if enable_admin:
            self.app.post("/admin/skills")(self._add_skill)
            self.app.delete("/admin/skills/{skill_id}")(self._remove_skill)
            self.app.get("/admin/skills")(self._list_skills)

    @staticmethod
    def _to_a2a_sdk_card(card: AgentCard):
        """Convert TACO AgentCard to upstream a2a.types.AgentCard."""
        from a2a.types import AgentCard as A2AAgentCard
        from a2a.types import AgentSkill as A2AAgentSkill
        from a2a.types import AgentCapabilities as A2ACapabilities

        skills = []
        for s in card.skills:
            a2a_skill = A2AAgentSkill(
                id=s.id,
                name=s.name,
                description=s.description,
                tags=s.tags if s.tags else [],
            )
            skills.append(a2a_skill)

        return A2AAgentCard(
            name=card.name,
            description=card.description,
            url=card.url,
            version=card.version,
            default_input_modes=card.default_input_modes,
            default_output_modes=card.default_output_modes,
            capabilities=A2ACapabilities(
                streaming=card.capabilities.streaming if card.capabilities else False,
            ),
            skills=skills,
        )

    def register_handler(self, task_type: str, handler: TaskHandler) -> None:
        """Register an async handler for a TACO task type.

        Handler signature: async def handler(task: Task, input_data: dict) -> Artifact
        """
        self._executor._handlers[task_type] = handler

    def register_streaming_handler(
        self, task_type: str, handler: StreamingTaskHandler,
    ) -> None:
        """Register an async streaming handler for a TACO task type.

        Handler signature: async def handler(task: Task, input_data: dict) -> AsyncIterator[Part]
        """
        self._executor._streaming_handlers[task_type] = handler
        if self.agent_card.capabilities:
            self.agent_card.capabilities.streaming = True

    # ------------------------------------------------------------------
    # Agent card endpoint (serves TACO card with x-construction)
    # ------------------------------------------------------------------

    async def _serve_agent_card(self) -> JSONResponse:
        return JSONResponse(
            self.agent_card.model_dump(by_alias=True, exclude_none=True),
        )

    # ------------------------------------------------------------------
    # Dynamic skill admin (opt-in, not part of A2A spec)
    # ------------------------------------------------------------------

    async def _add_skill(self, request: Request) -> JSONResponse:
        try:
            data = await request.json()
            skill = AgentSkill.model_validate(data)
        except Exception as exc:
            return JSONResponse(
                {"error": f"Invalid skill data: {exc}"}, status_code=400,
            )
        self.agent_card.skills.append(skill)
        return JSONResponse({"status": "ok", "skillId": skill.id})

    async def _remove_skill(self, skill_id: str) -> JSONResponse:
        original_count = len(self.agent_card.skills)
        self.agent_card.skills = [
            s for s in self.agent_card.skills if s.id != skill_id
        ]
        if len(self.agent_card.skills) == original_count:
            return JSONResponse(
                {"status": "not_found", "skillId": skill_id}, status_code=404,
            )
        return JSONResponse({"status": "ok", "skillId": skill_id})

    async def _list_skills(self) -> list[dict]:
        return [
            s.model_dump(by_alias=True, exclude_none=True)
            for s in self.agent_card.skills
        ]
