from datetime import date
from typing import List

import streamlit as st
from sqlalchemy import Date, create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from noshow.database.models import ApiPrediction


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

    CONNECTSTRING = rf"mssql+pymssql://{user}:{passwd}@{host}:{port}/{db}"
    engine = create_engine(CONNECTSTRING)
    session_object = sessionmaker(bind=engine)
    return session_object


@st.cache_data(ttl=600)
def get_patient_list(_session: Session, date_input: date, top_n: int = 20) -> List[str]:
    """Get the patient list ordered by prediction

    This function returns a list of patient ids who need to be called

    Parameters
    ----------
    _session : Session
        Session object used to query the database
    date_input : date
        The day of the appointments we're calling for
        (generally today +3 working days)
    top_n : int
        The number of patients to return, ordered by their maximum
        prediction.

    Returns
    -------
    List[str]
        List of unique patient ids, sorted by prediction
    """
    call_list = _session.execute(
        select(ApiPrediction.patient_id, func.max(ApiPrediction.prediction))
        .where(ApiPrediction.start_time.cast(Date) == date_input)
        .group_by(ApiPrediction.patient_id)
        .order_by(func.max(ApiPrediction.prediction).desc())
        .limit(top_n)
    ).all()
    patient_ids = [x.patient_id for x in call_list]
    return patient_ids
