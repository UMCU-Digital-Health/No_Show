import os
from datetime import datetime, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import Date, cast, select

from noshow.dashboard.connection import init_session
from noshow.database.models import (
    ApiCallResponse,
    ApiPatient,
    ApiPrediction,
    ApiRequest,
)
from noshow.preprocessing.utils import add_working_days

load_dotenv()

date_3_days = add_working_days(datetime.today(), 3)

# Global and env variables
db_user = os.environ["DB_USER"]
db_passwd = os.environ["DB_PASSWD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_DATABASE"]


def calc_calling_percentage(
    call_results_df: pd.DataFrame, call_outcomes: list[str]
) -> str:
    """Calculates the percentage of rows that have `call_outcomes` and
    returns it as a string with two decimal places and a percentage sign.

    Parameters
    ----------
    call_results_df : pd.DataFrame
        The DataFrame containing the call results
    call_outcomes : list[str]
        The outcomes to calculate the percentage for

    Returns
    -------
    str
        The percentage formatted as a string
    """
    num_outcomes = len(
        call_results_df[call_results_df["call_outcome"].isin(call_outcomes)]
    )
    total = len(call_results_df)
    return f"{num_outcomes / total * 100:.2f}%"


def kpi_page():
    """Page that contains basic KPIs for the no-show project"""
    st.write("## KPIs")

    if not isinstance(date_input, tuple) or len(date_input) != 2:
        st.info("Selecteer een tijdsperiode")
        return

    with session_object() as session:
        call_results = session.execute(
            select(
                ApiPrediction.start_time,
                ApiPrediction.clinic_name,
                ApiCallResponse.call_status,
                ApiCallResponse.call_outcome,
            )
            .outerjoin(ApiPrediction.callresponse_relation)
            .outerjoin(ApiPrediction.patient_relation)
            .where(
                (cast(ApiPrediction.start_time, Date) >= date_input[0])
                & (cast(ApiPrediction.start_time, Date) <= date_input[1])
                & (ApiPatient.treatment_group >= 1)
            )
        ).all()

    if not call_results:
        st.info("Geen data beschikbaar voor deze periode")
        return

    call_results_df = pd.DataFrame(call_results)
    call_results_df["date"] = call_results_df["start_time"].dt.date
    call_results_df.loc[call_results_df["call_outcome"].isnull(), "call_outcome"] = (
        "Niet gebeld"
    )
    call_results_df.loc[call_results_df["call_outcome"] == "Geen", "call_outcome"] = (
        "Onbereikbaar"
    )
    call_results_df["color_sort"] = call_results_df["call_outcome"].map(
        {
            "Niet gebeld": 0,
            "Onbereikbaar": 1,
            "Herinnerd": 2,
            "Verzet/Geannuleerd": 3,
            "Bel me niet": 4,
        }
    )

    clinic_selection_col, _ = st.columns([1, 2])
    clinic_selection = clinic_selection_col.selectbox(
        "Kies een kliniek",
        np.insert(call_results_df["clinic_name"].unique(), 0, "Alle poli's"),
        index=0,
    )
    if clinic_selection != "Alle poli's":
        call_results_df = call_results_df[
            call_results_df["clinic_name"] == clinic_selection
        ]

    metric_cols = st.columns(5)
    metric_cols[0].metric(
        "Aantal Hoofdagenda's", call_results_df["clinic_name"].nunique()
    )
    metric_cols[1].metric(
        "Aantal patienten herinnerd",
        len(call_results_df[call_results_df["call_outcome"] == "Herinnerd"]),
    )
    metric_cols[2].metric(
        "Aantal afspraken verzet of geannuleerd",
        len(call_results_df[call_results_df["call_outcome"] == "Verzet/Geannuleerd"]),
    )
    percentage_reached = calc_calling_percentage(
        call_results_df, ["Herinnerd", "Verzet/Geannuleerd"]
    )
    metric_cols[3].metric(
        "Percentage patienten bereikt",
        percentage_reached,
    )
    percentage_called = calc_calling_percentage(
        call_results_df, ["Herinnerd", "Verzet/Geannuleerd", "Onbereikbaar"]
    )
    metric_cols[4].metric(
        "Percentage patienten gebeld",
        percentage_called,
    )

    st.write("### Uitkomsten per dag")
    st.write(
        "Hieronder staat in de grafiek het aantal telefoontjes per dag van de "
        "afspraak en de uitkomst van het telefoontje. "
        "Let op dat de datum de dag van de afspraak is, de patienten worden "
        "drie dagen voor de afspraak gebeld."
    )
    bar_chart = (
        alt.Chart(call_results_df)
        .mark_bar()
        .encode(
            x=alt.X("date:T").timeUnit("yearmonthdate"),
            y="count()",
            color=alt.Color(
                "call_outcome",
                sort=[
                    "Niet gebeld",
                    "Onbereikbaar",
                    "Herinnerd",
                    "Verzet/Geannuleerd",
                    "Bel me niet",
                ],
            ),
            order=alt.Order("color_sort", sort="descending"),
        )
    )
    st.altair_chart(bar_chart, use_container_width=True)


