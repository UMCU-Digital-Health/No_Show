from pathlib import Path
from typing import Dict, Union

import pandas as pd
from dvclive import Live
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import OneHotEncoder


def train_cv_model(
    featuretable_path: Union[Path, str], output_path: Union[Path, str], param_grid: Dict
) -> None:
    """Use Cross validation to train a model and save results and parameters to dvclive

    Parameters
    ----------
    featuretable_path : Union[Path, str]
        Path to the featuretable
    output_path : Union[Path, str]
        Path to the output folder where to store the dvc results
    """

    featuretable = pd.read_parquet(featuretable_path)

    featuretable["no_show"] = featuretable["no_show"].replace({"no_show": 1, "show": 0})

    X, y = featuretable.drop(columns="no_show"), featuretable["no_show"]

    X_train, _, y_train, _ = train_test_split(
        X, y, test_size=0.2, random_state=0, shuffle=False
    )

    with Live(save_dvc_exp=True, dir=Path(output_path) / "dvclive") as live:
        oversampler = SMOTE()

        # Define the categorical columns in your feature matrix
        categorical_cols = [col for col in X.columns if X[col].dtype == "object"]
        num_cols = [col for col in X.columns if X[col].dtype != "object"]

        # Define the preprocessor pipeline for the categorical columns
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", "passthrough", num_cols),
                ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_cols),
            ]
        )

        # Define the final pipeline with preprocessor and random forest classifier
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("smotesampling", oversampler),
                ("classifier", RandomForestClassifier()),
            ]
        )

        # Train the pipeline on the training data
        grid = GridSearchCV(
            pipeline,
            param_grid=param_grid,
            cv=5,
            scoring=["roc_auc", "precision", "recall"],
            verbose=2,
            refit="roc_auc",
        )
        grid.fit(X_train, y_train)

        live.log_param("model_name", str(pipeline[-1]))
        live.log_params(grid.best_params_)
        live.log_metric("best_score", grid.best_score_)
        live.log_metric(
            "mean_precision", grid.cv_results_["mean_test_precision"][grid.best_index_]
        )
        live.log_metric(
            "mean_recall", grid.cv_results_["mean_test_recall"][grid.best_index_]
        )


if __name__ == "__main__":
    train_cv_model(
        featuretable_path=Path(__file__).parents[3]
        / "data"
        / "processed"
        / "featuretable.parquet",
        output_path=Path(__file__).parents[3] / "output",
        param_grid={"classifier__n_estimators": [75, 100]},
    )
