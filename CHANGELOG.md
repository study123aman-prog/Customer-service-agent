# CHANGELOG — NexBank NEXA (Project 463548C)

Development log for the 15-day methodology. Each entry records tasks completed, key design decisions and their rationale, challenges, open questions, and the plan for the next day.

Format: dates are the working sessions leading to submission. All work by Aman Singh; AI assistance per the policy noted in `README.md`.

---

## Day 1 — 2026-08-07 · Scenario immersion & stakeholder analysis

**Completed**
- Read all six parts of the brief and annotated requirements; extracted the 7 core deliverables and the mandatory repo structure.
- Analysed the 500-transcript data package (10 categories). Noted the hardest segments: Complaint/Escalation (11.3 turns, 58% resolution, 2.4 CSAT, CRITICAL) and Transaction Dispute (8.7 turns, 67%, 2.8 CSAT, HIGH).
- Mapped CEB vs RC concerns into a single tension the architecture must resolve.

**Decisions & rationale**
- Adopt a **capability core wrapped by an immutable rule-based safety layer**. Rationale: the RC's "0% incorrect advice" is a hard invariant that cannot be left to a probabilistic model; separating it lets us improve the learned components freely without touching safety.
- Name the agent **NEXA** and fix the persona early so tone is consistent across every deliverable.

**Challenges** — Reconciling "sub-200ms retrieval" with "<3s end-to-end" once LLM generation is included; parked for the latency-budget task.

**Open questions** — Exact channel mix (chat/voice/WhatsApp/app) weighting; assumed chat-first, voice via STT/TTS adapters.

**Next** — High-level architecture and component decomposition.

---

## Day 2 — 2026-08-08 · High-level architecture

**Completed**
- Decomposed the system into 14 components with clear responsibilities and interfaces.
- Drafted the request lifecycle (ingress → safety → NLU → dialogue → retrieval/generation → output safety → egress) with the immutable safety layer consulted at each step.

**Decisions & rationale**
- **Two guardrail chokepoints** (input safety before NLU, output safety before egress) rather than a single pass. Rationale: prompt injection must be caught pre-reasoning; hallucination/PII leaks must be caught post-generation.
- **Template-first generation for safety-critical content** (balances, rates, regulatory text); LLM only for empathy/clarification. Rationale: eliminates a whole class of hallucination risk on numbers.

**Challenges** — Deciding where authentication sits; placed it as a service the dialogue policy calls, so auth level gates actions rather than blocking the whole turn.

**Open questions** — State store technology (assumed Redis for hot state + durable log store).

**Next** — Dialogue state machine, interface contracts, failure modes, latency budget, scalability.

---

## Day 3 — 2026-08-09 · Dialogue state machine & non-functional design

**Completed**
- Full dialogue state schema (intent + alternatives, slot status, 20-turn history, sentiment trajectory, auth level, guardrail state, escalation-proximity score, context carry-over).
- State machine with 9 states and guarded transitions; action space of 8 actions.
- Component interface contracts (I/O per component), failure-mode table with fallbacks, end-to-end latency budget (p95 ≈ 2.6s), and 1x/10x/100x scalability plan.

**Decisions & rationale**
- **Escalation-proximity score** as a first-class state field updated every turn. Rationale: makes "graceful degradation before failure" measurable and lets escalation be proactive, not reactive.
- Fallback for every component defaults toward **safe human escalation**, satisfying the RC's fail-safe requirement.

**Challenges** — Context-window overflow on 25+ turn conversations; resolved with a sliding window + priority retention of auth state, open actions, and safety flags.

**Open questions** — None blocking.

**Next** — Intent taxonomy (primary/secondary/tertiary) and NLU pipeline.

---

## Day 4 — 2026-08-10 · Intent taxonomy structure

**Completed** — Designed the primary (6) → secondary → tertiary hierarchy; enumerated 32 leaf intents across Account, Transaction, Card, Product, Complaint, Security, plus general/OOS. Assigned auth level and safety rating to each.

