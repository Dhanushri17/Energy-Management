from datetime import datetime
from pydantic import BaseModel


class AnomalyCreate(BaseModel):
    measurement_id: int
    anomaly_type: str
    severity: str
    score: float | None = None


class AnomalyResponse(AnomalyCreate):
    id: int
    detected_at: datetime

    class Config:
        from_attributes = True