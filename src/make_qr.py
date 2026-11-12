"""Make the QR code for the course repository.

Run from the repo root:
    python -m src.make_qr https://github.com/<user>/<repo>
Output: graphics/qr_course_repo.png
Other codes (for example a paper): give the file name as second argument
    python -m src.make_qr https://doi.org/<doi> graphics/qr_paper.png
Also update \\repourl in slides/lecture_simulation_II.tex to the same link.
"""
import sys
from pathlib import Path

import qrcode

DEFAULT_URL = "https://github.com/harifel/duncan-chang-calibration"   # placeholder


def main(url=DEFAULT_URL, outfile="graphics/qr_course_repo.png"):
    img = qrcode.make(url, box_size=12, border=2)
    out = Path(outfile)
    out.parent.mkdir(exist_ok=True)
    img.save(out)
    print(f"QR code for {url} -> {out}")


if __name__ == "__main__":
    main(*sys.argv[1:3])
