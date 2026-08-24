from sqlalchemy.orm import Session

from app.models.flag import Flag


def list_flags_for_run(db: Session, run_id: str, status: str | None = None):
    query = db.query(Flag).filter(Flag.run_id == run_id)
    if status:
        query = query.filter(Flag.status == status)
    # Highest-risk flags first — matches the UI/UX plan's default Flag List sort.
    return query.order_by(Flag.confidence_score.desc()).all()
