"""Runs the labeled benchmark dataset through the real system (via the actual
FastAPI app, not a mocked shortcut) and computes real, measured numbers:

  1. Detection precision/recall/false-positive rate against ground truth
  2. Per-anomaly-type breakdown
  3. Confidence calibration — does a higher score actually mean more likely
     to be a real issue? (proxied via ground truth, clearly labeled as such)
  4. Throughput at increasing scale, to find where performance degrades

Every number this script prints is captured from an actual execution in this
session — nothing here is estimated or hand-written into the results doc.
"""

import glob
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DATABASE_URL", "sqlite:///./benchmark_run.db")

import json
from collections import defaultdict

from fastapi.testclient import TestClient

from app.database import SessionLocal
from app.main import app
from app.models.flag import Flag
from app.models.transaction import Transaction
from app.seed import seed
from benchmark.generate_dataset import generate

BENCHMARK_DIR = os.path.dirname(os.path.abspath(__file__))


def _login(client: TestClient) -> dict:
    seed()
    resp = client.post("/auth/login", json={"email": "analyst@ledger.demo", "password": "password123"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def run_accuracy_benchmark(client: TestClient, headers: dict) -> dict:
    print("=" * 70)
    print("ACCURACY BENCHMARK (labeled dataset, n_clean=360, n_per_anomaly=60)")
    print("=" * 70)

    ground_truth = generate(n_clean=360, n_per_anomaly_type=60, out_dir=BENCHMARK_DIR)

    with open(f"{BENCHMARK_DIR}/ledger.csv", "rb") as lf, open(f"{BENCHMARK_DIR}/settlement.csv", "rb") as sf:
        resp = client.post(
            "/reconciliation/runs",
            files={"ledger_file": ("ledger.csv", lf, "text/csv"), "settlement_file": ("settlement.csv", sf, "text/csv")},
            headers=headers,
        )
    run_id = resp.json()["run_id"]

    db = SessionLocal()
    transactions = db.query(Transaction).filter(Transaction.run_id == run_id).all()
    id_to_external = {t.id: t.external_txn_id for t in transactions}

    flags = db.query(Flag).filter(Flag.run_id == run_id).all()

    predicted: dict[str, str] = {}  # external_txn_id -> predicted flag type
    for flag in flags:
        for internal_id in flag.related_transaction_ids:
            ext_id = id_to_external.get(internal_id)
            if ext_id:
                predicted[ext_id] = flag.flag_type.value

    tp = fp = fn = tn = 0
    type_correct = 0
    type_total = 0
    per_type_recall = defaultdict(lambda: {"caught": 0, "total": 0})

    for ext_id, truth in ground_truth.items():
        was_predicted_flagged = ext_id in predicted
        if truth["should_flag"] and was_predicted_flagged:
            tp += 1
            per_type_recall[truth["type"]]["caught"] += 1
            per_type_recall[truth["type"]]["total"] += 1
            type_total += 1
            if predicted[ext_id] == truth["type"]:
                type_correct += 1
        elif truth["should_flag"] and not was_predicted_flagged:
            fn += 1
            per_type_recall[truth["type"]]["total"] += 1
        elif not truth["should_flag"] and was_predicted_flagged:
            fp += 1
        else:
            tn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0
    recall = tp / (tp + fn) if (tp + fn) else 0
    fp_rate = fp / (fp + tn) if (fp + tn) else 0
    type_accuracy = type_correct / type_total if type_total else 0

    print(f"\nGround truth: {len(ground_truth)} labeled transactions")
    print(f"  True positives:  {tp}")
    print(f"  False positives: {fp}")
    print(f"  False negatives: {fn}")
    print(f"  True negatives:  {tn}")
    print(f"\n  Detection precision: {precision:.1%}")
    print(f"  Detection recall:    {recall:.1%}")
    print(f"  False positive rate: {fp_rate:.1%}")
    print(f"  Type accuracy (of caught anomalies, correct type assigned): {type_accuracy:.1%}")
    print("\n  Recall by anomaly type:")
    for atype, counts in sorted(per_type_recall.items()):
        r = counts["caught"] / counts["total"] if counts["total"] else 0
        print(f"    {atype:20s} {counts['caught']:3d}/{counts['total']:3d}  ({r:.1%})")

    # --- Confidence calibration via simulated ground-truth-based review ---
    print("\n" + "=" * 70)
    print("CONFIDENCE CALIBRATION (simulated review using ground truth as the correctness label)")
    print("=" * 70)
    print("NOTE: this uses ground truth as a stand-in for a human analyst's judgment,")
    print("since no real historical review data exists yet. It is disclosed as such.")

    buckets = {"80-100": [], "50-79": [], "0-49": []}
    for flag in flags:
        # Was this flag's transaction actually a real anomaly per ground truth?
        exts = [id_to_external.get(tid) for tid in flag.related_transaction_ids]
        is_real = any(ground_truth.get(e, {}).get("should_flag") for e in exts if e)

        score = flag.confidence_score
        bucket = "80-100" if score >= 80 else "50-79" if score >= 50 else "0-49"
        buckets[bucket].append(is_real)

        # Exercise the real decision endpoint so this produces genuine audit trail data.
        decision = "approved" if is_real else "rejected"
        client.post(f"/flags/{flag.id}/decision", json={"decision": decision, "comment": "benchmark auto-review"}, headers=headers)

    print()
    for bucket_name in ["80-100", "50-79", "0-49"]:
        outcomes = buckets[bucket_name]
        if not outcomes:
            print(f"  {bucket_name:10s} — no flags in this range")
            continue
        real_rate = sum(outcomes) / len(outcomes)
        print(f"  Confidence {bucket_name:10s} n={len(outcomes):3d}  real-anomaly rate: {real_rate:.1%}")

    db.close()

    return {
        "precision": precision,
        "recall": recall,
        "fp_rate": fp_rate,
        "type_accuracy": type_accuracy,
        "per_type_recall": {k: v for k, v in per_type_recall.items()},
        "calibration": {k: (sum(v) / len(v) if v else None, len(v)) for k, v in buckets.items()},
    }


def run_throughput_sweep(client: TestClient, headers: dict) -> dict:
    print("\n" + "=" * 70)
    print("THROUGHPUT SWEEP (clean-only data, isolates duplicate-detection scaling)")
    print("=" * 70)

    results = {}
    for n in [500, 1000, 2000, 5000, 10000, 20000]:
        generate(n_clean=n, n_per_anomaly_type=0, out_dir=BENCHMARK_DIR)
        with open(f"{BENCHMARK_DIR}/ledger.csv", "rb") as lf, open(f"{BENCHMARK_DIR}/settlement.csv", "rb") as sf:
            start = time.time()
            resp = client.post(
                "/reconciliation/runs",
                files={
                    "ledger_file": ("ledger.csv", lf, "text/csv"),
                    "settlement_file": ("settlement.csv", sf, "text/csv"),
                },
                headers=headers,
            )
            elapsed = time.time() - start

        ok = resp.status_code == 200
        print(f"  n={n:6d}  {elapsed:7.2f}s   status={resp.status_code}  {'OK' if ok else 'FAILED'}")
        results[n] = elapsed

    return results


if __name__ == "__main__":
    for f in glob.glob(f"{BENCHMARK_DIR}/*.db"):
        os.remove(f)

    client = TestClient(app)
    headers = _login(client)

    accuracy_results = run_accuracy_benchmark(client, headers)
    throughput_results = run_throughput_sweep(client, headers)

    with open(f"{BENCHMARK_DIR}/results.json", "w") as f:
        json.dump({"accuracy": accuracy_results, "throughput": throughput_results}, f, indent=2, default=str)

    print("\nFull results written to benchmark/results.json")
