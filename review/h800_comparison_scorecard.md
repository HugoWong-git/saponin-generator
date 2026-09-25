# H800 Independent Review — Comparison Scorecard

**Date:** 2026-09-25
**Subject:** `stage1_literature_review.zip` (H800 run, v4, 2026-09-25)
**Scored against:** `h800_independent_review_prompt.md` Part 2

---

## 0. The run was not blind

The comparison was designed as a blind replication. It was not run blind.

| Given | Evidence |
|---|---|
| **Part 1 prompt** | Exact 10 section headings; `## Access statement (Rule 1)`; the four citation tags |
| **v2 protocol** | Its subtitle names `systematic_review_protocol_general.md v2.0`; `acquisition_record.csv` reproduces 28 fields of the §7.2 schema and uses the status vocabulary (`full_pdf_vor` 77, `full_pdf_preprint` 13, `metadata_only` 86) |
| **A separate user brief** | The README maps to sections (a)–(i), which appear in no document of ours |

It also **extended** the protocol on its own: §7.1b/c route definitions, a §12.5 false-positive audit, a §12.6 runbook, a `quarantined_fp` status, and a `G-WRONG-ITEM` gate built from our `failed_wrong_item` state. Those extensions are sound and worth adopting.

**Consequence:** this tests the protocol, not independent judgement. Agreement on conclusions carries little evidential weight. **Disagreement still carries full weight**, and there is a significant one (§B).

---

## A. Citation integrity — the headline result

### A.1 What its own audit caught

The run quarantined **17 false positives**. Its memorised arXiv IDs resolved to papers in unrelated fields — Brownian-motion mathematics, plasma physics, Bernoulli numbers, electricity-price forecasting, federated learning for autonomous driving, Ising/Apollonian networks, trajectory prediction.

By its own count: **14 of 24 memorised arXiv IDs were wrong** (§9 item 8); R8 states 7 of 14 initially-used IDs were mis-mapped.

**This is the predicted failure mode, confirmed, and caught by download-and-verify.** Without that step, 17 authoritative-looking fabricated citations would be in the bibliography. The protocol's retrieval-then-verify design is vindicated.

### A.2 What its audit did *not* catch — the more important finding

Four `[RETRIEVED]` entries were verified against external sources. `[RETRIEVED]` is its strongest tag, defined as *"full text on disk and title-verified (G-WRONG-ITEM)"*.

**All four carry metadata errors.**

| Work | Its claim | Verified | Error |
|---|---|---|---|
| **GCPN** arXiv 1806.02473 | "You, J., Liu, B., Ying, R., **Pritch, W. L., Wang, Z.**" — ICLR 2018 | You, Liu, Ying, **Vijay Pande, Jure Leskovec** — NeurIPS 2018 | **2 fabricated author names** + wrong venue |
| **GVAE** arXiv 1703.01925 | NeurIPS 2017 | **ICML 2017** (34th ICML) | Wrong venue; authors correct |
| **MolDiff** arXiv 2305.07508 | *"MolDiff: **Multi-objective Molecular Graph Generation with Diffusion**"*, 2020, filed under **2D graph** | *"MolDiff: **Addressing the Atom-Bond Inconsistency Problem in 3D Molecule Diffusion Generation**"*, **2023**, a **3D** method | **Fabricated title**, wrong year, wrong family |
| **DiffSBDD** arXiv 2210.13695 | "DiffSBDD/**EDM**", 2021 | Schneuing et al., **2022**; EDM is a **different paper** | Wrong year; two papers conflated |

### A.3 The mechanism — verification and citation are decoupled

MolDiff is tagged **`ratio=1.0`**, a perfect title match — yet the title printed in the bibliography is not that paper's title.

The gate confirmed *a file matching a title was downloaded*. The bibliography entry was then **written from memory anyway**. The check and the written claim were never bound to each other.

> This is the "quote accurate, meaning wrong" gap from protocol §0.1, appearing in a sharper form: **file correct, description fabricated.**
>
> It is not caught by G-WRONG-ITEM, and it would not be caught by G-VERBATIM either, since no quote is involved.

**Additional attribution errors, internal to the text:**

