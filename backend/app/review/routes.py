from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.audit.service import log_event
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.audit_log import AuditLogEntry
from app.models.flag import Flag, FlagStatus
from app.models.user import User

router = APIRouter(prefix="/flags", tags=["review"])


class DecisionRequest(BaseModel):
    decision: str  # "approved" | "rejected" | "escalated"
    comment: str | None = None


@router.get("/{flag_id}")
def get_flag(flag_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    flag = db.query(Flag).filter(Flag.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    return flag


@router.post("/{flag_id}/decision")
def record_decision(
    flag_id: str,
    payload: DecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """FR-21/FR-22/FR-23: every decision is attributed, timestamped, and logged.
    FR-24: changing a decision later creates a NEW audit entry — history is preserved.
    """
    flag = db.query(Flag).filter(Flag.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    if payload.decision not in ("approved", "rejected", "escalated"):
        raise HTTPException(status_code=400, detail="Invalid decision value")

    if payload.decision == "escalated" and not (payload.comment and payload.comment.strip()):
        raise HTTPException(status_code=400, detail="A comment is required when escalating a flag")

    previous_state = {"status": flag.status.value}

    flag.status = FlagStatus(payload.decision)
    flag.reviewed_by = user.id
    flag.review_comment = payload.comment
    flag.reviewed_at = datetime.utcnow()
    db.commit()

    log_event(
        db,
        entity_type="flag",
        entity_id=flag.id,
        action=f"decision:{payload.decision}",
        actor=user.id,
        previous_state=previous_state,
        new_state={"status": flag.status.value, "comment": payload.comment},
    )

    return {"flag_id": flag.id, "status": flag.status.value}


@router.get("/{flag_id}/audit-trail")
def flag_audit_trail(flag_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return (
        db.query(AuditLogEntry)
        .filter(AuditLogEntry.entity_type == "flag", AuditLogEntry.entity_id == flag_id)
        .order_by(AuditLogEntry.timestamp.asc())
        .all()
    )
