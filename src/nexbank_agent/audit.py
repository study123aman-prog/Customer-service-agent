"""
audit.py — minimal, mask-at-source audit trail for the demo.

Mirrors docs/architecture/audit-logging.md: every turn produces one structured
event, and any sensitive value is redacted *before* it is written (mask-at-source),
so the log itself can never leak a card number, CVV, or OTP. In the demo we keep
events in memory and can optionally append them to a JSONL file.
"""

import json
import time
from .masking import redact_pii


class AuditLog:
    """Collects one event per turn. Deterministic apart from the timestamp."""

    def __init__(self):
        self.events = []

    def record(self, session_id, turn, user_message, decision):
        """Build and store a redacted event describing how a turn was handled."""
        event = {
            "ts": round(time.time(), 3),
            "session_id": session_id,
            "turn": turn,
            # mask-at-source: the raw message is redacted before it is ever stored
            "user_message_redacted": redact_pii(user_message),
            "intent": decision.get("intent"),
            "auth_level": decision.get("auth_level"),
            "blocked": decision.get("blocked"),
            "escalation": decision.get("escalation"),
            "masked": decision.get("masked"),
            "flags": list(decision.get("flags", [])),
            "template": decision.get("template"),
        }
        self.events.append(event)
        return event

    def as_jsonl(self):
        """Return the whole log as newline-delimited JSON (one event per line)."""
        return "\n".join(json.dumps(e, ensure_ascii=False) for e in self.events)
