import pickle
from pathlib import Path
from typing import Any, Optional, Union


def load_model(model_path: Optional[Union[str, Path]]) -> Any:
    if model_path is None:
        model_path = (
            Path(__file__).parents[3] / "output" / "models" / "no_show_model_cv.pickle"
        )

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    return model
