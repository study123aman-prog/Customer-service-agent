"""
safety.py — the detection helpers that power the immutable safety layer (C6).

DESIGN NOTE (important for the viva):
  Detection here is deliberately simple and transparent — lexicon lookups plus a
  few narrow regexes. In production these signals would come from an ML classifier,
  but the *decision* to block is always taken by fixed code (see engine.py), never
  by a model. Keeping detection readable is the whole point: every block in the test
  suite can be traced to one function below.

  Each function answers ONE yes/no question about the user's message. engine.py calls
  them in a fixed priority order. None of them ever return account data.
"""

import re
from .config import safety_cfg

# --- Lexicons ---------------------------------------------------------------
# Loaded from config/agent_config.json so the wording is auditable in one place.
# The second argument to safety_cfg() is a safe fallback if the file is missing.

ADVICE_LEX      = safety_cfg("advice_lexicon", ["should i", "recommend", "best for me"])
PERSONAL_LEX    = safety_cfg("personal_signal_lexicon", ["my salary", "for me"])
INJECTION_LEX   = safety_cfg("injection_lexicon", ["ignore all previous", "you are now"])
JAILBREAK_LEX   = safety_cfg("jailbreak_lexicon", ["you are dan", "hypothetically"])
EXFIL_LEX       = safety_cfg("exfil_lexicon", ["system prompt", "your instructions"])
SOCIAL_LEX      = safety_cfg("social_eng_lexicon", ["internal audit", "police officer"])
MONEY_LEX       = safety_cfg("money_move_lexicon", ["transfer", "pay my", "send money"])
XCUST_LEX       = safety_cfg("cross_customer_lexicon", ["my wife's", "power of attorney"])
AML_LEX         = safety_cfg("aml_structuring_lexicon", ["split", "avoid reporting"])
PEP_LEX         = safety_cfg("pep_lexicon", ["member of parliament", "sitting mp"])
MAX_INPUT_CHARS = safety_cfg("max_input_chars", 1200)

# Verbs that turn a "should I ..." question into a request for a personal decision.
ACTION_VERBS = ["buy", "sell", "invest", "put", "prepay", "choose", "pick",
                "take", "switch", "move", "open", "close", "go for", "get"]

# Words that clearly signal a real fraud/security emergency (hard escalation).
FRAUD_LEX = ["didn't authorise", "did not authorise", "didn't authorize",
             "did not authorize", "unauthorised", "unauthorized", "money is missing",
             "stolen", "someone else has access", "account takeover", "hacked",
             "fraud", "fraudulent", "i didn't make", "did not make these"]

# Self-harm / crisis words (kept narrow to avoid false positives).
CRISIS_LEX = ["suicide", "kill myself", "end my life", "self harm", "harm myself"]


def _any(text, lexicon):
    """True if any phrase in `lexicon` appears in the (already lower-cased) text."""
    return any(phrase in text for phrase in lexicon)


# --- 1. Denial of service ---------------------------------------------------

def is_oversized(message):
    """Input longer than the configured cap — truncate + throttle, never crash."""
    return len(message) > MAX_INPUT_CHARS


def is_flood(message):
    """Nonsense flood: long enough to matter but almost no letters/digits."""
    stripped = message.strip()
    if len(stripped) < 20:
        return False
    alnum = sum(c.isalnum() for c in stripped)
    return (alnum / len(stripped)) < 0.2


# --- 2. Prompt-injection / jailbreak / exfiltration -------------------------

def has_injection(t):
    return _any(t, INJECTION_LEX)


def has_jailbreak(t):
    return _any(t, JAILBREAK_LEX)


def has_exfiltration(t):
    return _any(t, EXFIL_LEX)


# --- 3. Social engineering (authority / impersonation claims) ---------------

def has_social_engineering(t):
    return _any(t, SOCIAL_LEX)


# --- 4. Volunteered credentials (value must actually be present) ------------

def volunteered_credential(t):
    """
    True only when the user has *supplied a secret value*, not merely mentioned one.
    That distinction matters: "what's my CVV?" is a PII request (handled elsewhere),
    while "my CVV is 123" is a volunteered credential we must refuse + warn about.
    """
    if "password is" in t or "netbanking password" in t or "password:" in t:
        return True
    if re.search(r"\bcvv\b[^0-9]{0,6}\d{3,4}", t):        # "cvv 123"
        return True
    if re.search(r"\botp\b[^0-9]{0,20}\d{4,8}", t):       # "otp ... is 884213"
        return True
    if re.search(r"\bpin\b[^0-9]{0,6}(is|:)?\s*\d{3,6}", t):  # "pin is 1234"
        return True
    if re.search(r"(?:\d[ \-]?){13,19}", t):              # a full card-length number
        return True
    return False


