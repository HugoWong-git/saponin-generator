# Reported Metrics — What Published Models Actually Say

**What this is.** A transcription of the metric values published models report, as printed in their sources. **Nothing here is computed by me.** Where a value could not be retrieved, the cell says so rather than being filled.

**Date:** 2026-09-23. Companion to `evaluation_protocol.md` v3.3 and `metric_coverage_gap_analysis.md`.
**Machine-readable version:** `reported_metrics.xlsx` — same content as 317 rows in tidy long format, one row per model-metric, filterable on section, dataset, model, metric, direction, source and confidence. Sheets: `README`, `All_Reported` (299), `Not_Retrieved` (9), `Meta_Findings` (9). Every numeric value in the workbook was round-trip verified against the tables below.

---

## How to read this

**Source confidence, marked on every block:**

| Mark | Meaning |
|---|---|
| **[PRIMARY-FULL]** | Results table fetched from the paper or publisher page this session, transcribed verbatim |
| **[PRIMARY-PARTIAL]** | From the paper, but via search excerpt rather than the full table |
| **[SECONDARY]** | From another paper's comparison table. The original authors may have reported differently |
| **[NOT RETRIEVED]** | Could not access. Left empty deliberately |

**Three warnings before using any number below.**

1. **Cross-paper comparison is mostly invalid.** Different datasets, sample sizes, RDKit versions and preprocessing. A validity of 0.98 on QM9 and 0.85 on GuacaMol are not on the same scale.
2. **Library size changes rankings.** [Ozcelik2025] showed FCD and uniqueness both move with sample size, and models swap places across scales. Sample sizes below are recorded where known — often they are not stated.
3. **None of these is a saponin number.** Every dataset here is drug-like or small-molecule. MOSES caps at 27 heavy atoms; QM9 at 9. Their absolute values carry no information about performance on your chemistry.

---

## 1. MOSES benchmark — baseline models  **[PRIMARY-FULL]**

Source: [Polykovskiy2020], Frontiers in Pharmacology 11:565644, full results tables fetched this session.
Dataset: ZINC Clean Leads, 4,591,276 molecules at source, MW 250–350 Da, **8–27 heavy atoms**. Values are mean ± SD over three independent initialisations.

### 1.1 Validity and uniqueness

| Model | Valid ↑ | Unique@1k ↑ | Unique@10k ↑ |
|---|---|---|---|
| *Train (reference)* | 1.0 | 1.0 | 1.0 |
| HMM | 0.076 ± 0.0322 | 0.623 ± 0.1224 | 0.5671 ± 0.1424 |
| NGram | 0.2376 ± 0.0025 | 0.974 ± 0.0108 | 0.9217 ± 0.0019 |
| Combinatorial | 1.0 ± 0.0 | 0.9983 ± 0.0015 | 0.9909 ± 0.0009 |
| CharRNN | 0.975 ± 0.026 | 1.0 ± 0.0 | 0.999 ± 0.0 |
| VAE | 0.977 ± 0.001 | 1.0 ± 0.0 | 0.998 ± 0.001 |
| AAE | 0.937 ± 0.034 | 1.0 ± 0.0 | 0.997 ± 0.002 |
| JTN-VAE | 1.0 ± 0.0 | 1.0 ± 0.0 | 0.9996 ± 0.0003 |
| LatentGAN | 0.897 ± 0.002 | 1.0 ± 0.0 | 0.997 ± 0.005 |

### 1.2 Filters, novelty, internal diversity

| Model | Filters ↑ | Novelty ↑ | IntDiv1 | IntDiv2 |
|---|---|---|---|---|
| *Train* | 1.0 | 0.0 | 0.857 | 0.851 |
| HMM | 0.9024 ± 0.0489 | 0.9994 ± 0.001 | 0.8466 ± 0.0403 | 0.8104 ± 0.0507 |
| NGram | 0.9582 ± 0.001 | 0.9694 ± 0.001 | 0.8738 ± 0.0002 | 0.8644 ± 0.0002 |
| Combinatorial | 0.9557 ± 0.0018 | 0.9878 ± 0.0008 | 0.8732 ± 0.0002 | 0.8666 ± 0.0002 |
| CharRNN | 0.994 ± 0.003 | 0.842 ± 0.051 | 0.856 ± 0.0 | 0.85 ± 0.0 |
| VAE | 0.997 ± 0.0 | 0.695 ± 0.007 | 0.856 ± 0.0 | 0.85 ± 0.0 |
| AAE | 0.996 ± 0.001 | 0.793 ± 0.028 | 0.856 ± 0.003 | 0.85 ± 0.003 |
| JTN-VAE | 0.976 ± 0.0016 | 0.9143 ± 0.0058 | 0.8551 ± 0.0034 | 0.8493 ± 0.0035 |
| LatentGAN | 0.973 ± 0.001 | 0.949 ± 0.001 | 0.857 ± 0.0 | 0.85 ± 0.0 |

