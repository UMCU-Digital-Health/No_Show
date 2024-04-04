import pickle
from pathlib import Path
from typing import Any, Union

import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

from noshow.database.models import ApiPrediction


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


def create_treatment_groups(predictions: pd.DataFrame) -> pd.DataFrame:
    """
    Create treatment groups based on predictions.

    Parameters
    ----------
    predictions : pd.DataFrame
        DataFrame containing prediction scores.

    Returns
    -------
    pd.DataFrame
        DataFrame with treatment group assignments.

    Notes
    -----
    This function creates treatment groups based on prediction scores. It first bins the
    prediction scores using quantile bins. Then, it performs stratified randomization
    to assign control and treatment groups based on the score bins and clinic.

    The treatment group assignment is determined by the group number modulo 2.
    If the group number is even, the patient is assigned to the control group.
    If the group number is odd, the patient is assigned to the treatment group.
    """
    # Create prediction score bins using quantile bins, for example 10
    predictions["score_bin"] = pd.qcut(predictions["prediction_score"], q=10)
    # Create stratified randomization in control and treatment groups
    predictions["treatment_group"] = (
        predictions.groupby(["clinic", "score_bin"]).ngroup() % 2
    )
    return predictions
