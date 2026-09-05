"""
engine.py — the decision engine (the runnable heart of the design).

`evaluate()` runs one user message through a FIXED, ORDERED pipeline and returns a
Decision. The order encodes the central design commitment from the docs:

    the immutable safety layer (C6) is checked BEFORE any capability,
    so nothing the learning system does can ever weaken a safety rule.

Priority order (highest first):
    0  denial-of-service (oversize / flood)
    1  data exfiltration            -> refuse, log
    2  prompt injection             -> neutralise, stay NEXA
    3  jailbreak / role-play        -> hold the line
    4  social engineering           -> refuse privileged access
    5  volunteered credential       -> refuse + warn
    6  fraud / crisis               -> hard escalation
    7  PII disclosure request       -> refuse, offer last-4 only
    8  money movement               -> refuse, guide to self-service
    9  cross-customer access        -> refuse
    10 regulated behaviours (AML, PEP, UPI reversal, loan verdict, grievance)
    11 financial advice             -> boundary, route to advisor
    12 intent classification        (only now do we look at "what do they want")
    13 authentication gate          -> step-up / re-auth if needed
    14 serve the answer             (facts come only from the KB)

Every branch returns the SAME Decision shape so callers (tests, CLI, audit) don't
care which branch fired.
"""

import hashlib

from . import nlu, knowledge, safety
from .config import rank
from .templates import render


# --- Decision shape ---------------------------------------------------------

def _decision(response_text, *, blocked=False, escalation=None, masked=False,
              flags=None, intent="GEN-000", auth_level="anonymous", template=None):
    """Assemble the dict every path returns. `flags` defaults to an empty list."""
    return {
        "response_text": response_text,
        "blocked": blocked,
        "escalation": escalation,
        "masked": masked,
        "flags": list(flags or []),
        "intent": intent,
        "auth_level": auth_level,
        "template": template,
    }


def _ref(seed):
    """Stable, non-sensitive case reference for escalations (e.g. REF-0A1B2C)."""
    h = hashlib.md5(seed.encode("utf-8")).hexdigest()[:6].upper()
    return f"REF-{h}"


# --- Authentication policy --------------------------------------------------

def _wants_profile_change(t):
    return ("change my" in t or "update my" in t) and \
           any(k in t for k in ["mobile", "number", "email", "address", "nominee"])


def _wants_limit_increase(t):
    return "increase" in t and "limit" in t


def _wants_card_block(t):
    return "block" in t and "card" in t


def _required_level(intent, t):
    """
    Minimum auth level an action requires. CRITICAL changes need full_kyc; account-
    specific reads need otp_verified; everything else can be served anonymously.
    """
    if _wants_profile_change(t) or _wants_limit_increase(t):
        return "full_kyc"
    if _wants_card_block(t) or intent in ("ACC-001", "TXN-001"):
        return "otp_verified"
    return "anonymous"


# --- Factual answers (numbers pulled ONLY from KB structured facts) ---------

def _emi(principal, annual_rate_pct, years):
    """Standard reducing-balance EMI. Pure math, easy to verify by hand."""
    r = annual_rate_pct / 1200.0            # monthly rate as a fraction
    n = int(years * 12)
    if r == 0:
        return principal / n
    factor = (1 + r) ** n
    return principal * r * factor / (factor - 1)


def _emi_answer(t):
    """Answer an EMI question factually (it's arithmetic, never 'you can afford')."""
    import re
    principal = 2000000.0
    m = re.search(r"(\d[\d,]*)\s*(lakh|lac|crore|cr)", t)
    if m:
        val = float(m.group(1).replace(",", ""))
        principal = val * (1e7 if m.group(2).startswith(("cr", "cro")) else 1e5)
    rate = 8.5
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", t)
    if m:
        rate = float(m.group(1))
    years = 20
    m = re.search(r"(\d+)\s*year", t)
    if m:
        years = int(m.group(1))
    emi = _emi(principal, rate, years)
    return (f"The EMI on a ₹{principal:,.0f} home loan at {rate}% for {years} years is "
            f"approximately ₹{emi:,.0f} per month. That's a straight arithmetic "
            f"figure — the exact amount depends on the sanctioned rate.")


