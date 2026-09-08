from sqlalchemy import Column, Integer, String, Float, DateTime
from backend.app.database.base import Base


class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    plant_id = Column(String, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    irradiance = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    dc_voltage = Column(Float, nullable=True)
    dc_current = Column(Float, nullable=True)
    ac_power = Column(Float, nullable=True)
    battery_soc = Column(Float, nullable=True)
    inverter_status = Column(String, nullable=True)