# Changelog

## [Unreleased]

## [0.1.0] - 2026-05-31

### Added
- `FlowStatus`, `UnitStatus`, `AgentStatus`, `UnitType`, `WaitType`, `EnvelopeStatus` status constants
- `WaitCondition` with `for_event()`, `for_time()`, `for_external()` factories and full JSON round-trip
- `ResumeSpec`, `spec_to_json`, `spec_from_json`, `register_resume_callback_builder`, `build_callback_from_spec`
- `success()`, `error()`, `unified()` envelope builders
- `ExecutionContext`, `ExecutionResult` pipeline context types
- `build_execution_record`, `record_from_flow_run`, `record_from_agent_run`, `record_from_job_log`
- `SessionKey` — typed `{agent}!{channel}:{scope}` session identifier with full string round-trip
- Zero required dependencies — pure Python stdlib
