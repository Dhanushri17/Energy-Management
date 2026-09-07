from datetime import datetime
from pydantic import BaseModel


class RecommendationCreate(BaseModel):
    diagnosis_id: int
    recommendation: str
    action: str
    priority: str
    confidence: float | None = None


class RecommendationResponse(RecommendationCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True