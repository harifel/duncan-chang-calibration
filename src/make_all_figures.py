"""Rebuild the data and all figures with one command.

Run from the repo root:  python -m src.make_all_figures
Order: make_data, make_gifs, make_viz_examples, make_story_figures.
"""
from pathlib import Path

# The scripts read and write relative paths, so the working folder must be the repo root.
# (make_gifs also reads the data file when it is imported, so import it after make_data.)


def snapshot():
    """Modification time of every file in data/ and graphics/."""
    return {p: p.stat().st_mtime_ns for d in ("data", "graphics") for p in Path(d).rglob("*") if p.is_file()}


def step(name, func):
    before = snapshot()
    func()
    for p, t in sorted(snapshot().items()):
        if before.get(p) != t and "frames_" not in p.as_posix():
            print(f"  [{name}] wrote {p.as_posix()}")
    n_frames = sum(1 for p, t in snapshot().items() if before.get(p) != t and "frames_" in p.as_posix())
    if n_frames:
        print(f"  [{name}] wrote {n_frames} animation frames in graphics/frames_*/")


def main():
    from src import make_data
    step("make_data", make_data.main)
    from src import make_gifs
    step("make_gifs", make_gifs.main)
    from src import make_viz_examples
    step("make_viz_examples", make_viz_examples.main)
    from src import make_story_figures
    step("make_story_figures", make_story_figures.main)


if __name__ == "__main__":
    main()
