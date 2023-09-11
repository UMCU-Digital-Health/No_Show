import pickle
from pathlib import Path
from typing import Any, Optional

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
    prediction_start_date: Optional[str] = None,
    add_sensitive_info: bool = False,
) -> pd.DataFrame:
    featuretable = create_features(appointments_df, all_postal_codes)

    if prediction_start_date:
        featuretable = featuretable.sort_index().loc[
            (slice(None), slice(prediction_start_date, None)), :
        ]
    featuretable = select_feature_columns(featuretable)
    featuretable = featuretable.drop(columns="no_show")

    prediction_probs: np.ndarray = model.predict_proba(featuretable)
    prediction_df = pd.DataFrame(
        prediction_probs[:, 1], index=featuretable.index, columns=["prediction"]
    )
    if add_sensitive_info:
        sensitive_info = appointments_df[
            [
                "APP_ID",
                "name_text",
                "name_given1_callMe",
                "telecom1_value",
                "telecom2_value",
                "telecom3_value",
                "name",
                "description",
                "birthDate",
            ]
        ]
        prediction_df = prediction_df.join(sensitive_info)
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
