from datetime import datetime

from pydantic import BaseModel, Field


class MeasurementCreate(BaseModel):
    plant_id: str
    timestamp: datetime

    irradiance: float | None = Field(default=None, ge=0)
    temperature: float | None = None
    dc_voltage: float | None = Field(default=None, ge=0)
    dc_current: float | None = Field(default=None, ge=0)
    ac_power: float | None = Field(default=None, ge=0)
    battery_soc: float | None = Field(default=None, ge=0, le=100)
    inverter_status: str | None = None


class MeasurementResponse(MeasurementCreate):
    id: int

    class Config:
        from_attributes = True