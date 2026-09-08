from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.schemas.prediction import PredictionCreate, PredictionResponse
from backend.app.models.prediction import Prediction


router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PredictionResponse)
def create_prediction(
    prediction: PredictionCreate,
    db: Session = Depends(get_db),
):
    new_prediction = Prediction(**prediction.model_dump())

    db.add(new_prediction)
    db.commit()
    db.refresh(new_prediction)

    return new_prediction


@router.get("/", response_model=list[PredictionResponse])
def get_predictions(
    db: Session = Depends(get_db),
):
    predictions = db.query(Prediction).all()
    return predictions