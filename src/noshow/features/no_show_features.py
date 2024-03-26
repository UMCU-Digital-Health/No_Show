import pandas as pd

from noshow.features.cumulative_features import calc_cumulative_features


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
    appointments_df.loc[:, "prev_no_show"] = (
        appointments_df["no_show"].replace({"no_show": "1", "show": "0"}).astype(int)
    )

    appointments_df = calc_cumulative_features(
        appointments_df, "prev_no_show", "prev_no_show"
    )

    appointments_df = calc_cumulative_features(
        appointments_df, "no_show", "earlier_appointments", cumfunc="count"
    )

    appointments_df["prev_no_show_perc"] = (
        appointments_df["prev_no_show"] / appointments_df["earlier_appointments"]
    )
    appointments_df.loc[
        appointments_df["prev_no_show_perc"].isna(), "prev_no_show_perc"
    ] = 0

    return appointments_df
