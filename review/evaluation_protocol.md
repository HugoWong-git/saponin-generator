# Stage 1 Prior — Full-Scope Evaluation Protocol

**Purpose.** Everything that should be considered when judging whether the Stage 1 prior is fit to be the foundation of the saponin generator. Organised as a reference, not a checklist to complete in order — take what each decision needs.

**Version 3.3 — 2026-09-23.** Supersedes v3.1, v3.0, v2.0, v1.0. Changelog in §23.
**Companion to** `literature_review_report.md`. Citation keys resolve against `bibliography.md`.

**On implementability.** Several tiers name tools this environment could not run. Where a claim rests on something unverified, it says so inline. Nothing here is gated on my being able to execute it.

---

## Contents

**Part I — Before you train**
1. Framing — why a prior is judged differently
2. Corpus readiness and data quality
3. Experimental design: splits, baselines, controls, pre-registration

**Part II — Does it produce real saponins?**
4. Core distribution learning (the five validated metrics)
5. Chemical and physical validity beyond parsing
6. Saponin-specific structural metrics
7. Chemical ontology classification
8. Property distributions
9. Synthesizability and biosynthetic plausibility

**Part III — Does it cover the space, honestly?**
10. Coverage and diversity
11. Failure detectors
12. Memorisation, novelty and leakage

**Part IV — Is it a good prior for Stage 2?**
13. Likelihood and calibration
14. Optimisability
15. Robustness and sampling behaviour

**Part V — The model as an artefact**
16. Tokenisation and sequence diagnostics
17. Engineering and operational
18. Governance, licensing and reproducibility

**Part V — The model as an artefact**
15A. Training dynamics, overfitting and checkpoint selection
16. Tokenisation and sequence diagnostics
17. Engineering and operational
18. Governance, licensing and reproducibility

**Part VI — Judgement**
19. Qualitative and expert review
19A. Model comparison and the decision procedure

**Part VII — Deciding**
20. Failure-mode catalogue · Acceptance gates · Reporting · Changelog

---

# Part I — Before you train

## 1. Framing — why a prior is judged differently from a generator

A Stage 1 prior is usually evaluated as a distribution learner: does it produce valid molecules resembling the training set? Necessary, **not sufficient**, because in a REINVENT-family pipeline the prior does not stop working when Stage 2 begins.

In that formulation the prior's likelihood term stays **inside the RL loss for the whole of Stage 2** — it "acts to ensure that the generated SMILES are syntactically valid and has been shown to empirically enforce reasonable chemistry," with a σ hyperparameter trading prior likelihood against reward [Guo2024].

> **The prior is a persistent regulariser, not a discarded initialisation.** Its quality bounds what Stage 2 can produce. A prior assigning low likelihood to a class of desirable saponins will penalise Stage 2 for generating them, and reward shaping does not fully undo that.

Six questions follow, and most published suites answer only the first two.

| | Question | Sections |
|---|---|---|
| **A** | Does it produce chemically real saponins? | 4, 5, 6, 7, 8, 9 |
| **B** | Does it cover saponin space? | 10 |
| **C** | Is it honest — generating, not recalling? | 11, 12 |
| **D** | Is it a good prior *for optimisation*? | 13, 14, 15 |
| **E** | Is it a sound engineering artefact? | 16, 17, 18 |
| **F** | Does it convince a chemist? | 19 |

---

## 2. Corpus readiness and data quality

**Evaluate the data before the model.** Most of what looks like model failure is corpus failure, and every downstream metric inherits corpus defects silently.

### 2.1 Structural hygiene

| # | Check | Why |
|---|---|---|
| **D1** | **Parse rate** — RDKit sanitisation success | Baseline sanity |
| **D2** | **Deduplication by InChIKey** (not by SMILES string) | The same molecule appears under many SMILES; string-level dedup leaves duplicates that inflate apparent data volume |
| **D3** | **Salt, solvate and counter-ion stripping** | [Skinnider2021] retained only the heaviest fragment with ≥3 heavy atoms |
| **D4** | **Mixture and multi-component detection** | COCONUT 2.0 curation explicitly removes multi-component entries [Chandrasekhar2025]; assume TeroKit needs the same |
| **D5** | **Charge normalisation** | Neutralise where chemically sensible; record what was changed |
| **D6** | **Tautomer canonicalisation** | Otherwise the same molecule is learned as several |
| **D7** | **Element whitelist** | [Skinnider2021] retained Br, C, Cl, F, H, I, N, O, P, S. Fluorinated "natural products" are a known contamination marker — COCONUT removed them outright [Chandrasekhar2025] |
| **D8** | **Valence-error scan** | Aggregated databases carry them; TeroMOL aggregates broadly [Chen2023] |
| **D9** | **Rare-token filtering** | [Skinnider2021] dropped molecules with tokens present in <0.01% of the database |
| **D10** | **Length cap decision** | [Skinnider2021] capped at 250 characters; GuacaMol at 100 [Brown2019]. **Measure your distribution before choosing** — a cap that truncates real saponins silently removes your hardest cases |

### 2.2 Composition audit

| # | Check | Why |
|---|---|---|
| **D11** | **Aglycone : glycoside ratio** | The project's single most important unmeasured quantity (R11). Aglycones teach ring systems; only glycosides teach glycosylation |
| **D12** | **Stereochemistry completeness** — fully specified / partial / flat | R12. If much of the corpus is flat, the entire case for a SMILES CLM weakens |
| **D13** | **Class balance** — run NPClassifier over the training set | Establishes the reference class distribution for §7 *and* reveals whether one skeleton dominates |
| **D14** | **Sugar composition** | The reference histogram for S3 |
| **D15** | **Size and length distributions** | Sets the context-window requirement (§16) |
| **D16** | **Internal diversity of the corpus** | [Skinnider2021] found low-data CLMs succeed far more readily in *homogeneous* regions — so corpus homogeneity predicts achievable quality |
| **D17** | **Source-database overlap** | TeroMOL aggregates from many sources; overlapping subsets bias frequency-based metrics |

`audit_corpus.py` (shipped earlier) covers D1, D11, D12, D14, D15, D16 and parts of D2.

### 2.3 Provenance

| # | Check |
|---|---|
| **D18** | **Per-molecule source tracking** — which sub-database each came from, retained through curation |
| **D19** | **Licence audit** — TeroKit [Zeng2020, Chen2023] and COCONUT [Chandrasekhar2025] terms, and what they permit for a *derived model* you may want to release (§18) |
| **D20** | **Frozen splits** — define and hash train/validation/test **before** any modelling. Splits chosen after seeing results are not splits |

---

## 3. Experimental design

### 3.1 The A↔B reference baseline

Every distribution-matching metric is a *distance*; its floor is not zero but the distance between two samples of real data.

1. Split the curated corpus into disjoint halves **A** and **B**.
2. Compute every distribution metric **between A and B**.
3. That vector is the target. A model reaching it is statistically indistinguishable from real saponins on that measure.

Report every distance as **`value / base`**, never as a bare number.

### 3.2 Splits — compute all three

| Split | Purpose |
|---|---|
| **Random** | Optimistic bound; easy reference |
| **Scaffold** (Bemis–Murcko [Bemis1996]) | The honest generalisation test. **Default for reporting** |
| **Source-organism / taxonomic** | If TeroKit carries organism metadata: can the model generalise to a plant genus it never saw? The closest proxy for discovering saponins from unstudied taxa |

