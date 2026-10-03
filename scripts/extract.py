#!/usr/bin/env python3
"""
extract.py -- reconstruct table rows from an offer document page.

Why this exists rather than `pdftotext -layout`:

    pdftotext lays text out by inserting spaces to approximate the original
    column positions. On a three or five year financial table that has been
    typeset with tight columns, the approximation collapses and figures land
    under the wrong heading. The failure is silent. You get a plausible
    looking table with the columns interleaved, and if you trust it you will
    report an inconsistency that does not exist.

    This script instead clusters words by their y coordinate into rows, sorts
    each row by x, and inserts an explicit separator wherever the horizontal
    gap between two words exceeds a threshold. The separators show you where
    the column boundaries actually are, so you can see when a row is short a
    cell rather than guessing.

Usage:
    python extract.py <document.pdf> <from_page> <to_page> [--offset N]
                      [--tol 2.2] [--gap 6] [--sep "  |  "]

    from_page / to_page are pdf pages by default. With --offset N they are
    read as printed pages and converted (pdf = printed + N).

Read the output as: each "  |  " marks a column boundary the typesetter left.
A row with fewer separators than its neighbours is missing a value, which is
usually where a footing error hides.
"""

import sys
import argparse

import pdfplumber


def rows(page, tol=2.2, gap=6.0, sep="  |  "):
    """Group a page's words into visual rows and mark column gaps.

    tol  vertical tolerance in points for treating two words as the same row.
         2.2 suits the 8 to 10 point type used in offer document tables. Raise
         it if a single logical row is being split; lower it if two adjacent
         rows are being merged.

    gap  horizontal gap in points that counts as a column boundary. 6 is about
         one and a half space widths at 9 point, which separates columns
         without splitting ordinary word spacing. Raise it for loosely set
         tables, lower it for very tight ones.
    """
    words = page.extract_words(use_text_flow=False, keep_blank_chars=False)
    lines = []
    for w in sorted(words, key=lambda w: (round(w["top"], 1), w["x0"])):
        for line in lines:
            if abs(line["top"] - w["top"]) <= tol:
                line["words"].append(w)
                break
        else:
            lines.append({"top": w["top"], "words": [w]})

    out = []
    for line in sorted(lines, key=lambda l: l["top"]):
        parts = []
        prev_x1 = None
        for w in sorted(line["words"], key=lambda w: w["x0"]):
            if prev_x1 is not None and w["x0"] - prev_x1 > gap:
                parts.append(sep)
            parts.append(w["text"])
            prev_x1 = w["x1"]
        out.append("".join(parts))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("start", type=int)
    ap.add_argument("end", type=int)
    ap.add_argument("--offset", type=int, default=0,
                    help="if set, start/end are printed pages; pdf = printed + offset")
    ap.add_argument("--tol", type=float, default=2.2, help="row grouping tolerance in points")
    ap.add_argument("--gap", type=float, default=6.0, help="column gap threshold in points")
    ap.add_argument("--sep", default="  |  ", help="column separator to emit")
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    lo = a.start + a.offset
    hi = a.end + a.offset

    with pdfplumber.open(a.pdf) as pdf:
        n = len(pdf.pages)
        for i in range(lo, hi + 1):
            if not 1 <= i <= n:
                print(f"\n===== PDF PAGE {i} out of range (1..{n}) =====")
                continue
            printed = i - a.offset
            print(f"\n===== PDF PAGE {i}   (printed {printed}) =====")
            page = pdf.pages[i - 1]
            emitted = rows(page, tol=a.tol, gap=a.gap, sep=a.sep)
            # A page whose only extractable text is its own page number is a
            # scan or a page of vector outlines, not an empty page. Say so,
            # because the difference decides whether a missing note is
            # "missing" or merely "not verifiable".
            if sum(len(r.strip()) for r in emitted) < 60:
                print(f"[no readable text on this page ({sum(len(r.strip()) for r in emitted)} "
                      f"characters) -- render it with render.py and read it visually]")
                for r in emitted:
                    if r.strip():
                        print(f"  stray text: {r.strip()!r}")
                continue
            for r in emitted:
                print(r)


if __name__ == "__main__":
    main()
