import numpy as np
import pandas as pd


def add_days_since_created(appointments_df: pd.DataFrame) -> pd.DataFrame:
    """Add the number of days since appointment was created

    Created date is sometimes later than startdate,
    in that case set days since created to 0

    Parameters
    ----------
    appointments_df : pd.DataFrame
        Dataframe containing appointment info.
        Requires a datetime index level called `start` and a column `created`

    Returns
    -------
    pd.DataFrame
        Input Dataframe with extra column `days_since_created`
    """
    appointments_df["days_since_created"] = (
        appointments_df.index.get_level_values("start") - appointments_df["created"]
    )

    appointments_df["days_since_created"] = appointments_df[
        "days_since_created"
    ].dt.days

    # Sometimes the created date is later than the start date
    appointments_df.loc[
        appointments_df["days_since_created"] < 0, "days_since_created"
    ] = 0

    return appointments_df


def add_appointments_same_day(appointments_df: pd.DataFrame) -> pd.DataFrame:
    """Add the number of appointments on the same day

    Parameters
    ----------
    appointments_df : pd.DataFrame
        Dataframe containing appointment info, has to contain a datetime index
        level called `start`, a index level called `pseudo_id` and a column `APP_ID`.

    Returns
    -------
    pd.DataFrame
        The input dataframe with extra column `appointments_same_day`
    """
    appointment_date = appointments_df.index.get_level_values("start").date
    appointment_pseudo_id = appointments_df.index.get_level_values("pseudo_id")
    appointments_df["appointments_same_day"] = appointments_df.groupby(
        [appointment_pseudo_id, appointment_date]
    )["APP_ID"].transform("count")

    return appointments_df


def add_minutes_early(appointments_df: pd.DataFrame, cutoff: int = 60) -> pd.DataFrame:
    """Add the number of minutes a patient was early

    Will add both the number of minutes a patient was early at that appointment, and
    a column with the average minutes early from the previous appointments.

    minutes early will be negative when too late for the appointment.

    Parameters
    ----------
    appointments_df : pd.DataFrame
        A dataframe containing appointment info, needs to contain a datetime index
        level called `start` and a datetime column `gearriveerd`
    cutoff : int, optional
        When values lie outside of this cutoff value, set to zero, by default 60

    Returns
    -------
    pd.DataFrame
        The input dataframe with extra columns `minutes_early` and `prev_minutes_early`.
        Note: Only use `prev_minutes_early` in model,
        since `minutes_early` will leak data!
    """
    appointments_df["minutes_early"] = (
        appointments_df.index.get_level_values(level="start")
        - appointments_df["gearriveerd"]
    ).dt.total_seconds() / 60

    appointments_df.loc[appointments_df["minutes_early"] > cutoff, "minutes_early"] = 0
    appointments_df.loc[appointments_df["minutes_early"] < -cutoff, "minutes_early"] = 0

    appointments_df = appointments_df.sort_index(level="start")
    appointments_df["prev_minutes_early"] = (
        appointments_df.groupby(level="pseudo_id")["minutes_early"]
        .shift(1, fill_value=0)
        .groupby(level="pseudo_id")
        .cumsum()
        / appointments_df["earlier_appointments"]
    )

    appointments_df["prev_minutes_early"] = appointments_df[
        "prev_minutes_early"
    ].replace([np.inf, -np.inf, np.nan], 0)

    return appointments_df


def add_time_features(appointments_df: pd.DataFrame) -> pd.DataFrame:
    """Add time features to dataframe

    Parameters
    ----------
    appointments_df : pd.DataFrame
        The input dataframe, needs a datetime index level called `start`.

    Returns
    -------
    pd.DataFrame
        The input dataframe with extra columns: `weekday` and `hour`.
    """
    appointments_df["weekday"] = appointments_df.index.get_level_values("start").weekday
    appointments_df["hour"] = appointments_df.index.get_level_values("start").hour

    return appointments_df
