from sqlalchemy import Column, Integer, Text, Float, DateTime, ForeignKey
from datetime import datetime

from backend.app.database.base import Base


class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, index=True)

    anomaly_id = Column(
        Integer,
        ForeignKey("anomalies.id"),
        nullable=False,
        index=True,
    )

    diagnosis = Column(Text, nullable=False)

    probable_cause = Column(Text, nullable=True)

    confidence = Column(Float, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )