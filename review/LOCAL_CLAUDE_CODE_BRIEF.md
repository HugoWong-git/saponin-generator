# Brief for Local Claude Code — Saponin Stage-1 Literature Review

**Purpose:** you are taking over a literature review that has been through two
prior attempts. The evidence is already on this machine. Your job is to produce
a correct, fully-sourced review from it.

**Written:** 2026-09-26, by a cloud Claude Code session that audited both prior
attempts but could not access the PDFs.

---

## 0. Read these first

### 0.1 From the project repository

Clone or pull `HugoWong-git/saponin-generator`, branch
**`claude/busy-bell-14zrop`**. Read in this order:

| File | Why |
|---|---|
| `review/systematic_review_protocol_general.md` | **The protocol you must follow.** v2.0, fully automated, three phases |
| `review/h800_comparison_scorecard.md` | Every defect found in the previous attempt. Do not repeat them |
| `reports/corpus_and_prior_audit.md` | Measured facts about the actual corpus and trained model |
| `review/open_questions.md` | Q1–Q10; Q4a/Q4b closed, Q4d/Q4e are new measured defects |
| `review/literature_review_report.md` | The first attempt (Cycle 1). §7 recommendation, §8 risk register |
| `review/evaluation_protocol.csv` | 170 metrics with per-section published coverage |
| `review/published_reported_metrics.csv` | 314 transcribed published values |

### 0.2 From this machine

Paths as reported in the handover (verify them; they may have moved):

```
/code/ELTvLab/module0_utilities/LitReview/
  projects/saponin_prior_review/
    pdf_store/                  # 90 PDFs + fulltext.txt + meta.json, 263 MB
    pdf_store/quarantine/       # 17 false positives — KEEP, they are evidence
  lit_v2/
    acquisition_record.csv      # 191 rows — the single source of truth
    search_ledger.csv           # only 12 queries
    extraction.jsonl            # only 3 records
    candidates.json, coverage.json, consistency.json, flow.json
    fp_audit.json, arxiv_uncertain.json
  <pipeline>                    # acq_lib.py, lit_config.py, run_*.py, run_loop.sh
```

---

## 1. Project background

A **two-stage molecular generative model for saponins** — triterpenoid or
steroid aglycone cores bearing sugar (glycoside) moieties.

- **Stage 1**: an unconditional distribution-learning **prior** — learns what a
  saponin looks like.
- **Stage 2**: goal-directed fine-tuning (RL / transfer learning).

The prior's likelihood term stays **inside** the Stage 2 objective as a
regularising term, so the prior bounds what Stage 2 can produce. Stage 1 quality
is decisive, not preparatory.

**The review question:** should Stage 1 **adapt an existing published generative
model, or build a custom architecture** for this molecular class?

**Corpus:** `data/saponin_train_46k_valid.smi` in the repo — 45,966 SMILES.

---

## 2. Measured facts — use these, do not re-derive or contradict them

These were computed in the cloud session with RDKit 2026.3.6 and are recorded in
`reports/corpus_and_prior_audit.md`. They are **measurements, not inferences**,
and both prior review attempts were written without them.

### 2.1 The corpus is bimodal

| | Glycosides | Aglycones |
|---|---|---|
| Count | 18,654 (**40.58%**) | 27,312 (**59.42%**) |
| Mean MW | 987.7 | 515.1 |
| Mean rings | 8.2 | 5.0 |

The median molecule has **zero sugars**.

### 2.2 The corpus is stereochemically rich

87.5% carry a tetrahedral marker: 65.71% fully specified, 24.68% partial,
9.61% flat. Median 10 defined stereocentres, p95 33, max 67.

### 2.3 The trained prior has two measured defects

**Defect 1 — the 128-token cap is a glycoside-selective filter.**
`max_sequence_length = 128` appears in no config; inherited from
`reinvent_pubchem.prior`. **41.4% of glycosides exceed it, against 0.7% of
aglycones.** Sampling 10,000 molecules from the epoch-3 prior:

| | Training | Generated |
|---|---|---|
| Glycoside fraction | 40.58% | **23.38%** |
| Sugars/molecule | 1.27 | **0.38** |
| ≥4 sugars | 14.7% | **0.23%** |

