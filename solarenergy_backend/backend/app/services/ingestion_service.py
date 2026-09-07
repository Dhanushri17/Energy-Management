from sqlalchemy.orm import Session

from backend.app.models.measurement import Measurement


def save_measurement(
    db: Session,
    measurement_data: dict,
) -> Measurement:
    """
    Store a validated measurement in the database.

    The API layer is responsible for request validation.
    This service is responsible for measurement persistence.
    """

    new_measurement = Measurement(
        **measurement_data
    )

    db.add(new_measurement)
    db.commit()
    db.refresh(new_measurement)

    return new_measurement