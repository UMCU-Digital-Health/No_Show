import pandas as pd
from test_noshow import FakeModel, fake_appointments, fake_postal_codes

from noshow.model.predict import create_prediction
from noshow.preprocessing.load_data import process_appointments


def test_create_prediction():
    appointments_df = pd.DataFrame(fake_appointments())
    appointments_df["created"] = pd.to_datetime(appointments_df["created"])
    appointments_df = process_appointments(appointments_df)

    preds = create_prediction(FakeModel, appointments_df, fake_postal_codes(None))
    assert preds.shape == (3, 1)

    preds_booked = create_prediction(
        FakeModel, appointments_df, fake_postal_codes(None), filter_only_booked=True
    )
    assert preds_booked.shape == (2, 1)
