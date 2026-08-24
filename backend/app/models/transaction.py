import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum, JSON
from sqlalchemy.orm import relationship

from app.database import Base


class TransactionSource(str, enum.Enum):
    ledger = "ledger"
    settlement = "settlement"


class MatchStatus(str, enum.Enum):
    matched = "matched"
    flagged = "flagged"
    unmatched = "unmatched"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    run_id = Column(String, ForeignKey("reconciliation_runs.id"), nullable=False)
    source = Column(Enum(TransactionSource), nullable=False)

    external_txn_id = Column(String, nullable=False, index=True)
    amount = Column(Numeric, nullable=False)
    currency = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    counterparty = Column(String, nullable=True)
    raw_row = Column(JSON, nullable=True)

    match_status = Column(Enum(MatchStatus), default=MatchStatus.unmatched)

    run = relationship("ReconciliationRun", back_populates="transactions")
