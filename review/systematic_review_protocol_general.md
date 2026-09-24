# Systematic Literature Review Module — General Protocol

**Version:** 1.0 (draft), 2026-09-24
**Scope:** domain-agnostic. Any field, any review question.
**Deployment:** local build. Free/open-access retrieval. One locally-hosted LLM screener, with a human verification sample.
**Status:** specification only — not executed.

---

## 0. What this is

A protocol for running a literature review so that **every claim is traceable to
a sentence in a document you hold on disk**.

It exists because unstructured review produces confident-looking output whose
evidence base is uneven and invisible. This protocol makes evidence strength a
recorded property of every claim rather than an impression.

**Design principles**

| Principle | Mechanism |
|---|---|
| Nothing is asserted that is not quoted | Extraction schema rejects values without a source quote |
| Nothing is claimed above its weakest source | Confidence grade propagates, machine-checked |
| Every search is repeatable | All queries logged verbatim with dates and filters |
| Absence is a claim, and needs a boundary | Citation-sweep procedure, not "I didn't find it" |
| The machine triages; the human decides the hard cases | Confidence-routed screening |
| Nothing is deleted | Append-only logs, cached raw responses |

---

## 1. Roles — machine vs human

Fix this before building. It determines what the review can claim.

| Stage | Machine | Human |
|---|---|---|
| Search | Executes and logs all queries | Approves the search strategy |
| Deduplicate | Automatic | — |
| Screen (title/abstract) | Screens **all** records | Screens a **validation sample**; adjudicates flagged cases |
| Retrieve | Resolver chain, PDF store | Supplies PDFs the chain cannot reach |
| Summarise | Drafts per-paper records | Verifies a sample |
| Extract | Proposes fields + quotes | **Verifies a sample against the PDF** |
| Appraise | Proposes grades | Confirms or overrides |
| Audit | Runs gates, computes statistics | Reads the audit report and accepts or rejects |
| Synthesise | Drafts | Owns the conclusions |

**The human is never optional.** The protocol is designed so that human effort
is *small and targeted*, not absent.

---

## 2. Pipeline

Three phases. Each phase gates the next — **nothing advances until its phase
passes its own checks.** Within each phase, every stage writes an append-only
artefact, and nothing downstream may assert more than upstream provenance
supports.

```
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE A — DOWNLOAD & CURATION        "get the right papers, on disk"     ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [1] PROTOCOL   question, criteria, outcomes  → protocol.md (frozen+hash) ║
║ [2] SEARCH     queries → candidate records   → search_ledger.csv         ║
║                                              → raw_cache/               ║
║ [3] DEDUPE     DOI/title normalisation       → dedupe_log.csv           ║
║ [4] SCREEN     title+abstract → in/out/?     → screening_log.csv        ║
║ [5] RETRIEVE   resolver ladder + manual queue→ retrieval_log.csv        ║
║                                              → pdf_store/               ║
╚══════════════════════════════════════════════════════════════════════════╝
        ↓  gate: every INCLUDE has a PDF, or a logged reason it does not
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE B — SUMMARIZE & RECORD         "turn papers into structured data"  ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [6] SUMMARISE  per-paper structured record   → summaries.jsonl          ║
║ [7] EXTRACT    schema-enforced values+quotes → extraction.csv           ║
║ [8] APPRAISE   quality + confidence grade    → appraisal.csv            ║
╚══════════════════════════════════════════════════════════════════════════╝
        ↓  gate: every value carries a verbatim quote that matches its source
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE C — AUDIT                      "prove the record is trustworthy"   ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [9]  VERIFY    human sample vs stored PDFs   → verification_log.csv     ║
║ [10] RELIABILITY screening stats, κ, recall  → reliability.json         ║
║ [11] GATES     all automated checks (§13)    → audit_report.md          ║
║ [12] REPORT    synthesis + PRISMA flow       → prisma_flow.json         ║
║                                              → review.md                ║
╚══════════════════════════════════════════════════════════════════════════╝
```

**Why the phases are separated by gates rather than run continuously:** each
phase has a different failure mode, and each failure is cheap to fix in place
and expensive to fix later.

