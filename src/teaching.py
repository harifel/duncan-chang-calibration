"""Helpers for the live demo: students type guesses, we show the RMSE."""
import matplotlib.pyplot as plt
import pandas as pd

from src.duncan_chang import forward_model, rmse

LABELS = ["Ei [kPa]", "phi [deg]", "c [kPa]"]


def show_guess(theta, strain, q_meas, name="Your guess"):
    """Plot one guess with the differences to the measurement. Print the RMSE."""
    q_mod = forward_model(theta, strain)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.vlines(strain[::4] * 100, q_mod[::4], q_meas[::4], color="#e4002b", lw=1, alpha=0.8)
    ax.plot(strain * 100, q_meas, ".", color="lightgray", label="measured")
    ax.plot(strain * 100, q_mod, "k", lw=2, label=name)
    ax.set_xlabel("Strain [%]")
    ax.set_ylabel("Stress q [kPa]")
    ax.set_title(f"{name}: RMSE = {rmse(theta, strain, q_meas):.1f} kPa", loc="left")
    ax.legend(loc="lower right")
    plt.show()
    return rmse(theta, strain, q_meas)


def rank_guesses(guesses, strain, q_meas):
    """Plot all guesses together. Return a table, best (smallest RMSE) first."""
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(strain * 100, q_meas, ".", color="lightgray", label="measured")
    rows = []
    for name, theta in guesses.items():
        ax.plot(strain * 100, forward_model(theta, strain), label=name)
        rows.append([name, *theta, rmse(theta, strain, q_meas)])
    ax.set_xlabel("Strain [%]")
    ax.set_ylabel("Stress q [kPa]")
    ax.legend(loc="lower right", fontsize=8)
    plt.show()
    table = pd.DataFrame(rows, columns=["Name", *LABELS, "RMSE [kPa]"])
    return table.sort_values("RMSE [kPa]").reset_index(drop=True).round(1)
