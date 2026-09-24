# What Published Models Actually Report — A Coverage Gap Analysis

**Question asked:** analyse every published model against the v3.2 evaluation protocol, to locate the gap.
**Date:** 2026-09-23. Companion to `evaluation_protocol.md` v3.2 and `literature_review_report.md`.

---

## 0. What this is, and what it is not

**This is not a performance comparison.** I cannot score published models on the protocol's metrics. Doing so would require obtaining each model's weights, generating ≥100,000 molecules from each, and computing ~150 metrics — none of which is possible from here, and inventing numbers the papers never reported would be the single worst failure mode for a document meant to govern your model selection.

**This is a reporting-coverage analysis.** For each published model and each section of the protocol, it records whether anyone has *ever measured that thing* — and what they found where they did. That answers "where is the gap" precisely, by separating three categories:

| Category | Meaning for you |
|---|---|
| **Field standard** | Everyone reports it; you will be compared on it; tooling exists |
| **Rare** | Someone has done it; you can cite precedent and reuse code |
| **Never done** | No published generative model reports it. **You would be first — and there is no baseline to compare against** |

That third category is the actual answer to your question, and it is larger than I expected.

### Confidence marking

My knowledge of what each paper reported varies by how much of it I read. Every row is marked:

- **[F]** full text or substantial sections read this session
- **[P]** partial — results tables or abstract plus search excerpts
- **[A]** abstract level only

Treat **[A]** rows as provisional. I have not inflated confidence to make the table look complete.

---

## 1. The headline

Of the protocol's ~150 metrics, published generative models collectively report **roughly 25–30**, and those cluster almost entirely in two sections: core distribution learning (§4) and failure detectors (§11).

**Nine of the protocol's nineteen sections have no published generative-model precedent at all.**

The most comprehensive published evaluation of a molecular generative model that I verified is [Skinnider2021], which computed **23 metrics** across 8,447 models. That is the field ceiling, and it covers §4, §8 and §11 well — and nothing else in this protocol.

---

## 2. Coverage by protocol section

| § | Section | Published coverage | Best precedent | Verdict |
|---|---|---|---|---|
| **2** | Corpus readiness | Partial — curation described, rarely *measured* | [Skinnider2021] **[F]** documents salt stripping, neutralisation, element whitelist, rare-token filtering, 250-char cap; [Chandrasekhar2025] **[P]** documents COCONUT curation | **Practice exists, metrics do not.** Nobody reports corpus-quality numbers as evaluation |
| **3** | Design: splits, controls | **Weak.** Scaffold splits rare in generative work; controls almost absent | [Skinnider2021] **[F]** used 10 replicates × 11 sizes × 4 databases — the strongest design I found | **Gap.** I found no generative paper using an off-target or broken-model control |
| **4** | Core distribution learning | **Field standard** | [Skinnider2021] **[F]** — all five, and the source of the ρ≥0.80 selection | Covered. You will be judged here |
| **5** | Physical validity beyond parsing | **Near-absent in 2D.** 3D papers report a related but different thing | [Hoogeboom2022] **[P]**, [Xu2023] **[P]** report *atom/molecule stability* from geometry | **Gap.** 3D embeddability, Bredt's rule, aromaticity round-trip: no precedent found |
| **6** | Saponin-specific (S1–S19) | **None. Zero.** | — | **Total gap.** No published generative model reports glycosylation rate, sugar identity, anomeric validity, or ring-fusion stereochemistry |
| **7** | Chemical ontology | **None in generative evaluation** | [Kim2021] **[P]** built NPClassifier; I found no generative paper using it to evaluate outputs | **Gap and opportunity.** The tool exists, MIT/CC0 — nobody has pointed it at generated molecules |
| **8** | Property panel | **Field standard** | [Skinnider2021] **[F]** — JSD over 17 properties; [Polykovskiy2020] **[P]** — 4 | Covered |
| **9** | Synthesizability / biosynthesis | **Synthetic: common. Biosynthetic: none** | SA score widely reported; [Thakkar2021] **[P]** RAscore; [Zheng2022] **[F]** BioNavi-NP exists but not as generative evaluation | **Gap.** Biosynthetic plausibility of *generated* molecules: no precedent |
| **10** | Coverage and diversity | **Partial — improving recently** | [Thomas2024] **[P]** SEDiv, scaffold/FG/ring diversity, outlier bits; [Renz2024] **[P]** #Circles | Covered for newer metrics; older papers report only IntDiv |
| **11** | Failure detectors | **Field standard, and over-relied upon** | Everyone | Covered — see §4 below on why this is a problem |
| **12** | Memorisation / leakage | **Weak.** Novelty universal; the diagnostic forms rare | Novelty everywhere; exact-reproduction and near-duplicate rates occasionally | **Gap.** I found no generative paper reporting a train/test leakage audit or augmentation-leakage check |
| **13** | Likelihood / calibration | **Aggregate only** | NLL/perplexity standard in LM-style papers | **Gap.** NLL *by subgroup* — the metric that predicts Stage 2 friction — no precedent found |
| **14** | Optimisability | **Recently strong** | [Gao2022] **[F]** PMO, AUC top-10 over 25 algorithms × 23 tasks; [Guo2024] **[F]** | Covered. Best-developed area outside §4 |
| **15** | Robustness / sampling | **Partial, recently improved** | [Özçelik2025] **[F]** temperature vs top-k/top-p, library-size effects | Partly covered; retraining variance still rare |
| **15A** | Training dynamics / overfitting | **Standard in ML, absent as *molecular* evaluation** | Loss curves ubiquitous; loss–quality divergence rarely examined | **Gap.** Per-token-type loss and the divergence epoch: no precedent found |
| **16** | Tokenisation diagnostics | **Described, not measured** | [Skinnider2021] **[F]** describes tokenisation precisely; reports no OOV or truncation metric | **Gap.** Truncation rate, round-trip fidelity, two-digit ring closures: no precedent |
| **17** | Engineering / operational | **Occasional, unsystematic** | [DeCao2018] **[P]** reports ~5× training-time advantage | **Gap.** Inference throughput — the real Stage 2 constraint — essentially never reported |
| **18** | Governance / licensing | **Essentially never** | — | **Total gap** |
| **19** | Qualitative review | **Illustrative, not systematic** | Most papers show hand-picked structures | **Gap.** Blind real-vs-generated testing: no precedent found |
| **19A** | Comparison / decision rule | **One paper, very recent** | [Özçelik2025] **[F]** — the first serious treatment I found | **Newly opened.** See §5 |

