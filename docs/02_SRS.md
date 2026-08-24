# Software Requirements Specification (SRS)
## Ledger — AI Finance Controller Agent

**Version:** 1.0
**Status:** Draft for Buildathon Submission

---

## 1. Introduction

### 1.1 Purpose
This document specifies the functional and non-functional requirements for Ledger, an AI-assisted reconciliation and anomaly-detection system. It is intended to guide implementation and testing, and every requirement below is written to be independently verifiable.

### 1.2 Scope
Ledger ingests two structured datasets (a transaction ledger and a settlement report), reconciles them, detects anomalies, generates explanations, and supports human review with full audit logging. This SRS covers the MVP as defined in the Ledger PRD.

---

## 2. User Roles & Permissions

| Role | Permissions |
|---|---|
| **Analyst** | Upload files, trigger reconciliation runs, view flags, view explanations, approve/reject/escalate flags, view audit trail for runs they have access to |
| **Admin** | All Analyst permissions, plus: view all runs across all analysts, view aggregate/cross-run statistics, manage user accounts (create/deactivate) |

**Permission Rules:**
- PR-1: Only authenticated users may access any system functionality.
- PR-2: An Analyst can only act on flags within runs they created, unless explicitly granted Admin role.
- PR-3: A flag's status can only be changed by an authenticated user with Analyst or Admin role; the action is always attributed to that user's identity in the audit log.
- PR-4: No role can delete or modify an existing audit log entry. Audit entries are append-only.

---

## 3. Functional Requirements

### 3.1 Authentication & Session

- **FR-1:** The system shall allow a user to log in with email and password.
  - *Acceptance:* Valid credentials return an authenticated session token; invalid credentials return a generic error without revealing whether the email or password was incorrect.
- **FR-2:** The system shall reject any API request without a valid session token with a 401 response.
- **FR-3:** Session tokens shall expire after a configurable period (default: 24 hours) and require re-authentication after expiry.

### 3.2 File Ingestion

- **FR-4:** The system shall allow an authenticated user to upload a ledger CSV file and a settlement CSV file for a single reconciliation run.
  - *Acceptance:* Both files are required before a run can be triggered; the system rejects a run request missing either file.
- **FR-5:** The system shall validate uploaded files for: correct file type (.csv), required columns present, non-empty file, and parseable rows.
  - *Acceptance:* Any validation failure returns a specific error identifying which check failed and, where possible, which row/column caused it.
- **FR-6:** The system shall reject files exceeding a configured maximum size (default: 10MB for MVP) with a clear error message.
- **FR-7:** Upon successful validation, the system shall persist raw transaction records from both files, tagged by source (`ledger` or `settlement`) and associated with the reconciliation run.

### 3.3 Reconciliation Engine

- **FR-8:** The system shall attempt to match each ledger transaction to a settlement record using transaction ID as the primary key.
- **FR-9:** Where transaction ID matching fails, the system shall attempt a secondary match using amount + timestamp within a configurable tolerance window (default: amount exact, timestamp ± 24 hours).
- **FR-10:** Every ledger and settlement record shall end a reconciliation run in exactly one of these states: `matched`, `flagged`, or `unmatched_pending_review`.
- **FR-11:** The system shall compute and store, per run: total records processed, matched count, flagged count, and total flagged value.

### 3.4 Anomaly Detection

- **FR-12:** The system shall detect and flag **duplicate charges**: two or more ledger records with the same amount and counterparty within a configurable time window (default: 5 minutes).
- **FR-13:** The system shall detect and flag **missing settlements**: a ledger transaction with no corresponding settlement record after the expected settlement window (default: 3 business days).
- **FR-14:** The system shall detect and flag **amount mismatches**: a matched pair where the ledger amount and settlement amount differ by more than a configurable tolerance (default: > ₹1 or > 0.5%, whichever is greater).
- **FR-15:** The system shall detect and flag **timing anomalies**: a matched pair where the settlement occurred outside the expected settlement window.
- **FR-16:** Each flag shall record: flag type, related transaction ID(s), computed delta (amount/time difference), and the rule that triggered it.