### 3.3 Controls — the part most protocols omit

Without these, a model can look good while being useless.

| # | Control | What it establishes |
|---|---|---|
| **C1** | **Real held-out data, scored as if generated** | The **ceiling**. Any metric where your model beats real data is a metric measuring the wrong thing |
| **C2** | **Random sample of training molecules** | The **memorisation floor** — what perfect recall would score |
| **C3** | **Random sample of COCONUT non-terpenoids** | The **off-target floor** — what "wrong chemistry" scores. Distinguishes metrics with discriminating power from metrics that score everything alike |
| **C4** | **Character n-gram model** on the same corpus | The **trivial-model floor**. A deep model that barely beats a 5-gram has learned little |
| **C5** | **From-scratch model on the 40k, no pretraining** | The pretraining control. If it matches, prefer it — no non-terpenoid bias to fight in Stage 2 |
| **C6** | **Shuffled-SMILES model** (train on corrupted strings) | Confirms the metric suite can detect a broken model. A sanity check on the *evaluation*, not the model |

C6 deserves emphasis: it tests your evaluation harness. If a deliberately broken model passes your gates, the gates are wrong.

### 3.4 Ablation matrix

Vary one factor at a time, everything else fixed:

- Pretraining corpus: none / TeroMOL-180k / COCONUT-695k / COCONUT→TeroMOL
- Terpenoid class subset: all / large classes only (di-, sester-, tri-, steroid, meroterpenoid) — tests R13
- Augmentation: 1× / 2× / 3× / 5× / 10× — expect a **low** optimum at 40k [Skinnider2021]
- Architecture: LSTM / GRU / transformer / S4 [Ozcelik2024]
- Representation: SMILES / SELFIES — expect SMILES to win [Skinnider2021, Skinnider2024]
- Stereo: isomeric vs flattened — quantifies what stereochemistry costs and buys

### 3.5 Statistical requirements

- **≥100,000 samples per evaluation; prefer 500,000.** [Skinnider2021] sampled 500k per model and found some property-distribution metrics **unstable below 100k**. [Ozcelik2025] gives direct evidence: FCD and FDD **decrease with library size**, plateauing only above 10⁴–10⁵ designs, and recommends reporting similarity metrics only for libraries of ≥10⁵.
- **Compare only at identical library size, regardless of architecture** [Ozcelik2025]. Library size systematically biases evaluation and **can reverse model rankings** — two models compared at different sample sizes may swap places for reasons unrelated to quality. This is a precondition of comparison, not a reporting detail.
- **≥3 seeds** per configuration, mean ± SD ([Skinnider2021] used 10; 3 is the practical floor).
- **Paired tests across seeds** for any gated comparison — [Skinnider2024] used paired t-tests at n = 10.
- **Report effect sizes, not just significance.** With ~70 metrics, some will differ by chance; note the multiple-comparison exposure and treat single marginal results sceptically.
- **Fix and report the sampling temperature** with every number.
- **Pre-register the gates** (§21) before seeing results.

---

# Part II — Does it produce real saponins?

## 4. Core distribution learning

The five metrics that correlated with model quality at **ρ ≥ 0.80 across all four databases** in the largest systematic benchmark available — 8,447 models, >4 billion molecules [Skinnider2021]. Everything else in the field failed that test.

| # | Metric | Target |
|---|---|---|
| **1.1** | **% valid** | **~80–85%, not 95%.** COCONUT-trained CLMs never exceeded 82% at *any* training-set size, including 500k [Skinnider2021] |
| **1.2** | **FCD** [Preuer2018] | → `base`; report ratio |
| **1.3** | **% stereocentres** (JSD) | → `base`. Saponin-critical, not generic |
| **1.4** | **Murcko scaffolds** (JSD) | → `base` |
| **1.5** | **NP-likeness** (JSD) [Ertl2008] | → `base` |

**Use Jensen–Shannon distance** — [Skinnider2021] benchmarked it against Wasserstein and KL and found JSD tracked ground truth best.

**Measure validity before filtering.** Invalid SMILES are sampled at significantly lower likelihood than valid ones, so post-hoc filtering is a free quality filter and a property of the representation, not a defect [Skinnider2024].

**Integrating the five.** [Skinnider2021] combined them by PCA and used PC1 as a single score, releasing `CLMeval` for it. Worth adopting when comparing many candidates.

**FCD calibration warning.** [Subramanian2023] found both a string model and JT-VAE scored poorly on FCD on small focused datasets — not from weakness but because ChemNet was calibrated on drug-like bioactivity data. Saponins sit far outside that. Expect poor absolute FCD regardless of model quality; use ratios only.

## 5. Chemical and physical validity beyond parsing

RDKit-parseable is a low bar. These catch molecules that parse and could not exist.

| # | Check | Catches |
|---|---|---|
| **V1** | **Valence and charge sanity** | Hypervalent atoms, implausible net charge |
| **V2** | **Radical / unpaired-electron check** | Usually a generation artefact |
| **V3** | **Aromaticity round-trip** | SMILES → mol → SMILES instability; a perception-model disagreement flag |
| **V4** | **InChI round-trip consistency** | Structures RDKit accepts but InChI rejects |
| **V5** | **3D embeddability (ETKDG success rate)** | **The strongest cheap physical-plausibility filter.** A molecule that cannot be embedded in 3D cannot exist. Rarely reported, and directly relevant to strained fused polycyclics like triterpenoid skeletons |
| **V6** | **Bredt's-rule and trans-cycloalkene violations** | Anti-Bredt bridgeheads and trans double bonds in small rings — classic generative artefacts in polycyclic systems |
| **V7** | **Unstable / non-natural functional groups** | Acyl halides, anhydrides, peroxides where the corpus has none. Define the list from the *training set*, not from drug-design filters |
| **V8** | **Element whitelist compliance** | Elements absent from the corpus |
| **V9** | **Stereochemical self-consistency** | Impossible stereo combinations at ring fusions — saponins have many fused ring junctions |
| **V10** | **Ring-size sanity** | Macrocycles or 3-membered rings at rates the corpus does not support |

V5 and V6 are the two most worth adding if you add only two: both target the fused-polycyclic failure mode that generic suites never test.

## 6. Saponin-specific structural metrics

**No published suite evaluates any of this.** MOSES, GuacaMol and MolScore are drug-design tools; none knows what a glycoside is. This tier is the project's genuine methodological contribution.

