# HANDOFF — Saponin Generative Model, Stage 1 Prior Literature Review

**Project:** two-stage molecular generative model for saponins
**This document:** complete state of the literature review as of 2026-09-24
**Written for:** someone with zero prior context who needs to continue the work
**Working directory:** `/home/claude/saponin_review/`

---

## 0. Read this first — the two rules that govern everything here

These are not stylistic preferences. They were established through correction during the work and every artefact in this directory obeys them.

**Rule 1 — Every factual claim carries an inline citation key, and unverifiable claims are flagged rather than stated.**
A citation key was once *fabricated* in this project (see §7.1). The recovery discipline is now permanent: a machine checker (§5.4) runs against every document, and `bibliography.md` marks each entry `[VERIFIED]` or `[!] partial`. If you cannot verify an attribution, write the claim with the gap visible — never invent an author, year or venue to make a sentence look finished.

**Rule 2 — Nothing is computed that was not actually computed.**
`reported_metrics_record.md` and `reported_metrics.xlsx` are *transcriptions*. Where a table could not be retrieved, it is recorded as `NOT RETRIEVED`, not estimated. Published models have **not** been scored against this project's protocol, because that would require their weights and ≥100k generated molecules each. Reporting *coverage* was possible and was done; performance *scoring* was not and was refused. Preserve that distinction — it is the load-bearing honesty of the whole review.

---

## 1. Goal and scope

### 1.1 The project

A **two-stage molecular generative model for saponins** — triterpenoid or steroid aglycone cores bearing sugar moieties.

| Stage | Purpose |
|---|---|
| **Stage 1** | An unconditional distribution-learning **prior** — learns what a saponin looks like |
| **Stage 2** | Goal-directed fine-tuning (RL / transfer learning) toward design objectives |

**Why Stage 1 quality is decisive, not merely preparatory:** the prior's likelihood term stays *inside* the Stage 2 RL objective as a regularising term (the σ hyperparameter in REINVENT-style agents) [Guo2024]. The prior is not a starting point the optimiser leaves behind — it bounds what Stage 2 can produce. A weak prior cannot be fixed downstream.

### 1.2 What this review was asked to decide

**Adapt an existing model, or build a custom architecture for Stage 1?**

The review was scoped as a structured, citation-grounded, multi-cycle literature review covering **six model families**, against a stated minimum-coverage bar (§2.2) that had to be met before any recommendation could stop being provisional.

### 1.3 The corpus (as described, not yet inspected)

| Property | Value | Status |
|---|---|---|
| Size | **~40,000** triterpenoids and saponins | stated by user |
| Source | **TeroKit / TeroMOL** [Zeng2020, Chen2023] | stated by user |
| Wider terpenome available | ~180,000 total in TeroMOL; ~140k outside the pull | from source docs |
| Also inside TeroKit | **TeroENZ** — 13,462 enzymes, 4,293 reactions | from source docs |
| Aglycone : glycoside split | **UNKNOWN** | Q4a — gating |
| Stereochemistry retained? | **UNKNOWN** | Q4b — gating |

> **This matters more than any other open item.** An earlier revision of the corpus size (from "several hundred" to 40,000 — a 100× change) reversed two recommendations mid-review. The 40k figure, its glycoside fraction and its stereochemical completeness are all still unverified against the actual file. `audit_corpus.py` exists to measure all three and **has never been run** (§5.3).

---

## 2. Key decisions and inclusion/exclusion criteria

### 2.1 The headline recommendation

> **Adapt an existing SMILES chemical language model prior. Do not build a custom architecture for Stage 1.**
> — `literature_review_report.md` §7.1, marked **provisional** pending Cycle 2.

The recommended configuration:

1. **Representation:** isomeric SMILES, stereo descriptors retained. Not SELFIES, not graphs, not 3D.
2. **Three-stage curriculum**, each stage a legitimate stopping point:
   - *Stage 0, pretrain* — terpenome-wide TeroMOL (~180k), or COCONUT 2.0 (695k), or COCONUT→TeroMOL
   - *Stage 1, adapt* — the 40k triterpenoid + saponin set
   - *Stage 2, specialise* — the glycosylated subset only, if large enough to fine-tune without collapse