---

## 3. Per-model assessment

Ordered by relevance to your project. "Protocol sections touched" counts sections where the paper reports *something*, not full coverage.

| Model | Confidence | Reports | Sections touched | The gap for your purposes |
|---|---|---|---|---|
| **Low-data CLM benchmark** [Skinnider2021] | **[F]** | 23 metrics incl. all five §4, 17 property JSDs, % stereocentres, internal/external diversity, novelty, uniqueness | §4, §8, §10(partial), §11, §2(practice) | **The field ceiling, and it stops at §8.** No ontology, no saponin metrics, no Stage-2 fitness, no tokenisation metrics. Its % stereocentres is the *only* stereo metric in routine use, and it is aggregate |
| **GuacaMol** [Brown2019] | **[P]** | Validity, uniqueness, novelty, KL, FCD + goal-directed suite | §4, §11 | Five distribution metrics. No stereochemistry beyond none; dataset caps at 88 heavy atoms |
| **MOSES** [Polykovskiy2020] | **[P]** | Valid, unique@1k/@10k, novelty, FCD, SNN, Frag, Scaf, IntDiv1/2, Filters, 4 properties | §4, §8, §10, §11 | Broader than GuacaMol on similarity; **dataset caps at 27 heavy atoms** — structurally irrelevant to saponins |
| **MolScore / moleval** [Thomas2024] | **[P]** | SEDiv, scaffold uniqueness/diversity, FG and ring-system diversity, outlier bits, purchasability, analogue similarity | §10, §11 | **The best coverage-metric suite available** and the one to adopt. Still nothing saponin-specific or Stage-2-fitness related |
| **PMO** [Gao2022] | **[F]** | AUC top-10 vs oracle calls, 25 algorithms × 23 tasks | §14 | The only rigorous optimisability benchmark. Drug-like objectives only |
| **Augmented Memory** [Guo2024] | **[F]** | PMO AUC, Tanimoto distributions, UMAP, IntDiv1, scaffold-purge diversity | §14, §11 | Documents RL mode collapse; **no quantitative analysis of prior-drift thresholds** — the σ sweep in P5 remains uncharted |
| **Evaluation-choices study** [Özçelik2025] | **[F]** | Library-size effects on FCD/FDD/uniqueness; temperature vs top-k/p; substructure-count metric | §15, §19A, §3 | **The closest thing to a decision procedure in the literature.** See §5 |
| **NPGPT** [Sakano2024] | **[P]** | FCD 1.290 vs LSTM 1.794 on COCONUT; distribution comparison | §4 | **The most NP-relevant prior, evaluated on essentially one metric.** No stereochemistry, no glycoside analysis, no ontology |
| **S4 CLM** [Ozcelik2024] | **[A]** | Benchmarked across drug-discovery tasks incl. NP design; prospective kinase validation | §4, §14(partial) | Benchmarked on NP design but the metric detail is not something I verified |
| **Low-data TL** [Moret2020] | **[P]** | Validity, novelty vs Enamine 700M, scaffold novelty, FCD | §4, §12(partial) | Novelty-focused; no stereochemistry despite NP framing |
| **Stereochemistry-aware generation** [Tom2025] | **[P]** | Isomeric ECFP similarity, docking, CD spectra, optimisation AUC | §14, partial stereo | **The one paper dedicated to stereochemistry — and it explicitly excludes ring isomers.** See §4 |
| **REINVENT 4** [Loeffler2024] | **[P]** | Framework; task-specific metrics | §14 | Reference implementation rather than an evaluated model |
| **JT-VAE** [Jin2018] | **[P]** | 100% validity, reconstruction accuracy, property optimisation | §4(partial) | Validity by construction; **stereochemistry is post-hoc RDKit enumeration plus re-ranking**, not learned or measured |
| **MolGAN** [DeCao2018] | **[P]** | Validity 98–100%, uniqueness ~2%, novelty >97%, druglikeness/synthesisability/solubility, ~5× training-time advantage | §4(partial), §11, §17(partial) | One of the few to report a timing number. QM9-scale only |
| **DiGress** [Vignac2023] | **[F]** | Validity, uniqueness, novelty, FCD, SNN, Scaf, Filters, KL | §4, §10(partial), §11 | Evaluated on MOSES/GuacaMol; **states some complex molecules could not be round-tripped graph↔SMILES at all** |
| **EDM / GeoLDM / MolDiff** [Hoogeboom2022, Xu2023, Peng2023] | **[P]** | Atom stability, molecule stability, validity, uniqueness | §5(adjacent), §11 | Molecule stability is the nearest thing to a physical-validity metric in the field — but it is geometry-derived and drug-scale |
| **Large-molecule VAE** [Ochiai2023] | **[A]** | Not verified | — | Still the open Cycle-2 read |

