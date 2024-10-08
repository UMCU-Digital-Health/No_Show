from unittest.mock import Mock

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
        "pseudo_id": [1, 2, 3, 1, 3, 2, 4, 1, 2, 4],
        "clinic": ["C1", "C1", "C2", "C2", "C3", "C3", "C5", "C5", "C5", "C5"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_bins():
    """Fixture to create a sample bin dictionary for testing."""
    data = {
        "A": {0.0: 0.003, 0.25: 0.03, 0.5: 0.053, 0.75: 0.077, 1.0: 0.69},
        "B": {0.0: 0.003, 0.25: 0.03, 0.5: 0.053, 0.75: 0.077, 1.0: 0.69},
        "C": {0.0: 0.003, 0.25: 0.02, 0.5: 0.053, 0.75: 0.067, 1.0: 0.69},
        "D": {0.0: 0.003, 0.25: 0.03, 0.5: 0.053, 0.75: 0.077, 1.0: 0.69},
        "E": {0.0: 0.013, 0.25: 0.03, 0.5: 0.083, 0.75: 0.097, 1.0: 0.69},
    }
    return data


@pytest.fixture
def no_patients():
    """Fixture to create an empty DataFrame for testing."""
    data = []
    return data


@pytest.fixture
def some_patients():
    """Fixture to create a sample DataFrame for testing."""
    data = [
        {"id": 1, "treatment_group": 1},
        {"id": 2, "treatment_group": 0},
    ]
    return data


def test_quantile_binning(sample_df, no_patients, sample_bins):
    """
    Test function for the quantile binning process and treatment group assignment.
    Raises:
        AssertionError: If there are issues with bin creation,
                        structure of the result DataFrame,
                        or treatment group assignment not alternating within groups.
    """
    original_columns = set(sample_df.columns)

    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = no_patients

    # Apply the function
    result = create_treatment_groups(sample_df, session, sample_bins)

    assert set(result.columns) == original_columns.union(
        {"treatment_group"}
    ), "Result DataFrame does not have the correct structure"
    assert (
        result["treatment_group"].dtype == int
    ), "treatment_group column is not of type int"
    # check if every pseudo_id has one unique treatment group
    assert (
        result.groupby("pseudo_id")["treatment_group"].nunique().max() == 1
    ), "Some pseudo_ids have multiple treatment groups"


def test_empty_df(empty_df, no_patients, sample_bins):
    """
    Test function for handling an empty DataFrame.
    """
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = no_patients
    # if value error is raised, the function is working correctly
    with pytest.raises(ValueError):
        result = create_treatment_groups(empty_df, session, sample_bins)
        assert result


def test_create_treatment_groups_no_patients(sample_df, no_patients, sample_bins):
    # Test case for no patients in the database
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = no_patients
    result = create_treatment_groups(sample_df, session, sample_bins)
    assert (result["treatment_group"] == [1, 0, 0, 0, 1, 0, 0, 0, 0, 1]).all()


def test_create_treatment_groups_with_patients(sample_df, some_patients, sample_bins):
    # Test case for patients in the database
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = some_patients
    result = create_treatment_groups(sample_df, session, sample_bins)

    assert (result["treatment_group"] == [0, 1, 1, 0, 0, 0, 1, 1, 1, 0]).all()


def test_create_treatment_group_empty_rct_agendas(
    sample_df, some_patients, sample_bins
):
    """Test case for empty rct_agendas, should add all patients to group 2"""
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = some_patients
    result = create_treatment_groups(sample_df, session, sample_bins, rct_agendas=[])

    result = result["treatment_group"]
    assert (result == 2).all()


def test_create_treatment_group_some_rct_agendas(sample_df, some_patients, sample_bins):
    """Test case for some rct_agendas, should add patients of A and B to RCT,
    meaning group 0 or 1 and patients of other agendas to group 2"""
    session = Mock()
    session.query.return_value.filter.return_value.all.return_value = some_patients
    result = create_treatment_groups(
        sample_df, session, sample_bins, rct_agendas=["C1", "C5"]
    )

    assert (
        result.loc[result["clinic"].isin(["C1", "C5"]), "treatment_group"] < 2
    ).all()
    assert (
        result.loc[~result["clinic"].isin(["C1", "C5"]), "treatment_group"] == 2
    ).all()
