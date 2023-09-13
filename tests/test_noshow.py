import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


class FakeModel:
    def predict_proba(self, feature_table):
        return np.zeros((len(feature_table), 2))


def fake_postal_codes(_=None) -> pd.DataFrame:
    """Mock function for `process_postal_codes`

    Needs to accept a parameter, but this parameter will be ignored
    """
    return pd.DataFrame(
        {
            "postalcode": [3994, 2034],
            "latitude": [52.0238, 52.3613],
            "longitude": [5.1842, 4.6464],
        }
    ).set_index("postalcode")


def fake_model(_=None):
    """Mock function for returning `load_model`

    Needs to accept a parameter, but this parameter will be ignored
    """
    return FakeModel()


def datetime_to_float(date_str, include_time):
    format = r"%Y-%m-%dT%H:%M:%S" if include_time else r"%Y-%m-%d"
    return datetime.strptime(date_str, format).timestamp() * 1000  # timestamp in ms


def fake_appointments(float_date: bool = False) -> List[Dict]:
    with open(Path(__file__).parent / "data" / "test_appointments.json", "r") as f:
        appointments_json = json.load(f)
    if float_date:
        for idx, row in enumerate(appointments_json):
            appointments_json[idx]["start"] = datetime_to_float(row["start"], True)
            appointments_json[idx]["end"] = datetime_to_float(row["end"], True)
            if appointments_json[idx]["gearriveerd"] is not None:
                appointments_json[idx]["gearriveerd"] = datetime_to_float(
                    row["gearriveerd"], True
                )
            appointments_json[idx]["birthDate"] = datetime_to_float(
                row["birthDate"], False
            )
            appointments_json[idx]["created"] = datetime_to_float(row["created"], True)
    return appointments_json
