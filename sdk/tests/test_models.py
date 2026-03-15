"""Tests for taco.models — A2A protocol wire-format models."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

from taco._compat import (
    extract_structured_data,
    extract_text,
    make_artifact,
    make_data_part,
    make_message,
    make_text_part,
)
from taco.types import (
    AgentCard,
    AgentConstructionExt,
    DataPart,
    Part,
    Role,
    SkillConstructionExt,
    Task,
    TaskState,
    TaskStatus,
    TextPart,
)


class TestPart:
    def test_text_part(self):
        p = make_text_part("hello")
        assert extract_text(p) == "hello"
        assert extract_structured_data(p) is None

    def test_structured_data_part(self):
        p = make_data_part({"key": "value"})
        assert extract_structured_data(p) == {"key": "value"}
        assert extract_text(p) is None

    def test_text_part_via_constructor(self):
        p = Part(root=TextPart(text="hello"))
        assert p.root.text == "hello"

    def test_data_part_via_constructor(self):
        p = Part(root=DataPart(data={"key": "value"}))
        assert p.root.data == {"key": "value"}


class TestCamelCaseSerialization:
    def test_task_status_round_trip(self):
        ts = TaskStatus(state=TaskState.working)
        data = ts.model_dump(by_alias=True)
        assert "state" in data
        ts2 = TaskStatus.model_validate(data)
        assert ts2.state == TaskState.working

    def test_task_round_trip(self):
        task = Task(
            id=str(uuid.uuid4()),
            status=TaskStatus(state=TaskState.completed),
            context_id="ctx-123",
            metadata={"taskType": "test"},
        )
        data = task.model_dump(by_alias=True, exclude_none=True)
        assert "contextId" in data
        assert data["contextId"] == "ctx-123"
        task2 = Task.model_validate(data)
        assert task2.context_id == "ctx-123"

    def test_skill_construction_ext_aliases(self):
        ext = SkillConstructionExt(
            task_type="estimate",
            input_schema="bom-v1",
            output_schema="estimate-v1",
        )
        data = ext.model_dump(by_alias=True)
        assert data["taskType"] == "estimate"
        assert data["inputSchema"] == "bom-v1"
        assert data["outputSchema"] == "estimate-v1"

    def test_agent_card_x_construction_alias(self):
        card = AgentCard(
            name="Test",
            description="Test agent",
            url="http://localhost:9999",
            x_construction=AgentConstructionExt(
                trade="mechanical",
                csi_divisions=["23"],
            ),
        )
        data = card.model_dump(by_alias=True, exclude_none=True)
        assert "x-construction" in data
        assert data["x-construction"]["trade"] == "mechanical"


class TestAgentCard:
    def test_full_construction_card(self, sample_agent_card: AgentCard):
        data = sample_agent_card.model_dump(by_alias=True, exclude_none=True)
        card2 = AgentCard.model_validate(data)
        assert card2.name == "Test Agent"
        assert card2.x_construction is not None
        assert card2.x_construction.trade == "mechanical"
        assert card2.x_construction.csi_divisions == ["23"]
        assert card2.skills[0].x_construction.task_type == "test-task"

    def test_empty_name_fails(self):
        with pytest.raises(ValidationError):
            AgentCard(name="", description="x", url="http://localhost")

    def test_empty_description_fails(self):
        with pytest.raises(ValidationError):
            AgentCard(name="x", description="", url="http://localhost")


class TestTaskState:
    def test_core_values(self):
        # A2A SDK TaskState is a superset — check core values exist
        core = {"working", "completed", "failed", "canceled", "input-required"}
        actual = {s.value for s in TaskState}
        assert core.issubset(actual)

    def test_string_value(self):
        assert TaskState.working == "working"
        assert TaskState.completed == "completed"


class TestLiterals:
    def test_invalid_trade(self):
        with pytest.raises(ValidationError):
            AgentConstructionExt(trade="nonexistent")

    def test_valid_trade(self):
        ext = AgentConstructionExt(trade="electrical")
        assert ext.trade == "electrical"

    def test_invalid_project_type(self):
        with pytest.raises(ValidationError):
            AgentConstructionExt(trade="mechanical", project_types=["nonexistent"])


class TestMessage:
    def test_message_creation(self):
        m = make_message("user", [make_text_part("hello")])
        assert m.role == Role.user
        assert len(m.parts) == 1

    def test_message_with_multiple_parts(self):
        m = make_message("user", [make_text_part("hello"), make_data_part({"x": 1})])
        assert len(m.parts) == 2


class TestArtifact:
    def test_artifact_with_metadata(self):
        a = make_artifact(
            parts=[make_text_part("data")],
            name="test",
            description="desc",
            metadata={"schema": "test-v1"},
        )
        assert a.metadata["schema"] == "test-v1"


class TestCompatHelpers:
    def test_make_text_part(self):
        p = make_text_part("hello")
        assert isinstance(p.root, TextPart)
        assert p.root.text == "hello"

    def test_make_data_part(self):
        p = make_data_part({"x": 1})
        assert isinstance(p.root, DataPart)
        assert p.root.data == {"x": 1}

    def test_make_message_auto_id(self):
        m = make_message("agent", [make_text_part("hi")])
        assert m.message_id is not None
        assert m.role == Role.agent

    def test_make_artifact_auto_id(self):
        a = make_artifact([make_text_part("data")])
        assert a.artifact_id is not None

    def test_extract_text_from_text_part(self):
        p = make_text_part("hello")
        assert extract_text(p) == "hello"

    def test_extract_text_from_data_part(self):
        p = make_data_part({"x": 1})
        assert extract_text(p) is None

    def test_extract_structured_data_from_data_part(self):
        p = make_data_part({"x": 1})
        assert extract_structured_data(p) == {"x": 1}

    def test_extract_structured_data_from_text_part(self):
        p = make_text_part("hello")
        assert extract_structured_data(p) is None


class TestUpstreamReExports:
    """Tests for a2a.utils re-exports via taco._compat."""

    def test_get_text_parts(self):
        from taco._compat import get_text_parts

        parts = [make_text_part("a"), make_data_part({"x": 1}), make_text_part("b")]
        result = get_text_parts(parts)
        assert result == ["a", "b"]

    def test_get_data_parts(self):
        from taco._compat import get_data_parts

        parts = [make_text_part("a"), make_data_part({"x": 1}), make_data_part({"y": 2})]
        result = get_data_parts(parts)
        assert result == [{"x": 1}, {"y": 2}]

    def test_get_file_parts_empty(self):
        from taco._compat import get_file_parts

        parts = [make_text_part("a"), make_data_part({"x": 1})]
        result = get_file_parts(parts)
        assert result == []

    def test_new_agent_text_message(self):
        from taco._compat import new_agent_text_message

        msg = new_agent_text_message("hello")
        assert msg.role == Role.agent
        assert len(msg.parts) == 1

    def test_new_agent_parts_message(self):
        from taco._compat import new_agent_parts_message

        parts = [make_text_part("x"), make_data_part({"y": 1})]
        msg = new_agent_parts_message(parts)
        assert msg.role == Role.agent
        assert len(msg.parts) == 2

    def test_get_message_text(self):
        from taco._compat import get_message_text

        msg = make_message("user", [make_text_part("hello"), make_text_part("world")])
        result = get_message_text(msg)
        assert "hello" in result
        assert "world" in result

    def test_new_text_artifact(self):
        from taco._compat import new_text_artifact

        a = new_text_artifact(name="test", text="hello")
        assert a.name == "test"
        assert len(a.parts) == 1

    def test_new_data_artifact(self):
        from taco._compat import new_data_artifact

        a = new_data_artifact(name="test", data={"key": "val"})
        assert a.name == "test"
        assert len(a.parts) == 1

    def test_imports_via_taco_package(self):
        """Verify all re-exports are accessible from the top-level taco package."""
        import taco

        assert callable(taco.get_text_parts)
        assert callable(taco.get_data_parts)
        assert callable(taco.get_file_parts)
        assert callable(taco.new_agent_text_message)
        assert callable(taco.new_agent_parts_message)
        assert callable(taco.get_message_text)
        assert callable(taco.new_text_artifact)
        assert callable(taco.new_data_artifact)

    def test_file_part_exported(self):
        """FilePart should be importable from taco package."""
        from taco import FilePart

        assert FilePart is not None


class TestBackwardCompat:
    def test_json_rpc_aliases(self):
        from taco.models import JsonRpcError, JsonRpcRequest, JsonRpcResponse
        from taco.types import JSONRPCError, JSONRPCRequest, JSONRPCResponse

        assert JsonRpcError is JSONRPCError
        assert JsonRpcRequest is JSONRPCRequest
        assert JsonRpcResponse is JSONRPCResponse

    def test_taco_base_model_alias(self):
        from a2a._base import A2ABaseModel

        from taco.models import TacoBaseModel

        assert TacoBaseModel is A2ABaseModel
