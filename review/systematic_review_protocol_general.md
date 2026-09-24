# Systematic Literature Review Module — General Protocol

**Version:** 2.0 (draft), 2026-09-24
**Scope:** domain-agnostic. Any field, any review question.
**Deployment:** local build. Free/open-access retrieval. One locally-hosted LLM.
**Automation posture:** **v1 is fully automated — no human in the loop.**
**Status:** specification only — not executed.

---

## 0. What this is

A protocol for running a literature review so that **every claim is traceable to
a sentence in a document you hold on disk**.

It exists because unstructured review produces confident-looking output whose
evidence base is uneven and invisible. This protocol makes evidence strength a
recorded property of every claim rather than an impression.

### 0.1 v1 is fully automated — and what that costs

Human validation is **deliberately excluded from v1**. That is a reasonable
staging decision, and §16 specifies exactly where humans re-enter later without
rework. But it must be stated honestly, because it changes what the output may
claim.

**What full automation still gives you — these are real and enforceable:**

| Guarantee | Mechanism |
|---|---|
| No fabricated quotes | `source_quote` must string-match stored full text (**G-VERBATIM**) |
| No unsourced values | Schema rejects a value lacking quote + locator (**G-QUOTE**) |
| No claim above its evidence | Grade ceiling propagates from acquisition status (**G-GRADE**) |
| Reproducible retrieval | Every query logged; every raw response cached |
| Honest coverage reporting | Acquisition status recorded per paper in detail (§7) |
| Internal consistency | Self-agreement, ensemble agreement, cross-source triangulation |

**What full automation cannot give you — do not claim these:**

| Not available | Why |
|---|---|
| **PRISMA compliance** | Requires two independent screeners. One model is not two |
| **Sensitivity / specificity / κ** | These need ground truth. Without a human-screened sample there is none |
| **Detection of misreading** | A model can quote accurately and interpret wrongly. No automated gate catches this reliably (§9.4 reduces it; nothing removes it) |
| **Known recall** | You cannot state what fraction of relevant papers the screener found |

> **The one-line version:** an automated pipeline can prove it did not *invent*
> anything. It cannot prove it did not *misunderstand* anything.
>
> That distinction should appear in any output this pipeline produces. An
> internal engineering review can live with it. A publication cannot.

### 0.2 Design principles

| Principle | Mechanism |
|---|---|
| Nothing is asserted that is not quoted | Schema rejects values without a source quote |
| A quote must stand alone | Blind re-derivation check (§9.4) |
| Nothing is claimed above its weakest source | Grade ceiling, machine-enforced |
| Every search is repeatable | All queries logged verbatim with dates and filters |
| Absence is a claim, and needs a boundary | Citation-sweep procedure, not "I didn't find it" |
| Uncertainty is recorded, not resolved | `UNCERTAIN` is a terminal state in v1, carried into the report |
| Nothing is deleted | Append-only logs, cached raw responses |

---

## 1. Roles in v1

| Stage | Machine | Human (deferred to v2) |
|---|---|---|
| Protocol | — | Writes and freezes it *(the one thing a human must do)* |
| Search | Executes and logs all queries | Approves strategy |
| Deduplicate | Automatic | Confirms fuzzy merges |
| Screen | Screens all records; flags `UNCERTAIN` | Validation sample; adjudication |
| Retrieve | Resolver ladder; records detailed status | Supplies paywalled PDFs |
| Summarise | Per-paper structured record | Verifies a sample |
| Extract | Values + quotes | Verifies against PDF |
| Appraise | Proposes grades | Confirms or overrides |
| Audit | Runs all machine checks | Reads report; accepts or rejects |
| Synthesise | Drafts | Owns the conclusions |

**Even in v1, one human step is unavoidable: writing the protocol (§3).** A
review with machine-invented inclusion criteria is not a review of anything in
particular. That is minutes of work, not hours.

---

## 2. Pipeline

Three phases, each gating the next.

