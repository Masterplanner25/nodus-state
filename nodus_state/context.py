"""ExecutionContext and ExecutionResult dataclasses.

Framework-agnostic execution state objects for tracking the lifecycle of a
single execution request — from intake through completion.
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ExecutionContext:
    """Lightweight mutable context carried through an execution pipeline.

    Attributes
    ----------
    request_id:
        Unique ID for this request (UUID or X-Trace-ID from headers).
    route_name:
        Logical name of the execution route (e.g. ``"flow.run"``).
    user_id:
        Authenticated user / tenant ID.
    input_payload:
        Deserialized request input (method, path, params, etc.).
    metadata:
        Mutable bag for pipeline stages to attach derived values
        (eu_id, trace_id, event refs, wait conditions, etc.).
    pipeline_active:
        True while this context is inside an active execution pipeline.
    """

    request_id: str
    route_name: str
    user_id: str | None = None
    input_payload: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)
    pipeline_active: bool = True

    @classmethod
    def new(cls, route_name: str, *, user_id: str | None = None) -> "ExecutionContext":
        """Create a fresh ExecutionContext with a generated request_id."""
        return cls(
            request_id=str(uuid.uuid4()),
            route_name=route_name,
            user_id=user_id,
            input_payload={},
            metadata={},
        )


@dataclass(slots=True)
class ExecutionResult:
    """Outcome of one execution pipeline pass.

    Attributes
    ----------
    success:
        True if the execution completed without error.
    data:
        The execution output (any value).
    error:
        Error message when ``success`` is False.
    memory_context_count:
        Number of memory nodes recalled as context for this execution.
    metadata:
        Execution metadata (trace_id, eu_id, event refs, wait info, etc.).
    eu_status:
        The execution unit status at completion
        (``"success"``, ``"error"``, ``"waiting"``, etc.).
    """

    success: bool
    data: Any = None
    error: str | None = None
    memory_context_count: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)
    eu_status: str | None = None

    def to_response(self) -> dict[str, Any]:
        """Serialise to the canonical HTTP response dict.

        Returns a plain dict — no framework-specific encoding applied.
        The caller is responsible for JSON serialisation.
        """
        trace_id = str(self.metadata.get("trace_id") or "")
        eu_id = self.metadata.get("eu_id")
        status_label = self.eu_status or ("success" if self.success else "error")
        canonical_metadata: dict[str, Any] = {
            "events": list(self.metadata.get("event_refs") or []),
            "next_action": self.metadata.get("next_action"),
        }
        side_effects = self.metadata.get("side_effects")
        if side_effects:
            canonical_metadata["side_effects"] = side_effects
            canonical_metadata["degraded_side_effects"] = [
                name
                for name, detail in side_effects.items()
                if isinstance(detail, dict) and detail.get("status") in {"failed", "missing"}
            ]
        if self.eu_status == "waiting":
            canonical_metadata["eu_wait_for"] = self.metadata.get("eu_wait_for")
        if not self.success:
            canonical_metadata["error"] = (
                self.metadata.get("detail") or self.error or "Execution failed"
            )
            status_code = self.metadata.get("status_code")
            if status_code is not None:
                canonical_metadata["status_code"] = status_code
        return {
            "status": status_label,
            "data": self.data,
            "trace_id": trace_id,
            "eu_id": eu_id,
            "memory_context_count": self.memory_context_count,
            "metadata": canonical_metadata,
        }
