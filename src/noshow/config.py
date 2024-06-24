import logging
from pathlib import Path

import tomli

logger = logging.getLogger(__name__)

CONFIG_PATH = Path(__file__).parents[2] / "run" / "config" / "config.toml"


def load_config(config_path: Path) -> dict:
    """Load the configuration from the specified path.

    Parameters
    ----------
    config_path : Path
        The path to the configuration file.

    Returns
    -------
    dict
        The loaded configuration as a dictionary.
    """
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomli.load(f)

    # For unit testing, return default values
    logger.error(f"Config file not found: {config_path}")
    return {
        "feature_building": {
            "mute_period": 0,
            "minutes_early_cutoff": 60,
            "appointments_last_days": 14,
        },
        "clinic_phonenumbers": {},
    }


config = load_config(CONFIG_PATH)
MUTE_PERIOD = config["feature_building"]["mute_period"]
MINUTES_EARLY_CUTOFF = config["feature_building"]["minutes_early_cutoff"]
APPOINTMENTS_LAST_DAYS = config["feature_building"]["appointments_last_days"]

CLINIC_PHONENUMBERS = config["clinic_phonenumbers"]
