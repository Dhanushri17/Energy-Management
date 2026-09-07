from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from datetime import datetime

from backend.app.database.base import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)

    measurement_id = Column(
        Integer,
        ForeignKey("measurements.id"),
        nullable=False,
        index=True,
    )

    predicted_power = Column(Float, nullable=False)

    actual_power = Column(Float, nullable=True)

    deviation_percent = Column(Float, nullable=True)

    created_at = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )