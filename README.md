# Ledger — AI Finance Controller

An AI-powered reconciliation and anomaly-detection agent built for the Razorpay AI Buildathon 2026 (AI Finance Controller track).

## What it does

Ledger compares a merchant's transaction ledger against a bank/gateway settlement report, automatically flags mismatches — duplicate charges, missing settlements, amount mismatches, timing anomalies — and explains each flag in plain English using an LLM that is strictly grounded in pre-computed data. Every match result and every human decision is written to an immutable audit trail.

**Core guardrail:** the AI never decides whether something is an anomaly — that logic is deterministic, rule-based code. The LLM's only job is to phrase an already-computed result in plain English.

## Project docs

Full planning documents live in [`/docs`](./docs):
- [`01_PRD.md`](./docs/01_PRD.md) — product requirements, MVP scope, user stories, success metrics
- [`02_SRS.md`](./docs/02_SRS.md) — detailed functional/technical requirements, validation rules, edge cases
- [`03_Architecture.md`](./docs/03_Architecture.md) — system architecture, data flow, API design
- [`04_UIUX_Plan.md`](./docs/04_UIUX_Plan.md) — screens, user flows, design system
- [`05_Development_Plan.md`](./docs/05_Development_Plan.md) — phased build roadmap with Definition of Done

[`knowledge.md`](./knowledge.md) (project root) is the condensed working reference for AI coding agents (Freebuff/Codebuff-compatible — auto-loaded at session start).

## Tech stack

| Layer | Choice |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, pandas |
| Frontend | React, TypeScript, Tailwind CSS, Vite |
| Database | PostgreSQL (SQLite works fine for local dev) |
| AI | Claude API (Anthropic) — explanation generation only |
| Auth | JWT session tokens |

## Running locally

### 1. Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp ../.env.example ../.env   # fill in ANTHROPIC_API_KEY if you have one — the app works without it
python -m app.seed           # creates demo users
uvicorn app.main:app --reload
```

API runs at `http://localhost:8000` — interactive docs at `http://localhost:8000/docs`.

**Demo login:** `analyst@ledger.demo` / `password123` (or `admin@ledger.demo` for admin access)

> By default the app uses SQLite (`sqlite:///./ledger.db`) so you can run it with zero external
> setup. Point `DATABASE_URL` at Postgres when you're ready for something closer to production.

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

App runs at `http://localhost:5173`.

### 3. With Docker Compose (backend + Postgres)

```bash
docker compose up
```

## Try it with sample data

Seeded test CSVs — one example of each anomaly type — are in [`backend/tests/fixtures/`](./backend/tests/fixtures/). Upload both files from the "New Run" screen to see a full reconciliation happen end-to-end.

## Tests

```bash
cd backend
pytest -v
```

16 unit tests cover the anomaly detection rules, CSV validation, and confidence scoring — the deterministic core the whole product depends on.

## Without an Anthropic API key

The app runs and reconciles correctly even with `ANTHROPIC_API_KEY` unset — flags are created and fully usable, just with `explanation_status: "unavailable"` instead of an AI-generated explanation (this is a deliberate requirement, not a bug — see FR-20 in the SRS).
