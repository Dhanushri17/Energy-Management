from datetime import datetime
from pydantic import BaseModel


class PredictionCreate(BaseModel):
    measurement_id: int
    predicted_power: float
    actual_power: float | None = None
    deviation_percent: float | None = None


class PredictionResponse(PredictionCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True