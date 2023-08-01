import os
from datetime import date, datetime, timedelta
from typing import cast

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import select

from noshow.dashboard.connection import get_patient_list, init_session
from noshow.dashboard.helper import (
    highlight_row,
    navigate_patients,
    next_preds,
    previous_preds,
)
from noshow.database.models import ApiCallResponse, ApiPrediction, ApiSensitiveInfo

load_dotenv()


db_user = os.environ["DB_USER"]
db_passwd = os.environ["DB_PASSWD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_DATABASE"]

if "name_idx" not in st.session_state:
    st.session_state["name_idx"] = 0
if "pred_idx" not in st.session_state:
    st.session_state["pred_idx"] = 0

date_3_days = datetime.today() + timedelta(days=3)
if date_3_days.weekday() == 5:  # Saturday
    date_3_days = date_3_days + timedelta(days=2)
elif date_3_days.weekday() == 6:  # Sunday
    date_3_days = date_3_days + timedelta(days=1)


def main():
    st.set_page_config(page_title="No Show bel-dashboard")

    with st.sidebar:
        date_input = st.date_input(
            "Voor welke dag wil je bellen (standaard over 3 dagen)", date_3_days
        )

    if not date_input:
        return None
    date_input = cast(date, date_input)
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
                ApiPrediction.clinic_reception,
                ApiPrediction.clinic_phone_number,
                ApiCallResponse.call_status,
            )
            .outerjoin(ApiPrediction.callresponse_relation)
            .where(ApiPrediction.start_time >= date_input)
            .where(
                ApiPrediction.patient_id == patient_ids[st.session_state["name_idx"]]
            )
        ).all()

    all_predictions_df = pd.DataFrame(patient_predictions)
    all_predictions_df.loc[
        all_predictions_df["call_status"] == "Gebeld", "call_status"
    ] = "🟢"
    all_predictions_df.loc[
        all_predictions_df["call_status"] != "🟢", "call_status"
    ] = "🔴"
    pred_id = int(all_predictions_df.iat[st.session_state["pred_idx"], 0])
    col1, col2 = st.columns(2)
    with col1:
        st.button(
            "Vorige patient", on_click=navigate_patients, args=(len(patient_ids), False)
        )
    with col2:
        st.button(
            "Volgende patient",
            on_click=navigate_patients,
            args=(len(patient_ids), True),
        )

    st.header("Patient-gegevens")
    st.write(f"- Naam: {current_patient.full_name}")
    st.write(f"- Voornaam: {current_patient.first_name}")
    st.write(f"- Geboortedatum: {current_patient.birth_date}")
    st.write(f"- Mobiel: {current_patient.mobile_phone}")
    st.write(f"- Thuis: {current_patient.home_phone}")
    st.write(f"- Overig nummer: {current_patient.other_phone}")

    st.header("Afspraakoverzicht")
    st.dataframe(
        all_predictions_df.drop(columns="id").style.apply(highlight_row, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    with Session() as session:
        current_response = session.get(ApiPrediction, pred_id).callresponse_relation
    if not current_response:
        current_response = ApiCallResponse(
            call_status="Niet gebeld",
            call_outcome="Geen",
            remarks="",
            prediction_id=pred_id,
        )
    with st.form("patient_form", clear_on_submit=True):
        status_list = ["Niet gebeld", "Gebeld", "Onbereikbaar"]
        res_list = ["Herinnerd", "Verzet/Geannuleerd", "Geen"]
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
        st.text_input("Opmerkingen: ", value=current_response.remarks, key="opm_input")
        st.form_submit_button(
            "Volgende",
            on_click=next_preds,
            args=(
                len(all_predictions_df),
                Session,
                current_response,
            ),
            type="primary",
        )
    st.button(
        "Vorige",
        on_click=previous_preds,
    )


if __name__ == "__main__":
    main()
