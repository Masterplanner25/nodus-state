"""nodus-state — execution state vocabulary for AI-native systems.

A shared, typed language for describing what an execution is doing, what it
is waiting for, how to resume it, and what it produced.  Zero required
dependencies — pure Python stdlib.

Status constants:
    FlowStatus, UnitStatus, AgentStatus, UnitType, WaitType, EnvelopeStatus

Wait conditions:
    WaitCondition          — structured wait descriptor with factories + serialisation
    WAIT_TYPE_EVENT / TIME / EXTERNAL — wait type constants

Resume specs:
    ResumeSpec             — serialisable resume descriptor
    spec_to_json           — serialise to JSON string
    spec_from_json         — deserialise from JSON string
    register_resume_callback_builder — register a resume handler factory
    build_callback_from_spec         — reconstruct and fire a resume callback
    RESUME_HANDLER_EU      — built-in handler key for EU resume

Envelopes:
    success(result, events, trace_id) -> dict
    error(message, events, trace_id)  -> dict
    unified(*, eu_id, trace_id, status, output, error, ...) -> dict

Execution context:
    ExecutionContext        — mutable pipeline context (request_id, route_name, metadata, …)
    ExecutionResult        — pipeline outcome (success, data, error, eu_status, …)

Execution records:
    build_execution_record(*, run_id, trace_id, …) -> dict
    record_from_flow_run(flow_run, …)  -> dict
    record_from_agent_run(agent_run, …) -> dict
    record_from_job_log(log, …)        -> dict

Session identity:
    SessionKey             — typed {agent}!{channel}:{scope} session key with round-trip
"""
from .context import ExecutionContext, ExecutionResult
from .sessions import SessionKey
from .envelopes import error, success, unified
from .records import (
    build_execution_record,
    record_from_agent_run,
    record_from_flow_run,
    record_from_job_log,
)
from .resume import (
    RESUME_HANDLER_EU,
    ResumeCallbackBuilder,
    ResumeSpec,
    build_callback_from_spec,
    register_resume_callback_builder,
    spec_from_json,
    spec_to_json,
)
from .statuses import (
    AgentStatus,
    EnvelopeStatus,
    FlowStatus,
    UnitStatus,
    UnitType,
    WaitType,
)
from .wait import (
    WAIT_TYPE_EVENT,
    WAIT_TYPE_EXTERNAL,
    WAIT_TYPE_TIME,
    WaitCondition,
    _parse_utc_datetime,
)

__all__ = [
    # Status constants
    "FlowStatus",
    "UnitStatus",
    "AgentStatus",
    "UnitType",
    "WaitType",
    "EnvelopeStatus",
    # Wait
    "WaitCondition",
    "WAIT_TYPE_EVENT",
    "WAIT_TYPE_TIME",
    "WAIT_TYPE_EXTERNAL",
    "_parse_utc_datetime",
    # Resume
    "ResumeSpec",
    "ResumeCallbackBuilder",
    "RESUME_HANDLER_EU",
    "spec_to_json",
    "spec_from_json",
    "register_resume_callback_builder",
    "build_callback_from_spec",
    # Envelopes
    "success",
    "error",
    "unified",
    # Context
    "ExecutionContext",
    "ExecutionResult",
    # Records
    "build_execution_record",
    "record_from_flow_run",
    "record_from_agent_run",
    "record_from_job_log",
    # Session identity
    "SessionKey",
]
