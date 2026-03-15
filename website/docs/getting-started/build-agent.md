---
sidebar_position: 1
title: Build Your First Agent
---

# Build Your First Agent in 5 Minutes

This guide walks you through creating a TACO-compatible construction agent from scratch.

## 1. Install the SDK

```bash
pip install taco-agent[server]
```

This installs the TACO SDK with FastAPI-based server support.

## 2. Define Your Agent Card

Every TACO agent needs an **Agent Card** — a declaration of who you are, what trade you serve, and what you can do.

```python
from taco import ConstructionAgentCard, ConstructionSkill

card = ConstructionAgentCard(
    name="My Mechanical Takeoff Agent",
    url="http://localhost:8080",
    trade="mechanical",
    csi_divisions=["22", "23"],  # Plumbing & HVAC
    skills=[
        ConstructionSkill(
            id="generate-bom",
            name="Generate Bill of Materials",
            description="Generates a BOM from project drawings",
            task_type="takeoff",
            output_schema="bom-v1",
        )
    ],
)
```

Key fields:
- **`trade`** — Your construction trade (e.g., `mechanical`, `electrical`, `structural`)
- **`csi_divisions`** — CSI MasterFormat divisions your agent covers
- **`skills`** — What your agent can do, each with a `task_type` and optional `output_schema`

See [Agent Card Extensions](/docs/agent-card-extensions) for all available fields.

## 3. Create a Handler

The handler processes incoming tasks. It receives a `Task` object and parsed input data, and returns an `Artifact`.

```python
from taco.server import A2AServer
from taco._compat import make_artifact, make_data_part
from a2a.types import Artifact, Task


async def handle_takeoff(task: Task, input_data: dict) -> Artifact:
    # Do your work here
    bom_result = {"items": [{"description": "Copper pipe 1/2in", "quantity": 120}]}

    # Return the result as an artifact
    return make_artifact(
        parts=[make_data_part(bom_result)],
        name="bom",
        description="Generated bill of materials",
    )
```

The server handles status updates (working → completed) and event streaming automatically.

## 4. Start the Server

```python
import uvicorn

# Convert card to A2A format and create the server
a2a_card = card.to_a2a()
server = A2AServer(a2a_card)
server.register_handler("takeoff", handle_takeoff)

uvicorn.run(server.app, host="0.0.0.0", port=8080)
```

Or use the shorthand if you just need to serve the agent card:

```python
card.serve(host="0.0.0.0", port=8080)
```

## 5. Test It

Your agent is now running. Test it with curl:

```bash
# Check the agent card
curl http://localhost:8080/.well-known/agent.json | python -m json.tool

# Check health
curl http://localhost:8080/health

# Send a task (JSON-RPC)
curl -X POST http://localhost:8080/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "message/send",
    "id": "1",
    "params": {
      "message": {
        "messageId": "msg-1",
        "role": "user",
        "parts": [{"kind": "text", "text": "Generate BOM for project drawings"}]
      }
    }
  }'
```

Or use the TACO CLI:

```bash
taco inspect http://localhost:8080
taco send http://localhost:8080 "Generate BOM for project drawings"
```

## Next Steps

- Browse the full list of [Task Types](/docs/task-types) your agent can support
- Learn about [Data Schemas](/docs/schemas/) for typed output
- See the [SDK Reference](/docs/sdk) for all available classes and options
