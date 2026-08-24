# Development Plan & Roadmap
## Ledger — AI Finance Controller Agent

**Version:** 1.0
**Principle:** Sequenced so development can start immediately with no open decisions blocking any phase.

---

## 1. Overview

This plan converts the PRD, SRS, Architecture, and UI/UX documents into an executable build sequence. It assumes a small team (1–3 builders) working toward a buildathon submission (public GitHub repo, working demo, pitch video). Phases are ordered by dependency, not just by "logical" grouping — nothing is scheduled before what it depends on is ready.

**Total estimated build time:** ~10–14 focused working days for a polished MVP (compressible to a few intense days if the team is experienced and scope is held firmly to Section 6 of the PRD).

---

## 2. Priority Legend

- **P0** — Must exist for the product to function at all / demo to work. Non-negotiable.
- **P1** — Strongly improves the demo/judging experience. Build if time allows after all P0 is done.
- **P2** — Nice-to-have polish. Only touch after P0 and P1 are both solid.

---

## 3. Phase Breakdown

### Phase 0 — Setup (Day 1)
**Goal:** A running skeleton, not features.

- [ ] P0: Initialize repo structure (backend/, frontend/, docs/), commit all 5 planning documents into `/docs`.
- [ ] P0: Set up FastAPI backend skeleton with health-check endpoint.
- [ ] P0: Set up React + Tailwind frontend skeleton with a placeholder login page.
- [ ] P0: Set up PostgreSQL (or SQLite for local dev) and connect it to the backend.
- [ ] P0: Define and migrate the core schema (User, ReconciliationRun, Transaction, Flag, AuditLogEntry).
- [ ] P0: Set up environment variable handling for secrets (DB URL, Claude API key, JWT secret).
- [ ] P1: Set up Docker Compose for local backend + DB.

**Dependencies:** None — this is the starting point.
**Definition of Done:** Backend and frontend both run locally, connected to a live database, with an empty but functioning schema.

---

### Phase 1 — Authentication (Day 1–2)
**Goal:** Every subsequent feature can assume "who is this user."

- [ ] P0: Implement `/auth/login` (email/password, JWT issuance).
- [ ] P0: Implement auth middleware (token validation on protected routes).
- [ ] P0: Seed at least one Analyst user and one Admin user for demo purposes.
- [ ] P1: Implement session expiry handling and clean 401 responses on the frontend.

**Dependencies:** Phase 0 schema (User table).
**Definition of Done:** A user can log in via the frontend and reach an authenticated dashboard shell; unauthenticated requests are rejected.

---

### Phase 2 — Ingestion (Day 2–3)
**Goal:** Get real data into the system, safely.

- [ ] P0: Build `/reconciliation/runs` (POST) — accepts two CSV files, validates schema/rows per SRS Section 6.
- [ ] P0: Implement row-level and file-level validation errors (FR-5, V-1 through V-5).
- [ ] P0: Persist raw transactions tagged by source and run.
- [ ] P0: Build frontend Upload screen (FileDropZone component, inline validation feedback).
- [ ] P1: Add a small synthetic/sample dataset generator script for demo purposes (clean data + seeded anomalies).

**Dependencies:** Phase 1 (auth — uploads are tied to a user).
**Definition of Done:** A user can upload two valid CSVs and see them persisted; a malformed file produces a specific, correct error message (per EC-1–EC-6).

---

### Phase 3 — Reconciliation Engine (Day 3–5)
**Goal:** The deterministic core of the product — this is what everything else depends on being correct.

- [ ] P0: Implement transaction ID matching (FR-8).
- [ ] P0: Implement amount/timestamp fallback matching (FR-9).
- [ ] P0: Implement anomaly rules: duplicate (FR-12), missing settlement (FR-13), amount mismatch (FR-14), timing anomaly (FR-15).
- [ ] P0: Compute run-level stats (matched count, flagged count, flagged value — FR-11).
- [ ] P0: Write unit tests against seeded test cases for all 4 anomaly types (this is your accuracy proof for judges).
- [ ] P1: Make matching tolerances configurable (not hardcoded), per SRS defaults.

**Dependencies:** Phase 2 (needs persisted transaction data to operate on).
**Definition of Done:** Running reconciliation against the sample dataset correctly matches ≥95% of clean records and correctly triggers all 4 anomaly types on seeded test cases (PRD Section 12 acceptance criteria).

---

### Phase 4 — AI Explanation Layer (Day 5–6)
**Goal:** Add the "AI Finance Controller" intelligence — scoped narrowly and safely.

- [ ] P0: Build the Claude API integration wrapper (structured, grounded prompt per flag).
- [ ] P0: Implement deterministic confidence scoring (FR-19 — not LLM-generated).
- [ ] P0: Implement graceful failure handling — flag remains usable if explanation fails (FR-20).
- [ ] P1: Add async/background generation so explanation doesn't block flag creation (PERF-3).
- [ ] P1: Manually audit a sample of generated explanations against ground truth to confirm no hallucinated figures (ties to PRD success metric: 100% grounded explanations).

**Dependencies:** Phase 3 (needs real flags with computed data to explain).
**Definition of Done:** Every flag from the test dataset has an explanation that references only real, correct numbers — verified manually, not assumed.

---

### Phase 5 — Review Dashboard & Decisioning (Day 6–8)
**Goal:** The interface analysts actually use — this is what a judge will interact with live.