### 1.3 FCD and SNN

| Model | FCD Test ↓ | FCD TestSF ↓ | SNN Test ↑ | SNN TestSF ↑ |
|---|---|---|---|---|
| *Train* | 0.008 | 0.476 | 0.642 | 0.586 |
| HMM | 24.4661 ± 2.5251 | 25.4312 ± 2.5599 | 0.3876 ± 0.0107 | 0.3795 ± 0.0107 |
| NGram | 5.5069 ± 0.1027 | 6.2306 ± 0.0966 | 0.5209 ± 0.001 | 0.4997 ± 0.0005 |
| Combinatorial | 4.2375 ± 0.037 | 4.5113 ± 0.0274 | 0.4514 ± 0.0003 | 0.4388 ± 0.0002 |
| CharRNN | 0.073 ± 0.025 | 0.52 ± 0.038 | 0.601 ± 0.021 | 0.565 ± 0.014 |
| VAE | 0.099 ± 0.013 | 0.567 ± 0.034 | 0.626 ± 0.0 | 0.578 ± 0.001 |
| AAE | 0.556 ± 0.203 | 1.057 ± 0.237 | 0.608 ± 0.004 | 0.568 ± 0.005 |
| JTN-VAE | 0.3954 ± 0.0234 | 0.9382 ± 0.0531 | 0.5477 ± 0.0076 | 0.5194 ± 0.007 |
| LatentGAN | 0.296 ± 0.021 | 0.824 ± 0.030 | 0.538 ± 0.001 | 0.514 ± 0.009 |

### 1.4 Fragment and scaffold similarity

| Model | Frag Test ↑ | Frag TestSF ↑ | Scaf Test ↑ | Scaf TestSF ↑ |
|---|---|---|---|---|
| *Train* | 1.0 | 0.999 | 0.991 | 0.0 |
| HMM | 0.5754 ± 0.1224 | 0.5681 ± 0.1218 | 0.2065 ± 0.0481 | 0.049 ± 0.018 |
| NGram | 0.9846 ± 0.0012 | 0.9815 ± 0.0012 | 0.5302 ± 0.0163 | 0.0977 ± 0.0142 |
| Combinatorial | 0.9912 ± 0.0004 | 0.9904 ± 0.0003 | 0.4445 ± 0.0056 | 0.0865 ± 0.0027 |
| CharRNN | 1.0 ± 0.0 | 0.998 ± 0.0 | 0.924 ± 0.006 | 0.11 ± 0.008 |
| VAE | 0.999 ± 0.0 | 0.998 ± 0.0 | 0.939 ± 0.002 | 0.059 ± 0.01 |
| AAE | 0.991 ± 0.005 | 0.99 ± 0.004 | 0.902 ± 0.037 | 0.079 ± 0.009 |
| JTN-VAE | 0.9965 ± 0.0003 | 0.9947 ± 0.0002 | 0.8964 ± 0.0039 | 0.1009 ± 0.0105 |
| LatentGAN | 0.999 ± 0.003 | 0.998 ± 0.003 | 0.886 ± 0.015 | 0.1 ± 0.006 |

**Two things worth noting for your own reporting.** The *Train* row is exactly the Tier 0 A↔B baseline the protocol asks for — MOSES publishes its own reference floor (FCD 0.008 on Test, 0.476 on TestSF), and that is the right model to copy. And *Scaf TestSF* for the training set is **0.0** by construction, which is a useful reminder that some metrics have a meaningful floor of zero rather than one.

---

## 2. GuacaMol benchmark — distribution learning  **[PRIMARY-PARTIAL]**

Source: [Brown2019], JCIM 59(3):1096–1108, Table 1. From a search excerpt of the paper rather than a fetched table.
Dataset: ChEMBL-24, 1,591,378 molecules, **2–88 heavy atoms**. 10,000 molecules sampled per benchmark.

