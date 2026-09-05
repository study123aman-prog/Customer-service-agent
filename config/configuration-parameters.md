# Configuration Parameters — NexBank NEXA

**Deliverable:** Cross-cutting configuration reference (supports L2 Architecture, L3 Taxonomy, L4 Guardrails, L5 Learning).
**Machine-readable companion:** [`agent_config.json`](agent_config.json) — the file the demo actually loads.

This document is the **canonical, human-readable reference for every tunable threshold** in the system. It exists so that no number is a "magic constant" buried in prose or code: each value has one home, one owner, and one rationale. Other documents (architecture, intent-taxonomy, knowledge-base, guardrails, metrics) cite parameters by name and link here.

## The one rule: what may change, and what may never

The system is a **capability core wrapped by an immutable safety layer.** That split governs this whole file:

- **Immutable** parameters express *hard safety*. They live in code (chokepoint **C6**) and in the fixed structure below. The continuous-learning pipeline (C14) **cannot** alter them — not by tuning, not by A/B test, not by supervisor correction. Changing one is a code change subject to Risk-Committee (RC) review, never an automated update.
- **Soft-tunable** parameters express *policy and quality* (phrasing, ranking, when to ask a clarifying question). The learning pipeline may move these **within documented bounds**, but only after a candidate change passes the **safety suite at 100%** (see [`../docs/learning-pipeline/`](../docs/learning-pipeline/)).
- **Reference targets** are measured on the metrics dashboards; they are goals, not switches the engine reads.

Every row below is tagged `[Immutable]`, `[Soft]`, or `[Target]`.

## Relationship to `agent_config.json`

`agent_config.json` is the **runtime source of truth** the demo parses on start-up (`src/nexbank_agent/config.py`). This Markdown file is the **documentation source of truth** that explains and defends those same values. They are kept in lockstep. If the two ever disagree, `agent_config.json` governs the running demo and this document must be corrected to match — never the reverse. Immutable hard-safety rules are deliberately **absent** from the JSON: they are code, not configuration, so they cannot be edited by changing a file.

---

## 1. Identity & persona

JSON path: `persona`.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `persona.name` | `NEXA` | [Immutable] | Agent must always self-identify as NEXA; never role-play another identity (anti-jailbreak). |
| `persona.full_name` | `NexBank Expert Assistant` | [Soft] | Wording only. |
| `persona.voice` | `friendly, trustworthy, modern` | [Soft] | Tone target; phrasing is learnable, never at the expense of a safety rule. |
| `persona.languages` | `en`, `hinglish` | [Soft] | Supported input languages for the demo scope. |

## 2. NLU & intent confidence

JSON path: `nlu_confidence`. Referenced elsewhere as **`intent_confidence_threshold`** (see `../docs/intent-taxonomy/`), which maps to `secondary_min` below — the default gate for accepting a leaf intent.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `nlu_confidence.primary_min` | `0.60` | [Soft] | Below this on the top-level intent → clarify rather than act. |
| `nlu_confidence.secondary_min` (**`intent_confidence_threshold`**) | `0.70` | [Soft] | Default accept threshold for a specific intent. |
| `nlu_confidence.tertiary_min` | `0.75` | [Soft] | Finest-grained intents demand the highest confidence. |
| `nlu_confidence.margin_min` | `0.15` | [Soft] | Top-1 minus top-2 must clear this margin, else clarify — prevents confident-but-ambiguous misroutes. |

**Fallback ladder.** accept → clarify (max 2 targeted questions, see §4) → rule-based shortlist → escalate **ESC-004** (Capability, P2) after 3 consecutive low-confidence turns. ESC-004 — *not* the ESC-003 crisis lane — is the correct destination for "the bot cannot understand," so a merely confused customer is never routed into the duty-of-care protocol.

## 3. Knowledge retrieval