**Defect 2 — the pipeline emits no stereochemistry.**
Zero of 8,858 valid generated molecules carry a stereocentre. The model assigns
mean probability **6.6 × 10⁻⁹** per step to the 18 stereo tokens in its own
vocabulary, decreasing from epoch 1 to epoch 4. Every sampling config sets
`isomeric_smiles = false`.

### 2.4 Validity reality check

This project's model: **86.97%** validity (published epoch report), 88.58% on an
independent reconstruction. Any recommendation that sets a validity gate above
this is wrong for this chemistry — see §4.3.

---

## 3. State of the evidence on disk

From the handover's own `COUNT_RECONCILIATION.md` and `ISSUES.md`. Verify before
relying on any of it.

| Thing | Count | Note |
|---|---|---|
| Ledger rows | 191 | `acquisition_record.csv` is the single source of truth |
| **Full text on disk** | **90** | 77 `full_pdf_vor` + 13 `full_pdf_preprint` |
| `metadata_only` | 86 | never retrieved |
| Quarantined false positives | 15 in ledger / **17 on disk** | 2 cross-field FPs re-marked |
| Orphan store dirs | 21 | pre-ledger partial attempts, no ledger row |
| `fulltext.txt` present | 92 | 2 extras with no PDF — see I-1 |
| Extraction records | **3** | the extraction step essentially did not run |
| Search queries logged | **12** | thin for a systematic review |

### 3.1 Known data hazards

- **I-7 — `file_path` is stale.** Points at `/code/ELTvLab/.../pdf_store/...` or
  older `/tmp/...`. **Reconcile by folder basename**, which is lossless for the
  90 full-text rows.
- **I-1 — 2 dirs hold `fulltext.txt` with no PDF** (`10.1038-s41573-023-00832-0`,
  `10.1038-s41587-023-01767-y`). Text came from an HTML pass. Their ledger rows
  say `metadata_only`, so ledger and disk disagree. Either re-fetch the PDF or
  drop the text — do not silently treat as full text.
- **27 manifest rows have `resolver_source: unknown`** (21 orphans + 6 full-text).
  Classify the 6 before relying on their provenance.
- **I-5 — 16 of 20 seeded arXiv IDs were mis-remembered; 13 targets remain
  unpinned.** See `arxiv_uncertain.json`.

### 3.2 Provenance

30 of the 90 PDFs were retrieved through a Sci-Hub backend (`sci.bban.top`) and
are labelled as such in `PROVENANCE_MANIFEST.csv`.

**Keep that provenance label on every row.** A publication-grade review must
state its retrieval routes in the methods section, so the label is needed
regardless of anything else. For any paper you still need, use the legitimate
ladder in protocol §7.1 — Unpaywall, Europe PMC, PMC author manuscripts,
preprint servers, institutional repositories, CORE, then author request or
interlibrary loan.

---

## 4. Known defects in the previous attempt — do not repeat these

Full detail in `review/h800_comparison_scorecard.md`.

### 4.1 Fabricated bibliographic data inside "verified" entries

Four entries tagged `[RETRIEVED]` ("full text on disk and title-verified") were
checked externally. **All four were wrong:**

| Work | Claimed | Actual |
|---|---|---|
| GCPN, arXiv 1806.02473 | authors "…Pritch, W. L., Wang, Z."; ICLR 2018 | You, Liu, Ying, **Pande, Leskovec**; **NeurIPS 2018** |
| GVAE, arXiv 1703.01925 | NeurIPS 2017 | **ICML 2017** |
| MolDiff, arXiv 2305.07508 | *"Multi-objective Molecular Graph Generation with Diffusion"*, 2020, filed as 2D | *"…Atom-Bond Inconsistency Problem in **3D** Molecule Diffusion Generation"*, **2023**, 3D method |
| DiffSBDD, arXiv 2210.13695 | "DiffSBDD/EDM", 2021 | Schneuing et al., **2022**; EDM is a **different paper** |

Also: GVAE attributed to "Jin, Barzilay, Jaakkola 2018" (it is Kusner et al.
2017; Jin et al. is JT-VAE), those two papers merged into one table row, and
"SELFIES-LM (Keller 2019)" cited with no support (SELFIES is Krenn et al. 2019).

### 4.2 The mechanism — and the gate it demands

