from datetime import date

import pandas as pd
import streamlit as st
from test_api import FakeDB

from noshow.dashboard.connection import get_patient_list, init_session
from noshow.dashboard.helper import (
    highlight_row,
    next_preds,
    previous_preds,
    start_calling,
)
from noshow.database.models import ApiCallResponse, ApiPatient


class FakeSessionMaker:
    def __enter__(self):
        return FakeDB()

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeStreamlitSessionState:
    def __init__(self):
        self._data = {
            "pred_idx": 0,
            "status_input": "Niet gebeld",
            "res_input": "Geen antwoord",
            "opm_input": "Opmerking",
            "number_input": "123456789",
            "opt_out_checkbox": False,
        }

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, key):
        return self._data[key]


def test_init_session():
    session_object = init_session(
        user="test_user",
        passwd="test_passwd",
        host="test_host",
        port="5432",
        db="test_db",
    )
    assert session_object is not None


def test_get_patient_list():
    patient_list = get_patient_list(FakeDB(), date(2023, 10, 1))
    assert isinstance(patient_list, list)


def test_highlight_row(monkeypatch):
    # monkeypatch the st.session_state
    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())

    # create a sample series
    row = pd.Series([1, 2, 3], name=0)
    empty_row = pd.Series([1, 2, 3], name=1)

    # test the function
    highlighted_row = highlight_row(row)
    highlighted_empty_row = highlight_row(empty_row)
    assert highlighted_row == ["background-color: gray; color: white"] * len(row)
    assert highlighted_empty_row == ["", "", ""]


def test_previous_preds(monkeypatch):
    # monkeypatch the st.session_state
    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())

    # test the function
    previous_preds("Niet gebeld")
    assert st.session_state["pred_idx"] == 0

    monkeypatch.setattr("streamlit.session_state", {"pred_idx": 1})
    # test when call_status is "Wordt gebeld"
    previous_preds("Wordt gebeld")
    assert st.session_state["pred_idx"] == 1


def test_start_calling():
    # create a fake call response
    call_response = ApiCallResponse(
        call_status="Niet gebeld", call_outcome="", remarks="", prediction_id="1"
    )

    # test the function
    start_calling(FakeSessionMaker, call_response)
    assert call_response.call_status == "Wordt gebeld"


def test_next_preds(monkeypatch):
    # monkeypatch the st.session_state
    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())
    # create a fake call response
    call_response = ApiCallResponse(
        call_status="Niet gebeld", call_outcome="", remarks="", prediction_id="1"
    )
    patient = ApiPatient(id="1")
    patient.call_number = 123456789
    patient.opt_out = 0

    # test the function
    next_preds(5, FakeSessionMaker, call_response, patient, "")
    assert st.session_state["pred_idx"] == 1

    st.session_state["pred_idx"] = 0
    next_preds(1, FakeSessionMaker, call_response, patient, "")
    assert st.session_state["pred_idx"] == 0
