import pandas as pd
from matplotlib.axes import Axes

from noshow.visualisation.features_plots import feature_barplot, feature_scatter

fake_feature_data = pd.DataFrame(
    {"no_show": ["show", "show", "no_show", "show"], "feature": [1, 1, 2, 2]}
)


def test_feature_barplot():
    ax = feature_barplot(fake_feature_data, "feature")
    assert type(ax) is Axes


def test_feature_scatterplot():
    ax = feature_scatter(fake_feature_data, "feature")
    assert type(ax) is Axes
