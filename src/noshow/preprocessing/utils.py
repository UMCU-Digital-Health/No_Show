from datetime import datetime, timedelta


def add_working_days(start_date: datetime, n_days: int) -> datetime:
    """Calculate date in `n_days` working days

    Function to calculate the date in n working days, excluding weekends

    Parameters
    ----------
    start_date : datetime
        date to add days to
    n_days : int
        number of working days to add

    Returns
    -------
    datetime
        date in `n_days` working days
    """
    current_date = start_date
    while n_days > 0:
        current_date += timedelta(days=1)
        if current_date.weekday() < 5:
            n_days -= 1
    return current_date
