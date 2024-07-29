import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import tomli
from azure.data.tables import TableServiceClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader

from noshow.api.app_helpers import (
    load_model,
)
from noshow.config import CLINIC_PHONENUMBERS, KEEP_SENSITIVE_DATA
from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import (
    load_appointment_json,
    process_appointments,
    process_postal_codes,
)
from noshow.preprocessing.utils import add_working_days

logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

credential = DefaultAzureCredential()
service = TableServiceClient(
    endpoint="https://noshow01dsa.table.core.windows.net/", credential=credential
)
call_predictions_client = service.get_table_client(table_name="callpredictions")
sensitive_info_client = service.get_table_client(table_name="sensitiveinfo")

with open(Path(__file__).parents[3] / "pyproject.toml", "rb") as f:
    config = tomli.load(f)

API_VERSION = config["project"]["version"]

api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


def get_bins():
    with open(
        Path(__file__).parents[3] / "data" / "processed" / "fixed_pred_score_bin.json",
        "r",
    ) as f:
        fixed_bins = json.load(f)
    return fixed_bins


def get_api_key(api_key_header: str = Security(api_key_header)) -> str:
    if api_key_header == os.getenv("X_API_KEY", ""):
        return api_key_header
    else:
        raise HTTPException(403, "Unauthorized, Api Key not valid")


@app.post("/predict")
async def predict(
    input: List[Dict],
    start_date: Optional[str] = None,
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
        by default the date in 3 weekdays (i.e. excluding the weekend)

    Returns
    -------
    Dict[str, Any]
        Prediction output in FHIR format
    """
    if start_date is None:
        start_date_dt = add_working_days(datetime.today(), 3)
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
            "name_text": row["name_text"],
            "name_given1_callMe": row["name_given1_callMe"],
            "birthDate": str(row["birthDate"]),
            "telecom1_value": row["telecom1_value"],
            "telecom2_value": row["telecom2_value"],
            "telecom3_value": row["telecom3_value"],
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
