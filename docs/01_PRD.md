# Product Requirements Document (PRD)
## Ledger — AI Finance Controller Agent

**Version:** 1.0
**Status:** Draft for Buildathon Submission
**Owner:** [Your Name]
**Track:** Razorpay AI Buildathon 2026 — AI Finance Controller

---

## 1. Overview

Ledger is an AI-powered reconciliation and anomaly-detection agent that compares a merchant's internal transaction ledger against bank/gateway settlement reports, automatically flags mismatches, explains each flag in plain English, and maintains a full audit trail of every decision — human or AI. It is built to bring speed to financial reconciliation without sacrificing the accuracy, traceability, and human oversight that finance-critical workflows require.

---

## 2. Problem Statement

Payment platforms and merchants maintain two records of the same money movement: what their own system logged (the ledger) and what the bank or payment gateway actually settled. These two records frequently drift apart — duplicate charges, missing settlements, amount mismatches, and delayed payouts all occur regularly at scale.

Today, this reconciliation is largely manual: finance/ops teams cross-check spreadsheets row by row. This process is slow, error-prone, doesn't scale with transaction volume, and creates real financial risk — mismatches that go unnoticed become direct revenue loss or compliance exposure.

**Core problem:** There is no fast, explainable, and trustworthy way to automatically catch reconciliation discrepancies before they become financial losses.

---

## 3. Target Users

| User | Description | Primary Need |
|---|---|---|
| **Finance/Ops Analyst** (primary) | Reviews daily/weekly reconciliation output, investigates flags, makes approve/reject decisions | Fast, trustworthy flags with clear reasoning, so they don't have to manually cross-check every row |
| **Finance Manager/Admin** (secondary) | Oversees reconciliation health across runs, reviews audit history, manages analyst access | High-level visibility into risk exposure and confidence that every decision is traceable |

---

## 4. Goals & Objectives

1. Automatically detect reconciliation mismatches with high precision, minimizing false positives that waste analyst time.
2. Make every flag explainable in plain language, grounded strictly in the underlying data (no unverified AI reasoning).
3. Preserve full traceability — every match, flag, and human decision is logged and auditable.
4. Keep humans in control of final decisions; the system assists, it does not auto-resolve financial discrepancies unsupervised.
5. Demonstrate a working, demoable product within buildathon constraints, without over-scoping.

---

## 5. Core Features

1. **CSV Data Ingestion** — Upload a ledger file and a settlement file.
2. **Reconciliation Engine** — Automated matching of ledger transactions to settlement records.
3. **Anomaly Detection** — Rule-based flagging of duplicates, missing settlements, amount mismatches, and timing anomalies.
4. **AI-Generated Explanations** — Plain-English rationale + confidence score for every flag, grounded in the computed data.
5. **Review Dashboard** — List and detail views of all flags, with filtering and sorting.
6. **Human-in-the-Loop Decisions** — Analysts approve, reject, or escalate each flag.
7. **Audit Trail** — Immutable log of every match result and every human decision.
8. **Reconciliation Summary Report** — Run-level statistics: match rate, flagged value, breakdown by anomaly type.

---

## 6. MVP Scope

The MVP is intentionally narrow: **one end-to-end reconciliation workflow, done well**, rather than many shallow features.

**In scope for MVP:**
- CSV upload for ledger + settlement data (no live bank/API integration)
- Exact and near-match reconciliation logic
- Four anomaly types: duplicate charge, missing settlement, amount mismatch, timing anomaly
- AI explanation generation for each flag, using only the computed match data as grounding
- A single reviewer role that can approve/reject/escalate flags
- A simple, functional dashboard (list view, detail view, summary view)
- Audit log viewable per flag and per run
- Single-organization, single-currency dataset

**Explicitly deferred beyond MVP:** see Section 10 (Out-of-Scope).

---

## 7. User Stories