**Decisions & rationale** — Went to **32 intents (>25 minimum, >30 for the "Linguist" badge)** but stopped there to keep the taxonomy defensible and the disambiguation tractable. Each intent carries required/optional slots up front so slot-filling is derivable directly from the taxonomy.

**Challenges** — Avoiding overlap between `PRD-001 Product Info` and `PRD-005 Investment Advisory`; solved by making the *advice* boundary an intent property, not just a guardrail.

**Open questions** — None.

**Next** — Entity model, validation rules, sample utterances.

---

## Day 5 — 2026-08-11 · Entities, slot-filling, utterances

**Completed** — Entity type catalogue with extraction method, validation (Luhn for card, PAN/Aadhaar regex, IFSC, UPI handle), and sensitivity tags; slot-filling policy; 250+ sample utterances (≥10/intent) including Hinglish variants.

**Decisions & rationale** — **Never accept full Aadhaar/CVV/PIN** at the entity layer (reject + educate), so PII minimisation is enforced before any model sees the value.

**Challenges** — Hinglish entity extraction (amounts written "do hazaar paanch sau"); documented a normalisation step, kept numerals as the demo scope.

**Next** — Disambiguation, multi-intent, out-of-scope.

---

## Day 6 — 2026-08-12 · Disambiguation & NLU robustness

**Completed** — Decision trees for all 6 confusable intent pairs; multi-intent handling; out-of-scope detection; per-layer confidence thresholds and fallback ladder.

**Decisions & rationale** — Disambiguation uses **clarifying-question sequences gated by confidence margin** (top-1 minus top-2), not just absolute confidence — this reduces the "robotic loop" anti-pattern.

**Challenges** — `SEC-001 fraud` vs `TXN-002 dispute` reclassification mid-conversation; documented a re-classification trigger on strong fraud lexicon + sentiment drop (mirrors Case Study 2).

**Next** — Knowledge base schema and entries.

---

## Day 7 — 2026-08-13 · Knowledge base schema & content

**Completed** — KB entity-relationship schema; 61 sample entries across product/policy/regulatory/FAQ/troubleshooting/escalation; regulatory tagging with TTL and compliance metadata; access-control-by-auth-level matrix.

**Decisions & rationale** — Every KB entry carries a **`freshness_ttl` and `regulatory_tag`**; expired regulatory entries hard-block generation (fail-closed) rather than serving stale rates. Rationale: KB staleness is a P0 risk in A11.

**Next** — Retrieval pipeline and maintenance workflow.

---

## Day 8 — 2026-08-14 · Retrieval pipeline

**Completed** — Hybrid retrieval (dense + BM25) with fusion weights, cross-encoder re-ranking, contextual query rewriting, confidence + uncertainty threshold, sub-200ms p95 budget, graceful "I don't know" fallback; knowledge-update workflow with approval chain + rollback.

**Decisions & rationale** — **Hybrid over pure dense**: banking queries mix exact tokens (IFSC, product names, section 80C) with semantic phrasing; BM25 anchors the exact tokens, embeddings catch paraphrase. Re-ranking budgeted at 40ms on top-20.

**Challenges** — Hitting 200ms with a cross-encoder; capped candidate set at 20 and cache hot entries.

**Next** — Guardrails: financial advice + security.

---

## Day 9 — 2026-08-15 · Financial-advice & security guardrails

**Completed** — Full information-vs-advice matrix; the 8 mandatory security rules with implementation detail; PII masking spec; session-timeout and re-auth rules.

**Decisions & rationale** — Advice detection is **layered** (lexical trigger → intent → LLM classifier → deterministic block), and the final block is rule-based so the learning pipeline can never soften it.

**Next** — Adversarial vectors + 50+ test cases.

---

## Day 10 — 2026-08-16 · Adversarial robustness & test suite

