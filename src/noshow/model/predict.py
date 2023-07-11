import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from noshow.features.feature_pipeline import create_features, select_feature_columns
from noshow.preprocessing.load_data import (
    load_appointment_csv,
    process_appointments,
    process_postal_codes,
)


def create_prediction(
    model: Any,
    appointments_df: pd.DataFrame,
    all_postal_codes: pd.DataFrame,
    filter_only_booked: bool = False,
) -> pd.DataFrame:
    featuretable = create_features(appointments_df, all_postal_codes)

    if filter_only_booked:
        featuretable = featuretable.loc[featuretable["status"] == "booked"]
    featuretable = select_feature_columns(featuretable)

    prediction_probs: np.ndarray = model.predict_proba(featuretable)
    prediction_df = pd.DataFrame(
        prediction_probs[:, 1], index=featuretable.index, columns=["prediction"]
    )
    return prediction_df


if __name__ == "__main__":
    project_folder = Path(__file__).parents[3]
    data_path = project_folder / "data" / "raw"
    output_path = project_folder / "data" / "processed"
    appointments_df = load_appointment_csv(data_path / "poliafspraken_no_show.csv")
    appointments_df = process_appointments(appointments_df)
    all_postal_codes = process_postal_codes(data_path / "NL.txt")
    with open(
        project_folder / "output" / "models" / "no_show_model_cv.pickle", "rb"
    ) as f:
        model = pickle.load(f)
    predictions = create_prediction(model, appointments_df, all_postal_codes)
    print(predictions)
