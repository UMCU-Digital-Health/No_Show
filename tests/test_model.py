from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from sklearn.dummy import DummyClassifier
from test_noshow import (
    FakeModel,
    create_unit_test_clinic_config,
    fake_appointments,
    fake_postal_codes,
)

from noshow.features.feature_pipeline import create_features, select_feature_columns
from noshow.model.predict import create_prediction
from noshow.model.train_model import train_cv_model
from noshow.preprocessing.load_data import (
    load_appointment_pydantic,
    process_appointments,
)


def test_create_prediction():
    appointments_df = load_appointment_pydantic(fake_appointments())
    appointments_df = process_appointments(
        appointments_df, create_unit_test_clinic_config()
    )

    preds = create_prediction(FakeModel(), appointments_df, fake_postal_codes(None))
    assert preds.shape == (12, 1)  # 12 appointments in test data

    preds_booked = create_prediction(
        FakeModel(),
        appointments_df,
        fake_postal_codes(None),
        prediction_start_date="2024-07-16",
    )
    # First patient has 2 appointments on same day
    # second has 1 on the day and one in the future
    assert preds_booked.shape == (5, 1)
    assert all(preds_booked.index.get_level_values("start") >= "2024-07-16")


def test_train_model():
    appointments_df = load_appointment_pydantic(fake_appointments())
    appointments_df = process_appointments(
        appointments_df, create_unit_test_clinic_config()
    )
    feature_table = create_features(appointments_df, fake_postal_codes(None)).pipe(
        select_feature_columns
    )
    # We need more data for training the dummy classifier, so just repeat the data
    feature_table = pd.concat(
        [
            feature_table,
            feature_table,
            feature_table,
            feature_table,
            feature_table,
            feature_table,
            feature_table,
            feature_table,
        ]
    )
    with TemporaryDirectory() as tempdirname:
        train_cv_model(
            feature_table,
            tempdirname,
            DummyClassifier(),
            param_grid={},
            save_exp=False,
        )
        assert (Path(tempdirname) / "no_show_model_cv.pickle").is_file()
