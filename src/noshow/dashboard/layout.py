"""This module contains the layout functions for the calling dashboard."""

from typing import List

import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker

from noshow.dashboard.helper import (
    highlight_row,
    navigate_patients,
    next_preds,
    previous_preds,
    search_number,
    start_calling,
)
from noshow.database.models import ApiCallResponse, ApiPatient, ApiSensitiveInfo

STATUS_LIST = [
    "Niet gebeld",
    "Wordt gebeld",
    "Gebeld",
    "Onbereikbaar",
]
RES_LIST = [
    "Herinnerd",
    "Verzet/Geannuleerd",
    "Geen",
    "Voicemail ingesproken",
]
CALL_NUMBER_LIST = [
    "Niet van toepassing",
    "Mobielnummer",
    "Thuis telefoonnummer",
    "Overig telefoonnummer",
]


def render_patient_selection(
    patient_ids: List[str],
    Session: sessionmaker,
    enable_dev_mode: bool = False,
) -> None:
    """Render the patient selection buttons

    Parameters
    ----------
    patient_ids : List[str]
        List of patient ids
    Session : sessionmaker
        SQLAlchemy sessionmaker object
    enable_dev_mode : bool, optional
        If extra dev info should be displayed, by default False
    """
    st.write(f"## Patient {st.session_state['name_idx'] + 1}/{len(patient_ids)}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "Vorige patient",
            on_click=navigate_patients,
            args=(len(patient_ids), False),
        )
    with col2:
        with st.popover(
            "🔍 Zoeken", help="Zoek op telefoonnummer om een patient te vinden."
        ):
            phone_number = st.text_input("Zoek op telefoonnummer...")
            st.button(
                "Zoek",
                on_click=search_number,
                args=(Session, phone_number, patient_ids),
            )
    with col3:
        st.button(
            "Volgende patient",
            on_click=navigate_patients,
            args=(len(patient_ids), True),
        )
    st.header("Patient-gegevens")
    if enable_dev_mode:
        st.write(f"- ID: {patient_ids[st.session_state['name_idx']]}")


def render_patient_info(
    Session: sessionmaker,
    current_response: ApiCallResponse,
    current_patient: ApiSensitiveInfo,
    current_patient_nmbr: ApiPatient,
) -> None:
    """Render patient information

    This function is responsible for rendering the patient information on the dashboard.

    Parameters
    ----------
    Session : sessionmaker
        The SQLAlchemy sessionmaker object used for database operations.
    current_response : ApiCallResponse
        The current call response object.
    current_patient : ApiSensitiveInfo
        The current patient object containing sensitive information.
    current_patient_nmbr : ApiPatient
        The current patient object containing the call number.
    """
    if current_response.call_status == "Niet gebeld":
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
            if current_response.call_status == "Wordt gebeld":
                st.warning("Deze patient wordt momenteel gebeld!", icon="📞")
            else:
                st.warning("Deze patient is al gebeld!", icon="⚠️")
            st.write(f"- Naam: {current_patient.full_name or 'Onbekend'}")
            st.write(f"- Voornaam: {current_patient.first_name or 'Onbekend'}")
            st.write(f"- Patientnummer: {current_patient.hix_number or 'Onbekend'}")
            st.write(f"- Geboortedatum: {current_patient.birth_date or 'Onbekend'}")
            st.write(f"- Mobiel: {current_patient.mobile_phone or 'Onbekend'}")
            st.write(f"- Thuis: {current_patient.home_phone or 'Onbekend'}")
            st.write(f"- Overig nummer: {current_patient.other_phone or 'Onbekend'}")
            st.write("")
            if not current_patient_nmbr.call_number:
                current_patient_nmbr.call_number = 0
            call_number_type = CALL_NUMBER_LIST[current_patient_nmbr.call_number]
            st.write(f"- Eerder contact ging via: {call_number_type or 'Onbekend'}")
        else:
            st.write("Patientgegevens zijn verwijderd.")


def render_appointment_overview(
    all_predictions_df: pd.DataFrame,
    Session: sessionmaker,
    user_name: str,
    current_response: ApiCallResponse,
    current_patient_nmbr: ApiPatient,
    last_updated: pd.Timestamp,
    enable_dev_mode: bool = False,
) -> None:
    """Render the appointment overview

    Parameters
    ----------
    all_predictions_df : pd.DataFrame
        The DataFrame containing all the predictions.
    Session : sessionmaker
        The SQLAlchemy sessionmaker object used for database operations.
    user_name : str
        The current user e-mail.
    current_response : ApiCallResponse
        The current call response object.
    current_patient_nmbr : ApiPatient
        The current patient object containing the call number.
    last_updated : pd.Timestamp
        The timestamp when the last predictions were generated.
    enable_dev_mode : bool, optional
        If extra dev info should be displayed, by default False
    """
    st.header("Afspraakoverzicht")
    if not enable_dev_mode:
        all_predictions_df = all_predictions_df.drop(columns="id")
    st.dataframe(
        all_predictions_df.style.apply(highlight_row, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    with st.form("patient_form", clear_on_submit=True):
        st.selectbox(
            "Status gesprek:",
            options=STATUS_LIST,
            index=STATUS_LIST.index(current_response.call_status),
            key="status_input",
        )
        st.selectbox(
            "Resultaat gesprek: ",
            options=RES_LIST,
            index=RES_LIST.index(current_response.call_outcome),
            key="res_input",
        )
        options_idx = [0, 1, 2, 3]
        st.selectbox(
            "Contact gemaakt via: ",
            options=options_idx,
            format_func=lambda x: CALL_NUMBER_LIST[x],
            index=options_idx.index(current_patient_nmbr.call_number),
            key="number_input",
        )
        st.text_input("Opmerkingen: ", value=current_response.remarks, key="opm_input")

        st.checkbox(
            "De patiënt heeft aangegeven niet meer telefonisch benaderd te willen worden.",
            value=(current_patient_nmbr.opt_out == 1),
            key="opt_out_checkbox",
        )

        st.form_submit_button(
            "Opslaan",
            on_click=next_preds,
            args=(
                len(all_predictions_df),
                Session,
                current_response,
                current_patient_nmbr,
                user_name,
            ),
            type="primary",
        )
        if current_response.timestamp is not None:
            st.caption(
                f"Laatst opgeslagen om: {current_response.timestamp:%Y-%m-%d %H:%M:%S},"
                f" door: {current_response.user}"
            )
    st.button(
        "Vorige",
        on_click=previous_preds,
    )
    st.divider()
    st.caption(
        f"Laatste voorspellingen gegenereerd om: {last_updated:%Y-%m-%d %H:%M:%S}"
    )
