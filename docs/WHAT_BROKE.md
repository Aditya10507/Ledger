# What Broke, and How We Recovered

Three real incidents from this project's actual build history — not hypothetical, not smoothed
over for the pitch. Each one was found, diagnosed, and fixed with evidence, in this order.

## 1. A silent correctness bug: flagged value always showed ₹0

**What broke:** `ReconciliationRun.total_flagged_value` existed as a database column and was
displayed on the Run Summary page, but the reconciliation service never actually calculated it.
Every run showed ₹0 in "Flagged Value" regardless of how much money was actually at risk. No
error, no crash — just a silently wrong number sitting in front of an analyst.

**How it was found:** Not by a user complaint — by a deliberate code review pass that grepped
the codebase for every place `total_flagged_value` was referenced, and found it was written to
nowhere.

**How it was fixed:** Each anomaly's contributing transaction amount (or summed group amount,
for duplicates) is now accumulated as flags are created and written to the run record.

**How it was verified:** Re-ran the same benchmark dataset before and after the fix. Before:
₹0 reported regardless of input. After: real values (e.g., ₹70,880 on a test dataset with mixed
anomalies) — confirmed by direct comparison, not just "it looks right now."

## 2. A dependency version conflict: passlib/bcrypt

**What broke:** The very first end-to-end test run failed at the login step. `passlib`'s bcrypt
backend raised an error trying to read `bcrypt.__about__.__version__`, which doesn't exist in
newer `bcrypt` releases — a known incompatibility between `passlib`'s bcrypt detection code and
`bcrypt >= 4.1`.

**How it was found:** Immediately, from the first full pipeline test — the error message pointed
directly at the version mismatch.

**How it was fixed:** Pinned `bcrypt==4.0.1` explicitly in `requirements.txt` alongside
`passlib[bcrypt]==1.7.4`, rather than leaving the version unconstrained and hoping pip resolves
something compatible.

**How it was verified:** Re-ran the full login → upload → reconcile → decide → audit flow after
the pin — passed cleanly, and it's stayed pinned since.

## 3. A real performance bottleneck: O(n²) duplicate detection

**What broke:** Nothing was reported broken — this was found by *choosing to measure* rather
than assuming the system would scale. A throughput benchmark at increasing record counts showed
5,000 records taking ~30 seconds, far more than the roughly-linear growth expected from the
smaller test sizes.

**How it was diagnosed:** The duplicate-detection function compared every ledger transaction
against every other one — a full pairwise scan, O(n²) by construction. At small scale (a few
hundred rows) this is invisible. At a few thousand, it dominates runtime.

**How it was fixed:** Transactions are now bucketed by `(amount, counterparty)` before any
comparison happens — a real duplicate always shares both exactly, so transactions that couldn't
possibly match are never compared at all. Within a bucket, items are sorted by time so the scan
can stop early once outside the duplicate window.

**How it was verified, with real before/after numbers:**

| Records | Before (O(n²)) | After (bucketed) |
|---|---|---|
| 5,000 | 29.98s | 9.75s |
| 20,000 | *(not tested — would have taken minutes)* | 37.51s |

Full methodology and the extended results (out to 20,000 records) are in
`docs/BENCHMARK_RESULTS.md`.

---

## The pattern across all three

None of these were caught by "it looks like it works." All three were caught by either reading
the code deliberately looking for gaps, or by measuring instead of assuming. That's the habit
this project tried to build in, not just the fixes themselves — see
`docs/KNOWN_LIMITATIONS.md` for what we know is still not fully proven (confidence calibration
in particular), stated with the same directness as these three fixes.
