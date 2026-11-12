"""Make the figures for the visualization part of the lecture.

Run from the repo root:  python -m src.make_viz_examples
Output:
  graphics/viz_bad.png            same data, common mistakes
  graphics/viz_good.png           same data, readable and honest
  graphics/viz_rmse.png           one manual guess, red misfit lines, RMSE in the figure
  graphics/optimizer_history.png  (a) start, middle and end curve, (b) best RMSE per improvement step
Input: data/synthetic_test.csv, results/parameters.csv (if missing, the fit is computed).
The numbers are fixed (no random part): the same run always gives the same figures.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import least_squares

from src.duncan_chang import forward_model, rmse, calibrate

# ---------------------------------------------------------------- settings
TUG_RED = "#e4002b"
GREY = "#8c8c8c"
INK = "#222222"
FIG_SIZE = (6, 4)            # inches, all figures of this script
FIG_SIZE_WIDE = (10, 4)      # two panels side by side
DPI = 200
FONT_SIZE = 12
MIN_GAIN = 1e-3             # an evaluation counts as a step if RMSE drops by 0.1 %
GUESS = [35e3, 26.0, 12.0]   # manual guess: Ei [kPa], phi [deg], c [kPa]
START = [100e3, 25.0, 10.0]  # start values of the optimizer
BOUNDS = [(10e3, 200e3), (20.0, 40.0), (0.0, 30.0)]
OUT = Path("graphics")
DATA_FILE = Path("data/synthetic_test.csv")
PARAM_FILE = Path("results/parameters.csv")

plt.rcParams.update({"font.size": FONT_SIZE})


def load():
    """Strain, measured stress and fitted parameters."""
    data = pd.read_csv(DATA_FILE)
    strain, q_meas = data["strain"].to_numpy(), data["q_measured"].to_numpy()
    if PARAM_FILE.exists():
        fitted = pd.read_csv(PARAM_FILE, index_col=0)["fitted"].to_numpy()
    else:                                   # notebook was not run yet
        fitted = calibrate(strain, q_meas, START, BOUNDS).x
    return strain, q_meas, fitted


def bad_figure(strain, q_meas, theta):
    """Typical mistakes: no labels, no units, rainbow colours, clutter."""
    q_fit = forward_model(theta, strain)
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.scatter(strain, q_meas, c=strain, cmap="jet", s=60)
    ax.plot(strain, q_fit, "y-", lw=1)
    ax.set_ylim(150, 400)                     # cut axis hides the start of the test
    ax.tick_params(labelsize=6)
    ax.grid(True, lw=2, color="lightblue")
    ax.legend(["data", "fit"], loc="center", fontsize=14)
    ax.set_title("Figure 1")
    fig.tight_layout()
    return fig


def good_figure(strain, q_meas, theta):
    """Labels with units, one message, direct comparison, residuals shown."""
    q_fit = forward_model(theta, strain)
    fig, (ax, ax_res) = plt.subplots(
        2, 1, figsize=FIG_SIZE, sharex=True, height_ratios=[3, 1],
        gridspec_kw={"hspace": 0.08})
    ax.plot(strain * 100, q_meas, ".", color=GREY, ms=4, label="Measurement")
    ax.plot(strain * 100, q_fit, color=TUG_RED, lw=2, label="Fitted model")
    ax.set_ylabel("Deviator stress $q$ [kPa]")
    ax.legend(loc="lower right", frameon=False)
    ax.text(0.03, 0.95, f"RMSE = {rmse(theta, strain, q_meas):.1f} kPa",
            transform=ax.transAxes, va="top")
    ax_res.axhline(0, color="black", lw=0.8)
    ax_res.plot(strain * 100, q_meas - q_fit, ".", color=GREY, ms=3)
    ax_res.set_xlabel("Axial strain $\\varepsilon_a$ [%]")
    ax_res.set_ylabel("Misfit [kPa]")
    ax_res.set_ylim(-7, 16)             # free space above the points for the note
    ax_res.text(0.97, 0.95, "Misfit = measurement $-$ fitted model", transform=ax_res.transAxes,
                ha="right", va="top", fontsize=FONT_SIZE - 3)
    for a in (ax, ax_res):
        a.spines[["top", "right"]].set_visible(False)
    return fig


def rmse_figure(strain, q_meas, guess):
    """One manual guess. Red lines show the misfit. The RMSE is in the figure."""
    q_mod = forward_model(guess, strain)
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.vlines(strain[::4] * 100, q_mod[::4], q_meas[::4], color=TUG_RED, lw=1.2,
              alpha=0.8, label="Misfit")
    ax.plot(strain * 100, q_meas, ".", color=GREY, ms=4, label="Measurement")
    ax.plot(strain * 100, q_mod, color=INK, lw=2, label="Manual guess")
    ax.set_xlabel("Axial strain $\\varepsilon_a$ [%]")
    ax.set_ylabel("Deviator stress $q$ [kPa]")
    ax.legend(loc="lower right", frameon=False)
    ax.text(0.03, 0.95, f"RMSE = {rmse(guess, strain, q_meas):.0f} kPa",
            transform=ax.transAxes, va="top")
    ax.spines[["top", "right"]].set_visible(False)
    return fig


def run_optimizer(strain, q_meas):
    """Run the search from START. Return the best-so-far RMSE at every improvement."""
    tried = []

    def residuals(theta):
        tried.append(np.array(theta))
        return forward_model(theta, strain) - q_meas

    lo, hi = zip(*BOUNDS)
    result = least_squares(residuals, START, bounds=(lo, hi),
                           x_scale=np.array(hi) - np.array(lo))
    best, steps = np.inf, []
    for theta in tried:                      # keep only the evaluations that improved
        value = rmse(theta, strain, q_meas)
        if value < best * (1 - MIN_GAIN):
            best = value
            steps.append((theta, value))
    return steps, result.x


def history_figure(strain, q_meas):
    """(a) start, middle and end curve. (b) best RMSE per improvement step."""
    steps, theta_end = run_optimizer(strain, q_meas)
    values = [v for _, v in steps]
    mid = len(steps) // 2
    fig, (ax, axh) = plt.subplots(1, 2, figsize=FIG_SIZE_WIDE,
                                  gridspec_kw={"width_ratios": [1.3, 1]})
    ax.plot(strain * 100, q_meas, ".", color=GREY, ms=4, label="Measurement")
    for theta, style, label in [
            (steps[0][0], dict(color=GREY, ls=":", lw=2), f"Start (RMSE {values[0]:.0f} kPa)"),
            (steps[mid][0], dict(color=INK, ls="--", lw=2), f"Middle (RMSE {values[mid]:.0f} kPa)"),
            (theta_end, dict(color=TUG_RED, lw=2), f"End (RMSE {rmse(theta_end, strain, q_meas):.1f} kPa)")]:
        ax.plot(strain * 100, forward_model(theta, strain), label=label, **style)
    ax.set_xlabel("Axial strain $\\varepsilon_a$ [%]")
    ax.set_ylabel("Deviator stress $q$ [kPa]")
    ax.set_title("(a) Curves", loc="left")
    ax.legend(loc="lower right", frameon=False, fontsize=FONT_SIZE - 2)
    axh.plot(range(len(values)), values, "o-", color=TUG_RED, ms=4)
    axh.set_yscale("log")
    axh.set_xlabel("Improvement step")
    axh.set_ylabel("Best RMSE [kPa]")
    axh.set_title("(b) Search", loc="left")
    for a in (ax, axh):
        a.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def main():
    strain, q_meas, theta = load()
    OUT.mkdir(exist_ok=True)
    figures = [
        ("viz_bad.png", bad_figure(strain, q_meas, theta), {}),
        ("viz_good.png", good_figure(strain, q_meas, theta), {"bbox_inches": "tight"}),
        ("viz_rmse.png", rmse_figure(strain, q_meas, GUESS), {"bbox_inches": "tight"}),
        ("optimizer_history.png", history_figure(strain, q_meas), {"bbox_inches": "tight"}),
    ]
    for name, fig, options in figures:
        fig.savefig(OUT / name, dpi=DPI, **options)
        plt.close(fig)
        print(f"Wrote graphics/{name}")


if __name__ == "__main__":
    main()