MolDiff was tagged `ratio=1.0`, a perfect title match, **while the title printed
in the bibliography was not that paper's title.**

The gate confirmed *a file matching a title was downloaded*. The bibliography
entry was then **written from memory anyway.** Verification and written citation
were never bound together.

**Therefore, enforce this gate — it is mandatory, not optional:**

```
G-CITE-BIND   Every bibliographic field in a written citation — title,
              authors, year, venue, DOI — must be extracted from the
              stored PDF's own first page or from Crossref metadata for
              that exact DOI. Never generated from recall. A field that
              cannot be so extracted is left blank or marked unresolved,
              never filled in from memory.
```

Record, per field, which source it came from: `pdf_page1`, `crossref`,
`openalex`, or `unresolved`. If any field's source would be "recall", the entry
fails the gate.

### 4.3 Literature the previous attempt never cited

It cited **none** of these. Several are decisive.

| Work | Why it matters |
|---|---|
| **Skinnider 2021**, *Chemical language models enable navigation in sparsely populated chemical space*, Nat Mach Intell 3(9):759–770, DOI 10.1038/s42256-021-00368-1 | 8,447 models, >4 billion molecules. The largest systematic benchmark of which metrics track quality. Reports COCONUT-trained CLMs **never exceeding 82% validity at any training-set size including 500k** |
| **Skinnider 2024**, *Invalid SMILES are beneficial rather than detrimental to chemical language models*, Nat Mach Intell 6(4):437–448, DOI 10.1038/s42256-024-00821-x | Directly refutes the "validity by construction" argument for SELFIES. Also the SMILES-vs-SELFIES head-to-head |
| **Polykovskiy 2020** MOSES; **Brown 2019** GuacaMol | Benchmark size ceilings — 27 and 88 heavy atoms. Scores do not transfer to saponins |
| **Özçelik 2024** (S4 CLM); **Özçelik 2025** (library-size effects) | State-space CLMs; and that FCD/uniqueness move with library size so models swap ranks across scales |
| **Thomas 2024** MolScore; **Renz 2024** | SEDiv, outlier bits, #Circles |
| **Kim 2021** NPClassifier | Natural-product ontology with an `isglycoside` field |
| **Chandrasekhar 2025** COCONUT 2.0 | The natural-product corpus |

All are in `review/bibliography.md` with verified metadata. **Retrieve and read
these before writing §2 and §6 of the review.**

### 4.4 The consequential reasoning error

The previous attempt recommended **SELFIES** on validity-by-construction grounds
and set **"validity ≥95% as a hard pre-Stage-2 gate."**

That gate would reject this project's own model (86.97%) and every published
natural-product CLM. It is a drug-design default imported without checking
whether it transfers. Skinnider 2021 is the evidence that it does not.

**Do not inherit either conclusion. Re-derive the representation choice from
Skinnider 2021 and 2024, and set the validity target from natural-product
evidence.**

---

## 5. Tasks, in order

### Task 1 — Reconcile and audit the store (do this first)

1. Verify the 90 full-text rows against files on disk, matching by folder
   basename (per I-7).
2. Recompute SHA-256 for every PDF; compare against the manifest. Report
   mismatches.
3. Resolve I-1 (2 text-only dirs) and classify the 6 `unknown`-source full-text
   rows.
4. Confirm all 17 quarantine dirs are intact.
5. Check **every** record for retraction via Crossref `update-to`.
6. Write `store_audit.md`: what is on disk, what the ledger claims, every
   disagreement.

**Do not proceed until the ledger and the disk agree, or every disagreement is
documented.**

### Task 2 — Rebuild the bibliography under G-CITE-BIND

For each of the 90 full texts: extract title, authors, year, venue and DOI from
**page 1 of the PDF** and cross-check against Crossref for that DOI. Record the
source of each field. Flag every disagreement.

Expect to find more errors than the four in §4.1 — those were the only ones the
cloud session could check without the files.

Produce `bibliography_verified.md` with per-field provenance, and
`bibliography_errors.md` listing every correction made to the previous version.

### Task 3 — Retrieve the missing decisive literature

The papers in §4.3, plus the 86 `metadata_only` rows, prioritised by which
review claim depends on them. Use the §7.1 ladder. Record acquisition status per
protocol §7.2/7.3.