# --- 5. Fraud / crisis (hard escalations) -----------------------------------

def is_fraud(t):
    return _any(t, FRAUD_LEX)


def is_crisis(t):
    return _any(t, CRISIS_LEX)


# --- 6. PII disclosure requests ---------------------------------------------

def wants_pii_disclosure(t):
    """User is asking us to READ OUT a full sensitive value (card/Aadhaar/PIN/CVV)."""
    if _any(t, ["full card", "full account", "complete account", "full aadhaar",
                "full pan", "entire card", "whole card", "full debit card",
                "full credit card"]):
        return True
    if "read out" in t and ("card" in t or "number" in t):
        return True
    if "cvv" in t:                                        # asking about CVV
        return True
    if "pin" in t and _any(t, ["tell", "what is", "what it is", "forgot", "reveal",
                                "remind"]):
        return True
    if ("account number" in t or "card number" in t) and \
       _any(t, ["give me", "what is my", "tell me my", "my complete", "my full",
                "read", "share"]):
        return True
    return False


# --- 7. Money-movement requests ---------------------------------------------

def wants_money_move(t):
    # Word-boundary match so "prepay my home loan" (an advice question) is NOT
    # mistaken for the money phrase "pay my". Substring matching would misfire here.
    return any(re.search(r"\b" + re.escape(p) + r"\b", t) for p in MONEY_LEX)


def is_dispute(t):
    """A money request framed as reversing/disputing a charge (vs a fresh transfer)."""
    return _any(t, ["reverse", "dispute", "chargeback", "charge back", "refund"])


# --- 8. Cross-customer access requests --------------------------------------

def wants_cross_customer(t):
    return _any(t, XCUST_LEX)


# --- 9. Regulated behaviours ------------------------------------------------

def is_grievance(t):
    return _any(t, ["complaint", "grievance", "ombudsman", "nodal",
                    "file a formal", "want to file", "escalate this"])


def is_loan_decision(t):
    """Asking for an approve/reject verdict on a loan (never fully automated)."""
    triggers = ["am i approved", "approved for", "approve me", "will i get the loan",
                "qualify for", "eligible for a loan", "loan approved", "reject my loan"]
    return _any(t, triggers)


def is_upi_deemed(t):
    return "upi" in t and _any(t, ["failed", "debited", "not credited",
                                    "didn't go through", "did not go through",
                                    "money was debited"])


def is_pep(t):
    return _any(t, PEP_LEX)


def is_aml_structuring(t):
    """Structuring = splitting deposits to dodge reporting thresholds."""
    if "avoid reporting" in t or "without reporting" in t or "avoid the report" in t:
        return True
    if "split" in t and _any(t, ["deposit", "smaller", "amounts", "cash"]):
        return True
    if "break up the deposit" in t:
        return True
    return False


# --- 10. Financial advice ---------------------------------------------------

def has_personal_signal(t):
    return _any(t, PERSONAL_LEX)


def is_advice(t):
    """
    A request for a PERSONAL recommendation, as opposed to a factual question.
      * Any explicit recommendation phrase ("recommend", "best for me", ...), OR
      * "should I/we ..." combined with an action verb or a personal signal.
    Factual questions ("what is the FD rate?", "difference between FD and RD?")
    deliberately fall through to normal answering.
    """
    if _any(t, ADVICE_LEX):
        # "should i"/"should we" are in the lexicon but are too broad on their own,
        # so require an action verb or personal detail to treat them as advice.
        if ("should i" in t or "should we" in t) and \
           not (_any(t, ACTION_VERBS) or has_personal_signal(t)):
            # e.g. "who should I call?" — not investment advice. Keep checking others.
            others = [p for p in ADVICE_LEX if p not in ("should i", "should we")]
            return _any(t, others)
        return True
    return False


def is_advice_pressure(t, context):
    """Customer pushing back after a boundary was already set (Case Study 3)."""
    pressed = _any(t, ["just tell me", "just say it", "come on", "you would pick",
                       "which one you", "give me a straight"])
    # Only treat as "pressure" if a PRIOR turn was itself an advice request,
    # not merely because the conversation has any history.
    prior_advice = any(is_advice(x.lower()) or mentions_advice_topic(x.lower())
                       for x in context.get("turns", []))
    return pressed or prior_advice


# --- Helpers used to shape safe responses -----------------------------------

def mentions_advice_topic(t):
    """Does the message reference an investment topic (used for jailbreak routing)?"""
    return _any(t, ["invest", "stock", "mutual fund", "shares", "portfolio",
                    "advice", "fd or", "gold", "crypto"])
