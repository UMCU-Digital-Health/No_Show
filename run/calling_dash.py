import os
from datetime import datetime, timedelta
from typing import List

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from noshow.dashboard.connection import init_session
from noshow.database.models import ApiCallResponse, ApiPrediction, ApiSensitiveInfo

load_dotenv()


db_user = os.environ["DB_USER"]
db_passwd = os.environ["DB_PASSWD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_DATABASE"]

if "name_idx" not in st.session_state:
    st.session_state["name_idx"] = 0


def highlight_row(row: pd.Series) -> List[str]:
    if row.name == st.session_state["name_idx"]:
        return ["background-color: gray; color: white"] * len(row)
    else:
        return [""] * len(row)


def next_patient(list_len: int, Session: sessionmaker, pred_id: int) -> None:
    with Session() as session:
        call_response = session.scalar(
            select(ApiCallResponse).where(ApiCallResponse.prediction_id == pred_id)
        )
        if not call_response:
            call_response = ApiCallResponse(
                call_status=st.session_state.status_input,
                call_outcome=st.session_state.res_input,
                remarks=st.session_state.opm_input,
                prediction_id=int(pred_id),
            )
        else:
            call_response.call_status = st.session_state.status_input
            call_response.call_outcome = st.session_state.res_input
            call_response.remarks = st.session_state.opm_input

        session.merge(call_response)
        session.commit()
    if st.session_state["name_idx"] + 1 < list_len:
        st.session_state["name_idx"] += 1


def prev_patient() -> None:
    if st.session_state["name_idx"] > 0:
        st.session_state["name_idx"] -= 1


def main():
    st.set_page_config(page_title="No Show bel-dashboard", layout="wide")
    st.header("Bel-overzicht")

    date_3_days = datetime.today() + timedelta(days=3)
    if date_3_days.weekday() == 5:
        date_3_days = date_3_days + timedelta(days=2)
    elif date_3_days.weekday() == 6:
        date_3_days = date_3_days + timedelta(days=1)

    with st.sidebar:
        date_input = st.date_input(
            "Voor welke dag wil je bellen (standaard over 3 dagen)", date_3_days
        )
    if not date_input:
        return None
    Session = init_session(db_user, db_passwd, db_host, db_port, db_database)
    with Session() as session:
        all_predictions = session.execute(
            select(
                ApiPrediction.call_order,
                ApiPrediction.start_time,
                ApiSensitiveInfo.full_name,
                ApiSensitiveInfo.first_name,
                ApiSensitiveInfo.mobile_phone,
                ApiSensitiveInfo.home_phone,
                ApiSensitiveInfo.other_phone,
                ApiSensitiveInfo.clinic_reception,
                ApiSensitiveInfo.clinic_phone_number,
                ApiCallResponse.call_status,
                ApiPrediction.id,
            )
            .outerjoin(ApiPrediction.sensitiveinfo_relation)
            .outerjoin(ApiPrediction.callresponse_relation)
            .order_by(ApiPrediction.call_order)
        ).all()

    all_predictions_df = pd.DataFrame(all_predictions)

    all_predictions_df.loc[
        all_predictions_df["call_status"] != "Gebeld", "call_status"
    ] = "🔴"
    all_predictions_df.loc[
        all_predictions_df["call_status"] == "Gebeld", "call_status"
    ] = "🟢"
    pred_id = int(all_predictions_df.iat[st.session_state["name_idx"], 10])

    st.dataframe(
        all_predictions_df.drop(columns=["id"]).style.apply(highlight_row, axis=1),
        use_container_width=True,
        hide_index=True,
    )

    st.header(f"Gesprek met {all_predictions_df.iloc[st.session_state['name_idx'], 2]}")
    with Session() as session:
        current_response = session.scalar(
            select(ApiCallResponse).where(ApiCallResponse.prediction_id == pred_id)
        )

    with st.form("patient_form"):
        status_list = ["Niet gebeld", "Gebeld", "Onbereikbaar"]
        res_list = ["Herinnerd", "Verzet/Geannuleerd"]
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
            on_click=next_patient,
            args=(
                len(all_predictions_df),
                Session,
                pred_id,
            ),
            type="primary",
        )

    st.button("Vorige", on_click=prev_patient)


if __name__ == "__main__":
    main()
