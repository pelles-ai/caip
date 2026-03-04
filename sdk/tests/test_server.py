"""Tests for taco.server — A2A server protocol implementation."""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx
import pytest

from taco.types import (
    AgentCard,
    Artifact,
    Part,
    Task,
    TaskState,
)
from taco._compat import (
    make_artifact,
    make_data_part,
    make_text_part,
    extract_structured_data,
)
from taco.server import A2AServer


@pytest.fixture()
def client(sample_server: A2AServer):
    """HTTPX async client wired to the test server via ASGI transport."""
    transport = httpx.ASGITransport(app=sample_server.app)
    return httpx.AsyncClient(transport=transport, base_url="http://test")


def _rpc(method: str, params: dict | None = None, rpc_id: str = "1") -> dict:
    return {"jsonrpc": "2.0", "id": rpc_id, "method": method, "params": params or {}}


def _msg_payload(
    method: str, task_type: str, input_data: dict, context_id: str | None = None,
) -> dict:
    """Build a JSON-RPC message/send or message/stream payload.

    Uses the A2A SDK message format with DataPart.
    """
    msg = {
        "role": "user",
        "parts": [{"kind": "data", "data": input_data}],
        "messageId": "test-msg-1",
    }
    params: dict = {
        "message": msg,
        "metadata": {"taskType": task_type},
    }
    if context_id:
        params["contextId"] = context_id
    return _rpc(method, params)


def _send_msg(task_type: str, input_data: dict, context_id: str | None = None) -> dict:
    return _msg_payload("message/send", task_type, input_data, context_id)


def _stream_msg(task_type: str, input_data: dict, context_id: str | None = None) -> dict:
    return _msg_payload("message/stream", task_type, input_data, context_id)


class TestAgentCardDiscovery:
    async def test_agent_card_endpoint(self, client: httpx.AsyncClient):
        # TACO serves its own card at /.well-known/agent-card.json
        resp = await client.get("/.well-known/agent-card.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Agent"
        assert data["url"] == "http://localhost:9999"

    async def test_agent_card_has_skills(self, client: httpx.AsyncClient):
        resp = await client.get("/.well-known/agent-card.json")
        data = resp.json()
        assert len(data["skills"]) == 1
        assert data["skills"][0]["x-construction"]["taskType"] == "test-task"

    async def test_agent_card_has_x_construction(self, client: httpx.AsyncClient):
        resp = await client.get("/.well-known/agent-card.json")
        data = resp.json()
        xc = data["x-construction"]
        assert xc["trade"] == "mechanical"
        assert "23" in xc["csiDivisions"]

    async def test_agent_card_also_at_old_path(self, client: httpx.AsyncClient):
        """A2A SDK also serves at /.well-known/agent.json for backward compat."""
        resp = await client.get("/.well-known/agent.json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["name"] == "Test Agent"


class TestMessageSend:
    async def test_success(self, client: httpx.AsyncClient):
        payload = _send_msg("test-task", {"foo": "bar"})
        resp = await client.post("/", json=payload)
        assert resp.status_code == 200
        body = resp.json()
        assert body["jsonrpc"] == "2.0"
        result = body["result"]
        assert result["status"]["state"] == "completed"
        # The echo handler returns input as DataPart
        artifacts = result["artifacts"]
        assert len(artifacts) >= 1
        parts = artifacts[0]["parts"]
        assert len(parts) >= 1
        # DataPart has 'data' key in A2A SDK format
        assert parts[0]["data"] == {"foo": "bar"}

    async def test_missing_task_type(self, client: httpx.AsyncClient):
        payload = _rpc("message/send", {
            "message": {
                "role": "user",
                "parts": [{"kind": "data", "data": {}}],
                "messageId": "test-1",
            },
            "metadata": {},
        })
        resp = await client.post("/", json=payload)
        body = resp.json()
        # With a single handler, it should auto-select
        assert "result" in body

    async def test_artifact_metadata(self, client: httpx.AsyncClient):
        payload = _send_msg("test-task", {"key": "value"})
        resp = await client.post("/", json=payload)
        body = resp.json()
        artifact = body["result"]["artifacts"][0]
        assert artifact["metadata"]["schema"] == "test-v1"
        assert artifact["name"] == "echo-result"


class TestTaskGetAndCancel:
    async def test_get_task(self, client: httpx.AsyncClient):
        # First create a task
        send_resp = await client.post("/", json=_send_msg("test-task", {"a": 1}))
        task_id = send_resp.json()["result"]["id"]

        # Then get it
        get_payload = _rpc("tasks/get", {"id": task_id})
        resp = await client.post("/", json=get_payload)
        body = resp.json()
        assert body["result"]["id"] == task_id
        assert body["result"]["status"]["state"] == "completed"

    async def test_cancel_completed_task_returns_error(self, client: httpx.AsyncClient):
        """A2A SDK correctly rejects cancellation of already-completed tasks."""
        send_resp = await client.post("/", json=_send_msg("test-task", {"a": 1}))
        task_id = send_resp.json()["result"]["id"]

        cancel_payload = _rpc("tasks/cancel", {"id": task_id})
        resp = await client.post("/", json=cancel_payload)
        body = resp.json()
        assert "error" in body


class TestErrorHandling:
    async def test_invalid_json(self, client: httpx.AsyncClient):
        resp = await client.post(
            "/",
            content=b"not json",
            headers={"content-type": "application/json"},
        )
        body = resp.json()
        # A2A SDK returns error for invalid JSON
        assert "error" in body

    async def test_handler_exception(self, sample_agent_card: AgentCard):
        server = A2AServer(sample_agent_card)

        async def failing_handler(task: Task, input_data: dict) -> Artifact:
            raise RuntimeError("boom")

        server.register_handler("test-task", failing_handler)
        transport = httpx.ASGITransport(app=server.app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.post("/", json=_send_msg("test-task", {}))
            body = resp.json()
            result = body["result"]
            assert result["status"]["state"] == "failed"
