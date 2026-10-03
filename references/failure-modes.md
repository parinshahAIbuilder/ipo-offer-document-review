# Failure modes

Every item here is a mistake actually made while reviewing real offer documents,
caught either by the reviewer or by the client. They are listed first because a
confidently asserted finding that turns out to be wrong costs more credibility
than three real findings buy. An issuer who catches you in one error will use it
to dismiss the other twenty.

The common shape of all of them: **the document was right and the reading was
wrong.** Assume that first.

---

## 1. Column order reversed

**What happens.** You read a three year table, assume the newest year is in the
first data column, compute a trend, and report that receivables collapsed or
margins inverted. In fact the issuer ordered the columns oldest first.

**Why it bites.** Roughly a third of Indian offer documents put the earliest
year first, and the header row is often split across two lines by the extractor
so the years do not sit visibly above their columns.

**How to defend.** Never infer column order from position. Pin it with an
independent figure that can only be true for one ordering:

- A ratio disclosed elsewhere. Days sales outstanding is ideal: recompute
  `receivables / revenue x 365` for each candidate ordering and see which one
  reproduces the disclosed figure. In one review the trade receivable sequence
  looked reversed until the DSO key performance indicator of 88 / 101 / 79
  matched exactly one ordering, which settled it in a single calculation.
- Any monotonic series in the same table, such as share capital after a bonus
  issue, or accumulated depreciation, which can only rise.
- The audit report date, which fixes the latest year.

If nothing pins it, say the ordering could not be confirmed rather than
asserting a trend.

---

## 2. Scan artefact read as a figure

**What happens.** A scanned page renders `80.50` as `00.50`, or `8` as `3`, and
you report a misstatement that is not in the document.

**How to defend.** Before asserting that a printed figure is wrong, re-render
the region at 300 dpi with `render.py --crop` and look again. In one review a
current tax liability read as `00.50` at normal resolution and resolved to
`80.50` when magnified. The finding was withdrawn before it went out, but only
because it was checked.

Treat any figure that is implausible on its face as an artefact until magnified.
Genuine typesetting errors exist, but they are far rarer than scan noise.

---

## 3. Proforma treated as a contradiction of restated

**What happens.** You compare proforma financial information against restated
financial information, find they differ line by line, and report an
inconsistency.

**Why it is wrong.** They are supposed to differ. Proforma financial information
exists precisely because a material event, typically an acquisition, a disposal
or a scheme, occurred after the period covered by the restated statements. Its
purpose is to show what the results would have looked like had the event
occurred at the start of the period. Divergence is the point of the exercise,
not a defect.

**How to defend.** Before writing anything about proforma figures, read the
actual adjustment columns, not the summary. Trace restated plus adjustments
equals proforma for each line. Only if that fails is there a finding. Also read
the basis of preparation note: proforma information is sometimes prepared
voluntarily rather than under a mandatory requirement, and describing a
voluntary presentation as mandatory is itself an error.

---

## 4. Asserting absence without searching

**What happens.** You report that a demand, a litigation or a related party
transaction is not disclosed. It is disclosed, in a section you had not reached.

**How to defend.** Never write "not disclosed", "absent" or "missing" without
having grepped the whole extracted text for the amount, the counterparty name
and two or three distinctive keywords. Search for the number both with and
without thousands separators, since extraction is inconsistent.

Phrase the finding to match what you actually did: "we were unable to locate a
corresponding entry in the litigation section and ask for confirmation" is
defensible; "this demand is not disclosed" is not, unless you searched.

---

## 5. Confusing "missing" with "not verifiable"

**What happens.** A note sits inside a block of pages that carry no extractable
text. You cannot search it, so you report the disclosure as missing.

**Why it matters.** These are different findings with different remedies and
very different tone. An issuer who can point to the note on a page you could not
read will treat your whole report as careless.

**How to defend.** `probe.py` tells you which pages are not machine readable.
For any disclosure whose note falls in that range, either render and read the
pages, or classify the item as **not verifiable** and say why in the same line.
Reserve **missing** for things you searched the readable text for and did not
find.

You can still make a strong finding about the readable sections: "in the 490
machine readable pages the phrase appears once" is a precise, checkable claim.

---

## 6. `pdftotext -layout` column collapse

**What happens.** The layout mode approximates columns with spaces. On a tight
financial table the approximation fails and figures land under the wrong
heading. The output looks plausible, so the error is silent.

**How to defend.** Use `extract.py`, which clusters words by y coordinate and
marks real column boundaries with a separator. When a row shows fewer separators
than its neighbours, a cell is missing, which is usually where a footing error
hides. If a table still looks wrong after that, render the page and read it.

---

## 7. Rounding noise reported as a discrepancy

**What happens.** Components sum to 551.67 against a stated total of 551.68 and
you raise it at the same severity as a real inconsistency.

**How to defend.** Differences of one or two in the last decimal across a column
of eight or more figures are rounding, not error. Group them into a single low
severity item covering all such instances in the document, note that each is
individually trivial, and say what they indicate collectively, which is usually
that the final proof was not read against the underlying schedules. That framing
is accurate and is one an issuer can act on.

A difference that repeats identically in two places, such as 0.30 appearing both
as a component gap and as a summary against statement difference, is not
rounding. That is one error propagating, and it is a real finding.

---

## 8. Overstating non compliance

**What happens.** You cite a regulation as breached where the position actually
turns on facts you do not have, such as contract terms or board approvals.

**How to defend.** Three registers, used deliberately:

| Register | Use when | Wording |
|---|---|---|
| Non compliance | The provision is clear and the document itself shows the failure | "does not comply with" |
| Disclosure appears incomplete | The requirement is clear, the disclosure is partial | "the disclosure does not state" |
| Requires clarification | The answer depends on facts not in the document | "the question arises squarely and we express no view" |

Prefer the weakest register that still makes the point. A finding phrased as a
question the issuer must answer is harder to deflect than an accusation they can
deny.

---

## 9. Reporting only defects

**What happens.** The report lists twenty problems and nothing else. The issuer
reads it as hostile, the client cannot tell which items are serious, and nobody
can see whether the document is broadly sound or broadly rotten.

**How to defend.** Recompute the things that could have been wrong and were not,
and say so with the arithmetic shown. A section recording what was tested and
found correct does three things: it proves the review was actually performed, it
lets the reader calibrate the severity of what follows, and it makes the
findings that remain much harder to wave away.

Also record, in the report itself, any hypothesis you formed and then withdrew
on testing. That is a feature, not an embarrassment.

---

## 10. Tooling assumptions that waste a round trip

- `pdftoppm` and `pdfimages` are frequently absent, especially on Windows. Use
  `render.py`, which needs only PyMuPDF.
- Whole document pdfplumber scans routinely exceed a two minute command
  timeout. Work in page ranges of at most twenty, or use PyMuPDF, which is far
  faster for bulk text extraction.
- Large heredocs are fragile under Windows shells. Write files with the file
  writing tool rather than shell redirection when the content contains quotes,
  backslashes or non ASCII characters.
- Non raw Python strings silently turn `\b` into a backspace character and `\s`
  into a warning. When patching regex patterns programmatically, use raw
  strings, and verify the patch by printing the pattern back.