3. **Run the from-scratch baseline.** Same architecture, 40k only, no pretraining. **If it matches the pretrained model, prefer it** — a model trained only on in-domain data carries no drug-like bias to fight in Stage 2.
4. **Architecture:** 3-layer LSTM/GRU baseline [Skinnider2021]; S4 [Ozcelik2024] as primary challenger for long strings; decoder-only transformer [Bagal2022] third.
5. **Augmentation: sweep {1×, 2×, 3×, 5×, 10×} and expect the optimum to be LOW.**
6. **Evaluation:** the five well-behaved metrics plus SEDiv/outlier-bits plus a per-sugar composition histogram.

### 2.2 Minimum coverage bar (from the original brief)

No final recommendation until all are met:

| Category | Required | Covered | Status |
|---|---|---|---|
| SMILES / chemical language models | ≥3 | 7 | **Met** |
| Graph VAE / GAN | ≥2 | 2 in depth | **Nominally met, substantively weak** — see Q1, Q2 |
| Diffusion (2D + 3D) | ≥2 | 4 | **Met** |
| NP / saponin-specific | all findable | 4 + 1 unread | **[Zheng2019] still unread** — Q5 |

**The recommendation is provisional precisely because of row 2.** [Ochiai2023] is a VAE built specifically for *large, 3D-complex* molecules and is the single paper most likely to overturn a Cycle 1 conclusion. It has only been read at abstract level.

### 2.3 Decisions settled, with the evidence

| Decision | Resolution | Evidence |
|---|---|---|
| SMILES vs SELFIES | **SMILES** | [Skinnider2021], [Skinnider2024]; [Subramanian2023] shows the string model beating JT-VAE even handicapped with SELFIES |
| Minimum TL dataset size | **≥190 molecules** floor | [Amabilino2020]; [Moret2020] demonstrates TL from as few as 5 in the extreme |
| Which metrics to trust | Five well-behaved from [Skinnider2021] + SEDiv/outlier-bits [Thomas2024] | — |
| Uniqueness | **Not a ranking metric** — Tier 3 failure detector, reported as a *curve* | [Skinnider2021], [Renz2024], [Ozcelik2025] |
| Sphere-exclusion-diversity paper identity | **[Renz2024]** (Renz, Luukkonen & Klambauer) | corrected from a fabricated key — §7.1 |
| [SweetFold2026] authorship | **Sundar & Yang 2026**, bioRxiv 10.64898/2026.07.16.738959 | verified |

### 2.4 Exclusion criteria — what was ruled out and why

| Excluded | Reason |
|---|---|
| **3D equivariant diffusion** (EDM, GeoLDM, MolDiff) for Stage 1 | At GEOM-DRUGS' 44.2-atom average, molecule stability is **"nearly 0% for all the methods"** [Xu2023]. Saponins are larger. This is the strongest single piece of evidence in the review |
| **GANs** (MolGAN) | ~2% uniqueness — mode collapse — disqualifying for a diversity-maximising prior [DeCao2018] |
| **Graph VAEs** as the primary path | Designed for small molecules; stereochemistry is post-hoc RDKit enumeration, not learned [Jin2018]. *Provisional — see Q1* |
| **MOSES / GuacaMol benchmark SCORES** | MOSES caps at 27 heavy atoms, GuacaMol at 88; saponins exceed both. **Their metric CODE is reusable; their SCORES are not** |
| Custom architecture invention | Architecture variation almost never matched training-set size in effect, across 8,447 models [Skinnider2021] |

### 2.5 Where "build custom" still has a legitimate claim

Not a new architecture — but three custom *components*:

1. **A glycan-aware hybrid tokenizer** — aglycone as SMILES, glycosylation pattern as structured tokens. Principle demonstrated by [SweetFold2026]. **The single most defensible custom contribution available.**
2. **Anomeric-configuration validity metrics** — no published metric evaluates α/β correctness.
3. **A saponin-specific evaluation suite** — the project needs its own reference distributions because benchmark scores are not transferable.

---

## 3. Themes, papers and how they are categorized

`bibliography.md` / `bibliography.bib` hold **50 entries**, each with a per-entry verification status.

### 3.1 The six model families

