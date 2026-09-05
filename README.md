# NexBank NEXA — Agentic AI Customer Service System

**Project code:** 463548C
**Category:** Customer Service Agent / Agentic AI Engineer
**Author:** Aman Singh
**Role in scenario:** Lead Conversational AI Architect, NexBank

> A production-grade, self-improving agentic AI customer-service system for **NexBank**, a fictional Indian neo-bank (2.7M customers, ~18,000 interactions/day).
>
> This repository is a **design and specification deliverable**: it documents an architecture detailed enough for an ML/platform team to build from, and ships a small **offline reference demo** that exercises the core reasoning loop end to end.
>
> The agent persona is **NEXA** — the *NexBank Expert Assistant*.
>
> **Brand voice:** *friendly, trustworthy, modern.*

---

## 1. The problem in one paragraph

NexBank wants to move 60% of first-line support to an AI-first system within 18 months (projected saving ₹42 crore/year) while lifting CSAT from 3.2 to 4.5 out of 5.

The system must satisfy two governance bodies with opposing pressures:

* **Customer Experience Board (CEB)** — wants natural, empathetic, high-resolution conversations.
* **Risk Committee (RC)** — tolerates *zero* incorrect financial advice and demands RBI / PCI-DSS / KYC-AML compliance, tamper-proof audit trails, and adversarial robustness.

NEXA is designed around that tension: a layered dialogue + NLU + retrieval stack for capability, wrapped in an **immutable rule-based safety layer** that the learning pipeline can never weaken.

### Design targets

| Metric                          |                                Target |       Legacy baseline |
| ------------------------------- | ------------------------------------: | --------------------: |
| Containment rate                |                                 ≥ 70% | ~35–48% (competitors) |
| CSAT (1–5)                      |                                 ≥ 4.5 |                   3.2 |
| Incorrect financial-advice rate |                                **0%** |                     — |
| First response time             | < 30s (business) / < 3s technical p95 |                     — |
| Intent recognition accuracy     |                                 > 92% |                     — |

---

## 2. Repository map

| Path                                                 | Contents                                                                                                                          |
| ---------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| [`docs/architecture/`](docs/architecture/)           | System architecture (14 components), dialogue state machine, interface contracts, failure modes, latency budget, scalability      |
| [`docs/intent-taxonomy/`](docs/intent-taxonomy/)     | 32-intent hierarchical taxonomy, entity model, slot-filling, disambiguation, out-of-scope, sample utterances                      |
| [`docs/knowledge-base/`](docs/knowledge-base/)       | KB schema, 61 sample entries, hybrid retrieval pipeline (sub-200ms), maintenance & regulatory-update workflow                     |
| [`docs/guardrails/`](docs/guardrails/)               | Financial-advice, security, regulatory, and adversarial guardrails; implementation strategy; incident-response playbook           |
| [`docs/learning-pipeline/`](docs/learning-pipeline/) | Continuous-learning pipeline, 3 feedback sources, safety-invariant preservation, A/B testing                                      |
| [`docs/escalation/`](docs/escalation/)               | 15 escalation triggers, routing logic, handoff context package, queue management                                                  |
| [`docs/metrics/`](docs/metrics/)                     | Leading/lagging/operational metrics, improvement cycle, 3 dashboard specifications                                                |
| [`diagrams/`](diagrams/)                             | Mermaid diagrams: system architecture, guardrail pipeline, dialogue state machine, escalation routing, learning loop, auth ladder |
| [`simulations/`](simulations/)                       | 20+ annotated sample conversation flows                                                                                           |
| [`tests/`](tests/)                                   | 50+ adversarial/safety test cases (data + runnable pytest)                                                                        |
| [`config/`](config/)                                 | 6-layer system-prompt spec, prompt-template library, configuration parameters                                                     |
| [`src/`](src/)                                       | Offline Python reference demo of the core loop                                                                                    |
| [`CHANGELOG.md`](CHANGELOG.md)                       | Day-by-day development log                                                                                                        |

### Suggested reading order

**architecture → intent-taxonomy → knowledge-base → guardrails → learning-pipeline → escalation → metrics → simulations**

Start with [`docs/architecture/README.md`](docs/architecture/README.md).

---

## 3. Architecture at a glance

