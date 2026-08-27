"""Post-generation grounding check for AI explanations.

Core guardrail (knowledge.md Section 2): the LLM is only allowed to phrase
already-computed facts, never invent numbers. This module is the enforcement
mechanism for that rule — it runs after every explanation is generated and
checks whether every number the model mentioned actually traces back to real,
verified data. This is defense in depth: even if the prompt fails to fully
constrain the model, this catches it before anyone trusts the explanation.
"""

import re
from decimal import Decimal

NUMBER_PATTERN = re.compile(r"\d+(?:,\d{3})*(?:\.\d+)?")
TOLERANCE = 1.0  # allows for reasonable rounding in phrasing (e.g. "about ₹50")


def _parse_numbers(text: str) -> list[float]:
    numbers = []
    for match in NUMBER_PATTERN.findall(text):
        try:
            numbers.append(float(match.replace(",", "")))
        except ValueError:
            continue
    return numbers


def check_grounded(explanation: str, allowed_numbers: set[float]) -> tuple[bool, list[float]]:
    """Returns (is_grounded, offending_numbers).

    allowed_numbers should include: the confidence score, the computed delta
    (if any), and the amount of every transaction related to the flag.
    Numbers like "2" or "3" from ordinary phrasing ("2-3 sentences") are
    common false positives at this scale, so very small integers are exempt —
    they carry no financial meaning on their own.
    """
    offending = []
    for number in _parse_numbers(explanation):
        if number < 10:
            continue  # small numbers are almost always phrasing, not financial figures
        if not any(abs(number - allowed) <= TOLERANCE for allowed in allowed_numbers):
            offending.append(number)

    return len(offending) == 0, offending
