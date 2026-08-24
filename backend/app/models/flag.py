import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum, JSON, Text, Integer
from sqlalchemy.orm import relationship

from app.database import Base


class FlagType(str, enum.Enum):
    duplicate = "duplicate"
    missing_settlement = "missing_settlement"
    amount_mismatch = "amount_mismatch"
    timing_anomaly = "timing_anomaly"


class FlagStatus(str, enum.Enum):
    open = "open"
    approved = "approved"
    rejected = "rejected"
    escalated = "escalated"


class ExplanationStatus(str, enum.Enum):
    ok = "ok"
    unavailable = "unavailable"
    pending = "pending"


class Flag(Base):
    __tablename__ = "flags"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("reconciliation_runs.id"), nullable=False)

    flag_type = Column(Enum(FlagType), nullable=False)
    related_transaction_ids = Column(JSON, nullable=False)  # list[str]
    computed_delta = Column(Numeric, nullable=True)
    confidence_score = Column(Integer, nullable=False)

    ai_explanation = Column(Text, nullable=True)
    explanation_status = Column(Enum(ExplanationStatus), default=ExplanationStatus.pending)

    status = Column(Enum(FlagStatus), default=FlagStatus.open)
    reviewed_by = Column(String, ForeignKey("users.id"), nullable=True)
    review_comment = Column(Text, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    run = relationship("ReconciliationRun", back_populates="flags")
