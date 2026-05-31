"""Execution result envelopes — standard dict shapes for all execution paths.

Three levels
------------
``success`` / ``error``
    Legacy two-status shape used by existing route handlers.
    Kept for backward compatibility — new code should use ``unified``.

``unified``
    Canonical ``ExecutionEnvelope`` shape used by the unification layer.
    Single stable contract that all execution paths should produce.
"""
from __future__ import annotations

from typing import Any


def success(
    result: Any,
    events: list[Any] | None,
    trace_id: str,
    *,
    next_action: Any = None,
) -> dict[str, Any]:
    """Build a SUCCESS execution envelope.

    Args:
        result:      The execution output (any serialisable value).
        events:      List of emitted event references (empty list if none).
        trace_id:    Request/execution trace ID.
        next_action: Optional hint to the caller about what to do next.
    """
    return {
        "status": "SUCCESS",
        "data": result,
        "result": result,
        "events": events or [],
        "next_action": next_action,
        "trace_id": str(trace_id),
    }


def error(
    message: str,
    events: list[Any] | None,
    trace_id: str,
) -> dict[str, Any]:
    """Build an ERROR execution envelope.

    Args:
        message:  Human-readable error description.
        events:   List of emitted event references (empty list if none).
        trace_id: Request/execution trace ID.
    """
    payload = {"message": message}
    return {
        "status": "ERROR",
        "data": payload,
        "result": payload,
        "events": events or [],
        "next_action": None,
        "trace_id": str(trace_id),
    }


def unified(
    *,
    eu_id: str | None,
    trace_id: str | None,
    status: str,
    output: Any,
    error: str | None,
    duration_ms: Any = None,
    attempt_count: Any = None,
) -> dict[str, Any]:
    """Build a canonical unified ExecutionEnvelope.

    This is the single stable shape that all execution paths should produce.
    The ``success()`` / ``error()`` helpers are preserved for backward
    compatibility with existing route handlers.

    Args:
        eu_id:         Execution unit ID.
        trace_id:      Request/execution trace ID.
        status:        Status string (``"success"``, ``"error"``, ``"waiting"``, etc.).
        output:        Execution output (any serialisable value).
        error:         Error message when status is ``"error"``, else None.
        duration_ms:   Elapsed wall-clock time in milliseconds.
        attempt_count: Number of execution attempts made.
    """
    return {
        "eu_id": eu_id,
        "trace_id": str(trace_id) if trace_id else None,
        "status": status,
        "output": output,
        "error": error,
        "duration_ms": duration_ms,
        "attempt_count": attempt_count,
    }
