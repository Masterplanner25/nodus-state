from __future__ import annotations

from types import SimpleNamespace

from nodus_state import (
    build_execution_record,
    record_from_agent_run,
    record_from_flow_run,
    record_from_job_log,
)


# ── build_execution_record ────────────────────────────────────────────────────

def test_build_execution_record_minimal():
    rec = build_execution_record(run_id="r1")
    assert rec["run_id"] == "r1"
    assert rec["trace_id"] == "r1"        # defaults to run_id
    assert rec["execution_unit_id"] == "r1"  # defaults to run_id
    assert rec["status"] is None


def test_build_execution_record_trace_id_explicit():
    rec = build_execution_record(run_id="r1", trace_id="t1")
    assert rec["trace_id"] == "t1"


def test_build_execution_record_execution_unit_enrichment():
    unit = {"id": "eu-99", "correlation_id": "corr-1", "extra": {"workflow_type": "flow"}}
    rec = build_execution_record(run_id="r1", execution_unit=unit)
    assert rec["execution_unit_id"] == "eu-99"
    assert rec["correlation_id"] == "corr-1"
    assert rec["workflow_type"] == "flow"


def test_build_execution_record_all_fields():
    rec = build_execution_record(
        run_id="r1",
        trace_id="t1",
        execution_unit_id="eu-1",
        parent_run_id="parent-r",
        workflow_type="agent_execution",
        status="completed",
        error=None,
        actor="agent",
        source="agent",
        result_summary={"steps": 5},
        correlation_id="corr-abc",
    )
    assert rec["workflow_type"] == "agent_execution"
    assert rec["actor"] == "agent"
    assert rec["result_summary"] == {"steps": 5}
    assert rec["correlation_id"] == "corr-abc"


# ── record_from_flow_run ──────────────────────────────────────────────────────

def _flow_run(**kwargs):
    defaults = dict(
        id="flow-1",
        trace_id="trace-flow",
        workflow_type="my_flow",
        status="completed",
        error_message=None,
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_record_from_flow_run_basic():
    rec = record_from_flow_run(_flow_run())
    assert rec["run_id"] == "flow-1"
    assert rec["trace_id"] == "trace-flow"
    assert rec["actor"] == "flow"
    assert rec["workflow_type"] == "my_flow"
    assert rec["status"] == "completed"


def test_record_from_flow_run_status_override():
    rec = record_from_flow_run(_flow_run(status="running"), status="failed")
    assert rec["status"] == "failed"


def test_record_from_flow_run_with_execution_unit():
    rec = record_from_flow_run(_flow_run(), execution_unit={"id": "eu-5"})
    assert rec["execution_unit"]["id"] == "eu-5"


# ── record_from_agent_run ─────────────────────────────────────────────────────

def _agent_run(**kwargs):
    defaults = dict(
        id="agent-1",
        trace_id="trace-agent",
        flow_run_id="flow-9",
        replayed_from_run_id=None,
        status="completed",
        error_message=None,
        result={"answer": 42},
        correlation_id="corr-agent",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_record_from_agent_run_basic():
    rec = record_from_agent_run(_agent_run())
    assert rec["run_id"] == "agent-1"
    assert rec["trace_id"] == "trace-agent"
    assert rec["execution_unit_id"] == "flow-9"  # uses flow_run_id
    assert rec["actor"] == "agent"
    assert rec["workflow_type"] == "agent_execution"
    assert rec["result_summary"] == {"answer": 42}
    assert rec["correlation_id"] == "corr-agent"


def test_record_from_agent_run_no_flow_run_id():
    run = _agent_run(flow_run_id=None)
    rec = record_from_agent_run(run)
    assert rec["execution_unit_id"] == "agent-1"  # falls back to id


def test_record_from_agent_run_result_summary_override():
    rec = record_from_agent_run(_agent_run(), result_summary={"custom": True})
    assert rec["result_summary"] == {"custom": True}


# ── record_from_job_log ───────────────────────────────────────────────────────

def _job_log(**kwargs):
    defaults = dict(
        id="job-1",
        trace_id="trace-job",
        status="completed",
        error_message=None,
        result=None,
        source="scheduler",
    )
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_record_from_job_log_basic():
    rec = record_from_job_log(_job_log())
    assert rec["run_id"] == "job-1"
    assert rec["trace_id"] == "trace-job"
    assert rec["actor"] == "async"
    assert rec["source"] == "scheduler"


def test_record_from_job_log_actor_override():
    rec = record_from_job_log(_job_log(), actor="cron")
    assert rec["actor"] == "cron"


def test_record_from_job_log_execution_unit_passthrough():
    rec = record_from_job_log(_job_log(), execution_unit={"id": "eu-j1"})
    assert rec["execution_unit"]["id"] == "eu-j1"
