from __future__ import annotations

import pytest
from datetime import datetime, timezone

from nodus_state import WAIT_TYPE_EVENT, WAIT_TYPE_EXTERNAL, WAIT_TYPE_TIME, WaitCondition
from nodus_state.wait import _parse_utc_datetime


# ── Factories ─────────────────────────────────────────────────────────────────

def test_for_event():
    wc = WaitCondition.for_event("job.completed", correlation_id="run-1")
    assert wc.type == WAIT_TYPE_EVENT
    assert wc.event_name == "job.completed"
    assert wc.correlation_id == "run-1"
    assert wc.trigger_at is None


def test_for_time():
    dt = datetime(2030, 1, 1, 12, 0, tzinfo=timezone.utc)
    wc = WaitCondition.for_time(dt)
    assert wc.type == WAIT_TYPE_TIME
    assert wc.trigger_at == dt
    assert wc.event_name is None


def test_for_time_adds_utc_tzinfo_when_naive():
    naive = datetime(2030, 1, 1, 12, 0)
    wc = WaitCondition.for_time(naive)
    assert wc.trigger_at.tzinfo is not None


def test_for_external():
    wc = WaitCondition.for_external("webhook.received")
    assert wc.type == WAIT_TYPE_EXTERNAL
    assert wc.event_name == "webhook.received"


def test_invalid_type_raises():
    with pytest.raises(ValueError, match="WaitCondition.type"):
        WaitCondition(type="invalid")


# ── Properties ────────────────────────────────────────────────────────────────

def test_is_event_based_for_event():
    assert WaitCondition.for_event("x").is_event_based is True
    assert WaitCondition.for_event("x").is_time_based is False


def test_is_event_based_for_external():
    assert WaitCondition.for_external("x").is_event_based is True


def test_is_time_based_for_time():
    dt = datetime(2030, 1, 1, tzinfo=timezone.utc)
    assert WaitCondition.for_time(dt).is_time_based is True
    assert WaitCondition.for_time(dt).is_event_based is False


def test_resume_event_for_event():
    wc = WaitCondition.for_event("x")
    assert wc.resume_event == "x"


def test_resume_event_is_none_for_time():
    dt = datetime(2030, 1, 1, tzinfo=timezone.utc)
    assert WaitCondition.for_time(dt).resume_event is None


# ── Serialisation round-trip ──────────────────────────────────────────────────

def test_to_dict_and_from_dict_event():
    wc = WaitCondition.for_event("op.done", correlation_id="c1")
    restored = WaitCondition.from_dict(wc.to_dict())
    assert restored == wc


def test_to_dict_and_from_dict_time():
    dt = datetime(2030, 6, 15, 10, 30, tzinfo=timezone.utc)
    wc = WaitCondition.for_time(dt)
    restored = WaitCondition.from_dict(wc.to_dict())
    assert restored.type == WAIT_TYPE_TIME
    assert restored.trigger_at == dt


def test_to_dict_and_from_dict_external():
    wc = WaitCondition.for_external("ext.event")
    restored = WaitCondition.from_dict(wc.to_dict())
    assert restored == wc


def test_from_dict_empty_returns_default():
    wc = WaitCondition.from_dict({})
    assert wc.type == WAIT_TYPE_EVENT


def test_to_dict_shape():
    wc = WaitCondition.for_event("test")
    d = wc.to_dict()
    assert set(d.keys()) == {"type", "trigger_at", "event_name", "correlation_id"}


# ── _parse_utc_datetime ───────────────────────────────────────────────────────

def test_parse_utc_datetime_none():
    assert _parse_utc_datetime(None) is None


def test_parse_utc_datetime_iso_string():
    result = _parse_utc_datetime("2030-01-01T12:00:00+00:00")
    assert result is not None
    assert result.tzinfo is not None


def test_parse_utc_datetime_z_suffix():
    result = _parse_utc_datetime("2030-01-01T12:00:00Z")
    assert result is not None


def test_parse_utc_datetime_invalid_returns_none():
    assert _parse_utc_datetime("not-a-date") is None


def test_parse_utc_datetime_naive_gets_utc():
    result = _parse_utc_datetime("2030-01-01T12:00:00")
    assert result is not None
    assert result.tzinfo is not None
