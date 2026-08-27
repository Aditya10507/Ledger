# Benchmark Results

Every number on this page comes from an actual run of `backend/benchmark/run_benchmark.py`
against the real system (real FastAPI app, real reconciliation engine, real database) — none of
it is estimated. Raw output is in `backend/benchmark/results.json`. Reproduce with:

```bash
cd backend
python benchmark/run_benchmark.py
```

---

## 1. Detection Accuracy

Dataset: 660 labeled transactions (360 clean, 300 across the four anomaly types — 60 each,
120 for duplicates since they come in pairs), generated with a fixed random seed for
reproducibility (`backend/benchmark/generate_dataset.py`).

| Metric | Result |
|---|---|
| Detection precision | **100.0%** |
| Detection recall | **100.0%** |
| False positive rate | **0.0%** |
| Type accuracy (correct anomaly type assigned) | **100.0%** |

**Recall by anomaly type:**

| Type | Caught |
|---|---|
| amount_mismatch | 60/60 (100%) |
| duplicate | 120/120 (100%) |
| missing_settlement | 60/60 (100%) |
| timing_anomaly | 60/60 (100%) |

### Honest caveat on these numbers

This benchmark uses **unambiguous** cases by design — amount mismatches are well above the
detection threshold, timing anomalies are well outside the settlement window, duplicates are
exact matches. **100% accuracy here proves the rule logic is implemented correctly, not that
the system is perfect on messy real-world data.** Real transaction data will have genuinely
ambiguous cases sitting right at a threshold boundary (e.g., a ₹12 delta when the threshold is
₹12.50), and this benchmark doesn't yet measure behavior there. A fairer stress test would add
borderline cases deliberately — that's listed in Known Limitations rather than papered over here.

---

## 2. Confidence Calibration

**Method:** Since no real historical analyst decisions exist yet, ground truth was used as a
stand-in for "was this flag actually correct" and fed through the real `/flags/{id}/decision`
endpoint — so this also produced genuine audit trail data, not just a report.

| Confidence bucket | n | Real-anomaly rate |
|---|---|---|
| 80–100 | 120 | 100.0% |
| 50–79 | 120 | 100.0% |
| 0–49 | 0 | — no flags in this range |

### Honest caveat on these numbers

**This does not yet demonstrate that low-confidence flags are less reliable than high-confidence
ones** — both buckets show 100% because this benchmark produced zero false positives. Confidence
calibration is only meaningfully testable against a dataset that actually contains some wrong
flags spread across different confidence levels. This is the single most important next step for
proving the explainability claim rigorously, and it's called out explicitly in
`KNOWN_LIMITATIONS.md` rather than glossed over.

---

## 3. Throughput

Clean-only data (isolates the reconciliation/matching path from anomaly-detection cost).
Measured end-to-end via the real HTTP upload endpoint, not a shortcut internal call.

| Records | Time | 
|---|---|
| 500 | 0.97s |
| 1,000 | 1.94s |
| 2,000 | 3.70s |
| 5,000 | 9.75s |
| 10,000 | 18.67s |
| 20,000 | 37.51s |

**SRS PERF-1 requirement** ("1,000 transaction pairs in under 30 seconds"): met with wide margin
(1.94s, ~15x faster than the requirement).

**Scaling characteristic:** now linear (~1.9ms/record) — see `KNOWN_LIMITATIONS.md` for the
O(n²) bottleneck this replaced, found via this same benchmark, and how it was fixed.

The remaining per-record cost is dominated by row-by-row pandas iteration during CSV validation
and one-row-at-a-time ORM inserts during persistence — not by the reconciliation algorithm
itself. Vectorizing both would very likely cut this further; not yet done, listed as a next step.
