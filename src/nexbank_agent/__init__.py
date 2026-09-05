"""
nexbank_agent — offline reference demo for the NEXA agentic customer-service design.

This package is a SMALL, DETERMINISTIC, STANDARD-LIBRARY-ONLY illustration of the
architecture described in ../../docs. It is a teaching/《viva》reference, NOT a
production system: there are no real models, no network calls, and no real
customer data. Every "AI" step (intent classification, retrieval, sentiment) is a
transparent rule-based stand-in behind an interface that a real model could
replace without changing the safety design.

The one thing this demo takes completely seriously is the SAFETY LAYER: the
ordered guardrail checks in engine.evaluate() mirror the immutable rules in the
design docs, and the test suite in ../../tests exercises all of them.

Public API:
    from nexbank_agent import evaluate, Session
    d = evaluate("what's my balance?", auth_level="otp_verified")
    print(d["response_text"], d["flags"])
"""

from .engine import evaluate, Session, Decision  # noqa: F401

__all__ = ["evaluate", "Session", "Decision"]
__version__ = "1.0"