| # | Metric | Catches | Risk |
|---|---|---|---|
| **S1** | **Glycosylation rate** — P(≥1 sugar) vs reference | A prior that quietly stops emitting sugars. Passes every generic metric | R11 |
| **S2** | **Sugars per molecule** (JSD) | Mono-/bis-/tridesmosidic balance drifting | R11 |
| **S3** | **Monosaccharide composition** (JSD) | **Sugar collapse** — rhamnose/xylose/arabinose drifting toward glucose. Passes validity *and* anomeric checks while being the wrong molecule | R10 |
| **S4** | **Anomeric configuration validity** | RDKit-valid structures that are stereochemical nonsense at the anomeric carbon | R2 |
| **S5** | **Glycosylation regiochemistry** — C-3 ether, C-28 ester, … | Sugars attached where they never occur | — |
| **S6** | **Aglycone skeleton class** (rule-based) | Skeleton collapse. Largely superseded by §7, but keep as an independent check on the ML classifier | — |
| **S7** | **Stereo completeness** | The model learning to omit stereo descriptors because it is easier | R12 |
| **S8** | **Sugar chain length and branching** | Linear vs branched oligosaccharide balance | — |
| **S9** | **O- vs C-glycoside ratio; ether vs ester linkage** | C-glycosides are a real saponin subclass; a prior that never emits them has a blind spot | — |
| **S10** | **Sugar acylation rate** | Acyl groups on sugars are common and easily lost | — |
| **S11** | **Stereocentre count distribution** | Complements 1.3 — the count, not just the fraction | R12 |
| **S12** | **Aglycone : sugar mass ratio** | Coarse but robust: are both halves generated in proportion? | R11 |
| **S13** | **Aglycone ring-system integrity** | Whether generated triterpenoid cores are intact 6-6-6-6-6 / 6-6-6-6-5 systems rather than plausible-looking fragments | — |
| **S14** | **Free hydroxyl / carboxyl pattern on the aglycone** | The functionalisation pattern that determines where glycosylation can occur | — |
| **S15** | **Absolute configuration / enantiomer check** | **The gap aggregate stereo metrics cannot see.** Triterpenoids are single-enantiomer natural products. A model can produce the mirror image — correct stereocentre *count*, correct *fraction*, fully specified, chemically valid, and the unnatural antipode. Compare generated molecules against reference enantiomers; *ent*- series do occur in terpenoids (*ent*-kaurane diterpenoids, for example), so "some *ent*-" is not automatically wrong — it has to match the reference rate | R2 |
| **S16** | **Ring-fusion stereochemistry** — configuration at the A/B, B/C, C/D ring junctions | The most chemically decisive stereo feature of a triterpenoid skeleton, and invisible to any count- or fraction-based metric. *cis*- vs *trans*-fused decalin junctions determine the whole 3D shape | R2 |
| **S17** | **Position-resolved stereo accuracy** | For each scaffold, is R/S assigned correctly *at each mapped position* relative to real examples of that scaffold? S7 and S11 confirm stereocentres are present and counted correctly; only this confirms they are **right** | R2 |
| **S18** | **Double-bond geometry (E/Z)** — JSD over configured double bonds | Δ12 unsaturation is characteristic of oleanane/ursane skeletons; geometry errors here are structural errors | — |
| **S19** | **Sugar ring integrity** | Distinct from S3 identity: is each sugar a well-formed pyranose/furanose with the right substitution pattern, or a sugar-*shaped* ring that is not a sugar? | R10 |

**Why S15–S17 are separate from S7 and S11.** The stereo metrics inherited from the literature — % stereocentres [Skinnider2021], stereo completeness, stereocentre count — are all **aggregate**. They confirm stereochemistry is *present and abundant*, never that it is *correct*. A model can score perfectly on all three while producing the wrong enantiomer at every centre. For a class of single-enantiomer natural products with decisive ring-fusion stereochemistry, aggregate metrics are not sufficient, and no published suite closes this gap.

**Build order.** S1, S2, S7, S11, S12, S18 are cheap substructure counting — build before the first training run. S3, S4, S15, S16, S17 and S19 need real stereochemical perception; S16 and S17 additionally need scaffold-level atom mapping, which is the most demanding thing in this protocol to implement. Start with S15 (whole-molecule enantiomer comparison) — it is the cheapest of the three and catches the most catastrophic failure.

**Honest caveat on S3.** The sugar detection in `audit_corpus.py` is a shape heuristic: it cannot distinguish glucose from galactose from mannose, which is precisely what S3 requires. S3 needs stereocentre-by-stereocentre matching against reference monosaccharides. Check `privateer` or PDB carbohydrate-validation tooling before writing one.

## 7. Chemical ontology classification

Answers a question no fingerprint metric can: *are these the right kind of natural product?*

### 7.1 NPClassifier — primary

**NPClassifier** [Kim2021] predicts a three-level **pathway → superclass → class** ontology from counted Morgan fingerprints, built specifically for natural products. Three reasons it fits:

1. **NP-native** — terpenoid classes are first-class categories.
2. Returns an **`isglycoside` flag** — an independent implementation cross-checking S1.
3. **MIT** code, **CC0** data/models/ontology, Dockerised for local deployment — necessary at 100k+ molecules per evaluation.

| # | Metric |
|---|---|
| **O1** | **Pathway distribution JSD** — should be overwhelmingly terpenoid; anything else is drift |
| **O2** | **Superclass distribution JSD** — triterpenoids vs steroids vs others |
| **O3** | **Class distribution JSD** — the fine level. **Catches skeleton-class collapse** |
| **O4** | **Unclassifiable / low-confidence rate** — an **off-manifold detector**: molecules that parse, look plausible, and are not recognisably natural products |
| **O5** | **`isglycoside` rate** — cross-check on S1 |
| **O6** | **Class coverage** — how many reference classes appear at all |
| **O7** | **Per-class NLL** — join O3 to §13: which classes does the prior find *unlikely*? |

**A design question O3 does not settle: match the reference, or rebalance it?**

O3 scores the model on *matching* the training class distribution. But if TeroKit is dominated by oleanane-type saponins — which D13 will tell you — then a model that faithfully reproduces that imbalance is doing exactly what distribution learning asks, and is also a poor foundation for a generator whose stated goal is **diversity**. Matching an imbalanced reference means under-generating the rare skeletons that are arguably the most interesting design space.

The two are in genuine tension and the resolution is a project decision, not a metric:

| Option | When it is right | Cost |
|---|---|---|
| **Match the reference** (minimise O3) | Stage 2 will optimise within well-populated chemistry; you want maximum realism | Rare classes stay rare; the prior assigns them low likelihood, and §13's L2 will show it — meaning Stage 2 is penalised for exploring there |
| **Deliberately rebalance** — class-weighted sampling or oversampling rare classes at Stage 1 | Stage 2 needs access to under-represented skeletons | O3 worsens by construction; you must then report O3 against the **intended** distribution, not the corpus distribution, and say so |

**Decide this before training and record it (GV5), because it changes how O3 and G7 are read.** If you rebalance, G7's threshold applies to your target distribution, and the honest reporting is both numbers: JSD against the corpus *and* against the target.

**Scope caveat.** Per-level category counts, per-class F1, and how NPClassifier weighs aglycone versus sugar were **not extractable** (ACS 403, PMC CAPTCHA). Before gating on O3, classify corpus half A and confirm the returned classes match chemical expectation. Treat O3 thresholds as provisional until then.

### 7.2 ClassyFire — secondary

**ClassyFire** [Djoumbou2016] applies **ChemOnt**: 4,825 categories (4,146 organic, 678 inorganic), up to 11 levels deep, average depth five. Broader, not NP-specific.

Use as a **cross-check**. Agreement between two independently-built ontologies is much stronger evidence than either alone, and disagreement localises the problem.

## 8. Property distributions

[Skinnider2021] found **individual** property JSDs weakly or inconsistently correlated with model quality — hence none are in §4. As a **panel** they are cheap, and a systematic skew across several is real signal.