def _info_answer(intent, t):
    """Serve a product/fact answer for a non-advice question, sourced from the KB."""
    if intent == "PRD-002":
        rate = knowledge.fact("KB-PRD-003", "rate_pct", 6.5)
        return render("T-FACT-RATE", product="Fixed Deposit", rate=f"{rate}%",
                      tenure="1-year deposit",
                      key_terms="interest at maturity; senior citizens earn +0.5%")
    if intent == "PRD-RD":
        rd_min = knowledge.fact("KB-PRD-004", "min_monthly", 500)
        body = (f"An FD (Fixed Deposit) takes a one-time lump sum for a fixed tenure "
                f"at a fixed rate. An RD (Recurring Deposit) takes a fixed amount every "
                f"month (from ₹{rd_min}/month) for your chosen tenure. Both earn fixed "
                f"interest — the difference is lump-sum versus monthly saving.")
        return render("T-FACT-GENERIC", fact_body=body)
    if intent == "PRD-TAX":
        limit = knowledge.fact("KB-PRD-016", "limit", 150000)
        body = (f"Yes — a 5-year tax-saver Fixed Deposit qualifies for a deduction "
                f"under Section 80C, up to ₹{limit:,} per financial year. Regular FDs "
                f"don't get this benefit, and the interest earned is taxable.")
        return render("T-FACT-GENERIC", fact_body=body)
    if intent == "PRD-MF":
        sip = knowledge.fact("KB-PRD-014", "sip_min", 100)
        body = (f"NexBank offers mutual funds through NexInvest — equity, debt, and "
                f"hybrid funds — and you can start a SIP from as little as ₹{sip} a "
                f"month. Which fund fits a particular goal is something our "
                f"SEBI-registered advisors can walk you through.")
        return render("T-FACT-GENERIC", fact_body=body)
    if intent == "PRD-LOAN":
        if "emi" in t:
            return render("T-FACT-GENERIC", fact_body=_emi_answer(t))
        rate = knowledge.fact("KB-PRD-009", "rate_from_pct", 8.25)
        body = (f"Our NexHome Loan starts from {rate}% p.a., with tenure up to 30 "
                f"years and financing up to 90% of property value. The applicable "
                f"rate is set by our lending team based on your profile.")
        return render("T-FACT-GENERIC", fact_body=body)
    if intent == "PRD-INS":
        body = ("Our NexProtect term insurance offers cover up to ₹1 crore; a medical "
                "check is required above ₹50 lakh cover. Full terms are in the policy "
                "document.")
        return render("T-FACT-GENERIC", fact_body=body)
    if intent == "CRD-001":
        body = ("Our NexCredit cards range from the Classic (up to 40 interest-free "
                "days, 2% cashback) to the Premium (50 interest-free days, 5x rewards). "
                "I can share the details of any card you're interested in.")
        return render("T-FACT-GENERIC", fact_body=body)
    # default
    return render("T-CLARIFY")


# --- The pipeline -----------------------------------------------------------

