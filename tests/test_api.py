import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

import noshow.api.app as app
from noshow.api.app import predict


class FakeModel:
    def predict_proba(feature_table):
        return np.zeros((2, len(feature_table)))


@pytest.mark.asyncio
async def test_predict_endpoint(monkeypatch):
    def fake_postal_codes(_):
        return pd.DataFrame(
            {
                "postalcode": [3994, 2034],
                "latitude": [52.0238, 52.3613],
                "longitude": [5.1842, 4.6464],
            }
        ).set_index("postalcode")

    def fake_model(_=None):
        return FakeModel

    with open(Path(__file__).parent / "data" / "test_appointments.json", "r") as f:
        appointments_json = json.load(f)

    monkeypatch.setattr(app, "process_postal_codes", fake_postal_codes)
    monkeypatch.setattr(app, "load_model", fake_model)
    output = await predict(appointments_json)
    output_df = pd.DataFrame(output)
    assert output_df.shape == (2, 3)