| Group | Properties |
|---|---|
| Size | MW, heavy atoms, atom-type proportions |
| Lipophilicity | Wildman–Crippen logP, TPSA |
| H-bonding | Donors, acceptors |
| Topology | Total / aromatic / aliphatic rings, rotatable-bond fraction, sp³ fraction |
| Complexity | Bertz topological complexity |
| Drug-likeness | QED, SA score [Ertl2009] |
| Sequence | SMILES / token length |

**Read these as a saponin chemist, not a medicinal chemist.** QED and Lipinski are near-meaningless here — saponins violate them by construction, and a prior scoring "well" on QED has drifted toward drug-like space and away from target. Report QED to show it **matches the reference**, never to show it is high. Same for SA score, which is calibrated on drug-like fragment frequencies (see §9).

Token-length JSD is an early warning that the model is truncating complex structures.

## 9. Synthesizability and biosynthetic plausibility

For saponins, "can it be made" splits into two different questions, and the biological one matters more.

### 9.1 Synthetic accessibility — use with caution

| # | Metric | Caveat |
|---|---|---|
| **A1** | **SA score** [Ertl2009] | Calibrated on drug-like fragment frequencies. Saponins score poorly by construction. Interpret **only** against `base` |
| **A2** | **RAscore** [Thakkar2021] | ML classifier for whether a synthetic route is findable, ~4,500× faster than running the underlying CASP tool. Trained on drug-like retrosynthesis — **applicability to saponins is unverified**; validate on real saponins before trusting it |
| **A3** | **SCScore / SYBA** | Alternative scorers, **⚠️ not verified this cycle**. Listed for completeness |

**The right use of all three:** compare generated against real held-out saponins. If generated molecules score *better* than real saponins, the model is drifting toward simpler, more drug-like chemistry — a failure dressed as a success.

### 9.2 Biosynthetic plausibility — the more meaningful test

A saponin has to be something a plant could make. This is stronger than synthetic accessibility and, for this project, more relevant.

| # | Metric |
|---|---|
| **B1** | **Biosynthetic pathway findability** — can a retro-biosynthesis tool route the molecule to known building blocks? |
| **B2** | **Pathway length / step count distribution** vs real saponins |
| **B3** | **Glycosyltransferase plausibility** — is the sugar-linkage pattern one that known enzymes produce? |
| **B4** | **Terpenoid-skeleton biosynthetic consistency** — does the aglycone follow isoprenoid cyclisation logic? |

**BioNavi-NP** [Zheng2022] is the natural tool: a transformer plus AND-OR-tree search that predicts biosynthetic pathways for natural products, reporting a **90.2% success rate** on 368 test compounds, 72.8% correct building-block recovery (1.7× a rule-based approach), and 88% on 25 unseen compounds. It covers terpenoids via the MVA/MEP pathway. Code at `github.com/prokia/BioNavi-NP`; web server at `biopathnavi.qmclab.com`.

**Note the adjacency.** BioNavi-NP shares authors (Zeng, Wu) and a domain (`qmclab.com`) with TeroKit [Zeng2020, Chen2023] — the same group that built your training database built this. Whether they interoperate directly is **unverified**, but it is the first thing to check.

**TeroENZ is already in your hands.** TeroKit ships **13,462 biosynthetic enzymes across 2,541 species and 4,293 reactions** [Chen2023]. That is a ready-made substrate for B3 and B4 without any external tool — arguably the most project-specific metric available to you, and nobody has built it.

---

# Part III — Does it cover the space, honestly?

## 10. Coverage and diversity

| # | Metric | Source |
|---|---|---|
| **2.1** | **SEDiv @ 1k** — sphere-exclusion diversity; fraction of a 1,000-molecule sample needed to describe its space. Higher = better coverage | [Thomas2024] |
| **2.2** | **#Circles** — related sphere-exclusion count | [Renz2024] |
| **2.3** | **Scaffold diversity** — distinct Murcko scaffolds | [Thomas2024] |
| **2.4** | **Scaffold uniqueness** — their frequency distribution; catches "many molecules, one skeleton" | [Thomas2024] |
| **2.5** | **Ring-system diversity** — directly sensitive to aglycone skeletons | [Thomas2024] |
| **2.6** | **Functional-group diversity** | [Thomas2024] |
| **2.7** | **Outlier bits ("silliness")** — fingerprint bits absent from any real molecule | [Thomas2024] |
| **2.8** | **Scaffold coverage / recall** — fraction of *reference* scaffolds reproduced. Diversity without coverage = drifting off-target | derived |
| **2.9** | **SNN** — mean Tanimoto to nearest reference neighbour. **Interpret in both directions**: too high = memorisation, too low = off-distribution | [Polykovskiy2020] |
| **2.10** | **Frag / Scaf cosine similarity** | [Polykovskiy2020] |
| **2.11** | **Coverage of the property manifold** — do generated molecules span the reference's full range, or only its mode? | derived |
| **2.12** | **Number of substructures** — size-invariant coverage measure, ~85× faster than clustering | [Ozcelik2025] |
| **2.13** | **Design frequency** — how often each molecule is generated. Frequently-generated molecules are often simple substructures (benzene, amine, ether) and "unsuitable for prospective studies"; frequency is a quality signal, not just a count | [Ozcelik2025] |

2.1–2.7 are in `moleval` (MolScore); 2.9–2.10 in MOSES. Reuse the **metric code**, not MOSES *scores* (§22.3).

## 11. Failure detectors

**Report these. Never gate on them except at an alarm threshold.**

These metrics have **no quality gradient** — they cannot rank two reasonable models — but they have a **floor**. MolGAN's ~2% uniqueness [DeCao2018] is exactly the failure a Stage 1 diversity prior cannot tolerate, and uniqueness is the metric that names it.

| # | Metric | Not a quality metric because | Still catches |
|---|---|---|---|
| **3.1** | **% unique** | Every model in [Skinnider2021] exceeded 99%, **and it decreases with library size, ranking models differently across scales** — [Ozcelik2025] recommends treating it as a sanity check only | Mode collapse. Report as a **curve** — uniqueness@1k/@10k/@100k/@500k. The saturation point is informative when the endpoint is not |
| **3.2** | **IntDiv₁, IntDiv₂** | Misranks coverage — scored GDB-13 as more diverse than GDB-17 [Renz2024] | Total collapse; also expected by reviewers |
| **3.3** | **% novel** | Uncorrelated with quality [Skinnider2021]; maximised by drifting off-distribution [Subramanian2023] | Gross memorisation (see §12 for the diagnostic version) |
| **3.4** | **Duplicate rate within sample** | — | Sampling bugs; temperature too low |
| **3.5** | **MOSES Filters (PAINS/MCF)** | Drug-design constructs; saponins fail them for irrelevant reasons | Gross structural pathology only. Against `base`, never absolutely |

## 12. Memorisation, novelty and leakage

