import pandas as pd


def calc_cumulative_features(
    df: pd.DataFrame,
    column_name: str,
    feature_name: str,
    exclude_last: str = "3D",
    cumfunc: str = "sum",
) -> pd.DataFrame:
    """Calculate cumulative features

    This function will calculate cumulative sum or count over features,
    but exclude the last `exclude_last` observations. This is useful, since
    some of these observations will not be known at the time of prediction.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe, with an index on `pseudo_id` and `start`.
    column_name : str
        The column name on which to base the feature.
    feature_name : str
        The column name for the newly created feature.
    exclude_last : str, optional
        How many recent observations to exclude from calculation,
        can be anything pandas rolling understands, by default "3D"
    cumfunc : str, optional
        The cumulative function to use, by default "sum"

    Returns
    -------
    pd.DataFrame
        The input dataframe with added column containing the new feature.

    Raises
    ------
    NotImplementedError
        Raises a not implemented error in case the cumfunc parameter is not sum or count
    """
    if cumfunc not in ("sum", "count"):
        raise NotImplementedError()

    df = df.sort_index(level="start")
    grouped_cum_values = df.groupby(level="pseudo_id", sort=False)[column_name]
    if cumfunc == "sum":
        total_cum_values = grouped_cum_values.cumsum()
    else:
        total_cum_values = grouped_cum_values.cumcount() + 1

    # Exclude last n days of data
    exclude_last_rolling = (
        df.reset_index()
        .set_index("start")
        .groupby("pseudo_id", sort=False)[column_name]
        .rolling(exclude_last)
    )
    if cumfunc == "sum":
        exclude_last_values = exclude_last_rolling.sum()
    else:
        exclude_last_values = exclude_last_rolling.count()

    df[feature_name] = total_cum_values - exclude_last_values
    return df
