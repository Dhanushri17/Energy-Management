from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.schemas.measurement import (
    MeasurementCreate,
    MeasurementResponse,
)
from backend.app.models.measurement import Measurement
from backend.app.services.ingestion_service import save_measurement


router = APIRouter(
    prefix="/measurements",
    tags=["Measurements"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=MeasurementResponse)
def create_measurement(
    measurement: MeasurementCreate,
    db: Session = Depends(get_db),
):
    new_measurement = save_measurement(
        db=db,
        measurement_data=measurement.model_dump(),
    )

    return new_measurement


@router.get("/", response_model=list[MeasurementResponse])
def get_measurements(
    db: Session = Depends(get_db),
):
    measurements = (
        db.query(Measurement)
        .all()
    )

    return measurements