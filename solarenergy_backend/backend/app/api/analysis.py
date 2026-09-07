from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.app.database.connection import engine
from backend.app.models.measurement import Measurement
from backend.app.models.prediction import Prediction
from backend.app.models.anomaly import Anomaly
from backend.app.models.diagnosis import Diagnosis
from backend.app.models.recommendation import Recommendation
from backend.app.services.intelligence_service import (
    run_intelligence_engine,
)
from backend.app.services.diagnosis_service import (
    run_diagnosis_engine,
)


router = APIRouter(
    prefix="/analysis",
    tags=["Analysis"],
)


def get_db():
    db = Session(bind=engine)
    try:
        yield db
    finally:
        db.close()


@router.get("/{measurement_id}")
def analyze_measurement(
    measurement_id: int,
    db: Session = Depends(get_db),
):
    # 1. Get measurement
    measurement = (
        db.query(Measurement)
        .filter(Measurement.id == measurement_id)
        .first()
    )

    if measurement is None:
        raise HTTPException(
            status_code=404,
            detail="Measurement not found",
        )

    # 2. Prepare current measurement data
    measurement_data = {
        "plant_id": measurement.plant_id,
        "timestamp": measurement.timestamp,
        "irradiance": measurement.irradiance,
        "temperature": measurement.temperature,
        "dc_voltage": measurement.dc_voltage,
        "dc_current": measurement.dc_current,
        "ac_power": measurement.ac_power,
        "battery_soc": measurement.battery_soc,
        "inverter_status": measurement.inverter_status,
    }

    # 3. Get historical measurements
    historical_measurements = (
        db.query(Measurement)
        .filter(
            Measurement.plant_id == measurement.plant_id,
            Measurement.id != measurement.id,
            Measurement.timestamp < measurement.timestamp,
        )
        .order_by(Measurement.timestamp.desc())
        .limit(10)
        .all()
    )

    historical_data = [
        {
            "plant_id": item.plant_id,
            "timestamp": item.timestamp,
            "irradiance": item.irradiance,
            "temperature": item.temperature,
            "dc_voltage": item.dc_voltage,
            "dc_current": item.dc_current,
            "ac_power": item.ac_power,
            "battery_soc": item.battery_soc,
            "inverter_status": item.inverter_status,
        }
        for item in historical_measurements
    ]

    # 4. Run Intelligence Core
    try:
        intelligence_result = run_intelligence_engine(
            measurement_data=measurement_data,
            historical_data=historical_data,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Intelligence analysis failed: {str(exc)}",
        )

    # 5. Validate Intelligence Core result
    required_intelligence_fields = [
        "predicted_power",
        "actual_power",
        "deviation_percent",
        "anomaly",
        "severity",
        "historical_comparison",
        "quantitative_analysis",
        "data_quality",
        "evidence",
    ]

    missing_intelligence_fields = [
        field
        for field in required_intelligence_fields
        if field not in intelligence_result
    ]

    if missing_intelligence_fields:
        raise HTTPException(
            status_code=500,
            detail=(
                "Intelligence Core returned an incomplete result. "
                f"Missing fields: {missing_intelligence_fields}"
            ),
        )

    anomaly_data = intelligence_result.get("anomaly") or {}

    if "score" not in anomaly_data:
        raise HTTPException(
            status_code=500,
            detail="Intelligence Core anomaly result is incomplete.",
        )

    # 6. Find existing prediction
    prediction = (
        db.query(Prediction)
        .filter(
            Prediction.measurement_id == measurement.id
        )
        .first()
    )

    # 7. Create or update prediction
    if prediction is None:
        prediction = Prediction(
            measurement_id=measurement.id,
            predicted_power=intelligence_result["predicted_power"],
            actual_power=intelligence_result["actual_power"],
            deviation_percent=intelligence_result[
                "deviation_percent"
            ],
        )
        db.add(prediction)
    else:
        prediction.predicted_power = intelligence_result[
            "predicted_power"
        ]
        prediction.actual_power = intelligence_result[
            "actual_power"
        ]
        prediction.deviation_percent = intelligence_result[
            "deviation_percent"
        ]

    # 8. Find existing anomaly
    anomaly = (
        db.query(Anomaly)
        .filter(
            Anomaly.measurement_id == measurement.id
        )
        .first()
    )

    # 9. Create or update anomaly
    anomaly_type = anomaly_data.get("type")
    anomaly_severity = intelligence_result.get("severity")

    if anomaly is None:
        anomaly = Anomaly(
            measurement_id=measurement.id,
            anomaly_type=(
                anomaly_type
                if anomaly_type is not None
                else "NONE"
            ),
            severity=(
                anomaly_severity
                if anomaly_severity is not None
                else "LOW"
            ),
            score=anomaly_data.get("score"),
        )
        db.add(anomaly)
    else:
        anomaly.anomaly_type = (
            anomaly_type
            if anomaly_type is not None
            else "NONE"
        )
        anomaly.severity = (
            anomaly_severity
            if anomaly_severity is not None
            else "LOW"
        )
        anomaly.score = anomaly_data.get("score")

    # 10. Save prediction and anomaly together
    try:
        db.commit()
        db.refresh(prediction)
        db.refresh(anomaly)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to store intelligence results.",
        )

    # 11. Build evidence package
    evidence_package = {
        **measurement_data,
        **intelligence_result,
    }

    # 12. Run Diagnosis Agent
    try:
        diagnosis_result = run_diagnosis_engine(
            evidence_package
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Diagnosis analysis failed: {str(exc)}",
        )

    # 13. Validate Diagnosis Agent result
    required_diagnosis_fields = [
        "diagnosis",
        "probable_cause",
        "confidence",
        "recommendation",
        "action",
        "priority",
    ]

    missing_diagnosis_fields = [
        field
        for field in required_diagnosis_fields
        if field not in diagnosis_result
    ]

    if missing_diagnosis_fields:
        raise HTTPException(
            status_code=500,
            detail=(
                "Diagnosis Agent returned an incomplete result. "
                f"Missing fields: {missing_diagnosis_fields}"
            ),
        )

    # 14. Find existing diagnosis
    diagnosis = (
        db.query(Diagnosis)
        .filter(
            Diagnosis.anomaly_id == anomaly.id
        )
        .first()
    )

    # 15. Create or update diagnosis
    if diagnosis is None:
        diagnosis = Diagnosis(
            anomaly_id=anomaly.id,
            diagnosis=diagnosis_result["diagnosis"],
            probable_cause=diagnosis_result[
                "probable_cause"
            ],
            confidence=diagnosis_result[
                "confidence"
            ],
        )
        db.add(diagnosis)
    else:
        diagnosis.diagnosis = diagnosis_result[
            "diagnosis"
        ]
        diagnosis.probable_cause = diagnosis_result[
            "probable_cause"
        ]
        diagnosis.confidence = diagnosis_result[
            "confidence"
        ]

    # 16. Save diagnosis
    try:
        db.commit()
        db.refresh(diagnosis)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to store diagnosis result.",
        )

    # 17. Find existing recommendation
    recommendation = (
        db.query(Recommendation)
        .filter(
            Recommendation.diagnosis_id == diagnosis.id
        )
        .first()
    )

    # 18. Create or update recommendation
    if recommendation is None:
        recommendation = Recommendation(
            diagnosis_id=diagnosis.id,
            recommendation=diagnosis_result[
                "recommendation"
            ],
            action=diagnosis_result["action"],
            priority=diagnosis_result["priority"],
            confidence=diagnosis_result["confidence"],
        )
        db.add(recommendation)
    else:
        recommendation.recommendation = (
            diagnosis_result["recommendation"]
        )
        recommendation.action = diagnosis_result[
            "action"
        ]
        recommendation.priority = diagnosis_result[
            "priority"
        ]
        recommendation.confidence = diagnosis_result[
            "confidence"
        ]

    # 19. Save recommendation
    try:
        db.commit()
        db.refresh(recommendation)
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to store recommendation.",
        )

    # 20. Return complete analysis
    return {
        "measurement_id": measurement.id,
        "plant_id": measurement.plant_id,
        "ac_power": measurement.ac_power,
        "irradiance": measurement.irradiance,
        "temperature": measurement.temperature,
        "battery_soc": measurement.battery_soc,
        "inverter_status": measurement.inverter_status,
        "prediction": {
            "id": prediction.id,
            "predicted_power": prediction.predicted_power,
            "actual_power": prediction.actual_power,
            "deviation_percent": prediction.deviation_percent,
        },
        "intelligence": {
            "anomaly": intelligence_result["anomaly"],
            "severity": intelligence_result["severity"],
            "historical_comparison": intelligence_result[
                "historical_comparison"
            ],
            "quantitative_analysis": intelligence_result[
                "quantitative_analysis"
            ],
            "data_quality": intelligence_result[
                "data_quality"
            ],
            "evidence": intelligence_result["evidence"],
        },
        "diagnosis": {
            "id": diagnosis.id,
            "diagnosis": diagnosis.diagnosis,
            "probable_cause": diagnosis.probable_cause,
            "confidence": diagnosis.confidence,
        },
        "recommendation": {
            "id": recommendation.id,
            "recommendation": (
                recommendation.recommendation
            ),
            "action": recommendation.action,
            "priority": recommendation.priority,
            "confidence": recommendation.confidence,
        },
    }