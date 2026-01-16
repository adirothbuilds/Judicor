# Judicor – End‑to‑End Roadmap (Hackathon‑Ready)

## Goal of This Document

This document defines the **complete, concrete, end‑to‑end roadmap** for Judicor,
from its current working prototype to a **submission‑ready hackathon product**.

It is written to:
- Be consumed by **Codex during development**
- Be readable by **hackathon judges**
- Translate vision → architecture → tasks
- Break work into **small, executable steps**

The ultimate goal is to **fully align with Gemini / agent‑centric hackathon requirements**:
- Real AI usage (not a wrapper)
- Clear agent roles
- Deterministic and auditable reasoning
- Runnable and testable by reviewers

---

## 1. What Judicor Is (One‑Paragraph Pitch)

Judicor is an **AI‑assisted incident judgment engine** for DevOps and SRE teams.
It embeds a **read‑only AI agent** into the full lifecycle of a production incident —
from initial detection, through investigation, to resolution and post‑mortem.

The AI does not mutate systems.
Instead, it reasons over **incident context, system signals, and historical data**,
helping humans reach faster, safer decisions.

---

## 2. Core Design Principles

These principles must never be violated during implementation:

1. **Human‑in‑the‑loop**
2. **AI is read‑only**
3. **Policy‑gated outputs**
4. **Deterministic demo behavior**
5. **Auditable reasoning**
6. **Clear separation of concerns**
7. **CLI‑first, control‑plane backed**

---

## 3. Current State (Baseline – Already Implemented)

✔ Typer‑based CLI  
✔ Local identity initialization (`judicor init`)  
✔ Secure identity storage under `~/.judicor`  
✔ Local session persistence (attached incident)  
✔ Client abstraction with dummy implementation  
✔ AI abstraction with dummy + Gemini  
✔ Gemini integration using `google‑genai`  
✔ AI policy enforcement (confidence threshold)  
✔ Control‑plane placeholder (FastAPI)  
✔ Dockerfiles (CLI + control plane)  
✔ Makefile orchestration  
✔ ~80% automated test coverage  

This baseline is **intentionally minimal but correct**.

---

## 4. Target End State (Hackathon Submission)

By submission time, Judicor must demonstrate:

- A **real AI agent**, not a chat wrapper
- Multiple AI roles across incident lifecycle
- Realistic incident flow
- Ability for judges to:
  - Run locally
  - Trigger incidents
  - Ask questions
  - Observe reasoning
  - See resolution output

---

## 5. Incident Lifecycle Model (Canonical)

Every incident follows this lifecycle:

```
CREATED
  ↓
ACTIVE
  ↓
INVESTIGATING
  ↓
RESOLVED
  ↓
ARCHIVED
```

Each transition is **explicit**, **logged**, and **auditable**.

---

## 6. AI as an Agent (Not Chat)

AI participates as **multiple role‑based agents**.

### Core Agent Roles

| Role | Responsibility |
|----|---------------|
| Analyzer | Initial understanding of the incident |
| Investigator | Answer questions using live context |
| Summarizer | Maintain rolling incident summary |
| Resolver | Generate closure reasoning & report |

Each role has:
- A dedicated prompt
- A bounded responsibility
- Policy enforcement

---

## 7. High‑Level Architecture

```
User
 └─ CLI (Typer)
     └─ Client
         ├─ Identity
         ├─ Session Store
         ├─ Incident State
         ├─ AI Factory
         │    ├─ Gemini
         │    └─ Dummy
         ├─ Policy Engine
         └─ Control Plane (HTTP)

Control Plane
 ├─ Incident Store
 ├─ Timeline Store
 ├─ Integration Adapters (read‑only)
 └─ Auth / Ownership
```

---

## 8. Roadmap by Phases (End‑to‑End)

### Phase 1 — Incident Domain Hardening

**Goal:** Make incidents first‑class, explicit, and deterministic.

Tasks:
- [x] Define incident state enum
- [x] Enforce legal state transitions
- [x] Add incident timeline (events)
- [x] Persist timeline locally (initially)
- [x] Add timestamps to all transitions
- [x] Add tests for state machine

Status: **Completed**

---

### Phase 2 — Session & Context Management

**Goal:** Every AI call is grounded in current incident context.

Tasks:
- [x] Extend session store:
  - attached_incident_id
  - last_activity
- [x] Load incident context on client init (dummy client)
- [x] Fail fast if context is missing (CLI exits non‑zero)
- [x] Add CLI command: `judicor context`
- [x] Tests for session recovery

Status: **Completed**

---

### Phase 3 — AI Agent Matrix (Critical Phase)

**Goal:** Turn AI into lifecycle agents.

Tasks:
- [x] Introduce `AgentRole` enum
- [x] Refactor `ai.factory` to accept `(provider, role)`
- [x] Split prompt building per role
- [ ] Create prompt templates per lifecycle stage
- [x] Store conversation history per incident (history store + summaries)
- [x] Feed rolling summary into next prompts
- [ ] Enforce read‑only guarantees
- [ ] Add policy per role (different thresholds)
- [ ] Tests for each role

Status: **In progress** — need per‑stage templates, read‑only guardrails, per‑role policies, and role tests.

---

### Phase 4 — Control Plane (Real Backend)

**Goal:** Centralize incidents and support multi‑user access.

Tasks:
- [x] Implement FastAPI endpoints:
  - Create incident
  - Get incident
  - Append timeline event
  - Resolve incident
- [ ] Bind identity → session → incident
- [x] Token‑based auth (simple)
- [x] Server‑side incident store (in‑memory or file)
- [x] Health endpoint (readiness pending)
- [x] Tests for API layer

Status: **Mostly done** — identity binding and readiness endpoint still pending.

---

### Phase 5 — Integrations (Read‑Only Signals)

**Goal:** Show real‑world reasoning inputs.

Tasks:
- Define `Integration` interface
- Create fake vendor integration:
  - Metrics (CPU, latency, errors)
  - Logs (sample)
- Allow AI to query integrations via tools
- Inject integration snapshots into prompts
- CLI command: `judicor integrations list`
- Tests for integration adapters

---

### Phase 6 — Resolution & Knowledge Capture

**Goal:** Close the loop.

Tasks:
- Resolver agent generates:
  - Root cause
  - Resolution steps
  - Confidence
- Persist closure report
- Generate post‑mortem summary
- Prepare ticket payload (mock)
- Feed closed incidents as future context
- Tests for resolution output

---

### Phase 7 — Demo & Submission Hardening

**Goal:** Make judges love it.

Tasks:
- Seed demo data
- Create demo script
- Freeze deterministic outputs
- Finalize README
- Add architecture diagram
- Ensure `docker run` works
- Ensure `make demo` works

---

## 9. Demo Narrative (What Judges Experience)

1. Initialize identity
2. Trigger incident
3. AI analyzes incident
4. User attaches
5. User asks investigation questions
6. AI reasons with confidence
7. Incident is resolved
8. AI produces closure summary

Total demo time: **5–7 minutes**

---

## 10. Why This Will Score High

Judicor aligns strongly with hackathon expectations because it:

- Uses Gemini as a **real agent**
- Demonstrates **multi‑stage reasoning**
- Avoids hallucination via policy
- Is runnable, testable, auditable
- Solves a real SRE problem

---

## 11. Final Success Criteria

✔ Judges can run it locally  
✔ AI shows reasoning quality  
✔ Architecture is clear  
✔ Scope is ambitious but controlled  
✔ Product tells a complete story  

---

## Status

Current state: **Strong foundation**  
Next step: **Phase 1 execution**  
