from pathlib import Path

import pandas as pd

from noshow.features.appointment_features import (
    add_appointments_same_day,
    add_days_since_created,
    add_minutes_early,
    add_time_features,
)
from noshow.features.no_show_features import prev_no_show_features
from noshow.features.patient_features import add_patient_features
from noshow.preprocessing.load_data import (
    load_appointment_csv,
    process_appointments,
    process_postal_codes,
)


def create_features(
    appointments_df: pd.DataFrame,
    all_postal_codes: pd.DataFrame,
    minutes_early_cutoff: int = 60,
) -> pd.DataFrame:
    """Create all the feature for the no-show model

    This function is a pipeline that applies all the feature
    creation code to generate a feature table.

    Parameters
    ----------
    appointments_df : pd.DataFrame
        The dataframe containing all the appointment data, see the
        process_appointments function on how to read this data.
    all_postal_codes : pd.DataFrame
        The dataframe containing all the postalcodes in the
        Netherlands
    minutes_early_cutoff : int, optional
        Cutoff value for the minutes early feature, by default 60

    Returns
    -------
    pd.DataFrame
        The featuretable
    """
    appointments_features = (
        appointments_df.pipe(prev_no_show_features)
        .pipe(add_appointments_same_day)
        .pipe(add_days_since_created)
        .pipe(add_minutes_early, minutes_early_cutoff)
        .pipe(add_time_features)
        .pipe(add_patient_features, all_postal_codes)
        .sort_index(level="start")
    )

    return appointments_features


def select_feature_columns(featuretable: pd.DataFrame) -> pd.DataFrame:
    return featuretable[
        [
            "hour",
            "weekday",
            "specialty_code",
            "minutesDuration",
            "no_show",
            "prev_no_show",
            "prev_no_show_perc",
            "age",
            "dist_umcu",
            "prev_minutes_early",
            "earlier_appointments",
            "appointments_same_day",
            "days_since_created",
        ]
    ]


if __name__ == "__main__":
    data_path = Path(__file__).parents[3] / "data" / "raw"
    output_path = Path(__file__).parents[3] / "data" / "processed"
    appointments_df = load_appointment_csv(data_path / "poliafspraken_no_show.csv")
    appointments_df = process_appointments(appointments_df)
    all_postalcodes = process_postal_codes(data_path / "NL.txt")
    appointments_features = (
        create_features(appointments_df, all_postalcodes)
        .pipe(select_feature_columns)
        .to_parquet(output_path / "featuretable.parquet")
    )
