import logging
import os
import pickle
from pathlib import Path
from typing import Dict, Union

import mlflow
import pandas as pd
from dotenv import load_dotenv
from matplotlib import pyplot as plt
from sklearn.base import BaseEstimator
from sklearn.calibration import CalibrationDisplay
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, train_test_split

from noshow.config import setup_root_logger

logger = logging.getLogger(__name__)


def train_cv_model(
    featuretable: pd.DataFrame,
    output_path: Union[Path, str],
    classifier: BaseEstimator,
    param_grid: Dict,
    save_exp: bool = True,
) -> None:
    """Use Cross validation to train a model and save results and parameters to mlflow

    Parameters
    ----------
    featuretable : pd.DataFrame
        The featuretable
    output_path : Union[Path, str]
        Path to the output folder where to store the dvc results
    classifier : BaseEstimator
        The classifier to use
    param_grid : Dict
        The parameter grid to search for the best model
    save_exp : bool
        If we want to save the experiment to MLFlow, by default True
    """

    if save_exp:
        mlflow.set_experiment("Periodic Retraining")
        mlflow.autolog(log_models=False)

        if os.getenv("MLFLOW_TRACKING_URI") is None:
            logger.warning(
                "MLFLOW_TRACKING_URI is not set, will default to mlruns directory."
            )

        run_id = mlflow.start_run().info.run_id

    featuretable["no_show"] = (
        featuretable["no_show"].replace({"no_show": "1", "show": "0"}).astype(int)
    )

    X, y = featuretable.drop(columns="no_show"), featuretable["no_show"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0, shuffle=False
    )

    train_groups = X_train.index.get_level_values("pseudo_id")

    cv = StratifiedGroupKFold()

    # Train the pipeline on the training data
    grid = GridSearchCV(
        classifier,
        param_grid=param_grid,
        cv=cv,
        scoring=["roc_auc", "precision", "recall"],
        verbose=2,
        refit="roc_auc",
        n_jobs=5,
    )
    grid.fit(X_train, y_train, groups=train_groups)

    y_pred = grid.best_estimator_.predict_proba(X_test)  # type: ignore
    test_roc_auc = roc_auc_score(y_test, y_pred[:, 1])

    # Create and log calibration curve
    fig, ax = plt.subplots(figsize=(10, 6))
    CalibrationDisplay.from_predictions(y_test, y_pred[:, 1], n_bins=10, ax=ax)
    ax.set_title("Calibration Curve")
    ax.set_xlabel("Mean Predicted Probability")
    ax.set_ylabel("Fraction of Positives")
    plt.tight_layout()

    if save_exp and mlflow.active_run():
        mlflow.log_metric("test_roc_auc", float(test_roc_auc))
        mlflow.log_figure(fig, "calibration_curve.png")
    elif save_exp:
        logger.info("Mlflow run not active, re-activating run to log custom metrics.")
        with mlflow.start_run(run_id=run_id):
            mlflow.log_metric("test_roc_auc", float(test_roc_auc))
            mlflow.log_figure(fig, "calibration_curve.png")

    model_path = Path(output_path) / "no_show_model_cv.pickle"
    with open(model_path, "wb") as f:
        pickle.dump(grid.best_estimator_, f)
    logger.info(f"Model saved to {model_path}")


if __name__ == "__main__":
    load_dotenv(override=True)
    setup_root_logger()
    project_folder = Path(__file__).parents[3]

    featuretable = pd.read_parquet(
        project_folder / "data" / "processed" / "featuretable.parquet"
    )

    model = HistGradientBoostingClassifier(categorical_features=["hour", "weekday"])

    best_model = train_cv_model(
        featuretable=featuretable,
        output_path=project_folder / "output" / "models",
        classifier=model,
        param_grid={
            "max_iter": [200, 300, 500],
            "learning_rate": [0.01, 0.05, 0.1],
        },
    )
