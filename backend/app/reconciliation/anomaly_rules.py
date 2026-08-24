from datetime import timedelta

from app.models.flag import FlagType
from app.models.transaction import Transaction

AMOUNT_MISMATCH_ABS = 1.0          # FR-14 default: > ₹1
AMOUNT_MISMATCH_PCT = 0.005        # or > 0.5%, whichever is greater
SETTLEMENT_WINDOW_DAYS = 3         # FR-13 / FR-15 default
DUPLICATE_WINDOW_MINUTES = 5       # FR-12 default


def detect_amount_mismatch(ledger_txn, settlement_txn) -> dict | None:
    """FR-14. EC-5: differences within tolerance (e.g. rounding) are NOT flagged."""
    delta = abs(float(ledger_txn.amount) - float(settlement_txn.amount))
    threshold = max(AMOUNT_MISMATCH_ABS, float(ledger_txn.amount) * AMOUNT_MISMATCH_PCT)
    if delta > threshold:
        return {"flag_type": FlagType.amount_mismatch, "delta": delta}
    return None


def detect_missing_settlement(ledger_txn, now) -> dict | None:
    """FR-13: a ledger transaction with no settlement after the expected window."""
    if (now - ledger_txn.timestamp) > timedelta(days=SETTLEMENT_WINDOW_DAYS):
        return {"flag_type": FlagType.missing_settlement, "delta": None}
    return None


def detect_timing_anomaly(ledger_txn, settlement_txn) -> dict | None:
    """FR-15: a matched pair that settled outside the expected window."""
    delta_days = (settlement_txn.timestamp - ledger_txn.timestamp).days
    if delta_days > SETTLEMENT_WINDOW_DAYS:
        return {"flag_type": FlagType.timing_anomaly, "delta": delta_days}
    return None


def detect_duplicates(ledger_txns: list[Transaction]) -> list[list[Transaction]]:
    """FR-12: same amount + counterparty within a short time window."""
    groups: list[list[Transaction]] = []
    seen: set[str] = set()

    for i, t1 in enumerate(ledger_txns):
        if t1.id in seen:
            continue
        group = [t1]
        for t2 in ledger_txns[i + 1:]:
            if t2.id in seen:
                continue
            same_amount = float(t1.amount) == float(t2.amount)
            same_counterparty = t1.counterparty == t2.counterparty
            within_window = abs((t1.timestamp - t2.timestamp).total_seconds()) <= DUPLICATE_WINDOW_MINUTES * 60
            if same_amount and same_counterparty and within_window:
                group.append(t2)
                seen.add(t2.id)
        if len(group) > 1:
            seen.add(t1.id)
            groups.append(group)

    return groups
