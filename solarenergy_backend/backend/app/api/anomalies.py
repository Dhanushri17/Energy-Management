from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.schemas.anomaly import AnomalyCreate, AnomalyResponse
from backend.app.models.anomaly import Anomaly


router = APIRouter(
    prefix="/anomalies",
    tags=["Anomalies"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=AnomalyResponse)
def create_anomaly(
    anomaly: AnomalyCreate,
    db: Session = Depends(get_db),
):
    new_anomaly = Anomaly(**anomaly.model_dump())

    db.add(new_anomaly)
    db.commit()
    db.refresh(new_anomaly)

    return new_anomaly


@router.get("/", response_model=list[AnomalyResponse])
def get_anomalies(
    db: Session = Depends(get_db),
):
    anomalies = db.query(Anomaly).all()
    return anomalies