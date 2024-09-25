import os
from datetime import date, datetime
from pathlib import Path
from typing import cast

import pandas as pd
import streamlit as st
import tomli
from dotenv import load_dotenv
from sqlalchemy import select

from noshow.dashboard.connection import get_patient_list, init_session
from noshow.dashboard.helper import (
    highlight_row,
    navigate_patients,
    next_preds,
    previous_preds,
    render_patient_info,
    search_number,
)
from noshow.database.models import (
    ApiCallResponse,
    ApiPatient,
    ApiPrediction,
    ApiRequest,
    ApiSensitiveInfo,
)
from noshow.preprocessing.utils import add_working_days

load_dotenv()

with open(Path(__file__).parents[1] / "pyproject.toml", "rb") as f:
    config = tomli.load(f)

VERSION = config["project"]["version"]

# Global and env variables
db_user = os.environ["DB_USER"]
db_passwd = os.environ["DB_PASSWD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_DATABASE"]

if "name_idx" not in st.session_state:
    st.session_state["name_idx"] = 0
if "pred_idx" not in st.session_state:
    st.session_state["pred_idx"] = 0

date_3_days = add_working_days(datetime.today(), 3)


def reset_name_index() -> None:
    """Reset the name index when changing the date"""
    st.session_state["name_idx"] = 0
    st.session_state["pred_idx"] = 0


def main():
    """Main function of the streamlit dashboard"""

    # Page config and sidebar
    support_message = os.getenv("SUPPORT", None)
    st.set_page_config(
        page_title="No Show bel-dashboard",
        page_icon=":chair:",
        menu_items={
            "Get help": f"{support_message}",
            "About": (
                f"No Show v{VERSION}\n\n AI for Health, https://www.umcutrecht.nl/nl"
            ),
        },
    )

    with st.sidebar:
        date_input = st.date_input(
            "Voor welke dag wil je bellen (standaard over 3 werkdagen)",
            date_3_days,
            on_change=reset_name_index,
        )
        enable_dev_mode = st.toggle("Toon ID's")

    if not date_input:
        return None
    date_input = cast(date, date_input)

    # Retrieve data from application database
    Session = init_session(db_user, db_passwd, db_host, db_port, db_database)
    with Session() as session:
        patient_ids = get_patient_list(session, date_input)
        if not patient_ids:
            st.header(f"Geen afspraken op {date_input}")
            return None

        current_patient = session.get(
            ApiSensitiveInfo, patient_ids[st.session_state["name_idx"]]
        )
        patient_predictions = session.execute(
            select(
                ApiPrediction.id,
                ApiPrediction.start_time,
                ApiPrediction.clinic_name,
                ApiPrediction.clinic_reception,
                ApiPrediction.clinic_phone_number,
                ApiCallResponse.call_status,
                ApiRequest.timestamp,
            )
            .outerjoin(ApiPrediction.callresponse_relation)
            .outerjoin(ApiPrediction.request_relation)
            .where(ApiPrediction.start_time >= date_input)
            .where(
                ApiPrediction.patient_id == patient_ids[st.session_state["name_idx"]]
            )
            .where(ApiPrediction.active)
            .order_by(ApiPrediction.start_time)
        ).all()
    all_predictions_df = pd.DataFrame(patient_predictions)
    last_updated = max(all_predictions_df["timestamp"])
    all_predictions_df = all_predictions_df.drop(columns="timestamp")
    all_predictions_df.loc[
        all_predictions_df["call_status"] == "Gebeld", "call_status"
    ] = "🟢"
    if "Wordt gebeld" in all_predictions_df["call_status"].values:
        all_predictions_df.loc[
            ~(all_predictions_df["call_status"] == "🟢"), "call_status"
        ] = "📞"
    all_predictions_df.loc[
        ~all_predictions_df["call_status"].isin(["🟢", "📞"]),
        "call_status",
    ] = "🔴"
    pred_id = all_predictions_df.iat[st.session_state["pred_idx"], 0]

    # load information related to call history
    with Session() as session:
        current_response = session.get(ApiPrediction, pred_id).callresponse_relation
        current_patient_nmbr = session.get(
            ApiPatient, patient_ids[st.session_state["name_idx"]]
        )
    if not current_response:
        current_response = ApiCallResponse(
            call_status="Niet gebeld",
            call_outcome="Geen",
            remarks="",
            prediction_id=pred_id,
        )
    # convert rows that are initiallised as None to 0
    if current_patient_nmbr.call_number is None:
        current_patient_nmbr.call_number = 0

    status_list = [
        "Niet gebeld",
        "Wordt gebeld",
        "Gebeld",
        "Onbereikbaar",
    ]
    res_list = [
        "Herinnerd",
        "Verzet/Geannuleerd",
        "Geen",
        "Bel me niet",
        "Voicemail ingesproken",
    ]
    call_number_list = [
        "Niet van toepassing",
        "Mobielnummer",
        "Thuis telefoonnummer",
        "Overig telefoonnummer",
    ]

    # Main content of streamlit app
    st.write(f"## Patient {st.session_state['name_idx'] + 1}/{len(patient_ids)}")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            "Vorige patient",
            on_click=navigate_patients,
            args=(len(patient_ids), False, current_response.call_status),
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
            args=(len(patient_ids), True, current_response.call_status),
        )
    st.header("Patient-gegevens")
    if enable_dev_mode:
        st.write(f"- ID: {patient_ids[st.session_state['name_idx']]}")

    render_patient_info(
        Session,
        current_response,
        current_patient,
        current_patient_nmbr,
        call_number_list,
    )

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
            options=status_list,
            index=status_list.index(current_response.call_status),
            key="status_input",
        )
        st.selectbox(
            "Resultaat gesprek: ",
            options=res_list,
            index=res_list.index(current_response.call_outcome),
            key="res_input",
        )
        options_idx = [0, 1, 2, 3]
        st.selectbox(
            "Contact gemaakt via: ",
            options=options_idx,
            format_func=lambda x: call_number_list[x],
            index=options_idx.index(current_patient_nmbr.call_number),
            key="number_input",
        )
        st.text_input("Opmerkingen: ", value=current_response.remarks, key="opm_input")
        st.form_submit_button(
            "Opslaan",
            on_click=next_preds,
            args=(
                len(all_predictions_df),
                Session,
                current_response,
                current_patient_nmbr,
            ),
            type="primary",
        )
    st.button(
        "Vorige",
        on_click=previous_preds,
    )
    st.divider()
    st.write(f"Laatste update: {last_updated:%Y-%m-%d %H:%M:%S}")


if __name__ == "__main__":
    main()