```
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE A — DOWNLOAD & CURATION        "get the right papers, on disk"     ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [1] PROTOCOL   question, criteria, outcomes  → protocol.md (frozen+hash) ║
║ [2] SEARCH     queries → candidate records   → search_ledger.csv         ║
║                                              → raw_cache/               ║
║ [3] DEDUPE     DOI/title normalisation       → dedupe_log.csv           ║
║ [4] SCREEN     title+abstract → in/out/?     → screening_log.csv        ║
║ [5] RETRIEVE   resolver ladder               → acquisition_record.csv   ║
║                                              → pdf_store/               ║
╚══════════════════════════════════════════════════════════════════════════╝
        ↓  gate: every record has a terminal acquisition_status
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE B — SUMMARIZE & RECORD         "turn papers into structured data"  ║
╠══════════════════════════════════════════════════════════════════════════╣
║ [6] SUMMARISE  per-paper structured record   → summaries.jsonl          ║
║ [7] EXTRACT    schema-enforced values+quotes → extraction.csv           ║
║ [8] APPRAISE   quality + confidence grade    → appraisal.csv            ║
╚══════════════════════════════════════════════════════════════════════════╝
        ↓  gate: every value carries a verbatim quote that matches its source
╔══════════════════════════════════════════════════════════════════════════╗
║ PHASE C — AUDIT                      "prove the record is self-consistent"║
╠══════════════════════════════════════════════════════════════════════════╣
║ [9]  CONSISTENCY  re-derivation, ensemble    → consistency.json         ║
║ [10] COVERAGE     acquisition + bias profile → coverage.json            ║
║ [11] GATES        all automated checks (§13) → audit_report.md          ║
║ [12] REPORT       synthesis + flow counts    → flow.json, review.md     ║
╚══════════════════════════════════════════════════════════════════════════╝
```

| Phase | Failure it prevents | Cost if it leaks downstream |
|---|---|---|
| **A** | Reviewing the wrong or an incomplete set of papers | Every later conclusion drawn from a biased sample |
| **B** | Recording a number that is wrong or unsourced | Conclusions rest on values nobody can check |
| **C** | Shipping without knowing the limits | Findings cannot be defended when challenged |

**Phase A is re-runnable.** New search rounds, snowballing and late-arriving
PDFs re-enter at the right stage; ledgers append rather than overwrite, so flow
counts stay reconcilable.

---

## 3. Stage 1 — Protocol (frozen, human-written)

Written and **hashed** before any search runs. Later changes are amendments,
logged with date and reason.

Must specify: the question in a structured frame (PICO/PECO/SPIDER or a stated
custom frame); explicit **inclusion criteria**; **exclusion criteria** each with
a short code (`EX1 wrong population`, `EX2 not primary research`, …) used
verbatim in logs; the **data items to extract** (the extraction schema, fixed in
advance); date and language limits with justification; sources to search (§4);
and the planned synthesis.

> Criteria invented mid-run cannot be applied consistently to records already
> processed. Freezing this is what makes the run interpretable.

---

## 4. Stage 2 — Search

### 4.1 Sources — free, no subscription

| Source | Key | Gives | Notes |
|---|---|---|---|
| **OpenAlex** | none | 250M+ works, citation graph, OA status | Primary discovery. `mailto=` for polite pool |
| **Crossref** | none | Authoritative metadata, references, **retractions** | `mailto=` for polite pool |
| **Europe PMC** | none | Full-text XML for its OA subset | **Best extraction source when available** |
| **PubMed E-utilities** | optional | Biomedical metadata | Use the API, never the web interface |
| **Semantic Scholar** | optional | Citation graph, open PDFs | Key raises rate limits substantially |
| **Unpaywall** | email | DOI → legal OA copy | Workhorse of the resolver ladder |
| **CORE** | free key | OA full-text aggregator | Good fallback |
| **DOAJ** | none | OA journal index | |
| **arXiv / bioRxiv / medRxiv / ChemRxiv** | none | Preprints | Often the only reachable version |

