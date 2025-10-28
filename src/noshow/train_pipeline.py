"""Pipeline for the entire training process, from exporting the data to training
the model."""

import logging
from pathlib import Path

import click
from dotenv import load_dotenv
from sklearn.ensemble import HistGradientBoostingClassifier

from noshow.config import CLINIC_CONFIG, setup_root_logger
from noshow.database.export import export_data
from noshow.features.feature_pipeline import create_features, select_feature_columns
from noshow.model.train_model import train_cv_model
from noshow.preprocessing.load_data import (
    load_appointment_csv,
    process_appointments,
    process_postal_codes,
)

logger = logging.getLogger(__name__)


@click.command()
@click.option("--skip-export", is_flag=True, help="Skip data export from the database.")
def train_pipeline(skip_export: bool) -> None:
    """Main function to run the training pipeline for the no-show model."""
    load_dotenv(override=True)
    setup_root_logger()

    if not skip_export:
        logger.info("Starting data export...")
        export_data()

    data_path = Path(__file__).parents[2] / "data" / "raw"
    output_path = Path(__file__).parents[2] / "data" / "processed"
    model_path = Path(__file__).parents[2] / "output" / "models"

    logger.info("Processing data...")
    appointments_df = load_appointment_csv(data_path / "poliafspraken_no_show.csv")
    appointments_df = process_appointments(appointments_df, CLINIC_CONFIG)
    all_postalcodes = process_postal_codes(data_path / "NL.txt")
    appointments_features = create_features(appointments_df, all_postalcodes).pipe(
        select_feature_columns
    )
    appointments_features.to_parquet(output_path / "featuretable.parquet")
    logger.info(
        "Data processing completed and saved to "
        f"{output_path / 'featuretable.parquet'}."
    )

    logger.info("Start training...")

    model = HistGradientBoostingClassifier(categorical_features=["hour", "weekday"])

    train_cv_model(
        featuretable=appointments_features,
        output_path=model_path,
        classifier=model,
        param_grid={
            "max_iter": [200, 300, 500],
            "learning_rate": [0.01, 0.05, 0.1],
        },
    )


if __name__ == "__main__":
    train_pipeline()
