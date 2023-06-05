import pandas as pd

from noshow.features.patient_features import add_patient_features


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
