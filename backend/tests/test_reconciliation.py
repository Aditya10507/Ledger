from datetime import datetime, timedelta
from types import SimpleNamespace

from app.reconciliation.anomaly_rules import (
    detect_amount_mismatch,
    detect_duplicates,
    detect_missing_settlement,
    detect_timing_anomaly,
)


def _txn(**kwargs):
    defaults = dict(id="t1", amount=1000, timestamp=datetime.utcnow(), counterparty="Acme")
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def test_amount_mismatch_detected_above_threshold():
    ledger = _txn(amount=1000)
    settlement = _txn(amount=950)
    result = detect_amount_mismatch(ledger, settlement)
    assert result is not None
    assert result["delta"] == 50


def test_amount_within_tolerance_not_flagged():
    # EC-5: rounding-level differences must NOT be flagged.
    ledger = _txn(amount=1000)
    settlement = _txn(amount=999.5)
    assert detect_amount_mismatch(ledger, settlement) is None


def test_missing_settlement_flagged_after_window():
    old_txn = _txn(timestamp=datetime.utcnow() - timedelta(days=5))
    result = detect_missing_settlement(old_txn, datetime.utcnow())
    assert result is not None


def test_missing_settlement_not_flagged_within_window():
    recent_txn = _txn(timestamp=datetime.utcnow() - timedelta(hours=1))
    assert detect_missing_settlement(recent_txn, datetime.utcnow()) is None


def test_timing_anomaly_detected():
    ledger = _txn(timestamp=datetime.utcnow())
    settlement = _txn(timestamp=datetime.utcnow() + timedelta(days=8))
    result = detect_timing_anomaly(ledger, settlement)
    assert result is not None
    assert result["delta"] == 8


def test_duplicate_detection_groups_matching_transactions():
    t1 = _txn(id="a", amount=500, counterparty="Acme", timestamp=datetime.utcnow())
    t2 = _txn(id="b", amount=500, counterparty="Acme", timestamp=t1.timestamp + timedelta(minutes=2))
    t3 = _txn(id="c", amount=999, counterparty="Other", timestamp=datetime.utcnow())

    groups = detect_duplicates([t1, t2, t3])
    assert len(groups) == 1
    assert {t.id for t in groups[0]} == {"a", "b"}


def test_duplicate_detection_ignores_transactions_outside_window():
    t1 = _txn(id="a", amount=500, counterparty="Acme", timestamp=datetime.utcnow())
    t2 = _txn(id="b", amount=500, counterparty="Acme", timestamp=t1.timestamp + timedelta(minutes=30))
    assert detect_duplicates([t1, t2]) == []