### Task 4 — Extract properly

Extraction produced only 3 records. Do it for real:

- Every value carries `source_quote` + `source_locator` + `quote_char_offset`
- **G-VERBATIM**: the quote must string-match the stored `fulltext.txt`
- **Blind re-derivation** (protocol §9.4) on 100% of values: a second pass sees
  only the quote and must reproduce the value from it alone
- Prefer XML/JATS tables over PDF table parsing; record table headers and units;
  mark PDF-parsed tables lower confidence
- `evidence_grade` derived from `acquisition_status`, never typed

### Task 5 — Per-paper summary records

Protocol §8. One record per included paper. Every `key_findings` entry carries a
quote and locator. Record author-stated limitations.

### Task 6 — Write the review

Ten sections, same structure as before (it is a good structure):

1. Recommendation · 2. Representation · 3. Model family assessment ·
4. Architecture and training · 5. Data requirements · 6. Evaluation metrics ·
7. Molecular-class-specific considerations · 8. Risks · 9. Open questions ·
10. Bibliography

**Requirements:**

- Cover **at least six** model families: RNN/LSTM CLMs; transformer/state-space
  CLMs; VAEs (string and graph); GANs; autoregressive/flow graph models;
  diffusion (2D and 3D).
- **Re-derive the representation choice** from Skinnider 2021/2024 rather than
  inheriting either prior conclusion.
- **Set the validity target from natural-product evidence**, not drug-design
  defaults.
- Use the §2 measured facts. The token-cap and stereochemistry defects are real,
  measured properties of the running model and belong in §7 and §8.
- Address the augmentation question with evidence: Skinnider 2021 reports the
  benefit attenuating at large training sets; the previous attempt recommended
  ×5–10 from Moret 2020. **Both papers are relevant and they pull in different
  directions at 46k. Resolve it explicitly rather than picking one.**

### Task 7 — Audit (protocol §12)

Produce `audit_report.md`: gate results, re-derivation pass rate, acquisition
breakdown, evidence-grade distribution, coverage and bias profile, preprint-only
claims, single-source claims, cross-source disagreements, retraction check.

---

## 6. Rules

1. **Never invent a citation.** If you recall a finding but not its source,
   write *"a result I believe exists but cannot attribute: <finding>"*. That is a
   correct answer. The previous attempt had **16 of 20 seeded arXiv IDs wrong**
   — memorised identifiers in this domain are unreliable.
2. **G-CITE-BIND on every bibliographic field** (§4.2).
3. **G-VERBATIM on every extracted value** — quote must match stored text.
4. **Evidence grade is derived from acquisition status, never asserted.**
5. **Keep provenance labels** on every row, including Sci-Hub-sourced ones.
6. **Do not edit the prior artefacts in place.** Write corrections as new files
   and keep the originals; the errors are evidence of how this went wrong.
7. **No human validation is assumed**, so state the limits the protocol requires:
   single unvalidated screener, unknown recall, no PRISMA compliance, extraction
   not human-verified. See protocol §14.1.
8. **Report what you could not do.** An honest gap beats a filled one.

---

## 7. Deliverables

| File | Contents |
|---|---|
| `store_audit.md` | Task 1 |
| `bibliography_verified.md` | Task 2, with per-field provenance |
| `bibliography_errors.md` | Every correction to the previous bibliography |
| `acquisition_record.csv` | Rebuilt, protocol §7.2 schema |
| `extraction.csv` | Task 4, every value quote-bound |
| `summaries.jsonl` | Task 5 |
| `SAPONIN_STAGE1_REVIEW_v5.md` | Task 6 |
| `audit_report.md` | Task 7 |

Commit to the `saponin-generator` repo on branch `claude/busy-bell-14zrop`, or a
branch from it, so the cloud session can review the result.

---

## 8. The one thing that matters most

The previous attempt was *diligent* — it built a real pipeline, retrieved 90 full
texts, and caught 17 of its own fabrications. It still produced a bibliography
with invented author names inside entries marked verified, and a recommendation
resting on literature it never read.

Both failures have the same cause: **the writing was not bound to the evidence.**

You have 90 papers on disk. Every sentence you write about any of them should be
traceable to a specific quote in a specific file. Where it cannot be, say so.