- §3 attributes **GVAE to "Jin, Barzilay, Jaakkola 2018"**. GVAE is Kusner et al. 2017; Jin et al. is JT-VAE. The row then cites "JT-VAE/GVAE arXiv 1802.04364" as a single work — **two distinct papers and two distinct families merged into one row**.
- §3 lists **"SELFIES-LM (Keller 2019)"** as representative work. SELFIES is Krenn et al. 2019. No support is offered for "Keller".

### A.4 Scores

| Metric | Result |
|---|---|
| Verifiable `[RETRIEVED]` entries checked | 4 |
| **Metadata error rate on checked `[RETRIEVED]`** | **4 / 4 (100%)** |
| Fabricated author names | 2 (GCPN) |
| Fabricated titles | 1 (MolDiff) |
| arXiv IDs correct on checked items | 4 / 4 — **the identifiers are right; the prose about them is not** |
| Self-caught fabrications | 17 quarantined |
| **Honest abstentions** | **11 `[UNCERTAIN]` + explicit "not verifiable this session"** — good |

**Calibration:** the tags do partly track truth — `[UNCERTAIN]` items are genuinely unverified, and it declined to claim MolGAN, GFlowNet, TANKRD and MoleculeACE. That is real, creditable honesty. But `[RETRIEVED]` does **not** mean what it says: it means *a file is on disk*, not *this description is accurate*.

---

## B. Substantive comparison

| Dimension | Ours | H800 | Agree? |
|---|---|---|---|
| Adapt vs build | Adapt | Adapt | ✅ |
| Representation | **SMILES** | **SELFIES** | ❌ **Major** |
| Validity target | **~80–85%** | **≥95%, as a hard gate** | ❌ **Major** |
| Augmentation | Sweep, expect a **low** optimum | **×5–10** | ❌ |
| Diffusion for Stage 1 | Ruled out | "Strong candidate" (2D) | ❌ |
| GAN | Ruled out | Not recommended | ✅ |
| Graph VAE | Ruled out (provisionally) | "Strong candidate" | ❌ |
| 46k sufficient | Yes | Yes | ✅ |
| Uniqueness as quality metric | No | "Weak alone" | ✅ |
| Saponin-specific suite needed | Yes | Yes | ✅ |
| Aglycone→glycan curriculum | Yes | Yes | ✅ |

### B.1 The SELFIES vs SMILES disagreement is resolvable

It cites **none** of the empirical literature that decides this question:

| Work | Cited by H800 |
|---|---|
| Skinnider 2021 (8,447 models) | ❌ |
| Skinnider 2024 (*Invalid SMILES are beneficial…*) | ❌ |
| Polykovskiy / MOSES | ❌ |
| Özçelik (S4, and the 2025 library-size work) | ❌ |
| Thomas / MolScore | ❌ |
| Renz | ❌ |
| NPClassifier | ❌ |
| COCONUT | ❌ |

Its entire SELFIES case rests on **validity-by-construction**. That is precisely the argument Skinnider 2024 sets out to refute — invalid SMILES are reported as *beneficial rather than detrimental*, because invalid strings are sampled at lower likelihood and post-hoc filtering acts as a free quality filter.

Our position also rests on Skinnider 2024's head-to-head: SMILES beat SELFIES on Murcko scaffolds (p = 3.6 × 10⁻⁶) and NP-likeness (p = 1.8 × 10⁻⁹).

**H800 did not weigh that evidence against its position. It never saw it.** This is a coverage failure, not a reasoning failure — and it is the single most consequential gap in its review.

### B.2 The ≥95% validity gate would fail every natural-product CLM

It sets **"validity ≥95% as a hard pre-Stage-2 gate"**.

Skinnider 2021 reports COCONUT-trained chemical language models never exceeding **82%** validity at *any* training-set size, including 500k. Our own epoch report measures **86.97%** on this project's actual model.

Applying H800's gate would reject the working model, and every published natural-product CLM. It is a drug-design default imported without checking whether it transfers — rubric failure mode **D1**, confirmed.

---

## C. Independent-discovery checks

