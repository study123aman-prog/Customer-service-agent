# Entity Model & Validation — NexBank NEXA

**Deliverable:** L2 (entity extraction specifications) · Parent: [`README.md`](README.md)

Entity types, extraction methods, validation rules, and sensitivity tags. Validation runs **before** a value enters a slot; sensitivity tags drive masking (C10) and logging redaction (C12). PII minimisation is enforced at this layer — several values are **rejected on sight**.

---

## 1. Entity catalogue

| Entity | Example | Extraction | Validation | Sensitivity | Masking rule |
|---|---|---|---|---|---|
| `account_ref` | SA-XXXX-XXXX-1234 | Regex + checksum | Format + Luhn-style check + backend verification | HIGH · PII | Show last 4 only |
| `account_type` | savings / current | Enum match | ∈ product catalogue | LOW | none |
| `transaction_id` | TXN9F2A… | Regex | Length/charset + backend lookup | MEDIUM | none |
| `transaction_amount` | ₹1,500.00 | Currency parser | Currency detect + range/sanity check | MEDIUM | none |
| `card_ref` (partial) | last 4: 5678 | Regex (last 4) | Exactly 4 digits; **never full PAN of card** | CRITICAL · PCI | Always `XXXX-XXXX-XXXX-5678` |
| `card_number` (full) | 16 digits | — | **REJECTED** — never accepted/stored | CRITICAL · PCI | n/a (blocked) |
| `cvv` / `pin` / `password` | — | — | **REJECTED** — instruct customer never to share | CRITICAL | n/a (blocked) |
| `aadhaar_partial` | last 4 only | Regex (last 4) | Exactly 4 digits; **full Aadhaar rejected** | CRITICAL · KYC | last 4 only |
| `pan` | ABCDE1234F | Regex `^[A-Z]{5}[0-9]{4}[A-Z]$` | Format + NSDL verification | CRITICAL · KYC | `ABCDEXXXXF` |
| `upi_id` | user@bank | Regex `^[\w.\-]{2,}@[a-z]{2,}$` | Format + handle resolution | MEDIUM | mask local part |
| `phone_number` | +91 98765 43210 | Regex + libphonenumber | E.164 + country code | HIGH · PII | last 4 (`…3210`) |
| `ifsc` | HDFC0001234 | Regex `^[A-Z]{4}0[A-Z0-9]{6}$` | Checksum + directory | LOW | none |
| `neft_rtgs_ref` (UTR) | 16-char UTR | Regex | 16 alphanumeric + lookup | MEDIUM | none |
| `merchant_name` | Amazon, Swiggy | Fuzzy match | Fuzzy match vs merchant DB (≥0.8) | LOW | none |
| `otp_token` | 482917 | Regex `^\d{6}$` | 6 digits; **ephemeral — never logged/stored** | CRITICAL | fully redacted in logs |
| `date` / `date_range` | 18th March / last 30 days | Date parser | Valid date; not future for past-txn context | LOW | none |
| `currency` | INR, USD | ISO-4217 match | ∈ ISO 4217 | LOW | none |
| `complaint_id` | CMP-2024-78901 | Regex `^CMP-\d{4}-\d{5}$` | Format + backend lookup | LOW | none |
| `nominee_name` | full name | NER (person) | Non-empty, name-like | HIGH · PII | mask in logs |
| `relationship` | spouse / child | Enum | ∈ allowed set | LOW | none |
| `proof_document` | Aadhaar / passport (type only) | Enum | Document *type* only; never the number | MEDIUM | none |
| `frequency` | monthly / weekly | Enum | ∈ {daily,weekly,monthly,quarterly} | LOW | none |
| `product_name` | NexFD, NexHome Loan | Fuzzy match | ∈ product catalogue | LOW | none |
| `loan_type` / `deposit_type` / `insurance_type` | home / FD / term | Enum | ∈ catalogue | LOW | none |

---

## 2. Hard-rejection rules (PII minimisation)

The following are **never accepted, stored, or echoed**, even if the customer volunteers them. On detection, NEXA stops, does not store the value, and educates the customer:

- Full card number (PAN), CVV/CVC, ATM PIN, internet/mobile-banking password.
- Full Aadhaar number (only last 4 permitted for reference).
- OTP is accepted transiently for verification only and is **redacted from every log** and never retained after the auth decision.

Example refusal copy: *"For your safety, please never share your full card number, CVV, PIN, or password with anyone — including NexBank staff or this assistant. I can help using just the last 4 digits."*

This satisfies Security Rules 1 and 5 (`../guardrails/account-security.md`) and PCI-DSS handling.

---

## 3. Validation utilities (referenced by the demo)

| Utility | Rule |
|---|---|
| `luhn(check_digits)` | Mod-10 checksum for card/account references (last-4 flows skip full-PAN validation entirely). |
| `pan_valid(s)` | `^[A-Z]{5}[0-9]{4}[A-Z]$` (5 letters, 4 digits, 1 letter). |
| `ifsc_valid(s)` | `^[A-Z]{4}0[A-Z0-9]{6}$` (5th char is always `0`). |
| `upi_valid(s)` | `^[\w.\-]{2,}@[a-z]{2,}$`; handle resolvable against PSP list. |
| `phone_valid(s)` | E.164; default region IN; must include country code for international. |
| `amount_parse(s)` | Detect currency symbol/word; strip separators; range check (e.g. UPI ≤ ₹1L per NPCI limits). |

`src/nexbank_agent/entities.py` implements these in stdlib for the demo; production would add backend verification calls (NSDL, bank core, PSP directory).

---

## 4. Normalisation (incl. Hinglish)

- **Numerals in words** ("do hazaar paanch sau" → 2500) — production adds an Indic number normaliser; the demo handles digit forms and common word-numbers.
- **Currency phrasing** ("15k", "1.5 lakh", "₹15,000") normalised to a canonical `Decimal`.
- **Dates** ("kal" → yesterday, "18th March") resolved relative to conversation timestamp.
- **Casing/handles** lower-cased for UPI/IFSC before validation.

---

### Cross-references
- Sensitivity → masking at output: [`../guardrails/account-security.md`](../guardrails/account-security.md)
- Sensitivity → log redaction: [`../architecture/audit-logging.md`](../architecture/audit-logging.md)