JSON path: `retrieval`. Design target is hybrid dense + sparse retrieval fused with Reciprocal Rank Fusion (RRF), then cross-encoder re-ranking.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `retrieval.w_dense` | `0.6` | [Soft] | Weight on the embedding retriever. |
| `retrieval.w_sparse` | `0.4` | [Soft] | Weight on BM25 (anchors exact tokens: IFSC, "Section 80C", product names). |
| `retrieval.top_k_candidates` | `20` | [Soft] | Candidate pool before re-rank; capped to hold the 200 ms budget. |
| `retrieval.top_k_return` (**`knowledge_retrieval_top_k`**) | `3` | [Soft] | Passages handed to generation. |
| `retrieval.rrf_k` | `60` | [Soft] | RRF constant; robust to score-scale differences between retrievers. |
| `retrieval.cross_encoder_rerank` | `true` | [Soft] | Re-rank the candidate set on top-20. |
| `retrieval.retrieval_confidence_threshold` | `0.45` | [Soft] | Below this fused score the system says "I don't know" and clarifies/deflects instead of guessing — the mechanism behind **0% fabricated facts**. |
| `retrieval.latency_budget_ms_p95` | `200` | [Target] | p95 retrieval budget; see §9. |

## 4. Dialogue control

JSON path: `dialogue`.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `dialogue.max_clarifications` | `2` | [Soft] | At most two targeted clarifying questions; the third low-confidence turn escalates (ESC-004). Bounds the "Robotic Loop" anti-pattern. |
| `dialogue.confirm_before_consequential` | `true` | [Immutable] | Any consequential action (e.g. card block) must be explicitly confirmed before it is taken. |

## 5. Authentication & session

JSON path: `authentication`. The ladder is compared by **rank**; each intent declares a minimum level and the gate proceeds only when `current_rank >= required_rank`.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `authentication.levels` | `anonymous` (0), `otp_verified` (1), `biometric_verified` (2), `full_kyc` (3) | [Immutable] | Order defines rank; the demo wires this directly. |
| `authentication.session_timeout_minutes` | `5` | [Immutable] | Idle sessions must re-authenticate before any account-specific action. |

Minimum levels per action class: public info (product facts, rates, EMI math) → `anonymous`; balance / transactions / card block → `otp_verified`; profile / mobile-email change / limit increase → `full_kyc`. Auth gating is a hard rule: no learned policy can lower a required level.

## 6. Escalation

JSON path: `escalation`. Full trigger catalogue in [`../docs/escalation/`](../docs/escalation/).

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `escalation.proximity_threshold` | `0.7` | [Soft] | Soft escalation fires when the `escalation_proximity` score crosses this. |
| `escalation.frustration_sentiment_threshold` | `-0.5` | [Soft] | Sustained sentiment below this contributes to proximity (feeds ESC-007). |
| `escalation.hard_triggers` | `ESC-001, 003, 005, 008, 009, 010, 011, 013, 014, 015` (10) | [Immutable] | Fire immediately on detection, ignore the score, cannot be suppressed by learning. |
| `escalation.soft_triggers` | `ESC-002, 004, 006, 007, 012` (5) | [Soft] | Accumulate via the proximity score; tunable within bounds. |

10 of the 15 triggers are hard — the safety-, rights-, and regulation-driven ones. Note **ESC-003 = customer distress / crisis (P0, duty-of-care)** and **ESC-004 = repeated NLU failure (P2, capability)**; they are distinct and must not be conflated.

## 7. Safety & guardrails

