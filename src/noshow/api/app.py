import json
import logging
import os
import tomllib
from datetime import datetime
from pathlib import Path
from typing import Optional

import tomli
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security.api_key import APIKeyHeader

from noshow.api.app_helpers import (
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

credential = DefaultAzureCredential()
service = TableServiceClient(
    endpoint="https://noshow01dsa.table.core.windows.net/", credential=credential
)
call_predictions_client = service.get_table_client(table_name="callpredictions")
sensitive_info_client = service.get_table_client(table_name="sensitiveinfo")

with open(Path(__file__).parents[3] / "pyproject.toml", "rb") as f:
    config = tomllib.load(f)

API_VERSION = config["project"]["version"]

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


def get_bins():
    with open(
        Path(__file__).parents[3] / "data" / "processed" / "fixed_pred_score_bin.json",
        "r",
    ) as f:
        fixed_bins = json.load(f)
    return fixed_bins


@app.post("/predict")
async def predict(
    appointments: list[Appointment],
    start_date: Optional[str] = None,
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

    # TODO better assign treatment group
    prediction_df["treatment_group"] = 2

    # Store pseudo_id, prediction in azure table storage
    for _, row in prediction_df.iterrows():
        entity = {
            "PartitionKey": row["pseudo_id"],
            "RowKey": row["APP_ID"],
            "start": str(row["start"]),
            "prediction": str(row["prediction"]),
            "treatment_group": str(row["treatment_group"]),
            "clinic_name": str(row["hoofdagenda"]),
            "clinic_reception": str(row["description"]),
            "clinic_phone_number": CLINIC_CONFIG[row["clinic"]].phone_number,
            "clinic_teleq_unit": CLINIC_CONFIG[row["clinic"]].teleq_unit,
            "api_version": API_VERSION,
            "response_code": 200,
            "response_message": "success",
            "endpoint": "predict",
            "runtime": (datetime.now() - start_time).total_seconds(),
        }
        call_predictions_client.upsert_entity(entity=entity)
        sensitive_entity = {
            "PartitionKey": row["pseudo_id"],
            "RowKey": row["APP_ID"],
            "hix_number": row["patient_id"],
            "name_text": row["name_text"],
            "name_given1_callMe": row["name_given1_callMe"],
            "birthDate": str(row["birthDate"]),
            "mobile_phone": row["telecom1_value"],
            "home_phone": row["telecom2_value"],
            "other_phone": row["telecom3_value"],
        }
        sensitive_info_client.upsert_entity(entity=sensitive_entity)

    # Get entities from azure table storage that have a start date more than 7 days ago
    # TODO gebruik LOOKBACK_DAYS
    deletable_entities = call_predictions_client.query_entities(
        query_filter=f"start lt '{start_date}'"
    )
    # retrieve partitionkey and rowkey from entities
    entities = [
        {"PartitionKey": entity["PartitionKey"], "RowKey": entity["RowKey"]}
        for entity in deletable_entities
    ]
    # delete entities from azure table storage
    for entity in entities:
        sensitive_info_client.delete_entity(entity["PartitionKey"], entity["RowKey"])

    # TODO: fix outdated
    # fix_outdated_appointments(db, prediction_df["APP_ID"], start_date)

    return prediction_df.reset_index().to_dict(orient="records")


@app.get("/")
async def root():
    """Return a standard response."""
    return {"message": "UMCU <3"}
