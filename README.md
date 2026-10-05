# ipo-offer-document-review

A Claude skill for forensic regulatory and investor review of Indian IPO offer
documents, being draft red herring prospectuses, red herring prospectuses and
prospectuses, against SEBI ICDR 2018, SEBI LODR 2015, the Companies Act 2013,
Schedule III Division II, Ind AS and the Income Tax Act 1961.

It was built from a working merchant banking review practice rather than from
the regulations alone, so a good deal of what it encodes is the difference
between a finding that survives contact with the issuer and one that does not.

The companion skill
[review-markup](https://github.com/parinshahAIbuilder/review-markup)
delivers the findings into the issuer's own files: colour coded highlights with
severity graded comments in the offer document itself, tracked changes in Word,
and cell marking in Excel. This skill produces the findings. Install both where
the deliverable is a marked up document rather than a report.

## What it does

Given an offer document it will map the document, read it in the order that
reaches the substance fastest, recompute the arithmetic rather than accepting
it, and produce a severity graded report with a paragraph level regulatory
citation behind every material finding. It will also draft the covering letter
to the issuer and, when the issuer replies, assess the reply item by item.

The kinds of things it is built to catch:

- the same figure carrying two different values in two places
- totals that do not foot, and summaries that do not agree with the statements
  they summarise
- a material balance sheet movement that the document declines to explain
- headline operating cash flow driven by a single working capital movement
- changes in accounting estimates in the year that sets the pricing
- non recurring gains folded into the comparatives used in the price basis
- mandatory disclosures that are absent, and the separate question of
  disclosures that merely cannot be verified
- pricing and Objects sections that do not support themselves

## Installing

Copy the folder into your personal skills directory:

```
~/.claude/skills/ipo-offer-document-review/
```

Then start a new Claude Code session. Skills are discovered at session start, so
a session already running will not see it.

Confirm it loaded by typing `/` and looking for `ipo-offer-document-review`.

## Using it

Either the slash form:

```
/ipo-offer-document-review review the attached RHP
```

or simply describe the job, since the description is written to catch the way
these requests are normally phrased:

- find the errors, omissions and missing disclosures in this RHP
- reconcile the restated financials against the summary
- check the Basis for the Issue Price and the Objects of the Issue
- the company has replied to our observations, is their answer right

## Requirements

Python with `pdfplumber` and `pymupdf`:

```
pip install pdfplumber pymupdf
```

Nothing else. In particular the scripts deliberately avoid `pdftoppm`,
`pdfimages` and `pdftotext`, which are frequently absent and, in the last case,
actively unreliable on financial tables.

## What is in here

```
SKILL.md                            the workflow
scripts/probe.py                    page offset, machine readability map, section index
scripts/extract.py                  table reconstruction by word clustering
scripts/render.py                   page rendering for sections carrying no text
references/failure-modes.md         ten ways to be wrong, each from a real review
references/reconciliation-tests.md  the arithmetic battery
references/regulatory-map.md        ICDR, Companies Act, Schedule III, Ind AS, tax
references/report-format.md         report structure, severity rubric, house style
```

### probe.py

Run this first on any document. It settles the three things everything else
depends on, in about a minute on a 550 page file:

```
python scripts/probe.py document.pdf
```

- **The page offset.** Offer documents are cited by printed page, and every
  cross reference inside the document is a printed page. Citing pdf pages in
  correspondence to an issuer is a tell.
- **Which pages are not machine readable.** Financial statement sections
  routinely arrive as scans or as text converted to vector outlines. This
  governs what you may conclude: a note you cannot search is not verifiable,
  never missing.
- **Where the sections are.**

Tested against offer documents ranging from 500 to 850 pages, with page offsets
of three, four and five detected correctly in each case.

### The failure modes file

Worth reading on its own. Every entry is a mistake actually made on a real
document, including a table read in reverse column order, a scan artefact that
turned 80.50 into 00.50, proforma financial information mistaken for a
contradiction of the restated statements when divergence is the entire point of
preparing it, and the distinction between a disclosure that is missing and one
that merely sits on a page you could not search.

The common shape of all of them is that the document was right and the reading
was wrong, which is the assumption to start from.

## A note on scope

The skill produces observations and questions for an issuer. It does not and
will not make a recommendation to subscribe or not to subscribe, and the report
format requires that to be stated expressly.

## Licence

MIT. See [LICENSE](LICENSE).
