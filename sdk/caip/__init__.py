"""CAIP — Construction A2A Interoperability Protocol SDK"""

__version__ = "0.1.0"

# A2A protocol models
from .models import (
    AgentCard,
    AgentConstructionExt,
    AgentSkill,
    Artifact,
    Availability,
    BOMUnit,
    CaipBaseModel,
    Certification,
    FlagSeverity,
    Integration,
    JsonRpcError,
    JsonRpcRequest,
    JsonRpcResponse,
    Message,
    Part,
    ProjectType,
    RFICategory,
    RFIPriority,
    SecurityExt,
    SkillConstructionExt,
    Task,
    TaskState,
    TaskStatus,
    Trade,
)

# CAIP data schemas
from .schemas import (
    BOMAlternate,
    BOMFlaggedItem,
    BOMLineItem,
    BOMMetadata,
    BOMSchema,
    BOMV1,
    BOMSourceDocument,
    ChangeOrderSchema,
    EstimateLineItem,
    EstimateMetadata,
    EstimateSummary,
    EstimateV1,
    QuoteLineItem,
    QuoteMetadata,
    QuoteSummary,
    QuoteTerms,
    QuoteV1,
    RFIAssignee,
    RFICoordinates,
    RFIMetadata,
    RFIReference,
    RFISchema,
    RFIV1,
    ScheduleSchema,
)

# Convenience factories
from .agent_card import ConstructionAgentCard, ConstructionSkill

__all__ = [
    # A2A protocol models
    "AgentCard",
    "AgentConstructionExt",
    "AgentSkill",
    "Artifact",
    "Availability",
    "BOMUnit",
    "CaipBaseModel",
    "Certification",
    "FlagSeverity",
    "Integration",
    "JsonRpcError",
    "JsonRpcRequest",
    "JsonRpcResponse",
    "Message",
    "Part",
    "ProjectType",
    "RFICategory",
    "RFIPriority",
    "SecurityExt",
    "SkillConstructionExt",
    "Task",
    "TaskState",
    "TaskStatus",
    "Trade",
    # CAIP data schemas
    "BOMAlternate",
    "BOMFlaggedItem",
    "BOMLineItem",
    "BOMMetadata",
    "BOMSchema",
    "BOMSourceDocument",
    "BOMV1",
    "ChangeOrderSchema",
    "EstimateLineItem",
    "EstimateMetadata",
    "EstimateSummary",
    "EstimateV1",
    "QuoteLineItem",
    "QuoteMetadata",
    "QuoteSummary",
    "QuoteTerms",
    "QuoteV1",
    "RFIAssignee",
    "RFICoordinates",
    "RFIMetadata",
    "RFIReference",
    "RFISchema",
    "RFIV1",
    "ScheduleSchema",
    # Server (lazy — requires caip[server])
    "A2AServer",
    "TaskHandler",
    "StreamingTaskHandler",
    # Convenience factories
    "ConstructionAgentCard",
    "ConstructionSkill",
    # Client (lazy — requires caip[client])
    "CAIPClient",
    "CAIPClientError",
    "RpcError",
    "AgentRegistry",
]


def __getattr__(name: str):
    if name in ("A2AServer", "TaskHandler", "StreamingTaskHandler"):
        try:
            from .server import A2AServer, StreamingTaskHandler, TaskHandler  # noqa: F811
        except ImportError:
            raise ImportError(
                "Server dependencies not installed. "
                "Install with: pip install caip[server]"
            ) from None
        _map = {
            "A2AServer": A2AServer,
            "TaskHandler": TaskHandler,
            "StreamingTaskHandler": StreamingTaskHandler,
        }
        return _map[name]
    if name in ("CAIPClient", "CAIPClientError", "RpcError"):
        try:
            from .client import CAIPClient, CAIPClientError, RpcError  # noqa: F811
        except ImportError:
            raise ImportError(
                "Client dependencies not installed. "
                "Install with: pip install caip[client]"
            ) from None
        _map = {"CAIPClient": CAIPClient, "CAIPClientError": CAIPClientError, "RpcError": RpcError}
        return _map[name]
    if name == "AgentRegistry":
        try:
            from .registry import AgentRegistry  # noqa: F811
        except ImportError:
            raise ImportError(
                "Client dependencies not installed. "
                "Install with: pip install caip[client]"
            ) from None
        return AgentRegistry
    raise AttributeError(f"module 'caip' has no attribute {name!r}")
