from typing import List

import pandas as pd
import streamlit as st
from sqlalchemy.orm import sessionmaker

from noshow.database.models import ApiCallResponse


def highlight_row(row: pd.Series) -> List[str]:
    """Highlight a row in a pandas dataframe

    Highlights the row we are additing (from the state session)

    Parameters
    ----------
    row : pd.Series
        A row from a pandas dataframe

    Returns
    -------
    List[str]
        A list of css classes or an empty list
    """
    if row.name == st.session_state["pred_idx"]:
        return ["background-color: gray; color: white"] * len(row)
    else:
        return [""] * len(row)


def previous_preds():
    """Go to previous prediction"""
    if st.session_state["pred_idx"] > 0:
        st.session_state["pred_idx"] -= 1


def next_preds(
    list_len: int,
    Session: sessionmaker,
    call_response: ApiCallResponse,
) -> None:
    """Go to the next prediction and save results

    Parameters
    ----------
    list_len : int
        Length of the prediction list
    Session : sessionmaker
        Session used to save the current call response
    call_response : ApiCallResponse
        call response object that needs to be edited
    """
    call_response.call_status = st.session_state.status_input
    call_response.call_outcome = st.session_state.res_input
    call_response.remarks = st.session_state.opm_input

    with Session() as session:
        session.merge(call_response)
        session.commit()
    if st.session_state["pred_idx"] + 1 < list_len:
        st.session_state["pred_idx"] += 1


def navigate_patients(list_len: int, navigate_forward: bool = True):
    """Navigate through patients

    Navigates through the patients list and reset the prediction index

    Parameters
    ----------
    list_len : int
        Length of patient list
    navigate_forward : bool, optional
        Whether to navigate forward or backword, by default True
    """
    if navigate_forward:
        if st.session_state["name_idx"] + 1 < list_len:
            st.session_state["name_idx"] += 1
            st.session_state["pred_idx"] = 0
    else:
        if st.session_state["name_idx"] > 0:
            st.session_state["name_idx"] -= 1
            st.session_state["pred_idx"] = 0
