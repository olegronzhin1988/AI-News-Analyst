# analysis.py includes models for ai agent response results - records

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Text, JSON
from database import Base
from datetime import datetime, timezone

# Class for ai agent results
class AnalysisRecord(Base):
    __tablename__="analysis_records"

# Record id
    id: Mapped[int] = mapped_column(primary_key=True,
                                    autoincrement=True)
# Topic of analysis
    topic: Mapped[str] = mapped_column(nullable=False,
                                       index=True)
# Days interval used for search
    days: Mapped[int] = mapped_column(Integer)
# Articles found
    articles_found: Mapped[int] = mapped_column(Integer)
# Articles analyzed
    articles_analyzed: Mapped[int] = mapped_column(Integer)
# Sentiment results of analysis
    sentiment_positive: Mapped[int] = mapped_column(Integer)
    sentiment_neutral: Mapped[int] = mapped_column(Integer)
    sentiment_negative: Mapped[int] = mapped_column(Integer)
# Analysus result summary
    summary: Mapped[str] = mapped_column(Text)
# Analysis key events
    key_events: Mapped[list] = mapped_column(JSON, default=list)
# Analysis sourses
    sources: Mapped[list] = mapped_column(JSON, default=list)
# Analysis AI Provider
    ai_provider_used: Mapped[str]
# Analysis creation date and time
    created_at:Mapped[datetime] = mapped_column(default=lambda:datetime.now(timezone.utc))