---

## 4. The nine sections with no published precedent

This is the answer to "where is the gap."

### 4.1 Saponin-specific structure (§6, S1–S19) — the total gap

**No published generative model reports any of it.** Not glycosylation rate, not sugars per molecule, not monosaccharide identity, not anomeric configuration validity, not ring-fusion stereochemistry, not O-/C-glycoside ratio.

This is consistent with the review's finding that no saponin-, triterpenoid-glycoside- or steroidal-glycoside-specific generative model exists, and with [Liu2025]'s explicit statement that NP-specific generation strategies **and evaluation systems** are still needed.

**Consequence:** you have no baseline. There is no published number to compare S3 or S4 against. Your A↔B reference (§3.1) is not merely good practice here — it is the *only* available comparator.

### 4.2 Stereochemistry beyond aggregate — sharper than I expected

[Tom2025] is the one paper dedicated to stereochemistry-aware string-based generation. It states plainly that current generative models "either ignore stereochemistry or consider it as a postprocessing step after molecule generation" — a citable confirmation that the field treats this as an afterthought.

But its own scope is the finding that matters for you: it covers "E/Z geometric diastereomers and R/S diastereomers and enantiomers" and **explicitly excludes axial chirality and ring isomers**, on a ZINC15 drug-like subset.

> **Ring isomers are exactly the triterpenoid case.** The A/B, B/C and C/D ring-fusion stereochemistry that determines a saponin aglycone's 3D shape is excluded from the only paper that takes stereochemistry seriously. Protocol metric **S16 has no precedent anywhere**, and the gap is not an oversight in my reading — it is a stated scope boundary in the state of the art.

### 4.3 Chemical ontology in generative evaluation (§7)

NPClassifier [Kim2021] is published, MIT/CC0 and Dockerised. I found **no generative paper using it to evaluate generated molecules.** The tool and the need both exist; the connection has not been made. This is the cheapest novel contribution available to you.

### 4.4 Biosynthetic plausibility (§9.2)

BioNavi-NP [Zheng2022] exists and reports 90.2% pathway success on real natural products. I found no generative paper using it — or anything like it — to assess whether *generated* molecules are biosynthetically reachable. For a natural-product generator this is arguably the most meaningful validity question, and it is unasked.