Field-specific additions as applicable: ACM DL, IEEE Xplore, DBLP, ERIC,
EconLit, AGRICOLA, ClinicalTrials.gov, PROSPERO.

### 4.2 Rules

- **Use APIs, never scrape HTML.** Most "blocked" access is an anti-bot defence
  on the web interface; the REST API of the same corpus is usually open and
  publishes its limits.
- **Identify yourself** — `mailto` / real User-Agent. Anonymous traffic triggers
  rate-limiting.
- **Back off exponentially** on 429/503.
- **Cache every raw response** to `raw_cache/`, keyed by request hash. Re-runs
  must not re-request.
- **Log every query** — source, exact string, filters, date, result count.

### 4.3 Beyond keyword search

Keyword search systematically misses work using different vocabulary. Add
**backward citation chasing** (references of includes), **forward citation
chasing** (works citing includes, via OpenAlex), and **snowball to closure** —
repeat until no new includes appear; record the number of rounds.

---

## 5. Stage 3 — Deduplication

- Normalise DOI (lowercase, strip `https://doi.org/`)
- Match on DOI first, then normalised title + year + first author
- Fuzzy title match (token-set ratio ≥ 95) → **merge but flag** in v1, since no
  human confirms it; the flag surfaces in the audit report
- **Preprint ↔ published: link, do not merge.** Extract from the published
  version; record both; note any discrepancy
- Log every merge with its reason

---

## 6. Stage 4 — Screening (single model, no validation sample)

### 6.1 What this stage can and cannot claim in v1

Without a human-screened sample there is **no ground truth**, therefore **no
measurable recall**. Do not report sensitivity, specificity or κ — there is
nothing to compute them against.

What remains measurable is **self-consistency**: whether the screener gives the
same answer to the same record, and whether that answer survives rewording.
Those are stability properties, not correctness properties. Report them as such.

### 6.2 Screening design

**Bias hard toward inclusion.** The error costs are asymmetric and, without
human checking, uncorrectable:

- A **false exclude** silently removes a paper from the review permanently.
- A **false include** costs one automated full-text pass — which is cheap.

In v1, set the threshold so that anything not clearly excludable is retained.
**Prefer a large included set you can filter at full text over a clean one you
cannot audit.**

**Three-way output, with `UNCERTAIN` as a terminal state:**

| Decision | v1 routing |
|---|---|
| `INCLUDE` | → retrieval |
| `EXCLUDE` | → excluded, with criterion code |
| `UNCERTAIN` | → **retrieved and processed as INCLUDE**, flagged throughout, and **listed separately in the report** |

> In v2 `UNCERTAIN` routes to a human. In v1 there is no human, so the safe
> resolution is to include it and mark it. Never let the model resolve its own
> uncertainty silently — the flag must survive into the output, so a reader can
> see which conclusions depend on records the screener was unsure about.

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

Primary pass at temperature 0 with a fixed seed, so the run is reproducible.

### 6.3 Machine-only reliability measures

| Measure | How | Interpretation |
|---|---|---|
| **Stability** | Re-screen a random 10% at temperature 0.7, k=3; report the share with identical decisions | The screener is not arbitrary |
| **Prompt sensitivity** | Screen the same subset with 2 independently-worded prompts encoding the same criteria; report agreement | Decisions follow criteria, not wording |
| **Ensemble disagreement** | If a second model is available, screen a subset with both; report disagreement rate | Correlated-error check |
| **Boundary audit** | Sample records nearest the decision threshold and record their reasons verbatim | Shows *where* the criteria are ambiguous |

**Stop rules:** stability < 0.90 → tighten prompt or lower temperature.
Prompt agreement < 0.80 → the criteria are ambiguous; rewrite them and
**re-screen from scratch**, do not patch results.

These numbers describe the instrument's *consistency*. They say nothing about
its *accuracy*. Report them under a heading that says so.

---

## 7. Stage 5 — Retrieval, the acquisition record, and the PDF store

This is where the request for detail lands. **What was actually obtained for
each paper is the single most important provenance fact in the review** — it
caps every claim downstream.

### 7.1 Resolver ladder

