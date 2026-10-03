#!/usr/bin/env python3
"""
probe.py -- first pass over an Indian IPO offer document (DRHP / RHP).

Answers the three questions every review has to settle before any analysis can
start:

  1. What is the offset between pdf page numbers and printed page numbers?
     Offer documents are cited by printed page, and every cross reference
     inside the document ("see Objects of the Issue on page 131") is a printed
     page. Getting the offset wrong makes every citation in the final report
     wrong, which is the fastest way to lose an issuer's confidence.

  2. Which pages are not machine readable?
     Financial statement sections arrive either as scans or as text converted
     to vector outlines. Those pages cannot be text searched, and that changes
     what you are entitled to conclude: a note you cannot search is "not
     verifiable", never "missing".

  3. Where do the standard sections start?
     So you can go straight to Objects, Basis for the Issue Price, the restated
     financials and the rest without paging through the document.

Usage:
    python probe.py <document.pdf>
    python probe.py <document.pdf> --json     # full detail, per page
"""

import sys
import re
import json
import argparse
from collections import Counter

try:
    import pymupdf
except ImportError:  # older wheels expose the module as fitz
    import fitz as pymupdf


# Headings as they appear at the top of the page that opens each section.
#
# Two conventions have to be tolerated. Many issuers prefix the heading with a
# section number, as in "SECTION II - RISK FACTORS", and the separator is
# variously a colon, a hyphen, an en dash or an em dash. Rather than enumerate
# dash codepoints, which is easy to get wrong and hard to read, the prefix is
# matched as "SECTION <roman> <up to four of anything>".
SEC = r"(?:SECTION\s+[IVXL]+.{0,4})?"

SECTION_PATTERNS = [
    ("Definitions and Abbreviations", r"DEFINITIONS\s+AND\s+ABBREVIATIONS"),
    ("Summary of the Offer Document", r"SUMMARY\s+OF\s+(?:THE\s+)?(?:OFFER|ISSUE)\s+DOCUMENT"),
    ("Risk Factors", SEC + r"RISK\s+FACTORS"),
    ("The Issue / The Offer", r"^\s*THE\s+(?:ISSUE|OFFER)\s*$"),
    ("Summary of Financial Information", r"SUMMARY\s+(?:OF\s+)?FINANCIAL\s+INFORMATION"),
    ("General Information", r"^\s*GENERAL\s+INFORMATION\s*$"),
    ("Capital Structure", r"^\s*CAPITAL\s+STRUCTURE\s*$"),
    ("Objects of the Issue", r"OBJECTS\s+OF\s+THE\s+(?:ISSUE|OFFER)"),
    ("Basis for the Issue Price", r"BASIS\s+FOR\s+(?:THE\s+)?(?:ISSUE|OFFER)\s+PRICE"),
    ("Statement of Tax Benefits", r"STATEMENT\s+OF\s+(?:SPECIAL\s+)?TAX\s+BENEFITS"),
    ("Industry Overview", r"^\s*INDUSTRY\s+OVERVIEW\s*$"),
    ("Our Business", r"^\s*OUR\s+BUSINESS\s*$"),
    ("Key Regulations and Policies", r"KEY\s+REGULATIONS\s+AND\s+POLICIES"),
    ("History and Certain Corporate Matters", r"HISTORY\s+AND\s+CERTAIN\s+CORPORATE"),
    ("Our Management", r"^\s*OUR\s+MANAGEMENT\s*$"),
    ("Our Promoters and Promoter Group", r"OUR\s+PROMOTERS?\s+AND\s+PROMOTER\s+GROUP"),
    ("Our Group Companies", r"^\s*OUR\s+GROUP\s+COMPAN"),
    ("Dividend Policy", r"^\s*DIVIDEND\s+POLICY\s*$"),
    ("Financial Statements", SEC + r"FINANCIAL\s+(?:STATEMENTS|INFORMATION)\s*$"),
    ("Restated Financial Information",
     r"RESTATED\s+(?:CONSOLIDATED\s+|STANDALONE\s+)?FINANCIAL\s+INFORMATION"),
    ("Other Financial Information", r"OTHER\s+FINANCIAL\s+INFORMATION"),
    ("MD and A", r"MANAGEMENT.{0,3}S\s+DISCUSSION\s+AND\s+ANALYSIS"),
    ("Capitalisation Statement", r"CAPITALI[SZ]ATION\s+STATEMENT"),
    ("Financial Indebtedness", r"^\s*FINANCIAL\s+INDEBTEDNESS\s*$"),
    ("Outstanding Litigation", r"OUTSTANDING\s+LITIGATION"),
    ("Government and Other Approvals", r"GOVERNMENT\s+AND\s+OTHER\s+APPROVALS"),
    ("Other Regulatory and Statutory Disclosures", r"OTHER\s+REGULATORY\s+AND\s+STATUTORY"),
    ("Issue Structure", r"^\s*(?:ISSUE|OFFER)\s+STRUCTURE\s*$"),
    ("Issue Procedure", r"^\s*(?:ISSUE|OFFER)\s+PROCEDURE\s*$"),
    ("Main Provisions of Articles", r"MAIN\s+PROVISIONS\s+OF\s+(?:THE\s+)?ARTICLES"),
    ("Material Contracts and Documents", r"MATERIAL\s+CONTRACTS\s+AND\s+DOCUMENTS"),
    ("Declaration", r"^\s*DECLARATION\s*$"),
]

