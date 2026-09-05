# Knowledge Base — Entry Catalogue (61 entries)

Parent: [`README.md`](README.md) · Machine-readable source: [`../../src/data/knowledge_base.json`](../../src/data/knowledge_base.json)

Auto-generated from the JSON so the catalogue never drifts from what the demo loads. Exceeds the 50-entry minimum. Each entry lists its id, title, linked intents, freshness TTL, regulatory tag, and minimum auth level.

**Category tally:** product: 18 · policy: 14 · regulatory: 6 · faq: 12 · troubleshooting: 6 · escalation: 5


## Product (18)

| ID | Title | Intents | TTL (d) | Reg tag | Min auth |
|---|---|---|---|---|---|
| KB-PRD-001 | NexSave Savings Account | PRD-001, ACC-007 | 90 | — | anonymous |
| KB-PRD-002 | NexFD Fixed Deposit — rates | PRD-001, PRD-003 | 7 | — | anonymous |
| KB-PRD-003 | NexFD 1-year rate | PRD-003 | 7 | — | anonymous |
| KB-PRD-004 | NexRD Recurring Deposit | PRD-003, PRD-001 | 30 | — | anonymous |
| KB-PRD-005 | NexCredit Card — Classic | PRD-001, CRD-005 | 90 | — | anonymous |
| KB-PRD-006 | NexCredit Card — Premium | PRD-001, CRD-003, CRD-005 | 90 | — | anonymous |
| KB-PRD-007 | Credit card EMI conversion | CRD-004 | 90 | — | otp_verified |
| KB-PRD-008 | Reward points redemption | CRD-005 | 90 | — | otp_verified |
| KB-PRD-009 | NexHome Loan | PRD-001, PRD-002 | 30 | — | anonymous |
| KB-PRD-010 | NexPersonal Loan | PRD-001, PRD-002 | 30 | — | anonymous |
| KB-PRD-011 | Home loan EMI example | PRD-001, PRD-002 | 30 | — | anonymous |
| KB-PRD-012 | Loan eligibility factors | PRD-002 | 90 | — | otp_verified |
| KB-PRD-013 | NexProtect Term Insurance | PRD-001, PRD-004 | 90 | IRDAI-AI-2024 | anonymous |
| KB-PRD-014 | NexInvest Mutual Funds | PRD-001, PRD-005 | 90 | SEBI-ROBO-2024 | anonymous |
| KB-PRD-015 | NexGold Digital Gold | PRD-001, PRD-005 | 30 | — | anonymous |
| KB-PRD-016 | Tax benefits — Section 80C | PRD-001, PRD-005 | 90 | — | anonymous |
| KB-PRD-017 | Salary account features | ACC-007, PRD-001 | 90 | — | anonymous |
| KB-PRD-018 | Forex rate availability | PRD-001, TXN-006 | 7 | — | anonymous |

## Policy (14)

| ID | Title | Intents | TTL (d) | Reg tag | Min auth |
|---|---|---|---|---|---|
| KB-POL-001 | Zero-liability on unauthorised transactions | SEC-001, TXN-002 | 90 | RBI-DPSC-2024 | anonymous |
| KB-POL-002 | Transaction dispute process | TXN-002 | 90 | — | otp_verified |
| KB-POL-003 | UPI deemed-success auto-reversal | TXN-003 | 30 | RBI-DPSC-2024 | otp_verified |
| KB-POL-004 | Card blocking and liability window | CRD-001, CRD-002, SEC-001 | 90 | — | otp_verified |
| KB-POL-005 | Account closure process | ACC-005 | 90 | — | full_kyc |
| KB-POL-006 | KYC update requirements | ACC-003, ACC-004, ACC-006 | 60 | RBI-KYC-MD | biometric_verified |
| KB-POL-007 | Statement availability | ACC-002 | 180 | — | otp_verified |
| KB-POL-008 | Standing instructions / recurring payments | TXN-005 | 90 | — | biometric_verified |
| KB-POL-009 | International transfer limits & docs | TXN-006 | 30 | RBI-LRS | full_kyc |
| KB-POL-010 | Credit limit change policy | CRD-003 | 90 | — | biometric_verified |
| KB-POL-011 | Grievance redressal mechanism | CMP-001, CMP-003 | 90 | RBI-BO-2006 | anonymous |
| KB-POL-012 | Session security & timeout | SEC-002, SEC-003, SEC-004 | 90 | — | anonymous |
| KB-POL-013 | Provisional credit for disputes | TXN-002 | 30 | RBI-DPSC-2024 | otp_verified |
| KB-POL-014 | Complaint resolution SLA | CMP-001, CMP-002 | 90 | — | otp_verified |

