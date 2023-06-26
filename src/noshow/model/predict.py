import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from noshow.features.feature_pipeline import create_features
from noshow.preprocessing.load_data import process_appointments, process_postal_codes


def create_prediction(
    model: Any,
    appointments_df: pd.DataFrame,
    all_postal_codes: pd.DataFrame,
) -> np.ndarray:
    featuretable = create_features(appointments_df, all_postal_codes)

    featuretable = featuretable[
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
    prediction_probs: np.ndarray = model.predict_proba(featuretable)
    return prediction_probs


if __name__ == "__main__":
    project_folder = Path(__file__).parents[3]
    data_path = project_folder / "data" / "raw"
    output_path = project_folder / "data" / "processed"

    appointments_df = process_appointments(data_path / "poliafspraken_no_show.csv")
    all_postal_codes = process_postal_codes(data_path / "NL.txt")
    with open(
        project_folder / "output" / "models" / "no_show_model_cv.pickle", "rb"
    ) as f:
        model = pickle.load(f)
    predictions = create_prediction(model, appointments_df, all_postal_codes)
    print(predictions)