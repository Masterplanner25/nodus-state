"""Structured session identity for multi-channel AI systems.

Session keys encode which agent is handling which conversation, on which
channel, with which peer or thread.  Storing them as unformatted strings
leads to subtle bugs (field order, delimiter escaping, typos).  This module
provides a typed, round-trippable alternative.

Format::

    {agent_id}!{scope_type}:{scope_value}[!{subscope_type}:{subscope_value}]

Examples::

    SessionKey(agent_id="main")
        → "main!main"

    SessionKey(agent_id="main", channel="slack", peer="U12345")
        → "main!channel:slack!peer:U12345"

    SessionKey(agent_id="research", channel="discord", thread="T9876")
        → "research!channel:discord!thread:T9876"
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

# Delimiter between segments.
_SEP = "!"
# Delimiter within a segment between key and value.
_KV_SEP = ":"
# The scope token used when no channel is set.
_DEFAULT_SCOPE = "main"

# Characters allowed in any segment component — printable ASCII minus the
# two delimiters so that round-tripping is unambiguous.
_SAFE_RE = re.compile(r"^[^!:]+$")


def _require_safe(value: str, label: str) -> None:
    if not value:
        raise ValueError(f"SessionKey {label} must be a non-empty string")
    if not _SAFE_RE.match(value):
        raise ValueError(
            f"SessionKey {label} {value!r} must not contain '!' or ':'"
        )


@dataclass
class SessionKey:
    """Structured session identity for multi-channel AI systems.

    Fields
    ------
    agent_id : str
        Identifies the agent handling this session.  Required.
    channel : str or None
        Communication channel (e.g. ``"slack"``, ``"discord"``).  If set,
        at least one of *peer* or *thread* should also be provided.
    peer : str or None
        Peer/user identifier within the channel (e.g. ``"U12345"``).
        Mutually exclusive with *thread* — a session is either
        peer-scoped or thread-scoped, not both.
    thread : str or None
        Thread or room identifier within the channel (e.g. ``"T9876"``).

    String format::

        {agent_id}!{scope_type}:{scope_value}[!{subscope_type}:{subscope_value}]

    When no channel is set the canonical string is ``"{agent_id}!main"``.
    """

    agent_id: str
    channel: Optional[str] = None
    peer: Optional[str] = None
    thread: Optional[str] = None

    def __post_init__(self) -> None:
        _require_safe(self.agent_id, "agent_id")
        if self.channel is not None:
            _require_safe(self.channel, "channel")
        if self.peer is not None:
            _require_safe(self.peer, "peer")
        if self.thread is not None:
            _require_safe(self.thread, "thread")
        if self.peer is not None and self.thread is not None:
            raise ValueError(
                "SessionKey cannot have both 'peer' and 'thread' set at the same time"
            )

    # ── Serialisation ─────────────────────────────────────────────────────

    def to_string(self) -> str:
        """Serialise to canonical string form.

        Examples::

            SessionKey("main").to_string()
                → "main!main"
            SessionKey("main", channel="slack", peer="U12345").to_string()
                → "main!channel:slack!peer:U12345"
        """
        if self.channel is None:
            return f"{self.agent_id}{_SEP}{_DEFAULT_SCOPE}"

        parts = [self.agent_id, f"channel{_KV_SEP}{self.channel}"]
        if self.peer is not None:
            parts.append(f"peer{_KV_SEP}{self.peer}")
        elif self.thread is not None:
            parts.append(f"thread{_KV_SEP}{self.thread}")
        return _SEP.join(parts)

    @classmethod
    def from_string(cls, raw: str) -> "SessionKey":
        """Parse a canonical string into a :class:`SessionKey`.

        Raises
        ------
        ValueError
            If the string is empty, contains fewer than two segments, or
            any segment is malformed.
        """
        if not raw:
            raise ValueError("SessionKey string must not be empty")

        parts = raw.split(_SEP)
        if len(parts) < 2:
            raise ValueError(
                f"SessionKey string must contain at least two '!'-delimited segments: {raw!r}"
            )

        agent_id = parts[0]
        if not agent_id:
            raise ValueError(f"SessionKey agent_id segment is empty in {raw!r}")

        scope_segment = parts[1]

        # Default (no-channel) form: "{agent_id}!main"
        if scope_segment == _DEFAULT_SCOPE and len(parts) == 2:
            return cls(agent_id=agent_id)

        # Channel form: second segment is "channel:{value}"
        if _KV_SEP not in scope_segment:
            raise ValueError(
                f"Expected 'channel:<value>' or 'main' as second segment, "
                f"got {scope_segment!r} in {raw!r}"
            )

        scope_key, scope_value = scope_segment.split(_KV_SEP, 1)
        if scope_key != "channel":
            raise ValueError(
                f"Expected 'channel' as scope key, got {scope_key!r} in {raw!r}"
            )
        if not scope_value:
            raise ValueError(f"channel value is empty in {raw!r}")

        channel = scope_value
        peer: Optional[str] = None
        thread: Optional[str] = None

        if len(parts) > 2:
            subscope_segment = parts[2]
            if _KV_SEP not in subscope_segment:
                raise ValueError(
                    f"Expected 'peer:<value>' or 'thread:<value>' as third segment, "
                    f"got {subscope_segment!r} in {raw!r}"
                )
            sub_key, sub_value = subscope_segment.split(_KV_SEP, 1)
            if sub_key == "peer":
                if not sub_value:
                    raise ValueError(f"peer value is empty in {raw!r}")
                peer = sub_value
            elif sub_key == "thread":
                if not sub_value:
                    raise ValueError(f"thread value is empty in {raw!r}")
                thread = sub_value
            else:
                raise ValueError(
                    f"Expected 'peer' or 'thread' as subscope key, got {sub_key!r} in {raw!r}"
                )

        if len(parts) > 3:
            raise ValueError(
                f"SessionKey string has too many segments (max 3): {raw!r}"
            )

        return cls(agent_id=agent_id, channel=channel, peer=peer, thread=thread)

    # ── Factory ───────────────────────────────────────────────────────────

    @classmethod
    def default(cls, agent_id: str) -> "SessionKey":
        """Return the default (no-channel) session key for *agent_id*."""
        return cls(agent_id=agent_id)

    # ── Properties ────────────────────────────────────────────────────────

    @property
    def is_direct(self) -> bool:
        """True if this is a direct peer-to-peer session (has *peer* set)."""
        return self.peer is not None

    @property
    def is_threaded(self) -> bool:
        """True if this is a thread-scoped session (has *thread* set)."""
        return self.thread is not None

    @property
    def scope_label(self) -> str:
        """Human-readable scope string.

        Examples::

            SessionKey("main").scope_label              → "main"
            SessionKey("main","slack","U12345").scope_label  → "slack/U12345"
            SessionKey("r","discord",thread="T9876").scope_label → "discord/thread:T9876"
        """
        if self.channel is None:
            return _DEFAULT_SCOPE
        if self.peer is not None:
            return f"{self.channel}/{self.peer}"
        if self.thread is not None:
            return f"{self.channel}/thread{_KV_SEP}{self.thread}"
        return self.channel

    # ── Dunder ────────────────────────────────────────────────────────────

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        parts = [f"agent_id={self.agent_id!r}"]
        if self.channel is not None:
            parts.append(f"channel={self.channel!r}")
        if self.peer is not None:
            parts.append(f"peer={self.peer!r}")
        if self.thread is not None:
            parts.append(f"thread={self.thread!r}")
        return f"SessionKey({', '.join(parts)})"