JSON path: `safety`. **These entries are detection *support* only.** The actual blocks are immutable code at C6; the lexicons make the demo's detection transparent and auditable for the viva, and are deliberately conservative.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `safety.guardrail_strictness_level` | `HIGH` | [Immutable] | Fixed posture: all hard rules always on. "Strictness" tuning applies only to *soft* thresholds; the hard floor never moves. Change requires RC approval. |
| `safety.max_input_chars` | `1200` | [Soft] | Over-length input is truncated + throttled (`dos_mitigated`), never crashed. |
| `safety.advice_lexicon` | list | [Soft] | First-pass signal for the advice guardrail; the *block* itself is rule-based and immutable. |
| `safety.personal_signal_lexicon` | list | [Soft] | Personalisation signals that turn an info request into an advice request. |
| `safety.injection_lexicon` | list | [Soft] | Prompt-injection detection support. |
| `safety.jailbreak_lexicon` | list | [Soft] | Role-play / "safety off" detection support. |
| `safety.exfil_lexicon` | list | [Soft] | System-prompt / training-data exfiltration detection support. |
| `safety.social_eng_lexicon` | list | [Soft] | Authority-impersonation detection support. |
| `safety.credential_lexicon` | list | [Soft] | Detects volunteered secrets so they are refused and never stored. |
| `safety.money_move_lexicon` | list | [Soft] | Detects money-movement requests → guide only, never transact. |
| `safety.cross_customer_lexicon` | list | [Soft] | Detects third-party-account access attempts. |
| `safety.aml_structuring_lexicon` | list | [Soft] | Detects structuring/evasion → refuse + AML flag. |
| `safety.pep_lexicon` | list | [Soft] | Detects PEP self-identification → enhanced due diligence (ESC-015). |

Growing a lexicon (catching *more*) is a soft change; it can never *shrink* a hard block. The advice, PII, cross-customer, money-movement, AML, and PEP **decisions** are immutable regardless of what any lexicon says.

## 8. Performance & latency budget

JSON path: `targets` (+ `retrieval.latency_budget_ms_p95`).

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `retrieval.latency_budget_ms_p95` | `200 ms` | [Target] | Retrieval stage p95. |
| `targets.technical_p95_seconds_max` | `3 s` | [Target] | End-to-end technical p95 (design estimate ≈ 2.6 s). |
| `targets.first_response_seconds_max` | `30 s` | [Target] | Business SLA for first reply — ~10× headroom over technical p95. |

## 9. Reference targets (business KPIs)

JSON path: `targets`. Measured on the dashboards in [`../docs/metrics/`](../docs/metrics/); the engine does not read these.

| Parameter | Value | Class | Notes |
|---|---|---|---|
| `targets.containment_min` | `0.70` | [Target] | ≥70% of interactions resolved without human handoff. |
| `targets.csat_min` | `4.5` | [Target] | Customer satisfaction floor. |
| `targets.incorrect_advice_max` | `0.0` | [Target] | **Zero** personalised financial advice reaching a customer — the hard invariant the whole design protects. |

## 10. What the offline demo actually wires

The runnable demo in `src/nexbank_agent/` is a **deterministic, stdlib-only reference**, not the production system. To keep it honest about scope, here is exactly what it consumes from `agent_config.json`:

- **Actively wired:** `authentication.levels` (drives the auth-rank gate) and the whole `safety.*` block (`max_input_chars` + the detection lexicons, via `safety_cfg(...)`).
- **Documented but simplified:** `retrieval.*` — the demo uses a small keyword/TF-IDF match rather than the full hybrid+RRF+cross-encoder pipeline, so `w_dense/w_sparse/rrf_k/cross_encoder_rerank/retrieval_confidence_threshold` describe the *design*, not the demo's runtime. A known consequence is that the keyword matcher can over-match a genuinely out-of-scope query to a keyword-adjacent KB fact; the production `retrieval_confidence_threshold` is the control that prevents this, and is specified here for that reason.
- **Design-level:** `nlu_confidence.*` (beyond the primary/margin defaults), `escalation.*` scoring, and all `targets.*` describe production behaviour and are measured/observed rather than enforced by the minimal demo.

This separation is intentional: it lets the demo prove the **safety** behaviours end-to-end (which are the graded invariants) without pretending to ship a full ML retrieval stack.

## 11. Change control

| Class | Who can change it | Gate |
|---|---|---|
| [Immutable] | Risk Committee only, via code review | Full re-validation; version bump |
| [Soft] | Learning pipeline (or engineer), within documented bounds | **Safety suite 100% pass** + canary + auto-rollback |
| [Target] | Product / Risk, as goals evolve | Dashboard + governance review |

Any change to this file must be mirrored in `agent_config.json` (and vice-versa) in the same commit, with the rationale recorded in [`../CHANGELOG.md`](../CHANGELOG.md). Current config version: **1.1**.
