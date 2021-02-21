from typing import Union

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

from mlmatrics.utils import add_identity


def std_calibration(y_true: list, y_pred: list, y_std: Union[list, dict]) -> None:
    """Plot the calibration of one (passed as list) or multiple (passed as dict)
    sets of uncertainty estimates for a single pair of ground truth targets
    `y_true` and model predictions `y_pred`. Overconfidence is visualized as shaded
    areas below the parity line, underconfidence (oversized uncertainties) as
    shaded areas above the parity line.

    Inspired by https://github.com/uncertainty-toolbox/uncertainty-toolbox#visualizations.

    Args:
        y_true (list): ground truth targets
        y_pred (list): model predictions
        y_std (list | dict): model uncertainties
    """
    if type(y_std) != dict:
        y_std = {"std": y_std}

    res = np.abs(y_pred - y_true)
    resolution = 100

    lines = []  # collect plotted lines to show second legend with miscalibration areas
    for key, std in y_std.items():

        z_scored = (res / std).reshape(-1, 1)

        exp_proportions = np.linspace(0, 1, resolution)
        gaussian_upper_bound = norm.ppf(0.5 + exp_proportions / 2)
        obs_proportions = np.mean(z_scored <= gaussian_upper_bound, axis=0)

        [line] = plt.plot(
            exp_proportions, obs_proportions, linewidth=2, alpha=0.8, label=key
        )
        plt.fill_between(
            exp_proportions, y1=obs_proportions, y2=exp_proportions, alpha=0.2
        )
        miscal_area = np.trapz(obs_proportions, dx=1 / resolution) - 0.5
        lines.append([line, miscal_area])

    add_identity(label="ideal")

    plt.xlim(0, 1)
    plt.ylim(0, 1)

    legend1 = plt.legend(loc="upper left")
    # Multiple legends on the same axes:
    # https://matplotlib.org/3.3.3/tutorials/intermediate/legend_guide.html#multiple-legends-on-the-same-axes
    plt.gca().add_artist(legend1)

    lines, areas = zip(*lines)

    if len(lines) > 1:
        legend2 = plt.legend(
            lines,
            [f"{area:.2f}" for area in areas],
            title="Miscalibration areas",
            loc="lower right",
            ncol=2,
        )
        legend2._legend_box.align = "left"  # https://stackoverflow.com/a/44620643
    else:
        plt.legend(lines, [f"Miscalibration area: {areas[0]:.2f}"], loc="lower right")
