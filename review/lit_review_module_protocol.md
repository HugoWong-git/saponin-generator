# Literature Review Module — Protocol

**Status:** draft for discussion, 2026-09-24. Not yet executed.
**Target rigour:** publication-grade systematic review (PRISMA 2020).
**Access model:** open-access retrieval, with human-mediated fallback for paywalled items.

This document is both the design spec for the module and, once agreed, the
**pre-specified protocol** the review runs under. For a publication-grade review
the protocol must be fixed *before* searching — that is the point of writing it
now rather than after.

---

## 1. Why this exists — the measured failure it addresses

The Cycle 1 review was curated ad hoc. Its citation integrity is strong; its
evidence depth is not, and the weakness is unevenly distributed.

| Measure | Result |
|---|---|
| Bibliographic metadata verified | 45 ✅ / 2 ⚠️ of 47 entries |
| Coverage assessments from **full text** | 16 of 42 (38%) |
| Coverage assessments from partial / abstract | 26 of 42 (**62%**) |
| Extracted values from a fetched primary table | 212 of 314 (67%) |
| Extracted values secondary / partial / unretrieved | 102 of 314 (**33%**) |
| Papers not retrieved at all | 9 |

**The missingness is systematic, not random.** Blockers named across the
documents: ACS HTTP 403 (×7), PMC/PubMed CAPTCHA (×12), Crossref / Europe PMC
rate-limiting (×6). ACS publishes *JCIM*, the core venue for this field, so the
gap is concentrated precisely where the relevant literature sits.

**Most of those were anti-bot defences on HTML pages, not paywalls.** The REST
APIs for the same corpora are free, keyless or email-keyed, and do not serve
CAPTCHAs. A large share of the 9 unretrieved and 49 partial entries is likely
recoverable with no subscription at all — by querying APIs rather than scraping
pages. That is the single biggest available improvement.

---

## 2. Prerequisite — network access

From the current cloud environment, all four scholarly APIs are **denied by the
environment's network policy** (not by the publishers):

```
api.openalex.org      connect_rejected
api.crossref.org      connect_rejected
api.unpaywall.org     connect_rejected
www.ebi.ac.uk         connect_rejected   (Europe PMC)
```

Add these hosts under Network access in the environment settings, or raise the
access level, before the module can run. Also worth allowing:
`api.semanticscholar.org`, `export.arxiv.org`, `api.biorxiv.org`,
`chemrxiv.org`, `pubchem.ncbi.nlm.nih.gov`.

**Without this the module cannot function**, and the review stays at Cycle 1's
retrieval quality regardless of how good the rest of the design is.

---

## 3. Architecture

Five stages, each writing an auditable artefact. Nothing downstream may assert
more than its upstream provenance supports.

```
[1] SEARCH      queries → candidate records        → search_ledger.csv
[2] SCREEN      title/abstract → include/exclude   → screening_log.csv
[3] RETRIEVE    resolver chain → full text or gap  → retrieval_log.csv
[4] EXTRACT     schema-enforced fields + quotes    → extraction.csv
[5] APPRAISE    per-study quality + confidence     → appraisal.csv
                                                   → prisma_flow.json
```

### 3.1 Search — reproducible by construction

Every query is recorded verbatim: source, query string, filters, date run,
result count. A query that is not in the ledger did not happen.

Sources, in priority order:

| Source | Cost | What it gives |
|---|---|---|
| **OpenAlex** | free, no key | 250M+ works, full citation graph, OA status |
| **Crossref** | free (polite pool, `mailto`) | authoritative metadata, reference lists |
| **Europe PMC** | free | full text for its OA subset, no CAPTCHA |
| **Semantic Scholar** | free, key optional | citation graph, open PDFs, TLDRs |
| **arXiv / bioRxiv / ChemRxiv** | free | preprints, often the only reachable version |
| **PubChem / PubMed** | free (E-utilities) | use the **API**, never the web interface |

Use the polite pool everywhere — send a `mailto` / User-Agent. The Cycle 1
rate-limiting was largely a consequence of anonymous requests.

### 3.2 Screen — the hard problem, stated plainly

**PRISMA 2020 expects two independent screeners with a reported agreement
statistic.** This project has one human reviewer and a model. That is *not*
equivalent, and it is the most likely reason a journal or examiner rejects the
review on methodological grounds.

Three honest options:

| Option | What it costs | Defensibility |
|---|---|---|
| **A. Two human screeners** | staff time across the whole candidate set | Full PRISMA compliance |
| **B. LLM-assisted, human-validated** (recommended) | staff screen a **random sample** (≥20%, ≥100 records), model screens all | Defensible **if** agreement is reported and the design is disclosed |
| **C. Single human screener** | least time | Discloseable limitation, but weakest |

**Option B in detail**, since it fits the access model:

1. The model screens every record against pre-specified criteria, emitting
   include/exclude **plus a reason** for each.
2. A human independently screens a random sample, blind to the model's call.
3. Compute **Cohen's κ** on that sample. Report it in the methods.
4. All disagreements are adjudicated by the human and the adjudications kept.
5. If κ is poor (< 0.6), the criteria are ambiguous — revise them and re-screen
   rather than proceeding.

This is a real methodological position with precedent, not a workaround — but
only when the validation sample and κ are actually reported. Skipping step 3
turns it into option C with extra steps.

**Your staff's time is better spent on the screening sample than on fetching
PDFs.** PDF retrieval is a bottleneck the module can queue and batch; screening
validation is the thing that makes the review publishable.

### 3.3 Retrieve — OA-first with a human fallback queue