- [ ] P0: Build Run Summary screen (stat cards, breakdown by anomaly type).
- [ ] P0: Build Flag List screen (filter/sort, ConfidenceMeter, FlagBadge components).
- [ ] P0: Build Flag Detail screen (explanation, related transactions side-by-side, DecisionBar).
- [ ] P0: Implement `/flags/{id}/decision` endpoint (approve/reject/escalate + comment).
- [ ] P1: Add empty/loading/error states per UI/UX plan Section 8.
- [ ] P1: Polish visual design per UI/UX plan (typography, color, spacing system).

**Dependencies:** Phase 3 & 4 (needs flags and explanations to display).
**Definition of Done:** A user can go from Run Summary → Flag List → Flag Detail → make a decision, entirely through the UI, with no manual API calls needed.

---

### Phase 6 — Audit Trail (Day 8–9)
**Goal:** Make every prior action traceable — this is a core judging criterion.

- [ ] P0: Implement audit log writes on every state-changing action (run creation, flag creation, decisions).
- [ ] P0: Build per-flag audit trail view (AuditRow component, chronological).
- [ ] P1: Build global Admin audit log view with filters.
- [ ] P1: Confirm architecturally that no update/delete route exists for audit entries (SEC-5 — verify, don't just assume).

**Dependencies:** Phases 2–5 (needs real events happening across the system to log).
**Definition of Done:** Every action taken during a full demo walkthrough appears correctly, in order, in the audit trail — zero gaps.

---

### Phase 7 — Testing & Bug Fixing (Day 9–11)
**Goal:** Confidence that the demo won't break live in front of judges.

- [ ] P0: Full end-to-end run-through using the sample dataset (upload → reconcile → review → decide → audit).
- [ ] P0: Test all edge cases from SRS Section 9 (EC-1 through EC-6) explicitly, not just happy path.
- [ ] P0: Fix any P0-blocking bugs found during full run-through.
- [ ] P1: Cross-browser check on the frontend (at minimum Chrome, since that's most likely for a live demo).
- [ ] P1: Load a slightly larger dataset (e.g., 1,000+ rows) to confirm performance targets (PERF-1) hold.

**Dependencies:** All prior phases functionally complete.
**Definition of Done:** A full, unscripted run-through of the entire user journey completes with no crashes, no silent failures, and matches all PRD acceptance criteria (Section 12).

---

### Phase 8 — Deployment & Demo Prep (Day 11–13)
**Goal:** A live, shareable, judge-accessible product.

- [ ] P0: Deploy backend + database to Render/Railway.
- [ ] P0: Deploy frontend to Vercel, pointed at the live backend.
- [ ] P0: Verify the deployed version works end-to-end (not just localhost) — deployment environment differences are a common last-minute failure point.
- [ ] P0: Prepare the demo dataset (clean data with clearly seeded, explainable anomalies) so the live walkthrough tells a clear story.
- [ ] P0: Write the public GitHub README (problem, architecture summary, how to run locally, screenshots).
- [ ] P0: Record the pitch video: one flagged case walked through end-to-end (mismatch → explanation → confidence → human override → audit trail), per the earlier pitch narrative.
- [ ] P1: Add architecture diagram image to the README (can reuse the data-flow diagram from the Architecture doc).

**Dependencies:** Phase 7 (only deploy something that's already been verified working).
**Definition of Done:** A judge can open the deployed link, log in with demo credentials, and walk through the full flow without any local setup — and the pitch video clearly demonstrates accuracy, explainability, and human oversight, matching the track's explicit judging criteria.

---

### Phase 9 — Stretch Polish (Only if time remains)
- [ ] P2: Aggregate Admin analytics view across runs.
- [ ] P2: Configurable matching tolerances exposed in UI (not just backend config).
- [ ] P2: Basic automated test suite (beyond the manual/unit tests already required in Phase 3).
- [ ] P2: Improve empty-state and micro-interaction polish across the dashboard.

**Rule:** Nothing in Phase 9 is touched until every P0 item across all prior phases is done and verified.

---

## 4. Milestone Summary

| Milestone | Target Day | Signals |
|---|---|---|
| M1 — Skeleton running | Day 1 | Login page loads, backend health check passes |
| M2 — Data flows in | Day 3 | Real CSVs upload and persist correctly |
| M3 — Core logic proven | Day 5 | Reconciliation + anomaly detection pass all seeded test cases |
| M4 — AI layer live | Day 6 | Every flag has a grounded, correct explanation |
| M5 — Full UI flow works | Day 8 | Complete journey usable end-to-end in the browser |
| M6 — Auditable | Day 9 | Every action traceable with zero gaps |
| M7 — Demo-ready | Day 13 | Deployed, tested, README + pitch video complete |

---

## 5. Dependency Chain (Critical Path)

```
Setup → Auth → Ingestion → Reconciliation Engine → AI Explanations
                                        │
                                        ▼
                              Review Dashboard → Audit Trail
                                        │
                                        ▼
                              Testing → Deployment → Demo Prep
```

The Reconciliation Engine (Phase 3) is the true critical path — every downstream phase depends on it producing correct, trustworthy output. If time gets tight, protect Phase 3's quality before adding any UI polish.

---

## 6. MVP Definition of Done (Ship Gate)

Before calling this "submission ready," confirm every item from the PRD's Section 12 acceptance criteria passes, plus:

- [ ] Deployed and accessible via a public URL
- [ ] Public GitHub repo with clear README and setup instructions
- [ ] Pitch video recorded, under the time limit, tells a clear one-case-walkthrough story
- [ ] No P0 item from any phase above is left incomplete
- [ ] A person outside the build team can follow the demo without explanation and understand what problem is being solved and how