Fixed order; the rung that succeeded is recorded.

```
1. Europe PMC OA subset          → full-text XML   (best: structured, section-tagged)
2. Unpaywall / OpenAlex OA loc.  → publisher OA PDF (version of record)
3. PMC OA / institutional repo   → accepted manuscript
4. Preprint server               → arXiv / bioRxiv / medRxiv / ChemRxiv
5. CORE aggregator               → author deposit
6. Publisher landing page        → abstract, sometimes full HTML
7. Crossref / OpenAlex metadata  → metadata only
8. → terminal failure state, recorded with reason
```

### 7.2 The acquisition record — full schema

One row per record, `acquisition_record.csv`. This is deliberately verbose:
every field answers a question someone will later ask about a claim.

```json
{
  "record_id": "W2755950973",
  "doi": "10.1038/s42256-021-00368-1",
  "citation_key": "Author2021",

  "acquisition_status": "full_pdf_vor",
  "content_obtained": "full_text",
  "version_obtained": "VoR",
  "evidence_ceiling": "F",

  "resolver_rung": 2,
  "resolver_source": "unpaywall",
  "source_url": "https://.../s42256-021-00368-1.pdf",
  "oa_status": "hybrid",
  "licence": "CC-BY-4.0",
  "licence_permits_local_copy": true,

  "file_path": "pdf_store/10.1038-s42256-021-00368-1/original.pdf",
  "file_sha256": "3f2a...",
  "file_bytes": 4182934,
  "page_count": 12,
  "mime_type": "application/pdf",

  "text_extraction": "native_text",
  "ocr_applied": false,
  "text_chars": 51204,
  "text_chars_per_page": 4267,
  "extraction_confidence": "high",

  "has_abstract": true,
  "has_introduction": true,
  "has_methods": true,
  "has_results": true,
  "has_discussion": true,
  "has_references": true,
  "has_figures_text": true,
  "has_tables_text": true,
  "tables_parsed": 4,
  "supplementary_listed": true,
  "supplementary_obtained": false,
  "supplementary_note": "SI PDF behind publisher login",

  "retracted": false,
  "has_correction": false,
  "crossref_update_to": null,

  "attempts": 2,
  "first_attempt": "2026-09-24T10:02:11Z",
  "last_attempt": "2026-09-24T10:02:48Z",
  "failure_history": [
    {"rung": 1, "source": "europepmc", "outcome": "not_in_oa_subset"}
  ],
  "blocked_by": null,
  "http_status": 200,
  "notes": ""
}
```

### 7.3 `acquisition_status` — controlled vocabulary

The primary state. Terminal states are what the gate in §2 requires.

**Success states** (ordered by quality of what was obtained):

| Status | Meaning | `evidence_ceiling` |
|---|---|---|
| `full_text_xml` | JATS/XML full text, section-tagged | **F** |
| `full_pdf_vor` | Version-of-record PDF | **F** |
| `full_pdf_aam` | Accepted manuscript (post-peer-review, pre-typeset) | **F** |
| `full_html` | Publisher HTML full text, parsed | **F** |
| `full_pdf_preprint` | Preprint only; may differ from published version | **F⁻** |
| `partial_text` | Some sections only (first page, excerpt, truncated) | **P** |
| `abstract_only` | Abstract retrieved, no body | **A** |
| `metadata_only` | Title/authors/venue; no abstract | **NR** |

**Failure states:**

| Status | Meaning |
|---|---|
| `failed_paywalled` | Reached publisher; content behind payment |
| `failed_blocked` | CAPTCHA, robots.txt, anti-bot, 403 |
| `failed_rate_limited` | 429 after retries exhausted |
| `failed_network` | DNS, timeout, egress policy denial |
| `failed_not_found` | 404, dead DOI, unresolvable |
| `failed_no_oa_location` | No OA copy exists anywhere indexed |
| `failed_corrupt` | File retrieved but unreadable |
| `failed_wrong_item` | Retrieved file does not match the DOI |
| `withdrawn_retracted` | Retracted or withdrawn — **excluded, but recorded** |
| `unobtainable` | Terminal after all rungs exhausted |