### 4.5 Five more, briefly

| Gap | Status |
|---|---|
| **Physical validity (§5)** — 3D embeddability, Bredt's rule | 3D papers report geometry-derived stability; no 2D generative paper reports embeddability |
| **NLL by subgroup (§13)** | Aggregate NLL standard; the disaggregated form that predicts Stage 2 friction, absent |
| **Tokenisation metrics (§16)** | Tokenisation is *described* carefully and *measured* almost never |
| **Engineering (§17)** | Inference throughput — the binding constraint on Stage 2 — essentially unreported |
| **Governance (§18)** | No precedent found |

---

## 5. What [Özçelik2025] changes — and a correction it forces

Published 2025, and the closest thing in the literature to §19A. Its findings bear directly on the protocol:

| Finding | Effect on the protocol |
|---|---|
| FCD and FDD **decrease with library size**, plateauing only above 10⁴–10⁵ designs; libraries rank differently by size | **Confirms §3.5.** My ≥100,000-sample requirement was inferred from [Skinnider2021]'s stability observation; this is direct evidence. **Strengthened: always compare at identical library size, regardless of architecture** |
| **Uniqueness decreases as library size increases**, causing models to rank differently across scales; recommend treating it as a "sanity check" only | **Independent confirmation of the Tier 11 position.** Exactly the correction you pushed me to make — and it supports reporting uniqueness as a *curve*, since the curve is the artefact |
| Frequently-generated molecules are often simple substructures — benzene, amine, ether — "unsuitable for prospective studies" | **New.** Design *frequency* is itself a quality signal; frequent ≠ good |
| Top-k and top-p with restrictive parameters cause mode collapse; **temperature sampling remains superior** for diversity control | **Refines R2.** Protocol treated top-k/top-p and temperature as parallel sweeps; they are not equivalent |
| "Number of substructures" is size-invariant and ~85× faster than clustering | **New metric worth adopting** alongside SEDiv |

**The correction:** the protocol's §19A says to establish a noise floor from repeat *retraining*. That remains right, but [Özçelik2025] shows a second confounder I had not accounted for — **library size changes model rankings**. Two models compared at different sample sizes can swap places for reasons unrelated to quality. Fixed sample size is now a precondition of comparison, not merely a reporting detail.

---

## 6. What this means for the project

1. **On ~25–30 metrics you will be compared to the field.** Cover §4, §8, §10, §11 properly and use standard implementations — MolScore, MOSES metric code, `CLMeval`.

2. **On the rest, there is no baseline, so build your own.** The A↔B reference is not optional. For §6 and §7 especially, "how does this compare to published work" has no answer other than your own reference distribution.

3. **Three contributions are genuinely novel and cheap**, in order of effort:
   - **NPClassifier applied to generated molecules** (§7). Tool exists, licence permissive, nobody has done it.
   - **Saponin-specific structural metrics** (§6). Nobody has any of them.
   - **Biosynthetic plausibility of generated structures** (§9.2), using BioNavi-NP or the TeroENZ enzyme set already inside TeroKit.

4. **S16 — ring-fusion stereochemistry — is the sharpest gap.** The one paper dedicated to stereochemistry-aware generation excludes ring isomers by design, and ring fusion is what defines a triterpenoid skeleton's shape. If you implement one novel metric, this is the one with the clearest claim to being first.

5. **The field's evaluation habits are themselves a finding.** The two most-reported metrics — uniqueness and novelty — are the two that two independent sources now say should not be used for ranking [Skinnider2021, Özçelik2025]. Your protocol is already ahead of common practice on this. That is worth stating explicitly if this work is written up.

---

## 7. What would close the remaining uncertainty

Rows marked **[A]** and several **[P]** rest on abstracts and search excerpts, not full texts. To make this analysis publication-grade:

| Priority | Action |
|---|---|
| 1 | Read [Ochiai2023] in full — still the open Cycle-2 gating item |
| 2 | Verify [Ozcelik2024] S4's reported metric set for the NP design tasks |
| 3 | Systematically check the metric tables of ~10 recent NP-generative papers rather than relying on the ones this review surfaced |
| 4 | Confirm the "no generative paper uses NPClassifier for evaluation" claim with a citation search on [Kim2021] — I searched but cannot claim exhaustiveness |

**Item 4 matters most.** It is the strongest novelty claim in this document and rests on my not having found something. Absence of evidence in a bounded search is weaker than a citation-graph check.
