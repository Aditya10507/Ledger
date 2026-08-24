import pandas as pd
import pytest

from app.ingestion.validators import ValidationError, validate_csv


def _df(rows, columns=("transaction_id", "amount", "currency", "timestamp")):
    return pd.DataFrame(rows, columns=list(columns))


def test_valid_csv_passes():
    df = _df([["TXN1", 100, "INR", "2026-08-01T10:00:00"]])
    validate_csv(df)  # should not raise


def test_missing_column_rejected():
    df = pd.DataFrame([[100, "INR"]], columns=["amount", "currency"])
    with pytest.raises(ValidationError):
        validate_csv(df)


def test_empty_file_rejected():
    df = _df([])
    with pytest.raises(ValidationError):
        validate_csv(df)


def test_negative_amount_rejected():
    df = _df([["TXN1", -50, "INR", "2026-08-01T10:00:00"]])
    with pytest.raises(ValidationError):
        validate_csv(df)


def test_duplicate_transaction_id_rejected():
    df = _df([
        ["TXN1", 100, "INR", "2026-08-01T10:00:00"],
        ["TXN1", 200, "INR", "2026-08-01T11:00:00"],
    ])
    with pytest.raises(ValidationError):
        validate_csv(df)


def test_mixed_currency_rejected():
    df = _df([
        ["TXN1", 100, "INR", "2026-08-01T10:00:00"],
        ["TXN2", 100, "USD", "2026-08-01T10:00:00"],
    ])
    with pytest.raises(ValidationError):
        validate_csv(df)
