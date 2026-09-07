from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from datetime import datetime

from backend.app.database.base import Base


class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)

    measurement_id = Column(
        Integer,
        ForeignKey("measurements.id"),
        nullable=False,
        index=True,
    )

    anomaly_type = Column(String, nullable=False)

    severity = Column(String, nullable=False)

    score = Column(Float, nullable=True)

    detected_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )