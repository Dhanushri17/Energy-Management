from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.schemas.diagnosis import DiagnosisCreate, DiagnosisResponse
from backend.app.models.diagnosis import Diagnosis


router = APIRouter(
    prefix="/diagnoses",
    tags=["Diagnoses"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=DiagnosisResponse)
def create_diagnosis(
    diagnosis: DiagnosisCreate,
    db: Session = Depends(get_db),
):
    new_diagnosis = Diagnosis(**diagnosis.model_dump())

    db.add(new_diagnosis)
    db.commit()
    db.refresh(new_diagnosis)

    return new_diagnosis


@router.get("/", response_model=list[DiagnosisResponse])
def get_diagnoses(
    db: Session = Depends(get_db),
):
    diagnoses = db.query(Diagnosis).all()
    return diagnoses