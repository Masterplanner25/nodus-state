"""Execution record builders — canonical dict shapes for recording execution history.

``build_execution_record`` is a pure function that constructs the standard dict
persisted to execution history / audit logs.

The ``record_from_*`` helpers are duck-typed adapters that extract fields from
any object with the right attribute names (ORM model, dataclass, plain dict).
Pass a pre-built ``execution_unit`` dict to include EU-level metadata.
"""
from __future__ import annotations

from typing import Any


def build_execution_record(
    *,
    run_id: str | None = None,
    trace_id: str | None = None,
    execution_unit_id: str | None = None,
    parent_run_id: str | None = None,
    workflow_type: str | None = None,
    status: str | None = None,
    error: str | None = None,
    actor: str | None = None,
    source: str | None = None,
    result_summary: Any = None,
    correlation_id: str | None = None,
    execution_unit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the canonical execution record dict.

    This is a pure function with no external dependencies.

    Args:
        run_id:             Primary run identifier (flow run ID, agent run ID, etc.).
        trace_id:           Distributed trace ID; defaults to ``run_id``.
        execution_unit_id:  ExecutionUnit ID; defaults to ``run_id``.
        parent_run_id:      Parent run ID for hierarchical execution chains.
        workflow_type:      Workflow category (``"agent_execution"``, ``"flow"``, etc.).
        status:             Final status string.
        error:              Error message when the run failed.
        actor:              Who executed (``"flow"``, ``"agent"``, ``"async"``, etc.).
        source:             Source system or subsystem.
        result_summary:     Serialisable summary of the execution output.
        correlation_id:     Correlation chain ID linking related runs.
        execution_unit:     Pre-built execution unit dict (optional enrichment).

    Returns:
        Canonical execution record dict.
    """
    unit = dict(execution_unit or {})
    return {
        "run_id": run_id,
        "trace_id": trace_id or run_id,
        "execution_unit_id": execution_unit_id or unit.get("id") or run_id,
        "parent_run_id": parent_run_id,
        "workflow_type": workflow_type or unit.get("extra", {}).get("workflow_type"),
        "status": status,
        "error": error,
        "actor": actor,
        "source": source,
        "correlation_id": correlation_id or unit.get("correlation_id"),
        "result_summary": result_summary,
        "execution_unit": unit or None,
    }


def record_from_flow_run(
    flow_run: Any,
    *,
    status: str | None = None,
    error: str | None = None,
    result_summary: Any = None,
    execution_unit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an execution record from a duck-typed flow run object.

    Args:
        flow_run:       Any object with ``id``, ``trace_id``, ``workflow_type``,
                        ``status``, ``error_message`` attributes.
        execution_unit: Optional pre-built EU dict.  Pass this to include
                        EU-level metadata in the record.
    """
    return build_execution_record(
        run_id=str(getattr(flow_run, "id", None) or ""),
        trace_id=getattr(flow_run, "trace_id", None),
        execution_unit_id=str(getattr(flow_run, "id", None) or ""),
        workflow_type=getattr(flow_run, "workflow_type", None),
        status=status or getattr(flow_run, "status", None),
        error=error or getattr(flow_run, "error_message", None),
        actor="flow",
        source="flow",
        result_summary=result_summary,
        execution_unit=execution_unit,
    )


def record_from_agent_run(
    agent_run: Any,
    *,
    result_summary: Any = None,
    execution_unit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an execution record from a duck-typed agent run object.

    Args:
        agent_run:      Any object with ``id``, ``trace_id``, ``flow_run_id``,
                        ``replayed_from_run_id``, ``status``, ``error_message``,
                        ``result``, ``correlation_id`` attributes.
        execution_unit: Optional pre-built EU dict.
    """
    return build_execution_record(
        run_id=str(getattr(agent_run, "id", None) or ""),
        trace_id=getattr(agent_run, "trace_id", None),
        execution_unit_id=str(
            getattr(agent_run, "flow_run_id", None)
            or getattr(agent_run, "id", None)
            or ""
        ),
        parent_run_id=str(getattr(agent_run, "replayed_from_run_id", None) or "") or None,
        workflow_type="agent_execution",
        status=getattr(agent_run, "status", None),
        error=getattr(agent_run, "error_message", None),
        actor="agent",
        source="agent",
        result_summary=(
            result_summary
            if result_summary is not None
            else getattr(agent_run, "result", None)
        ),
        correlation_id=getattr(agent_run, "correlation_id", None),
        execution_unit=execution_unit,
    )


def record_from_job_log(
    log: Any,
    *,
    workflow_type: str | None = None,
    actor: str = "async",
    source: str | None = None,
    result_summary: Any = None,
    execution_unit: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build an execution record from a duck-typed async job log object.

    Args:
        log:            Any object with ``id``, ``trace_id``, ``status``,
                        ``error_message``, ``result``, ``source`` attributes.
        execution_unit: Optional pre-built EU dict.
    """
    return build_execution_record(
        run_id=str(getattr(log, "id", None) or ""),
        trace_id=getattr(log, "trace_id", None) or str(getattr(log, "id", None) or ""),
        execution_unit_id=str(getattr(log, "id", None) or ""),
        workflow_type=workflow_type,
        status=getattr(log, "status", None),
        error=getattr(log, "error_message", None),
        actor=actor,
        source=source or getattr(log, "source", None),
        result_summary=(
            result_summary
            if result_summary is not None
            else getattr(log, "result", None)
        ),
        correlation_id=str(getattr(log, "id", None) or ""),
        execution_unit=execution_unit,
    )
