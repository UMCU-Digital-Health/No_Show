import pickle
from pathlib import Path
from typing import Any, Union

import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from noshow.database.models import ApiPatient, ApiPrediction


def load_model(model_path: Union[str, Path, None] = None) -> Any:
    if model_path is None:
        model_path = (
            Path(__file__).parents[3] / "output" / "models" / "no_show_model_cv.pickle"
        )

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return model


def add_clinic_phone(clinic_name: str) -> str:
    if clinic_name == "Revalidatie & Sport":
        return "58831"
    elif clinic_name == "Longziekten":
        return "56192"
    elif clinic_name == "Kind-KNO":
        return "54902"
    elif clinic_name == "Kind-Neurologie":
        return "67370"
    elif clinic_name == "Kind-Orthopedie":
        return "67470"
    elif clinic_name == "Kind-Plastische chirurgie":
        return "53594"
    else:
        return ""


def fix_outdated_appointments(
    session: Session, app_ids: pd.Series, start_date: str
) -> None:
    """Set the status of outdated appointments on inactive

    Appointments can change while the model is running, existing apointments
    will be updated by the api, but deleted appointments or appointments that
    are rescheduled further in the future need to be set to inactive to prevent
    them from showing up in the dashboard.

    Parameters
    ----------
    session : Session
        Session variable that holds the database connection
    app_ids : Union[List, Series]
        List of app ids for which a prediction has been made
    start_date : str
        start date from which the predictions are made
    """
    all_ids = session.scalars(
        select(ApiPrediction.id)
        .where(ApiPrediction.start_time >= start_date)
        .where(ApiPrediction.active)
    ).all()
    inactive_ids = set(all_ids).difference(app_ids)
    for app_id in inactive_ids:
        apiprediction = session.get(ApiPrediction, app_id)
        if apiprediction:
            apiprediction.active = False
            session.merge(apiprediction)
            session.commit()


def create_treatment_groups(
    predictions: pd.DataFrame, session: Session, n_bins: int = 4
) -> pd.DataFrame:
    """
    Create treatment groups based on predictions.

    Parameters
    ----------
    predictions : pd.DataFrame
        DataFrame containing predictions.
    session : Session
        Session variable that holds the database connection.
    n_bins : int, optional
        Number of bins to create for prediction scores (default is 4).

    Returns
    -------
    pd.DataFrame
        DataFrame with treatment group assignments.

    Raises
    ------
    ValueError
        If the predictions DataFrame is empty.
    """
    if predictions.empty:
        raise ValueError("The predictions DataFrame is empty.")

    # get unique patient ids
    unique_patient_ids = predictions["pseudo_id"].unique().tolist()

    # Get all unqiue patients from the ApiPatient table and save to df
    patients = (
        session.query(ApiPatient).filter(ApiPatient.id.in_(unique_patient_ids)).all()
    )
    patients = pd.DataFrame(patients)

    # Merge predictions with patients to get treatment group
    predictions = pd.merge(
        predictions,
        patients[["id", "treatment_group"]],
        right_on="id",
        left_on="pseudo_id",
        how="left",
    )

    # Create prediction score bins using quantile bins
    predictions["score_bin"] = pd.qcut(predictions["prediction"], q=n_bins)
    predictions = predictions.sort_values(["prediction"])

    # only keep top prediction per patient for treatment/control split
    deduplicated = predictions.drop_duplicates(subset="pseudo_id", keep="first")
    # only keep patients without treatment group
    deduplicated = deduplicated[deduplicated["treatment_group"].isnull()]

    # Create stratified randomization in control and treatment groups
    deduplicated = deduplicated.sort_values(["hoofdagenda", "prediction"])
    deduplicated["treatment_group"] = deduplicated.groupby(
        ["hoofdagenda", "score_bin"], observed=True
    )["prediction"].transform(lambda x: np.arange(len(x)) % 2)

    # update predictions with treatment groups from deduplicated based on pseudo_id
    merged = predictions.merge(
        deduplicated[["pseudo_id", "treatment_group"]],
        on="pseudo_id",
        how="left",
        suffixes=("", "_new"),
    )

    # Update the treatment_group values where there's a new value
    predictions["treatment_group"] = merged["treatment_group_new"].combine_first(
        predictions["treatment_group"]
    )
    # drop score_bin column
    predictions = predictions.drop(columns="score_bin")
    return predictions
