import logging
import os
import sys
import tomllib
from pathlib import Path
from typing import Dict, List

from pydantic import BaseModel
from rich.logging import RichHandler

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parents[2] / "run" / "config" / "config.toml"


class PreprocessConfig(BaseModel):
    """Preprocessing configuration, contains the codes used for no-shows in HiX"""

    no_show_codes: list[str] = ["N", "0000000012", "0000000013"]


class FeatureBuildingConfig(BaseModel):
    """Feature building configuration, contains the cutoff value for calculating
    the tardiness of patients and how many days of appointments to include for the
    number of appointments in the last days feature."""

    minutes_early_cutoff: int = 60
    appointments_last_days: int = 14


class DashboardConfig(BaseModel):
    """Dashboards configuration. contains how long a called patient should be
    muted and how long sensitive data should be kept.
    """

    mute_period: int = 0
    keep_sensitive_data: int = 14


class ClinicConfig(BaseModel):
    """Clinic configuration, used for clinic-specific information and
    filtering of appointments."""

    include_rct: bool
    phone_number: str
    teleq_name: str
    main_agenda_codes: List[str]
    subagenda_exclude: bool
    subagendas: List[str]
    appcode_exclude: bool
    appcodes: List[str]


class ProjectConfig(BaseModel):
    """Main project configuration, holds all configuration settings for the project."""

    preprocess: PreprocessConfig
    feature_building: FeatureBuildingConfig
    dashboard: DashboardConfig
    clinic: Dict[str, ClinicConfig]


def load_config(config_path: Path) -> ProjectConfig:
    """Load the configuration from the specified path.

    Parameters
    ----------
    config_path : Path
        The path to the configuration file.

    Returns
    -------
    ProjectConfig
        The project configuration read from the toml file.
    """
    if config_path.exists():
        with open(config_path, "rb") as f:
            config_dict = tomllib.load(f)
            return ProjectConfig(**config_dict)

    # For unit testing, return test values
    logger.error(f"Config file not found: {config_path}")
    return ProjectConfig(
        preprocess=PreprocessConfig(),
        feature_building=FeatureBuildingConfig(),
        dashboard=DashboardConfig(),
        clinic={
            "revalidatie_en_sport": ClinicConfig(
                include_rct=True,
                phone_number="58831",
                teleq_name="Sport en Revalidatie",
                main_agenda_codes=["ZH0307", "ZH0435"],
                subagenda_exclude=True,
                subagendas=[],
                appcode_exclude=False,
                appcodes=["CF15", "CF30"],
            )
        },
    )


def setup_root_logger() -> None:
    """Setup the root logger for the project.
    This function sets up the root logger with a specific format and level.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    # Some packages have already initialized the root logger, so we need to remove
    # their handlers first.
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Posit does not support rich logging, so use a simple console handler
    if os.getenv("CONNECT_SERVER") is not None:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("%(levelname)s: [%(name)s] - %(message)s")
        )
    else:
        console_handler = RichHandler(rich_tracebacks=True)
        console_handler.setFormatter(
            logging.Formatter(
                "%(message)s",
                datefmt="[%X]",
            )
        )
    root_logger.addHandler(console_handler)


project_config = load_config(CONFIG_PATH)

NO_SHOW_CODES = project_config.preprocess.no_show_codes
MUTE_PERIOD = project_config.dashboard.mute_period
KEEP_SENSITIVE_DATA = project_config.dashboard.keep_sensitive_data

MINUTES_EARLY_CUTOFF = project_config.feature_building.minutes_early_cutoff
APPOINTMENTS_LAST_DAYS = project_config.feature_building.appointments_last_days

CLINIC_CONFIG = project_config.clinic
