import pandas as pd
import pytest
from test_noshow import fake_appointments, fake_model, fake_postal_codes

import noshow.api.app as app
from noshow.api.app import predict


@pytest.mark.asyncio
async def test_predict_endpoint(monkeypatch):
    appointments_json = fake_appointments()
    monkeypatch.setattr(app, "process_postal_codes", fake_postal_codes)
    monkeypatch.setattr(app, "load_model", fake_model)
    output = await predict(appointments_json)
    output_df = pd.DataFrame(output)
    assert output_df.shape == (2, 3)