# A page carrying fewer than this many extractable characters is treated as not
# machine readable. Prose pages carry well over a thousand; a page of vector
# outlines or a scan carries zero; a divider page carries a handful.
READABLE_CHAR_THRESHOLD = 60

# How far into the page to look for a heading. A heading sits at the very top,
# so a tight window keeps the table of contents and the definitions section,
# which mention every heading in the document, from claiming the first match.
HEAD_WINDOW = 160

# A section heading stands alone on a short line. Prose lines and contents
# entries run longer, so this is what separates a real heading from a mention.
HEADING_MAX_CHARS = 70


def _as_page_number(line):
    m = re.fullmatch(r"(\d{1,4})", line)
    if m:
        return int(m.group(1))
    # Some issuers print "Page 131" or "131 of 555".
    m = re.fullmatch(r"(?:Page\s+)?(\d{1,4})(?:\s*(?:of|/)\s*\d{1,4})?", line, re.I)
    return int(m.group(1)) if m else None


def page_number_candidates(text):
    """Every plausible printed page number stamped on a page.

    Issuers differ on placement. Most use a footer, but a good number stamp the
    number at the top of the text block instead. Reading only the footer on one
    of those yields a number on a handful of pages by luck, and an offset
    derived from a thin and possibly skewed sample. So read both ends and let
    the caller vote across the whole document.
    """
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    out = []
    for line in lines[:3] + list(reversed(lines[-5:])):
        n = _as_page_number(line)
        if n is not None:
            out.append(n)
    return out


