from fastapi import FastAPI

from backend.app.api.measurements import router as measurements_router
from backend.app.api.predictions import router as predictions_router
from backend.app.api.anomalies import router as anomalies_router
from backend.app.api.diagnoses import router as diagnoses_router
from backend.app.api.recommendations import router as recommendations_router
from backend.app.api.analysis import router as analysis_router
from backend.app.api.plant import router as plant_router


app = FastAPI(
    title="AI Energy Management Backend",
    description="Offline backend for the AI Energy Management System",
    version="1.0.0",
)


app.include_router(measurements_router)
app.include_router(predictions_router)
app.include_router(anomalies_router)
app.include_router(diagnoses_router)
app.include_router(recommendations_router)
app.include_router(analysis_router)
app.include_router(plant_router)


@app.get("/")
def root():
    return {
        "message": "AI Energy Management Backend is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }