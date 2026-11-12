"""Make the story figure that is not made by another script: graphics/fit.png.

Run from the repo root:  python -m src.make_story_figures
The other story figures come from src/make_gifs.py:
  graphics/measured_only.png, graphics/identifiability_phi_c.png (and model_demo.png).
Colours, size and dpi are the same as in src/make_viz_examples.py.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.duncan_chang import forward_model
from src.make_viz_examples import (DPI, FIG_SIZE, GREY, OUT, TUG_RED, load)


def fit_figure(strain, q_meas, theta):
    """Measurement and fitted curve."""
    fig, ax = plt.subplots(figsize=FIG_SIZE)
    ax.plot(strain * 100, q_meas, ".", color=GREY, ms=5, label="Measurement")
    ax.plot(strain * 100, forward_model(theta, strain), color=TUG_RED, lw=2, label="Fitted model")
    ax.set_xlabel("Axial strain $\\varepsilon_a$ [%]")
    ax.set_ylabel("Deviator stress $q$ [kPa]")
    ax.legend(loc="lower right", frameon=False)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig


def main():
    strain, q_meas, theta = load()
    OUT.mkdir(exist_ok=True)
    fig = fit_figure(strain, q_meas, theta)
    fig.savefig(OUT / "fit.png", dpi=DPI)
    plt.close(fig)
    print("Wrote graphics/fit.png")


if __name__ == "__main__":
    main()
