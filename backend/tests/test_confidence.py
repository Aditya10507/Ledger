from app.explanation.confidence import compute_confidence


def test_confidence_is_deterministic():
    # Same input must always produce the same output (FR-19).
    a = compute_confidence("amount_mismatch", 50)
    b = compute_confidence("amount_mismatch", 50)
    assert a == b


def test_confidence_bounded_at_100():
    score = compute_confidence("duplicate", 9999)
    assert score <= 100


def test_confidence_unknown_type_uses_default():
    score = compute_confidence("something_new", None)
    assert 0 <= score <= 100
