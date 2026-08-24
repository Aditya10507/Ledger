from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.run import ReconciliationRun, RunStatus
from app.models.transaction import TransactionSource
from app.ingestion.service import parse_and_validate, persist_transactions
from app.ingestion.validators import ValidationError
from app.reconciliation.service import run_reconciliation
from app.review.service import list_flags_for_run

router = APIRouter(prefix="/reconciliation", tags=["reconciliation"])


@router.post("/runs")
async def create_run(
    ledger_file: UploadFile = File(...),
    settlement_file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """FR-4/FR-5: both files are required; each is validated before anything is persisted."""
    ledger_bytes = await ledger_file.read()
    settlement_bytes = await settlement_file.read()

    try:
        ledger_df = parse_and_validate(ledger_bytes)
        settlement_df = parse_and_validate(settlement_bytes)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail={"message": e.message, "row": e.row, "field": e.field})

    run = ReconciliationRun(
        created_by=user.id,
        ledger_filename=ledger_file.filename,
        settlement_filename=settlement_file.filename,
        status=RunStatus.processing,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    persist_transactions(db, run.id, ledger_df, TransactionSource.ledger)
    persist_transactions(db, run.id, settlement_df, TransactionSource.settlement)

    run_reconciliation(db, run.id)

    return {"run_id": run.id, "status": "processing"}


@router.get("/runs")
def list_runs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """PR-2: an Analyst only sees their own runs; Admins see everything."""
    query = db.query(ReconciliationRun)
    if user.role.value != "admin":
        query = query.filter(ReconciliationRun.created_by == user.id)
    return query.order_by(ReconciliationRun.created_at.desc()).all()


@router.get("/runs/{run_id}")
def get_run(run_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    run = db.query(ReconciliationRun).filter(ReconciliationRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    if user.role.value != "admin" and run.created_by != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to view this run")
    return run


@router.get("/runs/{run_id}/flags")
def get_run_flags(run_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list_flags_for_run(db, run_id)