| Phase | Failure it prevents | Cost if it leaks downstream |
|---|---|---|
| **A** | Reviewing the wrong or an incomplete set of papers | Every later conclusion is drawn from a biased sample |
| **B** | Recording a number that is wrong or unsourced | Conclusions rest on values nobody can check |
| **C** | Shipping without knowing the error rate | Findings cannot be defended when challenged |

**Phase A is re-runnable.** New search rounds, snowballing, and late-arriving
manual PDFs all re-enter at the appropriate stage; the ledgers append rather
than overwrite, so the flow counts stay reconcilable.

---

## 3. Stage 1 — Protocol (freeze before searching)

Written and **hashed** before any search runs. Changes after that point are
amendments, logged with date and reason — not silent edits.

Must specify:

- **Question**, in a structured frame (PICO, PECO, SPIDER, or a stated custom frame)
- **Inclusion criteria** — explicit, each independently checkable
- **Exclusion criteria** — each with a short code (`EX1 wrong population`, `EX2 not primary research`, …) used verbatim in screening logs
- **Outcomes / data items** to extract — the extraction schema, fixed in advance
- **Date range and language limits**, with justification
- **Sources to be searched** (§4)
- **Screening design** and its reliability plan (§6)
- **Planned synthesis** — narrative, tabular, or meta-analytic

> Freezing this is what separates a systematic review from a literature summary.
> Criteria invented mid-screening cannot be applied consistently to records
> already screened.

---

## 4. Stage 2 — Search

### 4.1 Sources — free, no subscription

| Source | Key | Gives | Notes |
|---|---|---|---|
| **OpenAlex** | none | 250M+ works, citation graph, OA status | Primary discovery. Use `mailto=` for the polite pool |
| **Crossref** | none | Authoritative metadata, reference lists | `mailto=` for polite pool |
| **Europe PMC** | none | Full-text XML for its OA subset | Best extraction source when available |
| **PubMed E-utilities** | optional | Biomedical metadata | Use the **API**, never the web interface |
| **Semantic Scholar** | optional | Citation graph, open PDFs, TLDRs | Key raises rate limits substantially |
| **Unpaywall** | email | DOI → legal OA copy | The workhorse of the resolver chain |
| **CORE** | free key | OA full-text aggregator | Good fallback |
| **DOAJ** | none | OA journal index | |
| **arXiv / bioRxiv / medRxiv / ChemRxiv** | none | Preprints | Often the only reachable version |

**Field-specific sources** (add as applicable): ACM DL, IEEE Xplore, DBLP,
ERIC, EconLit, AGRICOLA, ClinicalTrials.gov, PROSPERO.

### 4.2 Rules

- **Use APIs, never scrape HTML.** Most "blocked" access is an anti-bot defence
  on the web interface; the REST API of the same corpus is usually open, has no
  CAPTCHA, and publishes its limits.
- **Identify yourself.** Send `mailto` / a real User-Agent. Anonymous traffic is
  what triggers rate-limiting.
- **Back off exponentially** on 429/503. Never hammer.
- **Cache every raw response** to `raw_cache/` keyed by request hash. Re-runs
  must not re-request. This also makes the run auditable after the fact.
- **Log every query** — source, exact string, filters, date, result count. A
  query not in the ledger did not happen.

### 4.3 Beyond keyword search

Keyword search alone systematically misses work that uses different vocabulary.
Add:

- **Backward citation chasing** — references of every included paper
- **Forward citation chasing** — works citing every included paper (OpenAlex)
- **Snowballing to closure** — repeat until no new includes appear; record the
  number of rounds

---

## 5. Stage 3 — Deduplication

- Normalise DOI (lowercase, strip `https://doi.org/`)
- Match on DOI first; then on normalised title + year + first author
- Fuzzy title match (e.g. token-set ratio ≥ 95) flagged for human confirmation,
  not auto-merged
- Preprint ↔ published version: **link, do not merge.** Record both; extract from
  the published version; note if they differ
- Log every merge with the reason

---

## 6. Stage 4 — Screening with a single LLM

This is the methodologically sensitive stage. Read this section before building.

### 6.1 The constraint, stated plainly

