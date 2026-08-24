from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import require_admin
from app.database import get_db
from app.models.audit_log import AuditLogEntry

router = APIRouter(prefix="/audit-log", tags=["audit"])


@router.get("")
def global_audit_log(
    entity_type: str | None = None,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """FR-29 / Admin-only: cross-run audit visibility."""
    query = db.query(AuditLogEntry)
    if entity_type:
        query = query.filter(AuditLogEntry.entity_type == entity_type)
    return query.order_by(AuditLogEntry.timestamp.desc()).all()
