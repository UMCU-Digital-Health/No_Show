from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from sklearn.dummy import DummyClassifier
from test_noshow import FakeModel, fake_appointments, fake_postal_codes

from noshow.features.feature_pipeline import create_features, select_feature_columns
from noshow.model.predict import create_prediction
from noshow.model.train_model import train_cv_model
from noshow.preprocessing.load_data import process_appointments


def test_create_prediction():
    appointments_df = pd.DataFrame(fake_appointments())
    appointments_df["created"] = pd.to_datetime(appointments_df["created"], unit="ms")
    appointments_df["start"] = pd.to_datetime(appointments_df["start"], unit="ms")
    appointments_df = process_appointments(appointments_df)

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
    appointments_df = pd.DataFrame(fake_appointments())
    appointments_df["created"] = pd.to_datetime(appointments_df["created"], unit="ms")
    appointments_df["start"] = pd.to_datetime(appointments_df["start"], unit="ms")
    appointments_df["gearriveerd"] = pd.to_datetime(
        appointments_df["gearriveerd"], unit="ms"
    )
    appointments_df = process_appointments(appointments_df)
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
        (Path(tempdirname) / "models").mkdir()
        train_cv_model(
            feature_table,
            tempdirname,
            DummyClassifier(),
            param_grid={},
            save_dvc_exp=False,
            dvcyaml=None,  # Prevents writing to dvc.yaml
        )
        assert (Path(tempdirname) / "models" / "no_show_model_cv.pickle").is_file()
