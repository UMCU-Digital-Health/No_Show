from math import atan2, cos, radians, sin, sqrt


def haversine_distance(
    lat1: float,
    lon1: float,
    lat2: float = 52.08593762444437,
    lon2: float = 5.179600848939784,
) -> float:
    """Calculate Haversine distance

    Default second location is the location of the UMCU

    Parameters
    ----------
    lat1 : float
        Latitude of location 1
    lon1 : float
        Longitude of location 1
    lat2 : float, optional
        Latitude of location 2, by default 52.08593762444437
    lon2 : float, optional
        Latitude of location 2, by default 5.179600848939784

    Returns
    -------
    float
        The distance between both points in kilometers
    """
    r = 6373.0  # approximate radius of Earth in km

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = r * c

    return distance
