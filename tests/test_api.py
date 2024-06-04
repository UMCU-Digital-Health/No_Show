from unittest.mock import patch

import pandas as pd
import pytest
from sqlalchemy.orm import Session
from test_noshow import fake_appointments, fake_model, fake_postal_codes

import noshow.api.app as app
from noshow.api.app import predict


class FakeExecute:
    def all(self):
        print("requested all results...")
        return []


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
    appointments_json = fake_appointments()
    with patch("json.loads", return_value={"name": "test", "value": 123}):
        monkeypatch.setattr(app, "process_postal_codes", fake_postal_codes)
        monkeypatch.setattr(app, "load_model", fake_model)
        monkeypatch.setattr(app, "delete", lambda x: x)
        # patch create treatment groups and add column to the dataframe
        monkeypatch.setattr(
            app, "create_treatment_groups", lambda x, y, z: x.assign(treatment_group=1)
        )

        output = await predict(appointments_json, "2023-01-05", FakeDB())
        output_df = pd.DataFrame(output)
        assert output_df.shape == (4, 15)
