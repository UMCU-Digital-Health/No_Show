import pickle
from pathlib import Path
from typing import Any, Union


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
