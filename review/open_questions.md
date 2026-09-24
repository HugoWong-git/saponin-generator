# Open Questions — Cycle 2 Agenda

**Last updated:** 2026-09-24, after the first live corpus and prior audit.

> **Material change since Cycle 1:** the corpus is **~40,000 TeroKit triterpenoids/saponins**, not the several hundred originally assumed. Q4 is superseded by Q4a/Q4b/Q4c below; Q1–Q3 are unaffected.

> **Material change 2026-09-24:** `audit_corpus.py` has now been **executed**, against `data/saponin_train_46k_valid.smi` (45,966 molecules) with RDKit 2026.3.6. **Q4a and Q4b are closed.** Two new gating items, **Q4d and Q4e**, replace them — both are defects in the *implementation* rather than open questions in the literature, and both are measured rather than projected. Q1–Q3 remain gating and untouched. Full numbers: `corpus_and_prior_audit.md`.

Items are ordered by how much they could change the §7 adapt-vs-build recommendation. Q1–Q3 are gating: the brief requires them closed before the recommendation stops being provisional.

---

## Coverage gaps against the brief's minimum bar

The brief requires ≥3 SMILES/CLM papers, ≥2 graph VAE/GAN papers, ≥2 diffusion papers, plus any NP/saponin-specific work, before a final recommendation.

| Category | Required | Covered in depth | Status |
|---|---|---|---|
| SMILES / chemical language models | 3+ | 7 ([Skinnider2021], [Skinnider2024], [Moret2020], [Amabilino2020], [Loeffler2024], [Ozcelik2024], [Bagal2022]) | ✅ **Met** |
| Graph VAE / GAN | 2+ | 2 ([Jin2018], [DeCao2018]) — but [Ochiai2023] and HierVAE are abstract-level only | ⚠️ **Nominally met, substantively weak** — see Q1 |
| Diffusion (2D + 3D) | 2+ | 4 ([Vignac2023], [Hoogeboom2022], [Xu2023], [Peng2023]) | ✅ **Met** |
| NP / saponin-specific | all findable | [Sakano2024], [Liu2025], [Merk2018], [Skinnider2021] metabolome models; [Zheng2019] found but not read | ⚠️ **Read [Zheng2019]** — see Q5 |

---

## Q1 — [PRIORITY] Does [Ochiai2023] change the graph-VAE verdict? *(gating)*

**Why it matters.** §3.3 rules out graph VAEs partly on the grounds that they were designed for small molecules. [Ochiai2023] is a VAE built *specifically* for large molecular structures with 3D complexity, and explicitly motivated by the failure of CG-VAE, JT-VAE and HierVAE on exactly that problem. It is the single paper most likely to overturn a Cycle 1 conclusion, and it has only been read at abstract level.

**To extract:** maximum molecule size handled; training set and size; whether stereochemistry is represented and how; reconstruction accuracy vs JT-VAE/HierVAE at large sizes; low-data behaviour; code availability and licence; whether any natural products were in the evaluation set.

**Decision impact:** if it handles saponin-sized, stereochemistry-bearing molecules well in a low-data regime, §7 needs a genuine second candidate rather than a single recommended family.

---

## Q2 — [PRIORITY] HierVAE / hgraph2graph on its own terms *(gating)*

Currently a single table row sourced from a repository README and a third-party description. Needs the primary paper (Jin, Barzilay & Jaakkola, *Hierarchical Generation of Molecular Graphs using Structural Motifs*, ICML 2020 — **to be verified**).

**To extract:** motif vocabulary construction and whether it would cover triterpenoid ring systems and pyranose/furanose sugars; maximum molecule size; stereochemistry handling; low-data behaviour.

**Decision impact:** closes the graph-VAE coverage gap properly and tests the "vocabulary derived from training set" objection in §3.3.

---

## Q3 — [PRIORITY] Re-resolve the authorship of [CarbCofolding2026] *(gating on citation integrity, not on the decision)*

ACS returned 403; PMC and PubMed served CAPTCHA pages; Crossref and Europe PMC rate-limited. Venue, volume, issue, page, PMID and PMCID are confirmed, but the author list is not, and the substantive finding was read from an indexed excerpt rather than the full text.

**Route for Cycle 2:** retry Crossref/Europe PMC once rate limits reset; or locate a preprint; or find the paper cited with full authors in a later article's reference list (the route that worked for [Ochiai2023], [Mercado2020] and [ArusPous2019] this cycle).

**Decision impact:** none on the recommendation — it corroborates [SweetFold2026] rather than carrying an independent claim. But R2 in the risk register leans on it, so it should not go into a write-up unresolved.

---

## Q4 — [SUPERSEDED 2026-09-23, replaced by Q4a/Q4b] Dataset size

The original question assumed ~several hundred structures from COCONUT/KNApSAcK. **The corpus is ~40,000 triterpenoids and saponins from TeroKit/TeroMOL** [Zeng2020, Chen2023]. The size question is answered; what replaces it is composition and quality, below.

---

