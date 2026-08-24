from sqlalchemy.orm import Session

from app.models.audit_log import AuditLogEntry


def log_event(
    db: Session,
    entity_type: str,
    entity_id: str,
    action: str,
    actor: str,
    previous_state: dict | None = None,
    new_state: dict | None = None,
) -> None:
    """FR-25/FR-26: append-only audit log write.
    There is deliberately no update_event() or delete_event() function in this
    module — audit entries must never be modified once written (SEC-5).
    """
    entry = AuditLogEntry(
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        actor=actor,
        previous_state=previous_state,
        new_state=new_state,
    )
    db.add(entry)
    db.commit()