| Benchmark | Random sampler | SMILES LSTM | Graph MCTS | AAE | ORGAN | VAE |
|---|---|---|---|---|---|---|
| Validity | 1.000 | 0.959 | 1.000 | 0.822 | 0.379 | 0.870 |
| Uniqueness | 0.997 | 1.000 | 1.000 | 1.000 | 0.841 | 0.999 |
| Novelty | 0.000 | 0.912 | 0.994 | 0.998 | 0.687 | 0.974 |
| KL divergence | 0.998 | 0.991 | 0.522 | 0.886 | 0.267 | 0.982 |
| FCD | 0.929 | 0.913 | 0.015 | 0.529 | 0.000 | 0.863 |

GuacaMol reports FCD as a **transformed score where higher is better** — the opposite direction to MOSES's raw FCD. The two are not interchangeable.

The *Random sampler* row is GuacaMol's equivalent of a reference ceiling: it scores 0.998 KL and 0.929 FCD with 0.000 novelty, because it samples real molecules.

---

## 3. 3D equivariant diffusion  **[PRIMARY-FULL]**

Source: [Xu2023] (GeoLDM), ICML 2023, Table 1 fetched this session. Includes [Hoogeboom2022] (EDM) as a compared method.

### 3.1 QM9 — 130k molecules, max 9 heavy atoms (29 with H); 100K/18K/13K split

| Method | Atom stability % | Mol stability % | Valid % | Valid & unique % |
|---|---|---|---|---|
| *Data (reference)* | 99.0 | 95.2 | 97.7 | 97.7 |
| ENF | 85.0 | 4.9 | 40.2 | 39.4 |
| G-SchNet | 95.7 | 68.1 | 85.5 | 80.3 |
| GDM | 97.0 | 63.2 | — | — |
| GDM-AUG | 97.6 | 71.6 | 90.4 | 89.5 |
| **EDM** | 98.7 | 82.0 | 91.9 | 90.7 |
| EDM-Bridge | 98.8 | 84.6 | 92.0 | 90.7 |
| GraphLDM | 97.2 | 70.5 | 83.6 | 82.7 |
| GraphLDM-AUG | 97.9 | 78.7 | 90.5 | 89.5 |
| **GeoLDM** | 98.9 ± 0.1 | 89.4 ± 0.5 | 93.8 ± 0.4 | 92.7 ± 0.5 |

### 3.2 GEOM-DRUGS — ~450,000 molecules, up to 181 atoms, **average 44.2**

| Method | Atom stability % | Valid % |
|---|---|---|
| *Data (reference)* | 86.5 | 99.9 |
| GDM | 75.0 | 90.8 |
| GDM-AUG | 77.7 | 91.8 |
| **EDM** | 81.3 | 92.6 |
| EDM-Bridge | 82.4 | 92.8 |
| GraphLDM | 76.2 | 97.2 |
| GraphLDM-AUG | 79.6 | 98.0 |
| **GeoLDM** | 84.4 | 99.3 |

**The omission is the finding.** The authors state molecule stability and uniqueness "are omitted since they are nearly 0% and 100% respectively for all the methods," because "DRUG molecules contain larger and more complex structures, creating errors during bond type prediction based on pair-wise atom types and distances."

Read directly: at an average of 44.2 atoms, **essentially no generated molecule is stable, for every method tested**. Saponins are larger than that average. This is the single most decision-relevant number in this document for ruling out 3D diffusion at Stage 1 — and it is a number the field reports by declining to report it.

---

## 4. 2D graph diffusion — DiGress  **[SECONDARY]**

Source: values as printed in the DeFoG paper's comparison table, **not** fetched from [Vignac2023] directly. The original may differ in precision or protocol.

| Benchmark | Valid ↑ | V.U. ↑ | V.U.N. ↑ | KL div ↑ | FCD ↑ | Unique ↑ | Novelty ↑ | Filters ↑ | FCD ↓ | SNN ↑ | Scaf ↑ |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **GuacaMol** — training set | 100.0 | 100.0 | 0.0 | 99.9 | 92.8 | — | — | — | — | — | — |
| **GuacaMol** — DiGress | 85.2 | 85.2 | 85.1 | 92.9 | 68.0 | — | — | — | — | — | — |
| **MOSES** — training set | 100.0 | — | — | — | — | 100.0 | 0.0 | 100.0 | 0.01 | 0.64 | 99.1 |
| **MOSES** — DiGress | 85.7 | — | — | — | — | 100.0 | 95.0 | 97.1 | 1.19 | 0.52 | 14.8 |