- PRISMA expects **two independent screeners** with a reported agreement statistic.
- **One LLM screener is not that.** Running the same model twice is not
  independent — correlated errors repeat.
- What a single model *can* legitimately support:
  - **Self-consistency** across repeated runs (a stability measure, not agreement)
  - **Validated performance** against a human-screened sample (the real evidence)
- What it cannot support: a claim of dual independent screening.

**Therefore: the human validation sample is not optional.** It is the only thing
that converts the screener from an unvalidated filter into a measured instrument.

### 6.2 Screening design

**Bias toward inclusion at title/abstract.** The error costs are asymmetric:

- A **false exclude** silently removes a paper from the review forever.
- A **false include** costs one full-text read.

Set the operating point accordingly. Target **sensitivity (recall) ≥ 0.95** on
the validation sample; accept low precision at this stage. Pruning happens at
full text.

**Three-way output, not binary:**

| Decision | Routing |
|---|---|
| `INCLUDE` | → full-text retrieval |
| `EXCLUDE` | → excluded, with criterion code |
| `UNCERTAIN` | → **human queue** |

Force `UNCERTAIN` whenever the model's confidence is below a pre-set threshold,
or the abstract lacks the information needed to decide. A screener that is never
uncertain is miscalibrated.

**Structured output per record:**

```json
{
  "record_id": "W2755950973",
  "decision": "UNCERTAIN",
  "criteria_met": ["IN1", "IN3"],
  "criteria_failed": [],
  "exclusion_code": null,
  "reason": "Population matches but outcome measure is not stated in the abstract",
  "confidence": 0.44,
  "model": "<model-id>",
  "prompt_version": "v1.2",
  "run_seed": 7,
  "screened_date": "2026-09-24"
}
```

**Run settings:** temperature 0 and a fixed seed for the primary pass, so the
run is reproducible. Use temperature > 0 only for the stability check below.

### 6.3 Reliability measurement — what to actually report

Run all three. Report all three.

| Measure | How | What it evidences |
|---|---|---|
| **Stability** | Re-screen a random 10% at temperature 0.7, k=3 runs; report the proportion of records receiving an identical decision every time | The screener is not arbitrary |
| **Prompt sensitivity** | Screen the same subset with 2 independently worded prompts encoding the same criteria; report agreement | Decisions follow the criteria, not the wording |
| **Human validation** | A human screens a random sample, **blind** to the model's decision. Report **sensitivity, specificity, and Cohen's κ** | The only external evidence of correctness |

**Validation sample size:** ≥ 20% of records or ≥ 100 records, whichever is
larger; and **all** `UNCERTAIN` cases regardless of sample.

**Stopping rules:**

- Sensitivity < 0.95 → the screener is losing papers. Revise criteria or prompt
  and **re-screen from scratch**. Do not patch results.
- κ < 0.60 → the criteria are ambiguous to a reader. Fix the criteria, not the model.
- Stability < 0.90 → tighten the prompt or lower the temperature.

### 6.4 Disclosure

The methods section must state, without softening:

- That screening was performed by an LLM, which model, which version, what prompt, what settings
- That a single screener was used, and that this **does not meet PRISMA's dual-screening expectation**
- The validation sample size, sensitivity, specificity and κ
- How `UNCERTAIN` cases were adjudicated

> Check the target venue's AI-use policy **before** running the review. Guidance
> is actively evolving and varies by journal; some require disclosure, some
> restrict LLM screening outright. This is far cheaper to establish now than
> after the work is done.

---

## 7. Stage 5 — Retrieval and the PDF store

### 7.1 Resolver ladder

Fixed order. Record which rung succeeded for every item.

```
1. Unpaywall / OpenAlex best OA location   → OA PDF
2. Europe PMC OA subset                    → full-text XML  (preferred: clean structure)
3. Preprint server                         → arXiv / bioRxiv / medRxiv / ChemRxiv
4. CORE / institutional repository         → author deposit
5. Publisher landing page                  → often abstract only
6. Reference list of a paper already held  → for metadata resolution
7. → MANUAL QUEUE                          → human fetches
```

### 7.2 Manual queue

A first-class state, not a failure.

- States: `pending_manual → requested → received → extracted` (or `unobtainable`)
- Export a worklist: title, authors, year, DOI, **why it is needed**, and **which
  claim depends on it**
