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
from noshow.preprocessing.load_data import process_appointments, process_postal_codes


def create_features(
    appointments_df: pd.DataFrame,
    all_postal_codes: pd.DataFrame,
    minutes_early_cutoff: int = 60,
) -> pd.DataFrame:
    appointments_features = (
        appointments_df.pipe(prev_no_show_features)
        .pipe(add_appointments_same_day)
        .pipe(add_days_since_created)
        .pipe(add_minutes_early, minutes_early_cutoff)
        .pipe(add_time_features)
        .pipe(add_patient_features, all_postal_codes)
    )

    return appointments_features


if __name__ == "__main__":
    datamanager_path = Path("/mapr") / "no_show" / "no_show_datamanager"
    output_path = Path(__file__).parents[3] / "data" / "processed"

    appointments_df = process_appointments(
        datamanager_path / "poliafspraken_no_show.csv"
    )
    all_postalcodes = process_postal_codes(datamanager_path / "NL.txt")
    appointments_features = create_features(appointments_df, all_postalcodes)

    appointments_features[
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
    ].to_parquet(output_path / "featuretable.parquet")