Note the scaffold similarity: **14.8 against a training-set reference of 99.1**. And DiGress's own text records that some complex GuacaMol molecules could not be mapped graph→SMILES for evaluation at all.

---

## 5. Natural-product models

| Model | Metric | Value | Source confidence |
|---|---|---|---|
| **NPGPT** (smiles-gpt fine-tuned on COCONUT) [Sakano2024] | FCD to NP distribution | **1.290** | **[PRIMARY-PARTIAL]** |
| **NPGPT** — LSTM baseline | FCD to NP distribution | **1.794** | **[PRIMARY-PARTIAL]** |
| **Low-data CLM** [Skinnider2021] | % valid, ZINC @1,000 molecules | **6.7%** | **[PRIMARY-FULL]** |
| | % valid, ZINC @25,000 | **69.1%** | **[PRIMARY-FULL]** |
| | % valid, **COCONUT, any training size** | **never exceeded 82%** | **[PRIMARY-FULL]** |
| | % unique, all models | **>99%** | **[PRIMARY-FULL]** |
| | Metrics with ρ ≥ 0.80 to training-set size | % valid, FCD, % stereocentres, Murcko scaffolds, NP-likeness | **[PRIMARY-FULL]** |
| | Models trained / molecules evaluated | 8,447 models; >4 billion molecules | **[PRIMARY-FULL]** |
| | Metabolome corpora | bacterial 15,292 · fungal 15,453 · **plant 21,993** | **[PRIMARY-FULL]** |
| **Moret low-data TL** [Moret2020] | Novel vs Enamine (700M) | **>99%** | **[PRIMARY-PARTIAL]** |
| | Novel-scaffold fraction during TL | **75% → >95%** | **[PRIMARY-PARTIAL]** |

**Skinnider's 23 metrics, as listed in the paper** — the widest published evaluation of a molecular generative model I verified:

% valid · % novel · % unique · internal diversity · external diversity · FCD · and Jensen–Shannon distances for 17 properties: aliphatic rings, aromatic rings, total rings, rotatable-bond fraction, sp³ carbon fraction, **stereocentre fraction**, atom-type proportions, Bertz TC, H-bond acceptors, H-bond donors, logP, Murcko scaffolds, molecular weight, NP-likeness, QED, SA score, TPSA.

That list is the field ceiling. **Stereocentre fraction is the only stereochemistry metric in it**, and it is aggregate.

---

## 6. Small focused datasets — the closest analogue to your regime  **[PRIMARY-PARTIAL]**

Source: [Subramanian2023], Table 1. Patent-derived focused datasets, GuacaMol distribution-learning suite.

| Metric | RNN + SELFIES | JT-VAE |
|---|---|---|
| Validity | ~1.0 | 1.0 |
| Uniqueness | ~0.99 | 1.0 / 0.99 |
| Novelty | 0.55–0.58 | **0.89–1.00** |
| KL divergence | **0.96–0.98** | 0.75–0.87 |
| FCD | **0.60–0.61** | 0.28–0.32 |

The most informative rows in this document for your project. On small, domain-focused data both models score far below the ~0.9 FCD typical of large drug datasets — and **the string model matched the distribution roughly twice as well while losing on novelty**. That is the trade-off you should expect.

---

## 7. Optimisation benchmarks

| Model | Metric | Value | Confidence |
|---|---|---|---|
| **REINVENT** [Gao2022] | PMO AUC top-10 | **14.016** (ranked **1st of 25 algorithms** across 23 tasks) | **[PRIMARY-FULL]** |
| Graph GA [Gao2022] | PMO rank | 2nd | **[PRIMARY-FULL]** |
| SMILES LSTM-HC [Gao2022] | PMO rank | 6th | **[PRIMARY-FULL]** |
| **Augmented Memory** [Guo2024] | PMO AUC top-10 | **15.002** (beats REINVENT on 14/23 tasks, 95% confidence) | **[PRIMARY-FULL]** |
| Augmented Memory [Guo2024] | Oracle calls to reach similarity 0.8 | **6,144** vs double-loop RL's 12,416 | **[PRIMARY-FULL]** |

PMO's AUC top-10 is min–max scaled to [0,1] per task over a 10,000-oracle-call budget, then summed across tasks — hence values above 1.

---

