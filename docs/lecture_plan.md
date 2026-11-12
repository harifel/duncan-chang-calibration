# Lecture plan: Best practice Simulation II (90 min)

The session can be shortened. Frames marked [optional] in the slides can be cut.

| Min | Part |
|---|---|
| 30 | A. Warm-up questions |
| 5 | B. Roadmap: from results to paper |
| 25 | C. Live demo: Jupyter notebook |
| 10 | D. Repository and virtual environment |
| 15 | E. From results to paper: figures, structure, writing |
| 3 | F. Outlook: ML model for the Hardening Soil model |
| 2 | Take-home message |

## Part A. Warm-up questions (about 30 min)
Ask the group. Use a show of hands. Explain only where the answer is weak.

| # | Question | Target answer |
|---|---|---|
| 1 | Where do you search for papers? | Google Scholar, Scopus, Web of Science, TU Graz library, ResearchGate |
| 2 | How do you judge if a source is reliable? | Peer review, citations, authors, data available |
| 3 | How do you read a paper efficiently? | Title, abstract, figures, conclusion first. Then the details. |
| 4 | What is a reference manager? | Software that stores and formats citations (Zotero, Citavi, Mendeley) |
| 5 | What are the usual parts of a paper or thesis? | Introduction, background, methods, results, discussion, conclusion/outlook |
| 6 | In which part do you find the research question? | Introduction |
| 7 | How do you start writing? | Outline first. Figures and results early. Introduction and abstract last. |
| 8 | How do you build a paragraph? | Topic sentence, one idea, short summary if needed |
| 9 | How do you present a figure? | Describe what you see, one item at a time. Then conclude. |
| 10 | How do you write the method? | Every step in order, with all inputs, so others can repeat it |
| 11 | What is a reproducible result? | Another person gets the same result with your code and data |
| 12 | Who has used Python or Jupyter before? | Sets the level for Part C |

## Part B. Roadmap: from results to paper (about 5 min)
One slide with the agenda strip and the TikZ pipeline figure. Six stages:
results, figures, storyline, methods and results text, discussion and conclusion, introduction and abstract.

Message: in the demo we make stage 1. After the repository part we go through stages 2 to 6.

The same figure comes back at every change of part, so the group sees where we are:
the agenda strip (parts A to F) shows the current part. A blue frame marks the next stage.
Slides: start of D, start of E, inside E (after stage 3 and at the end), start of F [optional].

## Part C. Live demo: Jupyter notebook (about 25 min)
Use `notebooks/01_calibration_basics.ipynb`. Run one cell at a time.

| Step | Minutes | Message |
|---|---|---|
| 1 Model | 4 | A model maps parameters to a curve (example values) |
| 2 Measurement | 4 | Real tests are never perfect. The true values stay hidden. |
| 3 Guess by hand | 5 | Students guess. RMSE measures the misfit. |
| 4 Optimise | 5 | An algorithm searches for the smallest misfit |
| 5 Reveal and compare | 4 | Show the true values. Ei is found well. Phi and c are less certain. |
| 6 Save | 3 | Data and results go to files |

Discussion point: phi and c affect the curve in a similar way.
So the data cannot separate them well. This is the identifiability problem.

## Part D. Repo and virtual environment (about 10 min)
1. Show the folder structure (data, src, notebooks, results, graphics).
2. Create the virtual environment (Windows). Explain why: same package versions for everyone. Open the notebook in VS Code.
3. `git init`, `git add`, `git commit`, push to GitHub. Only the slides PDF is pushed (see `.gitignore`).
4. Show the benefit: backup, history, sharing, citation (Zenodo DOI).
5. Warn: never commit tokens.

## Part E. From results to paper (about 15 min)
We have the results from Part C. Now we make the paper.

| Slide | Content |
|---|---|
| Back to our results | Pipeline figure, stage 1 done |
| Stage 0 message | Communication goal: parameter identification, manually vs. automated |
| Stage 2 and 3: five figures | Input, judge, search, result, limit. Only figures already shown in the demo (`measured_only`, `rmse_residuals_blind`, last frame of the search animation, `fit`, `identifiability_phi_c`) |
| Visualization: bad and good | `graphics/viz_bad.png` and `graphics/viz_good.png` |
| Visualization: rules | Labels, units, colours, one message, script every figure |
| Where are we? | Pipeline figure, stages 1 to 3 done |
| Structure | Shape of a paper (TikZ figure) and what each part does |
| Write the text of a figure | Bad and good paragraph. Numbers are from the demo data. |
| A caption stands alone | Bad and good caption |
| Write the method | Bad and good method paragraph. Values are from the demo code. |
| Write the conclusion | Bad and good conclusion. It answers the question of the introduction. |
| Where are we? | Pipeline figure, all stages done |
| Practice: read a good paper [optional] | Five-minute reading task with our open-access paper |

Build all figures: `python -m src.make_all_figures`

Check before the lecture: the phi-c numbers on the "Write the text" slide.
For phi from 24 to 35 degrees, the best c falls from 43 to 0 kPa. The RMSE stays at 2.0 kPa.

## Part F. Outlook: our ML model for the Hardening Soil model (about 3 min)
One slide with two QR codes: the online tool and the repository.

- Tool: https://harifel.github.io/MLpFEM/
- Repo: https://github.com/harifel/MLpFEM
- Paper: https://doi.org/10.1007/s11440-026-02951-5 (open access, CC BY 4.0)

Message: a research result can become a tool that anyone opens in a browser.
Test the page on the lecture room network. Keep a screenshot as a backup.

## Backup slides (hidden at the end of the PDF)
Optimization: search for the minimum. Discussion questions.
Use them only if students ask.

## Take-home message (2 min)
Coding is not a burden anymore.
With a template and a clear structure, you start in minutes.
Plan the paper from the results: figures first, introduction last.
Point to the repo as a template.

## Bad and good slides: split or together
The slides with "Bad" and "Good" boxes show the bad example first. The good one appears with the next click.
One switch in the preamble of `slides/lecture_simulation_II.tex` controls all of them:
`\badgoodsplittrue` (split, default) or `\badgoodsplitfalse` (together on one page).
One slide only: `\IBGbadgood[both]{bad}{good}` or `\IBGbadgood[split]{bad}{good}`.

## Build the slides
Run `latexmk -pdf lecture_simulation_II.tex` inside `slides/`.
The `.latexmkrc` there finds the shared IBG Beamer template in `../../00_templates/BeamerTemplate`.
Compile the PDF before the first commit. The repository tracks only this PDF.
Make the figures first: `python -m src.make_data`, `python -m src.make_gifs`, `python -m src.make_viz_examples`.
