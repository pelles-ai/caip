"""Backward-compatible re-exports of TACO and A2A types.

In TACO 0.2+ the canonical definitions live in ``taco.types`` (for
construction-specific types and A2A re-exports). This module exists
for backward compatibility — existing code that imports from
``taco.models`` continues to work.
"""

from .types import (  # noqa: F401
    # A2A SDK re-exports
    AgentCapabilities,
    # Construction types
    AgentCard,
    AgentConstructionExt,
    AgentSkill,
    Artifact,
    Availability,
    BOMUnit,
    Certification,
    DataPart,
    FilePart,
    FlagSeverity,
    Integration,
    JSONRPCError,
    # Deprecated aliases (old casing)
    JsonRpcError,
    JSONRPCErrorResponse,
    JSONRPCRequest,
    JsonRpcRequest,
    JSONRPCResponse,
    JsonRpcResponse,
    JSONRPCSuccessResponse,
    Message,
    Part,
    ProjectType,
    RFICategory,
    RFIPriority,
    Role,
    SecurityExt,
    SkillConstructionExt,
    TacoBaseModel,
    Task,
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    TextPart,
    Trade,
    # Helpers
    get_construction_ext,
    get_skill_construction_ext,
)