## 8. GAN

| Model | Metric | Value | Confidence |
|---|---|---|---|
| **MolGAN** [DeCao2018] | Validity (QM9) | 98–100% | **[PRIMARY-PARTIAL]** |
| | **Uniqueness** | **~2%** | **[PRIMARY-PARTIAL]** |
| | Novelty | >97% | **[PRIMARY-PARTIAL]** |
| | Training time vs ORGAN | ≥5× faster | **[PRIMARY-PARTIAL]** |
| **ORGAN** [Brown2019] | GuacaMol validity / KL / FCD | 0.379 / 0.267 / **0.000** | **[PRIMARY-PARTIAL]** |

The two GAN entries are the clearest failure signatures in this document — 2% uniqueness and a 0.000 FCD score respectively.

---

## 9. Meta-findings on the metrics themselves  **[PRIMARY-FULL]**

Not model results, but numbers that govern how the above should be read.

| Finding | Source |
|---|---|
| FCD and FDD **decrease with library size**, plateauing only above 10⁴–10⁵ designs; libraries rank differently by size | [Ozcelik2025] |
| **Uniqueness decreases as library size increases**, ranking models differently across scales — treat as a sanity check only | [Ozcelik2025] |
| Recommend reporting similarity metrics only for libraries of **≥10⁵ designs** | [Ozcelik2025] |
| Restrictive top-*k*/top-*p* causes mode collapse; temperature sampling superior for diversity | [Ozcelik2025] |
| "Number of substructures" is size-invariant and **~85× faster** than clustering | [Ozcelik2025] |
| Some property-distribution metrics **unstable below 100,000 samples** | [Skinnider2021] |
| SMILES beat SELFIES: Murcko-scaffold JSD p = 3.6 × 10⁻⁶; NP-likeness JSD p = 1.8 × 10⁻⁹; **stereocentre-fraction JSD p = 0.10 (not significant)** | [Skinnider2024] |
| 10× SMILES augmentation ≈ quadrupling unique training molecules; 30× let 5,000 molecules match 50,000 canonical | [Skinnider2021] |
| BioNavi-NP pathway success on real NPs | 90.2% of 368 compounds [Zheng2022] |

The [Skinnider2024] row is worth dwelling on: SMILES beat SELFIES decisively on scaffolds and NP-likeness, but **the stereocentre difference was not significant**. Representation choice is settled on other grounds — it does not solve stereochemistry.

---

## 10. Not retrieved

Recorded so the gaps are visible rather than silently absent.

| Model | Why |
|---|---|
| **MolGPT** [Bagal2022] | ACS returned HTTP 403. Reported as "on par with contemporaries" for validity/uniqueness/novelty on MOSES and GuacaMol, with conditional control of logP, TPSA, SA, QED — **no numbers retrieved** |
| **S4 CLM** [Ozcelik2024] | Metric tables not retrieved. Qualitative claims only: superior capacity on complex properties, diverse scaffolds, 8/10 prospective kinase designs predicted highly active |
| **REINVENT 4** [Loeffler2024] | Framework paper; per-task metrics only. One figure retrieved: PDK1 active-molecule rate 1.9% (RL) → 3.5% (TL+RL) |
| **JT-VAE** [Jin2018] | Original reconstruction-accuracy and property-optimisation numbers not retrieved. MOSES-reported JTN-VAE values are in §1 |
| **DiGress** [Vignac2023] | Values in §4 are secondary. Primary tables not fetched |
| **Ochiai large-molecule VAE** [Ochiai2023] | Abstract only — still the open Cycle-2 item |
| **NPClassifier** [Kim2021] | Per-class F1 and per-level category counts not retrieved (ACS 403, PMC CAPTCHA) |
| **RAscore** [Thakkar2021] | Comparison against SA score / SCScore not retrieved |
| **Tom stereochemistry work** [Tom2025] | Quantitative results not retrieved; scope statement was the relevant finding |

---

## 11. The one thing this whole record shows

Across every table above — nine MOSES baselines, six GuacaMol baselines, ten 3D methods, two focused-dataset models, four optimisation entries — **not one reported value describes a glycoside, a sugar, an anomeric centre, or a ring fusion.**

The single stereochemistry metric anywhere in this record is Skinnider's aggregate stereocentre fraction, and [Skinnider2024] found it was the one metric where SMILES did *not* significantly beat SELFIES.

That is the gap, stated in the field's own numbers.
