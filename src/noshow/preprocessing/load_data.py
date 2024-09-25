from pathlib import Path
from typing import Dict, List, Union

import pandas as pd


def load_appointment_json(input: List[Dict]) -> pd.DataFrame:
    """Load prediction data from a JSON dictionary

    Parameters
    ----------
    input : List[Dict]
        The input data as a dictionary in the records orientation
        (every dictionary corresponds to a row)

    Returns
    -------
    pd.DataFrame
        The loaded JSON data as pandas dataframe
    """
    appointments_df = pd.DataFrame.from_records(input, coerce_float=True)

    appointments_df = appointments_df.replace("", None)
    appointments_df["created"] = pd.to_datetime(
        appointments_df["created"].astype(float), unit="ms"
    )
    appointments_df["start"] = pd.to_datetime(
        appointments_df["start"].astype(float), unit="ms"
    )
    appointments_df["end"] = pd.to_datetime(
        appointments_df["end"].astype(float), unit="ms"
    )
    appointments_df["gearriveerd"] = pd.to_datetime(
        appointments_df["gearriveerd"].astype(float), unit="ms"
    )
    appointments_df["birthDate"] = pd.to_datetime(
        appointments_df["birthDate"].astype(float), unit="ms"
    )

    appointments_df["address_postalCodeNumbersNL"] = appointments_df[
        "address_postalCodeNumbersNL"
    ].astype(float)

    # Clinic name and description are sometimes unknown since HiX6.3
    appointments_df.loc[appointments_df["name"].isnull(), "name"] = "Onbekend"
    appointments_df.loc[appointments_df["description"].isnull(), "description"] = (
        "Onbekend"
    )
    return appointments_df


def load_appointment_csv(csv_path: Union[str, Path]) -> pd.DataFrame:
    """Load data from a csv file

    The query used to create this CSV can be found in the data folder

    Parameters
    ----------
    csv_path : Union[str, Path]
        The path to the csv file

    Returns
    -------
    pd.DataFrame
        The pandas dataframe from the csv file
    """
    appointments_df = pd.read_csv(
        csv_path,
        parse_dates=["created"],
    )
    return appointments_df


def process_appointments(appointments_df: pd.DataFrame) -> pd.DataFrame:
    """Process the appointments data

    Parameters
    ----------
    appointments_df : Union[str, Path]
        The pandas dataframe with appointments data from either csv or json

    Returns
    -------
    pd.DataFrame
        Cleaned appointment DataFrame that can be used for feature building
    """
    appointments_df["start"] = pd.to_datetime(
        appointments_df["start"], errors="coerce", format="ISO8601"
    )
    appointments_df["end"] = pd.to_datetime(
        appointments_df["end"], errors="coerce", format="ISO8601"
    )
    appointments_df["gearriveerd"] = pd.to_datetime(
        appointments_df["gearriveerd"], errors="coerce", format="ISO8601"
    )

    appointments_df["no_show"] = "show"
    appointments_df.loc[appointments_df["cancelationReason_code"] == "N", "no_show"] = (
        "no_show"
    )

    # Some patients have multiple postal codes
    appointments_df = appointments_df.drop_duplicates(
        subset=appointments_df.columns.difference(["address_postalCodeNumbersNL"])
    )

    # Some start dates are NaT
    appointments_df = appointments_df.loc[~appointments_df["start"].isna()]

    # No phone consults
    appointments_df = appointments_df.loc[
        appointments_df["soort_consult"] != "Telefonisch"
    ]

    appointments_df = appointments_df.set_index(["pseudo_id", "start"])

    # Rolling features can't be calculated on non-unique index
    appointments_df = appointments_df[~appointments_df.index.duplicated(keep="last")]

    return appointments_df


def process_postal_codes(postalcodes_path: Union[str, Path]) -> pd.DataFrame:
    """Load and process all postalcode locations in the Netherlands

    This file can be found at: https://download.geonames.org/export/zip/NL.zip

    Parameters
    ----------
    postalcodes_path : Union[str, Path]
        Path to the tsv-file that contains postalcode information

    Returns
    -------
    pd.DataFrame
        A dataframe containing all postalcodes and longlat positions
        in the Netherlands
    """
    all_postalcodes = pd.read_table(
        postalcodes_path,
        sep="\t",
        header=None,
        names=[
            "country",
            "postalcode",
            "city",
            "admin_name1",
            "admin_code1",
            "admin_name2",
            "admin_code2",
            "admin_name3",
            "admin_code3",
            "latitude",
            "longitude",
            "accuracy",
        ],
    )
    all_postalcodes = all_postalcodes.set_index("postalcode")[["latitude", "longitude"]]
    all_postalcodes = all_postalcodes.loc[~all_postalcodes.index.duplicated()]
    return all_postalcodes
