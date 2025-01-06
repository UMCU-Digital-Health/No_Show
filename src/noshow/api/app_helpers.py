import pickle
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Union

import numpy as np
import pandas as pd
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from noshow.database.models import ApiPatient, ApiPrediction, ApiSensitiveInfo


def load_model(model_path: Union[str, Path, None] = None) -> Any:
    if model_path is None:
        model_path = (
            Path(__file__).parents[3] / "output" / "models" / "no_show_model_cv.pickle"
        )

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return model


def remove_sensitive_info(
    session: Session, start_time: datetime, lookback_days: int = 7
) -> None:
    """Remove sensitive information for patients that have not been predicted on
    in the last `lookback_days` days.

    Parameters
    ----------
    session : Session
        Session variable that holds the database connection
    start_time : datetime
        The start time of the predictions
    lookback_days : int, optional
        The number of days to look back, by default 7
    """
    patients_with_recent_predictions = (
        select(ApiPrediction.patient_id)
        .where(ApiPrediction.start_time > (start_time - timedelta(days=lookback_days)))
        .distinct()
        .scalar_subquery()
    )

    session.execute(
        delete(ApiSensitiveInfo).where(
            ApiSensitiveInfo.patient_id.notin_(patients_with_recent_predictions)
        )
    )


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


# Function to apply the appropriate bin edges to each group
def apply_bins(group, bin_dict):
    edges = bin_dict[group.name]
    # Use pd.cut to segment the prediction values into bins based on the edges
    # 'labels=False' will return the indices of the bins from 0 to n_bins-1
    group["score_bin"] = pd.cut(
        group["prediction"], bins=[0] + list(edges.values())[1:] + [1], labels=False
    )
    return group


def create_treatment_groups(
    predictions: pd.DataFrame,
    session: Session,
    bin_edges: Dict[str, list],
    rct_agendas: list[str] | None = None,
) -> pd.DataFrame:
    """
    Create treatment groups based on predictions.

    Parameters
    ----------
    predictions : pd.DataFrame
        DataFrame containing predictions.
    session : Session
        Session variable that holds the database connection.
    bin_edges : Dict[str, list]
        Dictionary containing the bin edges for each group.
    rct_agendas : list[str], optional
        List of agendas that are part of the RCT, if None than all agendas are
        assumed to be part of the RCT, by default None.

    Returns
    -------
    pd.DataFrame
        DataFrame with treatment group assignments.

    Raises
    ------
    ValueError
        If the predictions DataFrame is empty.
    """
    # set random state
    random.seed(1337)

    if predictions.empty:
        raise ValueError("The predictions DataFrame is empty.")

    # get unique patient ids
    unique_patient_ids = predictions["pseudo_id"].unique().tolist()

    # Get all unique patients from the ApiPatient table and save to df
    patients = (
        session.query(ApiPatient).filter(ApiPatient.id.in_(unique_patient_ids)).all()
    )
    patients = pd.DataFrame(patients)

    if not patients.empty:
        # Merge predictions with patients to get treatment group
        predictions = pd.merge(
            predictions,
            patients[["id", "treatment_group"]],
            right_on="id",
            left_on="pseudo_id",
            how="left",
        )
    else:
        predictions.loc[:, "treatment_group"] = None

    # Treatment group 2 means excluded from RCT
    if rct_agendas is not None:
        predictions.loc[~predictions["clinic"].isin(rct_agendas), "treatment_group"] = 2

    predictions = predictions.sort_values("prediction", ascending=False)
    # apply bins based on supplied fixed score_bins
    predictions = (
        predictions.groupby("hoofdagenda")
        .apply(apply_bins, bin_dict=bin_edges, include_groups=False)
        .reset_index()
    )
    predictions = predictions.drop(columns="level_1")

    # Fill NaN values in 'treatment_group' with calculated values
    mask = predictions["treatment_group"].isnull()
    predictions.loc[mask, "treatment_group"] = (
        predictions[mask]
        .groupby(["hoofdagenda", "score_bin"])["prediction"]
        .transform(lambda x: (np.arange(len(x)) + random.randint(0, 1)) % 2)
    )

    # For every new patient assign the treatment group based on the mode
    predictions.loc[mask, "treatment_group"] = (
        predictions[mask]
        .groupby("pseudo_id")["treatment_group"]
        .transform(lambda x: x.mode()[0] if not x.mode().empty else np.nan)
    )
    # drop score_bin column
    predictions = predictions.drop(columns="score_bin")
    predictions["treatment_group"] = predictions["treatment_group"].astype(int)
    return predictions


def store_predictions(
    prediction_df: pd.DataFrame,
    db: Session,
    logger: Any,
    apirequest: Any,
    CLINIC_CONFIG: Dict[str, Any],
) -> None:
    """
    Store predictions in the database.

    Parameters
    ----------
    prediction_df : pd.DataFrame
        DataFrame containing the predictions.
    db : Session
        Database session.
    logger : Any
        Logger for logging warnings and information.
    apirequest : Any
        API request object related to the predictions.
    CLINIC_CONFIG : Dict[str, Any]
        Configuration dictionary for clinic details.
    """
    for _, row in prediction_df.iterrows():
        apisensitive = db.get(ApiSensitiveInfo, row["pseudo_id"])

        if not apisensitive:
            if row["name_text"] is None:
                row["name_text"] = ""
                logger.warning(
                    f"Patient {row['pseudo_id']} has no name_text, "
                    "replacing with empty string"
                )

            apisensitive = ApiSensitiveInfo(
                patient_id=row["pseudo_id"],
                hix_number=row["patient_id"],
                full_name=row["name_text"],
                first_name=row["name_given1_callMe"],
                birth_date=row["birthDate"],
                mobile_phone=row["telecom1_value"],
                home_phone=row["telecom2_value"],
                other_phone=row["telecom3_value"],
            )
        else:
            # name and birthdate can't change, but phone number might
            apisensitive.mobile_phone = row["telecom1_value"]
            apisensitive.home_phone = row["telecom2_value"]
            apisensitive.other_phone = row["telecom3_value"]

        apipatient = db.get(ApiPatient, row["pseudo_id"])
        if not apipatient:
            apipatient = ApiPatient(
                id=row["pseudo_id"],
            )
        apipatient.treatment_group = int(row["treatment_group"])
        apiprediction = db.get(ApiPrediction, row["APP_ID"])
        if not apiprediction:
            apiprediction = ApiPrediction(
                id=row["APP_ID"],
                patient_id=row["pseudo_id"],
                prediction=row["prediction"],
                start_time=row["start"],
                request_relation=apirequest,
                patient_relation=apipatient,
                clinic_name=row["hoofdagenda"],
                clinic_reception=row["description"],
                clinic_phone_number=CLINIC_CONFIG[row["clinic"]].phone_number,
                clinic_teleq_unit=CLINIC_CONFIG[row["clinic"]].teleq_name,
                active=True,
            )
        else:
            # All values of a prediction can be updated except the ID and treatment
            apiprediction.prediction = row["prediction"]
            apiprediction.start_time = row["start"]
            apiprediction.request_relation = apirequest
            apiprediction.clinic_name = row["hoofdagenda"]
            apiprediction.clinic_reception = row["description"]
            apiprediction.clinic_phone_number = CLINIC_CONFIG[
                row["clinic"]
            ].phone_number
            apiprediction.clinic_teleq_unit = CLINIC_CONFIG[row["clinic"]].teleq_name
            apiprediction.active = True

        db.merge(apisensitive)
        db.merge(apiprediction)
        db.merge(apipatient)
        db.commit()