**Non-terminal:** `not_attempted`, `in_progress`, `queued_manual`
*(`queued_manual` is unused in v1; retained so v2 needs no schema change.)*

### 7.4 Supporting vocabularies

**`content_obtained`** — `full_text` · `partial_text` · `abstract` · `metadata` · `none`

**`version_obtained`** — `VoR` (version of record) · `AAM` (accepted manuscript) ·
`preprint` · `unknown`.
Matters because preprint numbers can differ from published ones. Any value
extracted from a `preprint` carries that fact into its provenance.

**`oa_status`** (Unpaywall) — `gold` · `green` · `hybrid` · `bronze` · `closed`

**`text_extraction`** — `native_text` · `ocr_applied` · `ocr_failed` ·
`no_text_layer` · `mixed`

**`extraction_confidence`** — heuristic on characters per page:

| Value | Rule of thumb |
|---|---|
| `high` | native text, > 1500 chars/page |
| `medium` | native text, 500–1500 chars/page, or clean OCR |
| `low` | OCR, or < 500 chars/page |
| `unusable` | < 100 chars/page — treat as `failed_corrupt` |

**`blocked_by`** — `paywall` · `captcha` · `robots` · `rate_limit` ·
`network_policy` · `login_required` · `geoblock` · `unknown`

### 7.5 Rules

- **`evidence_ceiling` is derived, never typed by hand.** It is a pure function
  of `acquisition_status` and `extraction_confidence`. **G-GRADE** enforces that
  no claim exceeds it. This is the mechanism that makes "we only had the
  abstract" impossible to forget.
- **Section flags are computed, not assumed.** Detect headings in the extracted
  text. A PDF whose `has_methods` is false cannot support a methods claim, and
  the gate should say so.
- **Check retraction on every record** via Crossref `update-to`. A retracted
  paper silently included is among the worst failures a review can have, and it
  is cheap to check.
- **Record the full failure history**, not just the final state. "Failed at rung
  1, succeeded at rung 4 as a preprint" is materially different from "succeeded"
  — and it is what lets you later tell whether your coverage gap is a publisher
  problem or a discipline problem.
- **`full_pdf_preprint` is marked `F⁻`** — full text, but of a version that may
  not match the published record. Claims from it should be flagged where the
  published version was never obtained.

### 7.6 PDF store

```
pdf_store/
  <doi-slug>/
    original.pdf            # byte-for-byte as retrieved
    fulltext.txt            # extracted text, page markers preserved
    fulltext.xml            # if JATS available
    supplementary/          # if obtained
    meta.json               # url, rung, date, sha256, page count, status
```

- **Content-addressed and immutable.** Never overwrite; a new retrieval creates
  a new version directory.
- **Preserve page markers** in extracted text so every quote is locatable.
- **Extraction:** PyMuPDF or pdfplumber. Low text yield → OCR (`ocrmypdf` /
  Tesseract) and set `ocr_applied`, which lowers `extraction_confidence`.
- **Record SHA-256** so any later check provably refers to the same file.
- Respect licences: store for local analysis; do not redistribute.

---

## 8. Stage 6 — Summarise (per-paper record)

Extraction (§9) pulls pre-specified values. Summarising produces a **structured
record of the whole paper**, so later questions can be answered without
re-reading, and relevance can be reassessed if the question shifts.

One record per included paper → `summaries.jsonl`.

```json
{
  "citation_key": "Author2021",
  "record_id": "W2755950973",
  "acquisition_status": "full_pdf_vor",
  "evidence_grade": "F",
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
  "screening_flag": null,
  "code_available": "github.com/...",
  "licence": "MIT",
  "summarised_by": "<model-id> v1.2"
}
```

**Rules**

- **Every `key_findings` entry carries a quote and locator.** Narrative fields
  may paraphrase; findings may not.