def monitoring_page():
    """Page that contains monitoring information for the no-show project"""
    st.write("## Monitoring")

    if not isinstance(date_input, tuple) or len(date_input) != 2:
        st.info("Selecteer een tijdsperiode")
        return

    with session_object() as session:
        monitoring_data = session.execute(
            select(
                ApiRequest.timestamp,
                ApiRequest.api_version,
                ApiRequest.response_code,
                ApiRequest.runtime,
                ApiPrediction.prediction,
                ApiPrediction.clinic_name,
            )
            .outerjoin(ApiPrediction.request_relation)
            .outerjoin(ApiPrediction.patient_relation)
            .where(
                (cast(ApiRequest.timestamp, Date) >= date_input[0])
                & (cast(ApiRequest.timestamp, Date) <= date_input[1])
                & (ApiPatient.treatment_group == 1)
            )
        ).all()

        monitoring_df = pd.DataFrame(monitoring_data)
        monitoring_df["date"] = monitoring_df["timestamp"].dt.date

        metric_columns = st.columns(2)

        metric_columns[0].metric(
            "Laatste api versie", max(monitoring_df["api_version"])
        )
        metric_columns[1].metric(
            "Laatste voorspelling",
            max(monitoring_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M")),
        )

        st.write("### Runtime van de API")
        runtime_chart = (
            alt.Chart(monitoring_df)
            .mark_line()
            .encode(
                x="timestamp:T",
                y="runtime:Q",
            )
        )
        st.altair_chart(runtime_chart, use_container_width=True)

        st.write("### response codes per dag")
        response_chart = (
            alt.Chart(monitoring_df)
            .mark_bar()
            .encode(
                x="yearmonthdate(timestamp):T",
                y="count()",
                color="response_code:N",
            )
        )
        st.altair_chart(response_chart, use_container_width=True)

        st.write("### Histogram van de voorspellingen")
        histogram_chart = (
            alt.Chart(monitoring_df)
            .mark_bar()
            .encode(
                x=alt.X("prediction:Q", bin=True),
                y="count()",
            )
        )
        st.altair_chart(histogram_chart, use_container_width=True)


if __name__ == "__main__":
    st.set_page_config("No-Show Admin Dashboard", page_icon="📈", layout="wide")
    st.title("No-Show Admin Dashboard")

    session_object = init_session(db_user, db_passwd, db_host, db_port, db_database)

    with st.sidebar:
        date_input = st.date_input(
            "Selecteer een tijdsperiode",
            (datetime.today() - timedelta(days=7), date_3_days),
        )

    nav = st.navigation(
        [st.Page(kpi_page, title="KPIs"), st.Page(monitoring_page, title="Monitoring")]
    )
    nav.run()
