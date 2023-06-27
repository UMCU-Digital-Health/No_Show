import configparser
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List
import pickle
import pandas as pd

from fastapi import FastAPI
import json
from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import process_appointments, process_postal_codes, load_appointment_json
from noshow.features.feature_pipeline import create_features
sys.path.append("./src")

app = FastAPI()

config = configparser.ConfigParser()
config.read(Path(__file__).parents[3] / "setup.cfg")
API_VERSION = config["api"]["version"]


@app.post("/predict")
async def predict(input: List[Dict]):
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
    data_path = './data/raw/'
    input_df = load_appointment_json(input)
    appointments_df = process_appointments(input_df)
    all_postalcodes = process_postal_codes(data_path + "NL.txt")
    appointments_df['address_postalCodeNumbersNL'] = pd.to_numeric(appointments_df['address_postalCodeNumbersNL'], errors='coerce')
    appointments_df.address_postalCodeNumbersNL.astype('float')
    appointments_features = create_features(appointments_df, all_postalcodes)
    appointments_features = appointments_features[
        [
            "hour",
            "weekday",
            "specialty_code",
            "minutesDuration",
            "no_show",
            "prev_no_show",
            "prev_no_show_perc",
            "age",
            "dist_umcu",
            "prev_minutes_early",
            "earlier_appointments",
            "appointments_same_day",
            "days_since_created",
        ]
    ]
    with open(
        "./output/models/no_show_model_cv.pickle", "rb"
    ) as f:
        model = pickle.load(f)
    prediction_probs = create_prediction(model, appointments_df, all_postalcodes)

    return prediction_probs

@app.get("/")
async def root():
    """Return a standard response."""
    return {"message": "UMCU <3"}