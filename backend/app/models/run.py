import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Integer, Numeric, ForeignKey, Enum
from sqlalchemy.orm import relationship

from app.database import Base


class RunStatus(str, enum.Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"


class ReconciliationRun(Base):
    __tablename__ = "reconciliation_runs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    ledger_filename = Column(String, nullable=False)
    settlement_filename = Column(String, nullable=False)
    status = Column(Enum(RunStatus), default=RunStatus.processing, nullable=False)

    total_records = Column(Integer, default=0)
    matched_count = Column(Integer, default=0)
    flagged_count = Column(Integer, default=0)
    total_flagged_value = Column(Numeric, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    transactions = relationship("Transaction", back_populates="run")
    flags = relationship("Flag", back_populates="run")
