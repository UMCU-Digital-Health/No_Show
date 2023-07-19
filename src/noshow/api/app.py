import configparser
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, cast

from fastapi import Depends, FastAPI
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from noshow.api.app_helpers import load_model
from noshow.database.models import ApiPrediction, ApiRequest, ApiSensitiveInfo, Base
from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import (
    load_appointment_json,
    process_appointments,
    process_postal_codes,
)

app = FastAPI()

config = configparser.ConfigParser()
config.read(Path(__file__).parents[3] / "setup.cfg")
API_VERSION = config["api"]["version"]

DB_USER = os.getenv("DB_USER", "")
DB_PASSWD = os.getenv("DB_PASSWD", "")
DB_HOST = os.getenv("DB_HOST", "")
DB_PORT = os.getenv("DB_PORT", 1433)
DB_DATABASE = os.getenv("DB_DATABASE", "")

if DB_USER == "":
    print("Using debug SQLite database...")
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
    execution_options = {"schema_translate_map": {"no_show": None}}
else:
    SQLALCHEMY_DATABASE_URL = (
        rf"mssql+pymssql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
    execution_options = None

engine = create_engine(SQLALCHEMY_DATABASE_URL, execution_options=execution_options)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
        db.close()
    except Exception as e:
        print(e)


@app.post("/predict")
async def predict(input: List[Dict], db: Session = Depends(get_db)) -> List[Dict]:
    """
    Predict the probability of a patient having a no-show.

    Parameters
    ----------
    input : List[Dict[str, str]]
        List of dictionaries containing the input data of a single patient.

    Returns
    -------
    Dict[str, Any]
        Prediction output in FHIR format
    """
    project_path = Path(__file__).parents[3]
    start_time = datetime.now()

    input_df = load_appointment_json(input)
    appointments_df = process_appointments(input_df)
    all_postalcodes = process_postal_codes(project_path / "data" / "raw" / "NL.txt")

    model = load_model()
    prediction_df = create_prediction(
        model,
        appointments_df,
        all_postalcodes,
        filter_only_last=True,
        add_sensitive_info=True,
    )

    prediction_df = prediction_df.sort_values(
        "prediction", ascending=False
    ).reset_index()

    # Remove all previous sensitive info like name, phonenumber
    db.query(ApiSensitiveInfo).delete()

    end_time = datetime.now()
    apirequest = ApiRequest(
        timestamp=start_time,
        api_version=API_VERSION,
        response_code=200,
        response_message="success",
        endpoint="predict",
        runtime=(end_time - start_time).total_seconds(),
    )
    for idx, row in prediction_df.iterrows():
        idx = cast(int, idx)
        apisensitive = ApiSensitiveInfo(
            full_name=row["name_text"],
            first_name=row["name_given1_callMe"],
            mobile_phone=row["telecom1_value"],
            home_phone=row["telecom2_value"],
            other_phone=row["telecom3_value"],
            clinic_reception=row["description"],
            clinic_phone_number="0582",  # TODO: find way to get number
        )
        apiprediction = ApiPrediction(
            patient_id=row["pseudo_id"],
            prediction=row["prediction"],
            call_order=idx,
            start_time=row["start"],
            request_relation=apirequest,
            sensitiveinfo_relation=apisensitive,
        )
        db.add(apiprediction)

    db.commit()
    return prediction_df.reset_index().to_dict(orient="records")


@app.get("/")
async def root():
    """Return a standard response."""
    return {"message": "UMCU <3"}


@app.get("/database")
async def debug_db(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Prints all the ApiPredictions from the database
    TODO: REMOVE BEFORE GOING LIVE!!
    """
    result_json = []
    for result in db.scalars(select(ApiPrediction)):
        result_json.append({"db_entry": str(result)})

    return result_json
