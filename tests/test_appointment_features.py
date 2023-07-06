import pandas as pd

from noshow.features.appointment_features import (
    add_appointments_last_days,
    add_appointments_same_day,
    add_days_since_last_appointment,
)


def test_prev_appointments_features():
    test_df = pd.DataFrame(
        {
            "pseudo_id": ["1234", "1234", "1234", "5678", "5678", "5678"],
            "APP_ID": [1, 2, 3, 4, 5, 6],
            "start": pd.to_datetime(
                [
                    "2022-01-01 09:00:00",
                    "2022-01-02 16:00:00",
                    "2022-01-10 17:00:00",
                    "2022-01-01 10:00:00",
                    "2022-01-04 11:00:00",
                    "2022-01-04 11:30:00",
                ]
            ),
        }
    ).set_index(["pseudo_id", "start"])

    output_df = (
        add_days_since_last_appointment(test_df)
        .pipe(add_appointments_last_days, 5)
        .pipe(add_appointments_same_day)
    )
    assert output_df.shape == (6, 4)
    assert output_df["days_since_last_appointment"].to_list() == [
        0.0,
        0.0,
        1.0,
        3.0,
        0.0,
        8.0,
    ]
    assert output_df["appointments_same_day"].to_list() == [
        1.0,
        1.0,
        1.0,
        2.0,
        2.0,
        1.0,
    ]
    assert output_df["appointments_last_days"].to_list() == [
        1.0,
        1.0,
        2.0,
        2.0,
        3.0,
        1.0,
    ]
