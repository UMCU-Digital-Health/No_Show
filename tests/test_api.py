import pytest
from sqlalchemy.orm import Session
from test_noshow import (
    create_unit_test_clinic_config,
    fake_appointments,
    fake_bins,
    fake_model,
    fake_postal_codes,
)

import noshow.api.app as app
import noshow.api.app_helpers as app_helpers
from noshow.api.app import predict


class FakeExecute:
    def all(self):
        print("requested all results...")
        return []

    def fetchall(self):
        print("requested all results...")
        return []

    def scalar(self):
        print("requested scalar result...")
        return None

    def scalar_one_or_none(self):
        print("requested scalar result or none...")
        return None


class FakeWhere:
    def where(self, stmt):
        print(f"{stmt} executed (with where)...")


class FakeDB(Session):
    def commit(self):
        print("committed")

    def merge(self, instance, *args, **kwargs):
        print(f"{instance} merged...")

    def add(self, instance, *args, **kwargs):
        print(f"{instance} added")

    def execute(self, statement, *args, **kwargs):
        print(f"{statement} executed...")
        return FakeExecute()

    def scalars(self, statement, *args, **kwargs):
        execute_res = FakeExecute()
        print(f"{statement} executed (with scalars)...")
        return execute_res

    def get(self, entity, ident, *args, **kwargs):
        print(f"Requesting {entity} at index {ident}...")
        return None


@pytest.mark.asyncio
async def test_predict_endpoint(monkeypatch):
    appointments_pydantic = fake_appointments()
    monkeypatch.setattr(app, "get_bins", fake_bins)
    monkeypatch.setattr(app, "process_postal_codes", fake_postal_codes)
    monkeypatch.setattr(app, "load_model", fake_model)
    monkeypatch.setattr(app_helpers, "delete", lambda x: FakeWhere())
    # patch create treatment groups and add column to the dataframe
    monkeypatch.setattr(
        app, "create_treatment_groups", lambda x, y, z, q: x.assign(treatment_group=1)
    )
    monkeypatch.setattr(app, "CLINIC_CONFIG", create_unit_test_clinic_config())
    monkeypatch.setattr(app_helpers, "CLINIC_CONFIG", create_unit_test_clinic_config())
    monkeypatch.setenv("DB_USER", "")
    monkeypatch.setenv("X_API_KEY", "test")

    output = await predict(appointments_pydantic, "2024-07-16", FakeDB(), "test")
    assert output == {"message": "5 predictions created and stored in db."}


# teste empty appointments
@pytest.mark.asyncio
async def test_predict_endpoint_empty_appointments(monkeypatch):
    appointments_pydantic = fake_appointments()
    monkeypatch.setattr(app, "get_bins", fake_bins)
    monkeypatch.setattr(app, "process_postal_codes", fake_postal_codes)
    monkeypatch.setattr(app, "load_model", fake_model)
    monkeypatch.setattr(app_helpers, "delete", lambda x: FakeWhere())
    # patch create treatment groups and add column to the dataframe
    monkeypatch.setattr(
        app, "create_treatment_groups", lambda x, y, z, q: x.assign(treatment_group=1)
    )
    monkeypatch.setattr(app, "CLINIC_CONFIG", create_unit_test_clinic_config())
    monkeypatch.setenv("DB_USER", "")
    monkeypatch.setenv("X_API_KEY", "test")

    # empty appointments
    with pytest.raises(Exception) as exc_info_empty:
        __ = await predict([], "2024-07-16", FakeDB(), "test")
    assert "400: Input cannot be empty." in str(exc_info_empty.value)

    # no appointments for the start date
    with pytest.raises(Exception) as exc_inf_wrong_date:
        __ = await predict(appointments_pydantic, "2024-07-15", FakeDB(), "test")
    assert "400: No appointments for the start date and filters" in str(
        exc_inf_wrong_date.value
    )
