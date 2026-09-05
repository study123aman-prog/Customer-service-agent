# Regulatory-Compliance Guardrails — NexBank NEXA

Parent: [`README.md`](README.md) · Enforced by: C6 + C10 + KB freshness (C8) · Reporting: C12.

Maps each applicable regulation to the concrete guardrail behaviour it drives and the testable assertion that proves it. This is the "Regulator" competency evidence: RBI, PCI-DSS, KYC/AML mapped with no gaps.

---

## 1. Framework → guardrail mapping

| Regulation / guideline | Authority | NEXA guardrail behaviour |
|---|---|---|
| **Digital Lending Guidelines (Sep 2022)** | RBI | Mandatory disclosures (rate, fees, T&C) in every product answer; cooling-off info on sign-up; no artificial urgency/high-pressure sales. |
| **Master Direction on Digital Payment Security Controls (Apr 2024)** | RBI | End-to-end encryption for payment channels; enhanced logging for payment convos; deemed-success/auto-reversal handling. |
| **Circular on Responsible AI in Financial Services (Draft 2025)** | RBI | AI disclosure at start; human-on-request; explainable, auditable decisions; **no fully automated credit decisions** (loan = info + human). |
| **Robo-Advisory Guidelines (2024)** | SEBI | Personalised investment advice requires a SEBI-registered adviser; information-only is exempt → advice guardrail + ESC-013. |
| **AI in Insurance Distribution (2024)** | IRDAI | Human oversight for AI-recommended insurance above thresholds; NEXA gives product info, routes recommendations to human. |
| **PCI DSS v4.0** | PCI SSC | Card masked to last-4 everywhere; CVV never requested/stored/shown; enhanced audit for payment convos. |
| **KYC/AML Master Direction** | RBI | Verify identity before account-specific info; flag suspicious patterns to AML; refuse laundering-facilitating requests; PEP → enhanced due diligence (ESC-015). |
| **IT (Reasonable Security Practices) Rules, 2011** | MeitY | Sensitive personal data handling standards for logs and storage. |
| **Digital Personal Data Protection Act, 2023** | GoI | Consent-based processing; data minimisation; right-to-deletion within 30 days; localisation. |
| **Banking Ombudsman Scheme, 2006 (amd. 2017)** | RBI | Grievance-redressal info within **2 turns** of any complaint; Nodal Officer → Ombudsman path. |
| **NIST AI RMF 1.0** | NIST | Risk identify/measure/manage framing for the risk matrix + monitoring. |
| **EU AI Act — High-Risk / OWASP LLM Top 10** | EU / OWASP | Transparency mandates; injection defences and LLM-specific controls (see `adversarial-robustness.md`). |

---

## 2. Behavioural rules encoded

- **RBI DLG disclosures.** Any `product.*` answer that states a rate/fee must include the key terms and (on sign-up flows) cooling-off info. C10 checks that a rate figure is accompanied by its disclosure snippet from KB.
- **Grievance within 2 turns.** On any `complaint.*` intent, the grievance-redressal info (KB-POL-011) is surfaced within 2 turns. *Assertion `GR-OMB-2TURN`.*
- **No automated credit decision.** Loan intents (PRD-002) return eligibility *factors and factual criteria*, never an approval/rejection decision. *Assertion `GR-LOAN-NOAUTO`.*
- **Deemed-success handling.** UPI failure (TXN-003) applies the RBI T+1 auto-reversal rule from KB-POL-003 (Case Study 6). *Assertion `GR-UPI-DEEMED`.*
- **PEP / AML.** PEP flag → ESC-015 enhanced due diligence; suspicious pattern → AML flag; no laundering facilitation. *Assertion `GR-PEP`, `GR-AML`.*
- **KB freshness fail-closed.** Regulatory figures whose TTL expired are blocked from generation → ESC-008 (`../knowledge-base/README.md` §3).

---

## 3. Regulatory reporting (C12 → compliance)

| Report | Cadence | Contents |
|---|---|---|
| AI interaction summary → RBI | Monthly | Volume, escalation rates, complaint categories |
| Customer complaint analysis → Ombudsman | Quarterly | Complaint categories, resolution times, redressal outcomes |
| AI system audit report | Annual | Accuracy, fairness, safety metrics, model version history |
| Ad-hoc regulatory query response | ≤48h | Traceable logs for specific interactions |

Log schema and retention that make these possible: [`../architecture/audit-logging.md`](../architecture/audit-logging.md).

---

## 4. Disclaimer discipline

- Investment/insurance/tax answers carry the appropriate "information only / consult a registered professional" note (from KB), never presented as advice.
- All regulatory facts in this repo are cross-checked against the official sources listed in the table; a production deployment requires formal compliance sign-off.
