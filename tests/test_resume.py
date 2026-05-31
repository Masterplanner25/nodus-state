from __future__ import annotations

import pytest

from nodus_state import (
    RESUME_HANDLER_EU,
    ResumeSpec,
    build_callback_from_spec,
    register_resume_callback_builder,
    spec_from_json,
    spec_to_json,
)
from nodus_state.resume import _RESUME_CALLBACK_BUILDERS


# ── JSON round-trip ───────────────────────────────────────────────────────────

def test_spec_to_json_round_trip():
    spec = ResumeSpec(
        handler=RESUME_HANDLER_EU,
        eu_id="eu-123",
        tenant_id="tenant-456",
        run_id="run-789",
        eu_type="flow",
    )
    restored = spec_from_json(spec_to_json(spec))
    assert restored.handler == spec.handler
    assert restored.eu_id == spec.eu_id
    assert restored.tenant_id == spec.tenant_id
    assert restored.run_id == spec.run_id
    assert restored.eu_type == spec.eu_type


def test_spec_from_json_eu_type_none():
    spec = ResumeSpec(handler="h", eu_id="e", tenant_id="t", run_id="r")
    restored = spec_from_json(spec_to_json(spec))
    assert restored.eu_type is None


# ── Callback registry ─────────────────────────────────────────────────────────

def test_register_and_build_callback():
    calls = []

    def my_builder(spec: ResumeSpec):
        def _resume():
            calls.append(spec.eu_id)
        return _resume

    register_resume_callback_builder("test.resume", my_builder)

    spec = ResumeSpec(handler="test.resume", eu_id="eu-1", tenant_id="t1", run_id="r1")
    cb = build_callback_from_spec(spec)
    cb()
    assert "eu-1" in calls


def test_build_callback_unregistered_handler_raises():
    spec = ResumeSpec(
        handler="handler.does.not.exist",
        eu_id="eu-1",
        tenant_id="t1",
        run_id="r1",
    )
    with pytest.raises(KeyError, match="handler.does.not.exist"):
        build_callback_from_spec(spec)


def test_builder_receives_full_spec():
    received = {}

    def capture_builder(spec: ResumeSpec):
        received["spec"] = spec
        return lambda: None

    register_resume_callback_builder("test.capture", capture_builder)
    spec = ResumeSpec(
        handler="test.capture",
        eu_id="eu-42",
        tenant_id="t-99",
        run_id="run-7",
        eu_type="agent",
    )
    build_callback_from_spec(spec)
    assert received["spec"] is spec


def test_register_overwrites_existing():
    calls = []

    def builder_v1(spec):
        return lambda: calls.append("v1")

    def builder_v2(spec):
        return lambda: calls.append("v2")

    register_resume_callback_builder("test.overwrite", builder_v1)
    register_resume_callback_builder("test.overwrite", builder_v2)

    spec = ResumeSpec(handler="test.overwrite", eu_id="e", tenant_id="t", run_id="r")
    build_callback_from_spec(spec)()
    assert calls == ["v2"]
