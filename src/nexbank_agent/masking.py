"""
masking.py — PII masking + input validators (the entities.md rules, in code).

Two jobs:
  1. VALIDATE identifiers the customer legitimately provides (PAN, IFSC, UPI, phone)
     and money amounts, using the exact patterns from docs/intent-taxonomy/entities.md.
  2. MASK any sensitive number down to last-4 (or fully redact CVV/PIN/OTP) so that
     no full sensitive value ever appears in a response, a log, or an audit trace.

All functions are pure and deterministic — easy to unit-test and to explain.
"""

import re

# --- Validators (used when the customer supplies an identifier) -------------

_PAN_RE = re.compile(r"^[A-Z]{5}[0-9]{4}[A-Z]$")
_IFSC_RE = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")
_UPI_RE = re.compile(r"^[a-zA-Z0-9.\-_]{2,}@[a-zA-Z]{2,}$")
_PHONE_RE = re.compile(r"^[6-9][0-9]{9}$")            # Indian 10-digit mobile


def luhn(number: str) -> bool:
    """Luhn checksum — validates a card number's structure (not that it's real)."""
    digits = [int(c) for c in re.sub(r"\D", "", number)]
    if len(digits) < 13:
        return False
    checksum, parity = 0, len(digits) % 2
    for i, d in enumerate(digits):
        if i % 2 == parity:
            d *= 2
            if d > 9:
                d -= 9
        checksum += d
    return checksum % 10 == 0


def pan_valid(pan: str) -> bool:
    return bool(_PAN_RE.match(pan.strip().upper()))


def ifsc_valid(ifsc: str) -> bool:
    return bool(_IFSC_RE.match(ifsc.strip().upper()))


def upi_valid(vpa: str) -> bool:
    return bool(_UPI_RE.match(vpa.strip()))


def phone_valid(phone: str) -> bool:
    return bool(_PHONE_RE.match(re.sub(r"\D", "", phone)))


def amount_parse(text: str):
    """Extract a rupee amount, understanding 'lakh'/'crore'. Returns float or None."""
    t = text.lower().replace(",", "")
    m = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lac|crore|cr|k)?", t)
    if not m:
        return None
    value = float(m.group(1))
    unit = m.group(2)
    if unit in ("lakh", "lac"):
        value *= 1e5
    elif unit in ("crore", "cr"):
        value *= 1e7
    elif unit == "k":
        value *= 1e3
    return value


# --- Masking ----------------------------------------------------------------

def last4(number: str) -> str:
    digits = re.sub(r"\D", "", number)
    return digits[-4:] if len(digits) >= 4 else "----"


def mask_card(number: str) -> str:
    return f"XXXX-XXXX-XXXX-{last4(number)}"


def mask_account(number: str) -> str:
    return f"XXXXXX{last4(number)}"


def redact_pii(text: str) -> str:
    """
    Make a string safe to log/echo:
      - long digit runs (>=6, i.e. cards/accounts/Aadhaar) -> keep last 4 only
      - anything that looks like a CVV/PIN/OTP value near those words -> [REDACTED]
    Deliberately conservative: it errs toward over-masking.
    """
    # Redact 3-8 digit values that follow a credential word.
    text = re.sub(r"(?i)\b(cvv|pin|otp|password|passcode)\b[^0-9]{0,6}\d{3,8}",
                  r"\1 [REDACTED]", text)
    # Reduce any long digit run to last-4.
    def _keep_last4(m):
        d = m.group(0)
        return "*" * (len(d) - 4) + d[-4:]
    text = re.sub(r"\d{6,}", _keep_last4, text)
    return text
