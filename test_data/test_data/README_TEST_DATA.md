# Ledger — Test Data Guide

Every file here has been run through the actual app to confirm it produces exactly the result described below — this isn't just sample data, it's verified test data.

## How to use these

1. Start the backend and frontend (see the main README).
2. Log in as `analyst@ledger.demo` / `password123`.
3. Go to **New Run**, upload the two files from a pair below, and check the result against what's listed here.

---

## Valid datasets (`/valid`)

### 1. `clean_ledger.csv` + `clean_settlement.csv`
**Tests:** the happy path — everything reconciles cleanly.

**Expected result:**
- Total records: 5
- Matched: 5 (100%)
- Flagged: 0
- Flag List screen should show the empty state: *"No anomalies found — all transactions reconciled cleanly."*

### 2. `anomaly_rich_ledger.csv` + `anomaly_rich_settlement.csv`
**Tests:** every feature at once — this is the pair to use for your demo/pitch video, since it exercises all four anomaly types plus explanations, review, and audit trail in one run.

**Expected result:**
- Total records: 14
- Matched: 5
- Flagged: 11, broken down as:
  - `amount_mismatch` × 3 → TXN3002 (₹2500 vs ₹2450), TXN3008 (₹900 vs ₹850), TXN3014 (₹980 vs ₹920)
  - `duplicate` × 2 → {TXN3003, TXN3004} and {TXN3009, TXN3010} (same amount/counterparty, ~2–3 min apart)
  - `missing_settlement` × 4 → TXN3004, TXN3005, TXN3010, TXN3011 (no matching settlement row)
  - `timing_anomaly` × 2 → TXN3006 (settled 9 days late), TXN3012 (settled 10 days late)

**Suggested demo walkthrough:** open the `TXN3002` amount-mismatch flag, read its AI explanation (or the "unavailable" fallback if you haven't set an API key), approve it, then check the audit trail — that's the exact narrative from the pitch script we discussed earlier.

---

## Invalid datasets (`/invalid`)

Each of these is designed to trigger **one specific validation error**. Upload each as the "Ledger CSV" alongside `clean_settlement.csv` as the settlement file — the run should be rejected before anything is saved, with the exact message below.

| File | Triggers | Expected error message |
|---|---|---|
| `missing_column.csv` | FR-5 / missing required column | `Missing required columns: currency` |
| `negative_amount.csv` | V-1 | `amount must be a positive number` |
| `duplicate_transaction_id.csv` | V-3 | `Duplicate transaction_id values found within the same file` |
| `mixed_currency.csv` | V-4 | `Multiple currencies found in one file — a run must use a single currency` |
| `empty_file.csv` | FR-5 | `File contains no data rows` |
| `bad_timestamp.csv` | V-2 | `timestamp could not be parsed` |

**What this proves:** the app never silently drops bad rows or crashes — every failure is specific and actionable, per SRS Section 8 (Error Handling). Good to show judges directly if they ask about robustness.

---

## Verification log (already run, for your reference)

```
CLEAN DATASET       → total=5  matched=5  flagged=0        [PASS]
ANOMALY-RICH DATASET → total=14 matched=5  flagged=11        [PASS]
  amount_mismatch=3, duplicate=2, missing_settlement=4, timing_anomaly=2

bad_timestamp.csv            → 400  "timestamp could not be parsed"                              [PASS]
duplicate_transaction_id.csv → 400  "Duplicate transaction_id values found within the same file"  [PASS]
empty_file.csv                → 400  "File contains no data rows"                                 [PASS]
missing_column.csv            → 400  "Missing required columns: currency"                         [PASS]
mixed_currency.csv            → 400  "Multiple currencies found in one file..."                    [PASS]
negative_amount.csv           → 400  "amount must be a positive number"                            [PASS]
```