### 3.5 AI Explanation Generation

- **FR-17:** For every flag created, the system shall generate a natural-language explanation using an LLM call.
- **FR-18:** The explanation prompt shall include only pre-computed, verified data (transaction IDs, amounts, deltas, timestamps, rule triggered) — the LLM shall not be asked to determine whether a mismatch exists, only to explain one that has already been deterministically identified.
- **FR-19:** Each explanation shall be accompanied by a confidence score (0–100), computed deterministically from the size/severity of the anomaly (not generated by the LLM).
  - *Acceptance:* Confidence scoring logic is fixed and reproducible — the same input always produces the same score.
- **FR-20:** If the LLM call fails or times out, the system shall still display the flag with its computed data, with an explanation status of "unavailable" rather than blocking the flag from view.

### 3.6 Review & Decisioning

- **FR-21:** The system shall allow an Analyst to set a flag's status to `approved`, `rejected`, or `escalated`.
- **FR-22:** The system shall allow an optional free-text comment to accompany any decision.
- **FR-23:** Once a decision is recorded, the system shall timestamp it and attribute it to the acting user's identity.
- **FR-24:** A flag's decision may be changed after the fact, but every change creates a new audit log entry; prior entries are never overwritten.

### 3.7 Audit Trail

- **FR-25:** The system shall log every state-changing event: run creation, match computation, flag creation, and every human decision.
- **FR-26:** Each audit log entry shall include: entity type, entity ID, action taken, actor (system or user ID), timestamp, and relevant before/after state.
- **FR-27:** Audit log entries shall be viewable, filtered by run or by flag, but never editable or deletable through the application.

### 3.8 Reporting

- **FR-28:** The system shall provide a summary view per reconciliation run showing: total records, matched %, flagged %, flagged value by anomaly type.
- **FR-29:** Admin users shall be able to view aggregate statistics across all runs (total runs, average match rate, total flagged value over time).

---

## 4. Business Rules

- **BR-1:** A transaction can belong to only one reconciliation run.
- **BR-2:** A flag must always reference at least one real transaction record — flags are never created without underlying data.
- **BR-3:** Confidence scores are bounded between 0 and 100 and are deterministic, not AI-generated.
- **BR-4:** The system never automatically resolves, corrects, or reverses a financial discrepancy — all resolution requires explicit human action.
- **BR-5:** Currency is fixed per run; cross-currency reconciliation is not supported in MVP.

---

## 5. Data Requirements

### 5.1 Core Entities

**User**
`id, name, email, password_hash, role [analyst|admin], created_at`

**ReconciliationRun**
`id, created_by (User), ledger_filename, settlement_filename, status [processing|completed|failed], total_records, matched_count, flagged_count, total_flagged_value, created_at, completed_at`

**Transaction**
`id, run_id, source [ledger|settlement], external_txn_id, amount, currency, timestamp, counterparty, raw_row (JSON), match_status [matched|flagged|unmatched]`

**Flag**
`id, run_id, flag_type [duplicate|missing_settlement|amount_mismatch|timing_anomaly], related_transaction_ids (array), computed_delta, confidence_score, ai_explanation, explanation_status [ok|unavailable], status [open|approved|rejected|escalated], reviewed_by, review_comment, reviewed_at, created_at`

**AuditLogEntry**
`id, entity_type, entity_id, action, actor, previous_state (JSON), new_state (JSON), timestamp`

### 5.2 Required CSV Columns (minimum viable schema)

| Column | Required | Notes |
|---|---|---|
| transaction_id | Yes | Unique identifier |
| amount | Yes | Numeric, positive |
| currency | Yes | ISO code, single value per run |
| timestamp | Yes | ISO 8601 or configurable format |
| counterparty | No | Used for duplicate detection when present |

---

