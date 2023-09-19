from datetime import datetime

from noshow.preprocessing.utils import add_working_days


def test_add_working_days():
    assert add_working_days(datetime(2023, 9, 11), 3) == datetime(2023, 9, 14)
    assert add_working_days(datetime(2023, 9, 11), 6) == datetime(2023, 9, 19)
    assert add_working_days(datetime(2023, 9, 13), 3) == datetime(2023, 9, 18)
    assert add_working_days(datetime(2023, 9, 15), 3) == datetime(2023, 9, 20)
