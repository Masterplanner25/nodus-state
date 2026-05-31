# nodus-state

Execution state vocabulary for AI-native systems. A shared, typed language for describing what an execution is doing, what it's waiting for, how to resume it, and what it produced. Zero required dependencies — pure Python stdlib.

## Install

```bash
pip install nodus-state
```

## Modules

### Status constants

```python
from nodus_state import FlowStatus, UnitStatus, AgentStatus, UnitType, WaitType

assert FlowStatus.WAITING in FlowStatus.ALL
assert UnitStatus.COMPLETED in UnitStatus.TERMINAL
assert AgentStatus.PENDING_APPROVAL in AgentStatus.ACTIVE
```

### Wait conditions

```python
from nodus_state import WaitCondition

# Event-based wait
wc = WaitCondition.for_event("job.completed", correlation_id="run-1")
assert wc.is_event_based
assert wc.resume_event == "job.completed"

# Time-based wait
from datetime import datetime, timezone
wc = WaitCondition.for_time(datetime(2030, 1, 1, tzinfo=timezone.utc))
assert wc.is_time_based

# Round-trip through JSON/JSONB
wc2 = WaitCondition.from_dict(wc.to_dict())
assert wc2 == wc
```

### Resume specs

```python
from nodus_state import (
    ResumeSpec, spec_to_json, spec_from_json,
    register_resume_callback_builder, build_callback_from_spec,
    RESUME_HANDLER_EU,
)

# Register at startup
def my_eu_builder(spec: ResumeSpec):
    def _resume():
        with my_db() as db:
            my_service(db).resume(spec.eu_id)
    return _resume

register_resume_callback_builder(RESUME_HANDLER_EU, my_eu_builder)

# Persist and restore
spec = ResumeSpec(handler=RESUME_HANDLER_EU, eu_id="eu-1", tenant_id="t1", run_id="r1")
raw = spec_to_json(spec)                # persist to DB / Redis
callback = build_callback_from_spec(spec_from_json(raw))
callback()                              # execute the resume
```

### Envelopes

```python
from nodus_state import success, error, unified

# Legacy two-status shapes
env = success({"result": 42}, [], "trace-abc")
# → {"status": "SUCCESS", "data": {...}, "trace_id": "trace-abc", ...}

env = error("something broke", [], "trace-abc")
# → {"status": "ERROR", "data": {"message": "..."}, ...}

# Canonical unified shape (recommended for new code)
env = unified(eu_id="eu-1", trace_id="t1", status="success", output={"x": 1}, error=None)
```

### Execution context

```python
from nodus_state import ExecutionContext, ExecutionResult

ctx = ExecutionContext.new("flow.run", user_id="user-123")
# ... pipeline stages attach to ctx.metadata ...

result = ExecutionResult(success=True, data={"steps": 5}, eu_status="success")
response = result.to_response()
# → {"status": "success", "data": {...}, "trace_id": "...", "metadata": {...}}
```

### Execution records

```python
from nodus_state import build_execution_record, record_from_flow_run

# Pure function — pass any serialisable values
rec = build_execution_record(
    run_id="r1", trace_id="t1", workflow_type="my_flow",
    status="completed", actor="flow",
)

# Duck-typed adapter — works with ORM models or plain objects
rec = record_from_flow_run(flow_run_obj, status="completed")
```

## Extracted from

`AINDY/core/execution_envelope.py`, `AINDY/core/execution_pipeline/context.py`, `AINDY/core/wait_condition.py`, `AINDY/kernel/resume_spec.py`, and `AINDY/core/execution_record_service.py` in the A.I.N.D.Y. runtime.