| § | Family | Key papers | Verdict for Stage 1 |
|---|---|---|---|
| 3.1 | RNN/LSTM SMILES CLMs | [Skinnider2021], [Skinnider2024], [Moret2020], [Amabilino2020] | **RECOMMENDED** |
| 3.2 | Transformer & state-space CLMs | [Bagal2022] MolGPT, [Ozcelik2024] S4, [Loeffler2024] REINVENT 4 | **Strong challengers** |
| 3.3 | VAEs (SMILES + graph) | [Jin2018] JT-VAE, HierVAE, [Ochiai2023] | **Ruled out — provisionally** |
| 3.4 | GANs | [DeCao2018] MolGAN | **Ruled out** |
| 3.5 | Autoregressive / flow graph models | GraphINVENT [Mercado2020], GraphNVP | Not competitive here |
| 3.6 | Diffusion (2D + 3D) | [Vignac2023] DiGress, [Hoogeboom2022] EDM, [Xu2023] GeoLDM, [Peng2023] MolDiff | **Ruled out for Stage 1** |

### 3.2 Other categories in the bibliography

- **Benchmarks & metrics:** [Polykovskiy2020] MOSES, [Brown2019] GuacaMol, [Gao2022] PMO, [Thomas2024] MolScore, [Renz2024], [Ozcelik2025]
- **Natural-product-specific:** [Sakano2024] NPGPT, [Liu2025], [Merk2018], [Zheng2019] QBMG *(unread)*
- **Chemical ontology:** [Kim2021] NPClassifier — pathway / superclass / class + `isglycoside`; ClassyFire/ChemOnt
- **Biosynthesis:** [Zheng2022] BioNavi-NP (90.2% pathway success on 368 real NPs); TeroENZ
- **Databases:** [Zeng2020] / [Chen2023] TeroKit/TeroMOL, [Chandrasekhar2025] COCONUT 2.0
- **Glycoscience:** [SweetFold2026], [CarbCofolding2026] *(authorship unresolved — Q3)*
- **Stereochemistry:** [Tom2025] — the one paper dedicated to stereochemistry-aware generation
- **Optimisation / Stage 2:** [Guo2024] Augmented Memory, [Gao2022] PMO

### 3.3 The three cross-cutting findings

**a. Loss–quality divergence.** Validation NLL can improve while sample diversity degrades. Checkpoint selection on loss alone is unsafe.

**b. Library size can reverse model rankings** [Ozcelik2025]. FCD and FDD fall with library size (plateau above 10⁴–10⁵); uniqueness *falls as library size rises*. **Identical library size is a precondition of any comparison**, not a reporting detail.

**c. The stereochemistry ceiling.** [Tom2025] states current models "either ignore stereochemistry or consider it as a postprocessing step" — but **explicitly excludes axial chirality and ring isomers**. Ring-fusion stereochemistry (A/B, B/C, C/D junctions) is what defines a triterpenoid skeleton's shape, and it is *outside the stated scope of the state of the art*.

---

## 4. Open questions and unresolved disagreements

`open_questions.md` holds Q1–Q10 in full. Ordered by how much each could change the §7 recommendation.

### 4.1 Gating — the recommendation stays provisional until these close

| ID | Question | Why it could change the answer |
|---|---|---|
| **Q1** | Does [Ochiai2023] change the graph-VAE verdict? | A VAE built for large, 3D-complex molecules, motivated by the failure of JT-VAE/HierVAE on exactly that. If it handles saponin-sized stereochemistry-bearing molecules in low data, §7 needs a genuine second candidate |
| **Q2** | HierVAE / hgraph2graph on its own terms | Currently one table row from a README and a third-party description. Needs the primary paper. Tests the "motif vocabulary won't cover pyranose sugars" objection |
| **Q3** | Re-resolve [CarbCofolding2026] authorship | Citation integrity only — no effect on the decision, but R2 leans on it |
| **Q4a** | What is the aglycone : glycoside split in the 40k? | Aglycones teach ring systems, not glycosylation. If glycosides are a minority, Stage 2 may not be viable and glycosides must be up-weighted inside Stage 1 instead |
| **Q4b** | Does the TeroKit download preserve stereochemistry? | **The entire §5 argument — that SMILES is right *because* it represents stereochemistry natively — collapses if the corpus is flat** |