- **Prioritise by consequence** — a paper gating a conclusion outranks one
  supporting a settled point
- Watch a `drop/` folder; ingest deposited PDFs automatically by DOI in filename
  or by matching extracted title
- `unobtainable` items remain visible in the flow diagram and in the limitations

### 7.3 PDF store

```
pdf_store/
  <doi-slug>/
    original.pdf            # byte-for-byte as retrieved
    fulltext.txt            # extracted text, page markers preserved
    fulltext.xml            # if Europe PMC / JATS available
    meta.json               # url, rung, retrieval date, sha256, page count
```

- **Content-addressed and immutable.** Never overwrite; new retrieval = new version.
- **Preserve page numbers** in extracted text — quotes must be locatable by a
  human opening the PDF.
- **Text extraction:** PyMuPDF or pdfplumber. If a PDF yields little text it is a
  scan → OCR (`ocrmypdf` / Tesseract) and **flag it**, since OCR text is
  lower-fidelity and quotes from it need closer human checking.
- **Record the SHA-256** so a later manual check provably refers to the same file.
- Respect licences: store for personal verification; do not redistribute.

---

## 8. Stage 6 — Summarise (per-paper record)

Extraction (§9) pulls *specific pre-specified values*. Summarising produces a
**structured record of the whole paper**, so that later questions can be
answered without re-reading everything — and so that a paper's relevance can be
reassessed if the review question shifts.

Both are needed. Extraction alone loses context; summaries alone are not
analysable.

### 8.1 Record schema

One record per included paper, written to `summaries.jsonl`.

```json
{
  "citation_key": "Author2021",
  "record_id": "W2755950973",
  "one_line": "Benchmarks 8,447 generative models to identify which evaluation metrics track quality.",
  "objective": "Determine which metrics correlate with model quality in low-data regimes",
  "study_type": "computational benchmark",
  "data_used": ["COCONUT", "ChEMBL", "GDB-13", "ZINC"],
  "sample_size": "8,447 models; >4 billion molecules",
  "methods_summary": "Trained CLMs across 11 training-set sizes x 10 replicates x 4 databases...",
  "key_findings": [
    {"finding": "Five metrics correlated with quality at rho >= 0.80 across all four databases",
     "source_quote": "...", "source_locator": "p. 763, Fig 3"}
  ],
  "limitations_stated_by_authors": ["Single architecture family"],
  "relevance_to_question": "Defines the metric set this review adopts",
  "relevance_grade": "central",
  "evidence_grade": "F",
  "code_available": "github.com/...",
  "licence": "MIT",
  "conflicts_declared": "none",
  "summarised_by": "<model-id> v1.2",
  "verified_by_human": false
}
```

### 8.2 Rules

- **Every entry in `key_findings` carries a quote and locator.** Narrative fields
  (`objective`, `methods_summary`) may be paraphrase; findings may not.
- **`relevance_grade`** ∈ `central` / `supporting` / `background` / `excluded-on-read`.
  A paper that passed abstract screening but proves irrelevant on full text is
  marked `excluded-on-read` **here**, with a reason — it stays in the flow
  counts as a full-text exclusion.
- **Author-stated limitations are recorded, not filtered.** They are frequently
  the most useful sentences in a paper and are routinely lost in summarisation.
- **Do not summarise from the abstract** when full text is held. If only the
  abstract is available, `evidence_grade` is `A` and the record is marked
  partial — the summary must not imply more was read than was.

---

## 9. Stage 7 — Extraction

### 9.1 The core rule

**A value cannot be recorded without the text it came from.**

```json
{
  "record_id": "W2755950973",
  "citation_key": "Author2021",
  "item": "sample_size",
  "value": "8447",
  "units": "models",
  "context": "benchmark sweep",
  "source_quote": "we trained a total of 8,447 models across four databases",
  "source_locator": "p. 761, Results, para 2",
  "evidence_grade": "F",
  "retrieved_from": "pdf_store/10.1038-s42256-021-00368-1/original.pdf",
  "extracted_by": "<model-id> v1.2",
  "verified_by_human": false,
  "extracted_date": "2026-09-24"
}
```

