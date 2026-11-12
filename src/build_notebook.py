"""Build notebooks/01_calibration_basics.ipynb (run: python -m src.build_notebook)."""
import nbformat as nbf

nb = nbf.v4.new_notebook()
M, C = nbf.v4.new_markdown_cell, nbf.v4.new_code_cell
nb.cells = [
M("# Find soil parameters from a noisy test"),
C("""import sys
sys.path.append('..')

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from src.duncan_chang import forward_model, rmse, calibrate
from src.teaching import show_guess, rank_guesses"""),
M("## 1. Model"),
C("""strain = np.linspace(0, 0.05, 200)
theta_demo = [60e3, 25, 10]          # Ei [kPa], phi [deg], c [kPa]

plt.plot(strain * 100, forward_model(theta_demo, strain), 'k')
plt.xlabel('Strain [%]'); plt.ylabel('Stress q [kPa]')
plt.show()"""),
M("## 2. Measurement"),
C("""data = pd.read_csv('../data/synthetic_test.csv')
strain, q_meas = data['strain'].values, data['q_measured'].values

plt.plot(strain * 100, q_meas, '.', color='gray')
plt.xlabel('Strain [%]'); plt.ylabel('Stress q [kPa]')
plt.show()"""),
M("## 3. Your guess"),
C("""Ei  = 80e3    # kPa
phi = 28      # deg
c   = 15      # kPa

show_guess([Ei, phi, c], strain, q_meas)"""),
M("## 3b. Guesses from the class"),
C("""class_guesses = {
    'Anna':  [60e3, 32, 10],
    'Ben':   [30e3, 27, 25],
    'Clara': [100e3, 35, 5],
}

rank_guesses(class_guesses, strain, q_meas)"""),
M("## 3c. Sliders (optional)"),
C("""from ipywidgets import interact, FloatSlider

@interact(Ei=FloatSlider(value=80e3, min=10e3, max=200e3, step=1e3),
          phi=FloatSlider(value=28, min=20, max=40, step=0.5),
          c=FloatSlider(value=15, min=0, max=30, step=0.5))
def try_it(Ei, phi, c):
    show_guess([Ei, phi, c], strain, q_meas)"""),
M("## 4. Let the computer search"),
C("""bounds = [(10e3, 200e3), (20, 40), (0, 30)]
start  = [100e3, 25, 10]

result = calibrate(strain, q_meas, start, bounds)
theta_fit = result.x"""),
M("## 5. Reveal: true values"),
C("""true = json.load(open('../data/true_parameters.json'))
theta_true = [true['Ei'], true['phi'], true['c']]

plt.plot(strain * 100, q_meas, '.', color='lightgray', label='measured')
plt.plot(strain * 100, forward_model(theta_fit, strain), 'r', label='fitted')
plt.xlabel('Strain [%]'); plt.ylabel('Stress q [kPa]'); plt.legend()
plt.savefig('../graphics/fit.png', dpi=200)
plt.show()

table = pd.DataFrame({'true': theta_true, 'fitted': theta_fit},
                     index=['Ei [kPa]', 'phi [deg]', 'c [kPa]']).round(1)
table"""),
M("## 6. Save"),
C("""table.to_csv('../results/parameters.csv')"""),
]
nb.metadata["kernelspec"] = {"display_name": "Python 3", "language": "python", "name": "python3"}
nbf.write(nb, "notebooks/01_calibration_basics.ipynb")
