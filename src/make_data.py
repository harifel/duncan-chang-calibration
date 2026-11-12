"""Create the synthetic measurement for the course.

Run from the repo root:  python -m src.make_data
Output:
  data/synthetic_test.csv       the "measurement" (students see this)
  data/true_parameters.json     the true values (shown only at the end)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.duncan_chang import forward_model, add_noise

THETA_TRUE = {"Ei": 50e3, "phi": 30.0, "c": 20.0}
STRAIN = np.linspace(0, 0.05, 200)


def main():
    q_true = forward_model(list(THETA_TRUE.values()), STRAIN)
    q_meas = add_noise(q_true, noise_factor=0.01, seed=42)
    Path("data").mkdir(exist_ok=True)
    pd.DataFrame({"strain": STRAIN, "q_measured": q_meas}).to_csv(
        "data/synthetic_test.csv", index=False, lineterminator=chr(10))  # same bytes on every system
    Path("data/true_parameters.json").write_text(json.dumps(THETA_TRUE, indent=2))
    print("Wrote data/synthetic_test.csv and data/true_parameters.json")


if __name__ == "__main__":
    main()
