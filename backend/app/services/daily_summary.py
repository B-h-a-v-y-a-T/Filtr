from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models import DailySummary


def save_daily_summary(
    db: Session, title: str, summary: str, source: str
):
    row = DailySummary(
        title=title,
        summary=summary,
        source=source
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_summaries(db: Session):
    result = db.execute(
        select(DailySummary).order_by(DailySummary.id.desc())
    )
    return result.scalars().all()