## Q4a — [RESOLVED 2026-09-24] What is the aglycone : glycoside split? *(was gating)*

**Answer: 40.58% glycosides (18,654) / 59.42% aglycones (27,312), n = 45,966.**

`audit_corpus.py` was run for the first time against a live RDKit install
(2026.3.6) and completed without error on all records. Full numbers in
`corpus_and_prior_audit.md` §2.

Glycosides are a minority, as feared — but 18,654 is close to the 21,993-molecule
plant-metabolome model [Skinnider2021] and two orders of magnitude above the
~190-molecule transfer-learning floor [Amabilino2020]. **The feared outcome — a
glycoside subset too small to fine-tune — does not occur. Stage 2 is viable.**

The two subpopulations are chemically distinct: mean MW 987.7 vs 515.1, mean ring
count 8.2 vs 5.0. **The corpus is bimodal and its median molecule has zero
sugars.** This bimodality turns out to matter more than the ratio itself — see Q4d.

**Caveat on provenance.** The file audited is `data/saponin_train_46k_valid.smi`
from the `saponin-generator` repository (45,966 SMILES), whose README describes it
as "compiled from published literature". The handoff describes the corpus as a
~40,000-molecule TeroKit/TeroMOL pull. These may or may not be the same
extraction; the correspondence has **not** been verified. R11 is answered for the
file that is actually training the model, which is the operative one.

---

## Q4b — [RESOLVED 2026-09-24] Is stereochemistry preserved? *(was gating)*

**Answer: yes at the corpus level — 87.5% of molecules carry a tetrahedral
marker; 65.71% fully specified, 24.68% partial, 9.61% flat.** Median 10 defined
stereocentres per molecule (p95 = 33).

**The §5 argument survives at the corpus level. It does not survive the
pipeline.** See Q4e — the trained model emits zero stereochemistry regardless.

The residual 34.3% that is flat or partial still warrants a policy decision before
any retraining: it teaches the model that stereocentres may be left unspecified,
at a mean of 2.44 undefined centres per molecule (p95 = 15).

---

## Q4d — [NEW 2026-09-24] The 128-token cap is a glycoside-selective filter *(gating on the implementation, not the literature)*

**Measured.** The trained checkpoints declare `max_sequence_length = 128` tokens,
a value set in **none** of the configs — it is inherited unchanged from the
upstream `reinvent_pubchem.prior`. Tokenised with REINVENT's own scheme, **41.4%
of glycosides exceed it against 0.7% of aglycones**; the cap sits essentially at
the median glycoside length (122 tokens).

Direct sampling from the epoch-3 prior (10,000 molecules) confirms the
consequence: generated glycoside fraction **23.38%** against 40.58% in training,
sugars per molecule **0.38** against 1.27, and molecules with ≥4 sugars **0.23%**
against 14.7% — a 64-fold collapse concentrated exactly where the cap bites. 5.46%
of sequences hit the cap without emitting an end token.

This is R9 realised as a measured defect rather than a projected risk, and it
vindicates the §7.2 correction (context window = max × 1.2, **not** p95): p95 here
is 170 tokens, which would still truncate the most glycosylated molecules.

**To do:** set `max_sequence_length` explicitly to ~410 (corpus max 342 × 1.2) and
retrain. This must precede any glycoside-only staging, or the cap removes 41.4% of
that subset.

---

## Q4e — [NEW 2026-09-24] The pipeline strips stereochemistry end-to-end *(gating on the implementation)*

**Measured.** Of 8,858 valid generated molecules, **zero** contain a stereocentre,
against 87.5% of the corpus. This is not sampling variance: the model assigns mean
probability **6.6 × 10⁻⁹** per step to the 18 stereo tokens present in its own
vocabulary, and that probability *decreases* monotonically from epoch 1 to epoch 4
— further transfer learning makes it more certain the tokens never occur.

Two compounding causes, one confirmed and one inferred:
- **Confirmed:** every sampling config sets `isomeric_smiles = false`, flattening
  output on write.
- **Inferred:** the base PubChem prior was trained on non-isomeric SMILES and the
  transfer-learning step is not presenting isomeric SMILES to override it. This has
  **not** been confirmed by instrumenting REINVENT's data loader, which would
  require installing REINVENT4.

**Decision impact: high, and it lands on the review's central claim.** §5 argues
for SMILES *because* it carries stereochemistry natively. That argument is correct
about the representation and about the corpus, and is being nullified by
configuration. For molecules whose sugars differ from one another only by
stereochemistry, glucose and galactose are indistinguishable in this model's output
by construction. R7/R12 are live.

**To do:** confirm the loader behaviour, retrain on isomeric SMILES, set
`isomeric_smiles = true`. The vocabulary already contains the needed tokens, so no
vocabulary change is required.

---

## Q4c — Is the wider terpenome worth using as pretraining data, and which subset?

TeroMOL holds ~180,000 molecules in total [Chen2023]; ~140k sit outside the triterpenoid/saponin pull. §6 argues this is worth using as a Stage 0 pretraining corpus, on the grounds that data volume dominates [Skinnider2021] and that a terpenome-wide corpus is more homogeneous than COCONUT.

