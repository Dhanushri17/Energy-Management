from datetime import datetime
from pydantic import BaseModel


class DiagnosisCreate(BaseModel):
    anomaly_id: int
    diagnosis: str
    probable_cause: str | None = None
    confidence: float | None = None


class DiagnosisResponse(DiagnosisCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True