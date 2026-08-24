from sqlalchemy.orm import Session

from app.explanation.claude_client import call_claude
from app.explanation.prompt_builder import build_prompt
from app.models.flag import ExplanationStatus, Flag


def generate_explanation(db: Session, flag: Flag) -> None:
    """FR-17/FR-20: generates and stores an explanation for a flag.
    A flag is always usable even if this fails — status is set to 'unavailable'
    rather than blocking the analyst's workflow.
    """
    prompt = build_prompt(flag)
    explanation = call_claude(prompt)

    if explanation:
        flag.ai_explanation = explanation
        flag.explanation_status = ExplanationStatus.ok
    else:
        flag.ai_explanation = None
        flag.explanation_status = ExplanationStatus.unavailable

    db.commit()