**Open sub-questions, all empirical:**
1. Does a 180k terpenome prior beat a 695k COCONUT prior for this target? (More homogeneous but smaller.)
2. Does including C10/C15 terpenoids help or hurt, given the size mismatch with glycosylated C30 triterpenoids? Compare a full-terpenome prior against a large-classes-only (di-/sester-/tri-/steroid/meroterpenoid) prior. This is R13.
3. Is COCONUT-then-TeroMOL sequential pretraining better than either alone?

**Decision impact:** medium. Affects the quality ceiling rather than the feasibility of the approach.

---

## Q5 — Does QBMG [Zheng2019] constitute prior art?

"Quasi-biogenic molecule generator with deep recurrent neural network" — surfaced via the reference list of [Skinnider2021] but not read. It is a natural-product-adjacent RNN generator and therefore a candidate for "most directly comparable prior work".

**To extract:** what "quasi-biogenic" covers and whether it includes glycosides; training set and size; metrics; whether stereochemistry was retained; code availability.

---

## Q6 — Is there a pretrained checkpoint for the [Skinnider2021] plant-metabolome model?

The plant metabolome CLM (21,993 molecules) is conceptually the closest published model to saponin chemistry. Code and training data are released; **checkpoint availability is unverified**. A released checkpoint would be a better starting prior than NPGPT for a plant-glycoside target.

**Route:** check the Zenodo deposits (10.5281/zenodo.4641960 for data, 10.5281/zenodo.4642099 for code) and the GitHub repository for weights.

---

## Q7 — 2025–2026 systematic surveys not yet read

The brief asks specifically what newer systematic surveys conclude about narrow, NP-like datasets. Two are identified but unread:

- **[Ozcelik2025]** *Generative Deep Learning for de Novo Drug Design — A Chemical Space Odyssey* (JCIM 2025).
- **[vanTilborg2024]** *Deep learning for low-data drug discovery: Hurdles and opportunities* (Curr Opin Struct Biol 2024) — the most on-topic title found for the central question of this review.

Also worth a look: *MolGenBench* (bioRxiv 2025) — application-oriented benchmark across 120 targets; likely drug-design-only but may contain transferable methodology.

---

## Q8 — Is there any generative work on glycosides or glycoconjugates at all?

Cycle 1 found none targeting saponins, triterpenoid glycosides or steroidal glycosides, and [Liu2025] corroborates that NP application cases are scarce. Before concluding "no prior art" in a write-up, search specifically for:

- generative models for **glycans / oligosaccharides** as molecules in their own right (distinct from the structure-prediction work in [SweetFold2026]);
- generative or enumerative models for **glycosylation patterns** on a fixed aglycone — this is arguably closer to the saponin problem than whole-molecule generation, and would inform the §7.3 hybrid-tokenizer proposal;
- **cardiac glycoside / steroidal glycoside** computational design;
- **ginsenoside** computational work (dammarane saponins are the best-studied saponin subclass and the most likely place for a one-off model to exist).

---

## Q9 — Does anyone evaluate anomeric configuration in generated structures?

§7.3 claims no published metric evaluates α/β correctness, and R2 and R10 both depend on that gap being real. The claim is currently an absence-of-evidence, not a verified absence.

**Route:** search carbohydrate cheminformatics validation literature (e.g. PDB carbohydrate validation tooling, `privateer`, glycan structure-validation papers) for a reusable α/β check before building one from scratch.

---

## Q10 — Sample efficiency of S4 versus RNN at a few hundred molecules

[Ozcelik2024] benchmarks S4 on NP design tasks, but the review has not established how S4 behaves at the *specific* data scale of this project. [Skinnider2021]'s finding that architecture barely matters was established for RNNs only and may not extend across architecture families.

**To extract:** the smallest dataset S4 was fine-tuned on; any direct RNN-vs-S4 comparison at small scale; parameter count and compute requirements versus a 3-layer LSTM.

---

## Resolved in Cycle 1 (kept for traceability)

- ~~SMILES vs SELFIES for the prior~~ → **Resolved: SMILES.** [Skinnider2021] and [Skinnider2024] agree; [Subramanian2023] shows the string model beating JT-VAE on distribution matching even when handicapped with SELFIES.
- ~~Minimum transfer-learning dataset size~~ → **Resolved: ≥190 molecules** [Amabilino2020], with [Moret2020] demonstrating TL from as few as 5 in the extreme case.
- ~~Which metrics to trust~~ → **Resolved:** the five well-behaved metrics from [Skinnider2021] plus SEDiv/outlier-bits from [Thomas2024]; uniqueness and IntDiv excluded ([Skinnider2021], [Renz2024]).
- ~~Identity of the sphere-exclusion-diversity paper~~ → **Resolved: [Renz2024]**, not the `Koch2024` key used in the first draft.
- ~~Authorship of [SweetFold2026]~~ → **Resolved: Sundar & Yang 2026**, bioRxiv 10.64898/2026.07.16.738959.