| # | Metric | Catches |
|---|---|---|
| **7.1** | **Exact training reproduction rate** (canonical SMILES) | Memorisation. Some is healthy; a high rate is not |
| **7.2** | **Exact held-out reproduction rate** | **Rediscovery — a positive signal.** Direct evidence of generalisation |
| **7.3** | **Near-duplicate rate** (Tanimoto > 0.99 to training) | Trivial variation dressed as novelty |
| **7.4** | **Novel-scaffold rate** | Interpret against `base` — the reference sets the natural rate |
| **7.5** | **Canonicalisation-collapse check** | Distinct strings collapsing to one canonical SMILES, inflating apparent uniqueness |
| **7.6** | **Train/test contamination audit** (InChIKey) | **Run once, first.** A leak invalidates every §13–14 number |
| **7.7** | **Augmentation leakage** | With randomised SMILES, confirm augmented variants of test molecules never entered training |

7.7 is specific to this pipeline and easy to get wrong: SMILES enumeration can smuggle test molecules into training under different strings.

---

# Part IV — Is it a good prior for Stage 2?

## 13. Likelihood and calibration

| # | Metric |
|---|---|
| **L1** | **Held-out NLL** (per token) on the **scaffold** split — the most diagnostic single number |
| **L2** | **NLL by subgroup** — by aglycone class (via O3), sugar count, molecule size, and above all by whatever Stage 2 will optimise toward. **A prior with good mean NLL but a bad tail on exactly your target chemistry will fight you, and the aggregate hides it** |
| **L3** | **NLL gap** — held-out minus training. The overfitting measure |
| **L4** | **Calibration curve** — binned predicted likelihood vs observed frequency |
| **L5** | **Perplexity** — reported alongside NLL for comparability with LM literature |
| **L6** | **Per-position entropy** — where in the string is the model uncertain? High entropy at stereo descriptors is diagnostic |
| **L7** | **NLL of known target saponins** — if specific compounds motivate the project, check the prior finds them likely |

## 14. Optimisability

| # | Metric |
|---|---|
| **P1** | **Sample-efficiency probe** — short RL run against a cheap proxy, scored by **AUC of top-10 average value vs oracle calls**, min-max scaled to [0,1] [Gao2022] |
| **P2** | **Multiple objectives** — at least two of different character (one property-based, one structural); sample efficiency is objective-dependent |
| **P3** | **Harness validation** — run your pipeline on a standard PMO task first and confirm it reproduces published numbers. REINVENT ranked **first of 25 algorithms across 23 tasks** [Gao2022]; Augmented Memory reported 15.002 AUC top-10 vs REINVENT's 14.016 [Guo2024] |
| **P4** | **Diversity collapse under RL** — track SEDiv, scaffold diversity and uniqueness **at every step**. Mode collapse is documented: "the model samples the same molecule repeatedly or becomes stuck at suboptimal minima" [Guo2024] |
| **P5** | **σ prior-drift sensitivity** — sweep the prior-vs-reward trade-off [Guo2024] and find where quality breaks. This maps the operating range you hand Stage 2. [Guo2024] gives no quantitative drift thresholds, so this is uncharted for your chemistry |
| **P6** | **Scaffold-recovery rate** — fraction of held-out scaffolds reproduced in 10⁵–10⁶ samples |
| **P7** | **Conditional-generation probe** — if Stage 2 conditions on scaffolds or properties, test that at Stage 1 |
| **P8** | **Warm-start advantage** — how many oracle calls the pretrained prior saves versus the from-scratch control (C5). The direct measure of what pretraining bought |

**Early-stop on diversity, not loss.** Transfer-learning duration has no principled stopping rule [Skinnider2021, Moret2020].

## 15. Robustness and sampling behaviour

| # | Check |
|---|---|
| **R1** | **Temperature sweep** — plot validity against SEDiv. A healthy prior trades them smoothly; one only valid when cold and only diverse when hot has no usable operating point |
| **R2** | **Top-k / top-p sweep** — **not equivalent to R1.** [Ozcelik2025] found restrictive top-*k*/top-*p* causes mode collapse while temperature sampling remains superior for diversity control. Sweep both, but expect temperature to be the usable lever |
| **R3** | **Seed sensitivity** — variance across seeds at fixed settings. Large variance undermines every single-run number |
| **R4** | **Degenerate-repetition detection** — repeated ring-closure loops and runaway chains, a known failure in long-sequence generation |
| **R5** | **Length-control behaviour** — does it terminate sensibly, or run to the context limit? |
| **R6** | **EOS calibration** — is the length distribution right, or is it truncating? |
| **R7** | **Numerical robustness** — fp16 vs fp32 sampling agreement |
| **R8** | **Batch-size invariance** — identical output distribution regardless of batch size (catches padding/masking bugs) |
| **R9** | **Retraining variance** — train the *same configuration* from scratch ≥3 times with different init seeds and compute every gated metric on each. **This is distinct from R3, which varies only the sampling seed.** It is the number that tells you whether a difference between two models is real |
| **R10** | **Checkpoint sensitivity** — metric variation across adjacent epochs near convergence. Large swings mean your reported number is an artefact of where you stopped |
| **R11** | **Distribution-shift robustness** — evaluate on a corpus slice held out by *source database* or *producing organism*, not randomly. Degradation here predicts how the prior behaves on genuinely new saponin chemistry |
| **R12** | **Data-order sensitivity** — same seed, shuffled training order. Should be negligible; if not, training is unstable |

---

## 15A. Training dynamics, overfitting and checkpoint selection

v3.0 treated overfitting as a single number — the NLL gap (L3). That is not enough to run a training programme on. Overfitting in a generative model is a *process* observed over epochs, and the most dangerous form of it is invisible to validation loss.

### The failure that validation loss does not catch

**Validation NLL and sample quality can diverge.** A model can keep improving on held-out likelihood while its *samples* get worse — more conservative, less diverse, concentrated on the corpus mode — or the reverse. Likelihood rewards putting probability mass on real molecules; it does not reward covering the space. Since Stage 1's job is diverse coverage, **selecting a checkpoint on validation loss alone can select against the project's actual goal**.

This is why [Skinnider2021] and [Moret2020] both note transfer-learning duration has no principled stopping rule, and why §14 says early-stop on diversity rather than loss.

| # | Metric |
|---|---|
| **F1** | **Train and validation loss curves** — per epoch, plotted, not just final values. The epoch where validation turns up is the classical overfitting point |
| **F2** | **Generative-quality curves** — recompute §4 metrics (validity, FCD, scaffold JSD) and SEDiv **every N epochs**, on the same fixed sample size. Plot alongside F1 |
| **F3** | **Loss–quality divergence epoch** — the epoch at which F1 and F2 stop agreeing. **Report it explicitly.** If it comes before your chosen checkpoint, you selected on the wrong signal |
| **F4** | **Checkpoint-selection criterion** — state it, in advance, and justify it. Candidate rules: best validation NLL; best PC1 composite; best SEDiv subject to a validity floor; last epoch before the divergence at F3 |
| **F5** | **Augmentation memorisation** — with randomised SMILES, held-out loss can look healthy while the model has memorised *augmented variants* of training molecules. Check reproduction of training molecules **under non-canonical SMILES**, not only canonical (pairs with 7.7) |
| **F6** | **Learning curve vs dataset size** — retrain on 10% / 25% / 50% / 100% of the corpus and plot final quality. A curve still rising at 100% means you are **data-limited**, and more corpus beats any architecture change — the central finding of [Skinnider2021]. A flat curve means you are capacity- or method-limited |
| **F7** | **Parameter count vs corpus size** — record the ratio. Context for F6 |
| **F8** | **Convergence evidence** — gradient-norm trace, loss spikes, any instability. A model that never converged cleanly makes every downstream number provisional |
| **F9** | **Per-token-type loss** — decompose loss by token class. **Are stereo descriptors and ring-closure digits harder than atoms?** If loss concentrates there, that is the mechanism behind the R2/R10 failures, visible directly |
| **F10** | **Epoch-wise memorisation trace** — 7.1 and 7.3 recomputed per epoch. Memorisation rises monotonically; this shows when it becomes unacceptable |

