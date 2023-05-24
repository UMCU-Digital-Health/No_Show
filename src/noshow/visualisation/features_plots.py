from typing import Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.axes import Axes


def feature_barplot(
    df: pd.DataFrame,
    feature_col: str,
    figsize: Tuple[int, int] = (10, 4),
    feature_name: Optional[str] = None,
    perc_feature: bool = False,
    round_decimals: int = 0,
) -> Axes:
    """Create a feature barplot

    This will plot the relative effect of a feature
    on the no-show percentage

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing the feature and no_show column
    feature_col : str
        Name of the feature column
    figsize : Tuple[int, int], optional
        Size of the figure, by default (10, 4)
    feature_name : Optional[str], optional
        Feature name for the title and x axis, if None use the
        feature column, by default None
    perc_feature : bool, optional
        Is the feature a percentage, will also multiply the x-axis with 10,
        to keep integer x-values, by default False
    round_decimals : int, optional
        How many decimals to round the percentage to, by default 0

    Returns
    -------
    Axes
        matplotlib Axes object
    """
    feature_vs_no_show = df.copy()
    if perc_feature:
        feature_vs_no_show[feature_col] = feature_vs_no_show[feature_col].round(
            round_decimals
        )
    feature_name = feature_col if feature_name is None else feature_name
    feature_vs_no_show = (
        feature_vs_no_show.groupby(feature_col)["no_show"]
        .value_counts(normalize=True, dropna=False)
        .unstack(level="no_show")
    )
    x_values = feature_vs_no_show.index
    if perc_feature:
        x_values = x_values * 10

    _, ax = plt.subplots(figsize=figsize)
    ax.bar(x_values, feature_vs_no_show["no_show"], label="No show")
    ax.bar(
        x_values,
        feature_vs_no_show["show"],
        bottom=feature_vs_no_show["no_show"],
        label="Show",
    )
    ax.set_xticks(x_values)
    ax.set_xticklabels(feature_vs_no_show.index)
    ax.set_title(f"Relative amount of no-shows given {feature_name}")
    ax.set_xlabel(feature_name)
    ax.legend()
    return ax


def feature_scatter(
    df: pd.DataFrame,
    feature_col: str,
    figsize: Tuple[int, int] = (10, 5),
    feature_name: Optional[str] = None,
    round_feature: bool = False,
    round_decimals: int = 0,
) -> Axes:
    """Create a feature scatter plot

    Parameters
    ----------
    df : pd.DataFrame
        Dataframe containing the feature and no_show column
    feature_col : str
        Name of the feature column
    figsize : Tuple[int, int], optional
        Size of the figure, by default (10, 4)
    feature_name : Optional[str], optional
        Feature name for the title and x axis, if None use the
        feature column, by default None
    round_feature : bool, optional
        If the feature should be rounded, by default False
    round_decimals : int, optional
        How many decimals to round the feature to, by default 0

    Returns
    -------
    Axes
        matplotlib Axes object
    """
    feature_name = feature_col if feature_name is None else feature_name

    feature_vs_no_show = df.copy()
    if round_feature:
        feature_vs_no_show[feature_col] = feature_vs_no_show[feature_col].round(
            round_decimals
        )

    feature_vs_no_show = (
        feature_vs_no_show.groupby(feature_col)["no_show"]
        .value_counts(normalize=True)
        .unstack(level="no_show")
    )

    _, ax = plt.subplots(figsize=figsize)

    ax.scatter(feature_vs_no_show.index, feature_vs_no_show["no_show"])
    ax.set_title(f"{feature_name} vs no show")
    ax.set_xlabel(feature_name)
    ax.set_ylabel("Relative no-show")
    return ax
