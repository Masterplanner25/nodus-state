import uuid

import pytest

from nodus_state import ExecutionContext, ExecutionResult


# ── ExecutionContext ──────────────────────────────────────────────────────────

def test_execution_context_fields():
    ctx = ExecutionContext(request_id="req-1", route_name="flow.run")
    assert ctx.request_id == "req-1"
    assert ctx.route_name == "flow.run"
    assert ctx.user_id is None
    assert ctx.pipeline_active is True
    assert ctx.metadata == {}


def test_execution_context_new_generates_uuid():
    ctx = ExecutionContext.new("flow.run")
    uuid.UUID(ctx.request_id)  # must be valid UUID
    assert ctx.route_name == "flow.run"


def test_execution_context_new_with_user_id():
    ctx = ExecutionContext.new("agent.run", user_id="user-123")
    assert ctx.user_id == "user-123"


def test_execution_context_metadata_mutable():
    ctx = ExecutionContext.new("test")
    ctx.metadata["trace_id"] = "t1"
    assert ctx.metadata["trace_id"] == "t1"


def test_execution_context_two_instances_independent_metadata():
    c1 = ExecutionContext.new("r1")
    c2 = ExecutionContext.new("r2")
    c1.metadata["x"] = 1
    assert "x" not in c2.metadata


# ── ExecutionResult ───────────────────────────────────────────────────────────

def test_execution_result_defaults():
    r = ExecutionResult(success=True)
    assert r.data is None
    assert r.error is None
    assert r.memory_context_count == 0
    assert r.eu_status is None
    assert r.metadata == {}


def test_to_response_success_shape():
    r = ExecutionResult(
        success=True,
        data={"key": "val"},
        metadata={"trace_id": "t1", "eu_id": "eu-1"},
    )
    resp = r.to_response()
    assert resp["status"] == "success"
    assert resp["data"] == {"key": "val"}
    assert resp["trace_id"] == "t1"
    assert resp["eu_id"] == "eu-1"
    assert resp["memory_context_count"] == 0


def test_to_response_error_shape():
    r = ExecutionResult(
        success=False,
        error="something broke",
        metadata={"trace_id": "t2", "status_code": 500},
    )
    resp = r.to_response()
    assert resp["status"] == "error"
    assert resp["metadata"]["error"] == "something broke"
    assert resp["metadata"]["status_code"] == 500


def test_to_response_eu_status_overrides_success_label():
    r = ExecutionResult(success=True, eu_status="waiting")
    resp = r.to_response()
    assert resp["status"] == "waiting"


def test_to_response_eu_status_waiting_includes_wait_for():
    r = ExecutionResult(
        success=True,
        eu_status="waiting",
        metadata={"eu_wait_for": "op.completed"},
    )
    resp = r.to_response()
    assert resp["metadata"]["eu_wait_for"] == "op.completed"


def test_to_response_side_effects_degrade():
    r = ExecutionResult(
        success=True,
        metadata={
            "side_effects": {
                "db_write": {"status": "success"},
                "event_emit": {"status": "failed"},
            }
        },
    )
    resp = r.to_response()
    assert "event_emit" in resp["metadata"]["degraded_side_effects"]
    assert "db_write" not in resp["metadata"]["degraded_side_effects"]


def test_to_response_events_from_metadata():
    r = ExecutionResult(
        success=True,
        metadata={"event_refs": [{"id": "e1"}, {"id": "e2"}]},
    )
    resp = r.to_response()
    assert len(resp["metadata"]["events"]) == 2
