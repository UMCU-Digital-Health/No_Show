import os

import pandas as pd
import pytest
from sqlalchemy.orm import Session
from test_noshow import fake_appointments, fake_bins, fake_model, fake_postal_codes

import noshow.api.app as app
import noshow.api.app_helpers as app_helpers
from noshow.api.app import predict


class FakeExecute:
    def all(self):
        print("requested all results...")
        return []


class FakeWhere:
    def where(self, stmt):
        print(f"{stmt} executed (with where)...")


class FakeDB(Session):
    def commit(self):
        print("committed")

    def merge(self, table):
        print(f"{table} merged...")

    def add(self, tmp):
        print(f"{tmp} added")

    def execute(self, stmt):
        print(f"{stmt} executed...")

    def scalars(self, stmt):
        execute_res = FakeExecute()
        print(f"{stmt} executed (with scalars)...")
        return execute_res

    def get(self, table, index):
        print(f"Requesting {table} at index {index}...")
        return None


@pytest.mark.asyncio
async def test_predict_endpoint(monkeypatch):
    os.environ["DB_USER"] = ""
    os.environ["X_API_KEY"] = "test"
    appointments_json = fake_appointments()
    monkeypatch.setattr(app, "get_bins", fake_bins)
    monkeypatch.setattr(app, "process_postal_codes", fake_postal_codes)
    monkeypatch.setattr(app, "load_model", fake_model)
    monkeypatch.setattr(app_helpers, "delete", lambda x: FakeWhere())
    # patch create treatment groups and add column to the dataframe
    monkeypatch.setattr(
        app, "create_treatment_groups", lambda x, y, z, q: x.assign(treatment_group=1)
    )

    output = await predict(appointments_json, "2024-07-16", FakeDB(), "test")
    output_df = pd.DataFrame(output)
    assert output_df.shape == (5, 16)
