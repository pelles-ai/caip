"""Pydantic models for the A2A (Agent-to-Agent) protocol wire format.

Covers Agent Cards, JSON-RPC messages, tasks, artifacts, and the
CAIP x-construction extensions. Uses camelCase aliases to match
the A2A JSON spec while keeping Pythonic snake_case internally.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Task lifecycle
# ---------------------------------------------------------------------------

class TaskState(str, Enum):
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    INPUT_REQUIRED = "input-required"


# ---------------------------------------------------------------------------
# Message / Part / Artifact
# ---------------------------------------------------------------------------

class Part(BaseModel):
    """A2A content unit. Supports text and structured data."""

    text: str | None = None
    structured_data: dict[str, Any] | None = Field(None, alias="structuredData")

    model_config = {"populate_by_name": True}


class Message(BaseModel):
    role: str  # "user" or "agent"
    parts: list[Part]


class Artifact(BaseModel):
    """Typed output from an agent."""

    name: str | None = None
    description: str | None = None
    parts: list[Part]
    metadata: dict[str, Any] | None = None


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------

class TaskStatus(BaseModel):
    state: TaskState
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
    )
    message: Message | None = None


class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    context_id: str | None = Field(None, alias="contextId")
    status: TaskStatus
    artifacts: list[Artifact] = []
    history: list[Message] = []
    metadata: dict[str, Any] = {}

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Agent Card + CAIP extensions
# ---------------------------------------------------------------------------

class SkillConstructionExt(BaseModel):
    """x-construction extension on a skill."""

    task_type: str = Field(alias="taskType")
    input_schema: str | None = Field(None, alias="inputSchema")
    output_schema: str = Field(alias="outputSchema")

    model_config = {"populate_by_name": True}


class AgentSkill(BaseModel):
    id: str
    name: str
    description: str
    x_construction: SkillConstructionExt | None = Field(
        None, alias="x-construction",
    )

    model_config = {"populate_by_name": True}


class AgentConstructionExt(BaseModel):
    """Top-level x-construction extension on an Agent Card."""

    trade: str
    csi_divisions: list[str] = Field(alias="csiDivisions")
    project_types: list[str] = Field(default_factory=list, alias="projectTypes")
    certifications: list[str] = []
    data_formats: dict[str, list[str]] = Field(
        default_factory=dict, alias="dataFormats",
    )
    integrations: list[str] = []

    model_config = {"populate_by_name": True}


class AgentCard(BaseModel):
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: dict[str, bool] = Field(
        default_factory=lambda: {"streaming": False, "pushNotifications": False},
    )
    skills: list[AgentSkill] = []
    x_construction: AgentConstructionExt | None = Field(
        None, alias="x-construction",
    )

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# JSON-RPC 2.0
# ---------------------------------------------------------------------------

class JsonRpcRequest(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int
    method: str
    params: dict[str, Any] = {}


class JsonRpcResponse(BaseModel):
    jsonrpc: str = "2.0"
    id: str | int
    result: dict[str, Any] | None = None
    error: dict[str, Any] | None = None
