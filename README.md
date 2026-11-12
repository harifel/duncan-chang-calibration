# Duncan-Chang calibration (teaching example)

Find soil parameters from a noisy triaxial test.
The model is the Duncan-Chang hyperbolic stress-strain law.

## Folder structure

| Folder | Content |
|---|---|
| `data/` | Input data (synthetic test curve) |
| `src/` | Python code: model, noise, calibration |
| `notebooks/` | Step-by-step Jupyter notebook |
| `results/` | Output tables |
| `graphics/` | Output figures |
| `tests/` | Small automatic checks |
| `docs/` | Lecture notes |
| `slides/` | Lecture slides (LaTeX) |

## Setup

```bat
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Open `notebooks/01_calibration_basics.ipynb` in VS Code. Choose the kernel from `.venv`. Run all cells.
(PowerShell can block the activation. Use the Command Prompt then.)
In step 3, students type their own guesses. Sliders are optional (`ipywidgets`).

## Make the figures

All figures of the slides come from scripts. Nothing is drawn by hand.
One command makes the data and all figures:

```bat
python -m src.make_all_figures
```

It prints one line per file written. The same run always gives the same numbers.

| Script | Output in `graphics/` |
|---|---|
| `src/make_data.py` | `data/synthetic_test.csv`, `data/true_parameters.json` |
| `src/make_gifs.py` | `model_demo.png`, `measured_only.png`, `identifiability_phi_c.png`, `identifiability_two_tests.png`, `identifiability_more_tests.png`, `map_sections.png`, `rmse_residuals*.gif/png`, `optimizer_search.gif`, frames in `frames_*/` |
| `src/make_viz_examples.py` | `viz_bad.png`, `viz_good.png`, `viz_rmse.png`, `optimizer_history.png` |
| `src/make_story_figures.py` | `fit.png` |

Other commands:

| Command | Output |
|---|---|
| `python -m src.make_qr <repo-link>` | `graphics/qr_course_repo.png` |
| `python -m src.build_notebook` | `notebooks/01_calibration_basics.ipynb` |
| `cd slides && latexmk -pdf lecture_simulation_II.tex` | Slides (PDF) |

Screenshots of the MLpFEM tool and the QR codes are in `graphics/external/`.
They come from https://harifel.github.io/MLpFEM/ and the open-access paper (CC BY 4.0).

Only the slides PDF is in this repository. The LaTeX source stays in the teaching folder, because it uses the shared IBG template.
The slides play the animations with the LaTeX package `animate` (Adobe Reader).
The GIF files in `graphics/` work in PowerPoint and Keynote.

## Use as a template

On GitHub: press "Use this template". Then rename the project and replace the model in `src/`.

## Test

```bash
pip install pytest
pytest
```

## Secrets

Never commit tokens or passwords. Keep them in environment variables.