**F9 is the most project-specific item here.** If stereo tokens carry disproportionate loss, you have located the sugar-collapse and anomeric-validity failures inside the training signal itself, rather than inferring them from generated output.

**F6 is the most decision-relevant.** It answers "should I get more data or change the model?" — and [Skinnider2021] found across 8,447 models that data volume dominates. Run it once; it settles many later arguments.


# Part V — The model as an artefact

## 16. Tokenisation and sequence diagnostics

**Under-examined and, for saponins, high-risk.** Long stereo-dense strings stress a tokeniser in ways drug-like SMILES do not.

| # | Check | Why it matters here |
|---|---|---|
| **T1** | **Vocabulary size and coverage** | [Skinnider2021] tokenised on characters, treating multi-character atoms (Br, Cl) and bracketed environments (`[nH]`) as single tokens |
| **T2** | **OOV rate on held-out data** | Any OOV token means unreachable chemistry |
| **T3** | **Stereo-token segmentation** | Is `[C@@H]` one token or several? Splitting it makes stereochemistry harder to learn — directly relevant to R2/R10 |
| **T4** | **Ring-closure handling above 9** | Saponins with many fused rings plus sugars need `%10`, `%11`… Verify the tokeniser handles two-digit closures; this is a classic silent failure |
| **T5** | **Token-frequency distribution** | Rare tokens are learned poorly; rare-sugar tokens sit exactly here |
| **T6** | **Sequence-length distribution vs context window** | **Set from the maximum plus headroom, not the p95.** An earlier version of this protocol said p95 — that is wrong here. A p95 window truncates 5% of the corpus, and in a saponin set the longest molecules are the most heavily glycosylated, i.e. exactly the ones the project exists to model. Use max × ~1.2, and verify against generated length too (T11) |
| **T7** | **Truncation rate** | Any truncation systematically removes your most complex molecules — the ones that matter most |
| **T8** | **Atom-level vs BPE comparison** | BPE may merge chemically meaningful units badly; worth one ablation |
| **T9** | **Round-trip fidelity** | detokenise(tokenise(x)) == x for 100% of the corpus |
| **T10** | **Augmentation-tokenisation interaction** | Randomised SMILES change token distributions; confirm the vocabulary covers all variants |
| **T11** | **Output truncation / incomplete-generation rate** | **Distinct from T7, which is input truncation.** Fraction of samples that hit the context limit without emitting EOS — an unterminated string that is discarded as invalid. Since the model's longest generations are its most glycosylated, a non-trivial rate here means the prior is systematically unable to finish exactly the molecules you want |
| **T12** | **Generated vs training length distribution** (JSD) | Even with a sufficient window, the model may under-generate length. A generated distribution shifted short is the model avoiding complexity — visible here and nowhere else |

## 17. Engineering and operational

Easy to omit and decisive in practice — Stage 2 RL needs enormous numbers of samples.

| # | Metric |
|---|---|
| **E1** | **Inference throughput** (molecules/sec, valid molecules/sec) — **the constraint on Stage 2**. A prior 3× slower needs 3× the wall-clock for the same RL run |
| **E2** | **Training cost** — GPU-hours and wall-clock per configuration |
| **E3** | **Model size and memory footprint** |
| **E4** | **Time-to-first-sample** and batch-scaling behaviour |
| **E5** | **Determinism** — same seed, same output, across restarts |
| **E6** | **Checkpoint size and load time** |
| **E7** | **Dependency and environment pinning** — exact versions of RDKit, the framework, the metric code. **RDKit version changes sanitisation behaviour**; validity is not comparable across versions |
| **E8** | **Failure modes under load** — OOM behaviour, graceful degradation |

E7 is not bureaucratic: a validity number computed under a different RDKit is not comparable to yours.

## 18. Governance, licensing and reproducibility

| # | Item |
|---|---|
| **GV1** | **Model card** — training data, intended use, limitations, evaluation results |
| **GV2** | **Data licensing for derived models** — what TeroKit [Zeng2020, Chen2023] and COCONUT [Chandrasekhar2025] permit for a model you may publish or share. **Resolve before training, not after** |
| **GV3** | **Provenance chain** — corpus version, curation script version, split hashes, all recorded |
| **GV4** | **Metric-suite versioning** — pin the evaluation code; metrics drift between releases |
| **GV5** | **Pre-registration** — gates and thresholds fixed before results are seen |
| **GV6** | **Negative-result recording** — failed configurations documented, not silently dropped |
| **GV7** | **Reproducibility package** — seeds, configs, and the exact sampled sets archived alongside the numbers |

---

# Part VI — Judgement

## 19. Qualitative and expert review

Not optional, and not replaceable by any number.

| # | Check |
|---|---|
| **Q1** | **Chemist review of 100–200 random, unfiltered, uncherry-picked structures.** The single best detector of failures no metric anticipates |
| **Q2** | **Chemical-space overlay** — UMAP or t-SNE of generated vs reference, superimposed **both ways** — the visualisation [Skinnider2021] used to show their metabolome models reproduced their target spaces |
| **Q3** | **Both tails** — inspect the lowest- and highest-likelihood valid samples |
| **Q4** | **Known-saponin rediscovery** — does it generate real, named saponins held out from training? |
| **Q5** | **Biosynthetic plausibility spot-check** — could a plant plausibly make this? Catches valid-but-absurd glycosylation patterns |
| **Q6** | **Blind real-vs-generated test** — can a chemist distinguish generated from real saponins above chance? The most intuitive summary of prior quality, and the one non-specialists trust |
| **Q7** | **Adversarial review** — ask a sceptic to find the worst molecule in 1,000 samples. Whatever they find becomes a new metric |

---

## 19A. Model comparison and the decision procedure

**If these metrics are the sole basis for judging every model, the protocol needs a decision rule, not just numbers.** With ~150 metrics across many candidates, "model A looks better" is not a finding. Three things make it one.

### 19A.1 Establish the noise floor first

**Before comparing any two models, you must know what difference is meaningless.**

Train one configuration from scratch **≥3 times** with different initialisation seeds (R9) and compute every gated metric on each run. The spread across those runs is your **noise floor**. Any difference between two candidate models smaller than that floor is not evidence of anything.

**A second confounder, independent of seed:** [Ozcelik2025] showed **library size alone changes model rankings**. Fix the sample size across every candidate before comparing anything; a ranking obtained at different sizes is not a ranking.

This is the single most important step in this section, and it is routinely skipped. Without it you will chase differences that are init-seed noise — and with ~150 metrics, some will always look impressive by chance.

Report the noise floor once per architecture family, as a band on every metric. Recompute it if the architecture changes materially.