| ID | As a... | I want to... | So that... |
|---|---|---|---|
| US-1 | Analyst | Upload a ledger CSV and a settlement CSV | I can start a reconciliation run without manual setup |
| US-2 | Analyst | See a summary of how many transactions matched vs. flagged | I understand the overall health of this reconciliation run at a glance |
| US-3 | Analyst | View a list of all flagged transactions | I can prioritize which discrepancies to investigate first |
| US-4 | Analyst | Click into a flag and see a plain-English explanation of why it was raised | I don't have to manually re-derive the reasoning myself |
| US-5 | Analyst | See a confidence score on each flag | I know which flags need urgent attention vs. which are likely low-risk |
| US-6 | Analyst | Approve, reject, or escalate a flag with an optional comment | I can record my decision and reasoning |
| US-7 | Analyst/Manager | View the full audit trail for any flag | I can prove exactly what happened and why, for compliance purposes |
| US-8 | Manager | View aggregate statistics across all runs | I can track reconciliation accuracy and risk exposure over time |
| US-9 | Analyst | See a clear error message if my uploaded file is malformed | I know exactly what to fix before re-uploading |

---

## 8. Success Metrics

| Metric | Target for MVP/Demo |
|---|---|
| Reconciliation accuracy (correct matches / total matchable records) | ≥ 95% on test dataset |
| False positive rate on flags | < 15% on test dataset |
| Time to reconcile a 1,000-row dataset | < 30 seconds end-to-end |
| Every flag has a grounded, non-hallucinated explanation | 100% (verified manually on demo dataset) |
| Every decision (AI flag + human action) is logged | 100% coverage, zero gaps in audit trail |

---

## 9. Assumptions

- Input data arrives as structured CSV files with a reasonably consistent schema (column mapping may be configurable, but format is tabular).
- A single currency is used across a given reconciliation run.
- The dataset used for the demo is either real Razorpay test-mode data or realistic synthetic data — not production data.
- One organization/tenant is sufficient for the MVP; multi-tenant support is not required to prove the concept.
- Analysts are trusted users; the MVP does not need to defend against malicious insiders.

---

## 10. Risks & Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| LLM produces a plausible-sounding but factually wrong explanation | High — undermines trust in a finance tool | Explanation prompt is strictly grounded in pre-computed data (amounts, IDs, deltas); LLM is only used to phrase the explanation, not to compute or judge the mismatch itself |
| Poor-quality or inconsistent CSV input breaks matching logic | Medium | Strict upload validation with clear error messages before any matching runs |
| Reconciliation logic produces too many false positives, eroding analyst trust | Medium | Tunable matching tolerance (e.g., timestamp window, minor rounding allowance); track false-positive rate as a core success metric |
| Scope creep beyond MVP during a time-boxed build | High | MVP scope is fixed in this document; anything not listed in Section 6 is explicitly out of scope until post-MVP |
| Judges perceive the "explanation" as just an LLM wrapper with no real logic | High | Core matching/anomaly-detection logic is deterministic and rule-based; the LLM's role is scoped narrowly to explanation generation, and this is called out clearly in the pitch |

---

## 11. Out-of-Scope (for MVP)

- Live bank/payment gateway API integrations (real-time data pull)
- Multi-currency and multi-tenant support
- Automated resolution/auto-correction of flagged discrepancies
- Email/Slack notification system
- Mobile application
- Role-based granular permission tiers beyond Analyst/Admin
- Custom ML model training (LLM used out-of-the-box for explanation generation only)
- Historical trend analytics beyond basic run-over-run summary

---

## 12. Acceptance Criteria (MVP Sign-off)

- [ ] User can upload a ledger CSV and a settlement CSV and trigger a reconciliation run.
- [ ] System correctly matches at least 95% of clean, matchable transactions on the test dataset.
- [ ] System correctly flags all four anomaly types when present in the test dataset.
- [ ] Every flag displays an AI-generated explanation that references only real computed values (no fabricated numbers).
- [ ] Every flag displays a confidence score.
- [ ] Analyst can approve, reject, or escalate a flag, and this decision is persisted.
- [ ] Every match result and every human decision appears in an audit trail, timestamped and attributable.
- [ ] Run summary view shows total records, matched count, flagged count, and flagged value.
- [ ] Invalid/malformed file upload produces a clear, actionable error message instead of a silent failure or crash.
