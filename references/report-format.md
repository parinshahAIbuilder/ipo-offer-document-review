# Report format and house style

## House style

The reader is a merchant banking director who will forward this to an issuer and
their counsel. Write the way a partner writes to a client, not the way a system
emits output.

- **Do not use the hyphen or dash character in prose.** This is a standing client
  preference and it is absolute. Write "non current", "three hundred and sixty
  five", "cross border", "pre issue". Rephrase where a compound is awkward. The
  character is fine inside a URL, a filename or a code block.
- No bullet fragments where a sentence belongs. Findings are argued, not listed.
- Name the standard of proof in the sentence: "we recomputed", "we were unable
  to locate", "we express no view on".
- Concede in the issuer's favour where the document is right, in the same
  paragraph as the criticism if that is where it belongs.
- Never recommend subscribing or not subscribing. State it explicitly at the end.

## Severity

| Level | Test | Typical remedy |
|---|---|---|
| **Critical** | An investor would want this resolved before the price band is filed. Goes to the reliability or usability of the offering document as a whole. | Restatement, new disclosure, or regeneration of the document |
| **High** | Materially affects how a reader interprets the financial position or the pricing. Underlying figures may be correctly disclosed but the presentation misleads. | New disclosure or correction in a named section |
| **Medium** | Incomplete disclosure, an unexplained material movement, or a question the document should answer and does not. | Written explanation, usually added to MD and A or a note |
| **Low** | Typographical, rounding, or presentational. Individually trivial. | Correction at proof stage |
| **Informational** | No defect. Recorded so the reader can see it was tested. | None |

Grade on consequence to the reader, not on the size of the number. A ₹0.30
million difference that makes a summary table fail to add up is High, because it
is visible on the face of the document. A ₹468 million capital expenditure
difference that the caption may fully explain is Medium, because it may not be
an error at all.

Do not inflate. A report with two Critical findings that are genuinely critical
carries far more weight than one with nine.

## Structure

Sections A to L, then the ranked list, then what was tested and found sound,
then the assessment. Every finding gets a stable reference of the form
`<section letter><number>` so the client can cite it back to the issuer.

| | Section | Contents |
|---|---|---|
| A | Executive summary | The document's own strengths first, then the central issue, then what follows from it. Written as prose an issuer will read, not a list. |
| B | Critical investor findings | Table: ref, severity, finding, evidence, regulatory reference. Six rows at most. |
| C | Financial reporting and Ind AS findings | Full findings with recomputation blocks |
| D | Income tax findings | Effective rate, cash tax, transfer pricing, indirect tax |
| E | Companies Act and Schedule III findings | |
| F | SEBI ICDR and LODR findings | Objects, pricing, peers, KPIs, machine readability |
| G | Secretarial and governance findings | Remuneration, board, subsidiaries, ESOP |
| H | Related party findings | Usually a table; note the aggregate is often modest and say so |
| I | Missing disclosure checklist | Present / Partially present / Missing / **Not verifiable** / Not applicable |
| J | Internal inconsistency report | Table: item, location one and value, location two and value, difference |
| K | Financial red flag dashboard | Metric tiles plus an earnings quality recomputation |
| L | Investor due diligence questions | Numbered, each answerable by the issuer, gating ones first |
| | Top ten issues | Ranked by how much resolution would change an investor's assessment, with a column saying why it ranks there |
| | What we recomputed and accepted | The arithmetic that agreed, plus any hypothesis formed and withdrawn |
| | Overall assessment | Concern level, reasoning, recommendation on process |
| | Scope and limitations | What was and was not available; the page offset; the not verifiable convention |

**Section I is where the not verifiable distinction lives.** If a note falls
inside a block of pages carrying no extractable text, it is not verifiable, and
the checklist must say so rather than calling it missing. See
`failure-modes.md` item 5.

**The "what we recomputed and accepted" section is not optional.** It proves the
review happened, lets the reader calibrate severity, and makes the remaining
findings much harder to dismiss. Show the arithmetic.

## Finding anatomy

Each substantive finding carries:

1. A heading that states the defect as a claim, not a topic.
2. A recomputation block, monospaced, showing the arithmetic.
3. Prose explaining what the requirement is and where the document falls short.
4. A metadata strip: **Evidence** (printed page references), **Regulatory
   reference** (to paragraph level), and where useful **Remedy sought**,
   **Severity note** or **Classification** recording that the item requires
   clarification rather than being asserted as non compliance.

Cite printed pages in the report, not pdf pages, and state the offset once in
the scope note.

## Overall assessment

Choose from Low, Moderate, Elevated or High concern. Say what drives the level
and, importantly, what would reduce it. Distinguish clearly between "the
financial statements appear misstated", which is rare and grave, and "the
disclosure around a correctly stated figure is insufficient", which is common
and curable. Most reviews land on the second.

Close with an explicit statement that the report expresses no view on the merits
of the investment and contains no recommendation to subscribe or not subscribe.

## Delivery

Publish the report as an artifact and hand over the link. The client forwards
these, so it needs to read as a finished document: real typographic hierarchy,
tabular figures, findings that scan at a glance by severity, and tables that
scroll inside their own container rather than pushing the page sideways.

## The issuer letter

Frequently requested as a follow up, sometimes as the primary deliverable. It is
a different document, not a reformatting of the report.

- Open by recording what tested correctly. It costs a paragraph and changes how
  the rest is received.
- One numbered paragraph per issue, in the order the issuer will care about,
  not the order of the report sections.
- Ask for a specific thing in each paragraph. "We request the counterparty, the
  contract value and the tenure" is actionable; "this is inadequate" is not.
- Separate the gating items from the rest explicitly, and say which must be
  answered before the price band is filed.
- Close with the overall position, including the constructive point that better
  disclosure usually strengthens the offering rather than weakening it.
- Offer to walk the finance team and the book running lead managers through the
  working.

When the issuer replies, assess each item on its merits and concede where they
are right, in terms. An issuer who sees you withdraw one item will engage
seriously with the rest.