def probe(path):
    doc = pymupdf.open(path)
    pages = []
    offsets = Counter()
    votes = 0

    for i, page in enumerate(doc, start=1):
        text = page.get_text()
        nchars = len(text.strip())
        try:
            ndraw = len(page.get_drawings())
        except Exception:
            ndraw = 0
        nimg = len(page.get_images(full=True))

        # Offset is pdf page minus printed page. Only count a candidate that
        # could actually be this page's number: front matter is roman numbered
        # or unnumbered, so a printed number above the pdf index is noise.
        found = []
        if nchars:
            for n in page_number_candidates(text):
                if 0 < n <= i:
                    offsets[i - n] += 1
                    votes += 1
                    found.append(n)

        pages.append({
            "pdf_page": i,
            "printed_candidates": found,
            "chars": nchars,
            "drawings": ndraw,
            "images": nimg,
            "readable": nchars >= READABLE_CHAR_THRESHOLD,
        })

    offset, agree = (offsets.most_common(1)[0] if offsets else (None, 0))
    for p in pages:
        p["printed_page"] = (p["pdf_page"] - offset) if offset is not None else (
            p["printed_candidates"][0] if p["printed_candidates"] else None)

    # Sections. Require the heading at the top of the page, and take the
    # printed number from the voted offset rather than from any single page,
    # since a stray integer in a table will otherwise win.
    sections = []
    seen = set()
    for i, page in enumerate(doc, start=1):
        head = page.get_text()[:HEAD_WINDOW]
        if not head.strip():
            continue
        # A section heading stands alone on a short line. Testing whole lines
        # rather than the raw blob keeps a risk factor that happens to mention
        # "restated financial information", or a contents entry, from claiming
        # the section. Those false positives send the reviewer to the wrong
        # page, which is worse than leaving a section unlisted.
        lines = [ln.strip() for ln in head.splitlines()
                 if ln.strip() and len(ln.strip()) <= HEADING_MAX_CHARS]
        if not lines:
            continue
        for name, pat in SECTION_PATTERNS:
            if name in seen:
                continue
            if any(re.search(pat, ln, re.I) for ln in lines):
                found = pages[i - 1]["printed_candidates"]
                printed = pages[i - 1]["printed_page"]
                # Flag only where nothing stamped on the page agrees with the
                # document wide offset, which usually means an annexure has
                # restarted its own numbering.
                anomaly = bool(found) and printed is not None and all(
                    abs(f - printed) > 1 for f in found)
                sections.append({
                    "section": name,
                    "pdf_page": i,
                    "printed_page": printed,
                    "printed_on_page": found[0] if anomaly else None,
                })
                seen.add(name)
                break

    # Contiguous runs of non readable pages.
    runs, start = [], None
    for p in pages:
        if not p["readable"]:
            if start is None:
                start = p["pdf_page"]
        elif start is not None:
            runs.append((start, p["pdf_page"] - 1))
            start = None
    if start is not None:
        runs.append((start, pages[-1]["pdf_page"]))

    # Only runs of three or more matter. Isolated blank or divider pages are
    # normal and are not an investor access problem.
    blocks = []
    for a, b in runs:
        if b - a + 1 < 3:
            continue
        s = pages[a - 1]
        mechanism = ("scanned images" if s["images"] and s["drawings"] < 200
                     else "vector outlines" if s["drawings"] >= 200
                     else "no embedded text")
        blocks.append({
            "pdf_from": a, "pdf_to": b, "pages": b - a + 1,
            "printed_from": (a - offset) if offset is not None else None,
            "printed_to": (b - offset) if offset is not None else None,
            "mechanism": mechanism,
            "drawings_per_page": s["drawings"],
            "images_per_page": s["images"],
        })

    doc.close()
    return {
        "file": path,
        "total_pages": len(pages),
        "offset": offset,
        "offset_confidence": f"{agree} of {votes} page number readings agree",
        "readable_pages": sum(1 for p in pages if p["readable"]),
        "unreadable_blocks": blocks,
        "sections": sections,
        "pages": pages,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf")
    ap.add_argument("--json", action="store_true",
                    help="emit full JSON including per page detail")
    a = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    r = probe(a.pdf)

    if a.json:
        print(json.dumps(r, indent=2))
        return

    print(f"File            : {r['file']}")
    print(f"Total pdf pages : {r['total_pages']}")
    print(f"Page offset     : {r['offset']}   ({r['offset_confidence']})")
    if r["offset"] is not None:
        print(f"                  printed page = pdf page - {r['offset']}")
        print(f"                  pdf page     = printed page + {r['offset']}")
    print(f"Readable pages  : {r['readable_pages']} of {r['total_pages']}")

    print("\nNON MACHINE READABLE BLOCKS")
    if not r["unreadable_blocks"]:
        print("  none of three pages or more")
    for b in r["unreadable_blocks"]:
        print(f"  pdf {b['pdf_from']} to {b['pdf_to']}"
              f"  (printed {b['printed_from']} to {b['printed_to']})"
              f"  {b['pages']} pages  [{b['mechanism']},"
              f" {b['drawings_per_page']} drawings/page]")

    print("\nSECTION INDEX   (printed page, then pdf page)")
    for s in r["sections"]:
        note = ""
        if s.get("printed_on_page") is not None:
            note = f"   [page prints {s['printed_on_page']}, numbering may restart here]"
        print(f"  {str(s['printed_page']):>5}  (pdf {s['pdf_page']:>4})  {s['section']}{note}")


if __name__ == "__main__":
    main()
