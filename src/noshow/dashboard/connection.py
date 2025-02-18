from datetime import date, timedelta
from typing import List

import streamlit as st
from sqlalchemy import Date, cast, func, select
from sqlalchemy.orm import Session, sessionmaker

from noshow.config import MUTE_PERIOD
from noshow.database.connection import get_connection_string, get_engine
from noshow.database.models import ApiCallResponse, ApiPatient, ApiPrediction


@st.cache_resource
def init_session(user: str, passwd: str, host: str, port: str, db: str) -> sessionmaker:
    """Initialize the connection to the database and cache the resource

    Parameters
    ----------
    user : str
        Username of the service account
    passwd : str
        Password of the service account
    host : str
        Host of the database
    port : int
        Database port
    db : str
        Database name

    Returns
    -------
    Engine
        The returned SQLAlchemy engine used for queries
    """

    connect_str = get_connection_string(user, passwd, host, port, db)
    engine = get_engine(connect_str)
    session_object = sessionmaker(bind=engine)
    return session_object


@st.cache_data
def get_patient_list(_session: Session, date_input: date) -> List[str]:
    """Get the patient list ordered by prediction

    This function returns a list of patient ids who need to be called

    Parameters
    ----------
    _session : Session
        Session object used to query the database
    date_input : date
        The day of the appointments we're calling for
        (generally today +3 working days)

    Returns
    -------
    List[str]
        List of unique patient ids, sorted by prediction
    """
    # Calculate the threshold date for the last call
    threshold_date = date.today() - timedelta(days=round(MUTE_PERIOD * 30.5))

    call_list = _session.execute(
        select(
            ApiPrediction.patient_id,
            ApiPatient.treatment_group,
            func.max(ApiPrediction.prediction),
        )
        .outerjoin(ApiPrediction.patient_relation)
        .outerjoin(ApiPrediction.callresponse_relation)
        .where(ApiPrediction.start_time.cast(Date) == date_input)
        .where(ApiPrediction.active)
        .where(
            (ApiCallResponse.timestamp.is_(None))
            | (cast(ApiCallResponse.timestamp, Date) <= cast(threshold_date, Date))
            | (cast(ApiCallResponse.timestamp, Date) == date.today())
        )
        .where(ApiPatient.treatment_group >= 1)
        .where((ApiPatient.opt_out.is_(None)) | (ApiPatient.opt_out == 0))
        .group_by(ApiPrediction.patient_id, ApiPatient.treatment_group)
        .distinct(ApiPrediction.patient_id)
        .order_by(ApiPatient.treatment_group, func.max(ApiPrediction.prediction).desc())
    ).all()

    patient_ids = [x.patient_id for x in call_list]
    return patient_ids
