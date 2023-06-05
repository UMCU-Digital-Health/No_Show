from pathlib import Path
from typing import Union

import pandas as pd


def process_appointments(appointment_path: Union[str, Path]) -> pd.DataFrame:
    """Process the appointments csv from the Data Platform

    The query used to create this CSV can be found in the data folder

    Parameters
    ----------
    appointment_path : Union[str, Path]
        Path to the CSV containing all appointment info

    Returns
    -------
    pd.DataFrame
        Cleaned appointment DataFrame that can be used for feature building
    """
    appointments_df = pd.read_csv(
        appointment_path,
        parse_dates=["created"],
    )
    appointments_df["start"] = pd.to_datetime(appointments_df["start"], errors="coerce")
    appointments_df["end"] = pd.to_datetime(appointments_df["end"], errors="coerce")
    appointments_df["gearriveerd"] = pd.to_datetime(
        appointments_df["gearriveerd"], errors="coerce"
    )

    appointments_df["no_show"] = appointments_df["cancelationReason_code"].isin(
        ["M", "C2", "C3", "0000000010", "D1", "N", "E1"]
    )
    appointments_df["no_show"] = appointments_df["no_show"].replace(
        {True: "no_show", False: "show"}
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

    return appointments_df


def process_postal_codes(postalcodes_path: Union[str, Path]) -> pd.DataFrame:
    """Load and process all postalcode locations in the Netherlands

    This file can be found at: https://download.geonames.org/export/dump/

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
