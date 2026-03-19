# TACO Examples

## Standalone Examples

Quick-start examples you can run immediately with zero configuration (no LLM key needed):

| Example | What it shows |
|---|---|
| [`quick_start.py`](quick_start.py) | Minimal single-file agent (~30 lines) with monitor UI |
| [`peer_communication.py`](peer_communication.py) | Two agents talking to each other via `TacoAgent` with peer discovery |

```bash
# Minimal agent
pip install taco-agent[all]
python quick_start.py
# Open http://localhost:8080/.well-known/agent.json and http://localhost:8080/monitor

# Two agents communicating
python peer_communication.py data          # Terminal 1
python peer_communication.py orchestrator  # Terminal 2
# Open http://localhost:9000/monitor to see inter-agent traffic
```

---

## Sandbox Demo

A working demonstration of the Construction A2A Interoperability Protocol. Three LLM-powered agents from "different companies" exchange typed construction data over A2A, coordinated by an orchestrator with a web dashboard.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  GC Orchestrator + Dashboard  (http://localhost:8000)        │
│  Discovers agents, sends tasks, shows typed results          │
└───────┬──────────────────┬──────────────────┬────────────────┘
        │                  │                  │
        ▼                  ▼                  ▼
┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ ACME          │  │ BuildSupply   │  │ PlanCheck     │
│ Estimating    │  │ Quote Agent   │  │ RFI Agent     │
│ Agent         │  │               │  │               │
│ :8001         │  │ :8002         │  │ :8003         │
│               │  │               │  │               │
│ bom-v1 →      │  │ bom-v1 →      │  │ bom-v1 →      │
│ estimate-v1   │  │ quote-v1      │  │ rfi-v1        │
│ + VE analysis │  │               │  │               │
└───────────────┘  └───────────────┘  └───────────────┘
```

Each agent is a standard A2A endpoint:
- `GET /.well-known/agent.json` — Agent Card with `x-construction` extensions
- `POST /` — JSON-RPC 2.0 (`message/send`, `message/stream`, `tasks/get`, `tasks/cancel`)

## Quick Start

### 1. Set up environment

```bash
cd examples
cp .env.example .env
# Edit .env with your API key
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run locally

```bash
python run_demo.py
```

### 4. Open the dashboard

Navigate to **http://localhost:8000**

1. Click **"Discover Agents"** — three agents appear with their trade, CSI divisions, and skills
2. Click **"Send Task"** on any agent skill — the BOM is sent via JSON-RPC, the LLM processes it, and typed results appear
3. Click **"Run Full Pipeline"** — sends the BOM to all three agents in parallel and shows combined results
4. Check the **message log** at the bottom to see the raw A2A JSON-RPC exchanges

## Docker Compose

```bash
cd examples
cp .env.example .env
# Edit .env with your API key
docker compose up --build
```

## Demo: Dynamic Skill Registration

This showcases how the A2A ecosystem adapts when agents add new capabilities:

1. Start the demo and click "Discover Agents"
2. Click **"+ Add VE Skill to Estimator"** in the header
3. Click **"Discover Agents"** again — the Estimating Agent now shows a second skill marked **NEW**
4. Click "Send Task" on the new "Value Engineering Analysis" skill

You can also add skills via curl:

```bash
curl -X POST http://localhost:8001/admin/skills \
  -H "Content-Type: application/json" \
  -d '{
    "id": "value-engineering",
    "name": "Value Engineering Analysis",
    "description": "Identifies cost reduction opportunities",
    "x-construction": {
      "taskType": "value-engineering",
      "inputSchema": "bom-v1",
      "outputSchema": "ve-suggestions-v1"
    }
  }'
```

## Demo: Full Pipeline

Click **"Run Full Pipeline"** in the dashboard header to send the sample BOM to all three agents in parallel. The orchestrator calls `POST /api/run-pipeline`, which dispatches estimate, quote, and RFI tasks concurrently and returns combined results.

You can also call it directly:

```bash
curl -X POST http://localhost:8000/api/run-pipeline
```

## Demo: Agent-to-Agent Communication

The estimating agent can fetch real supplier pricing from the supplier quote agent before generating its estimate. Set the `SUPPLIER_AGENT_URL` environment variable:

```bash
export SUPPLIER_AGENT_URL=http://localhost:8002
```

When set, the estimating agent uses the TACO SDK client to send a `quote` task to the supplier agent, then incorporates the real pricing into the LLM prompt. The artifact metadata includes `supplierDataUsed: true/false` to indicate whether supplier data was used.

## Demo: Agent Monitors

Every agent includes a live tracing UI at `/monitor`. After starting the demo, open any agent's monitor to see real-time A2A traffic:

- **Estimating Agent:** http://localhost:8001/monitor
- **Supplier Agent:** http://localhost:8002/monitor
- **RFI Agent:** http://localhost:8003/monitor

The monitor traces:
- **Incoming requests** — JSON-RPC calls received by the agent
- **Handler execution** — Task processing timing and results
- **Outgoing calls** — Peer agent calls (e.g., estimating → supplier)
- **Discovery** — Agent registration events

Events stream live via WebSocket and are stored in a ring buffer (max 2000).

To enable the monitor in your own agent, add `enable_monitor=True`:

```python
server = A2AServer(card, enable_monitor=True)
```

## Verification

Test agent discovery directly:

```bash
curl http://localhost:8001/.well-known/agent.json | python -m json.tool
```

Test a task via JSON-RPC:

```bash
curl -X POST http://localhost:8001/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-1",
    "method": "message/send",
    "params": {
      "message": {
        "role": "user",
        "parts": [{"kind": "data", "data": {"projectId": "test", "trade": "mechanical", "csiDivision": "23", "lineItems": [], "metadata": {"generatedBy": "test", "generatedAt": "2026-01-01T00:00:00Z"}}}]
      },
      "metadata": {"taskType": "estimate"}
    }
  }'
```

## File Structure

```
examples/
├── README.md
├── quick_start.py               # Minimal single-file agent
├── peer_communication.py        # Two agents communicating
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── run_demo.py
├── common/
│   ├── a2a_models.py          # A2A protocol Pydantic models
│   ├── a2a_server.py          # Reusable A2A server base class
│   ├── llm_provider.py        # Anthropic/OpenAI wrapper
│   ├── schemas.py             # bom-v1, rfi-v1, estimate-v1, quote-v1 Pydantic models
│   └── sample_data.py         # Sample mechanical HVAC BOM
├── agents/
│   ├── estimating_agent.py    # Port 8001 — estimate + value-engineering
│   ├── supplier_quote_agent.py # Port 8002 — material-procurement
│   └── rfi_generation_agent.py # Port 8003 — rfi-generation
└── orchestrator/
    ├── app.py                 # Orchestrator backend
    └── dashboard.html         # Web UI
```

## LLM Configuration

Set `LLM_PROVIDER` in `.env`:

| Provider | Env vars | Default model |
|----------|----------|---------------|
| `anthropic` (default) | `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | `claude-sonnet-4-20250514` |
| `openai` | `OPENAI_API_KEY`, `OPENAI_MODEL` | `gpt-4o` |
