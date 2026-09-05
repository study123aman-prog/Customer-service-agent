"""
build_kb.py — Generates knowledge_base.json for NexBank NEXA.

Why a builder (not hand-written JSON): the compact tuple form below is easy to
read/extend and keeps the 61 entries consistent (every entry gets the same
governance fields). Run:  python build_kb.py

Each tuple: (id, category, title, body, structured, keywords,
             related_intents, ttl_days, regulatory_tag, min_auth, authority)
Author: Aman Singh. Facts sourced from the NexBank product catalogue and the
regulatory references in docs/guardrails/regulatory-compliance.md.
"""
import json
from pathlib import Path

# effective_from is fixed for the seed set; production sets it per-edit.
EFFECTIVE_FROM = "2026-08-01"

E = [
    # ---------------- PRODUCT: deposits ----------------
    ("KB-PRD-001", "product", "NexSave Savings Account",
     "The NexSave Savings Account offers 4.5% annual interest, zero minimum balance, and instant UPI. Deposits are insured by DICGC up to Rs 5 lakh.",
     {"interest_rate_pct": 4.5, "min_balance": 0, "dicgc_cover": 500000},
     ["nexsave", "savings account", "zero balance", "upi", "dicgc"],
     ["PRD-001", "ACC-007"], 90, None, "anonymous", "NexBank Product Catalogue v2026.8"),

    ("KB-PRD-002", "product", "NexFD Fixed Deposit — rates",
     "NexFD offers 6.0% to 7.25% depending on tenure (7 days to 10 years). Senior citizens get an additional 0.50%. TDS applies as per IT rules.",
     {"rate_min_pct": 6.0, "rate_max_pct": 7.25, "senior_bonus_pct": 0.5, "tenure_min": "7 days", "tenure_max": "10 years"},
     ["nexfd", "fixed deposit", "fd rate", "tenure", "senior citizen", "tds"],
     ["PRD-001", "PRD-003"], 7, None, "anonymous", "NexBank Treasury rate sheet"),

    ("KB-PRD-003", "product", "NexFD 1-year rate",
     "The NexFD rate for a 1-year tenure is 6.5% per annum for regular customers and 7.0% for senior citizens.",
     {"tenure": "1 year", "rate_pct": 6.5, "senior_rate_pct": 7.0},
     ["fd 1 year", "one year fd", "fixed deposit rate", "6.5"],
     ["PRD-003"], 7, None, "anonymous", "NexBank Treasury rate sheet"),

    ("KB-PRD-004", "product", "NexRD Recurring Deposit",
     "NexRD lets you save a fixed amount monthly from Rs 500. Rates match the equivalent FD tenure. Missed installments attract a small penalty.",
     {"min_monthly": 500, "rate_basis": "equivalent FD tenure"},
     ["nexrd", "recurring deposit", "rd", "monthly saving"],
     ["PRD-003", "PRD-001"], 30, None, "anonymous", "NexBank Product Catalogue v2026.8"),

    # ---------------- PRODUCT: cards ----------------
    ("KB-PRD-005", "product", "NexCredit Card — Classic",
     "The NexCredit Classic card has a 40-day interest-free period, 2% cashback, and no annual fee in the first year. Requires income proof and a credit score check.",
     {"interest_free_days": 40, "cashback_pct": 2, "annual_fee_year1": 0},
     ["nexcredit classic", "credit card", "cashback", "no annual fee"],
     ["PRD-001", "CRD-005"], 90, None, "anonymous", "NexBank Product Catalogue v2026.8"),

    ("KB-PRD-006", "product", "NexCredit Card — Premium",
     "The NexCredit Premium card offers a 50-day interest-free period, airport lounge access, and 5x reward points. Minimum income 10 LPA and enhanced KYC required.",
     {"interest_free_days": 50, "rewards_multiplier": 5, "min_income_lpa": 10},
     ["nexcredit premium", "lounge access", "5x rewards", "premium card"],
     ["PRD-001", "CRD-003", "CRD-005"], 90, None, "anonymous", "NexBank Product Catalogue v2026.8"),

    ("KB-PRD-007", "product", "Credit card EMI conversion",
     "Eligible purchases above Rs 2,500 can be converted to EMI over 3 to 24 months. A one-time processing fee and interest apply; the exact schedule is shown before you confirm.",
     {"min_amount": 2500, "tenure_min_months": 3, "tenure_max_months": 24},
     ["emi conversion", "convert to emi", "installments", "credit card emi"],
     ["CRD-004"], 90, None, "otp_verified", "NexBank Cards policy"),

    ("KB-PRD-008", "product", "Reward points redemption",
     "Reward points can be redeemed for statement credit, vouchers, or products in the NexRewards catalogue. Points expire 24 months after they are earned.",
     {"expiry_months": 24, "redeem_options": ["statement credit", "vouchers", "catalogue"]},
     ["reward points", "redeem", "cashback balance", "points expiry"],
     ["CRD-005"], 90, None, "otp_verified", "NexRewards T&C"),

    # ---------------- PRODUCT: loans ----------------
    ("KB-PRD-009", "product", "NexHome Loan",
     "NexHome Loans start at 8.25% with tenure up to 30 years and up to 90% loan-to-value. Requires CIBIL above 700, property valuation, and legal check.",
     {"rate_from_pct": 8.25, "tenure_max_years": 30, "max_ltv_pct": 90, "min_cibil": 700},
     ["nexhome", "home loan", "housing loan", "ltv", "cibil"],
     ["PRD-001", "PRD-002"], 30, None, "anonymous", "NexBank Lending policy"),

    ("KB-PRD-010", "product", "NexPersonal Loan",
     "NexPersonal Loans start at 10.5% with tenure up to 5 years and instant disbursal for pre-approved customers. Requires CIBIL above 650 and income verification.",
     {"rate_from_pct": 10.5, "tenure_max_years": 5, "min_cibil": 650},
     ["nexpersonal", "personal loan", "instant loan", "disbursal"],
     ["PRD-001", "PRD-002"], 30, None, "anonymous", "NexBank Lending policy"),

    ("KB-PRD-011", "product", "Home loan EMI example",
     "Illustrative only: a Rs 20 lakh home loan at 8.5% for 20 years is approximately Rs 17,356 per month. Your actual EMI depends on the sanctioned rate and tenure.",
     {"principal": 2000000, "rate_pct": 8.5, "tenure_years": 20, "emi_approx": 17356},
     ["emi", "home loan emi", "20 lakh", "monthly installment"],
     ["PRD-001", "PRD-002"], 30, None, "anonymous", "NexBank EMI calculator"),

    ("KB-PRD-012", "product", "Loan eligibility factors",
     "Loan eligibility considers income, existing obligations (FOIR), CIBIL score, employment stability, and property value for secured loans. We can share factual criteria; final approval is subject to assessment.",
     {"factors": ["income", "FOIR", "CIBIL", "employment", "collateral"]},
     ["loan eligibility", "qualify", "criteria", "foir"],
     ["PRD-002"], 90, None, "otp_verified", "NexBank Lending policy"),

    # ---------------- PRODUCT: insurance & investment ----------------
    ("KB-PRD-013", "product", "NexProtect Term Insurance",
     "NexProtect term insurance covers life risk up to Rs 1 crore with online-only pricing advantage. A medical check is required for cover above Rs 50 lakh. IRDAI regulated.",
     {"max_cover": 10000000, "medical_check_above": 5000000},
     ["nexprotect", "term insurance", "life cover", "irdai"],
     ["PRD-001", "PRD-004"], 90, "IRDAI-AI-2024", "anonymous", "NexBank Insurance (IRDAI filing)"),

    ("KB-PRD-014", "product", "NexInvest Mutual Funds",
     "NexInvest is a direct mutual fund platform with SIPs from Rs 100 across equity, debt, and hybrid funds from partner AMCs. SEBI regulated; KYC and risk disclosure mandatory. Personalised advice requires a SEBI-registered advisor.",
     {"sip_min": 100, "fund_types": ["equity", "debt", "hybrid"]},
     ["nexinvest", "mutual fund", "sip", "amc", "sebi"],
     ["PRD-001", "PRD-005"], 90, "SEBI-ROBO-2024", "anonymous", "NexBank Wealth (SEBI)"),

    ("KB-PRD-015", "product", "NexGold Digital Gold",
     "NexGold lets you buy 24K gold from Rs 10 with an option for physical delivery, via an MMTC-PAMP partnership. Physical delivery uses insured logistics.",
     {"min_amount": 10, "purity": "24K", "partner": "MMTC-PAMP"},
     ["nexgold", "digital gold", "24k", "gold investment"],
     ["PRD-001", "PRD-005"], 30, None, "anonymous", "NexBank Product Catalogue v2026.8"),

    ("KB-PRD-016", "product", "Tax benefits — Section 80C",
     "Tax-saving FDs and certain instruments offer benefits under Section 80C up to Rs 1.5 lakh per year. This is general information, not tax advice; consult a tax professional for your situation.",
     {"section": "80C", "limit": 150000},
     ["80c", "tax benefit", "tax saving fd", "deduction"],
     ["PRD-001", "PRD-005"], 90, None, "anonymous", "Income Tax Act (general)"),

    # ---------------- POLICY ----------------
    ("KB-POL-001", "policy", "Zero-liability on unauthorised transactions",
     "Under NexBank's zero-liability policy, you are protected against unauthorised transactions if reported promptly. Report immediately so we can block the card and investigate.",
     {"customer_liability": "zero if reported promptly"},
     ["zero liability", "unauthorised", "fraud protection", "report"],
     ["SEC-001", "TXN-002"], 90, "RBI-DPSC-2024", "anonymous", "RBI customer liability framework"),

    ("KB-POL-002", "policy", "Transaction dispute process",
     "Disputes are acknowledged immediately and typically investigated within 7 working days. Provisional credit may be issued per policy. You will receive updates by SMS and can track via a complaint ID.",
     {"investigation_days": 7, "provisional_credit": "as per policy"},
     ["dispute", "chargeback", "investigation", "refund timeline"],
     ["TXN-002"], 90, None, "otp_verified", "NexBank Disputes policy"),

    ("KB-POL-003", "policy", "UPI deemed-success auto-reversal",
     "If money is debited but the beneficiary is not credited, RBI's deemed-success rule requires auto-reversal, typically within 48 hours (T+1). If not reversed, compensation may apply.",
     {"auto_reversal_hours": 48, "rule": "RBI deemed success"},
     ["upi failure", "deemed success", "auto reversal", "money deducted"],
     ["TXN-003"], 30, "RBI-DPSC-2024", "otp_verified", "RBI TAT harmonisation circular"),

    ("KB-POL-004", "policy", "Card blocking and liability window",
     "Blocking a card is immediate and irreversible for that card number; a replacement is issued. Transactions after a confirmed block are the bank's liability.",
     {"block": "immediate", "replacement": "issued"},
     ["block card", "card block", "liability", "replacement"],
     ["CRD-001", "CRD-002", "SEC-001"], 90, None, "otp_verified", "NexBank Cards policy"),

    ("KB-POL-005", "policy", "Account closure process",
     "Closure requires clearing dues, zeroing balance, and identity verification; high-value accounts and certain products need branch confirmation. A cooling-off contact is made before final closure.",
     {"requires": ["nil balance", "dues cleared", "verification"], "branch_for_highvalue": True},
     ["close account", "closure", "terminate account"],
     ["ACC-005"], 90, None, "full_kyc", "NexBank Account policy"),

    ("KB-POL-006", "policy", "KYC update requirements",
     "KYC updates (address, contact, nominee) require valid proof documents and step-up authentication. We accept document types only in chat; never share full ID numbers.",
     {"auth": "biometric or full KYC", "proof": "required"},
     ["kyc update", "address proof", "documents", "nominee"],
     ["ACC-003", "ACC-004", "ACC-006"], 60, "RBI-KYC-MD", "biometric_verified", "RBI KYC Master Direction"),

    ("KB-POL-007", "policy", "Statement availability",
     "Statements are available for the last 10 years in the app and by email. Formats: PDF and Excel. E-statements are free; physical copies may carry a fee.",
     {"history_years": 10, "formats": ["PDF", "Excel"], "estatement_fee": 0},
     ["statement", "estatement", "transaction history", "pdf"],
     ["ACC-002"], 180, None, "otp_verified", "NexBank Account policy"),

    ("KB-POL-008", "policy", "Standing instructions / recurring payments",
     "You can set up, modify, or cancel standing instructions. Setup and modification of a mandate require step-up authentication. Cancellations take effect before the next scheduled debit if requested in time.",
     {"auth_setup": "biometric", "cancel_cutoff": "before next debit"},
     ["standing instruction", "recurring payment", "autopay", "mandate"],
     ["TXN-005"], 90, None, "biometric_verified", "NexBank Payments policy"),

    ("KB-POL-009", "policy", "International transfer limits & docs",
     "Outward remittances follow the RBI Liberalised Remittance Scheme (LRS) limit per financial year and require purpose code and full KYC. Charges and FX rates are shown before confirmation.",
     {"scheme": "LRS", "requires": ["purpose code", "full KYC"]},
     ["international transfer", "remittance", "lrs", "forex", "abroad"],
     ["TXN-006"], 30, "RBI-LRS", "full_kyc", "RBI LRS master direction"),

    ("KB-POL-010", "policy", "Credit limit change policy",
     "Credit limit increases are subject to income proof and risk assessment; decreases are usually immediate. Temporary limit increases are available for eligible customers.",
     {"increase": "assessment + income proof", "decrease": "immediate"},
     ["credit limit", "limit increase", "limit decrease"],
     ["CRD-003"], 90, None, "biometric_verified", "NexBank Cards policy"),

    ("KB-POL-011", "policy", "Grievance redressal mechanism",
     "If dissatisfied, you can escalate to our Nodal Officer, and if unresolved in 30 days, to the RBI Banking Ombudsman. Grievance contact details are provided within 2 turns of any complaint.",
     {"nodal_officer": True, "ombudsman_after_days": 30},
     ["grievance", "ombudsman", "nodal officer", "complaint escalation"],
     ["CMP-001", "CMP-003"], 90, "RBI-BO-2006", "anonymous", "Banking Ombudsman Scheme 2006"),

    ("KB-POL-012", "policy", "Session security & timeout",
     "For your protection, sessions time out after 5 minutes of inactivity and require re-verification. We never ask for OTP, PIN, CVV, or passwords, and never call to request them.",
     {"timeout_minutes": 5, "never_ask": ["OTP", "PIN", "CVV", "password"]},
     ["session timeout", "security", "otp", "never share"],
     ["SEC-002", "SEC-003", "SEC-004"], 90, None, "anonymous", "NexBank Security policy"),

    # ---------------- REGULATORY ----------------
    ("KB-REG-001", "regulatory", "Investment advice requires SEBI advisor",
     "NexBank can provide factual product information but cannot give personalised investment advice. Personalised recommendations require a SEBI-registered investment adviser; we offer a free advisor consultation.",
     {"rule": "info allowed, personalised advice needs SEBI RIA"},
     ["investment advice", "sebi", "advisor", "recommendation", "robo advisory"],
     ["PRD-005"], 30, "SEBI-ROBO-2024", "anonymous", "SEBI (Investment Advisers) Regulations"),

    ("KB-REG-002", "regulatory", "Mandatory product disclosures (RBI DLG)",
     "All product information must include interest rates, fees, and key terms. New sign-ups include a cooling-off period. No high-pressure sales or artificial urgency is permitted.",
     {"disclose": ["rate", "fees", "terms"], "cooling_off": True},
     ["disclosure", "cooling off", "digital lending", "rbi guidelines"],
     ["PRD-001", "PRD-002"], 30, "RBI-DLG-2022", "anonymous", "RBI Digital Lending Guidelines 2022"),

    ("KB-REG-003", "regulatory", "PCI DSS card data handling",
     "Card numbers are masked to the last 4 digits in all display and logging. CVV/CVC is never requested, stored, or displayed. Payment conversations get enhanced audit logging.",
     {"mask": "last 4", "cvv": "never", "logging": "enhanced"},
     ["pci dss", "card masking", "cvv", "card data"],
     ["TXN-002", "CRD-001"], 30, "PCI-DSS-4.0", "anonymous", "PCI DSS v4.0"),

    ("KB-REG-004", "regulatory", "KYC/AML obligations",
     "Identity must be verified before sharing account-specific information. Suspicious patterns are flagged to the AML team, and requests that could facilitate money laundering are refused. PEP status triggers enhanced due diligence.",
     {"verify_before_data": True, "pep": "enhanced due diligence"},
     ["kyc", "aml", "money laundering", "pep", "due diligence"],
     ["SEC-004", "ACC-005"], 30, "RBI-KYC-MD", "anonymous", "RBI KYC/AML Master Direction"),

    ("KB-REG-005", "regulatory", "Data protection & consent (DPDP)",
     "Customer data is processed lawfully with consent, minimised to what is needed, and retained per policy. Customers may request deletion, handled within 30 days per applicable rules.",
     {"consent": True, "deletion_days": 30},
     ["data protection", "dpdp", "consent", "privacy", "deletion"],
     ["ACC-003", "CMP-004"], 60, "DPDP-2023", "anonymous", "Digital Personal Data Protection Act 2023"),

    ("KB-REG-006", "regulatory", "AI transparency disclosure",
     "Customers are told at the start that they are interacting with an AI assistant, may request a human at any time, and AI decisions affecting outcomes are explainable and auditable.",
     {"disclose_ai": True, "human_on_request": True},
     ["ai disclosure", "transparency", "explainability", "human agent"],
     ["GEN-001", "GEN-003"], 60, "RBI-RESP-AI-2025", "anonymous", "RBI Responsible AI (draft 2025)"),

    # ---------------- FAQ ----------------
    ("KB-FAQ-001", "faq", "How to reset internet banking password",
     "Go to Login > Forgot Password, verify with OTP on your registered mobile, and set a new password. Never share OTP or password with anyone.",
     {"path": "Login > Forgot Password"},
     ["reset password", "forgot password", "internet banking login"],
     ["SEC-003"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-FAQ-002", "faq", "How to set up UPI",
     "Open the app, go to UPI > Add Account, select your bank, verify your debit card details, and set a UPI PIN. Your UPI ID is created automatically.",
     {"path": "UPI > Add Account"},
     ["upi setup", "create upi", "upi pin", "upi id"],
     ["TXN-003", "PRD-001"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-FAQ-003", "faq", "What is IFSC and where to find it",
     "IFSC is an 11-character code identifying a bank branch for NEFT/RTGS/IMPS. Your IFSC is in the app under Account Details and on your cheque book.",
     {"ifsc_length": 11},
     ["ifsc", "ifsc code", "neft code", "branch code"],
     ["TXN-004"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-FAQ-004", "faq", "NEFT vs RTGS vs IMPS",
     "IMPS is instant and 24x7. NEFT settles in half-hourly batches. RTGS is real-time for high-value transfers (Rs 2 lakh and above). Choose based on amount and urgency.",
     {"imps": "instant 24x7", "rtgs_min": 200000},
     ["neft", "rtgs", "imps", "difference", "transfer type"],
     ["TXN-004", "PRD-001"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-FAQ-005", "faq", "How to update mobile number",
     "Updating your registered mobile requires biometric or full-KYC verification for security. Start the request and we will guide you through verification and proof.",
     {"auth": "biometric"},
     ["update mobile", "change number", "registered mobile"],
     ["ACC-003"], 180, None, "otp_verified", "NexBank Help Centre"),

    ("KB-FAQ-006", "faq", "Are my deposits insured?",
     "Yes. Deposits are insured by DICGC up to Rs 5 lakh per depositor per bank, covering principal and interest.",
     {"dicgc_cover": 500000},
     ["deposit insurance", "dicgc", "safe", "insured"],
     ["PRD-001"], 180, None, "anonymous", "DICGC"),

    ("KB-FAQ-007", "faq", "How to check reward points",
     "Open the app > Cards > Rewards to see your points balance, earn history, and redemption options.",
     {"path": "Cards > Rewards"},
     ["check points", "reward balance", "points"],
     ["CRD-005"], 180, None, "otp_verified", "NexBank Help Centre"),

    ("KB-FAQ-008", "faq", "How to raise a complaint",
     "You can raise a complaint here in chat, in the app under Help > Complaints, or by email. You will get a complaint ID to track progress.",
     {"channels": ["chat", "app", "email"]},
     ["raise complaint", "file complaint", "grievance", "ticket"],
     ["CMP-001"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-FAQ-009", "faq", "Cheque book request",
     "Request a cheque book in the app under Services > Cheque Book. It is delivered to your registered address in 5-7 working days.",
     {"delivery_days": "5-7"},
     ["cheque book", "chequebook", "request cheque"],
     ["PRD-001"], 180, None, "otp_verified", "NexBank Help Centre"),

    ("KB-FAQ-010", "faq", "Nominee — why and how",
     "A nominee receives account proceeds in case of the account holder's demise, simplifying claims. Add or change a nominee with full-KYC verification and the nominee's details.",
     {"auth": "full KYC"},
     ["nominee", "beneficiary", "why nominee"],
     ["ACC-006"], 180, None, "full_kyc", "NexBank Help Centre"),

    # ---------------- TROUBLESHOOTING ----------------
    ("KB-TRB-001", "troubleshooting", "UPI payment failed but money debited",
     "1) Do not retry immediately. 2) Check if the beneficiary received it. 3) Most debits without credit auto-reverse within 48 hours under RBI rules. 4) If not reversed, we raise a priority reversal request with the reference number.",
     {"steps": 4, "auto_reversal_hours": 48},
     ["upi failed", "money deducted", "not received", "reversal steps"],
     ["TXN-003"], 180, "RBI-DPSC-2024", "otp_verified", "NexBank Help + RBI"),

    ("KB-TRB-002", "troubleshooting", "Card declined at merchant",
     "Common causes: insufficient balance, limit reached, international usage disabled, or a temporary block. Check balance and limits, enable relevant usage in the app, and retry; if it persists we investigate.",
     {"causes": ["balance", "limit", "intl disabled", "block"]},
     ["card declined", "payment failed", "card not working"],
     ["CRD-001", "TXN-001"], 180, None, "otp_verified", "NexBank Help Centre"),

    ("KB-TRB-003", "troubleshooting", "Not receiving OTP",
     "1) Check network/signal. 2) Ensure DND isn't blocking bank SMS. 3) Confirm your registered mobile is correct. 4) Request resend after 60 seconds. If it still fails, we offer an alternate verification path.",
     {"resend_after_seconds": 60},
     ["otp not received", "no otp", "otp issue"],
     ["SEC-003", "ACC-001"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-TRB-004", "troubleshooting", "NEFT/RTGS not credited to beneficiary",
     "NEFT settles in batches and may take up to a few hours; RTGS is faster. Share the UTR so we can trace it. If beyond the expected window, we raise a trace with the beneficiary bank.",
     {"need": "UTR reference"},
     ["neft not credited", "rtgs delayed", "transfer pending", "utr"],
     ["TXN-004"], 180, None, "otp_verified", "NexBank Help Centre"),

    ("KB-TRB-005", "troubleshooting", "App login not working",
     "Update to the latest app version, check internet, and retry. If locked out, use Forgot Password with OTP. Repeated failures may indicate a security lock we can review after verification.",
     {},
     ["app not working", "login failed", "cant login", "locked out"],
     ["SEC-003", "SEC-004"], 180, None, "anonymous", "NexBank Help Centre"),

    ("KB-TRB-006", "troubleshooting", "Statement not downloading",
     "Try a shorter date range, switch format (PDF/Excel), and ensure sufficient device storage. We can also email the statement to your registered address.",
     {"alt": "email statement"},
     ["statement not downloading", "cant download statement"],
     ["ACC-002"], 180, None, "otp_verified", "NexBank Help Centre"),

    # ---------------- ESCALATION ----------------
    ("KB-ESC-001", "escalation", "When to escalate to Fraud team",
     "Confirmed or suspected fraud, unauthorised transactions, or stolen card details are escalated immediately (P0) to the Fraud Investigation team after taking protective action (card block).",
     {"priority": "P0", "queue": "Fraud Investigation"},
     ["fraud escalation", "unauthorised", "stolen card"],
     ["SEC-001"], 90, None, "anonymous", "NexBank Escalation matrix"),

    ("KB-ESC-002", "escalation", "Investment advisory handoff",
     "Requests for personalised investment advice are routed to a SEBI-registered advisor via a free consultation. NEXA provides factual product info only.",
     {"priority": "P1", "queue": "Wealth Advisory"},
     ["advisor", "investment advice", "sebi consultation"],
     ["PRD-005"], 90, "SEBI-ROBO-2024", "anonymous", "NexBank Escalation matrix"),

    ("KB-ESC-003", "escalation", "High-value account closure",
     "Closure requests for accounts above Rs 5 lakh are routed to a Relationship Manager for retention contact and branch verification before processing.",
     {"priority": "P1", "queue": "Relationship Manager", "threshold": 500000},
     ["high value closure", "relationship manager", "close account"],
     ["ACC-005"], 90, None, "full_kyc", "NexBank Escalation matrix"),

    ("KB-ESC-004", "escalation", "Regulatory uncertainty handoff",
     "If a regulatory question cannot be answered confidently from current, non-expired knowledge, NEXA does not guess; it routes to the Compliance Helpdesk.",
     {"priority": "P1", "queue": "Compliance Helpdesk"},
     ["regulatory question", "compliance", "uncertain"],
     ["PRD-001", "CMP-001"], 30, None, "anonymous", "NexBank Escalation matrix"),

    ("KB-ESC-005", "escalation", "Vulnerable customer / crisis",
     "Any mention of self-harm, threats, or emergencies is handled with empathy and routed immediately to the Crisis Response protocol; banking flow is paused.",
     {"priority": "P0", "queue": "Crisis Response"},
     ["self harm", "emergency", "crisis", "threat"],
     ["CMP-003"], 90, None, "anonymous", "NexBank Escalation matrix"),

    # ---------------- extra product/policy to reach breadth ----------------
    ("KB-PRD-017", "product", "Salary account features",
     "NexBank salary accounts offer zero balance, free unlimited transactions, and preferential loan rates. Conversion from savings is available.",
     {"min_balance": 0, "perks": ["free transactions", "preferential rates"]},
     ["salary account", "zero balance", "convert account"],
     ["ACC-007", "PRD-001"], 90, None, "anonymous", "NexBank Product Catalogue v2026.8"),

    ("KB-PRD-018", "product", "Forex rate availability",
     "Live USD/INR and other FX rates are available on the NexBank platform and app. We provide the current rate as information; we do not advise on currency timing.",
     {"info_only": True},
     ["forex", "usd inr", "exchange rate", "currency"],
     ["PRD-001", "TXN-006"], 7, None, "anonymous", "NexBank Treasury"),

    ("KB-POL-013", "policy", "Provisional credit for disputes",
     "For eligible disputed debit transactions, provisional credit may be granted during investigation per RBI TAT norms, and is reversed only if the dispute is found invalid.",
     {"provisional_credit": "eligible per RBI TAT"},
     ["provisional credit", "dispute refund", "tat"],
     ["TXN-002"], 30, "RBI-DPSC-2024", "otp_verified", "RBI TAT norms"),

    ("KB-POL-014", "policy", "Complaint resolution SLA",
     "Complaints are acknowledged immediately and targeted for resolution within defined SLAs by category; you receive a complaint ID and SMS updates at each stage.",
     {"ack": "immediate", "updates": "SMS"},
     ["complaint sla", "resolution time", "complaint update"],
     ["CMP-001", "CMP-002"], 90, None, "otp_verified", "NexBank Service policy"),

    ("KB-FAQ-011", "faq", "How to talk to a human agent",
     "You can ask for a human agent at any time and we will connect you to the next available representative or arrange a callback if outside working hours.",
     {"human_on_request": True},
     ["human agent", "talk to person", "representative", "callback"],
     ["GEN-003", "CMP-005"], 180, "RBI-RESP-AI-2025", "anonymous", "NexBank Service policy"),

    ("KB-FAQ-012", "faq", "Working hours and availability",
     "The NEXA assistant is available 24x7. Human specialist teams operate 9am-9pm IST; urgent security and fraud support is available round the clock.",
     {"ai": "24x7", "human": "9-21 IST", "fraud": "24x7"},
     ["working hours", "availability", "24x7", "timing"],
     ["GEN-002", "CMP-005"], 180, None, "anonymous", "NexBank Help Centre"),
]

def to_entry(t):
    (id_, cat, title, body, structured, keywords, intents, ttl, reg, auth, src) = t
    return {
        "id": id_, "category": cat, "title": title, "body": body,
        "structured": structured, "keywords": keywords,
        "related_intents": intents,
        "version": "1.0.0", "effective_from": EFFECTIVE_FROM,
        "freshness_ttl_days": ttl, "regulatory_tag": reg,
        "authority_source": src, "min_auth_level": auth,
        "sensitivity": "public" if auth == "anonymous" else "internal",
        "approved_by": "RC-fast-track" if reg else "product-owner",
        "supersedes": None,
    }

def main():
    entries = [to_entry(t) for t in E]
    assert len({e["id"] for e in entries}) == len(entries), "duplicate ids"
    out = Path(__file__).with_name("knowledge_base.json")
    out.write_text(json.dumps(entries, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(entries)} KB entries to {out}")
    # quick category tally
    from collections import Counter
    print(dict(Counter(e["category"] for e in entries)))

if __name__ == "__main__":
    main()
