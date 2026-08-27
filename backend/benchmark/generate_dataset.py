"""Generates a labeled benchmark dataset with known ground truth.

Every transaction is tagged with what SHOULD happen to it (clean match, or
flagged as a specific anomaly type) before the system ever sees it. This lets
run_benchmark.py compute real precision/recall — not a cherry-picked demo,
an actual measured accuracy number, per Razorpay's own stated bar:
"Throughput plus measured accuracy plus an honest exception list."

Deterministic (fixed seed) so results are reproducible run to run.
"""

import csv
import json
import random
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)

BASE_DATE = datetime(2026, 6, 1)
COUNTERPARTIES = ["Acme Traders", "Blue Retail", "Nova Foods", "Orion Corp", "Delta Mart", "Zenith Retail"]


def generate(n_clean: int, n_per_anomaly_type: int, out_dir: str) -> dict:
    """Returns the ground truth dict as well as writing ledger.csv, settlement.csv,
    and ground_truth.json into out_dir.
    """
    ledger_rows = []
    settlement_rows = []
    ground_truth = {}  # external_txn_id -> {"should_flag": bool, "type": str|None}

    txn_counter = 1

    def next_id():
        nonlocal txn_counter
        tid = f"BM{txn_counter:06d}"
        txn_counter += 1
        return tid

    # --- Clean matches ---
    for _ in range(n_clean):
        tid = next_id()
        amount = round(random.uniform(100, 50000), 2)
        counterparty = random.choice(COUNTERPARTIES)
        ledger_time = BASE_DATE + timedelta(hours=random.randint(0, 24 * 60))
        settlement_time = ledger_time + timedelta(days=random.choice([1, 2]))

        ledger_rows.append([tid, amount, "INR", ledger_time.isoformat(), counterparty])
        settlement_rows.append([tid, amount, "INR", settlement_time.isoformat()])
        ground_truth[tid] = {"should_flag": False, "type": None}

    # --- Amount mismatches ---
    for _ in range(n_per_anomaly_type):
        tid = next_id()
        amount = round(random.uniform(500, 50000), 2)
        counterparty = random.choice(COUNTERPARTIES)
        ledger_time = BASE_DATE + timedelta(hours=random.randint(0, 24 * 60))
        settlement_time = ledger_time + timedelta(days=1)
        # Delta well above the max(₹1, 0.5%) threshold so it's an unambiguous case.
        delta = max(50, amount * 0.05)
        settled_amount = round(amount - delta, 2)

        ledger_rows.append([tid, amount, "INR", ledger_time.isoformat(), counterparty])
        settlement_rows.append([tid, settled_amount, "INR", settlement_time.isoformat()])
        ground_truth[tid] = {"should_flag": True, "type": "amount_mismatch"}

    # --- Missing settlements (no settlement row at all) ---
    for _ in range(n_per_anomaly_type):
        tid = next_id()
        amount = round(random.uniform(100, 50000), 2)
        counterparty = random.choice(COUNTERPARTIES)
        ledger_time = BASE_DATE + timedelta(hours=random.randint(0, 24 * 60))

        ledger_rows.append([tid, amount, "INR", ledger_time.isoformat(), counterparty])
        # No settlement row written for this txn_id.
        ground_truth[tid] = {"should_flag": True, "type": "missing_settlement"}

    # --- Timing anomalies (settled well outside the 3-day window) ---
    for _ in range(n_per_anomaly_type):
        tid = next_id()
        amount = round(random.uniform(100, 50000), 2)
        counterparty = random.choice(COUNTERPARTIES)
        ledger_time = BASE_DATE + timedelta(hours=random.randint(0, 24 * 60))
        settlement_time = ledger_time + timedelta(days=random.randint(7, 14))

        ledger_rows.append([tid, amount, "INR", ledger_time.isoformat(), counterparty])
        settlement_rows.append([tid, amount, "INR", settlement_time.isoformat()])
        ground_truth[tid] = {"should_flag": True, "type": "timing_anomaly"}

    # --- Duplicates (pairs — n_per_anomaly_type pairs = 2x that many rows) ---
    for _ in range(n_per_anomaly_type):
        amount = round(random.uniform(100, 20000), 2)
        counterparty = random.choice(COUNTERPARTIES)
        ledger_time = BASE_DATE + timedelta(hours=random.randint(0, 24 * 60))

        tid_a = next_id()
        tid_b = next_id()
        settlement_time = ledger_time + timedelta(days=1)

        for tid, offset_minutes in [(tid_a, 0), (tid_b, 2)]:
            t = ledger_time + timedelta(minutes=offset_minutes)
            ledger_rows.append([tid, amount, "INR", t.isoformat(), counterparty])
            settlement_rows.append([tid, amount, "INR", settlement_time.isoformat()])
            ground_truth[tid] = {"should_flag": True, "type": "duplicate"}

    # Shuffle row order so the system can't rely on input ordering.
    random.shuffle(ledger_rows)
    random.shuffle(settlement_rows)

    with open(f"{out_dir}/ledger.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "amount", "currency", "timestamp", "counterparty"])
        writer.writerows(ledger_rows)

    with open(f"{out_dir}/settlement.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["transaction_id", "amount", "currency", "timestamp"])
        writer.writerows(settlement_rows)

    with open(f"{out_dir}/ground_truth.json", "w") as f:
        json.dump(ground_truth, f, indent=2)

    return ground_truth


if __name__ == "__main__":
    import sys

    out_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    gt = generate(n_clean=360, n_per_anomaly_type=60, out_dir=out_dir)
    print(f"Generated {len(gt)} labeled transactions in {out_dir}/")
