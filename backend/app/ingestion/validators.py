import pandas as pd

REQUIRED_COLUMNS = {"transaction_id", "amount", "currency", "timestamp"}


class ValidationError(Exception):
    """Raised on any file-level or row-level validation failure (SRS Section 6)."""

    def __init__(self, message: str, row: int | None = None, field: str | None = None):
        self.message = message
        self.row = row
        self.field = field
        super().__init__(message)


def validate_csv(df: pd.DataFrame) -> None:
    """Validates schema + row-level data per SRS V-1 through V-5.
    Raises ValidationError with a specific, actionable message on any failure —
    never silently drops rows or fails generically.
    """
    columns = {c.strip().lower() for c in df.columns}
    missing = REQUIRED_COLUMNS - columns
    if missing:
        raise ValidationError(f"Missing required columns: {', '.join(sorted(missing))}")

    if df.empty:
        raise ValidationError("File contains no data rows")

    df.columns = [c.strip().lower() for c in df.columns]

    # V-3: transaction_id must be unique within a single source file
    if df["transaction_id"].duplicated().any():
        raise ValidationError("Duplicate transaction_id values found within the same file")

    for idx, row in df.iterrows():
        # V-1: amount must be numeric and > 0
        try:
            amount = float(row["amount"])
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            raise ValidationError("amount must be a positive number", row=idx + 2, field="amount")

        # V-2: timestamp must parse
        try:
            pd.to_datetime(row["timestamp"])
        except Exception:
            raise ValidationError("timestamp could not be parsed", row=idx + 2, field="timestamp")

        if pd.isna(row["transaction_id"]) or str(row["transaction_id"]).strip() == "":
            raise ValidationError("transaction_id cannot be empty", row=idx + 2, field="transaction_id")

    # V-4: single currency per run
    if df["currency"].nunique() > 1:
        raise ValidationError("Multiple currencies found in one file — a run must use a single currency")