```text
Customer
   │
   ▼
Channel Gateway
   │
   ▼
Input Safety
   │
   ▼
NLU
   │
   ▼
Dialogue Manager
   │
   ▼
Dialogue Policy
   │
   ├─────────────── Immutable Safety Layer ───────────────┐
   │                  (rule-based, un-learnable)          │
   │                  consulted at every step             │
   │                                                     │
   ▼                                                     │
Auth Service · KB Retrieval · Response Generation       │
   │                                                     │
   ▼                                                     │
Output Safety
   │
   ▼
Customer
   │
   ├── Audit Logging
   ├── Metrics / Observability
   └── Escalation & Routing
              │
              ▼
Continuous Learning Pipeline
        (offline, safety-gated)
              ▲
              │
           feedback
```

Full component descriptions, interfaces, and diagrams:

[`docs/architecture/`](docs/architecture/)

---

## 4. The reference demo (`src/`)

The demo is a **compact, offline, dependency-free** (Python 3.10+, standard library only) implementation of NEXA's core loop.

It is a *reference* for the specification — not the production system — but it runs the real logic:

* Hierarchical intent classification
* Entity extraction with validation
* Sentiment tracking
* KB retrieval
* Immutable guardrail layer
* Escalation triggers
* Turn-level structured logging

### Running the demo

```bash
# No install, no API keys, fully offline (Python 3.10+)

# 1) Interactive console — chat with the engine.
# Every reply prints the safety metadata
# (flags / blocked / escalation) so you can SEE the guardrail fire.

cd src
python3 -m nexbank_agent.cli

# Optional:
# --auth otp_verified

cd ..

# 2) Regenerate the 30 scripted case-study scenarios
# (balance auth, dispute→fraud, advice guardrail,
# prompt-injection, Hinglish, complaint recovery)
# by replaying them through the LIVE engine.
#
# Writes:
# simulations/README.md
# simulations/transcripts.json

python3 simulations/build_simulations.py

# 3) Run the safety / guardrail suite
# (62 cases; exits non-zero on any failure).

python3 run_tests.py

# Optional:
# -v for per-failure detail

# Same cases are also runnable under pytest:

python3 -m pytest tests/test_guardrails.py
```

> The demo deliberately uses a rule-based/lexical classifier and a local keyword+TF-IDF retriever so it is deterministic and always runs.
>
> Where the *production* design calls for a transformer NLU model or an LLM generator, the code exposes a clearly-marked pluggable interface (`model-swappable` per Part E5) rather than hard-coding a provider.

---

## 5. How this maps to the assessment

| Deliverable (Part D / Campaign level)     | Location                                                                                |
| ----------------------------------------- | --------------------------------------------------------------------------------------- |
| L1 Architecture & dialogue management     | `docs/architecture/`, `diagrams/`                                                       |
| L2 Intent taxonomy & NLU                  | `docs/intent-taxonomy/`                                                                 |
| L3 Knowledge base & retrieval             | `docs/knowledge-base/`                                                                  |
| L4 Guardrails & safety (50+ tests)        | `docs/guardrails/`, `tests/`                                                            |
| L5 Continuous-learning pipeline           | `docs/learning-pipeline/`                                                               |
| L6 Escalation & satisfaction              | `docs/escalation/`, `docs/metrics/`                                                     |
| L7 Integration & 20+ conversations        | `simulations/`, `src/`                                                                  |
| Audit logging, risk matrix, system prompt | `docs/architecture/audit-logging.md`, `docs/architecture/risk-assessment.md`, `config/` |

---

## 6. AI tools used (transparency)

In line with the project's AI-assistance policy, AI tools were used as follows, and all outputs were reviewed and validated by the author against the project brief and the cited regulatory sources:

* **Claude (Anthropic)** — drafting and structuring specification documents, generating the Mermaid diagrams, and scaffolding the reference demo. All architectural decisions, trade-offs, and the final wording are the author's own and were validated line by line.

* **Regulatory facts** (RBI digital-payment/lending, SEBI robo-advisory, PCI-DSS, KYC/AML, DPDP Act) were cross-checked against the official sources listed in `docs/guardrails/regulatory-compliance.md`.

The author can explain every design choice and every line of demo code without AI assistance.

---

## 7. Disclaimer

NexBank, its customers, products, transcripts, and data are **fictional and simulated** for this assessment.

Nothing here is financial advice or a real banking service.

Regulatory references are for design realism; a real deployment would require formal legal/compliance sign-off.
