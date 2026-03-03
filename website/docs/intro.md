---
sidebar_position: 1
title: Introduction
---

# TACO — The A2A Construction Open-standard

An open standard for AI agent communication in the built environment.

## The Problem

Construction is one of the most fragmented industries in the world. A single commercial project can involve dozens of companies — general contractors, mechanical subs, electrical subs, architects, engineers, suppliers — each using different software, different file formats, and different workflows.

AI agents are entering this ecosystem fast. Agents that generate takeoffs from plan sheets. Agents that draft RFIs. Agents that coordinate schedules. Agents that source materials and compare supplier quotes.

But they're being built in isolation. Every vendor defines their own API, their own data formats, their own vocabulary. The result is a new generation of silos — AI silos — layered on top of the existing ones.

## Why Now

The [A2A protocol](https://a2a-protocol.org) (Linux Foundation) provides a universal standard for agent-to-agent communication: Agent Cards for discovery, JSON-RPC for messaging, task lifecycle management, and streaming. It solves the transport layer.

But A2A is domain-agnostic. It doesn't know what a takeoff is, what a BOM looks like, or how to find an agent that handles mechanical estimating for healthcare projects. Construction needs a shared vocabulary on top of A2A.

## What TACO Adds

TACO is a construction-specific ontology layer built on A2A. It defines:

| Layer | What it defines | Example |
|-------|----------------|---------|
| **Task Types** | A typed vocabulary of construction workflows | `takeoff`, `estimate`, `rfi-generation`, `submittal-review` |
| **Data Schemas** | Typed JSON schemas for construction artifacts | `bom-v1`, `rfi-v1`, `estimate-v1`, `schedule-v1`, `quote-v1` |
| **Agent Discovery** | Construction extensions to A2A Agent Cards | Filter by trade, CSI division, project type, platform integration |
| **Security** | Scope taxonomy, trust tiers, token delegation | `taco:trade:mechanical`, `taco:task:estimate`, `taco:project:PRJ-0042:write` |

Every TACO agent is a standard A2A agent. Zero lock-in.

## What TACO Does Not Do

- **Replace A2A.** TACO uses A2A's native extension points. It does not fork or modify the protocol.
- **Dictate implementation.** Agents are opaque. TACO defines what goes in and what comes out — not how agents work internally.
- **Replace existing platforms.** TACO integrates with Procore, ACC, Bluebeam, and others. It connects the ecosystem; it doesn't replace it.
- **Require AI.** While designed for AI agents, any software that speaks A2A and follows TACO schemas can participate — including traditional APIs, human-in-the-loop tools, and legacy system adapters.

## Quick Example

```python
from taco import ConstructionAgentCard, ConstructionSkill

# Define an agent that performs mechanical takeoffs
card = ConstructionAgentCard(
    name="My Mechanical Takeoff Agent",
    trade="mechanical",
    csi_divisions=["22", "23"],
    skills=[
        ConstructionSkill(
            id="generate-bom",
            task_type="takeoff",
            output_schema="bom-v1",
        )
    ],
)

# Serve as an A2A-compatible endpoint
card.serve(host="0.0.0.0", port=8080)
```

## Status

TACO is early stage. We're defining the core schemas and building the reference SDK. We're looking for construction technology companies, trade contractors, GCs, and platform vendors to help shape the standard.

- [GitHub Repository](https://github.com/pelles-ai/taco)
- [Contributing Guide](https://github.com/pelles-ai/taco/blob/main/CONTRIBUTING.md)
