import logging
from datetime import datetime, timedelta

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import Date, cast, select

from noshow.config import setup_root_logger
from noshow.dashboard.connection import init_session
from noshow.database.models import (
    ApiCallResponse,
    ApiPatient,
    ApiPrediction,
    ApiRequest,
)
from noshow.preprocessing.utils import add_working_days

logger = logging.getLogger(__name__)
setup_root_logger()

load_dotenv()

date_3_days = add_working_days(datetime.today(), 3)


def calc_calling_percentage(
    call_results_df: pd.DataFrame,
    call_outcomes: list[str],
    include_absolute: bool = True,
    include_opt_out: bool = False,
) -> str:
    """Calculates the percentage of rows that have `call_outcomes` and
    returns it as a string with two decimal places and a percentage sign.

    Also optionally include the absolute number of rows with `call_outcomes`.
    If `include_opt_out` is True, the percentage is calculated based on
    the total number of rows with `call_outcomes` and `opt_out` = 1.

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
    if include_opt_out:
        num_outcomes = len(
            call_results_df[
                (call_results_df["call_outcome"].isin(call_outcomes))
                & (call_results_df["opt_out"] == 1)
            ]
        )
    else:
        num_outcomes = len(
            call_results_df[call_results_df["call_outcome"].isin(call_outcomes)]
        )

    total = len(call_results_df)
    if total == 0:
        return "0 (0.00%)" if include_absolute else "0.00%"

    if include_absolute:
        return f"{num_outcomes} ({num_outcomes / total * 100:.2f}%)"
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
                ApiPatient.opt_out,
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
        "Aantal patienten gebeld",
        calc_calling_percentage(
            call_results_df,
            [
                "Herinnerd",
                "Verzet/Geannuleerd",
                "Onbereikbaar",
                "Voicemail ingesproken",
            ],
        ),
        help="Aantal patienten dat is gebeld, onafhankelijk van of ze bereikbaar waren",
    )
    metric_cols[1].metric(
        "Aantal patienten bereikt",
        calc_calling_percentage(call_results_df, ["Herinnerd", "Verzet/Geannuleerd"]),
        help=(
            "Aantal patienten dat is bereikt (herinnerd aan de afspraak "
            "of afspraak verzet/afgezegd)"
        ),
    )
    metric_cols[2].metric(
        "Aantal patienten herinnerd",
        calc_calling_percentage(call_results_df, ["Herinnerd"]),
        help="Aantal patienten dat is herinnerd aan de afspraak",
    )
    metric_cols[3].metric(
        "Aantal afspraken verzet of geannuleerd",
        calc_calling_percentage(call_results_df, ["Verzet/Geannuleerd"]),
        help="Aantal patienten dat de afspraak heeft verzet of geannuleerd",
    )

    metric_cols[4].metric(
        "Aantal patienten met opt-out",
        calc_calling_percentage(
            call_results_df,
            [
                "Herinnerd",
                "Verzet/Geannuleerd",
                "Geen",
                "Bel me niet",
                "Voicemail ingesproken",
                "Onbereikbaar",
            ],
            include_opt_out=True,
        ),
        help=(
            "Aantal patiënten die gebeld zijn ('Herinnerd' of 'Verzet/Geannuleerd') en "
            "hebben aangegeven in de toekomst niet meer gebeld te willen worden."
        ),
    )

    st.write("### Uitkomsten per dag")
    st.write(
        "Hieronder staat in de grafiek het aantal telefoontjes per dag van de "
        "afspraak en de uitkomst van het telefoontje. "
        "Let op dat de datum de dag van de afspraak is, de patienten worden "
        "drie dagen voor de afspraak gebeld."
    )

    show_not_called = st.checkbox("Toon niet gebelde patiënten", value=False)
    call_outcomes_plot = [
        "Herinnerd",
        "Verzet/Geannuleerd",
        "Voicemail ingesproken",
        "Onbereikbaar",
    ]
    if show_not_called:
        call_outcomes_plot.append("Niet gebeld")

    order_mapping = {k: i for i, k in enumerate(call_outcomes_plot)}
    call_results_df["order"] = call_results_df["call_outcome"].map(order_mapping)

    bar_chart = (
        alt.Chart(
            call_results_df[call_results_df["call_outcome"].isin(call_outcomes_plot)]
        )
        .mark_bar()
        .encode(
            x=alt.X(
                "yearmonthdate(date):O",
                axis=alt.Axis(title="Datum", labelAlign="center", labelAngle=0),
                bandPosition=0.5,
            ),
            y="count()",
            color=alt.Color(
                "call_outcome",
                scale=alt.Scale(
                    domain=list(order_mapping.keys()),
                    range=["#006400", "#90ee90", "#FFB90F", "#CD5C5C", "#7171C6"],
                ),
            ),
            order=alt.Order("order:Q", sort="ascending"),
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
                & (ApiPatient.treatment_group >= 1)
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

    session_object = init_session()

    with st.sidebar:
        date_input = st.date_input(
            "Selecteer een tijdsperiode",
            (datetime.today() - timedelta(days=7), date_3_days),
        )

    nav = st.navigation(
        [st.Page(kpi_page, title="KPIs"), st.Page(monitoring_page, title="Monitoring")]
    )
    nav.run()
