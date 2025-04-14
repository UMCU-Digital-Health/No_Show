from datetime import date

import pandas as pd
import streamlit as st
from test_api import FakeDB

from noshow.dashboard.connection import get_patient_list, init_session
from noshow.dashboard.helper import (
    get_user,
    highlight_row,
    navigate_patients,
    next_preds,
    previous_preds,
    search_number,
    start_calling,
)
from noshow.dashboard.layout import (
    render_appointment_overview,
    render_patient_info,
    render_patient_selection,
)
from noshow.database.models import ApiCallResponse, ApiPatient, ApiSensitiveInfo


class FakeSessionMaker:
    """Class to mock a sqlalchemy sessionmaker."""

    def __enter__(self):
        return FakeDB()

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class FakeStreamlitSessionState:
    """Class to mock the streamlit session state."""

    def __init__(self):
        self._data = {
            "pred_idx": 0,
            "name_idx": 0,
            "status_input": "Niet gebeld",
            "res_input": "Geen antwoord",
            "opm_input": "Opmerking",
            "number_input": "123456789",
            "opt_out_checkbox": False,
            "being_called": False,
            "saved": False,
        }

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, key):
        return self._data[key]


class FakeStreamlitHeader:
    def __init__(self):
        self._data = {
            "RStudio-Connect-Credentials": '{"user": "TEST_USER"}',
        }

    def get(self, key):
        return self._data.get(key, None)


def test_init_session():
    """Test the init_session function."""
    session_object = init_session(
        user="test_user",
        passwd="test_passwd",
        host="test_host",
        port="5432",
        db="test_db",
    )
    assert session_object is not None


def test_get_patient_list():
    """Test the get_patient_list function."""
    patient_list = get_patient_list(FakeDB(), date(2023, 10, 1))
    assert isinstance(patient_list, list)


def test_highlight_row(monkeypatch):
    """Test the function that highlights a row for streamlit."""
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
    """Test the function that goes to the previous prediction."""
    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())

    previous_preds()
    assert st.session_state["pred_idx"] == 0


def test_start_calling():
    """Test the start calling function"""
    # create a fake call response
    call_response = ApiCallResponse(
        call_status="Niet gebeld", call_outcome="", remarks="", prediction_id="1"
    )

    # test the function
    start_calling(FakeSessionMaker, call_response)  # type: ignore
    assert call_response.call_status == "Wordt gebeld"
    assert st.session_state["being_called"] is True
    assert st.session_state["saved"] is False


def test_next_preds(monkeypatch):
    """Test the function that goes to the next prediction."""
    session_state = FakeStreamlitSessionState()
    session_state["being_called"] = True
    monkeypatch.setattr("streamlit.session_state", session_state)
    call_response = ApiCallResponse(
        call_status="Niet gebeld", call_outcome="", remarks="", prediction_id="1"
    )
    patient = ApiPatient(id="1")
    patient.call_number = 123456789
    patient.opt_out = 0

    next_preds(5, FakeSessionMaker, call_response, patient, "")  # type: ignore
    assert st.session_state["pred_idx"] == 1
    assert st.session_state["saved"] is False
    assert st.session_state["being_called"] is True

    session_state = FakeStreamlitSessionState()
    session_state["being_called"] = True
    monkeypatch.setattr("streamlit.session_state", session_state)
    next_preds(1, FakeSessionMaker, call_response, patient, "")  # type: ignore
    assert st.session_state["pred_idx"] == 0
    assert st.session_state["saved"] is True
    assert st.session_state["being_called"] is False


def test_navigate_patients(monkeypatch):
    """Test the function that navigates to the next or previous patient."""
    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())
    patient_ids = ["1", "2", "3"]

    # Test the following cases:
    # 1. Navigate to the next patient when the current index is not the last one
    navigate_patients(len(patient_ids), True)
    assert st.session_state["name_idx"] == 1
    assert st.session_state["pred_idx"] == 0
    assert st.session_state["saved"] is False
    assert st.session_state["being_called"] is False

    # 2. Navigate back to the previous patient
    navigate_patients(len(patient_ids), False)
    assert st.session_state["name_idx"] == 0
    assert st.session_state["pred_idx"] == 0
    assert st.session_state["saved"] is False
    assert st.session_state["being_called"] is False

    # 3. Navigate back, when the index was already 0
    navigate_patients(len(patient_ids), False)
    assert st.session_state["name_idx"] == 0

    # 4. Navigate forwards when the list has length 1 (not going forward)
    navigate_patients(1, True)
    assert st.session_state["name_idx"] == 0

    # 5 Don't navigate when status is being called
    st.session_state["being_called"] = True
    navigate_patients(5, True)
    assert st.session_state["name_idx"] == 0


def test_search_number(monkeypatch):
    """Test the function that searches for a number in the patient list."""
    # Mock the session state
    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())

    class FakeSessionMakerReturn:
        """Class to mock a sqlalchemy sessionmaker that returns a
        patient for seach_number."""

        def __enter__(self):
            return FakeDBReturn()

        def __exit__(self, exc_type, exc_value, traceback):
            pass

    class FakeDBReturn:
        """Class to mock a sqlalchemy session that returns a patient for
        search_number."""

        def execute(self, stmt):
            return self

        def scalar(self):
            return "2"

    patient_ids = ["1", "2"]
    search_number(FakeSessionMakerReturn, "123456788", patient_ids)  # type: ignore
    assert st.session_state["name_idx"] == 1
    assert st.session_state["pred_idx"] == 0


def test_get_user():
    """Test the function that gets the user from the session state."""
    user = get_user(FakeStreamlitHeader())  # type: ignore
    assert user == "test_user"

    false_header = FakeStreamlitHeader()
    false_header._data = {}
    user = get_user(false_header)  # type: ignore
    assert user == "No user"


def test_layout_functions(monkeypatch):
    """Simple test to check if layout functions don't crash."""

    monkeypatch.setattr("streamlit.session_state", FakeStreamlitSessionState())

    call_response = ApiCallResponse(
        call_status="Niet gebeld", call_outcome="Geen", remarks="", prediction_id="1"
    )
    patient = ApiPatient(id="1")
    patient.call_number = 0
    sensitive_info = ApiSensitiveInfo(
        "1", "1", "Henk Jansen", "Henk", date(1950, 1, 1), "123456789", "", ""
    )

    # Test the layout functions
    render_patient_selection(["1", "2", "3"], FakeSessionMaker, False)  # type: ignore
    render_patient_info(FakeSessionMaker, call_response, sensitive_info, patient)  # type: ignore
    render_appointment_overview(
        pd.DataFrame(columns=["id"]),
        FakeSessionMaker,  # type: ignore
        "fake user",
        call_response,
        patient,
        pd.to_datetime("2025-01-01"),
        False,
    )
