import os
from datetime import datetime, timedelta

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import select

from noshow.dashboard.connection import init_session
from noshow.database.models import ApiPrediction, ApiSensitiveInfo

load_dotenv()


db_user = os.environ["DB_USER"]
db_passwd = os.environ["DB_PASSWD"]
db_host = os.environ["DB_HOST"]
db_port = os.environ["DB_PORT"]
db_database = os.environ["DB_DATABASE"]


def main():
    st.set_page_config(page_title="No Show bel-dashboard")
    st.write("# Alarmen en Voorspellingen")

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
                ApiPrediction.prediction,
                ApiSensitiveInfo.clinic_reception,
                ApiSensitiveInfo.clinic_phone_number,
            )
            .outerjoin(ApiPrediction.sensitiveinfo_relation)
            .order_by(ApiPrediction.call_order)
        ).all()

        all_predictions_df = pd.DataFrame(all_predictions)
    st.data_editor(all_predictions_df)


if __name__ == "__main__":
    main()
