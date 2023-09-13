import configparser
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import Session, sessionmaker

from noshow.api.app_helpers import load_model
from noshow.database.models import ApiPrediction, ApiRequest, ApiSensitiveInfo, Base
from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import (
    load_appointment_json,
    process_appointments,
    process_postal_codes,
)

load_dotenv()

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
    execution_options = {"schema_translate_map": {"noshow": None}}
else:
    SQLALCHEMY_DATABASE_URL = (
        rf"mssql+pymssql://{DB_USER}:{DB_PASSWD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"
    )
    execution_options = None

engine = create_engine(SQLALCHEMY_DATABASE_URL, execution_options=execution_options)
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


def get_db():
    try:
        db = SessionLocal()
        yield db
        db.close()
    except Exception as e:
        print(e)


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header == os.getenv("X_API_KEY", ""):
        return api_key_header
    else:
        raise HTTPException(403, "Unauthorized, Api Key not valid")


@app.post("/predict")
async def predict(
    input: List[Dict],
    start_date: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
) -> List[Dict]:
    """
    Predict the probability of a patient having a no-show.

    Parameters
    ----------
    input : List[Dict[str, str]]
        List of dictionaries containing the input data of a single patient.
    start_date: Optional[str]
        Start date of predictions, predictions will be made from that date,
        by default the date in 3 days (of after the weekend)

    Returns
    -------
    Dict[str, Any]
        Prediction output in FHIR format
    """
    if start_date is None:
        start_date_dt = datetime.today() + timedelta(days=3)
        if start_date_dt.weekday() == 5:
            start_date_dt = start_date_dt + timedelta(days=2)
        if start_date_dt.weekday() == 6:
            start_date_dt = start_date_dt + timedelta(days=1)
        start_date = start_date_dt.strftime(r"%Y-%m-%d")

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
        prediction_start_date=start_date,
        add_sensitive_info=True,
    )

    prediction_df = prediction_df.sort_values(
        "prediction", ascending=False
    ).reset_index()

    # Remove all previous sensitive info like name, phonenumber
    db.execute(delete(ApiSensitiveInfo))

    end_time = datetime.now()
    apirequest = ApiRequest(
        timestamp=start_time,
        api_version=API_VERSION,
        response_code=200,
        response_message="success",
        endpoint="predict",
        runtime=(end_time - start_time).total_seconds(),
    )
    db.add(apirequest)
    for _, row in prediction_df.iterrows():
        apisensitive = db.get(ApiSensitiveInfo, row["pseudo_id"])

        if not apisensitive:
            apisensitive = ApiSensitiveInfo(
                patient_id=row["pseudo_id"],
                full_name=row["name_text"],
                first_name=row["name_given1_callMe"],
                birth_date=row["birthDate"],
                mobile_phone=row["telecom1_value"],
                home_phone=row["telecom2_value"],
                other_phone=row["telecom3_value"],
            )
        else:
            # name and birthdate can't change, but phone number might
            apisensitive.mobile_phone = row["telecom1_value"]
            apisensitive.home_phone = row["telecom2_value"]
            apisensitive.other_phone = row["telecom3_value"]

        apiprediction = db.get(ApiPrediction, row["APP_ID"])
        if not apiprediction:
            apiprediction = ApiPrediction(
                id=row["APP_ID"],
                patient_id=row["pseudo_id"],
                prediction=row["prediction"],
                start_time=row["start"],
                request_relation=apirequest,
                clinic_reception=row["description"],
                clinic_phone_number="0582",  # TODO: find way to get number
            )
        else:
            # All values of a prediction can be updated except the ID fields
            apiprediction.prediction = row["prediction"]
            apiprediction.start_time = row["start"]
            apiprediction.request_relation = apirequest
            apiprediction.clinic_reception = row["description"]
            apiprediction.clinic_phone_number = "0582"

        db.merge(apisensitive)
        db.merge(apiprediction)
        db.commit()

    return prediction_df.reset_index().to_dict(orient="records")


@app.get("/")
async def root():
    """Return a standard response."""
    return {"message": "UMCU <3"}
