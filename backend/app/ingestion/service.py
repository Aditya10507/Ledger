from io import BytesIO

import pandas as pd
from sqlalchemy.orm import Session

from app.ingestion.validators import validate_csv
from app.models.transaction import Transaction, TransactionSource


def parse_and_validate(file_bytes: bytes) -> pd.DataFrame:
    # Handle BOM (Byte Order Mark) from Windows/Excel exports and try multiple encodings
    for encoding in ("utf-8-sig", "utf-8", "latin-1", "cp1252"):
        try:
            df = pd.read_csv(BytesIO(file_bytes), encoding=encoding)
            # If we got columns but they have BOM prefix, strip them
            df.columns = [c.strip().lstrip("\ufeff") for c in df.columns]
            if not df.empty or len(df.columns) > 0:
                break
        except (UnicodeDecodeError, pd.errors.EmptyDataError):
            continue
    else:
        df = pd.DataFrame()

    validate_csv(df)
    return df


def persist_transactions(db: Session, run_id: str, df: pd.DataFrame, source: TransactionSource) -> int:
    """FR-7: persists raw transaction records tagged by source and run."""
    count = 0
    for _, row in df.iterrows():
        txn = Transaction(
            run_id=run_id,
            source=source,
            external_txn_id=str(row["transaction_id"]).strip(),
            amount=float(row["amount"]),
            currency=str(row["currency"]).strip().upper(),
            timestamp=pd.to_datetime(row["timestamp"]),
            counterparty=row.get("counterparty") if "counterparty" in row else None,
            raw_row=row.to_dict(),
        )
        db.add(txn)
        count += 1
    db.commit()
    return count
