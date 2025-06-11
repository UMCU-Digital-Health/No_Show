from datetime import date
from pathlib import Path
from typing import Dict, List, Union

import pandas as pd

from noshow.api.pydantic_models import Appointment
from noshow.config import NO_SHOW_CODES, ClinicConfig


def load_appointment_pydantic(input: List[Appointment]) -> pd.DataFrame:
    """Load prediction data from a list of Appointments

    Parameters
    ----------
    input : List[Appointment]
        The input data as a list of Appointments

    Returns
    -------
    pd.DataFrame
        The loaded data as pandas dataframe
    """
    appointments_df = pd.DataFrame([a.model_dump() for a in input])
    appointments_df = appointments_df.replace("", None)

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
        date_format="ISO8601",
        dtype={"specialty_code": "object"},  # Avoids Dtype Mixed warning
    )

    appointments_df["start"] = pd.to_datetime(
        appointments_df["start"], errors="coerce", format="ISO8601"
    )
    appointments_df["end"] = pd.to_datetime(
        appointments_df["end"], errors="coerce", format="ISO8601"
    )
    appointments_df["gearriveerd"] = pd.to_datetime(
        appointments_df["gearriveerd"], errors="coerce", format="ISO8601"
    )

    return appointments_df


def process_appointments(
    appointments_df: pd.DataFrame,
    clinic_config: Dict[str, ClinicConfig],
    start_date: str | None = None,
) -> pd.DataFrame:
    """Process the appointments data

    Parameters
    ----------
    appointments_df : Union[str, Path]
        The pandas dataframe with appointments data from either csv or json
    clinic_config : Dict[str, ClinicConfig]
        The clinic configuration, containing filters and clinic info
    start_date : str, optional
        The start date for the predictions, if given will filter out appointments of
        patients that do not have an appointment on this date, by default None

    Returns
    -------
    pd.DataFrame
        Cleaned appointment DataFrame that can be used for feature building
    """
    appointments_df = apply_config_filters(appointments_df, clinic_config, start_date)

    appointments_df["no_show"] = "show"
    appointments_df.loc[
        appointments_df["mutationReason_code"].isin(NO_SHOW_CODES), "no_show"
    ] = "no_show"

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


def apply_config_filters(
    appointments_df: pd.DataFrame,
    clinic_config: Dict[str, ClinicConfig],
    start_date: str | None = None,
) -> pd.DataFrame:
    """Apply the clinic config filters to the appointments data

    Parameters
    ----------
    appointments_df : pd.DataFrame
        The appointments data
    clinic_config : Dict[str, ClinicConfig]
        The clinic configuration, containing filters and clinic info
    start_date : str, optional
        The start date for the predictions, if given will filter out appointments of
        patients that do not have an appointment on this date, by default None

    Returns
    -------
    pd.DataFrame
        The appointments data with the clinic config filters applied
    """
    clinic_df_list = []
    for name, config in clinic_config.items():
        clinic_df = appointments_df.loc[
            appointments_df["hoofdagenda_id"].isin(config.main_agenda_codes)
        ].copy()
        clinic_df["clinic"] = name

        if config.subagenda_exclude and config.subagendas:
            clinic_df = clinic_df.loc[
                ~clinic_df["subagenda_id"].isin(config.subagendas)
            ]
        elif config.subagendas:
            clinic_df = clinic_df.loc[clinic_df["subagenda_id"].isin(config.subagendas)]

        if config.appcode_exclude and config.appcodes:
            clinic_df = clinic_df.loc[~clinic_df["afspraak_code"].isin(config.appcodes)]
        elif config.appcodes:
            clinic_df = clinic_df.loc[clinic_df["afspraak_code"].isin(config.appcodes)]

        clinic_df_list.append(clinic_df)

    total_df = pd.concat(clinic_df_list)

    # After filtering there could still be appointments of patients that no longer have
    # an appointment on the start date.
    if start_date:
        patient_list = total_df.loc[
            total_df["start"].dt.date == date.fromisoformat(start_date), "pseudo_id"
        ].unique()
        total_df = total_df.loc[total_df["pseudo_id"].isin(patient_list)]

    return total_df