### 4.2 Non-gating but open

- **Q4c** — Is the wider terpenome worth using as Stage 0 pretraining, and which subset? (180k terpenome vs 695k COCONUT: more homogeneous but smaller)
- **Q5** — Does QBMG [Zheng2019] constitute prior art? Surfaced but unread
- **Q6** — Is there a released checkpoint for the [Skinnider2021] plant-metabolome model (21,993 molecules — conceptually the closest published model to saponin chemistry)?
- **Q7** — 2025–26 systematic surveys not yet read: [vanTilborg2024] is the most on-topic title found for the central question
- **Q8** — Is there *any* generative work on glycosides or glycoconjugates? Search glycans-as-molecules, glycosylation patterns on a fixed aglycone, cardiac glycosides, ginsenosides
- **Q9** — Does anyone evaluate anomeric configuration in generated structures? Currently absence-of-evidence
- **Q10** — S4 vs RNN sample efficiency at this data scale

### 4.3 Genuine disagreements in the literature

| Tension | Positions |
|---|---|
| **Does augmentation help?** | High factors help at small N, but **degrade** models from large training sets of structurally complex molecules, and the benefit is "attenuated completely" by 500k [Skinnider2021]. 40k sits exactly where this starts to bite. *Unresolved for this corpus — must be measured* |
| **Is uniqueness meaningful?** | Universally reported; two independent sources say it should not be used for ranking [Skinnider2021, Ozcelik2025]. **The two most-reported metrics in the field are the two that should not rank models** |
| **SMILES vs SELFIES on stereochemistry** | SMILES beats SELFIES decisively on scaffolds (p = 3.6 × 10⁻⁶) and NP-likeness (p = 1.8 × 10⁻⁹) — but **stereocentre-fraction JSD p = 0.10, not significant** [Skinnider2024]. Representation choice is settled on other grounds; *it does not solve stereochemistry* |

### 4.4 The weakest claim in the whole review

> The claim that **no published generative paper uses NPClassifier to evaluate generated molecules** rests on *not having found something* in a bounded search.

It is the strongest novelty claim available and it is the least verified. **A citation-graph check on [Kim2021] must close it before it is asserted in any write-up.** Same caution applies in weaker form to Q9.

---

## 5. What is done vs what is still needed

### 5.1 Deliverables that exist

| File | Size | What it is |
|---|---|---|
| `literature_review_report.md` | 58 KB | The main review. Master comparison table (21 entries), 6 family syntheses, 3 sub-question sections, §7 recommendation, §8 risk register R1–R13 |
| `bibliography.md` / `.bib` | 30 / 28 KB | 50 entries, per-entry verification status |
| `open_questions.md` | 11 KB | Q1–Q10, Cycle 2 agenda |
| `progress_log.md` | 40 KB | Newest-first changelog, 10 entries. **Read this for the reasoning behind any decision** |
| `evaluation_protocol.md` | 61 KB | **v3.3** — ~150 metrics across 19 sections, 28 gates, failure catalogue, §19A decision procedure |
| `metric_coverage_gap_analysis.md` | 19 KB | Which protocol metrics anyone has ever reported. Every row marked [F]/[P]/[A] by read depth |
| `reported_metrics_record.md` | 17 KB | Transcribed published values, 11 sections, source-confidence tagged |
| `reported_metrics.xlsx` | 28 KB | 317 rows, tidy long format, filterable. README + 3 data sheets |
| `audit_corpus.py` | 22 KB | Corpus profiler — **written but never executed** |
| `Saponin_Prior_Literature_Review.docx` | 53 KB | 30 pages, TOC, landscape section for the wide table |
| `Saponin_Prior_Literature_Review.pptx` | 335 KB | 12 slides |
| `Saponin_Evaluation_Gap.pptx` | 456 KB | 11 slides visualising the gap |
| `build_gap_deck.js` | 27 KB | Generator for the gap deck — rebuildable, not hand-edited |
| `gap_visualization.html` | 32 KB | The gap plates as a page (published artifact) |

### 5.2 The evaluation protocol in brief

