from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionSource

AMOUNT_TOLERANCE = 1.0          # currency units, for fallback matching
TIMESTAMP_TOLERANCE_HOURS = 24  # window for fallback matching when txn_id doesn't match


def match_transactions(db: Session, run_id: str) -> list[tuple[Transaction, Transaction | None]]:
    """FR-8/FR-9: matches each ledger transaction to a settlement transaction.
    Primary key: external_txn_id. Fallback: amount + timestamp window.
    Returns a list of (ledger_txn, matched_settlement_txn_or_None).
    """
    ledger_txns = db.query(Transaction).filter(
        Transaction.run_id == run_id, Transaction.source == TransactionSource.ledger
    ).all()
    settlement_txns = db.query(Transaction).filter(
        Transaction.run_id == run_id, Transaction.source == TransactionSource.settlement
    ).all()

    settlement_by_id = {s.external_txn_id: s for s in settlement_txns}
    used_settlement_ids: set[str] = set()
    results = []

    for ledger_txn in ledger_txns:
        match = settlement_by_id.get(ledger_txn.external_txn_id)

        if match is None:
            for s in settlement_txns:
                if s.id in used_settlement_ids:
                    continue
                if abs(float(s.amount) - float(ledger_txn.amount)) <= AMOUNT_TOLERANCE:
                    delta_hours = abs((s.timestamp - ledger_txn.timestamp).total_seconds()) / 3600
                    if delta_hours <= TIMESTAMP_TOLERANCE_HOURS:
                        match = s
                        break

        if match:
            used_settlement_ids.add(match.id)

        results.append((ledger_txn, match))

    return results
