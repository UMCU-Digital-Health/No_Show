import json
import logging
import os
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session, sessionmaker

from noshow.api.app_helpers import (
    create_treatment_groups,
    fix_outdated_appointments,
    load_model,
    remove_sensitive_info,
    store_predictions,
)
from noshow.api.pydantic_models import Appointment
from noshow.config import CLINIC_CONFIG, KEEP_SENSITIVE_DATA, setup_root_logger
from noshow.database.connection import get_engine
from noshow.database.models import (
    ApiRequest,
    Base,
)
from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import (
    load_appointment_pydantic,
    process_appointments,
    process_postal_codes,
)
from noshow.preprocessing.utils import add_working_days

logger = logging.getLogger(__name__)
setup_root_logger()

load_dotenv()

app = FastAPI()

with open(Path(__file__).parents[3] / "pyproject.toml", "rb") as f:
    config = tomllib.load(f)

API_VERSION = config["project"]["version"]

engine = get_engine()
Base.metadata.create_all(engine)
SessionLocal = sessionmaker(bind=engine)

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


def get_bins():
    with open(
        Path(__file__).parents[3] / "data" / "processed" / "fixed_pred_score_bin.json",
        "r",
    ) as f:
        fixed_bins = json.load(f)
    return fixed_bins


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/predict")
async def predict(
    appointments: list[Appointment],
    start_date: Optional[str] = None,
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_header),
) -> dict:
    """
    Predict the probability of a patient having a no-show.

    Parameters
    ----------
    appointments : list[Appointment]
        List of appointments containing the input data of multiple patient.
    start_date: Optional[str]
        Start date of predictions, predictions will be made from that date,
        by default the date in 3 weekdays (i.e. excluding the weekend)

    Returns
    -------
    dict[str, Any]
       A dictionary containing a message with the number of predictions stored
    """
    if api_key != os.environ["X_API_KEY"]:
        logger.error("403: Unauthorized, Api Key not valid")
        raise HTTPException(403, "Unauthorized, Api Key not valid")

    if start_date is None:
        start_date_dt = add_working_days(datetime.today(), 3)
        start_date = start_date_dt.strftime(r"%Y-%m-%d")
        logger.warning(f"No start date provided, using {start_date}")

    project_path = Path(__file__).parents[3]
    start_time = datetime.now()

    if len(appointments) == 0:
        logger.error("400: Input cannot be empty.")
        raise HTTPException(status_code=400, detail="Input cannot be empty.")

    appointments_df = load_appointment_pydantic(appointments)
    appointments_df = process_appointments(appointments_df, CLINIC_CONFIG, start_date)
    all_postalcodes = process_postal_codes(project_path / "data" / "raw" / "NL.txt")

    if appointments_df.empty:
        logger.error("400: No appointments for the start date and filters")
        raise HTTPException(
            status_code=400, detail="No appointments for the start date and filters"
        )

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

    rct_agendas = [
        clinic for clinic, config in CLINIC_CONFIG.items() if config.include_rct
    ]
    if rct_agendas is None or len(rct_agendas) == 0:
        logger.info("No RCT agendas, defaulting to treatment group 2")
        prediction_df["treatment_group"] = 2
    else:
        prediction_df = create_treatment_groups(
            prediction_df, db, get_bins(), rct_agendas
        )

    remove_sensitive_info(db, start_date, lookback_days=KEEP_SENSITIVE_DATA)

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

    internal_pred_ids = store_predictions(prediction_df, db, apirequest)

    fix_outdated_appointments(db, internal_pred_ids, start_date)

    logger.info("Predict endpoint finished successfully.")
    return {"message": f"{len(prediction_df)} predictions created and stored in db."}


@app.get("/")
async def root():
    """Return a standard response."""
    return {"message": "UMCU <3"}