**v3.3, ~150 metrics, 19 sections, 28 gates.** ID namespaces (all machine-checked for collisions): `D` corpus · `C` controls · `V` physical validity · `S1–S19` saponin-specific · `O` ontology · `A`/`B` synthesizability & biosynthesis · `F1–F10` training dynamics · `R1–R12` robustness · `T1–T12` tokenisation · `E` engineering · `GV` governance · `L`/`P` likelihood & optimisability · `Q` qualitative · `G0–G22+` gates.

It answers four questions the user raised explicitly: stereochemistry of generated output; does it contain sugar; subclass balance per NPClassifier; token length sufficient to generate a whole molecule untruncated (**context window = max × ~1.2, NOT p95** — p95 truncates the most-glycosylated 5%).

**The coverage result:** of ~150 metrics, published models collectively report **~25–30**. **Nine of nineteen sections have no published generative-model precedent at all:** physical validity, saponin-specific structure, chemical ontology, biosynthetic plausibility, NLL by subgroup, tokenisation diagnostics, engineering throughput, governance, and ring-fusion stereochemistry. The field ceiling is [Skinnider2021] at 23 metrics, covering three sections.

**Across 317 transcribed published values, not one describes a glycoside, a sugar, an anomeric centre, or a ring fusion.**

### 5.3 Known limitations — do not mistake these for completed work

| Limitation | Detail |
|---|---|
| **`audit_corpus.py` has never run against live RDKit** | `pip install rdkit` and `rdkit-pypi` both failed — the container's network is allowlisted to package registries and RDKit was unavailable. Pure-Python helpers were unit-tested via a stubbed import; **all chemistry paths are untested**. Treat it as a reviewed draft, not a validated tool |
| **The corpus has never been inspected** | Q4a and Q4b are unanswered. The 40k figure is from conversation |
| **[Ochiai2023] read at abstract level only** | Gating item Q1 |
| **HierVAE from a README** | Gating item Q2 |
| **[CarbCofolding2026] authorship unresolved** | ACS 403, PMC/PubMed CAPTCHA, Crossref/Europe PMC rate-limited |
| **MolGPT metrics not retrieved** | ACS 403. Recorded in §10 of the record, not paraphrased into numbers |
| **No published model has been scored on this protocol** | Deliberate — see Rule 2 |

### 5.4 The citation-integrity checker

Run this against every document before shipping anything. It currently reports **unresolved: NONE** across all five markdown files and the workbook's Source column.

> **Keep the scope at those five files.** `progress_log.md` is deliberately excluded: it records retired and corrected keys by name, including the fabricated `[Koch2024]` (§7.1), so running the checker over it reports an unresolved key that is *supposed* to be there. Adding it to the list produces a false positive — and "fixing" it would erase the record of the error. Verified 2026-09-24.

```python
import re
KEY = r'[A-Za-z][A-Za-z0-9]*\d{4}'
bib = open("bibliography.md").read()
defined = set(re.findall(r'\*\*\[(%s)\]\*\*' % KEY, bib))
for f in ("literature_review_report.md", "evaluation_protocol.md",
          "metric_coverage_gap_analysis.md", "reported_metrics_record.md",
          "open_questions.md"):
    doc = open(f).read()
    used = set()
    for g in re.findall(r'\[((?:%s)(?:\s*,\s*(?:%s))*)\]' % (KEY, KEY), doc):
        used.update(re.split(r'\s*,\s*', g))
    print(f, "unresolved:", sorted(used - defined) or "NONE")
```

### 5.5 What is still needed — in priority order

**Priority 1 — unblock the corpus (cheapest, highest information)**
1. Install RDKit; run `audit_corpus.py` against the TeroKit file
2. Read out Q4a (aglycone:glycoside split) and Q4b (stereochemistry completeness)
3. If largely flat, re-source stereochemistry via PubChem/ChEBI cross-reference by InChIKey, or revise the project's claims

**Priority 2 — close the gating literature items**
4. Read [Ochiai2023] in full → Q1
5. Obtain the HierVAE primary paper → Q2
6. Re-resolve [CarbCofolding2026] authorship → Q3
7. Read [Zheng2019] QBMG → Q5
8. Then **lift the "provisional" marker from §7, or revise it**

