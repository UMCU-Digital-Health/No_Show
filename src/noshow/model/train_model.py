import pickle
from pathlib import Path
from typing import Dict, Union

import pandas as pd
from dvclive import Live
from sklearn.base import BaseEstimator
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GridSearchCV, StratifiedGroupKFold, train_test_split


def train_cv_model(
    featuretable: pd.DataFrame,
    output_path: Union[Path, str],
    classifier: BaseEstimator,
    param_grid: Dict,
    save_dvc_exp: bool = True,
    **kwargs,
) -> None:
    """Use Cross validation to train a model and save results and parameters to dvclive

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
    save_dvc_exp : bool
        If we want to save the experiment in DVC, by default True
    kwargs
        Additional arguments to pass to the dvclive.Live context manager
    """

    featuretable["no_show"] = (
        featuretable["no_show"].replace({"no_show": "1", "show": "0"}).astype(int)
    )

    X, y = featuretable.drop(columns="no_show"), featuretable["no_show"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0, shuffle=False
    )

    train_groups = X_train.index.get_level_values("pseudo_id")

    with Live(
        save_dvc_exp=save_dvc_exp,
        dir=str(Path(output_path) / "dvclive"),
        **kwargs,
    ) as live:
        # Define the final pipeline with preprocessor and random forest classifier

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

        live.log_sklearn_plot("roc", y_test, y_pred[:, 1])
        live.log_sklearn_plot("calibration", y_test, y_pred[:, 1])
        live.log_sklearn_plot("precision_recall", y_test, y_pred[:, 1])
        live.log_param("model_name", str(classifier))
        live.log_params(grid.best_params_)
        live.log_metric("best_score", grid.best_score_)
        live.log_metric(
            "mean_roc_auc", grid.cv_results_["mean_test_roc_auc"][grid.best_index_]
        )
        live.log_metric(
            "std_roc_auc", grid.cv_results_["std_test_roc_auc"][grid.best_index_]
        )
        live.log_metric(
            "mean_precision", grid.cv_results_["mean_test_precision"][grid.best_index_]
        )
        live.log_metric(
            "mean_recall", grid.cv_results_["mean_test_recall"][grid.best_index_]
        )

        model_path = Path(output_path) / "models" / "no_show_model_cv.pickle"
        with open(model_path, "wb") as f:
            pickle.dump(grid.best_estimator_, f)


if __name__ == "__main__":
    project_folder = Path(__file__).parents[3]

    featuretable = pd.read_parquet(
        project_folder / "data" / "processed" / "featuretable.parquet"
    )

    model = HistGradientBoostingClassifier(categorical_features=["hour", "weekday"])

    best_model = train_cv_model(
        featuretable=featuretable,
        output_path=project_folder / "output",
        classifier=model,
        param_grid={
            "max_iter": [200, 300, 500],
            "learning_rate": [0.01, 0.05, 0.1],
        },
    )
