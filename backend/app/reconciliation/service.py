from datetime import datetime

from sqlalchemy.orm import Session

from app.audit.service import log_event
from app.explanation.confidence import compute_confidence
from app.explanation.service import generate_explanation
from app.models.flag import ExplanationStatus, Flag, FlagStatus
from app.models.run import ReconciliationRun, RunStatus
from app.models.transaction import MatchStatus
from app.reconciliation.anomaly_rules import (
    detect_amount_mismatch,
    detect_duplicates,
    detect_missing_settlement,
    detect_timing_anomaly,
)
from app.reconciliation.matcher import match_transactions


def run_reconciliation(db: Session, run_id: str) -> None:
    """Orchestrates the full pipeline for one run:
    match -> detect anomalies -> create flags -> score confidence -> explain -> audit log.

    This function is the critical path of the whole product (see 05_Development_Plan.md,
    Phase 3) — everything downstream (dashboard, review, audit) depends on this being correct.
    """
    run = db.query(ReconciliationRun).filter(ReconciliationRun.id == run_id).first()
    matches = match_transactions(db, run_id)
    now = datetime.utcnow()

    matched_count = 0
    flags_created: list[tuple[dict, list[str]]] = []

    for ledger_txn, settlement_txn in matches:
        if settlement_txn is None:
            anomaly = detect_missing_settlement(ledger_txn, now)
            if anomaly:
                ledger_txn.match_status = MatchStatus.flagged
                flags_created.append((anomaly, [ledger_txn.id]))
            else:
                # Not old enough to flag yet — sits as unmatched pending review (EC-1).
                ledger_txn.match_status = MatchStatus.unmatched
            continue

        anomaly = detect_amount_mismatch(ledger_txn, settlement_txn) or detect_timing_anomaly(
            ledger_txn, settlement_txn
        )
        if anomaly:
            ledger_txn.match_status = MatchStatus.flagged
            settlement_txn.match_status = MatchStatus.flagged
            flags_created.append((anomaly, [ledger_txn.id, settlement_txn.id]))
        else:
            ledger_txn.match_status = MatchStatus.matched
            settlement_txn.match_status = MatchStatus.matched
            matched_count += 1

    # Duplicate detection runs across all ledger transactions, independent of matching.
    ledger_txns = [m[0] for m in matches]
    for group in detect_duplicates(ledger_txns):
        flags_created.append(({"flag_type": "duplicate", "delta": None}, [t.id for t in group]))

    for anomaly, txn_ids in flags_created:
        flag = Flag(
            run_id=run_id,
            flag_type=anomaly["flag_type"],
            related_transaction_ids=txn_ids,
            computed_delta=anomaly.get("delta"),
            confidence_score=compute_confidence(anomaly["flag_type"], anomaly.get("delta")),
            explanation_status=ExplanationStatus.pending,
            status=FlagStatus.open,
        )
        db.add(flag)
        db.flush()  # so flag.id is available before commit

        flag_type_str = anomaly["flag_type"].value if hasattr(anomaly["flag_type"], "value") else anomaly["flag_type"]
        log_event(db, "flag", flag.id, "created", actor="system", new_state={"flag_type": flag_type_str})

        # FR-20: explanation failures never block flag creation — this call is safe either way.
        generate_explanation(db, flag)

    run.total_records = len(matches)
    run.matched_count = matched_count
    run.flagged_count = len(flags_created)
    run.status = RunStatus.completed
    run.completed_at = now
    db.commit()

    log_event(
        db,
        "run",
        run_id,
        "completed",
        actor="system",
        new_state={"matched": matched_count, "flagged": len(flags_created)},
    )
