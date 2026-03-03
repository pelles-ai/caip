"""TACO — The A2A Construction Open-standard SDK"""

__version__ = "0.1.0"

# A2A protocol models
from .models import (
    AgentCard,
    AgentConstructionExt,
    AgentSkill,
    Artifact,
    Availability,
    BOMUnit,
    TacoBaseModel,
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

# TACO data schemas
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
    "TacoBaseModel",
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
    # TACO data schemas
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
    # Server (lazy — requires taco[server])
    "A2AServer",
    "TaskHandler",
    "StreamingTaskHandler",
    # Convenience factories
    "ConstructionAgentCard",
    "ConstructionSkill",
    # Client (lazy — requires taco[client])
    "TacoClient",
    "TacoClientError",
    "RpcError",
    "AgentRegistry",
]


_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    # name -> (module, install hint)
    "A2AServer": (".server", "taco[server]"),
    "TaskHandler": (".server", "taco[server]"),
    "StreamingTaskHandler": (".server", "taco[server]"),
    "TacoClient": (".client", "taco[client]"),
    "TacoClientError": (".client", "taco[client]"),
    "RpcError": (".client", "taco[client]"),
    "AgentRegistry": (".registry", "taco[client]"),
}


def __getattr__(name: str):
    entry = _LAZY_IMPORTS.get(name)
    if entry is None:
        raise AttributeError(f"module 'taco' has no attribute {name!r}")
    module_path, install_hint = entry
    try:
        import importlib
        module = importlib.import_module(module_path, package=__name__)
    except ImportError:
        raise ImportError(
            f"Dependencies not installed. Install with: pip install {install_hint}"
        ) from None
    return getattr(module, name)
