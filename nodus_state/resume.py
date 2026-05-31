"""ResumeSpec — serialisable descriptor for resuming a suspended execution unit.

Usage
-----
Register a builder once at startup::

    from nodus_state import register_resume_callback_builder, RESUME_HANDLER_EU

    def my_builder(spec: ResumeSpec) -> Callable[[], None]:
        def _resume():
            with my_db_session() as db:
                my_eu_service(db).resume(spec.eu_id)
        return _resume

    register_resume_callback_builder(RESUME_HANDLER_EU, my_builder)

Then reconstruct and fire callbacks from persisted specs::

    spec = spec_from_json(raw_json)
    callback = build_callback_from_spec(spec)
    callback()
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import Callable, Protocol


RESUME_HANDLER_EU = "execution_unit.resume"


class ResumeCallbackBuilder(Protocol):
    """Protocol for resume callback factories.

    A builder receives a ``ResumeSpec`` and returns a zero-argument callable
    that, when called, performs the actual resume operation (typically
    transitioning an ExecutionUnit from ``waiting`` to ``resumed``).
    """

    def __call__(self, spec: "ResumeSpec") -> Callable[[], None]:
        ...


@dataclass
class ResumeSpec:
    """Serialisable descriptor for resuming a suspended execution unit.

    Attributes
    ----------
    handler:
        Registered builder key (e.g. ``RESUME_HANDLER_EU``).
    eu_id:
        Execution unit ID to resume.
    tenant_id:
        Tenant/user ID for isolation checks.
    run_id:
        Flow run or agent run ID associated with the EU.
    eu_type:
        Optional type hint (``"flow"``, ``"agent"``, etc.) for routing.
    """

    handler: str
    eu_id: str
    tenant_id: str
    run_id: str
    eu_type: str | None = None


_RESUME_CALLBACK_BUILDERS: dict[str, ResumeCallbackBuilder] = {}


def spec_to_json(spec: ResumeSpec) -> str:
    """Serialise a ``ResumeSpec`` to a JSON string for persistence."""
    return json.dumps(asdict(spec))


def spec_from_json(raw: str) -> ResumeSpec:
    """Deserialise a ``ResumeSpec`` from a JSON string."""
    return ResumeSpec(**json.loads(raw))


def register_resume_callback_builder(handler: str, builder: ResumeCallbackBuilder) -> None:
    """Register a callback factory for a named resume handler.

    Call this once at application startup before any wait/resume operations.

    Args:
        handler: Handler key (e.g. ``RESUME_HANDLER_EU``).
        builder: Callable that accepts a ``ResumeSpec`` and returns a
            zero-argument callable that performs the resume.
    """
    _RESUME_CALLBACK_BUILDERS[handler] = builder


def build_callback_from_spec(spec: ResumeSpec) -> Callable[[], None]:
    """Reconstruct an executable resume callback from a persisted ``ResumeSpec``.

    Args:
        spec: The resume specification.

    Returns:
        A zero-argument callable that performs the resume operation.

    Raises:
        KeyError: If no builder has been registered for ``spec.handler``.
            Call ``register_resume_callback_builder`` at startup.
    """
    builder = _RESUME_CALLBACK_BUILDERS.get(spec.handler)
    if builder is None:
        raise KeyError(
            f"No resume callback builder registered for handler {spec.handler!r}. "
            f"Call register_resume_callback_builder({spec.handler!r}, ...) at startup. "
            f"Registered handlers: {sorted(_RESUME_CALLBACK_BUILDERS)}"
        )
    return builder(spec)