def evaluate(message, auth_level="anonymous", context=None):
    """Run one message through the fixed safety-first pipeline; return a Decision."""
    context = context or {}
    t = message.lower()

    # 0. Denial of service — handle before anything reads the content.
    if safety.is_oversized(message) or safety.is_flood(message):
        return _decision(render("T-CLARIFY"), flags=["dos_mitigated"],
                         auth_level=auth_level, template="T-CLARIFY")

    # 1. Data exfiltration (system prompt / training data / encode tricks).
    if safety.has_exfiltration(t):
        return _decision(render("T-EXFIL-REFUSE"), blocked=True,
                         flags=["exfiltration_blocked"], auth_level=auth_level,
                         template="T-EXFIL-REFUSE")

    # 2. Prompt injection — treat as data, stay NEXA.
    if safety.has_injection(t):
        return _decision(render("T-INJECTION-RECOVER"), blocked=True,
                         flags=["injection_detected"], auth_level=auth_level,
                         template="T-INJECTION-RECOVER")

    # 3. Jailbreak / role-play — the unsafe ask underneath still gets refused.
    if safety.has_jailbreak(t):
        tmpl = "T-ADVICE-BOUNDARY" if safety.mentions_advice_topic(t) \
            else "T-INJECTION-RECOVER"
        return _decision(render(tmpl), blocked=True, flags=["jailbreak_detected"],
                         auth_level=auth_level, template=tmpl)

    # 4. Social engineering — authority claims never unlock privileged access.
    if safety.has_social_engineering(t):
        return _decision(render("T-SE-REFUSE"), blocked=True,
                         flags=["social_engineering_detected"], auth_level=auth_level,
                         template="T-SE-REFUSE")

    # 5. Volunteered credential — never store/echo; warn the customer.
    if safety.volunteered_credential(t):
        return _decision(render("T-CRED-WARN"), blocked=True,
                         flags=["credential_refused"], auth_level=auth_level,
                         template="T-CRED-WARN")

    # 6. Fraud / crisis — hard escalations that outrank normal handling.
    if safety.is_fraud(t):
        return _decision(render("T-ESCALATE-FRAUD", ref_id=_ref(message)),
                         escalation="ESC-001", flags=["security_escalation"],
                         auth_level=auth_level, template="T-ESCALATE-FRAUD")
    if safety.is_crisis(t):
        return _decision(render("T-ESCALATE-CRISIS"), escalation="ESC-003",
                         flags=["crisis_support"], auth_level=auth_level,
                         template="T-ESCALATE-CRISIS")

    # 7. PII disclosure request — refuse; offer last-4 only.
    if safety.wants_pii_disclosure(t):
        return _decision(render("T-PII-REFUSE", last4="5678"), blocked=True,
                         flags=["pii_protected"], auth_level=auth_level,
                         template="T-PII-REFUSE")

    # 8. Money movement — NEXA guides, it never moves money itself.
    if safety.wants_money_move(t):
        tmpl = "T-MONEY-DISPUTE" if safety.is_dispute(t) else "T-MONEY-REFUSE"
        return _decision(render(tmpl), blocked=True, flags=["money_refused"],
                         auth_level=auth_level, template=tmpl)

    # 9. Cross-customer access — only ever the customer's own account.
    if safety.wants_cross_customer(t):
        return _decision(render("T-XCUST-REFUSE"), blocked=True,
                         flags=["cross_customer_refused"], auth_level=auth_level,
                         template="T-XCUST-REFUSE")

    # 10. Regulated behaviours.
    if safety.is_aml_structuring(t):
        return _decision(render("T-AML-REFUSE"), blocked=True, escalation="ESC-015",
                         flags=["aml_flag"], auth_level=auth_level,
                         template="T-AML-REFUSE")
    if safety.is_pep(t):
        return _decision(render("T-PEP-EDD"), escalation="ESC-015",
                         flags=["pep_flag"], auth_level=auth_level,
                         template="T-PEP-EDD")
    if safety.is_upi_deemed(t):
        return _decision(render("T-UPI-DEEMED"), flags=["upi_deemed"],
                         auth_level=auth_level, template="T-UPI-DEEMED")
    if safety.is_loan_decision(t):
        factors = "income, existing EMIs (FOIR), CIBIL score, employment, and collateral"
        return _decision(render("T-LOAN-NOAUTO", loan_factors=factors), blocked=True,
                         escalation="ESC-014", flags=["loan_no_auto"],
                         auth_level=auth_level, template="T-LOAN-NOAUTO")
    if safety.is_grievance(t):
        return _decision(render("T-GRIEVANCE"), escalation="ESC-010",
                         flags=["grievance_surfaced"], auth_level=auth_level,
                         template="T-GRIEVANCE")

    # 11. Financial advice — give facts + advisor, never a personal recommendation.
    if safety.is_advice(t):
        tmpl = "T-ADVICE-HOLD" if safety.is_advice_pressure(t, context) \
            else "T-ADVICE-BOUNDARY"
        return _decision(render(tmpl), blocked=True, escalation="ESC-013",
                         flags=["advice_blocked"], auth_level=auth_level,
                         template=tmpl)

    # 12. Safe zone: classify the actual intent.
    intent, _conf = nlu.classify(message)

    if intent == "GREETING":
        return _decision(render("T-GREETING"), intent=intent, auth_level=auth_level,
                         template="T-GREETING")

    # 13. Authentication gate for account-specific / high-risk actions.
    need = _required_level(intent, t)
    if rank(need) > rank("anonymous"):
        expired = bool(context.get("auth_expired"))
        if rank(auth_level) < rank(need) or expired:
            tmpl = "T-TIMEOUT-REAUTH" if expired else "T-AUTH-STEPUP"
            return _decision(render(tmpl), flags=["auth_required"], intent=intent,
                             auth_level=auth_level, template=tmpl)

    # 14. Serve the answer.
    if intent == "ACC-001":       # balance
        text = render("T-FACT-BALANCE", account_type="savings", acct_last4="5678",
                      balance="₹42,500")
        return _decision(text, masked=True, flags=["pii_masked"], intent=intent,
                         auth_level=auth_level, template="T-FACT-BALANCE")
    if intent == "TXN-001":       # recent transactions
        txns = "UPI to Kirana ₹450, Salary credit ₹80,000, Card at BigBazaar ₹1,299"
        text = render("T-FACT-TXN", acct_last4="5678", txn_list=txns)
        return _decision(text, masked=True, flags=["pii_masked"], intent=intent,
                         auth_level=auth_level, template="T-FACT-TXN")
    if intent in ("PRD-002", "PRD-RD", "PRD-TAX", "PRD-MF", "PRD-LOAN",
                  "PRD-INS", "CRD-001"):
        return _decision(_info_answer(intent, t), intent=intent,
                         auth_level=auth_level, template="T-FACT-GENERIC")
    if intent == "CMP-001":
        return _decision(render("T-GRIEVANCE"), escalation="ESC-010",
                         flags=["grievance_surfaced"], intent=intent,
                         auth_level=auth_level, template="T-GRIEVANCE")

    # 15. Nothing matched — clarify (bounded to max_clarifications in Session).
    return _decision(render("T-CLARIFY"), intent="GEN-000", auth_level=auth_level,
                     template="T-CLARIFY")


# --- Session wrapper (multi-turn convenience for the CLI & simulations) -----

class Session:
    """
    Holds conversation state across turns. The engine itself is stateless; the
    Session just remembers auth level and prior turns so features like advice-
    pressure detection and re-auth-on-timeout work in a live chat.
    """

    def __init__(self, auth_level="anonymous", session_id="demo"):
        self.auth_level = auth_level
        self.session_id = session_id
        self.turns = []          # list of prior user messages
        self.auth_expired = False

    def send(self, message):
        context = {"turns": list(self.turns), "auth_expired": self.auth_expired}
        decision = evaluate(message, auth_level=self.auth_level, context=context)
        self.turns.append(message)
        return decision


# Convenience alias so callers can treat a Decision as a documented type.
Decision = dict
