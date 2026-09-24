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

## Not included

`build_gap_deck.js` is the generator for a slide deck. The rendered `.docx`,
`.pptx`, `.xlsx` and `.html` deliverables described in `HANDOFF.md` §5.1 were not
in the recovered archive and have not been rebuilt.
