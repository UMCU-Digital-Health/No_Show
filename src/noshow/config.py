from pathlib import Path

import tomli

CONFIG_PATH = Path(__file__).parents[2] / "run" / "config" / "config.toml"

with open(CONFIG_PATH, "rb") as f:
    config = tomli.load(f)


MUTE_PERIOD = config["feature_building"]["mute_period"]
MINUTES_EARLY_CUTOFF = config["feature_building"]["minutes_early_cutoff"]
APPOINTMENTS_LAST_DAYS = config["feature_building"]["appointments_last_days"]

CLINIC_PHONENUMBERS = config["clinic_phonenumbers"]
