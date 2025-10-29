from datetime import date, datetime

from noshow.preprocessing.utils import add_working_days


def test_add_working_days():
    assert add_working_days(datetime(2023, 9, 11), 3) == datetime(2023, 9, 14)
    assert add_working_days(datetime(2023, 9, 11), 6) == datetime(2023, 9, 19)
    assert add_working_days(datetime(2023, 9, 13), 3) == datetime(2023, 9, 18)
    assert add_working_days(datetime(2023, 9, 15), 0) == datetime(2023, 9, 15)


def test_subtract_working_days():
    assert add_working_days(datetime(2025, 10, 28), -3) == datetime(2025, 10, 23)
    assert add_working_days(datetime(2025, 10, 28), -6) == datetime(2025, 10, 20)
    assert add_working_days(datetime(2025, 10, 31), -3) == datetime(2025, 10, 28)
    assert add_working_days(datetime(2025, 10, 31), -6) == datetime(2025, 10, 23)


def test_working_days_date():
    assert add_working_days(date(2023, 9, 11), 3) == date(2023, 9, 14)
    assert add_working_days(datetime(2023, 9, 11), 3) == datetime(2023, 9, 14)
