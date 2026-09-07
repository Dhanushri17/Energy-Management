from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.schemas.plant import PlantCreate, PlantResponse
from backend.app.models.plant import Plant


router = APIRouter(
    prefix="/plants",
    tags=["Plants"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=PlantResponse)
def create_plant(
    plant: PlantCreate,
    db: Session = Depends(get_db),
):
    new_plant = Plant(
        **plant.model_dump()
    )

    db.add(new_plant)

    try:
        db.commit()
        db.refresh(new_plant)
    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Plant with this plant_id already exists.",
        )

    return new_plant


@router.get("/", response_model=list[PlantResponse])
def get_plants(
    db: Session = Depends(get_db),
):
    plants = (
        db.query(Plant)
        .all()
    )

    return plants