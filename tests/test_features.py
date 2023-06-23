import pandas as pd

from noshow.features.appointment_features import add_minutes_early
from noshow.features.cumulative_features import calc_cumulative_features
from noshow.features.no_show_features import prev_no_show_features
from noshow.features.patient_features import add_patient_features


def test_cum_features():
    test_df = pd.DataFrame(
        {
            "pseudo_id": ["1234", "1234", "1234", "5678", "5678", "5678"],
            "val": [1, 1, 0, 0, 1, 1],
            "start": pd.to_datetime(
                [
                    "2022-01-01 00:00:00",
                    "2022-01-02 00:00:00",
                    "2022-01-10 00:00:00",
                    "2022-01-01 00:00:00",
                    "2022-01-04 00:00:00",
                    "2022-01-05 00:00:00",
                ]
            ),
        }
    ).set_index(["pseudo_id", "start"])

    output_df = calc_cumulative_features(
        test_df, "val", "sum_out", exclude_last="3D", cumfunc="sum"
    )
    output_df = calc_cumulative_features(
        output_df, "val", "count_out", exclude_last="3D", cumfunc="count"
    )

    assert output_df.shape == (6, 3)
    assert output_df["sum_out"].to_list() == [0, 0, 0, 0, 0, 2]
    assert output_df["count_out"].to_list() == [0, 0, 0, 1, 1, 2]


def test_patient_features():
    test_df = pd.DataFrame(
        {
            "pseudo_id": ["1234", "5678"],
            "start": pd.to_datetime(["2022-01-01 00:00:00", "2022-01-01 00:00:00"]),
            "BIRTH_YEAR": [1991, 2000],
            "address_postalCodeNumbersNL": [3994, 3584],
        }
    ).set_index(["pseudo_id", "start"])
    postalcodes_df = pd.DataFrame(
        {
            "postal_code": [3994, 3584, 0000],
            "latitude": [52.0238, 52.0846, 0],
            "longitude": [5.1842, 5.1637, 0],
        }
    ).set_index("postal_code")

    output_df = add_patient_features(test_df, postalcodes_df)

    assert output_df.shape == (2, 4)
    # UMC is close to Uithof
    assert output_df.loc[("5678", slice(None)), "dist_umcu"].item() < 2
    # UMC is between 6 and 8 km of Houten
    assert 6 < output_df.loc[("1234", slice(None)), "dist_umcu"].item() < 8
    assert output_df["age"].to_list() == [31, 22]


def test_no_show_features():
    test_df = pd.DataFrame(
        {
            "pseudo_id": ["1234", "1234", "5678", "5678"],
            "no_show": ["no_show", "no_show", "no_show", "show"],
            "start": pd.to_datetime(
                [
                    "2022-01-01 00:00:00",
                    "2022-01-02 00:00:00",
                    "2022-01-01 00:00:00",
                    "2022-01-04 00:00:00",
                ]
            ),
        }
    ).set_index(["pseudo_id", "start"])

    output_df = prev_no_show_features(test_df)

    assert output_df.shape == (4, 4)
    assert output_df["prev_no_show"].to_list() == [0, 0, 0, 1]
    assert output_df["prev_no_show_perc"].to_list() == [0.0, 0.0, 0.0, 1.0]
    assert output_df["earlier_appointments"].to_list() == [0, 0, 0, 1]


def test_minutes_early():
    test_df = pd.DataFrame(
        {
            "pseudo_id": ["1234", "1234", "1234", "5678", "5678", "5678"],
            "earlier_appointments": [0, 0, 2, 0, 1, 1],
            "gearriveerd": pd.to_datetime(
                [
                    "2022-01-01 00:04:00",
                    "2022-01-02 00:02:00",
                    "2022-01-10 00:01:00",
                    "2021-12-31 23:55:00",
                    "2022-01-04 00:01:00",
                    "2022-01-05 00:00:00",
                ]
            ),
            "start": pd.to_datetime(
                [
                    "2022-01-01 00:00:00",
                    "2022-01-02 00:00:00",
                    "2022-01-10 00:00:00",
                    "2022-01-01 00:00:00",
                    "2022-01-04 00:00:00",
                    "2022-01-05 00:00:00",
                ]
            ),
        }
    ).set_index(["pseudo_id", "start"])

    output_df = add_minutes_early(test_df)

    assert output_df.shape == (6, 4)
    assert output_df["prev_minutes_early"].to_list() == [0.0, 0.0, 0.0, 5.0, 5.0, -3.0]
