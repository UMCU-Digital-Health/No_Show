from test_noshow import fake_appointments

from noshow.config import ClinicConfig
from noshow.preprocessing.load_data import (
    apply_config_filters,
    load_appointment_pydantic,
)


def test_include_subagendas():
    appointments_pydantic = fake_appointments()
    appointments_df = load_appointment_pydantic(appointments_pydantic)

    clinic_config = {
        "totaal_agenda": ClinicConfig(
            include_rct=True,
            phone_number="58831",
            teleq_name="Totaalagenda1",
            main_agenda_codes=["H1", "H2"],
            subagenda_exclude=False,
            subagendas=["S1"],
            appcode_exclude=False,
            appcodes=[],
        )
    }

    filtered_df = apply_config_filters(appointments_df, clinic_config)
    assert filtered_df.shape[0] == 2


def test_exclude_subagendas():
    appointments_pydantic = fake_appointments()
    appointments_df = load_appointment_pydantic(appointments_pydantic)

    clinic_config = {
        "totaal_agenda": ClinicConfig(
            include_rct=True,
            phone_number="58831",
            teleq_name="Totaalagenda1",
            main_agenda_codes=["H1", "H2"],
            subagenda_exclude=True,
            subagendas=["S1"],
            appcode_exclude=False,
            appcodes=[],
        )
    }

    filtered_df = apply_config_filters(appointments_df, clinic_config)
    assert filtered_df.shape[0] == 5


def test_include_appcodes():
    appointments_pydantic = fake_appointments()
    appointments_df = load_appointment_pydantic(appointments_pydantic)

    clinic_config = {
        "totaal_agenda": ClinicConfig(
            include_rct=True,
            phone_number="58831",
            teleq_name="Totaalagenda1",
            main_agenda_codes=["H1", "H2", "H3"],
            subagenda_exclude=False,
            subagendas=[],
            appcode_exclude=False,
            appcodes=["H46"],
        )
    }

    filtered_df = apply_config_filters(appointments_df, clinic_config)
    assert filtered_df.shape[0] == 1


def test_exclude_appcodes():
    appointments_pydantic = fake_appointments()
    appointments_df = load_appointment_pydantic(appointments_pydantic)

    clinic_config = {
        "totaal_agenda": ClinicConfig(
            include_rct=True,
            phone_number="58831",
            teleq_name="Totaalagenda1",
            main_agenda_codes=["H1", "H2", "H3"],
            subagenda_exclude=False,
            subagendas=[],
            appcode_exclude=True,
            appcodes=["H46"],
        )
    }

    filtered_df = apply_config_filters(appointments_df, clinic_config)
    assert filtered_df.shape[0] == 8
