import numpy as np
import pandas as pd
import pytest

from noshow.api.app_helpers import create_treatment_groups


@pytest.fixture
def empty_df():
    """Fixture to create an empty DataFrame for testing."""
    data = {"prediction": [], "hoofdagenda": []}
    return pd.DataFrame(data)


@pytest.fixture
def sample_df():
    """Fixture to create a sample DataFrame for testing."""
    data = {
        "prediction": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
        "hoofdagenda": ["A", "A", "B", "B", "C", "C", "D", "D", "E", "E"],
    }
    return pd.DataFrame(data)


class TestRCT:
    def test_quantile_binning(self, sample_df):
        """
        Test function for the quantile binning process and treatment group assignment.
        Raises:
            AssertionError: If there are issues with bin creation,
                            structure of the result DataFrame,
                            or treatment group assignment not alternating within groups.
        """
        original_columns = set(sample_df.columns)

        # Apply the function
        result = create_treatment_groups(sample_df)

        # Check if `score_bin` was created and other conditions met
        unique_bins = result["score_bin"].nunique()
        expected_bins = 10  # or any other expected number based on implementation
        assert (
            unique_bins == expected_bins
        ), f"Expected {expected_bins} unique bins, found {unique_bins}"
        assert set(result.columns) == original_columns.union(
            {"score_bin", "treatment_group"}
        ), "Result DataFrame does not have the correct structure"
        assert isinstance(
            result["score_bin"].dtype, pd.CategoricalDtype
        ), "score_bin column is not categorical"
        assert (
            result["treatment_group"].dtype == int
        ), "treatment_group column is not of type int"

    def test_alternate_assignment_within_groups(self, sample_df):
        """
        Test that within each hoofdagenda and score_bin group,
          treatment groups are alternately assigned.
        """
        result = create_treatment_groups(sample_df)

        # Check alternate assignment within each group
        for _, group in result.groupby(["hoofdagenda", "score_bin"], observed=True):
            treatment_groups = group["treatment_group"].values
            # Check if alternating
            assert np.all(
                np.diff(treatment_groups) != 0
            ), "Treatment groups are not alternately assigned within groups"
