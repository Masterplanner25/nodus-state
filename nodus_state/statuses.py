"""Execution state constants extracted from FlowRun, ExecutionUnit, and AgentRun models."""
from __future__ import annotations


class FlowStatus:
    """Status values for a FlowRun lifecycle."""

    RUNNING   = "running"
    WAITING   = "waiting"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED    = "failed"

    ALL: tuple[str, ...] = (RUNNING, WAITING, EXECUTING, COMPLETED, FAILED)
    TERMINAL: tuple[str, ...] = (COMPLETED, FAILED)
    ACTIVE: tuple[str, ...] = (RUNNING, WAITING, EXECUTING)


class UnitStatus:
    """Status values for an ExecutionUnit lifecycle.

    State machine::

        pending → executing → waiting → resumed → executing → completed
                                                           └→ failed
                  └→ completed
                  └→ failed
    """

    PENDING   = "pending"
    EXECUTING = "executing"
    WAITING   = "waiting"
    RESUMED   = "resumed"
    COMPLETED = "completed"
    FAILED    = "failed"

    ALL: tuple[str, ...] = (PENDING, EXECUTING, WAITING, RESUMED, COMPLETED, FAILED)
    TERMINAL: tuple[str, ...] = (COMPLETED, FAILED)
    ACTIVE: tuple[str, ...] = (PENDING, EXECUTING, WAITING, RESUMED)


class AgentStatus:
    """Status values for an AgentRun lifecycle."""

    PENDING_APPROVAL = "pending_approval"
    APPROVED         = "approved"
    EXECUTING        = "executing"
    COMPLETED        = "completed"
    FAILED           = "failed"

    ALL: tuple[str, ...] = (PENDING_APPROVAL, APPROVED, EXECUTING, COMPLETED, FAILED)
    TERMINAL: tuple[str, ...] = (COMPLETED, FAILED)
    ACTIVE: tuple[str, ...] = (PENDING_APPROVAL, APPROVED, EXECUTING)


class UnitType:
    """Execution unit type discriminators."""

    OPERATION = "operation"
    AGENT     = "agent"
    FLOW      = "flow"
    JOB       = "job"

    ALL: tuple[str, ...] = (OPERATION, AGENT, FLOW, JOB)


class WaitType:
    """Wait condition type discriminators (mirrors WaitCondition.type)."""

    EVENT    = "event"
    TIME     = "time"
    EXTERNAL = "external"

    ALL: tuple[str, ...] = (EVENT, TIME, EXTERNAL)


class EnvelopeStatus:
    """Status labels used in execution envelopes."""

    SUCCESS = "SUCCESS"
    ERROR   = "ERROR"
    WAITING = "WAITING"

    # Lowercase variants used in unified() and to_response()
    SUCCESS_LOWER = "success"
    ERROR_LOWER   = "error"
    WAITING_LOWER = "waiting"
