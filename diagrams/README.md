# NEXA — System Diagrams

Six diagrams that describe the NexBank customer-service agent (**NEXA**). They are written
in [Mermaid](https://mermaid.js.org/) so they render directly on GitHub and stay in version
control alongside the code. Each `.mermaid` source file in this folder is embedded below.

The diagrams are intentionally consistent with the runnable demo in `src/nexbank_agent/`:
diagram **02** mirrors the ordered checks in `engine.py`, **06** mirrors the auth-rank gate,
and **05** mirrors the safety-gated learning pipeline described in `docs/learning-pipeline.md`.

## Contents

1. [System architecture](#1-system-architecture) — end-to-end request flow
2. [Guardrail pipeline](#2-guardrail-pipeline) — the ordered safety checks
3. [Dialogue state machine](#3-dialogue-state-machine) — conversation lifecycle
4. [Escalation routing](#4-escalation-routing) — triggers → priority → human queue
5. [Learning loop](#5-learning-loop) — how the system improves without weakening safety
6. [Authentication ladder](#6-authentication-ladder) — levels and the step-up gate

---

## 1. System architecture

End-to-end path of a single message. Safety is enforced at three chokepoints (C2 input,
C6 immutable, C10 output). The learning loop can tune *soft* policy but is **blocked by
design** from altering the immutable C6 layer.

```mermaid
flowchart TB
    subgraph CH[Customer Channels]
        A1[App chat]
        A2[Web widget]
        A3[WhatsApp]
        A4[Voice / IVR]
    end

    CH --> ORC[Orchestrator]
    ORC --> C2{{C2 - Input Safety}}
    C2 -->|attack detected| C6
    C2 -->|clean| NLU[NLU - intent, entities, sentiment]

    NLU --> DSM[Dialogue State Manager]
    DSM --> POL[Dialogue Policy]
    POL --> AUTH{Auth level sufficient?}
    AUTH -->|no| STEP[Step-up authentication]
    AUTH -->|yes| RET[Hybrid Retrieval]
    RET --> KB[(Knowledge Base - structured facts)]
    RET --> GEN[Template-first Generation]

    GEN --> C6{{C6 - Immutable Safety Layer}}
    STEP --> C6
    C6 -->|hard trigger| ESC[Escalate to human]
    C6 -->|safe| C10{{C10 - Output Safety}}
    C10 --> RESP[Response to customer]

    RESP --> AUD[(Audit Log - masked at source)]
    ESC --> AUD
    AUD --> LRN[Continuous Learning]

    LRN -.->|tunes soft policy only| POL
    LRN -.->|blocked by design - cannot alter| C6
```

---

## 2. Guardrail pipeline

The ordered decision chain implemented in `engine.evaluate()`. Safety checks run **before**
any capability, and the order matters: exfiltration/injection/jailbreak are caught before
the advice check so an attack is never mislabelled as a product question.

```mermaid
flowchart TD
    IN[User message] --> D0{Oversize or flood?}
    D0 -->|yes| DOS[Throttle + clarify · dos_mitigated]
    D0 -->|no| D1{Data exfiltration?}
    D1 -->|yes| RXF[Refuse · exfiltration_blocked]
    D1 -->|no| D2{Prompt injection?}
    D2 -->|yes| RIJ[Stay NEXA · injection_detected]
    D2 -->|no| D3{Jailbreak / role-play?}
    D3 -->|yes| RJB[Hold the line · jailbreak_detected]
    D3 -->|no| D4{Social engineering?}
    D4 -->|yes| RSE[Refuse access · social_engineering_detected]
    D4 -->|no| D5{Volunteered credential?}
    D5 -->|yes| RCR[Warn + do not store · credential_refused]
    D5 -->|no| D6{Fraud or crisis?}
    D6 -->|yes| ESC[Hard escalation · ESC-001 / ESC-003]
    D6 -->|no| D7{PII disclosure request?}
    D7 -->|yes| RPII[Last-4 only · pii_protected]
    D7 -->|no| D8{Money movement?}
    D8 -->|yes| RMON[Guide, never move · money_refused]
    D8 -->|no| D9{Cross-customer access?}
    D9 -->|yes| RXC[Own account only · cross_customer_refused]
    D9 -->|no| D10{Regulated? AML / PEP / UPI / loan / grievance}
    D10 -->|yes| RREG[Regulated response + flag]
    D10 -->|no| D11{Financial advice?}
    D11 -->|yes| RADV[Facts + advisor, no rec · advice_blocked]
    D11 -->|no| INT[Classify intent]

    INT --> AU{Auth sufficient and fresh?}
    AU -->|no| STEP[Step-up / re-auth · auth_required]
    AU -->|yes| SERVE[Answer from KB facts · masked]

    classDef refuse fill:#fde8e8,stroke:#c0392b,color:#7b241c;
    classDef ok fill:#e8f8ef,stroke:#1e8449,color:#145a32;
    class DOS,RXF,RIJ,RJB,RSE,RCR,RPII,RMON,RXC,RREG,RADV,ESC,STEP refuse;
    class SERVE ok;
```

---

## 3. Dialogue state machine

The lifecycle of a conversation. Any hard trigger (fraud, crisis, disallowed advice,
grievance) can move the dialogue straight to escalation from either understanding or
fulfilment.

```mermaid
stateDiagram-v2
    [*] --> Greeting
    Greeting --> Understanding: customer states need
    Understanding --> Authenticating: account-specific action
    Understanding --> Fulfilling: public info / product fact
    Understanding --> Clarifying: low confidence
    Clarifying --> Understanding: reformulated
    Clarifying --> Escalation: max clarifications reached
    Authenticating --> Fulfilling: identity verified
    Authenticating --> Escalation: repeated auth failure
    Fulfilling --> Confirming: action / answer delivered
    Confirming --> Understanding: another request
    Confirming --> Closing: nothing further
    Understanding --> Escalation: hard trigger (fraud, crisis, advice, grievance)
    Fulfilling --> Escalation: hard trigger
    Escalation --> Closing: handed off with context package
    Closing --> [*]
```

---

## 4. Escalation routing

How a trigger is mapped to a priority and routed to the right human queue. Every handoff
carries a **masked context package** so the customer never has to repeat themselves and no
raw PII crosses the boundary.

```mermaid
flowchart LR
    subgraph T[Escalation triggers]
        F[Fraud / stolen card]
        CR[Self-harm / crisis]
        HR[Explicit human request]
        GRV[Grievance / complaint]
        REG[Advice / loan / PEP / AML]
        KBF[KB stale or missing]
        SENT[High frustration / repeat contact]
    end

    F --> P0[P0 - immediate]
    CR --> P0
    HR --> P1[P1 - priority]
    GRV --> P1
    REG --> P1
    KBF --> P2[P2 - standard]
    SENT --> P2

    P0 --> SEC[Security / fraud desk]
    P1 --> SPEC[Specialist / compliance / relationship team]
    P2 --> GENQ[General support queue]

    SEC --> PKG[Handoff package - masked context, intent, history, reason]
    SPEC --> PKG
    GENQ --> PKG
```

---

## 5. Learning loop

The system improves continuously, but every candidate change must pass the **full safety
suite at 100%** before it can ship, then go through canary + automatic rollback. The
immutable hard-safety rules are explicitly **out of scope** for learning — that is the
central design commitment: learning can tune soft policy but can never weaken hard safety.

```mermaid
flowchart LR
    subgraph LIVE[Runtime]
        INT[Interactions] --> AUD[(Audit log - masked)]
        AUD --> SIG[Signal mining - CSAT, containment, fallbacks, corrections]
    end

    SIG --> CAND[Candidate change - policy weights, templates, KB facts, NLU examples]
    CAND --> REV{Human review + sign-off}
    REV -->|rejected| ARCH[Archive with reason]
    REV -->|approved| GATE{{Safety suite - 100 percent must pass}}

    GATE -->|any fail| BLOCK[Blocked - cannot ship]
    GATE -->|all pass| CAN[Canary - small traffic slice]
    CAN --> MON{Metrics healthy?}
    MON -->|regressed| RB[Auto rollback]
    MON -->|healthy| PROMO[Promote to 100 percent]
    PROMO --> VER[Versioned release + changelog]

    RB --> ARCH
    BLOCK --> ARCH

    NOTE[Immutable hard-safety rules are out of scope for learning] -.-> GATE

    classDef stop fill:#fde8e8,stroke:#c0392b,color:#7b241c;
    classDef go fill:#e8f8ef,stroke:#1e8449,color:#145a32;
    class BLOCK,RB stop;
    class PROMO,VER go;
```

---

## 6. Authentication ladder

Four levels compared by **rank**. Each intent maps to a minimum required level; the gate
proceeds only when the current rank meets or exceeds it and the session has not idle-timed-out.

```mermaid
flowchart TD
    subgraph LADDER[Authentication levels - compared by rank]
        L0[anonymous · rank 0]
        L1[otp_verified · rank 1]
        L2[biometric_verified · rank 2]
        L3[full_kyc · rank 3]
        L0 --> L1 --> L2 --> L3
    end

    subgraph NEEDS[Minimum level per action]
        N0[Public info - product facts, rates, EMI math → anonymous]
        N1[Account balance, transactions, card block → otp_verified]
        N3[Profile change, mobile / email update, limit increase → full_kyc]
    end

    REQ[Incoming request] --> MAP[Map intent to required level]
    MAP --> CMP{current rank ≥ required rank?}
    CMP -->|yes, and not expired| SERVE[Proceed to fulfilment]
    CMP -->|no| STEP[Step-up authentication · auth_required]
    CMP -->|session idle-timed-out| REAUTH[Re-authenticate · timeout]

    classDef ok fill:#e8f8ef,stroke:#1e8449,color:#145a32;
    classDef refuse fill:#fde8e8,stroke:#c0392b,color:#7b241c;
    class SERVE ok;
    class STEP,REAUTH refuse;
```