| # | Finding | Weight | Result |
|---|---|---|---|
| 1 | Sequence length / context-window truncation | ⭐⭐⭐ | ❌ **Miss.** Zero occurrences of "truncat" or "sequence length" anywhere |
| 2 | Aglycone vs glycoside imbalance | ⭐⭐⭐ | 🟡 **Partial.** R4 flags corpus redundancy; Q1 asks for scaffold diversity; the aglycone→glycan curriculum implies awareness — but the split is never identified as the risk |
| 3 | Stereochemistry decisive | ⭐⭐⭐ | ✅ **Hit.** §7.3, R2, and Q2 — *"How much of the 46k has defined stereochemistry in its SMILES?"* is essentially our Q4b, reached independently |
| 4 | 3D diffusion fails at this size | ⭐⭐ | ❌ **Miss.** Calls 3D "Best" for stereochemistry; no stability-collapse caveat |
| 5 | Uniqueness not a quality metric | ⭐⭐ | ✅ Hit |
| 6 | FCD miscalibrated for this chemistry | ⭐⭐ | 🟡 Partial — flags descriptor dependence, not ChemNet calibration |
| 7 | Benchmark size ceilings don't transfer | ⭐⭐ | ✅ Hit (§7.2) |
| 8 | High augmentation may hurt | ⭐ | ❌ **Inverted** — recommends ×5–10 |
| 9 | Sugar identity is a stereochemical distinction | ⭐⭐ | ❌ Miss — mentions α/β, not monosaccharide identity |
| 10 | No published suite evaluates glycosylation | ⭐⭐ | ✅ Hit |

**Score: 4 hits, 2 partial, 4 miss (one inverted).**

The ⭐⭐⭐ stereochemistry hit is genuine and well-argued. The ⭐⭐⭐ sequence-length miss is the one that matters most — it is the defect actually present in the running model.

---

## D. Where it is better than ours

Stated plainly, because it is.

1. **It built the acquisition pipeline and ran it.** 191 records, 90 full texts, SHA-256 and provenance per file. Ours is a specification; theirs executes.
2. **G-WRONG-ITEM is a real contribution.** We defined `failed_wrong_item` as a status; it turned it into an enforced gate and caught 17 fabrications with it. **Adopt this.**
3. **The false-positive quarantine as a first-class state** is better than our design, which had no explicit home for a retrieved-but-wrong file.
4. **Moret 2020 extracted in detail** — 365,063-molecule pretrain, transfer sets as small as 5, first-layer freezing, the ×10 augmentation / T=0.7 table. Concrete numbers with a real source; better than our treatment of the same paper.
5. **Honest about not inspecting the corpus** — every corpus claim explicitly marked inference.

---

## E. Verdict for the pipeline

| Question | Answer |
|---|---|
| Can it retrieve and manage a corpus? | **Yes** — demonstrably, 191 records with provenance |
| Can it screen? | **Probably** — with the inclusion bias wide, as specified |
| Can it supply citations from memory? | **No.** 14 of 24 IDs wrong by its own count; 4/4 checked descriptions wrong |
| Can it write a bibliography entry from a verified file? | **No — not yet.** This is the decoupling in §A.3 |
| Can it reason about the domain? | **Partly.** Strong on stereochemistry and modularity; missed sequence length; inverted on augmentation |

### E.1 The protocol change this demands

**A new gate — bind the written citation to the file, not to a memory of it.**

```
G-CITE-BIND   Every bibliographic field in a written citation
              (title, authors, year, venue) must be extracted from
              the stored PDF's own first page / metadata,
              not generated. A field that cannot be so extracted
              is left blank, never filled from recall.
```

G-WRONG-ITEM checks *the right file arrived*. G-CITE-BIND checks *what we wrote about it came from the file*. The H800 run passes the first and fails the second, and that is exactly how two fabricated author names survived into a `[RETRIEVED]` entry.

---

## F. Two things to deal with before any of this is used

1. **Sci-Hub.** 30 of the PDFs came from `sci.bban.top`, self-described as a community Sci-Hub backend; the README requests a residential proxy for 47 more. Those rows cannot be disclosed in a methods section. Re-source via author email, ILL or document delivery before anything is written up.
2. **Internal inconsistency.** README reports 31 references tagged 24/5/2; `reference_list.txt` carries 66 tags (49/11/5/1). The access statement says 81 verified full texts; the README says 90. These do not reconcile — and a coverage number that moves between files is exactly what the audit phase exists to catch.