**Completed** — Defences for all 6 attack vectors; an initial set of adversarial/safety test cases (expanded to 62 during hardening) as structured data + a runnable pytest harness; false-positive analysis; guardrail monitoring dashboard; incident-response playbook.

**Decisions & rationale** — Test cases are **data-driven** (YAML) so they double as documentation *and* regression tests for the demo and any future model update (feeds the safety-invariant suite in L5).

**Challenges** — Balancing strictness vs the <3% guardrail false-positive target; tuned lexical triggers to require corroborating signals.

**Next** — Continuous-learning pipeline.

---

## Day 11 — 2026-08-17 · Continuous-learning pipeline

**Completed** — Supervisor-correction loop (sampling, taxonomy, propagation SLAs), CSAT signal integration, resolution-outcome tracking, data pipeline, model-update strategy, safety-preserving protocol (canary → 1/5/25/100% rollout, circuit breaker), A/B framework, immutable safety layer.

**Decisions & rationale** — **Safety test suite (200+ cases) is a hard gate**: no model version ships unless it passes 100%. Rationale: the RC's zero-regression requirement. Style/quality improvements are batched; safety corrections propagate immediately.

**Next** — Escalation routing.

---

## Day 12 — 2026-08-18 · Escalation & routing

**Completed** — 15 triggers with priority (P0/P1/P2), target queue, and SLA; routing decision logic; 8-element handoff context package; queue overflow/after-hours/priority-rebalancing; escalation-quality metrics + de-escalation logic.

**Decisions & rationale** — Escalation is driven by the **escalation-proximity score** plus hard triggers; hard triggers (fraud, self-harm, AML, PEP) bypass all scoring and fire immediately.

**Next** — Metrics, dashboards, system prompt, templates.

---

## Day 13 — 2026-08-19 · Metrics, dashboards & prompt architecture

**Completed** — Leading/lagging/operational metric definitions with targets and cadence; Detect→Diagnose→Design→Deploy→Validate→Document cycle; 3 dashboard specs with wireframes; 6-layer system-prompt spec with immutability rules; 16 prompt templates with triggers + safety annotations; configuration-parameter table.

**Decisions & rationale** — **Layers 0–2 of the system prompt are immutable by the learning pipeline** (only Layer 5 changes without RC review), mirroring the runtime immutable safety layer so the "un-learnable safety" principle holds at both prompt and code level.

**Next** — Sample conversations, audit logging, risk matrix, demo.

---

## Day 14 — 2026-08-20 · Conversations, logging, risk, demo build

**Completed** — 30 annotated sample conversations (all intent groups, guardrail activations, escalations, sentiment recovery, Hinglish, adversarial); interaction- and turn-level audit-logging schemas; technical/business/ethical risk matrices; built the offline Python reference demo and wired the 62 test cases into pytest.

**Decisions & rationale** — Each conversation is annotated with intent+confidence, entities, guardrails, and decision points so it doubles as a **test oracle** for the demo. Verified none of the 8 anti-patterns appear.

**Challenges** — Keeping the demo dependency-free while still showing hybrid retrieval; implemented a tiny TF-IDF in stdlib.

**Next** — Integration verification and submission.

---

## Day 15 — 2026-08-21 · Integration, verification & submission

**Completed**
- End-to-end integration check: ran the demo across all case-study scenarios; guardrail suite green.
- Verified minimum counts (32 intents, 61 KB entries, 62 test cases, 30 conversations, 15 escalation triggers) and checked the deliverable against the 10 automatic-failure conditions.
- Cross-reference validation across documents; README navigation finalised.
- Repository prepared for transfer to `@ZethetaIntern`.

**Decisions & rationale** — Final polish favoured cross-document coherence (single source of truth for thresholds in `config/configuration-parameters.md`) to avoid contradictions flagged in the Coherence scoring dimension.

**Open questions / future work** — Voice channel STT/TTS latency validation; multilingual coverage beyond Hindi/Hinglish; live load test at 10k concurrent sessions.

**Status:** Complete and submitted.
