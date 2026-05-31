"""Tests for SessionKey — structured session identity."""
from __future__ import annotations

import pytest
from nodus_state.sessions import SessionKey


# ── to_string ────────────────────────────────────────────────────────────────

class TestToString:
    def test_default_session_no_channel(self):
        assert SessionKey(agent_id="main").to_string() == "main!main"

    def test_channel_and_peer(self):
        k = SessionKey(agent_id="main", channel="slack", peer="U12345")
        assert k.to_string() == "main!channel:slack!peer:U12345"

    def test_channel_and_thread(self):
        k = SessionKey(agent_id="research", channel="discord", thread="T9876")
        assert k.to_string() == "research!channel:discord!thread:T9876"

    def test_channel_only(self):
        k = SessionKey(agent_id="bot", channel="web")
        assert k.to_string() == "bot!channel:web"

    def test_str_dunder_matches_to_string(self):
        k = SessionKey(agent_id="main", channel="slack", peer="U1")
        assert str(k) == k.to_string()

    def test_deterministic_output(self):
        k = SessionKey(agent_id="main", channel="slack", peer="U12345")
        assert k.to_string() == k.to_string()


# ── from_string ───────────────────────────────────────────────────────────────

class TestFromString:
    def test_default_scope(self):
        k = SessionKey.from_string("main!main")
        assert k.agent_id == "main"
        assert k.channel is None
        assert k.peer is None
        assert k.thread is None

    def test_channel_and_peer(self):
        k = SessionKey.from_string("main!channel:slack!peer:U12345")
        assert k.agent_id == "main"
        assert k.channel == "slack"
        assert k.peer == "U12345"
        assert k.thread is None

    def test_channel_and_thread(self):
        k = SessionKey.from_string("research!channel:discord!thread:T9876")
        assert k.agent_id == "research"
        assert k.channel == "discord"
        assert k.thread == "T9876"
        assert k.peer is None

    def test_channel_only(self):
        k = SessionKey.from_string("bot!channel:web")
        assert k.agent_id == "bot"
        assert k.channel == "web"
        assert k.peer is None
        assert k.thread is None

    def test_empty_string_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("")

    def test_single_segment_raises(self):
        with pytest.raises(ValueError, match="at least two"):
            SessionKey.from_string("justanagent")

    def test_missing_channel_prefix_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!slack!peer:U1")

    def test_unknown_scope_key_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!scope:whatever")

    def test_unknown_subscope_key_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!channel:slack!room:R1")

    def test_empty_channel_value_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!channel:!peer:U1")

    def test_empty_peer_value_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!channel:slack!peer:")

    def test_empty_thread_value_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!channel:slack!thread:")

    def test_too_many_segments_raises(self):
        with pytest.raises(ValueError):
            SessionKey.from_string("main!channel:slack!peer:U1!extra:x")


# ── Round-trip ────────────────────────────────────────────────────────────────

class TestRoundTrip:
    def _rt(self, key: SessionKey) -> SessionKey:
        return SessionKey.from_string(key.to_string())

    def test_default_session(self):
        k = SessionKey(agent_id="main")
        assert self._rt(k) == k

    def test_channel_and_peer(self):
        k = SessionKey(agent_id="main", channel="slack", peer="U12345")
        assert self._rt(k) == k

    def test_channel_and_thread(self):
        k = SessionKey(agent_id="research", channel="discord", thread="T9876")
        assert self._rt(k) == k

    def test_channel_only(self):
        k = SessionKey(agent_id="bot", channel="web")
        assert self._rt(k) == k

    def test_from_string_then_to_string(self):
        raw = "main!channel:slack!peer:U12345"
        assert SessionKey.from_string(raw).to_string() == raw


# ── Factory ───────────────────────────────────────────────────────────────────

class TestDefault:
    def test_default_returns_no_channel_key(self):
        k = SessionKey.default("myagent")
        assert k.agent_id == "myagent"
        assert k.channel is None
        assert k.peer is None
        assert k.thread is None

    def test_default_round_trips(self):
        k = SessionKey.default("bot")
        assert SessionKey.from_string(k.to_string()) == k


# ── Properties ────────────────────────────────────────────────────────────────

class TestIsDirect:
    def test_true_when_peer_set(self):
        assert SessionKey("a", "slack", peer="U1").is_direct is True

    def test_false_when_no_peer(self):
        assert SessionKey("a").is_direct is False
        assert SessionKey("a", "slack").is_direct is False
        assert SessionKey("a", "discord", thread="T1").is_direct is False


class TestIsThreaded:
    def test_true_when_thread_set(self):
        assert SessionKey("a", "discord", thread="T9").is_threaded is True

    def test_false_when_no_thread(self):
        assert SessionKey("a").is_threaded is False
        assert SessionKey("a", "slack").is_threaded is False
        assert SessionKey("a", "slack", peer="U1").is_threaded is False


class TestScopeLabel:
    def test_default_scope_label(self):
        assert SessionKey("main").scope_label == "main"

    def test_channel_and_peer(self):
        assert SessionKey("main", "slack", "U12345").scope_label == "slack/U12345"

    def test_channel_and_thread(self):
        assert SessionKey("r", "discord", thread="T9876").scope_label == "discord/thread:T9876"

    def test_channel_only(self):
        assert SessionKey("bot", "web").scope_label == "web"


# ── Validation ────────────────────────────────────────────────────────────────

class TestValidation:
    def test_empty_agent_id_raises(self):
        with pytest.raises(ValueError):
            SessionKey(agent_id="")

    def test_agent_id_with_bang_raises(self):
        with pytest.raises(ValueError):
            SessionKey(agent_id="bad!id")

    def test_agent_id_with_colon_raises(self):
        with pytest.raises(ValueError):
            SessionKey(agent_id="bad:id")

    def test_channel_with_delimiter_raises(self):
        with pytest.raises(ValueError):
            SessionKey(agent_id="a", channel="sl!ck")

    def test_peer_and_thread_together_raises(self):
        with pytest.raises(ValueError, match="both"):
            SessionKey(agent_id="a", channel="slack", peer="U1", thread="T1")


# ── Equality (dataclass) ──────────────────────────────────────────────────────

class TestEquality:
    def test_same_fields_equal(self):
        a = SessionKey("main", "slack", "U1")
        b = SessionKey("main", "slack", "U1")
        assert a == b

    def test_different_agent_not_equal(self):
        assert SessionKey("a") != SessionKey("b")

    def test_different_channel_not_equal(self):
        assert SessionKey("a", "slack") != SessionKey("a", "discord")

    def test_different_peer_not_equal(self):
        assert SessionKey("a", "slack", "U1") != SessionKey("a", "slack", "U2")

    def test_none_vs_set_not_equal(self):
        assert SessionKey("a") != SessionKey("a", "slack")
