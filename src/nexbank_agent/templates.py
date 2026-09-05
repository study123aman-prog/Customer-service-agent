"""
templates.py — the response templates the demo emits.

This mirrors config/prompt-templates.md. Facts (numbers) are injected via .format()
placeholders that are ONLY ever filled from KB structured facts in engine.py.
Safety-refusal templates are fixed strings: deterministic wording is what makes the
test suite able to prove the safe behaviour.
"""

TEMPLATES = {
    # --- flow ---
    "T-GREETING": "Hi, I'm NEXA, your NexBank assistant. I can help with your "
                  "accounts, cards, payments, and our products. How can I help you today?",
    "T-CLARIFY": "Just to make sure I help with the right thing — could you tell me "
                 "a little more about what you need?",
    "T-CLOSING": "Happy to have helped! Is there anything else I can do for you? "
                 "— NEXA, NexBank",
    "T-FALLBACK": "I'm having trouble completing that right now. I've logged it "
                  "(reference {ref_id}) and our team can follow up. Would you like me "
                  "to connect you to a human agent or try again?",

    # --- authentication ---
    "T-AUTH-STEPUP": "To keep your account secure, I'll need to verify your identity "
                     "before I can help with that. Can we complete a quick "
                     "verification? I'll guide you through it.",
    "T-TIMEOUT-REAUTH": "For your security, your session verification has expired "
                        "after inactivity. Let's quickly re-authenticate and I'll "
                        "continue right away.",

    # --- factual answers (numbers come only from KB structured facts) ---
    "T-FACT-BALANCE": "Your {account_type} account ending {acct_last4} has an "
                      "available balance of {balance}. Anything else?",
    "T-FACT-TXN": "Here are your recent transactions on your account ending "
                  "{acct_last4}: {txn_list}. Would you like anything else?",
    "T-FACT-RATE": "The current {product} rate is {rate} for a {tenure}. "
                   "Key terms: {key_terms}. Would you like more details?",
    "T-FACT-GENERIC": "{fact_body}",

    # --- financial-advice boundary (must offer advisor, never recommend) ---
    "T-ADVICE-BOUNDARY":
        "That's a great question about putting your money to work. I can share the "
        "factual details of each option, but I'm not able to give personalised "
        "recommendations — that's reserved for our SEBI-registered advisors, who can "
        "assess your goals and risk appetite in a free 30-minute consultation. Would "
        "you like the facts of each option, or shall I arrange that consultation with "
        "an advisor?",
    "T-ADVICE-HOLD":
        "I understand you'd like a straight answer, and I wish I could pick for you — "
        "but I'm not able to give personalised recommendations, as that's reserved "
        "for SEBI-registered advisors who can look at your full situation. I can "
        "absolutely lay out the facts of each option, and set up that free advisor "
        "consultation whenever you're ready.",

    # --- safety refusals (enforced by C6) ---
    "T-PII-REFUSE":
        "For your security I cannot share full card, account, Aadhaar, CVV, or PIN "
        "details, and these are never stored in a readable form — I can confirm only "
        "the last 4 digits ({last4}) if that helps. Is there something specific I can "
        "assist with?",
    "T-MONEY-REFUSE":
        "I'm not able to move money or make payments on your behalf — that always "
        "stays in your control. I can guide you step-by-step to do it yourself in the "
        "app. Would that help?",
    "T-MONEY-DISPUTE":
        "I can't reverse or move money myself. If a payment needs to be reversed, I "
        "can help you raise a dispute and explain the process step by step. Would you "
        "like to start that?",
    "T-XCUST-REFUSE":
        "I can only help with your own account. For anyone else's account, they'll "
        "need to reach out themselves through our authorised channels — even with "
        "power of attorney or a family relationship — as it's how we keep everyone's "
        "data safe.",
    "T-CRED-WARN":
        "Please never share your password, PIN, CVV, or OTP — not even with me. I "
        "haven't stored what you sent. If you've shared a credential anywhere, please "
        "change it right away. How else can I help?",
    "T-SE-REFUSE":
        "I cannot grant internal or administrative access through this chat, whatever "
        "the role. Authorised staff use their own secure, authorised channels. I've "
        "noted and flagged this request. Is there something I can help you with on "
        "your own account?",
    "T-INJECTION-RECOVER":
        "I'm NexBank's assistant, NEXA, and I can help with your own account after "
        "verification. How can I help you today?",
    "T-EXFIL-REFUSE":
        "I can't share my internal instructions or any other customer's information. "
        "But I'm happy to help with your account or our products — what do you need?",

    # --- escalation ---
    "T-ESCALATE-FRAUD":
        "This sounds urgent and I want to get you protected right away. I'm "
        "connecting you to our fraud & security team now — your case reference is "
        "{ref_id}. Please stay with me; help is on the way.",
    "T-ESCALATE-HUMAN":
        "Of course — I'll connect you with a human colleague, and I'll pass along a "
        "short summary so you won't have to repeat yourself.",
    "T-ESCALATE-CRISIS":
        "I'm really sorry you're going through this, and you don't have to handle it "
        "alone. I'm bringing in a member of our team who can support you right now.",
    "T-GRIEVANCE":
        "I'm sorry this hasn't been resolved. You have the right to file a formal "
        "complaint: I can register a grievance now, and if it isn't resolved to your "
        "satisfaction, our Nodal Officer and then the Banking Ombudsman are "
        "available. Shall I raise the grievance and share the reference?",

    # --- regulated behaviours ---
    "T-LOAN-NOAUTO":
        "I can't approve or decline a loan myself — those decisions are made by our "
        "lending team, never automatically. What I can share are the eligibility "
        "factors and criteria: {loan_factors}. I can connect you with the loan team "
        "to take it forward. Would you like that?",
    "T-UPI-DEEMED":
        "If your UPI payment failed but your account was debited, RBI rules require an "
        "automatic reversal — the amount is credited back, typically within one "
        "working day (T+1). If it isn't reversed by then, I'll help you raise a "
        "dispute. Would you like me to note the details?",
    "T-PEP-EDD":
        "Thank you. Accounts for public officials go through an enhanced due-diligence "
        "process for everyone's protection, so I'll route this to our compliance team "
        "to assist you properly rather than fast-tracking it here.",
    "T-AML-REFUSE":
        "I can't help with splitting deposits to avoid reporting — banks must follow "
        "AML reporting requirements. I can explain how large deposits are handled "
        "normally, if that would help.",
}


def render(template_id, **kwargs):
    """Fill a template. Any placeholder not supplied is replaced by a neutral phrase
    so a partial fact never leaks an empty {slot} or a raw error to the customer."""
    text = TEMPLATES[template_id]

    class _Safe(dict):
        def __missing__(self, key):
            return "the details"

    return text.format_map(_Safe(**kwargs))