## Regulatory (6)

| ID | Title | Intents | TTL (d) | Reg tag | Min auth |
|---|---|---|---|---|---|
| KB-REG-001 | Investment advice requires SEBI advisor | PRD-005 | 30 | SEBI-ROBO-2024 | anonymous |
| KB-REG-002 | Mandatory product disclosures (RBI DLG) | PRD-001, PRD-002 | 30 | RBI-DLG-2022 | anonymous |
| KB-REG-003 | PCI DSS card data handling | TXN-002, CRD-001 | 30 | PCI-DSS-4.0 | anonymous |
| KB-REG-004 | KYC/AML obligations | SEC-004, ACC-005 | 30 | RBI-KYC-MD | anonymous |
| KB-REG-005 | Data protection & consent (DPDP) | ACC-003, CMP-004 | 60 | DPDP-2023 | anonymous |
| KB-REG-006 | AI transparency disclosure | GEN-001, GEN-003 | 60 | RBI-RESP-AI-2025 | anonymous |

## Faq (12)

| ID | Title | Intents | TTL (d) | Reg tag | Min auth |
|---|---|---|---|---|---|
| KB-FAQ-001 | How to reset internet banking password | SEC-003 | 180 | — | anonymous |
| KB-FAQ-002 | How to set up UPI | TXN-003, PRD-001 | 180 | — | anonymous |
| KB-FAQ-003 | What is IFSC and where to find it | TXN-004 | 180 | — | anonymous |
| KB-FAQ-004 | NEFT vs RTGS vs IMPS | TXN-004, PRD-001 | 180 | — | anonymous |
| KB-FAQ-005 | How to update mobile number | ACC-003 | 180 | — | otp_verified |
| KB-FAQ-006 | Are my deposits insured? | PRD-001 | 180 | — | anonymous |
| KB-FAQ-007 | How to check reward points | CRD-005 | 180 | — | otp_verified |
| KB-FAQ-008 | How to raise a complaint | CMP-001 | 180 | — | anonymous |
| KB-FAQ-009 | Cheque book request | PRD-001 | 180 | — | otp_verified |
| KB-FAQ-010 | Nominee — why and how | ACC-006 | 180 | — | full_kyc |
| KB-FAQ-011 | How to talk to a human agent | GEN-003, CMP-005 | 180 | RBI-RESP-AI-2025 | anonymous |
| KB-FAQ-012 | Working hours and availability | GEN-002, CMP-005 | 180 | — | anonymous |

## Troubleshooting (6)

| ID | Title | Intents | TTL (d) | Reg tag | Min auth |
|---|---|---|---|---|---|
| KB-TRB-001 | UPI payment failed but money debited | TXN-003 | 180 | RBI-DPSC-2024 | otp_verified |
| KB-TRB-002 | Card declined at merchant | CRD-001, TXN-001 | 180 | — | otp_verified |
| KB-TRB-003 | Not receiving OTP | SEC-003, ACC-001 | 180 | — | anonymous |
| KB-TRB-004 | NEFT/RTGS not credited to beneficiary | TXN-004 | 180 | — | otp_verified |
| KB-TRB-005 | App login not working | SEC-003, SEC-004 | 180 | — | anonymous |
| KB-TRB-006 | Statement not downloading | ACC-002 | 180 | — | otp_verified |

## Escalation (5)

| ID | Title | Intents | TTL (d) | Reg tag | Min auth |
|---|---|---|---|---|---|
| KB-ESC-001 | When to escalate to Fraud team | SEC-001 | 90 | — | anonymous |
| KB-ESC-002 | Investment advisory handoff | PRD-005 | 90 | SEBI-ROBO-2024 | anonymous |
| KB-ESC-003 | High-value account closure | ACC-005 | 90 | — | full_kyc |
| KB-ESC-004 | Regulatory uncertainty handoff | PRD-001, CMP-001 | 30 | — | anonymous |
| KB-ESC-005 | Vulnerable customer / crisis | CMP-003 | 90 | — | anonymous |
