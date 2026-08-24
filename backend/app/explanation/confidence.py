"""Deterministic confidence scoring — NEVER LLM-generated (FR-19).
Same input always produces the same score, which is what makes it auditable.
"""

BASE_SCORES = {
    "duplicate": 80,
    "missing_settlement": 70,
    "amount_mismatch": 60,
    "timing_anomaly": 50,
}


def compute_confidence(flag_type, delta) -> int:
    flag_type_str = flag_type.value if hasattr(flag_type, "value") else str(flag_type)
    score = BASE_SCORES.get(flag_type_str, 50)
    if delta:
        score = min(100, score + min(20, int(abs(delta))))
    return score
