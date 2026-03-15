---
sidebar_position: 5
title: SDK Reference
---

# SDK Reference

The TACO Python SDK provides models, a server framework, a client, and an agent registry for building A2A-compatible construction agents.

## Installation

```bash
# Core models and schemas
pip install taco-agent

# With server support (FastAPI-based A2A server)
pip install taco-agent[server]

# With client support (async HTTP client)
pip install taco-agent[client]

# Everything
pip install taco-agent[server,client]
```

## Modules

| Module | Description |
|--------|-------------|
| `taco.types` | Pydantic v2 models for A2A protocol types (AgentCard, Task, Message, Part, etc.) and construction domain types |
| `taco.schemas` | Construction data schema models (BOMV1, RFIV1, EstimateV1, QuoteV1, ScheduleV1, ChangeOrderV1) |
| `taco.server` | A2AServer — FastAPI-based server with JSON-RPC routing, streaming, and task store |
| `taco.client` | TacoClient — async HTTP client for agent discovery, task submission, and streaming |
| `taco.agent_card` | ConstructionAgentCard and ConstructionSkill convenience classes |
| `taco.registry` | AgentRegistry — in-memory agent discovery with filtering by trade, task type, CSI division |
| `taco.agent` | TacoAgent — bidirectional agent that combines server, client pool, and registry |
| `taco.monitor` | Agent Monitor — opt-in live tracing UI for A2A communications |

## Quick Start: Expose an Agent

```python
import uvicorn
from taco import (
    ConstructionAgentCard, ConstructionSkill, A2AServer,
    make_artifact, make_data_part,
)

# 1. Define your agent's identity and capabilities
card = ConstructionAgentCard(
    name="My Mechanical Estimating Agent",
    trade="mechanical",
    csi_divisions=["22", "23"],
    skills=[
        ConstructionSkill(
            id="generate-estimate",
            task_type="estimate",
            input_schema="bom-v1",
            output_schema="estimate-v1",
        )
    ],
)

# 2. Create the server (with optional monitor UI at /monitor)
server = A2AServer(card.to_a2a(), enable_monitor=True)

# 3. Register a handler for the task type
async def handle_estimate(task, input_data):
    # Your estimation logic here
    estimate = generate_estimate(input_data)
    return make_artifact(
        parts=[make_data_part(estimate)],
        name="estimate-result",
        metadata={"schema": "estimate-v1"},
    )

server.register_handler("estimate", handle_estimate)

# 4. Run the server
uvicorn.run(server.app, host="0.0.0.0", port=8001)
```

## Quick Start: Call an Agent

```python
from taco import TacoClient, extract_structured_data

async with TacoClient(agent_url="http://localhost:8001") as client:
    # Discover agent capabilities
    card = await client.discover()
    print(card.name, card.skills)

    # Send a task
    task = await client.send_message("estimate", bom_data)
    estimate = extract_structured_data(task.artifacts[0].parts[0])

    # Or use the convenience method
    result = await client.run_task(
        task_type="estimate",
        input_data=bom_data,
    )
```

## Quick Start: Discover Agents

```python
from taco import AgentRegistry

registry = AgentRegistry()
await registry.register("http://estimator:8001")
await registry.register("http://supplier:8002")
await registry.register("http://rfi-agent:8003")

# Find by trade
mechanical = registry.find(trade="mechanical")

# Find by task type
estimators = registry.find(task_type="estimate")

# Find by CSI division
hvac = registry.find(csi_division="23")

# Combine filters
agents = registry.find(
    trade="mechanical",
    task_type="estimate",
    project_type="healthcare",
)
```

## Data Schema Models

All schemas use Pydantic v2 with snake_case Python attributes and camelCase JSON serialization:

```python
from taco import BOMV1, RFIV1, EstimateV1, QuoteV1, ScheduleV1, ChangeOrderV1

# Parse incoming JSON
bom = BOMV1.model_validate(json_payload)

# Access fields
print(bom.project_id)
print(bom.line_items[0].description)
print(bom.metadata.confidence)

# Serialize to JSON
json_output = bom.model_dump(by_alias=True, exclude_none=True)
```

## Streaming

The server supports SSE streaming for long-running tasks:

```python
from collections.abc import AsyncIterator
from taco import Part, make_text_part, make_data_part

async def stream_handler(task, input_data) -> AsyncIterator[Part]:
    for chunk in process_incrementally(input_data):
        yield make_text_part(f"Processing: {chunk}")
    yield make_data_part(final_result)

server.register_streaming_handler("estimate", stream_handler)
```

## Quick Start: Bidirectional Agent

`TacoAgent` combines an `A2AServer` (inbound), `AgentRegistry` (peer discovery), and a `TacoClient` pool (outbound) into a single object:

```python
import uvicorn
from taco import TacoAgent, ConstructionAgentCard, ConstructionSkill

card = ConstructionAgentCard(
    name="My Agent",
    url="http://localhost:8100",
    trade="electrical",
    skills=[
        ConstructionSkill(
            id="analyze",
            name="Analyze Data",
            task_type="analyze",
            input_schema="question-v1",
            output_schema="analysis-v1",
        )
    ],
)

# Discovers peers at startup, enables monitor UI at /monitor
agent = TacoAgent(
    card,
    peers=["http://localhost:8101"],  # or a YAML/JSON file path
    enable_monitor=True,
)

agent.register_handler("analyze", my_handler)

# Inside a handler, call a peer agent:
async def my_handler(task, input_data):
    result = await agent.send_to_peer("data-query", {"query": "..."})
    ...

uvicorn.run(agent.app, host="0.0.0.0", port=8100)
```

## Agent Monitor

The monitor is an opt-in live tracing UI that shows all A2A traffic flowing through an agent. Enable it with one flag:

```python
# Via A2AServer
server = A2AServer(card.to_a2a(), enable_monitor=True)

# Via TacoAgent
agent = TacoAgent(card, enable_monitor=True)
```

The monitor UI is mounted at `/monitor` on the agent's existing port — no extra servers or ports needed. It includes:

- **Live dashboard** at `/monitor/` with real-time event timeline
- **WebSocket** at `/monitor/ws` for live event streaming
- **REST API** at `/monitor/api/events`, `/monitor/api/info`, `/monitor/api/clear`

Events are tagged with labels like `RECEIVED`, `REPLIED`, `CALLING`, `GOT REPLY`, `PROCESSING`, `COMPLETED`, `FAILED`, and `DISCOVERY` for clear traceability.

For explicit control, use the `enable_monitor()` function:

```python
from taco.monitor import enable_monitor

enable_monitor(server=server, client=client, registry=registry)
```

## Status

The SDK is in early development. The API surface is subject to change. Current capabilities:

- Full A2A protocol support (message/send, message/stream, tasks/get, tasks/cancel)
- Agent Card discovery at `/.well-known/agent.json`
- Multi-turn conversations via context IDs
- In-memory task store
- Pydantic v2 models with full validation
- 178 tests passing

See the [GitHub repository](https://github.com/pelles-ai/taco) for the latest.
