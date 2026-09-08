from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationResponse,
)
from backend.app.models.recommendation import Recommendation


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=RecommendationResponse)
def create_recommendation(
    recommendation: RecommendationCreate,
    db: Session = Depends(get_db),
):
    new_recommendation = Recommendation(
        **recommendation.model_dump()
    )

    db.add(new_recommendation)
    db.commit()
    db.refresh(new_recommendation)

    return new_recommendation


@router.get("/", response_model=list[RecommendationResponse])
def get_recommendations(
    db: Session = Depends(get_db),
):
    recommendations = (
        db.query(Recommendation)
        .all()
    )

    return recommendations