# 5-Minute Pitch Script — Ledger

Structured to hit exactly what Razorpay said they grade: **"throughput plus measured accuracy
plus an honest exception list"**, and to directly answer their submission requirement to
**"explain what broke during development and how you recovered from it."**

---

## 0:00–0:45 — The problem (30–45 sec)

> "Every payment platform keeps two records of the same money movement: what the merchant's
> ledger says happened, and what the bank actually settled. These drift apart constantly —
> duplicate charges, missing settlements, amount mismatches, delayed payouts. Today, finance
> teams catch these by manually cross-checking spreadsheets. It doesn't scale, and mismatches
> that go unnoticed are direct revenue loss."

## 0:45–2:00 — Live walkthrough, one flagged case end-to-end (75 sec)

Upload the `anomaly_rich` dataset live. Walk through **one** flag start to finish:
1. Show the flag list — point at the confidence score
2. Open one flag (recommend the amount-mismatch case — cleanest story)
3. Read the AI explanation aloud, point out it's grounded in real computed numbers, not free text
4. Approve it, show the decision gets recorded
5. Open the audit trail — show the full history: created → explained → approved, all timestamped

> "That's the core loop: detect deterministically, explain in plain English, keep a human in
> the loop, and log everything so nothing is a black box."

## 2:00–3:00 — The numbers, not just the demo (60 sec)

This is the section most teams will skip — don't skip it.

> "A cherry-picked demo doesn't prove much, so we built a labeled benchmark with known ground
> truth — 660 transactions, exactly which ones should be flagged and why, decided before the
> system ever saw them."

State the real numbers from `docs/BENCHMARK_RESULTS.md`:
- **100% precision, 100% recall** on the labeled benchmark
- **1,000 transactions reconciled in under 2 seconds** — well inside the requirement
- Then, the honest part: *"That 100% is on unambiguous cases by design — we're upfront in our
  docs that real-world borderline cases haven't been stress-tested yet, and that our confidence
  calibration isn't proven against real false positives. We'd rather say that than oversell it."*

## 3:00–4:00 — What broke, and how we recovered (60 sec)

Pick **one** of the three from `docs/WHAT_BROKE.md` — the O(n²) story is the strongest, since it
shows initiative (nobody reported it) and has real before/after numbers:

> "We didn't just build this and assume it scales — we benchmarked it. At 5,000 records,
> reconciliation took 30 seconds. We traced it to an O(n²) duplicate-detection scan comparing
> every transaction to every other one. We rewrote it to bucket transactions by amount and
> counterparty first — cut it to under 10 seconds at the same scale, and confirmed linear
> scaling out to 20,000 records. That's the kind of thing you only find by measuring, not by
> assuming it works."

## 4:00–4:40 — Architecture in one breath (40 sec)

> "FastAPI and Postgres on the backend, React on the frontend. The one hard rule we built the
> whole system around: the AI never decides whether something is an anomaly — that's
> deterministic, rule-based code. The AI's only job is to explain a decision that's already been
> made, and we built an automatic grounding check that flags it in the audit trail if an
> explanation ever mentions a number that doesn't trace back to real data."

## 4:40–5:00 — Close (20 sec)

> "Everything I've shown — the accuracy numbers, the performance fix, the known gaps — is
> written down in the repo, not just in this pitch. Code, benchmark, and honest limitations list
> are all public. Happy to go deeper into any part of it."

---

## Backup slide / answer-ready facts (in case the panel asks)

- Precision/recall/throughput numbers: `docs/BENCHMARK_RESULTS.md`
- Known gaps, stated directly: `docs/KNOWN_LIMITATIONS.md`
- Full bug/fix history: `docs/WHAT_BROKE.md`
- 16 (now 21) automated tests, running in CI on every push: `.github/workflows/tests.yml`
- Core guardrail — AI never decides, only explains: `knowledge.md` Section 2
