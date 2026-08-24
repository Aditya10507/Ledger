import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, JSON

from app.database import Base


class AuditLogEntry(Base):
    """Append-only. No update/delete route is ever exposed for this table —
    see app/audit/service.py. This is enforced architecturally, not just by convention.
    """

    __tablename__ = "audit_log_entries"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String, nullable=False)       # "run" | "flag"
    entity_id = Column(String, nullable=False, index=True)
    action = Column(String, nullable=False)             # e.g. "created", "decision:approved"
    actor = Column(String, nullable=False)               # "system" or a user id
    previous_state = Column(JSON, nullable=True)
    new_state = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
