from datetime import date
from typing import List

import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker

from noshow.database.models import ApiCallResponse, ApiPatient


def render_patient_info(
    Session: sessionmaker,
    current_response: ApiCallResponse,
    current_patient: ApiPatient,
    current_patient_nmbr: int,
    call_number_list: List[str],
) -> None:
    """Render patient information

    Parameters
    ----------
    Session : sessionmaker
        SQLAlchemy sessionmaker object
    current_response : ApiCallResponse
        Current call response object
    current_patient : ApiPatient
        Current patient object
    current_patient_nmbr : int
        Current patient number
    call_number_list : List[str]
        List of call number types
    """
    if current_response.call_status != "Wordt gebeld":
        st.button(
            "Start met bellen patient",
            on_click=start_calling,
            args=(
                Session,
                current_response,
            ),
            type="primary",
        )
    else:
        if current_patient:
            st.write(f"- Naam: {current_patient.full_name or 'Onbekend'}")
            st.write(f"- Voornaam: {current_patient.first_name or 'Onbekend'}")
            st.write(f"- Geboortedatum: {current_patient.birth_date or 'Onbekend'}")
            st.write(f"- Mobiel: {current_patient.mobile_phone or 'Onbekend'}")
            st.write(f"- Thuis: {current_patient.home_phone or 'Onbekend'}")
            st.write(f"- Overig nummer: {current_patient.other_phone or 'Onbekend'}")
            st.write("")
            if not current_patient_nmbr.call_number:
                current_patient_nmbr.call_number = 0
            call_number_type = call_number_list[current_patient_nmbr.call_number]
            st.write(f"- Eerder contact ging via: {call_number_type or 'Onbekend'}")
        else:
            st.write("Patientgegevens zijn verwijderd.")


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


def previous_preds(call_status: str = "Niet gebeld"):
    """Go to previous prediction"""
    if call_status == "Wordt gebeld":
        st.error("Status is 'Wordt gebeld', verander de status voordat je verder gaat.")
        return

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

    with Session() as session:
        session.merge(call_response)
        session.commit()


def next_preds(
    list_len: int,
    Session: sessionmaker,
    call_response: ApiCallResponse,
    current_patient: ApiPatient,
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
    """
    call_response.call_status = st.session_state.status_input
    call_response.call_outcome = st.session_state.res_input
    call_response.remarks = st.session_state.opm_input
    current_patient.call_number = st.session_state.number_input

    if call_response.call_status == "Wordt gebeld":
        st.error("Status is 'Word Gebeld', verander de status voordat je verder gaat.")
        return
    if call_response.call_status == "Gebeld":
        current_patient.last_call_date = date.today()
    if call_response.call_outcome == "Bel me niet":
        current_patient.opt_out = 1
        call_response.call_status = "Gebeld"

    with Session() as session:
        session.merge(call_response)
        session.merge(current_patient)
        session.commit()
    if st.session_state["pred_idx"] + 1 < list_len:
        st.session_state["pred_idx"] += 1


def navigate_patients(
    list_len: int, navigate_forward: bool = True, call_status: str = "Niet gebeld"
):
    """Navigate through patients

    Navigates through the patients list and reset the prediction index

    Parameters
    ----------
    list_len : int
        Length of patient list
    navigate_forward : bool, optional
        Whether to navigate forward or backword, by default True
    """
    if call_status == "Wordt gebeld":
        st.error("Status is 'Wordt gebeld', verander de status voordat je verder gaat.")
        return
    elif navigate_forward:
        if st.session_state["name_idx"] + 1 < list_len:
            st.session_state["name_idx"] += 1
            st.session_state["pred_idx"] = 0
    else:
        if st.session_state["name_idx"] > 0:
            st.session_state["name_idx"] -= 1
            st.session_state["pred_idx"] = 0
