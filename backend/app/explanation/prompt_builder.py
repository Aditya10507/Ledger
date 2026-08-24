"""Builds the LLM prompt for flag explanations.

CRITICAL (project guardrail — see knowledge.md Section 2):
The LLM never decides whether something is an anomaly, and never invents numbers.
It is only given already-computed, verified facts and asked to phrase them clearly.
"""


def build_prompt(flag) -> str:
    flag_type_str = flag.flag_type.value if hasattr(flag.flag_type, "value") else str(flag.flag_type)

    return f"""You are explaining a financial reconciliation flag to a finance analyst.

Use ONLY the facts listed below. Do not invent numbers, causes, or transaction
details that are not explicitly listed here. Do not speculate about intent or fraud.
Write 2-3 plain-English sentences explaining what was flagged and why, suitable for
someone who needs to quickly decide whether to approve, reject, or escalate this flag.

Flag type: {flag_type_str}
Related transaction IDs: {flag.related_transaction_ids}
Computed delta: {flag.computed_delta}
Confidence score: {flag.confidence_score}/100

Explanation:"""
