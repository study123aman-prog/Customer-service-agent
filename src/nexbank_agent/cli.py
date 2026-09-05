#!/usr/bin/env python3
"""
cli.py — a tiny interactive console for the NEXA demo.

Run it to chat with the reference engine at a terminal:

    python3 -m nexbank_agent.cli
    python3 -m nexbank_agent.cli --auth otp_verified

Every reply prints the response plus the safety metadata (flags, blocked,
escalation) so you can SEE which guardrail fired — useful in a viva/demo.
Type 'quit' to exit, or 'audit' to dump the redacted audit log.
"""

import argparse

from .engine import Session
from .audit import AuditLog


def _format(decision):
    """One-line metadata summary shown under each reply."""
    bits = []
    if decision["blocked"]:
        bits.append("BLOCKED")
    if decision["escalation"]:
        bits.append(f"escalation={decision['escalation']}")
    if decision["masked"]:
        bits.append("masked")
    if decision["flags"]:
        bits.append("flags=" + ",".join(decision["flags"]))
    bits.append(f"intent={decision['intent']}")
    return "   [" + " | ".join(bits) + "]"


def main():
    parser = argparse.ArgumentParser(description="Chat with the NEXA demo engine.")
    parser.add_argument("--auth", default="anonymous",
                        help="starting auth level (anonymous / otp_verified / "
                             "biometric_verified / full_kyc)")
    args = parser.parse_args()

    session = Session(auth_level=args.auth)
    audit = AuditLog()
    turn = 0

    print("NEXA demo — type your message ('quit' to exit, 'audit' to see the log).")
    print(f"(auth level: {session.auth_level})\n")
    print("NEXA> Hi, I'm NEXA, your NexBank assistant. How can I help you today?")

    while True:
        try:
            message = input("\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not message:
            continue
        if message.lower() in ("quit", "exit"):
            break
        if message.lower() == "audit":
            print(audit.as_jsonl() or "   (no events yet)")
            continue

        turn += 1
        decision = session.send(message)
        audit.record(session.session_id, turn, message, decision)
        print(f"\nNEXA> {decision['response_text']}")
        print(_format(decision))


if __name__ == "__main__":
    main()
