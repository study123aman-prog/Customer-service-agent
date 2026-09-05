"""
nlu.py — Natural Language Understanding stand-in (intent + entities + sentiment).

This is a DETERMINISTIC keyword classifier standing in for the ML NLU pipeline in
docs/intent-taxonomy. It returns the same shape a real model would (intent code,
confidence, entities, sentiment) so engine.py doesn't care which is behind it.
Only the intents the demo actually needs are implemented; everything else returns
GEN-000 (out of scope / small talk) with low confidence, which drives a clarify.
"""

import re

# Ordered (intent, confidence, keyword-list). First rule whose keywords all/any
# match wins. Kept intentionally readable — each line is one intent's trigger.
_RULES = [
    ("GREETING",  0.98, ["hi", "hello", "hey", "namaste", "good morning", "good evening"]),
    ("ACC-001",   0.95, ["balance"]),                       # check balance
    ("TXN-001",   0.93, ["last 5", "recent transaction", "mini statement",
                          "last transactions", "transaction history", "transactions"]),
    ("PRD-002",   0.92, ["fd rate", "fixed deposit rate", "interest rate", "fd interest"]),
    ("PRD-RD",    0.90, ["difference between an fd", "fd and an rd", "fd and rd", "rd"]),
    ("PRD-LOAN",  0.90, ["emi", "home loan", "loan"]),
    ("PRD-TAX",   0.90, ["tax benefit", "80c", "tax saving", "save tax"]),
    ("PRD-MF",    0.90, ["mutual fund", "mutual funds", "sip"]),
    ("PRD-INS",   0.88, ["insurance", "term cover", "policy"]),
    ("CRD-001",   0.90, ["credit card", "debit card", "card limit", "block"]),
    ("CMP-001",   0.90, ["complaint", "grievance", "not resolved", "not fixed"]),
    ("PROFILE",   0.88, ["change my mobile", "change my number", "change my email",
                         "change my address", "update my"]),
]


def classify(message):
    """Return (intent_code, confidence). Deterministic; falls back to GEN-000."""
    t = message.lower()
    for intent, conf, kws in _RULES:
        if any(k in t for k in kws):
            return intent, conf
    return "GEN-000", 0.30


def extract_entities(message):
    """Pull the few entity types the demo uses. Only ever keeps last-4 of numbers."""
    ents = {}
    t = message
    # card / account last-4 (from an explicit "ending 1234" or a long run)
    m = re.search(r"(?:ending|ends)\s*(\d{4})", t, re.I)
    if m:
        ents["card_last4"] = m.group(1)
    # amounts like "5 lakh", "20 lakh", "10,000"
    m = re.search(r"(\d[\d,]*)\s*(lakh|lac|crore|cr|k)?", t, re.I)
    if m and any(c.isdigit() for c in m.group(0)):
        ents["amount_text"] = m.group(0).strip()
    return ents


# Small, transparent lexical sentiment. Negative words push the score down; used
# only to raise escalation_proximity, never to make a safety decision.
_NEG = ["angry", "furious", "terrible", "worst", "unacceptable", "frustrated",
        "missing", "stolen", "fraud", "cheated", "scam", "urgent", "not fixed",
        "third time", "still not", "ridiculous", "disgusted"]
_POS = ["thanks", "thank you", "great", "perfect", "awesome", "helpful", "good"]


def sentiment(message):
    """Return a float in [-1, 1]; negative = unhappy."""
    t = message.lower()
    score = 0
    for w in _NEG:
        if w in t:
            score -= 1
    for w in _POS:
        if w in t:
            score += 1
    if score == 0:
        return 0.0
    # squash to [-1, 1]
    return max(-1.0, min(1.0, score / 2.0))