A fixed ladder. The rung that succeeded is recorded per paper.

```
1. Unpaywall / OpenAlex OA location      → legal OA PDF
2. Europe PMC OA subset                  → full text XML (best for extraction)
3. Preprint server                       → arXiv / bioRxiv / ChemRxiv
4. Publisher landing page                → often abstract only; expect 403 on ACS
5. Reference list of a paper already held → the route that worked in Cycle 1
6. → MANUAL QUEUE                        → your staff
```

Rung 6 is a first-class state, not a failure. `retrieval_log.csv` tracks each
item through `pending_manual → requested → received → extracted`, with a
`drop/` folder the module watches for deposited PDFs. The queue is exported as
a simple worklist (title, DOI, why it's needed, which claim depends on it) so a
batch can be actioned in one sitting and prioritised by **what it would change**
— an abstract-only paper gating a recommendation outranks one supporting a
settled point.

### 3.4 Extract — provenance as a schema constraint

The core anti-fabrication mechanism, and the reason this is a module rather
than a checklist.

**A numeric value cannot be written without the text it came from.**

```json
{
  "citation_key": "Skinnider2021",
  "metric": "validity",
  "value": "0.82",
  "units": "fraction",
  "dataset": "COCONUT",
  "n_sampled": 100000,
  "source_quote": "never exceeded 82% at any training set size",
  "source_locator": "Results, para 4",
  "evidence_grade": "F",
  "retrieved_from": "europepmc_oa_xml",
  "retrieved_date": "2026-09-24"
}
```

A missing or empty `source_quote` is a **schema violation that fails the
build** — not a warning. This project has had one fabricated citation key; the
lesson taken was a machine check, and this extends that check from citation
keys to every number.

`evidence_grade` carries the Cycle 1 convention forward: `F` full text, `P`
partial, `A` abstract, `S` secondary (another paper's table), `NR` not
retrieved.

### 3.5 Appraise — quality and confidence

Per included study: study type, dataset(s), sample sizes, whether code and
weights are available, licence, and any conflict of interest. Per synthesised
claim: a confidence grade that **may not exceed the weakest supporting
source's `evidence_grade`** — machine-enforced.

---

## 4. Absence claims need their own procedure

The weakest claim in the current review — *no published generative paper uses
NPClassifier to evaluate generated molecules* — is also its strongest novelty
claim. It rests on not finding something in a bounded search.

An absence claim is only publishable if the boundary is stated. Procedure:

1. **Forward citation sweep.** Retrieve everything citing the seed paper via
   OpenAlex (free, complete). For [Kim2021] this is tractable and decisive.
2. **Screen that set** against the specific question.
3. **Report the boundary**: "Of N works citing [Kim2021] as of *date*, none
   applies it to generated molecules" — a checkable statement.
4. Where a sweep is not feasible, **downgrade the claim's language** to what the
   search supports, rather than asserting absence.

Apply the same to: anomeric-configuration evaluation (Q9), glycoside generative
prior art (Q8), and biosynthetic plausibility of generated molecules.

---

## 5. Machine checks (CI gates)

Each must pass before any document ships. All are cheap; all catch a failure
that has already happened in this project or is likely to.

| Gate | Fails when |
|---|---|
| **G-CITE** | A citation key in any document does not resolve in `bibliography.md`. *Scope: the five canonical files — `progress_log.md` is excluded, it deliberately names retired keys.* |
| **G-QUOTE** | Any extracted value lacks `source_quote` or `source_locator` |
| **G-GRADE** | A claim's confidence exceeds its weakest source's `evidence_grade` |
| **G-PRISMA** | Flow counts don't reconcile: identified − duplicates − excluded ≠ included |
| **G-QUERY** | A result appears that no ledgered query could have produced |
| **G-ABSENCE** | An absence claim has no citation-sweep record backing it |
| **G-STALE** | A retrieval is older than the review's cutoff date without recheck |

---

## 6. Build order

Highest information per unit of effort first.

1. **Unblock the network** (§2). Nothing else works without it.
2. **Retrieval ladder + manual queue** (§3.3). Re-run against the existing 47
   entries and the 9 not-retrieved. This alone may close much of the 33% gap,
   and it validates the whole approach before any new searching.
3. **Extraction schema + G-QUOTE** (§3.4). Backfill the 314 existing rows;
   anything that cannot be given a `source_quote` is downgraded or dropped.
4. **Citation sweep for the absence claims** (§4). Closes the review's weakest
   and most valuable claim.
5. **Search ledger + PRISMA flow** (§3.1). Needed for publication; not needed to
   improve accuracy, so it follows the things that do.
6. **Screening protocol + κ validation** (§3.2). Requires staff time — schedule
   it deliberately rather than opportunistically.

Steps 2–4 improve the *existing* review. Steps 5–6 are what make it
publication-grade. They are separable, and 2–4 are worth doing regardless of
whether the review is ever published.

---

## 7. What this does not fix

- **A hard paywall is still a hard paywall.** For genuinely closed items with no
  OA copy and no preprint, the ladder ends at your staff. The module makes that
  boundary visible and prioritised; it does not remove it.
- **LLM-assisted screening is not two human screeners.** §3.2 makes it
  defensible, not equivalent. Some venues will still object, and that should be
  established before the work is done rather than after.
- **Secondary values stay secondary.** Re-reading DiGress's own tables would
  reclassify the 44 SECONDARY rows; nothing short of that will.
- **This protocol is unexecuted.** Every number in §1 is measured; nothing in
  §3–6 has been run.
