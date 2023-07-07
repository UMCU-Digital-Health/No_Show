import json
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


class FakeModel:
    def predict_proba(feature_table):
        return np.zeros((len(feature_table), 2))


def fake_postal_codes(_) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "postalcode": [3994, 2034],
            "latitude": [52.0238, 52.3613],
            "longitude": [5.1842, 4.6464],
        }
    ).set_index("postalcode")


def fake_model(_=None):
    return FakeModel


def fake_appointments() -> List[Dict]:
    with open(Path(__file__).parent / "data" / "test_appointments.json", "r") as f:
        appointments_json = json.load(f)
    return appointments_json