- Empty `source_quote` or `source_locator` → **build failure**, not a warning.
- `source_quote` must appear **verbatim** in `fulltext.txt` — verify by string
  match at write time. A quote that does not match is a fabrication and must
  fail loudly.

### 9.2 Evidence grades

| Grade | Meaning |
|---|---|
| **F** | Full text held and read |
| **P** | Partial — abstract, or a table without surrounding text |
| **A** | Abstract only |
| **S** | Secondary — taken from another paper's report of it |
| **NR** | Not retrieved |

- `S` must name the intermediary source.
- `A` and `S` values may inform, but may not be the **sole** support for a headline claim.

### 9.3 Human verification

- Verify a random sample of ≥ 10% of extracted values against the stored PDF
- **Verify 100%** of values that support a headline conclusion
- Record `verified_by_human` per row and report the error rate found
- Any error found → widen the sample

---

## 10. Stage 8 — Appraisal

- **Per study:** design, sample size, data availability, code availability,
  licence, funding, conflicts, and a risk-of-bias assessment using an instrument
  appropriate to the field (RoB 2, ROBINS-I, QUADAS-2, CASP, or a stated custom
  rubric)
- **Per synthesised claim:** a confidence grade that **may not exceed the weakest
  supporting source's `evidence_grade`** — machine-enforced

---

## 11. Absence claims

"No one has done X" is often the most valuable finding and the most fragile.
Never assert it from keyword search alone.

1. **Forward citation sweep** — retrieve everything citing the canonical source
   for X (OpenAlex, free and complete)
2. **Screen that set** against the specific question
3. **State the boundary**: *"Of N works citing [Source] as of [date], none
   applies it to [context]"* — a checkable claim
4. If a sweep is infeasible, **downgrade the language** to what the search
   supports ("we found no…") rather than asserting absence

---

## 12. Phase C — Audit

The audit is a **discrete pass over the finished record**, not a feeling of
confidence. It runs after Phase B and produces `audit_report.md`, which is the
document you hand to anyone who asks "how do you know?".

It has four components.

### 12.1 Human verification against stored sources (Stage 9)

- Draw a random sample of extracted values and summary findings
- The verifier opens the **stored PDF** and checks the quote, the locator and
  the interpretation
- Record per row: `correct` / `quote-wrong` / `locator-wrong` / `misread`
- Minimum sample: **10% of all values**, **100% of values supporting a headline
  conclusion**, **100% of OCR-sourced values**
- **Any error widens the sample.** Two or more errors in a sample → verify the
  whole category

Distinguish the two failure types, because they have different fixes:

| Failure | Meaning | Fix |
|---|---|---|
| **quote-wrong** | The quote is not in the source | Fabrication — fails G-VERBATIM; investigate the whole run |
| **misread** | Quote is accurate, meaning is not | Interpretation error — no automated gate catches this; only human reading does |

### 12.2 Screening reliability (Stage 10)

Consolidates §6.3 into reportable numbers: sensitivity, specificity, κ against
the human sample; stability across repeat runs; prompt-variant agreement.
Written to `reliability.json` and quoted directly in the methods section.

### 12.3 Automated gates (Stage 11)

All gates in §13, run as one pass. Every gate reports pass/fail plus the
offending rows. A failing gate blocks the report — it is not advisory.

### 12.4 Coverage and bias audit (Stage 12 input)

The part most reviews omit. Quantify what the review **missed**, not only what
it found:

- **Retrieval rate** — of records screened in, what fraction was obtained?
- **Unobtainable profile** — are the missing items concentrated by publisher,
  year, language or field? If yes, that is a **systematic bias**, and it must be
  named in the limitations, not averaged away
- **Evidence-grade distribution** — what share of conclusions rests on `F` vs
  `P` / `A` / `S`?
- **Single-source claims** — list every conclusion supported by exactly one
  paper
- **Absence claims** — confirm each has a citation-sweep record (§11)

> A review that reports 67% full-text coverage and names where the other 33%
> went is more trustworthy than one that reports nothing and implies 100%.

### 12.5 Audit report contents

