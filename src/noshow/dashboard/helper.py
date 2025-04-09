import json
import logging
from datetime import date, datetime
from typing import List

import pandas as pd
import streamlit as st
from sqlalchemy import Date, cast, select
from sqlalchemy.orm import sessionmaker
from streamlit.runtime.context import StreamlitHeaders

from noshow.database.models import (
    ApiCallResponse,
    ApiPatient,
    ApiPrediction,
    ApiSensitiveInfo,
)

logger = logging.getLogger(__name__)


def highlight_row(row: pd.Series) -> List[str]:
    """Highlight a row in a pandas dataframe

    Highlights the row we are additing (from the state session)

    Parameters
    ----------
    row : pd.Series
        A row from a pandas dataframe

    Returns
    -------
    List[str]
        A list of css classes or an empty list
    """
    if row.name == st.session_state["pred_idx"]:
        return ["background-color: gray; color: white"] * len(row)
    else:
        return [""] * len(row)


def previous_preds():
    """Go to previous prediction"""
    if st.session_state["pred_idx"] > 0:
        st.session_state["pred_idx"] -= 1


def start_calling(Session: sessionmaker, call_response: ApiCallResponse):
    """Log the call status as 'Wordt gebeld' and save the results

    Parameters
    ----------
    Session : sessionmaker
        Session used to save the current call response
    call_response : ApiCallResponse
        call response object that needs to be edited

    Returns
    -------
    None
    """
    call_response.call_status = "Wordt gebeld"
    st.session_state["being_called"] = True
    st.session_state["saved"] = False

    with Session() as session:
        session.merge(call_response)
        session.commit()


def next_preds(
    list_len: int,
    Session: sessionmaker,
    call_response: ApiCallResponse,
    current_patient: ApiPatient,
    user_name: str,
) -> None:
    """Go to the next prediction and save results

    Parameters
    ----------
    list_len : int
        Length of the prediction list
    Session : sessionmaker
        Session used to save the current call response
    call_response : ApiCallResponse
        call response object that needs to be edited
    current_patient : ApiPatient
        current patient object
    user_name : str
        The current user e-mail
    """
    if st.session_state.res_input == "Geen":
        call_response.call_status = "Niet gebeld"
    else:
        call_response.call_status = "Gebeld"
    call_response.call_outcome = st.session_state.res_input
    call_response.remarks = st.session_state.opm_input
    call_response.timestamp = datetime.now()
    call_response.user = user_name
    current_patient.call_number = st.session_state.number_input
    current_patient.opt_out = st.session_state.opt_out_checkbox

    with Session() as session:
        session.merge(call_response)
        session.merge(current_patient)
        session.commit()

    if st.session_state["pred_idx"] + 1 < list_len:
        st.session_state["pred_idx"] += 1
    else:
        st.session_state["saved"] = True
        st.session_state["being_called"] = False


def navigate_patients(list_len: int, navigate_forward: bool = True):
    """Navigate through patients

    Navigates through the patients list and resets the prediction index

    Parameters
    ----------
    list_len : int
        Length of patient list
    navigate_forward : bool, optional
        Whether to navigate forward or backward, by default True
    """

    if not st.session_state["saved"] and st.session_state["being_called"]:
        st.error(
            "Klik eerst op 'Opslaan' voordat je verder gaat.",
            icon="🛑",
        )
        return

    if navigate_forward:
        if st.session_state["name_idx"] + 1 < list_len:
            st.session_state["name_idx"] += 1
            st.session_state["pred_idx"] = 0
            st.session_state["being_called"] = False
            st.session_state["saved"] = False
    else:
        if st.session_state["name_idx"] > 0:
            st.session_state["name_idx"] -= 1
            st.session_state["pred_idx"] = 0
            st.session_state["being_called"] = False
            st.session_state["saved"] = False


def navigate_uncalled(Session: sessionmaker, patient_ids: list[str]) -> None:
    """Navigate to the first patient who has not been called today.

    Parameters
    ----------
    Session : sessionmaker
        SQLAlchemy sessionmaker object
    patient_ids : list[str]
        List of patient IDs
    """
    with Session() as session:
        query = (
            select(ApiPrediction.patient_id)
            .outerjoin(ApiPrediction.callresponse_relation)
            .where(
                ApiCallResponse.call_outcome.in_(
                    [
                        "Herinnerd",
                        "Voicemail ingesproken",
                        "Verzet/Geannuleerd",
                        "Onbereikbaar",
                    ]
                )
            )
            .where(cast(ApiCallResponse.timestamp, Date) == cast(date.today(), Date))
            .where(ApiPrediction.active)
            .distinct()
        )
        called_today = session.execute(query).scalars().all()
        uncalled_patient = next(
            (
                patient_id
                for patient_id in patient_ids
                if patient_id not in called_today
            ),
            None,
        )
        if uncalled_patient:
            st.session_state["name_idx"] = patient_ids.index(uncalled_patient)
            st.session_state["pred_idx"] = 0
        else:
            st.info("Alle patiënten zijn vandaag al gebeld.", icon="ℹ️")


def search_number(
    Session: sessionmaker, phone_number: str, patient_ids: list[str]
) -> None:
    """Search for a patient by phone number

    Parameters
    ----------
    Session : sessionmaker
        SQLAlchemy sessionmaker object
    phone_number : str
        Phone number to search for
    patient_ids : list[str]
        List of patient ids
    """
    with Session() as session:
        patient_id = session.execute(
            select(ApiSensitiveInfo.patient_id)
            .where(
                (ApiSensitiveInfo.mobile_phone == phone_number)
                | (ApiSensitiveInfo.home_phone == phone_number)
                | (ApiSensitiveInfo.other_phone == phone_number)
            )
            .distinct()
        ).scalar()

        if patient_id and patient_id in patient_ids:
            st.session_state["name_idx"] = patient_ids.index(patient_id)
            st.session_state["pred_idx"] = 0
        else:
            st.info(
                "Geen patient gevonden met dit telefoonnummer op deze dag", icon="ℹ️"
            )


def get_user(headers: StreamlitHeaders) -> str:
    """Get the user from the streamlit headers

    Parameters
    ----------
    header : StreamlitHeaders
        Streamlit headers object, contains a RStudio-Connect-Credentials header
        when deployed to PositConnect

    Returns
    -------
    str
        The user e-mail in lowercase
    """
    credential_header = headers.get("RStudio-Connect-Credentials")
    if not credential_header:
        logger.warning("Rsconnect credentials not found")
        return "No user"
    credential_header = json.loads(credential_header)
    return credential_header.get("user").lower()
