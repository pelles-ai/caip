"""ACME Estimating Agent — generates cost estimates from a BOM.

Port 8001 | Task type: estimate | bom-v1 → estimate-v1
"""

from __future__ import annotations

import json
import os

import uvicorn

from common.a2a_models import (
    AgentCard,
    AgentConstructionExt,
    AgentSkill,
    Artifact,
    Part,
    SkillConstructionExt,
    Task,
)
from common.a2a_server import A2AServer
from common.llm_provider import LLMProvider

llm = LLMProvider()

SYSTEM_PROMPT = """\
You are a construction cost estimating expert. Given a Bill of Materials (BOM) \
in JSON format, generate a detailed cost estimate.

For each BOM line item, provide:
- materialUnitCost and materialTotal (realistic US national averages for commercial construction)
- laborHours and laborRate (union mechanical rates, ~$85-$120/hr depending on complexity)
- equipmentCost (if applicable — cranes, lifts, etc.)
- subtotal for each line

Then provide a summary with:
- totalMaterial, totalLabor, totalEquipment
- subtotal
- overheadPercentage (10-15%) and overheadAmount
- profitPercentage (8-12%) and profitAmount
- grandTotal

Include metadata with generatedBy="acme-estimating-agent", generatedAt (current ISO timestamp), \
confidence (0-1), pricingRegion="US-National", pricingDate (today), and any notes.

Output MUST be valid JSON matching this structure:
{
  "projectId": "...", "trade": "...", "csiDivision": "...",
  "lineItems": [{"bomItemId": "...", "description": "...", "quantity": N, "unit": "...",
    "materialUnitCost": N, "materialTotal": N, "laborHours": N, "laborRate": N,
    "laborTotal": N, "equipmentCost": N, "subtotal": N}],
  "summary": {"totalMaterial": N, "totalLabor": N, "totalEquipment": N, "subtotal": N,
    "overheadPercentage": N, "overheadAmount": N, "profitPercentage": N, "profitAmount": N,
    "grandTotal": N},
  "metadata": {"generatedBy": "...", "generatedAt": "...", "confidence": N,
    "pricingRegion": "...", "pricingDate": "...", "notes": []}
}

Return ONLY the JSON object, no markdown or explanation."""

HOST = os.getenv("AGENT_HOST", "localhost")

card = AgentCard(
    name="ACME Estimating Agent",
    description="Generates construction cost estimates from bills of materials using AI",
    url=f"http://{HOST}:8001",
    skills=[
        AgentSkill(
            id="generate-estimate",
            name="Generate Cost Estimate",
            description="Takes a BOM and produces a detailed cost estimate with labor, material, and equipment costs",
            x_construction=SkillConstructionExt(
                task_type="estimate",
                input_schema="bom-v1",
                output_schema="estimate-v1",
            ),
        ),
    ],
    x_construction=AgentConstructionExt(
        trade="multi-trade",
        csi_divisions=["22", "23", "26"],
        project_types=["commercial", "healthcare", "education"],
        data_formats={"input": ["bom-json"], "output": ["estimate-json", "csv"]},
        integrations=["procore", "sage"],
    ),
)

server = A2AServer(card)


async def handle_estimate(task: Task, input_data: dict) -> Artifact:
    result = await llm.generate_json(SYSTEM_PROMPT, json.dumps(input_data, indent=2))
    return Artifact(
        name="cost-estimate",
        description="AI-generated cost estimate from BOM",
        parts=[Part(structured_data=result)],
        metadata={"schema": "estimate-v1"},
    )


server.register_handler("estimate", handle_estimate)
app = server.app

if __name__ == "__main__":
    uvicorn.run("agents.estimating_agent:app", host="0.0.0.0", port=8001, reload=False)
