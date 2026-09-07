from sqlalchemy import Column, Integer, String, Float
from backend.app.database.base import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    capacity = Column(Float, nullable=False)
    location = Column(String, nullable=True)