### 19A.2 Define the primary metric in advance

Not every metric can be primary. Pre-commit (GV5) to a hierarchy:

| Level | Role | Suggested |
|---|---|---|
| **Gates** | Binary. A model failing any hard stop is out, regardless of everything else | G0, G9, G10, G11b |
| **Primary** | The single number that ranks surviving candidates | **PC1 composite** over the five §4 metrics [Skinnider2021], *or* PMO AUC (P1) if Stage 2 performance is the real objective |
| **Secondary** | Reported and inspected, used to break near-ties and to explain *why* | SEDiv, S-series, O-series, NLL by subgroup |
| **Diagnostic** | Never ranks anything; explains failures | Tier 11 detectors, F-series, T-series |

**A defensible default:** gates as hard filters → PC1 to rank → SEDiv and the saponin S-series to break ties within the noise floor. State whichever you choose before you look at results.

### 19A.3 The decision rule

```
For candidates A and B:
  1. Either fails a hard-stop gate            -> eliminated, no further comparison
  2. |primary(A) - primary(B)| < noise floor  -> TIE. Decide on secondary
                                                 criteria, then on cost (§17)
  3. Otherwise                                -> the higher primary wins,
                                                 IF no secondary metric has
                                                 degraded by >2x the noise floor
```

Step 3's proviso matters: a model that gains on the primary while losing badly on a saponin-specific metric has usually traded target chemistry for generic quality. That is the wrong trade for this project, and the primary metric alone will not show it.

### 19A.4 Multiple comparisons

With ~150 metrics and several candidates you are running hundreds of implicit tests. Some will look significant by chance.

- **Gate on a pre-registered subset**, not on whichever metrics happen to differ.
- **Report effect sizes with confidence intervals**, not bare p-values.
- Treat any single marginal result that contradicts the rest **sceptically**; require it to replicate across seeds before acting.
- Use paired tests across seeds — [Skinnider2024] used paired t-tests at n = 10.

### 19A.5 Per-model record

For every model built, record — this is the minimum for a comparison to be meaningful later:

| Field |
|---|
| Config hash, corpus version, split hashes, RDKit and framework versions |
| Training curves (F1, F2) and the checkpoint-selection rule used (F4) |
| Gate results: pass/fail per gate |
| Primary metric ± SD across seeds |
| Full metric table with `×base` ratios |
| Noise floor in force at the time |
| Controls (C1–C6) as computed for *this* evaluation run |
| Known deviations from the protocol, and why |

**Re-run the controls with every evaluation.** They are cheap, and they detect harness drift — a change in RDKit version or metric code that silently shifts every number. A control that moves when nothing should have changed is the warning you want.


# Part VII — Deciding

## 20. Failure-mode catalogue

Test for these directly rather than hoping a metric trips.

| Failure | Looks like | Caught by |
|---|---|---|
| **Aglycone dilution** | Excellent generic metrics, few sugars | S1, O5, D11 |
| **Sugar collapse** | Valid, correct anomeric config, wrong sugar | S3, O5 |
| **Skeleton collapse** | High validity, one dominant core | O3, S6, 2.5 |
| **Stereo omission** | Improving validity, falling stereo content | S7, 1.3, S11 |
| **Mode collapse** | High validity, plunging uniqueness | 3.1 curve, 2.1 |
| **Off-manifold drift** | High novelty, poor distribution match | O4, 3.3 + 1.2 read together |
| **Memorisation** | Superb FCD, low novelty | 7.1, 7.3, 2.9 |
| **Drug-like drift** | QED "improves" | 8-panel vs `base` |
| **Truncation** | Missing large molecules | T7, T6, length JSD |
| **Physical impossibility** | Parses, cannot be embedded | V5, V6 |
| **Leakage** | Implausibly good held-out NLL | 7.6, 7.7 |
| **Tokeniser failure** | Systematic loss of ring-rich molecules | T4, T9 |
| **Wrong enantiomer** | Perfect stereo completeness and count, unnatural antipode | **S15** — invisible to 1.3, S7, S11 |
| **Wrong ring fusion** | Correct skeleton class, wrong 3D shape | **S16**, V9 |
| **Right stereocentres, wrong assignment** | Every aggregate stereo metric passes | **S17** |
| **Short-generation bias** | Model avoids the most glycosylated molecules | **T11, T12** — not T7 |
| **Faithful imbalance** | Excellent O3, rare skeletons absent | O6, L2, §7 design note |
| **Evaluation failure** | A broken model passes | C6 |
| **Chasing noise** | Model B "beats" A on several metrics | **R9 noise floor** — without it, invisible |
| **Silent overfitting** | Validation loss fine, samples degrading | **F2, F3** — invisible to L3 alone |
| **Augmentation memorisation** | Held-out loss healthy, model has memorised randomised variants | **F5, 7.7** |
| **Harness drift** | All numbers shift between runs for no modelling reason | Controls re-run each time (19A.5) |

## 21. Acceptance gates

`base` = the A↔B reference on the **scaffold** split. Pre-register before seeing results.

| Gate | Criterion | If it fails |
|---|---|---|
| **G0** | No train/test leakage (7.6, 7.7) | **Hard stop.** Every Part IV number is invalid |
| **G1** | ≥ 75% valid | Check curation first; expect a ~82% ceiling |
| **G2** | FCD ≤ 2× `base`; all §4 JSDs ≤ 2× `base` | More data or better pretraining — not a new architecture |
| **G3** | 3D embeddability (V5) ≥ 0.9× `base` | Physically impossible structures |
| **G4** | SEDiv ≥ 0.8× `base`; scaffold diversity ≥ 0.8× `base` | Reduce augmentation; check over-training |
| **G5** | uniqueness@100k ≥ 90% | **Alarm, not a gradient.** Something is badly wrong |
| **G6** | NPClassifier pathway ≥ 95% terpenoid; O4 ≤ 2× `base` | Off-manifold drift |
| **G7** | NPClassifier class JSD ≤ 2× `base` | Skeleton collapse. Validate the classifier on half A first |
| **G8** | S1 within ±10% of reference; S2 JSD ≤ 2× `base` | Up-weight glycosides (R11) |
| **G9** | S3 JSD ≤ 2× `base` | **Hard stop.** Sugar collapse; consider the glycan-aware tokeniser |
| **G10** | S4 anomeric validity ≥ 95% | **Hard stop.** Re-examine corpus stereochemistry (R12) |
| **G11** | S7 ≥ 0.9× reference | Stereo descriptors being dropped |
| **G11b** | **S15 enantiomer rate within ±5% of reference** | **Hard stop.** The model is producing unnatural antipodes — valid, fully stereo-specified, and the wrong molecule |
| **G11c** | **S16 ring-fusion stereochemistry JSD ≤ 2× `base`** | The 3D shape of the aglycone is wrong even where the 2D skeleton is right |
| **G12** | Property panel: ≤ 2 of 13 exceed 3× `base` | Systematic skew |
| **G13** | Synthesizability/biosynthesis **not better** than real saponins | Drift toward simpler chemistry |
| **G14** | Exact-training reproduction ≤ 2× `base`; near-duplicates ≤ 5% | Memorisation |
| **G15** | NLL gap ≤ 15% of training NLL | Overfitting |
| **G16** | No held-out subgroup with NLL > 1.5× aggregate | The prior will fight Stage 2 there |
| **G17** | PMO AUC ≥ the from-scratch control (C5) | Pretraining is hurting — use the control |
| **G18** | SEDiv retains ≥ 50% through the RL probe | Prior too concentrated |
| **G19** | Beats the n-gram control (C4) on §4 by a clear margin | The deep model has learned little |
| **G20** | Tokeniser round-trip (T9) = 100%; input truncation (T7) ≤ 1%; **output truncation (T11) ≤ 1%**; generated-length JSD (T12) ≤ 2× `base` | Silent structural loss — at the input, at the output, or by the model quietly generating short |
| **G21** | Throughput sufficient for the planned Stage 2 budget | Re-plan Stage 2 or pick a faster model |
| **G22** | Chemist review (Q1): no systematic implausibility in 100 samples | Whatever they flag becomes a new metric |
| **G23** | **Noise floor established (R9, ≥3 retrains) before any model comparison** | Differences you are acting on may be init-seed noise |
| **G24** | **Loss–quality divergence epoch (F3) reported; checkpoint not selected after it** | Checkpoint chosen on validation loss while sample quality was already degrading |
| **G25** | **Learning curve vs dataset size (F6) run once** | You cannot tell whether more data or a different method is the answer |

