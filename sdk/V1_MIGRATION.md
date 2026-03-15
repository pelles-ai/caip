# TACO SDK — A2A Protocol v1.0 Migration Guide

## Overview

The A2A Protocol v1.0 switches the Python SDK from Pydantic models (`A2ABaseModel`)
to **protobuf messages**. The v1.0 SDK provides a backward-compatible layer at
`a2a.compat.v0_3.types` for incremental migration.

## Key Breaking Changes in a2a-sdk v1.0

### Part Types
```python
# v0.3 (current)
Part(root=TextPart(text="hello"))
Part(root=DataPart(data={"key": "value"}))
Part(root=FilePart(file=FileWithUri(uri="...")))

# v1.0 (new)
Part(text="hello")
Part(data={"key": "value"})
Part(file=File(uri="..."))
```

### Enum Values
```python
# v0.3 (current)
TaskState.completed
TaskState.working
Role.user
Role.agent

# v1.0 (new)
TaskState.TASK_STATE_COMPLETED
TaskState.TASK_STATE_WORKING
Role.ROLE_USER
Role.ROLE_AGENT
```

### AgentCard Structure
```python
# v0.3 (current)
AgentCard(url="http://...", ...)

# v1.0 (new)
AgentCard(supported_interfaces=[...], ...)
# Top-level `url` and `protocol_version` fields removed
```

## TACO Migration Strategy

### Phase 1: Zero-Change Compat Layer (first step)
Switch imports in `taco/types.py` from `a2a.types` to `a2a.compat.v0_3.types`:

```python
# Before
from a2a.types import Part, TextPart, DataPart, ...

# After
from a2a.compat.v0_3.types import Part, TextPart, DataPart, ...
```

This provides **identical API** with zero behavior change. All existing code
continues to work.

### Phase 2: Update _compat.py Helpers
Update `make_text_part`, `make_data_part`, `extract_text`, and
`extract_structured_data` to use native v1.0 Part constructors:

```python
# Before
def make_text_part(text: str) -> Part:
    return Part(root=TextPart(text=text))

# After
def make_text_part(text: str) -> Part:
    return Part(text=text)
```

### Phase 3: Adopt Native v1.0 Types
Incrementally update `types.py` imports from `a2a.compat.v0_3.types` to
`a2a.types` (the new protobuf-based types). Update enum references
throughout.

## Files That Need Changes

Only **two files** need modification for the compat layer switch:

| File | Changes |
|------|---------|
| `taco/types.py` | Switch `from a2a.types` to `from a2a.compat.v0_3.types` |
| `taco/_compat.py` | Switch `from a2a.types` to `from a2a.compat.v0_3.types` |

For full v1.0 adoption, additionally:

| File | Changes |
|------|---------|
| `taco/_compat.py` | Update Part constructors and accessors |
| `taco/server.py` | Update enum references in `_to_a2a_sdk_card` |
| `taco/schemas.py` | Uses `A2ABaseModel` — may need to switch base class |

## Timeline

- **a2a-sdk v1.0**: In development (`1.0-dev` branch, last commit March 13, 2026)
- **TACO v0.3.0**: Ships on current v0.3 API, prepared for v1.0 migration
- **TACO v0.4.0**: Will adopt compat layer when v1.0 ships
- **TACO v1.0.0**: Will adopt native v1.0 types