- **`relevance_grade`** ∈ `central` / `supporting` / `background` /
  `excluded-on-read`. A paper that passed abstract screening but proves
  irrelevant at full text is marked `excluded-on-read` here, with a reason, and
  counts as a full-text exclusion in the flow.
- **Author-stated limitations are recorded, not filtered.** Routinely the most
  useful sentences in a paper, and routinely lost in summarisation.
- **`evidence_grade` is inherited from `evidence_ceiling`**, never raised.
- **Never summarise from the abstract when full text is held**; and when only
  the abstract is held, the summary must not imply otherwise.

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
  "quote_char_offset": 18422,
  "evidence_grade": "F",
  "acquisition_status": "full_pdf_vor",
  "retrieved_from": "pdf_store/10.1038-s42256-021-00368-1/original.pdf",
  "file_sha256": "3f2a...",
  "extracted_by": "<model-id> v1.2",
  "rederivation_check": "pass",
  "extracted_date": "2026-09-24"
}
```

- Empty `source_quote` or `source_locator` → **build failure**, not a warning.
- `source_quote` must appear **verbatim** in `fulltext.txt`, verified by string
  match at write time, with the offset recorded. A non-matching quote is a
  fabrication and must fail loudly.

### 9.2 Evidence grades

| Grade | Meaning |
|---|---|
| **F** | Full text held and processed |
| **F⁻** | Full text, but preprint version only |
| **P** | Partial — abstract, or a table without surrounding text |
| **A** | Abstract only |
| **S** | Secondary — taken from another paper's report of it |
| **NR** | Not retrieved |

`S` must name the intermediary. `A`, `S` and `NR` may inform but may **never**
be the sole support for a headline claim.

### 9.3 Table extraction

Tables carry most quantitative claims and are the most common silent failure.

- Prefer **XML/JATS tables** (structured) over PDF table parsing (heuristic)
- Record `table_id`, caption, and the **full row/column headers** for each value
  — a number without its headers is uninterpretable
- Record the **units and direction** stated in the table (↑/↓, "lower is better")
- **Flag every PDF-parsed table** as lower confidence than an XML one
- Where a table cannot be parsed, record `NOT PARSED` rather than guessing

### 9.4 Blind re-derivation — the partial substitute for human checking

Since no human verifies extraction in v1, the strongest available automated
substitute:

1. A second pass sees **only the `source_quote`** — not the paper, not the
   surrounding text, not the original extraction.
2. It is asked to produce the value for that item from the quote alone.
3. If it cannot, or produces something different, `rederivation_check` = `fail`.

This enforces **quote sufficiency**: the quote must actually contain the value,
rather than merely sit near it. It catches the most common extraction error —
a quote that is real and adjacent but does not support the number attached to it.

**Run it on 100% of extracted values.** It is cheap and it is the only
correctness check available without a human.

**What it does not catch:** a quote that genuinely contains the value but whose
meaning depends on context that was not read — e.g. a number from a control
condition being recorded as the main result. Only a human reading the paper
catches that. Say so in the limitations.

---

## 10. Stage 8 — Appraisal

- **Per study:** design, sample size, data and code availability, licence,
  funding, declared conflicts, and a risk-of-bias assessment using an instrument
  appropriate to the field (RoB 2, ROBINS-I, QUADAS-2, CASP, or a stated rubric)
- **Per claim:** a confidence grade that may not exceed the weakest supporting
  source's `evidence_grade` — machine-enforced
- **In v1, appraisal is model-proposed and unreviewed.** Risk-of-bias judgement
  is interpretive; mark these `unverified` and treat them as provisional

---

## 11. Absence claims

"No one has done X" is often the most valuable finding and the most fragile.
Never assert it from keyword search alone.

1. **Forward citation sweep** — everything citing the canonical source for X
   (OpenAlex, free and complete)
2. **Screen that set** against the specific question
3. **State the boundary**: *"Of N works citing [Source] as of [date], none
   applies it to [context]"* — a checkable claim
4. If a sweep is infeasible, **downgrade the language** to what the search
   supports ("we found no…"), never an unqualified absence

In v1, add: **state that the sweep was screened by an unvalidated automated
screener.** An absence claim rests entirely on screening recall, and recall is
exactly what v1 cannot measure. This is the claim type most weakened by removing
human validation.

---

## 12. Phase C — Audit

A discrete pass producing `audit_report.md` — the document that answers "how do
you know?".

### 12.1 Consistency (Stage 9)

- **Re-derivation results** — pass/fail counts from §9.4, with every failure listed
- **Self-agreement** — screening stability, prompt sensitivity (§6.3)
- **Cross-source triangulation** — where two papers report the same quantity, do
  the extracted values agree? Disagreements are listed, not resolved
- **Internal contradiction scan** — claims in the synthesis that conflict with
  each other or with an extracted value

### 12.2 Coverage and acquisition profile (Stage 10)

Built directly from §7.2. The part most reviews omit: **quantify what was
missed**.

- **Acquisition breakdown** — count and share per `acquisition_status`
- **Evidence-grade distribution** — share of claims resting on F / F⁻ / P / A / S
- **Retrieval rate** — of records screened in, what share reached full text?
- **Unobtainable profile** — are failures concentrated by publisher, year,
  language, or venue? **Concentration means systematic bias**, and must be named
  rather than averaged away
- **Blocked-by breakdown** — paywall vs CAPTCHA vs network policy. These have
  different remedies, and the distinction tells you whether the gap is fixable
- **Preprint-only claims** — every value whose only source is `F⁻`
- **Supplementary gap** — papers whose SI was listed but not obtained
- **Retraction check** — confirm every record was checked; list any found
- **Single-source claims** — every conclusion resting on exactly one paper
- **`UNCERTAIN`-dependent claims** — every conclusion depending on a record the
  screener flagged

### 12.3 Gates (Stage 11)

All gates in §13, run as one pass, each reporting pass/fail plus offending rows.
A failing gate blocks the report. Not advisory.

### 12.4 Audit report contents

```
audit_report.md
├── Gate results                  pass/fail per gate, offending rows
├── Re-derivation                 pass rate, every failure listed
├── Screening consistency         stability, prompt agreement (NOT accuracy)
├── Acquisition breakdown         counts per status; retrieval rate
├── Evidence-grade distribution   share of claims by grade
├── Coverage bias                 unobtainable profile; blocked-by breakdown
├── Preprint-only claims          enumerated
├── Single-source claims          enumerated
├── UNCERTAIN-dependent claims    enumerated
├── Cross-source disagreements    enumerated, unresolved
├── Retractions                   checked / found
└── Limitations                   carried into the report verbatim
```

---

## 13. Quality gates

| Gate | Fails when |
|---|---|
| **G-PROTOCOL** | The frozen protocol hash changed without a logged amendment |
| **G-QUERY** | A record appears that no ledgered query could have produced |
| **G-QUOTE** | An extracted value lacks `source_quote` or `source_locator` |
| **G-VERBATIM** | A `source_quote` does not string-match the stored full text |
| **G-REDERIVE** | Re-derivation (§9.4) failed and the value was kept anyway |
| **G-GRADE** | A claim's confidence exceeds its `evidence_ceiling` |
| **G-CEILING** | An `evidence_ceiling` was set by hand rather than derived from acquisition status |
| **G-STATUS** | Any record lacks a terminal `acquisition_status` |
| **G-SECTION** | A claim cites a section the acquisition record says was not obtained |
| **G-RETRACT** | A record was not retraction-checked, or a retracted paper is included |
| **G-CITE** | A citation key does not resolve in the bibliography |
| **G-FLOW** | Flow counts do not reconcile: identified − duplicates − excluded = included |
| **G-ABSENCE** | An absence claim has no citation-sweep record |
| **G-CACHE** | A result cannot be reproduced from `raw_cache/` |

> **G-VERBATIM and G-REDERIVE are the two that matter most in v1.** Together
> they make fabricated and unsupported values structurally impossible — which is
> the strongest guarantee available without a human.

---

## 14. Reporting

- **Flow diagram** — identified / duplicates removed / screened / excluded with
  reasons / full text sought / obtained by status / included
- **Acquisition table** — the §12.2 breakdown, published in full
- **Search appendix** — every query verbatim, per source, with dates
- **Screening appendix** — model, prompt, settings, consistency statistics,
  explicitly labelled as consistency and not accuracy
- **Data availability** — publish the ledgers, acquisition record and extraction
  tables; they are the review's evidence

### 14.1 Mandatory limitations statement

Any output of a v1 run must state:

1. Screening was performed by a **single unvalidated automated screener**; recall
   is **unknown**; this **does not meet PRISMA**
2. Extraction was **not verified by a human** against source documents;
   automated checks confirm quotes are genuine and sufficient, **not that they
   were interpreted correctly**
3. Retrieval was **open-access-only**; the obtained set is **not a random sample**
   of the literature — with the §12.2 profile quantifying the skew
4. Risk-of-bias assessments are **model-proposed and unreviewed**

### On OA-only retrieval bias

Open-access-only retrieval skews by publisher, field, funder mandate and date.
State it, and quantify it from the acquisition record rather than asserting it
qualitatively.

---

## 15. Minimum viable build

| # | Component | Phase | Why here |
|---|---|---|---|
| 1 | Search ledger + raw cache | A | Everything depends on reproducible retrieval |
| 2 | Resolver ladder + **acquisition record** + PDF store | A | **Highest value per unit of effort**; caps every later claim |
| 3 | Extraction schema + **G-QUOTE** + **G-VERBATIM** | B | Makes fabricated values structurally impossible |
| 4 | Blind re-derivation + **G-REDERIVE** | B/C | The only correctness check available without a human |
| 5 | Summary records | B | Makes papers reusable without re-reading |
| 6 | Coverage/acquisition audit | C | Turns an unknown gap into a measured one |
| 7 | Screening + three-way routing | A | Scales to a large candidate set |
| 8 | Consistency statistics | C | Characterises the screener |
| 9 | Remaining gates + audit report | C | Makes the record defensible |
| 10 | Flow + report generation | C | Publication only |

**The ordering is deliberately not A → B → C.** Steps 1–6 give a trustworthy
small review immediately. Screening (7) is only worth building once the
candidate set is too large to process exhaustively.

> Build what makes a *small* review correct before what makes a *large* review
> feasible.

---

## 16. Where humans re-enter (v2) — designed in, not bolted on

v1 is fully automated, but the schema already carries the fields v2 needs. No
migration required.

| Insertion point | Field already present | What it unlocks |
|---|---|---|
| Screening validation sample | `screening_log.decision` | Sensitivity, specificity, κ — **PRISMA eligibility** |
| `UNCERTAIN` adjudication | `queued_manual` status | Removes the include-everything fallback |
| Extraction verification | `verified_by_human` *(add boolean)* | Catches misreading — the one thing automation cannot |
| Paywalled retrieval | `queued_manual`, `failure_history` | Closes the OA-only coverage gap |
| Appraisal review | `unverified` flag | Makes risk-of-bias defensible |
| Fuzzy-merge confirmation | dedupe flag | Removes silent merge risk |

**Cheapest first step toward v2:** a validation sample at screening. It is the
single change that converts "unknown recall" into a reported number, and it is
the gate most venues care about.

---

## 17. Honest limits

- **A hard paywall remains a hard paywall.** In v1 the ladder simply ends; the
  acquisition record makes the boundary visible and quantified.
- **One unvalidated LLM screener has unknown recall.** Not a PRISMA-compliant
  design, and it should not be described as one.
- **Verbatim matching prevents invention, not misreading.** §9.4 narrows the gap;
  only a human closes it.
- **Preprint-sourced values may not match the published record** — tracked as
  `F⁻`, never silently merged.
- **OA-only retrieval is a biased sample** — quantified in §12.2, not waved away.
- **This protocol is unexecuted.** No claim is made about its performance in
  practice.
