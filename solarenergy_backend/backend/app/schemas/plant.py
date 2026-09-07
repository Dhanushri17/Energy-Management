from pydantic import BaseModel


class PlantCreate(BaseModel):
    plant_id: str
    name: str
    capacity: float
    location: str | None = None


class PlantResponse(PlantCreate):
    id: int

    class Config:
        from_attributes = True