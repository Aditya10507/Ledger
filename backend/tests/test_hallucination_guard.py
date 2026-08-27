from app.explanation.hallucination_guard import check_grounded


def test_grounded_explanation_passes():
    allowed = {2500.0, 50.0, 60.0}  # amount, delta, confidence
    explanation = (
        "This transaction was flagged because the ledger amount of 2500 did not "
        "match the settlement amount, a difference of 50. Confidence: 60."
    )
    is_grounded, offending = check_grounded(explanation, allowed)
    assert is_grounded is True
    assert offending == []


def test_hallucinated_number_is_caught():
    allowed = {2500.0, 50.0, 60.0}
    # 9999 does not correspond to any real computed value — a fabricated figure.
    explanation = "This transaction shows a suspicious pattern involving 9999 in prior fraud cases."
    is_grounded, offending = check_grounded(explanation, allowed)
    assert is_grounded is False
    assert 9999.0 in offending


def test_small_numbers_are_not_flagged_as_hallucinations():
    # "2-3 sentences" style phrasing shouldn't trigger false alarms.
    allowed = {2500.0}
    explanation = "In 2 to 3 words: this looks like a duplicate charge of 2500."
    is_grounded, offending = check_grounded(explanation, allowed)
    assert is_grounded is True


def test_rounding_within_tolerance_is_accepted():
    allowed = {2500.0}
    explanation = "The amount was approximately 2500.4, within normal rounding."
    is_grounded, offending = check_grounded(explanation, allowed)
    assert is_grounded is True


def test_multiple_hallucinated_numbers_all_reported():
    allowed = {100.0}
    explanation = "Similar cases involved 45000 and 78000 in losses."
    is_grounded, offending = check_grounded(explanation, allowed)
    assert is_grounded is False
    assert set(offending) == {45000.0, 78000.0}
