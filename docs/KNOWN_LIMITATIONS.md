# Known Limitations & Exceptions

Written deliberately, not as an afterthought. Every item here is a real, current constraint of
the system — not a hedge. See `docs/BENCHMARK_RESULTS.md` for the measurements referenced below.

## Performance

- **Fixed and verified, but worth knowing the history:** duplicate detection originally scanned
  every ledger transaction against every other one (O(n²)). Benchmarking measured this at ~30s
  for 5,000 records. It was refactored to bucket transactions by `(amount, counterparty)` before
  comparing — real duplicates always share both exactly — which cut this to ~9.75s at 5,000
  records and confirmed linear scaling out to 20,000 records (37.5s). See
  `app/reconciliation/anomaly_rules.py` for the fix and `BENCHMARK_RESULTS.md` for before/after.
- **Remaining per-record cost** (~1.9ms/record at scale) is dominated by row-by-row pandas
  iteration in CSV validation and one-row-at-a-time ORM inserts, not the matching algorithm.
  Not yet optimized — vectorized pandas operations and bulk inserts are the obvious next step.
- The rate limiter (`app/auth/rate_limit.py`) is in-memory only. It resets on restart and
  doesn't share state across multiple backend instances. Fine for a single-instance deployment;
  would need a Redis-backed limiter for horizontal scaling.

## Accuracy & Detection

- The accuracy benchmark (100% precision/recall) uses **unambiguous** synthetic cases — deltas
  well above thresholds, timing well outside windows. It proves the rule logic is implemented
  correctly, not that real-world borderline cases are handled perfectly. Genuinely ambiguous
  cases (e.g., a delta just barely over the threshold) haven't been specifically stress-tested.
- **Confidence calibration is not yet proven** — see `BENCHMARK_RESULTS.md` Section 2. The
  benchmark run produced zero false positives, so there's no evidence yet that low-confidence
  flags are actually less reliable than high-confidence ones. This needs either deliberately
  ambiguous synthetic cases or real production data with genuine false positives to validate.
- Matching tolerance (amount ± ₹1, timestamp ± 24h fallback window) is fixed in code, not
  configurable per-merchant. Different businesses may need different tolerances.
- No fuzzy/partial string matching on counterparty names — a typo'd counterparty name across
  the two files would not match, and duplicate detection requires an *exact* counterparty match.

## Explainability

- AI explanations require `ANTHROPIC_API_KEY` to be configured. Without it, every flag shows
  "AI explanation unavailable" — this is deliberate degradation (FR-20), not a crash, but it does
  mean the explainability feature can't be demonstrated live without a configured key.
- The hallucination guard (`app/explanation/hallucination_guard.py`) checks that every number in
  a generated explanation traces back to real computed data, and logs a warning to the audit
  trail if not. It has not yet caught a real hallucination in practice — validated only via unit
  tests with deliberately fabricated numbers (`tests/test_hallucination_guard.py`), since no
  API key was available in this environment to generate real explanations at scale.

## Scope (deliberately out, not overlooked)

- No live bank/payment-gateway API integration — CSV upload only.
- Single currency per run; no multi-currency reconciliation.
- No automated resolution of discrepancies — every flag requires an explicit human decision.
- Two roles only (Analyst, Admin); no granular permission tiers.
- Not deployed to a multi-instance/production-scale environment — verified locally and via
  benchmark, not under real concurrent load.

## What we'd do next, in priority order

1. Validate confidence calibration against a dataset with genuine false positives.
2. Vectorize CSV validation and persistence to cut the remaining per-record overhead.
3. Make matching tolerances configurable per merchant/run instead of fixed in code.
4. Move the rate limiter to Redis for multi-instance deployment.
5. Add fuzzy counterparty matching to catch near-duplicate name variants.
