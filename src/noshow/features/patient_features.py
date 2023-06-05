import pandas as pd

from noshow.preprocessing.geo import haversine_distance


def add_patient_features(
    appointments_df: pd.DataFrame, all_postalcodes: pd.DataFrame
) -> pd.DataFrame:
    """Add patient age and distance to UMCU

    Parameters
    ----------
    appointments_df : pd.DataFrame
        A dataframe containing info on appointments,
        needs to contain the `address_postalCodeNumbersNL` and `BIRTH_YEAR`
        columns.
    all_postalcodes : pd.DataFrame
        A dataframe containing all postalcodes in the Netherlands with location.
        Needs to have a index on postalcode and columns `longitude` and `latitude`.

    Returns
    -------
    pd.DataFrame
        The appointment_df dataframe with added columns `age` and `dist_umcu`.
    """
    appointments_df = appointments_df.merge(
        all_postalcodes, left_on="address_postalCodeNumbersNL", right_index=True
    )

    appointments_df["dist_umcu"] = appointments_df.apply(
        lambda x: haversine_distance(x["latitude"], x["longitude"]), axis="columns"
    )

    appointments_df["age"] = (
        appointments_df.index.get_level_values("start").year
        - appointments_df["BIRTH_YEAR"]
    )
    appointments_df = appointments_df.drop(columns=["latitude", "longitude"])
    return appointments_df