**Priority 3 — firm up the novelty claims**
9. Citation-graph check on [Kim2021] → §4.4. *The single most important verification remaining*
10. Search carbohydrate cheminformatics validation tooling for a reusable α/β check → Q9
11. Run the Q8 searches for any glycoside generative prior art

**Priority 4 — begin implementation**
12. Stand up REINVENT 4 (Apache 2.0); implement the three-stage curriculum **and the from-scratch control**
13. Implement the A↔B reference distribution — for nine protocol sections it is the *only* comparator that exists
14. Implement the S-series saponin metrics and the NPClassifier tier

---

## 6. Ready-to-use instruction for a new Claude Code session

**First, upload the working files.** This review was produced in a temporary cloud workspace that does not persist — a new session starts with an empty directory. Upload at minimum the nine working files (`HANDOFF.md`, `progress_log.md`, `open_questions.md`, `literature_review_report.md`, `bibliography.md`, `bibliography.bib`, `evaluation_protocol.md`, `metric_coverage_gap_analysis.md`, `reported_metrics_record.md`) plus `audit_corpus.py`. The Word, PowerPoint, xlsx and HTML files are rendered outputs for human readers and are not needed to continue the work — they can be regenerated from the markdown.

Then paste the block below.

---

```text
You are continuing a structured, citation-grounded literature review for a two-stage
molecular generative model for saponins (triterpenoid/steroid aglycones with sugars).
Stage 1 is an unconditional distribution-learning prior; Stage 2 is goal-directed
fine-tuning. The prior's likelihood stays inside the Stage 2 RL objective, so prior
quality bounds final output — Stage 1 is decisive, not preparatory.

The working files have been uploaded to this session. Work from them in place.

START BY READING, IN THIS ORDER:
  1. HANDOFF.md            — full context; read completely before doing anything
  2. progress_log.md       — newest-first; the reasoning behind every decision
  3. open_questions.md     — the Cycle 2 agenda, Q1-Q10
  4. literature_review_report.md §7 and §8 — the recommendation and risk register

TWO NON-NEGOTIABLE RULES:

  1. CITATION INTEGRITY. Every factual claim gets an inline citation key that
     resolves against bibliography.md. Never invent an author, year or venue.
     If you cannot verify an attribution, flag the gap in the text rather than
     filling it. A fabricated key occurred earlier in this project and was caught
     only by a machine check — run the checker in HANDOFF.md §5.4 before shipping
     any document.

  2. NEVER FABRICATE NUMBERS. reported_metrics_record.md and reported_metrics.xlsx
     are transcriptions of published values only. Where something could not be
     retrieved it says NOT RETRIEVED. Published models have NOT been scored against
     this project's evaluation protocol and must not be — that needs their weights
     and >=100k generated molecules each. Reporting coverage is possible; scoring
     performance is not. Preserve that distinction.

CURRENT STATE:
  - Recommendation: adapt an existing SMILES chemical language model; do not build
    a custom architecture. Marked PROVISIONAL pending the gating items below.
  - Corpus: ~40,000 triterpenoids/saponins from TeroKit. Described in conversation,
    NEVER INSPECTED.
  - evaluation_protocol.md v3.3: ~150 metrics, 19 sections, 28 gates. Published
    models collectively report ~25-30 of those metrics; nine of nineteen sections
    have no published precedent at all.

PRIORITY 1 — UNBLOCK THE CORPUS (do this first):
  Install RDKit, then run audit_corpus.py against the TeroKit file. The script was
  written against the RDKit API but HAS NEVER BEEN EXECUTED against live RDKit
  (the package was unavailable in the original container), so expect to debug it —
  its pure-Python helpers are unit-tested, its chemistry paths are not. It answers
  two gating questions:
    Q4a — the aglycone:glycoside split. Aglycones teach ring systems, not
          glycosylation. If glycosides are a small minority, Stage 2 may not be
          viable and they must be up-weighted inside Stage 1 instead.
    Q4b — whether the download preserved stereochemistry. The entire argument for
          choosing SMILES rests on native stereo representation; if the corpus is
          flat, that argument collapses and must be revised, not restated.
  Report what you find even if it contradicts the current recommendation.

PRIORITY 2 — CLOSE THE GATING LITERATURE ITEMS:
  Q1  Read [Ochiai2023] in full — a VAE built for large, 3D-complex molecules,
      motivated by the failure of JT-VAE/HierVAE on exactly that problem. It is
      the paper most likely to overturn a Cycle 1 conclusion and has only been
      read at abstract level. Extract: max molecule size, stereochemistry handling,
      low-data behaviour, licence, whether natural products were evaluated.
  Q2  Obtain the HierVAE primary paper (Jin, Barzilay & Jaakkola, ICML 2020 —
      VERIFY this attribution, it is currently unconfirmed).
  Q3  Re-resolve [CarbCofolding2026] authorship. Previously blocked by ACS 403,
      PMC/PubMed CAPTCHA and Crossref rate limits. The route that worked before
      was finding the paper cited with full authors in a later paper's reference list.
  Q5  Read [Zheng2019] QBMG and assess whether it is prior art.
  Then either lift the "provisional" marker from §7, or revise the recommendation.

PRIORITY 3 — THE WEAKEST CLAIM IN THE REVIEW:
  Run a citation-graph check on [Kim2021] (NPClassifier). The claim that no
  published generative paper uses NPClassifier to evaluate generated molecules is
  the strongest novelty claim available AND the least verified — it rests on not
  having found something in a bounded search. Absence of evidence in a bounded
  search is weaker than a systematic check. Close it or qualify it.

WORKING PRACTICE:
  - Append a dated entry to progress_log.md for every substantive change, newest
    first, recording what changed and why — including anything you got wrong.
  - Update open_questions.md as items close; keep resolved items for traceability.
  - Shell network access is allowlisted to package registries only. Use WebFetch
    and WebSearch for literature; do not retry blocked sites with curl.
  - Some publishers (ACS) return 403 and PMC serves CAPTCHAs. Alternative routes
    that worked: arXiv, bioRxiv, ML Anthology, escholarship, colab.ws, and other
    papers' reference lists. If a source stays blocked, say so — do not paraphrase
    an abstract into a number.
```