## 6. Validation Rules

- **V-1:** `amount` must be numeric and greater than 0; rows failing this are rejected with a row-level error, not silently dropped.
- **V-2:** `timestamp` must parse to a valid date/time; unparseable rows are rejected with a row-level error.
- **V-3:** `transaction_id` must be non-empty; duplicate transaction_ids within the *same* source file are rejected as a file-level error (ambiguous primary key).
- **V-4:** `currency` must be consistent across all rows in a single run; mixed currencies trigger a file-level rejection.
- **V-5:** File must contain a header row matching expected column names (case-insensitive match accepted).

---

## 7. Authentication & Authorization

- **AA-1:** Passwords are never stored in plaintext; hashed using a standard algorithm (e.g., bcrypt).
- **AA-2:** All API endpoints except `/auth/login` require a valid session token.
- **AA-3:** Role checks are enforced server-side on every request — client-side role display is cosmetic only and never trusted as the authorization boundary.
- **AA-4:** An Analyst attempting to access a run they do not own (and is not Admin) receives a 403 response.

---

## 8. Error Handling

- **EH-1:** All validation errors return a structured response: `{error_code, message, field (if applicable), row (if applicable)}`.
- **EH-2:** System failures (e.g., LLM timeout, database error) are caught and logged server-side; the user sees a generic, non-technical error message.
- **EH-3:** A failed reconciliation run is marked `failed` with a reason, and does not leave partial/inconsistent data visible to the user.
- **EH-4:** Duplicate file upload for an in-progress run is rejected rather than queued or silently ignored.

---

## 9. Edge Cases

- **EC-1:** Ledger has a transaction with no matching settlement anywhere → flagged as `missing_settlement`, not silently dropped.
- **EC-2:** Settlement record exists with no corresponding ledger transaction → flagged as `unmatched_pending_review` and surfaced for analyst attention.
- **EC-3:** Two ledger transactions have identical amount, counterparty, and timestamp (true duplicates in source data, not a system error) → both flagged as `duplicate` with equal confidence.
- **EC-4:** Uploaded file has correct headers but zero data rows → rejected with a clear "empty dataset" error.
- **EC-5:** Amount mismatch is within tolerance (e.g., ₹0.50 rounding) → NOT flagged; must match BR/FR tolerance rules exactly.
- **EC-6:** LLM explanation service is down → flag is still created and visible with `explanation_status: unavailable`; system does not block the analyst's workflow.

---

## 10. Security Requirements

- **SEC-1:** All API traffic shall be served over HTTPS.
- **SEC-2:** Uploaded files are scanned for correct MIME type before processing to prevent arbitrary file execution.
- **SEC-3:** SQL access uses parameterized queries exclusively; no raw string interpolation into queries.
- **SEC-4:** Session tokens are stored securely (httpOnly cookies or equivalent), never exposed in URLs or logs.
- **SEC-5:** Audit log entries are immutable at the application layer (no update/delete endpoint exists for them).

---

## 11. Performance Requirements

- **PERF-1:** A reconciliation run of 1,000 transaction pairs shall complete matching and flagging in under 30 seconds.
- **PERF-2:** The flag list view shall load within 2 seconds for a run with up to 5,000 flags (with pagination).
- **PERF-3:** AI explanation generation shall not block the matching/flagging pipeline — flags are created and viewable even if explanations are still being generated asynchronously.

---

## 12. Acceptance Criteria Summary

| Requirement Area | Verifiable Outcome |
|---|---|
| Ingestion | Invalid files are rejected with specific, actionable errors |
| Matching | ≥95% correct match rate on clean test dataset |
| Anomaly Detection | All 4 anomaly types correctly triggered on seeded test cases |
| Explanations | 100% of explanations reference only real computed values |
| Review | Every decision is attributed, timestamped, and immutable in history |
| Audit | Every state change has a corresponding, unmodifiable log entry |
| Security | No unauthenticated access possible to any data endpoint |
