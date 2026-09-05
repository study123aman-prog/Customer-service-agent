# Response Template Catalogue — NexBank NEXA

Parent: [`system-prompt.md`](system-prompt.md) · Implemented by: `src/nexbank_agent/templates.py` (the demo uses these verbatim).

**Template-first for facts and safety; free generation only for empathy.** Templates give three guarantees the brief needs: (1) regulated wording is exact and reviewed, (2) factual numbers come from KB `structured` fields via `{placeholders}`, never model memory, and (3) safety refusals are deterministic. The learning pipeline may *rank/tune* templates but each is pre-approved and re-checked by C10.

Placeholders like `{fd_rate}` are filled **only** from retrieved KB structured facts; if the fact is missing/stale, the template is not used and the turn escalates (ESC-008).

---

## Conversation flow

**T-GREETING**
> Hi, I'm NEXA, your NexBank assistant. I can help with your accounts, cards, payments, and our products. How can I help you today?

**T-CLARIFY**
> Just to make sure I help with the right thing — {clarify_question}

**T-CLOSING**
> Happy to have helped! Is there anything else I can do for you? — NEXA, NexBank

**T-FALLBACK** (technical failure, ESC-012)
> I'm having trouble completing that right now. I've logged it (reference {ref_id}) and our team can follow up. Would you like me to connect you to a human agent or try again?

---

## Authentication

**T-AUTH-STEPUP**
> To keep your account secure, I'll need to verify your identity before I can help with that. Can we complete a quick verification? {auth_method_hint}

**T-TIMEOUT-REAUTH**
> For your security, your session verification has expired after inactivity. Let's quickly re-authenticate and I'll continue right away.

---

## Factual answers (numbers come from KB structured facts)

**T-FACT-BALANCE**
> Your {account_type} account ending {acct_last4} has an available balance of {balance}. Anything else?

**T-FACT-RATE**
> The current {product} rate is {rate} for {tenure}. Key terms: {key_terms}. Would you like more details?

**T-FACT-GENERIC**
> {fact_body} {disclosure_snippet}

---

## Financial-advice boundary (ESC-013)

**T-ADVICE-BOUNDARY** — *must offer an advisor; must never contain a recommendation.*
> That's a great question about putting your money to work. I can share the factual details: {option_a_facts} and {option_b_facts}. Which one fits best depends on your personal goals and risk appetite, which our SEBI-registered advisors can assess in a free 30-minute consultation. Would you like the details of either option, or shall I arrange that consultation?

**T-ADVICE-HOLD** — *when the customer presses (GA-ADV-PRESS).*
> I understand you'd like a straight answer, and I wish I could pick for you — but I'm not able to give personalised recommendations, as that's reserved for SEBI-registered advisors who can look at your full situation. I can absolutely lay out the facts of each option, and set up that free consultation whenever you're ready.

---

## Safety refusals (deterministic; enforced by C6)

**T-PII-REFUSE**
> For your security I can't share full card, account, Aadhaar, CVV, or PIN details — I can confirm the last 4 digits ({last4}) if that helps. Is there something specific I can assist with?

**T-MONEY-REFUSE**
> I'm not able to move money or make payments on your behalf — that always stays in your control. I can guide you step-by-step to do it yourself in the app. Would that help?

**T-XCUST-REFUSE**
> I can only help with your own account. For anyone else's account, they'll need to reach out themselves through our authorised channels, even with power of attorney or a family relationship — it's how we keep everyone's data safe.

**T-CRED-WARN**
> Please never share your password, PIN, CVV, or OTP — not even with me. I haven't stored what you sent. If you've shared a credential anywhere, please change it right away. How else can I help?

**T-SE-REFUSE** (ESC-009 on repeat)
> I'm not able to grant internal or administrative access through this chat, regardless of role. Authorised staff have their own secure channels. I've noted this request. Is there something I can help you with on your own account?

**T-INJECTION-RECOVER**
> I'm NexBank's assistant, NEXA, and I can help with your own account after verification. How can I help you today?

**T-EXFIL-REFUSE**
> I can't share my internal instructions or any other customer's information. But I'm happy to help with your account or our products — what do you need?

---

## Escalation

**T-ESCALATE-FRAUD** (ESC-001, P0)
> This sounds urgent and I want to get you protected right away. I'm connecting you to our fraud & security team now — your case reference is {ref_id}. Please stay with me; help is on the way.

**T-ESCALATE-HUMAN** (ESC-005)
> Of course — I'll connect you with a human colleague. Here's a quick summary I'll pass along so you won't have to repeat yourself: {handoff_summary}.

**T-ESCALATE-CRISIS** (ESC-003, P0)
> I'm really sorry you're going through this, and you don't have to handle it alone. I'm bringing in a member of our team who can support you right now.

**T-GRIEVANCE** (ESC-010) — *must surface the grievance path within 2 turns.*
> I'm sorry this hasn't been resolved. You have the right to file a formal complaint: I can register a grievance now, and if it isn't resolved to your satisfaction, our Nodal Officer and then the Banking Ombudsman are available. Shall I raise the grievance and share the reference?

---

## Regulated behaviours

**T-LOAN-NOAUTO** (ESC-014) — *must not approve/reject; give factors.*
> I can't approve or decline a loan myself — those decisions are made by our lending team, never automatically. What I can share are the eligibility factors and criteria: {loan_factors}. I can connect you with the loan team to take it forward. Would you like that?

**T-UPI-DEEMED** — *deemed-success auto-reversal.*
> If your UPI payment failed but your account was debited, RBI rules require an automatic reversal — the amount is credited back, typically within one working day (T+1). If it isn't reversed by then, I'll help you raise a dispute. Would you like me to note the details?

---

## Approval & versioning

Every template has an owner and an approval record; regulated templates (advice, loan, grievance, UPI) require Risk & Compliance sign-off. Template ids and versions are logged with each response (C12). The demo's `templates.py` mirrors this catalogue so the test suite verifies the exact safe wording.
