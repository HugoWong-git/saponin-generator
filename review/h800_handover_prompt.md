# Handover Prompt — H800 → Claude

Copy everything between the markers and send it to the H800 session.

**Design notes (for you, not to send):**
- It asks for **three separate packages**. Package A is small and lets work start immediately; the PDFs follow.
- Files are **segregated by provenance**. The Sci-Hub-sourced files are listed but **not** sent, so the rest of the package stays clean.
- It is told **not to re-run, re-fetch or fix anything**. A model asked to hand over will otherwise "improve" things and destroy the evidence of what it actually did.
- It is asked to reconcile the count discrepancies, because only it can.

---8<--- BEGIN PROMPT ---8<---

# Task: full handover of the Stage-1 literature review work

Your literature review work is being taken over. Your job now is a **complete,
faithful export of current state** — not new work.

## Hard rules

1. **Do not re-run the pipeline.** No new searches, no new downloads, no new
   verification passes. Export exactly what exists on disk right now.
2. **Do not fetch anything further from Sci-Hub, sci.bban.top, any mirror, or
   any proxy.** No new retrieval of any kind.
3. **Do not fix, improve, re-tag or re-write anything** — including entries you
   now think are wrong. Errors are evidence and must survive the handover
   intact. If you believe something is wrong, note it in the ISSUES file
   (below); do not change it in place.
4. **Do not delete the quarantine.** The 17 quarantined false positives are
   among the most valuable artefacts you produced.
5. **Label every file by provenance.** Files retrieved via `sci.bban.top` or
   any Sci-Hub route must be clearly labelled and listed. Their **bibliographic
   metadata is wanted** (DOI, title, authors, year, journal — this is factual
   data and will be used). Their **PDFs and extracted text should not be sent**;
   those papers will be re-fetched through publisher-OA, PMC or preprint routes
   instead, and quoted from those copies. The provenance labelling is needed for
   your own methods section regardless.

## Produce three packages

### PACKAGE A — `handover_A_metadata.zip` (send this first; should be small)

Everything except PDFs:

- `acquisition_record.csv` — complete, all rows, all columns, unmodified
- `provenance_split.csv` — **new file**, one row per retrieved file:
  `record_id, doi, file_path, sha256, file_bytes, resolver_source,
  provenance_class` where `provenance_class` is exactly one of
  `OPEN` (arxiv, unpaywall, openalex, OA-XML, publisher OA, institutional repo),
  `SCIHUB` (sci.bban.top or any mirror/proxy), or
  `UNKNOWN` (cannot determine — do not guess)
- `fulltext/` — the extracted text for every **`OPEN`-class** PDF you hold, as
  `<doi-slug>.txt`, with page markers preserved. Omit text for `SCIHUB`-class
  files; those papers will be re-fetched through other routes.
- `meta/` — every per-file `meta.json` (url, rung, retrieval date, sha256,
  page count, status)
- `quarantine_report.csv` — all 17 false positives: what was expected, what
  arrived, the arXiv id used, the field the wrong paper belonged to, how it was
  detected
- `search_ledger.csv` — every query: source, exact query string, filters, date,
  result count. If you did not log these, say so explicitly in ISSUES rather
  than reconstructing them
- `screening_log.csv` — every candidate with its include/exclude/uncertain
  decision, reason, and confidence, for all 163 candidates
- `reference_list.txt`, `store_report.md`, `missing_fulltext_20260925.md`,
  `missing_dois_plain.txt`, `SAPONIN_STAGE1_REVIEW_v4.md` — as they stand
- `code/` — the `lit_review_v2` pipeline source: resolvers, the G-WRONG-ITEM
  implementation, the §12.5 FP-audit, the §12.6 runbook, and any config
- `RUN_SETTINGS.md` — model id and full name, quantisation, context length,
  temperature, seed(s), hardware, total wall-clock time, number of passes, and
  whether any output was truncated
- `ISSUES.md` — see below

### PACKAGE B — `handover_B_pdfs_open.zip` (the PDFs I can use)

- Only files whose `provenance_class` is `OPEN`
- Original PDFs, byte-for-byte, named `<doi-slug>/original.pdf`
- Include any supplementary files obtained
- **Split into parts of ≤ 100 MB** (`handover_B_pdfs_open.part1.zip`, etc.) and
  say how many parts there are

### PACKAGE C — a list only, no files

- `scihub_sourced_list.csv` — the files classed `SCIHUB`, with full
  bibliographic detail so these papers can be re-fetched and cited:
  `doi, pmid, pmcid, title, authors, journal, year, volume, pages, sha256`
- Where you know of an open route for any of them (a PMC author manuscript, a
  preprint, a publisher OA version), add an `alternate_oa_url` column
- **Send the CSV. Do not send the PDFs or their extracted text.** These papers
  will be re-fetched via publisher-OA / PMC / preprint routes and quoted from
  those copies.

## `ISSUES.md` — answer these specifically

Answer each directly. "I don't know" is an acceptable and useful answer;
guessing is not.

1. **Reconcile the counts.** Your README says 90 full texts and 31 references.
   Your access statement says 81 verified full texts. Your `reference_list.txt`
   carries 66 citation tags. `acquisition_record.csv` has 191 rows with 77
   `full_pdf_vor` + 13 `full_pdf_preprint` + 15 `quarantined_fp` + 86
   `metadata_only`. **Which numbers are correct, and what does each one count?**
2. **What exactly did G-WRONG-ITEM compare?** Give the actual rule: which
   strings, what similarity measure, what threshold, and whether it checked
   anything beyond the title — authors, year, venue?
3. **Where did the bibliography text come from?** For each entry, were the
   title, author list, year and venue (a) extracted from the retrieved PDF,
   (b) taken from Crossref/OpenAlex metadata, or (c) written from model recall?
   If different fields came from different places, say which.
4. **What does `title_ratio=None` mean** in the bibliography entries, versus
   `ratio=1.0` or `ratio=0.86` elsewhere? Which entries were actually
   title-verified and which were not?
5. **List every entry you are not confident in**, beyond those already tagged
   `[UNCERTAIN]`.
6. **Did you inspect the 46,000-structure SMILES corpus at any point?** You
   state you did not — confirm, and note anything you did read about it.
7. **What failed or was abandoned?** Any pass that errored, any source that
   blocked you, anything you attempted and dropped.

## Packaging

- Send **Package A first** and confirm it is complete before starting B.
- For each package give: the file list, total size, and a SHA-256 of the zip.
- If anything cannot be exported, say so in `ISSUES.md` rather than omitting it
  silently.

## Reminder

The purpose is an accurate record of what you did, including the parts that went
wrong. A handover that looks tidier than the actual run is worse than useless —
the mistakes are the most informative part of the package.

---8<--- END PROMPT ---8<---
