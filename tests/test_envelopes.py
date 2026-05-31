from nodus_state import error, success, unified


# ── success() ─────────────────────────────────────────────────────────────────

def test_success_status():
    env = success({"key": "val"}, [], "trace-1")
    assert env["status"] == "SUCCESS"


def test_success_data_and_result_equal():
    data = {"x": 1}
    env = success(data, [], "t")
    assert env["data"] == data
    assert env["result"] == data


def test_success_trace_id_coerced_to_str():
    env = success(None, [], 123)
    assert env["trace_id"] == "123"


def test_success_events_default_empty():
    env = success("ok", None, "t")
    assert env["events"] == []


def test_success_next_action_default_none():
    env = success("ok", [], "t")
    assert env["next_action"] is None


def test_success_next_action_set():
    env = success("ok", [], "t", next_action={"type": "redirect"})
    assert env["next_action"] == {"type": "redirect"}


def test_success_events_passed_through():
    events = [{"id": "e1"}, {"id": "e2"}]
    env = success("ok", events, "t")
    assert env["events"] == events


# ── error() ───────────────────────────────────────────────────────────────────

def test_error_status():
    env = error("something broke", [], "trace-1")
    assert env["status"] == "ERROR"


def test_error_message_in_data():
    env = error("boom", [], "t")
    assert env["data"]["message"] == "boom"
    assert env["result"]["message"] == "boom"


def test_error_next_action_always_none():
    env = error("fail", [], "t")
    assert env["next_action"] is None


def test_error_trace_id_coerced_to_str():
    env = error("fail", None, 999)
    assert env["trace_id"] == "999"


# ── unified() ─────────────────────────────────────────────────────────────────

def test_unified_shape():
    env = unified(
        eu_id="eu-1",
        trace_id="trace-1",
        status="success",
        output={"result": 42},
        error=None,
    )
    assert env["eu_id"] == "eu-1"
    assert env["trace_id"] == "trace-1"
    assert env["status"] == "success"
    assert env["output"] == {"result": 42}
    assert env["error"] is None
    assert env["duration_ms"] is None
    assert env["attempt_count"] is None


def test_unified_trace_id_none_stays_none():
    env = unified(eu_id=None, trace_id=None, status="error", output=None, error="fail")
    assert env["trace_id"] is None


def test_unified_trace_id_coerced():
    env = unified(eu_id=None, trace_id="abc", status="s", output=None, error=None)
    assert env["trace_id"] == "abc"


def test_unified_duration_and_attempts():
    env = unified(
        eu_id="e",
        trace_id="t",
        status="success",
        output=None,
        error=None,
        duration_ms=150,
        attempt_count=2,
    )
    assert env["duration_ms"] == 150
    assert env["attempt_count"] == 2