**G9 and G10 remain the two hard stops specific to this project.** Everything else is standard practice adapted to a new chemistry. Those two are where a saponin generator either works or produces convincing molecules that are quietly the wrong compounds.

## 22. Reporting

### 22.1 Row template

```
model | corpus | pretrain | aug | temp | seeds | n_sampled | rdkit_version
§4  valid% | FCD(×b) | JSD-stereo(×b) | JSD-scaf(×b) | JSD-NP(×b) | PC1
§5  V1..V10 (embeddability, Bredt, aromaticity round-trip, …)
§6  S1..S14
§7  O1..O7 (pathway/superclass/class JSD, unclassifiable%, isglycoside%, coverage)
§8  13 property JSDs (×b)
§9  SA(×b) | RAscore | BioNavi success% | pathway-length JSD
§10 SEDiv | #Circles | scaf-div | scaf-uniq | ring-div | fg-div | outlier-bits | coverage | SNN | Frag | Scaf
§11 uniq@1k/@10k/@100k/@500k | IntDiv1 | novel% | dup% | filters%
§12 train-repro% | heldout-repro% | near-dup% | novel-scaf%
§13 NLL-test | NLL-gap | NLL by subgroup | perplexity | calibration
§14 PMO-AUC (×2 objectives) | SEDiv-retained% | sigma-range | warm-start advantage
§15 temp curve | seed variance | repetition rate
§16 vocab | OOV% | truncation% | round-trip%
§17 throughput | GPU-h | model size
§19 chemist verdict | blind-test accuracy
```

### 22.2 Controls row

Report C1–C6 in the same table. A metric where a control scores like your model is a metric with no discriminating power for this problem — drop it and say why.

### 22.3 What to compare against

Candidates against **each other** and against **`base`**. Never against published drug-like benchmark numbers: MOSES caps at 27 heavy atoms, GuacaMol at 88, and saponins routinely exceed both. Their metric *code* is reusable; their *scores* are not.

---

## 23. Changelog

**v3.0 (this version)** — expanded from 10 tiers to 19 sections across seven parts. Added: corpus readiness and data quality (§2); experimental controls including trivial-model, off-target and broken-model baselines (§3.3); chemical and physical validity beyond parsing, including 3D embeddability and Bredt's-rule checks (§5); synthesizability and **biosynthetic plausibility**, including BioNavi-NP and the TeroENZ enzyme set already in TeroKit (§9); tokenisation and sequence diagnostics (§16); engineering and operational metrics led by inference throughput (§17); governance, licensing and reproducibility (§18); a failure-mode catalogue (§20). Saponin metrics 12 → 14; gates 17 → 22. Two new references verified: [Thakkar2021], [Zheng2022].

**v3.3** — folded in [Ozcelik2025]: library size can reverse model rankings, so comparison at identical sample size is now a precondition (§3.5, §19A.1); uniqueness annotated as size-dependent (3.1); top-k/top-p separated from temperature (R2); added 2.12 substructure count and 2.13 design frequency. Also [Tom2025], which confirms the field ignores or post-processes stereochemistry and — by explicitly excluding ring isomers — establishes that S16 has no precedent.

**v3.2** — added **§15A training dynamics, overfitting and checkpoint selection** (F1–F10), covering train/validation curves, the **loss–quality divergence** that validation loss cannot catch, checkpoint-selection criteria, augmentation memorisation, the learning curve versus dataset size, and per-token-type loss. Added **§19A model comparison and the decision procedure** — noise floor from repeat retraining, a pre-registered primary/secondary/diagnostic hierarchy, an explicit decision rule, multiple-comparison handling, and a per-model record. Robustness extended with **R9–R12** (retraining variance, checkpoint sensitivity, distribution shift, data-order sensitivity). Gates G23–G25; four failure modes added. Prompted by the protocol becoming the sole evaluation standard for every model built, which requires a decision rule and not only measurements.

**v3.1** — added in response to four coverage questions. **S15–S19**: absolute configuration / enantiomer check, ring-fusion stereochemistry, position-resolved stereo accuracy, E/Z geometry, sugar ring integrity — closing a real gap, since every stereo metric inherited from the literature is *aggregate* and confirms only that stereochemistry is present, never that it is correct. **Corrected T6**: context window from max + headroom, not p95 — p95 truncates the most glycosylated 5%, which is the wrong 5% to lose. **T11/T12**: output truncation and generated-length distribution, distinct from T7 input truncation. **§7 design note**: matching an imbalanced class distribution conflicts with the diversity goal; the choice must be made and recorded before training. Gates G11b, G11c; G20 extended. Five failure modes added.

**v2.0** — reinstated uniqueness, IntDiv and novelty as failure detectors rather than banning them; added chemical ontology (NPClassifier, ClassyFire), property panel, memorisation/leakage and qualitative review; added sampling-size requirements.

**v1.0** — four tiers: baseline, core distribution learning, coverage, saponin-specific, Stage 2 fitness.

## 24. References introduced in v3.0

- **[Thakkar2021]** Thakkar, A.; Chadimová, V.; Bjerrum, E. J.; Engkvist, O.; Reymond, J.-L. (2021). *Retrosynthetic accessibility score (RAscore) — rapid machine learned synthesizability classification from AI driven retrosynthetic planning.* **Chemical Science** 12, 3339–3349. DOI: [10.1039/D0SC05401A](https://doi.org/10.1039/D0SC05401A)
- **[Zheng2022]** Zheng, S.; Zeng, T.; Li, C.; Chen, B.; Coley, C. W.; Yang, Y.; Wu, R. (2022). *Deep learning driven biosynthetic pathways navigation for natural products with BioNavi-NP.* **Nature Communications** 13, 3342. DOI: [10.1038/s41467-022-30970-9](https://doi.org/10.1038/s41467-022-30970-9). Code: [github.com/prokia/BioNavi-NP](https://github.com/prokia/BioNavi-NP); server: biopathnavi.qmclab.com
