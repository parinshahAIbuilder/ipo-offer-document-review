#!/usr/bin/env python3
"""
render.py -- turn pages that carry no extractable text into images you can read.

When probe.py reports a block of non machine readable pages, that block is
almost always the restated financial information, which is the part of the
document you most need. Two mechanisms produce it:

  * the pages are scans, so the figures exist only as pixels
  * the text has been converted to vector outlines at generation time, so the
    figures are drawn as shapes and no character survives

Either way the fix is the same: render to PNG and read the image.

A note on the toolchain. `pdftoppm` and `pdfimages` are frequently absent on
Windows installs, and reaching for them wastes a round trip. PyMuPDF is a
Python dependency you already have if pdfplumber works, and it renders at
arbitrary DPI without an external binary. Use it.

On DPI. 150 is enough to read headings and confirm structure. Figures in a
financial table need 165 to 200. Go to 300 with --crop when you are deciding
whether a digit is an 8 or a 0, which matters more than it sounds: a scan
artifact that turns 80.50 into 00.50 will otherwise be reported as a
misstatement that is not there.

Usage:
    python render.py <document.pdf> <from_page> <to_page> --out DIR
                     [--offset N] [--dpi 170]
                     [--crop x0,y0,x1,y1]     # fractions of the page, 0 to 1

Examples:
    # whole pages at reading quality
    python render.py rhp.pdf 337 341 --out ./out --dpi 170

    # zoom the lower right quadrant of one page to settle a digit
    python render.py rhp.pdf 340 340 --out ./out --dpi 300 --crop 0.5,0.5,1,1
"""

import os
import sys
import argparse

try:
    import pymupdf
except ImportError:
    import fitz as pymupdf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int)
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--offset", type=int, default=0,
                    help="if set, start/end are printed pages; pdf = printed + offset")
    ap.add_argument("--dpi", type=int, default=170)
    ap.add_argument("--crop", default=None,
                    help="x0,y0,x1,y1 as fractions of page size, e.g. 0.5,0.5,1,1")
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    os.makedirs(a.out, exist_ok=True)

    clip_frac = None
    if a.crop:
        try:
            clip_frac = [float(v) for v in a.crop.split(",")]
            assert len(clip_frac) == 4
        except Exception:
            sys.exit("--crop expects four comma separated fractions, e.g. 0,0,1,0.5")

    doc = pymupdf.open(a.pdf)
    lo = a.start + a.offset
    hi = a.end + a.offset

    for i in range(lo, hi + 1):
        if not 1 <= i <= doc.page_count:
            print(f"pdf page {i} out of range (1..{doc.page_count})")
            continue
        page = doc[i - 1]
        clip = None
        if clip_frac:
            r = page.rect
            clip = pymupdf.Rect(
                r.x0 + clip_frac[0] * r.width,
                r.y0 + clip_frac[1] * r.height,
                r.x0 + clip_frac[2] * r.width,
                r.y0 + clip_frac[3] * r.height,
            )
        pix = page.get_pixmap(dpi=a.dpi, clip=clip)
        name = f"p{i}.png" if not a.crop else f"p{i}_crop.png"
        path = os.path.join(a.out, name)
        pix.save(path)
        print(f"pdf {i} (printed {i - a.offset})  ->  {path}  "
              f"[{pix.width}x{pix.height} at {a.dpi} dpi]")

    doc.close()
    print("\nNow read these images. Do not infer a figure you cannot see clearly; "
          "re-render the region at 300 dpi with --crop instead.")


if __name__ == "__main__":
    main()
