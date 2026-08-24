# System Architecture Document
## Ledger — AI Finance Controller Agent

**Version:** 1.0
**Principle:** Keep it practical. Every component should be justified by an actual MVP requirement — no speculative infrastructure.

---

## 1. Architecture Overview

Ledger is a three-tier web application with one external AI dependency:

```
┌─────────────┐      ┌──────────────────┐      ┌───────────────┐
│   Frontend   │ ───► │   Backend API     │ ───► │   Database     │
│  (React SPA) │ ◄─── │  (FastAPI/Python) │ ◄─── │ (PostgreSQL)   │
└─────────────┘      └────────┬──────────┘      └───────────────┘
                               │
                               ▼
                      ┌──────────────────┐
                      │  Claude API       │
                      │  (explanation     │
                      │   generation only)│
                      └──────────────────┘
```

No microservices, no message queue, no separate ML infrastructure. The matching and anomaly-detection logic is deterministic code running inside the backend API — the LLM is a narrowly-scoped dependency used for one thing: turning computed results into plain English.

---

## 2. Recommended Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Frontend | React + Tailwind CSS | Fast to build, component-friendly for a dashboard-heavy UI |
| Backend | Python + FastAPI | Async-friendly, pairs naturally with pandas for reconciliation logic, fast to stand up |
| Reconciliation logic | pandas | Purpose-built for tabular matching/comparison; avoids hand-rolled CSV parsing |
| Database | PostgreSQL (SQLite acceptable for local/demo) | Relational integrity matters here (foreign keys between runs, transactions, flags, audit log) |
| AI | Claude API (Anthropic) | Used exclusively for explanation generation, grounded in pre-computed data |
| Auth | JWT-based session tokens | Simple, stateless, sufficient for MVP's two-role model |
| Deployment | Docker + Render/Railway (backend), Vercel (frontend) | Fast to deploy for a demo, no need for Kubernetes-scale infra |
| Monitoring | Structured logging (JSON logs) + optional Sentry | Enough visibility for a demo/MVP without building an observability platform |

**Explicitly avoided (over-engineering for this stage):** microservices split, Kafka/event streaming, custom ML model training, multi-region deployment, GraphQL. All of these solve problems Ledger doesn't have yet at MVP scale.

---

## 3. System Components

### 3.1 Frontend (React SPA)
- Handles file upload UI, dashboard views, flag detail views, and decision actions.
- Communicates with backend exclusively via REST API over HTTPS.
- Holds no business logic — all matching, flagging, and scoring happens server-side. The frontend only renders what the API returns.

### 3.2 Backend API (FastAPI)
Organized into four logical modules:

1. **Ingestion module** — file upload handling, schema validation, raw record persistence.
2. **Reconciliation module** — matching engine (transaction ID match → amount/timestamp fallback match) and anomaly detection rules (duplicate, missing settlement, amount mismatch, timing anomaly).
3. **Explanation module** — builds a structured, data-grounded prompt per flag and calls the Claude API; computes confidence score deterministically (not via LLM).
4. **Review & Audit module** — handles decision endpoints (approve/reject/escalate) and writes every state change to the audit log table.

### 3.3 Database (PostgreSQL)
Stores all persistent state: users, runs, transactions, flags, audit log entries. See Section 5 (SRS) for full schema — this document focuses on how it's used architecturally.

### 3.4 AI Integration Layer
A thin wrapper around the Claude API with one responsibility: given a flag's structured data (type, transaction IDs, amounts, delta, rule triggered), return a plain-English explanation. This layer:
- Never sends unverified/raw data to the LLM — only pre-validated, computed fields.
- Times out gracefully (flag remains visible with `explanation_status: unavailable` on failure — per FR-20).
- Is stateless and swappable — could be replaced with a different model without touching reconciliation logic.

---

## 4. Data Flow

