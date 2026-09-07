from backend.app.database.base import Base
from backend.app.database.connection import engine
from backend.app.models.plant import Plant
from backend.app.models.measurement import Measurement
from backend.app.models.prediction import Prediction
from backend.app.models.anomaly import Anomaly
from backend.app.models.diagnosis import Diagnosis
from backend.app.models.recommendation import Recommendation


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("PLANT TABLE CREATED SUCCESSFULLY")