```
audit_report.md
├── Gate results                    pass/fail per gate, offending rows
├── Verification sample             n, error rate, errors by type
├── Screening reliability           sensitivity, specificity, kappa, stability
├── Evidence-grade distribution     share of claims by grade
├── Coverage                        retrieval rate; profile of unobtainable items
├── Single-source claims            enumerated
├── Absence claims                  each with its sweep record
└── Known limitations               carried into the report's limitations section
```

---

## 13. Quality gates

Every gate runs in CI. All are cheap. Each catches a failure that occurs in real
reviews.

| Gate | Fails when |
|---|---|
| **G-PROTOCOL** | The frozen protocol hash changed without a logged amendment |
| **G-QUERY** | A record appears that no ledgered query could have produced |
| **G-QUOTE** | An extracted value lacks `source_quote` or `source_locator` |
| **G-VERBATIM** | A `source_quote` does not string-match the stored full text |
| **G-GRADE** | A claim's confidence exceeds its weakest source's grade |
| **G-CITE** | A citation key in any document does not resolve in the bibliography |
| **G-PRISMA** | Flow counts do not reconcile: identified − duplicates − excluded = included |
| **G-ABSENCE** | An absence claim has no citation-sweep record |
| **G-SCREEN** | Validation sensitivity below the pre-set floor |
| **G-CACHE** | A result cannot be reproduced from `raw_cache/` |

> **G-VERBATIM is the most important gate in this document.** It is the one that
> makes fabricated numbers structurally impossible rather than merely discouraged.

---

## 14. Reporting

- **PRISMA 2020 checklist** — all 27 items
- **Flow diagram** — identified / duplicates removed / screened / excluded with
  reasons / full text sought / not retrieved / included
- **Search appendix** — every query verbatim, per source, with dates
- **Screening appendix** — model, prompt, settings, validation statistics
- **Limitations** — must include: single-screener design, unobtainable items,
  OA-only retrieval bias, any OCR-sourced extractions
- **Data availability** — publish the ledgers and extraction tables; they are the
  review's evidence

### On OA-only retrieval bias

Open-access-only retrieval is **not** a random sample of the literature. It
skews by publisher, field, funder mandate and date. State this explicitly and,
where possible, quantify it: report what fraction of screened-in records were
obtainable, and whether the unobtainable set differs systematically (e.g.
concentrated in one publisher or older work).

---

## 15. Minimum viable build

Build in this order; each step is independently useful and leaves a working
system behind.

| # | Component | Phase | Why here |
|---|---|---|---|
| 1 | Search ledger + raw cache | A | Everything depends on reproducible retrieval |
| 2 | Resolver ladder + PDF store + manual queue | A | Unblocks reading; **highest value per unit of effort** |
| 3 | Extraction schema + **G-QUOTE** + **G-VERBATIM** | B | Makes fabricated values structurally impossible |
| 4 | Summary records | B | Makes papers re-usable without re-reading |
| 5 | Human verification sample | C | The only control for misreading |
| 6 | Screening + three-way routing | A | Scales the review to a large candidate set |
| 7 | Reliability statistics | C | Makes the screener defensible |
| 8 | Remaining gates + audit report | C | Makes the whole record defensible |
| 9 | PRISMA flow + report generation | C | Needed only for publication |

**Note the ordering is not strictly A → B → C.** Steps 1–5 give a trustworthy
small review immediately; screening (6) is only worth building once the
candidate set is too large to read. Build the thing that makes a *small* review
correct before the thing that makes a *large* review feasible.

- **Steps 1–5** improve accuracy now, and are worth building even for an
  internal review that will never be published.
- **Steps 6–9** are what make a review *systematic* and publishable.

---

## 16. Honest limits

- **A hard paywall remains a hard paywall.** The ladder ends at a human. The
  protocol makes that boundary visible and prioritised; it does not remove it.
- **One LLM screener is not two independent screeners.** §6 makes it measurable
  and disclosable, not equivalent.
- **Verbatim quote matching prevents invention, not misreading.** A model can
  quote accurately and still misinterpret. Human verification of headline values
  (§9.3) is the only control for that.
- **OA-only retrieval is a biased sample** (§12).
- **This protocol is unexecuted.** No claim is made about its performance in practice.
