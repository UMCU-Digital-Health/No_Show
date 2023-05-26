import pandas as pd


def prev_no_show_features(appointments_df: pd.DataFrame) -> pd.DataFrame:
    """Add previous no-show features to the dataframe

    Adds the following features:
    - prev_no_show: previous no-shows of this patient
    - earlier_appointments: How many earlier appointments did the patient have (total)
    - prev_no_show_perc: The percentage of earlier appointments that was a no-show

    Parameters
    ----------
    appointments_df : pd.DataFrame
        Dataframe with multiindex on pseudo-id and start,
        contains information on appointments

    Returns
    -------
    pd.DataFrame
        The input dataframe with added feature columns
    """
    appointments_df["prev_no_show"] = appointments_df["no_show"].replace(
        {"no_show": 1, "show": 0}
    )
    appointments_df = appointments_df.sort_index(level="start")
    appointments_df["prev_no_show"] = (
        appointments_df.groupby("pseudo_id", sort=False)["prev_no_show"]
        .shift(1, fill_value=0)
        .groupby("pseudo_id", sort=False)
        .cumsum()
    )

    appointments_df["earlier_appointments"] = appointments_df.groupby(
        "pseudo_id", sort=False
    )["no_show"].cumcount()

    appointments_df["prev_no_show_perc"] = (
        appointments_df["prev_no_show"] / appointments_df["earlier_appointments"]
    )
    appointments_df.loc[
        appointments_df["prev_no_show_perc"].isna(), "prev_no_show_perc"
    ] = 0

    return appointments_df
