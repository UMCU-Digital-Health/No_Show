from datetime import date, datetime, timedelta


def add_working_days(start_date: datetime | date, n_days: int) -> datetime | date:
    """Calculate date in `n_days` working days

    Function to calculate the date in n working days, excluding weekends
    Also works for negative n_days

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
    step = 1 if n_days >= 0 else -1
    days_remaining = abs(n_days)
    while days_remaining > 0:
        current_date += timedelta(days=step)
        if current_date.weekday() < 5:
            days_remaining -= 1
    return current_date
