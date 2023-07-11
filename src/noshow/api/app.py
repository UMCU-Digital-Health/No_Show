import configparser
import sys
from pathlib import Path
from typing import Dict, List

from fastapi import FastAPI

from noshow.api.app_helpers import load_model
from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import (
    load_appointment_json,
    process_appointments,
    process_postal_codes,
)

sys.path.append("./src")

app = FastAPI()

config = configparser.ConfigParser()
config.read(Path(__file__).parents[3] / "setup.cfg")
API_VERSION = config["api"]["version"]


@app.post("/predict")
async def predict(input: List[Dict]) -> List[Dict]:
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
    input_df = load_appointment_json(input)
    appointments_df = process_appointments(input_df)
    all_postalcodes = process_postal_codes(project_path / "data" / "raw" / "NL.txt")

    model = load_model()
    prediction_df = create_prediction(
        model, appointments_df, all_postalcodes, filter_only_booked=True
    )

    return prediction_df.reset_index().to_dict(orient="records")


@app.get("/")
async def root():
    """Return a standard response."""
    return {"message": "UMCU <3"}
