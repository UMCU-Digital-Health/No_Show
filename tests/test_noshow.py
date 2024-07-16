import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


class FakeModel:
    def predict_proba(self, feature_table):
        return np.random.rand(len(feature_table), 2)


def fake_postal_codes(_=None) -> pd.DataFrame:
    """Mock function for `process_postal_codes`

    Needs to accept a parameter, but this parameter will be ignored
    """
    return pd.DataFrame(
        {
            "postalcode": [3994, 2034, 3738, 8225, 3072, 9724],
            "latitude": [52.0238, 52.3613, 52.155789, 52.502652, 51.901032, 53.211872],
            "longitude": [5.1842, 4.6464, 5.177230, 5.490525, 4.486715, 6.576597],
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


def fake_bins():
    return {}


def fake_appointments() -> List[Dict]:
    with open(Path(__file__).parent / "data" / "test_appointments.json", "r") as f:
        appointments_json = json.load(f)
    return appointments_json
