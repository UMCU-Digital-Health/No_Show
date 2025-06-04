import logging
import os
import tomllib
from datetime import date, datetime
from pathlib import Path
from typing import cast

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import select

from noshow.config import setup_root_logger
from noshow.dashboard.connection import get_patient_list, init_session
from noshow.dashboard.helper import get_user
from noshow.dashboard.layout import (
    render_appointment_overview,
    render_patient_info,
    render_patient_selection,
)
from noshow.database.models import (
    ApiCallResponse,
    ApiPatient,
    ApiPrediction,
    ApiRequest,
    ApiSensitiveInfo,
)
from noshow.preprocessing.utils import add_working_days

load_dotenv(override=True)  # VS Code corrupts the .env file so override

logger = logging.getLogger(__name__)
setup_root_logger()

with open(Path(__file__).parents[1] / "pyproject.toml", "rb") as f:
    config = tomllib.load(f)

VERSION = config["project"]["version"]

if "name_idx" not in st.session_state:
    st.session_state["name_idx"] = 0
if "pred_idx" not in st.session_state:
    st.session_state["pred_idx"] = 0
if "being_called" not in st.session_state:
    st.session_state["being_called"] = False
if "saved" not in st.session_state:
    st.session_state["saved"] = False


date_3_days = add_working_days(datetime.today(), 3)


def reset_name_index() -> None:
    """Reset the name index when changing the date"""
    st.session_state["name_idx"] = 0
    st.session_state["pred_idx"] = 0
    st.session_state["being_called"] = False
    st.session_state["saved"] = False


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

    user_name = get_user(st.context.headers)
    with st.sidebar:
        st.write(f"Ingelogd als: {user_name}")
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
    session_object = init_session()
    with session_object() as session:
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
                ApiPrediction.clinic_teleq_unit,
                ApiPrediction.clinic_reception,
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

    render_patient_selection(patient_ids, session_object, enable_dev_mode)
    all_predictions_df = pd.DataFrame(patient_predictions)
    if all_predictions_df.empty:
        st.error(
            "Voorspellingen voor deze patient zijn niet meer beschikbaar. "
            "Ga naar de volgende patient.",
            icon="🚫",
        )
        logger.warning(
            "Predictions for current patient no longer available in the database."
        )
        return
    last_updated = all_predictions_df["timestamp"].max()
    all_predictions_df = all_predictions_df.drop(columns="timestamp")
    all_predictions_df["call_status"] = all_predictions_df["call_status"].fillna("🔴")
    all_predictions_df["call_status"] = all_predictions_df["call_status"].replace(
        {"Gebeld": "🟢", "Wordt gebeld": "📞", "Niet gebeld": "❌"}
    )

    if (
        st.session_state["pred_idx"] != 0
        and all_predictions_df.at[st.session_state["pred_idx"], "call_status"] == "🔴"
    ):
        all_predictions_df.at[st.session_state["pred_idx"], "call_status"] = "📞"
    pred_id = int(all_predictions_df.iat[st.session_state["pred_idx"], 0])

    # load information related to call history
    with session_object() as session:
        current_response = session.get(ApiPrediction, pred_id).callresponse_relation
        current_patient_nmbr = session.get(
            ApiPatient, patient_ids[st.session_state["name_idx"]]
        )
    if not current_response:
        current_response = ApiCallResponse(
            call_status="Niet gebeld",
            call_outcome="Onbereikbaar",
            remarks="",
            prediction_id=pred_id,
        )
    # convert rows that are initiallised as None to 0
    if current_patient_nmbr.call_number is None:
        current_patient_nmbr.call_number = 0

    render_patient_info(
        session_object,
        current_response,
        current_patient,
        current_patient_nmbr,
    )

    render_appointment_overview(
        all_predictions_df,
        session_object,
        user_name,
        current_response,
        current_patient_nmbr,
        last_updated,
        enable_dev_mode,
    )


if __name__ == "__main__":
    main()