```
1. User uploads ledger.csv + settlement.csv
        │
        ▼
2. Ingestion module validates schema & rows
        │  (reject with specific errors if invalid)
        ▼
3. Raw transactions persisted, tagged by source, linked to run
        │
        ▼
4. Reconciliation engine matches records
   (txn_id match → amount/timestamp fallback)
        │
        ▼
5. Anomaly rules applied to unmatched/mismatched records
   → Flag records created (type, transaction refs, delta)
        │
        ▼
6. Explanation module calls Claude API per flag
   (grounded prompt: only computed data, no free reasoning)
        │
        ▼
7. Flags + explanations + confidence scores stored,
   surfaced in dashboard
        │
        ▼
8. Analyst reviews → approve/reject/escalate
        │
        ▼
9. Every step (3–8) written to immutable Audit Log
```

---

## 5. API Design (Key Endpoints)

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/auth/login` | Authenticate, return session token |
| POST | `/reconciliation/runs` | Upload files, create a new run |
| GET | `/reconciliation/runs` | List runs (scoped by role) |
| GET | `/reconciliation/runs/{id}` | Run detail + summary stats |
| GET | `/reconciliation/runs/{id}/flags` | List flags for a run (paginated, filterable) |
| GET | `/flags/{id}` | Flag detail, including explanation + confidence |
| POST | `/flags/{id}/decision` | Record approve/reject/escalate + comment |
| GET | `/flags/{id}/audit-trail` | Full history for a specific flag |
| GET | `/audit-log` | Global audit log (Admin only, filterable) |

All endpoints return standard HTTP status codes; errors follow the structured format defined in the SRS (Section 8).

---

## 6. Authentication Architecture

- Login issues a signed JWT containing `user_id` and `role`, expiring after 24 hours (configurable).
- Token is sent as an `Authorization: Bearer` header on every request.
- Backend middleware validates the token and attaches the authenticated user to the request context before any route logic runs.
- Role checks (`Analyst` vs `Admin`) happen server-side in each route handler — never trusted from client state.

---

## 7. Storage

- **Relational data** (users, runs, transactions, flags, audit log) → PostgreSQL.
- **Raw uploaded files** → stored transiently during processing (local disk or object storage bucket for a short retention window), not retained long-term since parsed data lives in the database. For MVP, local disk storage with a cleanup job is sufficient; object storage (S3-compatible) is a natural upgrade path if needed later.

---

## 8. Security

- HTTPS enforced on all traffic (SEC-1).
- Passwords hashed with bcrypt; never logged or stored in plaintext.
- Parameterized queries throughout (no raw SQL string interpolation) to prevent injection.
- File upload validated by MIME type and size before parsing.
- Audit log table has no update/delete route exposed at the API layer — enforced architecturally, not just by convention.
- Secrets (DB credentials, Claude API key) loaded from environment variables, never committed to source control.

---

## 9. Deployment

**MVP/Demo deployment (simple, fast to stand up):**
- Backend: Dockerized FastAPI app deployed to Render or Railway.
- Frontend: React app deployed to Vercel, pointing to the backend API URL.
- Database: Managed PostgreSQL instance (Render/Railway/Supabase all work).
- Environment variables (Claude API key, DB connection string, JWT secret) managed via the hosting platform's secret manager.

A single `docker-compose.yml` covering backend + database is enough for local development — no orchestration platform needed at this stage.

---

## 10. Monitoring & Logging

- Structured (JSON) request logs at the API layer: endpoint, status code, latency, user ID.
- Errors (validation failures, LLM timeouts, DB errors) logged with enough context to reproduce, without logging sensitive data (e.g., full file contents, tokens).
- Optional: Sentry (or similar) for exception tracking if time permits — not required for MVP functionality, but strengthens the "production-minded" story in the pitch.

---

## 11. Scalability Considerations

The MVP is intentionally built for correctness and clarity over scale, but the architecture doesn't paint itself into a corner:

- Matching logic runs in-process via pandas, which comfortably handles tens of thousands of rows — fine for demo and early real usage. If volume grows significantly, this module can be extracted into an async worker/queue without changing the API contract.
- Database schema uses normalized tables with foreign keys, which scales cleanly with proper indexing (on `run_id`, `transaction_id`, `flag.status`).
- The AI explanation layer is already decoupled and asynchronous-friendly (FR-20), so it can be moved to a background job queue later without redesigning the flow.
- Stateless JWT auth means the backend can be horizontally scaled behind a load balancer with no session-affinity requirement, if ever needed.

None of these upgrades are part of MVP — they're simply not blocked by any current architectural decision.
