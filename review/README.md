# Stage 1 Prior — Literature Review

A structured, citation-grounded literature review deciding whether to **adapt an
existing chemical language model** or **build a custom architecture** for the
Stage 1 saponin prior.

These documents were produced in a separate working session and are committed
here because the container holding them was reclaimed and they had to be
recovered from a user-supplied archive. Keeping them in the repository prevents
a recurrence.

## Read in this order

| File | What it is |
|---|---|
| `HANDOFF.md` | Full context. Start here. |
| `progress_log.md` | Newest-first changelog — the reasoning behind every decision, including the errors |
| `open_questions.md` | The Cycle 2 agenda, Q1–Q10 |
| `literature_review_report.md` | The main review: 21-entry comparison table, six model-family syntheses, §7 recommendation, §8 risk register |
| `evaluation_protocol.md` | v3.3 — ~150 metrics, 19 sections, 28 gates |
| `metric_coverage_gap_analysis.md` | Which protocol metrics anyone has ever reported |
| `reported_metrics_record.md` | Transcribed published values (transcription only — see Rule 2) |
| `bibliography.md` / `.bib` | 50 entries, each with a verification status |

## Two rules these documents follow

1. **Every factual claim carries a citation key that resolves against
   `bibliography.md`.** A key was fabricated once in this project and caught only
   by a machine check. Run the checker in `HANDOFF.md` §5.4 before shipping
   anything — and keep its scope at the five files listed there, since
   `progress_log.md` deliberately names retired keys.

2. **Nothing is computed that was not actually computed.** The metrics records
   are transcriptions; unretrieved values say `NOT RETRIEVED`. Published models
   have not been scored against this project's protocol, because that would
   require their weights and ≥100k generated molecules each.

## Status

The §7 recommendation — *adapt an existing SMILES chemical language model; do not
build a custom architecture* — remains **provisional**, gated on Q1, Q2, Q3 and Q5.

**Q4a and Q4b closed on 2026-09-24** by the first live run of
`scripts/audit_corpus.py`. That audit also surfaced two measured defects in this
repository's own pipeline, filed as Q4d and Q4e. See
[`../reports/corpus_and_prior_audit.md`](../reports/corpus_and_prior_audit.md).

## CSV exports

Two machine-readable exports, generated from the markdown above on 2026-09-24.
They are **derived files** — the markdown documents remain the source of truth.

### `evaluation_protocol.csv` — 230 rows, 14 columns

One row per protocol item. `row_type` separates them: **170 metrics**, 28
acceptance gates, 22 failure modes, 7 property groups, 3 splits.

| Column | Meaning |
|---|---|
| `section`, `section_title`, `subsection` | Where it sits in `evaluation_protocol.md` |
| `row_type` | metric / acceptance gate / failure mode / property group / split |
| `metric_id` | The protocol's own ID (`D11`, `S1`, `T7`, `1.1`, `G4`, …) |
| `metric`, `detail` | Name, and the target / what it catches |
| `risk_ref` | Risk-register reference (`R10`, `R11`, …) where the protocol gives one |
| `published_coverage` | Whether anyone has ever measured this — joined per section from `metric_coverage_gap_analysis.md` |
| `best_published_precedent` | The strongest published precedent for that section |
| `gap_verdict` | The gap analysis's verdict for that section |
| `measurement_scope` | training corpus / generated sample / both / model internals |
| `measured_this_project` | Value measured on 2026-09-24, where one was measured |
| `measurement_note` | Provenance for that value |

**22 of the 170 metrics carry a measured value.** The remaining 148 are empty
because they have not been computed — not because they are zero. The three
published-coverage columns are joined at **section** granularity, since the gap
analysis assesses coverage per section rather than per metric.

### `published_reported_metrics.csv` — 314 rows, 12 columns

Tidy long format, one row per model × metric, transcribed from
`reported_metrics_record.md`. 49 distinct models, 47 distinct metrics.

| Column | Meaning |
|---|---|
| `block_num`, `block_title`, `subsection` | Source block in the record |
| `model`, `metric`, `value` | The transcribed value |
| `reported` | `yes` (274) · `no` (22, cell was "—" in the source) · `n/a` (18 narrative or not-retrieved rows) |
| `direction` | higher / lower is better, from the source's own arrow |
| `dataset`, `citation` | What it was measured on, and where it came from |
| `source_confidence` | PRIMARY-FULL (212) · PRIMARY-PARTIAL (49) · SECONDARY (44) · NOT RETRIEVED (9) |
| `notes` | Caveats, including why a value could not be retrieved |

**Three warnings carried over from the source, which the flat format strips:**

1. **Cross-paper comparison is mostly invalid** — different datasets, sample
   sizes, RDKit versions and preprocessing. Validity 0.98 on QM9 and 0.85 on
   GuacaMol are not on the same scale.
2. **Library size changes rankings** — FCD and uniqueness both move with sample
   size, and models swap places across scales.
3. **None of these is a saponin number.** MOSES caps at 27 heavy atoms, QM9 at 9.
   Absolute values carry no information about performance on this chemistry.

Block 4 (DiGress) carries two FCD columns in opposite directions —
GuacaMol-style (higher better) and MOSES-style (lower better). The `direction`
column distinguishes them; do not aggregate across them.

**Row-count note.** `reported_metrics_record.md` refers to a
`reported_metrics.xlsx` with 317 rows (299 reported / 9 not-retrieved / 9 meta).
That workbook was not in the recovered archive, so these 314 rows were rebuilt
from the markdown tables and **have not been reconciled against it**. The counts
are close but not identical.

## Not included

`build_gap_deck.js` is the generator for a slide deck. The rendered `.docx`,
`.pptx`, `.xlsx` and `.html` deliverables described in `HANDOFF.md` §5.1 were not
in the recovered archive and have not been rebuilt.