---

## 7. Appendix — errors made and corrected, for calibration

Recorded because a reader should know where this work has been wrong before.

### 7.1 The fabricated citation

A citation key **`Koch2024`** was invented — an author attribution that did not exist — for the sphere-exclusion-diversity paper. Verification identified the real authors as **Renz, Luukkonen & Klambauer 2024**, and four occurrences were corrected to `[Renz2024]`. It is logged in `progress_log.md` explicitly as "a fabricated attribution" rather than softened.

**Corollary, equally important:** a planned "cleanup" would have renamed two *correct* keys (`Subramanian2023`, `SweetFold2026`) to generic topic keys. Verification showed both were right, and the rename would have introduced new errors. **Verify before tidying.**

### 7.2 Substantive corrections

| Error | Correction |
|---|---|
| Corpus assumed "several hundred" | **40,000** — reversed the augmentation recommendation and un-forced transfer learning |
| Advised p95 for context-window sizing | **max × ~1.2** — p95 truncates the most-glycosylated 5%, exactly the molecules of interest |
| Uniqueness excluded entirely | Reinstated as a Tier 3 failure detector reported as a curve, after user pushback |
| NPClassifier omitted | Added as its own tier, after user pushback |
| §19A accounted for retraining-seed noise only | Added identical-library-size as a second, independent precondition [Ozcelik2025] |
| Governance IDs `G1–G7` collided with gate IDs `G0–G22` | Renamed to `GV1–GV7`; all 13 namespaces then machine-checked |
| Stale "several hundred" survived in the executive summary | Caught by the consistency checker after the §6/§7 rewrite |

### 7.3 User directions that shaped the work

- *"I will solely base it on our metrics for every model built"* → the protocol became a standalone standard and gained the §19A decision procedure
- *"All round please"* → 10 tiers expanded to 19 sections
- *"Tell me if you cannot do it"* → the refusal to score published models was stated plainly rather than worked around
- *"No need to compute anything"* → the transcription-only record

---

*End of handoff. Everything referenced is in `/home/claude/saponin_review/`.*
