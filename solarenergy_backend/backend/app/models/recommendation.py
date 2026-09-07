from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from datetime import datetime

from backend.app.database.base import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)

    diagnosis_id = Column(
        Integer,
        ForeignKey("diagnoses.id"),
        nullable=False,
        index=True,
    )

    recommendation = Column(Text, nullable=False)

    action = Column(String, nullable=False)

    priority = Column(String, nullable=False)

    confidence = Column(Float, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )