# Stage 1 Distribution-Learning Prior for Diverse Saponin Generation — Literature Review

**Status:** Cycle 1 complete, citation-verification pass applied (2026-09-22); **dataset-size revision applied 2026-09-23** after the corpus was identified as ~40,000 TeroKit triterpenoids/saponins rather than the several hundred originally assumed — §6, §7 and §8 were rewritten, and two recommendations (augmentation factor, from-scratch viability) reversed. Adapt-vs-build recommendation is **provisional** — see §7 and `open_questions.md`.
**Scope of Cycle 1:** all six model families covered at survey depth; SMILES/CLM family covered in depth; natural-product-specific and glycoside-specific work covered in depth.
**Citation convention:** short keys `[AuthorYear]` resolve against `bibliography.md` / `bibliography.bib`.
**Verification convention:** claims marked **⚠️UNVERIFIED** were not confirmed against the primary source in this cycle and must not be relied on for the decision. Where a reference's *authorship* could not be confirmed, the key is topic-based (e.g. `[CarbCofolding2026]`) and `bibliography.md` says so explicitly — no author name in this report is a guess.
**Corrections in this pass:** the sphere-exclusion-diversity paper was mis-keyed as `Koch2024` (a fabricated attribution) in the first draft; it is **[Renz2024]** (Renz, Luukkonen & Klambauer). See `progress_log.md`.

---

## 1. Executive summary

Five findings dominate the evidence gathered in Cycle 1, and together they largely determine the Stage 1 architecture choice.

1. **Data, not architecture, is the binding constraint in the low-data regime.** In the largest systematic low-data benchmark available (~8,500 models trained, >4 billion molecules evaluated), varying RNN hyperparameters — embedding size, hidden size, depth, dropout, batch size — almost never changed performance as much as changing the training set size did [Skinnider2021]. This single result argues strongly against investing effort in a custom architecture.

2. **The 40,000-molecule TeroKit corpus sits above every published training floor.** It is ~200x the minimum for effective transfer learning onto a pretrained SMILES RNN (**at least 190 molecules** [Amabilino2020]) and ~1.8x the plant-metabolome corpus that [Skinnider2021] used to learn a model reproducing its target chemical space almost exactly (21,993 molecules). **Training a prior directly on this corpus is viable**, which the first draft of this review — working from an assumed few hundred molecules — wrongly ruled out. Transfer learning is still recommended, but it now has to beat a from-scratch control rather than being the only option. What replaces dataset size as the binding constraint is dataset *composition*: the aglycone-to-glycoside ratio, which is unmeasured (§6).

3. **Saponin-like chemistry is the hardest case in the published benchmarks.** Models trained on COCONUT (the natural-product database) never exceeded **82% valid SMILES**, versus saturation near 100% for GDB/ZINC-like chemistry [Skinnider2021]. Complexity costs data: a ChEMBL model needed 500,000 molecules to match a GDB model trained on 25,000 [Skinnider2021].

4. **Stereochemistry and glycosidic configuration are a genuine, documented weak point — and the weakness is worst in exactly the model families that are otherwise fashionable.** Graph and 3D-diffusion models generally discard stereo descriptors entirely; SMILES models retain them syntactically but are not explicitly supervised on them. Independent work on glycans states plainly that SMILES-based encodings "fail to robustly represent monosaccharide identity, anomeric state (α/β configuration), glycosylation topology (N-, O-), and stereochemistry" [SweetFold2026], and a 2026 audit found systematic glycan stereochemistry errors in deep-learning cofolding outputs [CarbCofolding2026].

5. **No generative model targeting saponins, triterpenoid glycosides or steroidal glycosides was found.** The closest directly comparable prior work is NP-wide: **NPGPT** [Sakano2024], a GPT-style CLM fine-tuned on COCONUT, and the metabolome CLMs of [Skinnider2021]. A 2025 review of generative models for natural-product structural modification states explicitly that application cases in the NP field are scarce and that NP-specific generation strategies and evaluation systems are still needed [Liu2025].

**Provisional recommendation (see §7 for reasoning and §8 for risks): adapt, do not build.** Specifically: a SMILES chemical language model (RNN/LSTM or S4, or a decoder-only transformer), pretrained on a large terpenoid or natural-product corpus (TeroMOL's ~180k terpenome and/or COCONUT's 695k), then transfer-learned onto the 40k triterpenoid/saponin set and optionally onto the glycosylated subset — using **isomeric** SMILES throughout, with **low** randomized-SMILES augmentation at this corpus size, and with a from-scratch model on the 40k as the control. Do not use SELFIES. Do not use 2D graph or 3D diffusion models for Stage 1.

---

## 2. Master comparison table

Metric abbreviations: V = validity, U = uniqueness, N = novelty, FCD = Fréchet ChemNet Distance (lower is better in its raw form; GuacaMol reports a transformed score where higher is better), KL = GuacaMol KL-divergence score, IntDiv = internal diversity, SNN = similarity to nearest neighbour, Scaf/Frag = MOSES scaffold/fragment cosine similarity.

| Method | Family / representation | Data regime validated | Key reported metrics | Pros | Cons | Availability | Relevance to saponins |
|---|---|---|---|---|---|---|---|
| **SMILES LSTM (GuacaMol baseline)** [Brown2019] | RNN / SMILES | ChEMBL-24, 1,591,378 molecules | V 0.959, U 1.000, N 0.912, KL 0.991, FCD 0.913 | Best overall distribution learner in the GuacaMol baseline panel; closely reproduces training-set properties | Some invalid SMILES; large training set used | GuacaMol open-source (BenevolentAI) | **High** — reference point for what a well-trained CLM achieves |
| **REINVENT 4** [Loeffler2024] | RNN + transformer / SMILES | ChEMBL, PubChem priors; production use at AstraZeneca | Framework paper; per-task metrics not a single headline number | Apache 2.0; TL + RL + curriculum learning in one tool; documented, maintained, reference implementation; prior→TL→RL staging matches the user's two-stage plan exactly | Framework rather than a novel model; pretrained priors are drug-like (ChEMBL/PubChem), not NP | github.com/MolecularAI/REINVENT4, **Apache 2.0** | **Very high** — most likely Stage 1+2 backbone |
| **Low-data CLM benchmark** [Skinnider2021] | 3-layer RNN (GRU/LSTM) / SMILES, DeepSMILES, SELFIES | 200–500,000 molecules × 4 databases incl. **COCONUT**; 8,447 models | V 6.7% @1k → 69.1% @25k (ZINC); **COCONUT never >82% V**; 5 well-behaved metrics: %valid, FCD, **%stereocentres**, Murcko scaffolds, NP-score | The single most decision-relevant paper found; quantifies data floors per chemical space; identifies which metrics actually track model quality | RNN-only (no transformer/graph/diffusion comparison); metabolome case study used 15k–22k molecules, not hundreds | github.com/skinnider/low-data-generative-models; CLMeval R package; data on Zenodo | **Very high** — COCONUT is the closest published proxy for saponin chemistry |
| **Invalid-SMILES study** [Skinnider2024] | RNN + transformer / SMILES vs SELFIES | ChEMBL/GDB-13 subsets, 30k & 300k | SMILES beat SELFIES on Murcko-scaffold JSD (p=3.6e-6) and NP-likeness JSD (p=1.8e-9); stereocentre JSD n.s. (p=0.10) | Causal evidence that invalid SMILES act as a self-filter for low-likelihood samples; settles the SMILES-vs-SELFIES question | Single-author study; stereocentre result is the one metric where SMILES did *not* significantly win | Open access (Nat Mach Intell) | **Very high** — directly informs representation choice |
| **MolGPT** [Bagal2022] | Decoder-only transformer / SMILES | MOSES + GuacaMol (~1.6M / ~1.3M) | On par with contemporaries for V/U/N; conditional control of logP, TPSA, SA, QED | Small (~6M params **⚠️UNVERIFIED**); conditional generation built in; widely cited | Trained on drug-like space; no NP or stereo-specific evaluation found | Open-source (per [Liu2025] classification) | Medium — architecture template, not a reusable prior |
| **S4 CLM** [Ozcelik2024] | Structured state space / SMILES | Benchmarked incl. **natural-product design tasks** | Superior capacity to learn complex molecular properties while exploring diverse scaffolds; 8/10 prospective kinase designs predicted highly active | Explicitly benchmarked on NP design; strong global-sequence modelling (relevant for long saponin SMILES) | Newer, smaller community than RNN/transformer; no NP pretrained checkpoint identified | github.com/molML/s4-for-de-novo-drug-design | **High** — strongest alternative to an RNN prior for long strings |
| **NPGPT** [Sakano2024] | GPT-style CLM (smiles-gpt, ChemGPT) fine-tuned / SMILES + SELFIES | Pretrained PubChem-10M; **fine-tuned on COCONUT** | SMILES model FCD **1.290** to the NP distribution vs LSTM baseline **1.794** | The most directly comparable published prior: an NP-domain CLM with released fine-tuned checkpoints | NP-wide, not saponin-specific; no stereochemistry analysis found | github.com/ohuelab/npgpt, **MIT license**, COCONUT-finetuned checkpoints released | **Very high** — candidate starting checkpoint |
| **Moret low-data CLM** [Moret2020] | LSTM + BatchNorm / SMILES | ChEMBL24 pretrain; TL from as few as **5 natural products** (MEGx) | >99% of generated molecules new vs Enamine (700M); new-scaffold fraction rose 75%→>95% during TL | Demonstrates NP-directed transfer learning at extreme low data; open-access tool | Extreme-low-data TL biases hard toward the seed molecules; duration of TL is not principled | github.com/ETHmodlab/virtual_libraries | **High** — proof that NP-directed TL works at the scale the user has |
| **TL guidelines** [Amabilino2020] | GRU-RNN / SMILES | Varying TL set sizes | **≥190 molecules needed for effective GRU-RNN transfer learning** | Gives the concrete lower bound for the user's dataset question; warns against heavy post-filtering by similarity (introduces bias) | Drug-like datasets, not NP | Paywalled (ACS); SI freely available | **Very high** — the dataset-size answer |
| **JT-VAE** [Jin2018] | Graph VAE over junction tree of substructures | ZINC-250k (240k molecules) | 100% validity by construction | Valid by construction; interpretable substructure vocabulary | Vocabulary built from ZINC (780 substructures **⚠️UNVERIFIED**) — will not contain saponin ring systems/sugars without rebuilding; stereochemistry handled only as a **post-hoc re-ranking** of RDKit-enumerated stereoisomers; designed for small molecules and does not scale to large structures [Ochiai2023] | github.com/wengong-jin/icml18-jtnn (superseded by hgraph2graph) | **Low** — post-hoc stereo selection is the wrong mechanism for anomeric configuration |
| **HierVAE / hgraph2graph** [Jin2018 repo] | Hierarchical graph VAE | ChEMBL 1.8M | — | Developed specifically to extend VAEs to larger structures [Ochiai2023] | Not independently evaluated for NP/stereo in this cycle | github.com/wengong-jin/hgraph2graph | Medium — **⚠️UNVERIFIED**, promote to Cycle 2 |
| **Large-molecule 3D-complexity VAE** [Ochiai2023] | VAE / chemical latent space | Designed for **large molecular structures with 3D complexity** | — | Explicitly motivated by the failure of CG-VAE/JT-VAE/HierVAE on large complex compounds | Details not extracted in this cycle | Commun Chem, open access | **High (potential)** — closest graph/VAE work to the saponin size-and-complexity problem; **read in full in Cycle 2** |
| **MolGAN** [DeCao2018] | GAN + RL on dense graph tensors | **QM9 only** (≤9 heavy atoms) | V 98–100%, **U ≈ 2%**, N >97% | 5× faster training than ORGAN; near-100% validity | **Severe mode collapse** (uniqueness ~2%); fixed maximum graph size; QM9-scale only | github.com/nicola-decao/MolGAN | **Very low** — disqualifying for a diversity-maximising prior |
| **GraphNVP** [Madhawa2019] | Invertible flow / graph | ZINC-250k, QM9 | High uniqueness without domain heuristics | Not evaluated at saponin scale | Flows cannot omit minor graph variations (cited as the reason uniqueness beats MolGAN) | Open-source **⚠️UNVERIFIED** | Low |
| **GraphINVENT** [Mercado2020] | Autoregressive GNN / graph | ChEMBL-scale **⚠️UNVERIFIED** | Outperformed by DiGress on most MOSES metrics except hard-coded validity [Vignac2023] | Graph-native, no SMILES syntax burden | Hard-codes validity rules; **⚠️UNVERIFIED** details | github.com/MolecularAI/GraphINVENT **⚠️UNVERIFIED** | Low-Medium |
| **DiGress** [Vignac2023] | Discrete denoising diffusion / 2D graph | MOSES (1.9M), **GuacaMol (1.3M)** | GuacaMol: V 85.2, V.U.N. 85.1, KL 92.9, FCD score 68.0. MOSES: V 85.7, U 100, N 95.0, Filters 97.1, FCD 1.19, SNN 0.52, **Scaf 14.8** | First one-shot graph diffusion model to scale to GuacaMol; strong novelty | Authors state **"SMILES seem to be the most efficient molecular representation"**; extrapolates on GuacaMol but "completely fails" on MOSES; very low scaffold similarity (14.8); complex GuacaMol molecules could not be round-tripped graph↔SMILES for evaluation | github.com/cvignac/DiGress | **Low** — validity ceiling and scaffold mismatch both worse than a CLM, in a far larger data regime |
| **EDM** [Hoogeboom2022] | E(3)-equivariant diffusion / 3D point cloud | QM9 (≤29 atoms); GEOM-Drugs (≤181 atoms, mean 44.4) | More bond-prediction errors on GEOM-Drugs than QM9; molecule stability ≈0% on the DRUG set for all methods [Xu2023] | Foundational 3D generative model; conditional variants exist | Bonds inferred post hoc from geometry; effectively no stable molecules at drug size, let alone saponin size; no stereo/sugar handling | Open-source | **Very low** for Stage 1 |
| **GeoLDM** [Xu2023] | Latent equivariant diffusion / 3D | QM9, GEOM-Drugs (~450k molecules) | Up to 7% validity improvement for large-molecule generation over prior 3D methods | Latent space reduces cost vs atom-space diffusion | Still reports molecule stability ≈0% and uniqueness ≈100% on DRUG (metrics omitted as uninformative) | Open-source | **Very low** for Stage 1 |
| **MolDiff** [Peng2023] | Joint atom+bond diffusion / 3D | GEOM-Drugs | 3× improvement in success rate over prior 3D diffusion | Diagnoses and fixes the atom–bond inconsistency problem | Still drug-scale; 3D conformer data required — unavailable at scale for saponins | github.com/pengxingang/MolDiff | **Very low** for Stage 1 |
| **MOSES** [Polykovskiy2020] | Benchmark | ZINC Clean Leads, **8–27 heavy atoms** | Defines V, U, N, FCD, SNN, Frag, Scaf, IntDiv, Filters | Standardised metric implementations reusable on any dataset | **The dataset excludes saponin-sized molecules entirely** — MOSES *scores* are not transferable, though MOSES *metric code* is | github.com/molecularsets/moses | Metrics: high. Scores: not transferable |
| **GuacaMol** [Brown2019] | Benchmark | ChEMBL-24, **2–88 heavy atoms** | V, U, N, KL, FCD | Closer to saponin size range than MOSES; distribution-learning + goal-directed suites | Still drug-like chemistry; holdout construction is drug-similarity-based | github.com/BenevolentAI/guacamol | Metrics: high |
| **MolScore / moleval** [Thomas2024] | Benchmark/eval framework | — | Adds **SEDiv**, scaffold uniqueness/diversity, functional-group & ring-system diversity, **outlier bits**, purchasability | Supplies exactly the diversity metrics the user's Stage 1 goal requires; internal diversity is known to misrank chemical-space coverage [Renz2024] | Drug-design oriented defaults | github.com/MorganCThomas/MolScore, PyPI | **Very high** — recommended evaluation stack |

---

## 3. Family-by-family synthesis

### 3.1 RNN/LSTM SMILES chemical language models

This family is the most thoroughly characterised in the low-data regime, and it is the only family with published results on natural-product chemical space at multiple dataset sizes.

[Skinnider2021] is the pivotal study. Training 8,447 RNNs across ZINC, GDB-13, ChEMBL and COCONUT at eleven dataset sizes from 200 to 500,000 molecules, it establishes three facts that bear directly on the saponin problem. First, validity is a steeply increasing function of dataset size — 6.7% valid at 1,000 ZINC molecules, 69.1% at 25,000, saturating around 50,000 — and this curve is *shifted unfavourably* for complex chemistry: **COCONUT models never exceeded 82% valid SMILES at any training-set size**. Second, performance declines linearly below 1,000 molecules, which led the authors to conclude that RL- or TL-based strategies may remain the only viable options at the smallest sizes. Third, and most consequential for build-vs-adapt, a systematic sweep of six hyperparameters across 1,210 models showed that hyperparameter tuning almost never mattered as much as training-set size; GRUs and LSTMs performed roughly identically, and only "vanilla" RNNs were substantially worse.

The same study identified the single most effective low-data intervention: **data augmentation by non-canonical SMILES enumeration** [Bjerrum2017, ArusPous2019]. Augmenting 10× gave a performance increase comparable to quadrupling the number of unique training molecules; 30× augmentation let a model trained on 5,000 molecules match one trained on 50,000 canonical SMILES. Critically, the study also flags a caveat that applies directly to saponins: in the *most structurally complex* databases, very high augmentation factors sometimes *degraded* models learned from large training sets. Augmentation is a low-data tool, and its optimal factor must be tuned, not assumed.

[Moret2020] shows the extreme end of the same idea. Using an LSTM pretrained on ChEMBL24 and fine-tuned on as few as five dissimilar natural products from the MEGx collection, it generated molecules with >99% novelty against the 700M-compound Enamine set, with the fraction of novel scaffolds rising from 75% to over 95% during transfer learning. The mechanism is exactly the Stage-1-then-Stage-2 structure the user proposes.

[Amabilino2020] supplies the number the user asked for: **at least 190 molecules** are needed for effective GRU-RNN transfer learning. It also issues a warning worth heeding in Stage 2 — extensive post-filtering of generated molecules by similarity metrics should be avoided, because it introduces new biases into candidate selection.

**Verdict for saponins:** this family is the default. It is the only one with published evidence at the right dataset size, on the right kind of chemistry, with the right training procedure.

### 3.2 Transformer and state-space chemical language models

[Bagal2022] (MolGPT) established that a decoder-only transformer trained on next-token prediction over SMILES performs on par with the then-current field on MOSES and GuacaMol, with the added benefit of conditional property control. [Loeffler2024] (REINVENT 4) folds RNN and transformer generators into one framework alongside transfer learning, reinforcement learning and curriculum learning, under a permissive **Apache 2.0** licence — an important practical consideration given the user's eventual Stage 2.

[Ozcelik2024] introduces S4 (structured state space sequence) models to de novo design and, uniquely among the architecture papers surveyed, **benchmarks explicitly on natural-product design tasks**. S4's advantage is its capacity to learn global properties of long sequences — a property with obvious relevance to saponins, whose isomeric SMILES strings are long (multiple fused rings plus branched oligosaccharide chains with many stereocentres, easily exceeding the string lengths typical of drug-like molecules).

[Sakano2024] (NPGPT) is the most directly comparable published work to the user's Stage 1. Two pretrained GPT-style models — smiles-gpt (SMILES) and ChemGPT (SELFIES), both pretrained on PubChem-10M — were fine-tuned on COCONUT. The SMILES-based model achieved an FCD of **1.290** to the natural-product distribution, outperforming an LSTM baseline at 1.794. Code and the COCONUT-fine-tuned checkpoints are released under the **MIT licence**. This is a credible, license-clean starting point: a prior already adapted to NP chemical space, requiring only a second, narrower transfer-learning step onto saponins.

**Verdict for saponins:** competitive with, and possibly preferable to, the RNN family — especially S4 for long strings and NPGPT as a ready NP-adapted checkpoint. The decisive consideration is that all three are *string* models and therefore inherit the representation properties analysed in §4.

### 3.3 VAEs (SMILES-based and graph-based)

Graph VAEs solve the validity problem by construction and pay for it in flexibility. [Jin2018] (JT-VAE) decomposes each molecule into a junction tree over a substructure vocabulary derived from the training set, then reassembles molecules with a graph message-passing network, guaranteeing chemical validity at every step. The critical detail for this project is **how JT-VAE handles stereochemistry**: it generates a 2D structure, enumerates all stereoisomers with RDKit's `EnumerateStereoisomers`, encodes each, and picks the one whose embedding is most cosine-similar to the latent code. This is a post-hoc ranking over an enumerated set — it does not *learn* stereochemistry, and its cost grows combinatorially. A saponin with 10–15 stereocentres across an aglycone plus two or three sugars has a stereoisomer count in the thousands; the paper's own justification ("on average only few atoms could have stereochemical variations") does not hold for this chemistry.

[Ochiai2023] is explicit that CG-VAE and JT-VAE "were all designed for small molecules and could not handle large compound structures due to their high spatial order", and that HierVAE was developed in response. That paper — a VAE-based chemical latent space built specifically for *large molecular structures with 3D complexity* — is the most promising unexplored lead from Cycle 1 and should be read in full in Cycle 2.

A useful data point on focused/small datasets comes from [Subramanian2023], which compared RNN+SELFIES against JT-VAE on small, domain-focused patent-derived datasets using the GuacaMol distribution-learning suite. The result cuts two ways. JT-VAE won decisively on **novelty** (0.89–1.00 vs 0.55–0.58) and had perfect validity and uniqueness by construction. But the **string model matched the target distribution far better**: RNN+SELFIES scored KL 0.96–0.98 and FCD 0.60–0.61, against JT-VAE's KL 0.75–0.87 and FCD 0.28–0.32 (GuacaMol-transformed scores, higher is better). Both figures are well below the ~0.9 typical of large drug datasets, which the authors attributed to the training sets being smaller and more domain-focused than the data these metrics were calibrated on.

Two lessons for the saponin project. First, this is precisely the regime the project occupies, and it is a warning that **absolute FCD will look poor regardless of architecture** — rank models against each other, not against published drug-like numbers. Second, JT-VAE's novelty advantage here is not the win it appears to be: a graph VAE that generates 100% novel molecules while matching the training distribution half as well as a string model is exploring *away* from the target chemistry, which for a Stage 1 prior meant to reproduce saponin-likeness is a defect rather than a feature. Note also that the string model in this comparison used SELFIES — the representation [Skinnider2021] and [Skinnider2024] both find inferior to SMILES — so a SMILES CLM would be expected to widen the distribution-matching gap further.

**Verdict for saponins:** not recommended for Stage 1. Validity-by-construction is bought at the price of a training-set-derived substructure vocabulary and post-hoc stereochemistry — both of which fail on saponins.

### 3.4 GANs

[DeCao2018] (MolGAN) is the canonical entry and is disqualifying on its own terms for a diversity-maximising prior. It achieves 98–100% validity on QM9 but with a **uniqueness score of roughly 2%** — the authors describe the models as collapsing even in the RL-only case, and implement early stopping on uniqueness as a mitigation. It is also constrained to a fixed maximum graph size of 9 atoms in the reported experiments. GuacaMol's baseline panel tells the same story from a different angle: ORGAN scored 0.379 validity, 0.267 KL and **0.000 FCD** on distribution learning [Brown2019].

**Verdict for saponins:** rule out. Mode collapse is the exact failure mode a Stage 1 diversity prior cannot tolerate.

### 3.5 Autoregressive and flow-based graph models

[Madhawa2019] (GraphNVP) makes an instructive architectural point: invertible flows cannot omit minor graph variations, because every encoding must be analytically invertible, which is why they achieve far higher uniqueness than MolGAN. [Mercado2020] (GraphINVENT) is the practical autoregressive-GNN entry, and is the graph baseline DiGress compares against. Details for both remain **⚠️UNVERIFIED** in this cycle.

**Verdict for saponins:** deferred; no evidence yet that either handles stereochemistry or saponin-scale graphs.

### 3.6 Diffusion models (2D graph and 3D equivariant)

Two sub-families, both currently unsuitable for Stage 1, for different reasons.

**2D graph diffusion.** [Vignac2023] (DiGress) is the strongest entry: the first one-shot graph model to scale to GuacaMol's 1.3M molecules. Its own results contain the argument against using it here. On GuacaMol it reaches 85.2% validity where the SMILES LSTM baseline reaches 95.9% [Brown2019], and the paper states directly that "SMILES seem to be the most efficient molecular representation". On MOSES it achieves a scaffold similarity of only 14.8. Extrapolation behaviour is unstable — capable on GuacaMol, "completely fails" on MOSES, which the authors attribute to MOSES's homogeneous molecule sizes. Most tellingly for saponins, the paper notes that some GuacaMol molecules *could not be mapped from graphs back to SMILES for evaluation at all*, concluding that "more efficient tools for processing complex molecules as graphs are therefore needed". That is the saponin case, in a training regime three orders of magnitude larger than the one available here.

**3D equivariant diffusion.** [Hoogeboom2022] (EDM) generates atom positions and types, then infers bonds post hoc; the authors found more bond errors on GEOM-Drugs (up to 181 atoms, mean 44.4) than on QM9. [Xu2023] (GeoLDM) reports that on the DRUG dataset, molecule stability and uniqueness metrics are *omitted entirely* because they are near 0% and near 100% respectively for all methods — that is, essentially no generated drug-sized molecule is stable. [Peng2023] (MolDiff) diagnoses this as the atom–bond inconsistency problem and achieves a 3× success-rate improvement by generating atoms and bonds jointly, which is real progress but still leaves 3D diffusion at drug scale. Saponins are larger than the GEOM-Drugs mean, require a 3D conformer corpus that does not exist for this class at scale, and carry stereochemistry that 3D models represent only implicitly through geometry.

**Verdict for saponins:** rule out for Stage 1. Revisit only if Stage 2 requires 3D-conditioned optimisation.

---

## 4. Sub-question 1 — Which pretrained priors overlap saponin chemical space, and what adaptation would they need?

**Direct NP-space overlap:**

- **NPGPT** [Sakano2024] — fine-tuned on COCONUT, which is the natural-product database that includes triterpenoid and steroidal glycosides. Checkpoints released (MIT). Adaptation required: a second transfer-learning pass on the saponin set. This is the minimum-effort path.
- **The metabolome CLMs of** [Skinnider2021] — bacterial (15,292), fungal (15,453) and **plant (21,993)** metabolite models, trained with LSTM + high-factor SMILES enumeration. The plant metabolome model is conceptually the nearest neighbour to saponin chemistry. Code and training data are released; the trained checkpoints' availability is **⚠️UNVERIFIED**.
- **REINVENT 4 priors** [Loeffler2024] — ChEMBL/PubChem, i.e. drug-like, *not* NP. Overlap with saponin space is poor, but the framework supports training a new prior from an NP corpus directly, which is the recommended use.

**Corpus availability for adaptation.** COCONUT 2.0 [Chandrasekhar2025] contains **695,133 unique natural product structures** aggregated from 63 sources, and is openly downloadable (SDF/CSV/database dump). Its stereochemistry statistics are directly relevant: 82,220 molecules without stereocentres, **539,350 with preserved stereochemistry**, and 73,563 with stereocentres but without absolute stereochemistry. Note the database's own design decision — each entry represents a "flat" NP structure with known stereochemical forms attached as associated information. **Any saponin pipeline must extract the stereo-resolved forms explicitly, not the flat parent structures.**

**Estimated adaptation cost.** Pretraining a CLM on COCONUT-scale data (~700k molecules) is a single-GPU-days-scale job by the standards of [Skinnider2021], which trained thousands of such models. Fine-tuning on a few hundred saponins is minutes. The expensive part of this project is not compute; it is curation of a stereochemically correct saponin training set.

---

## 5. Sub-question 2 — Stereochemistry and glycosidic configuration, per architecture

This is the sharpest differentiator between families, and the evidence is unusually clear.

| Architecture | Stereo mechanism | Assessment for anomeric α/β configuration |
|---|---|---|
| SMILES CLM (RNN/transformer/S4) | Stereo descriptors (`@`, `@@`, `/`, `\`) are ordinary tokens; learned statistically from isomeric SMILES | **Best available option.** Stereo is representable and learnable, but not explicitly supervised. [Skinnider2021] found **"% stereocentres"** to be one of only five metrics robustly correlated with model quality — meaning stereo fidelity *is* measurable and *does* track training data volume. |
| SELFIES CLM | 100% syntactic validity by grammar | **Not recommended.** SELFIES models match the target chemical space worse than SMILES models at equal data [Skinnider2021], and substantially more SELFIES are needed to reach equivalent quality. [Skinnider2024] confirms the SMILES advantage on scaffold and NP-likeness distributions, though notably the stereocentre-fraction difference was *not* significant (p=0.10) — so SELFIES' deficit is not primarily a stereo deficit. |
| Graph VAE (JT-VAE) | Post-hoc: enumerate all stereoisomers with RDKit, pick the best-matching by latent cosine similarity [Jin2018] | **Poor.** Combinatorially expensive and structurally unprincipled for molecules with 10+ stereocentres. |
| 2D graph diffusion (DiGress) | Node/edge categorical attributes; stereo descriptors are not part of the standard graph attribute set | **Poor** — stereochemistry is generally discarded in the graph pipeline. |
| 3D diffusion (EDM/GeoLDM/MolDiff) | Stereochemistry implicit in 3D coordinates | **Poor in practice.** Bonds are inferred post hoc from geometry [Hoogeboom2022]; molecule stability ≈0% at drug scale [Xu2023]. Getting the geometry right enough to imply correct anomeric configuration is a harder problem than the generation itself. |

**External evidence on glycosidic bonds specifically.** The glycan-modelling literature is blunt about the limits of general-purpose representations. [SweetFold2026] states that when glycans are encoded as generic ligands, SMILES graphs or CCD monomers "fail to robustly represent monosaccharide identity, anomeric state (α/β configuration), glycosylation topology (N-, O-), and stereochemistry", and addresses this by parsing condensed glycan IUPAC notation into annotated glycan chains rather than using SMILES at all.

The *mechanism* they identify is the part that should worry this project most. SMILES-based inputs "represent glycans as a large single residue object, leading to context dilution"; without monosaccharide-level chemical information preserved, "sugars with similar compositions but different stereochemistry can collapse into most trained common entities" — concretely, galactose and mannose being conflated with the more prevalent glucose. **That failure mode maps directly onto saponins**, whose sugar moieties are overwhelmingly glucose, galactose, rhamnose, xylose and arabinose — a set of near-isomeric hexoses and pentoses distinguished largely by stereochemistry, with glucose by far the most frequent. A SMILES model that quietly regresses rare sugars toward glucose would produce structures that pass every validity check while being systematically wrong in exactly the dimension the project cares about. Caveat: SweetFold is a *structure-prediction* model, not a generative one, so this is an argument by mechanism rather than a demonstrated generative failure — but the representational cause is shared, and it is the strongest available argument for the glycan-aware tokenizer proposed in §7.3. [CarbCofolding2026] independently audits deep-learning cofolding tools and reports systematic glycan stereochemistry errors across canonical-SMILES input variants.

**Counter-evidence — carbohydrates are learnable with the right data.** [Pesciullesi2020] showed that transfer learning enables the Molecular Transformer to predict **regio- and stereoselective reactions on carbohydrates**. This is a reaction-prediction task rather than distribution learning, but it demonstrates that a SMILES-based transformer can acquire carbohydrate stereochemical competence given targeted fine-tuning data. This is the strongest available reason for optimism about a SMILES prior for saponins.

**Practical implication for Stage 1:** use isomeric SMILES, retain the plan to measure **% stereocentres JSD** and, additionally, construct a bespoke **anomeric-configuration validity check** (parse each generated glycosidic bond, verify α/β assignment is chemically well-formed). No published metric does this; this is a genuine gap the project should fill.

---

## 6. Sub-question 3 — Minimum dataset sizes for transfer learning onto a narrow class

Ordered from most to least conservative:

| Source | Reported threshold | Setting |
|---|---|---|
| [Amabilino2020] | **≥190 molecules** for effective GRU-RNN transfer learning | Drug-like, GRU-RNN, TL from a generic prior |
| [Moret2020] | TL demonstrated from **as few as 5** dissimilar natural products | LSTM pretrained on ChEMBL24; extreme-low-data regime; heavy bias toward seeds |
| [Skinnider2021] | **<1,000** molecules → performance declines linearly; direct training not viable; TL/RL "may remain the only viable options" | Direct (non-TL) training, four databases incl. COCONUT |
| [Skinnider2021] | **~15,000–22,000** molecules sufficient to learn a full metabolome model *directly* with 30× SMILES augmentation | Bacterial/fungal/plant metabolomes |

**Where the dataset actually sits (revised 2026-09-23).** The corpus is **~40,000 triterpenoids and saponins retrieved from TeroKit / TeroMOL** [Zeng2020, Chen2023], not the "several hundred" assumed in the first draft of this review. That is a different regime, and it changes the analysis materially:

- It is **~200x above** Amabilino's 190-molecule transfer-learning floor. The TL-feasibility question is no longer close.
- It is **~1.8x the size of the plant metabolome model** in [Skinnider2021] (21,993 molecules), and about 2.6x the bacterial and fungal sets. All three learned to reproduce their target chemical spaces well enough that generated and real metabolites overlapped almost completely in UMAP projection. **Direct training on the 40k set is therefore squarely inside the range with published support** — it is no longer contraindicated, it is a legitimate baseline that must be run.
- It is still **~17x smaller** than COCONUT 2.0 (695,133) and ~33x smaller than the GuacaMol and MOSES training sets, so this is not a regime in which graph diffusion or 3D models become viable. The family verdicts in §3 are unchanged.

**The binding constraint moves.** Under the low-data framing the question was whether a prior could be trained at all. At 40k it can, so the question becomes *what the 40k is made of* — specifically the **aglycone : glycoside ratio**. TeroMOL spans mono-, sesqui-, di-, tri- and sesterterpenoids, meroterpenoids and steroids, and does include glycosides [Chen2023], but a "triterpenoid and saponin" pull will contain a large fraction of **bare aglycones carrying no sugar at all**. Aglycones teach the model triterpenoid ring systems; only the glycosylated subset teaches it glycosylation — which sugars appear, at which positions, in which anomeric configuration, and in what chain lengths. If the glycosylated subset is, say, 6,000 of the 40,000, then the saponin-specific part of the problem is being learned from 6,000 examples and the §5 stereochemistry concerns apply at *that* number, not at 40,000. **This ratio is now the single most important unmeasured quantity in the project** — the audit script shipped with this report measures it.

**Using the rest of the terpenome as pretraining data.** TeroMOL holds roughly 180,000 terpenome molecules in total [Chen2023], so the ~140k beyond the triterpenoid/saponin pull is available. The evidence says this is worth using, as a **pretraining** stage rather than as training data mixed into the target set:

- Data volume is the dominant lever on CLM quality [Skinnider2021], so a 180k pretraining corpus is materially better than a 40k one for learning SMILES syntax, ring-closure and stereo-descriptor conventions.
- A terpenome-wide corpus is **more homogeneous** than COCONUT, and [Skinnider2021] found CLMs learn more readily in homogeneous regions of chemical space. A 180k terpenome prior may therefore transfer better to triterpenoids than a 695k all-natural-product prior, despite being roughly 4x smaller — this is a testable and genuinely interesting ablation rather than a settled point.
- The obvious mismatch is molecular size: mono- and sesquiterpenoids (C10, C15) are far smaller than a C30 triterpenoid bearing an oligosaccharide chain. [Skinnider2021] warns specifically that conclusions drawn on small-molecule databases (GDB) may not transfer to complex molecules, and DiGress's instability was attributed to homogeneous molecule sizes in its training set [Vignac2023]. For *pretraining* this matters less than it would for direct training, but it argues for including the larger classes (di-, sester-, triterpenoids, steroids, meroterpenoids) preferentially over the C10/C15 classes if a choice must be made.

This yields a **three-stage curriculum** — terpenome-wide, then triterpenoid/saponin, then glycosylated-only — which [Loeffler2024] supports natively. See §7.1.

**The homogeneity caveat now cuts favourably.** [Skinnider2021] found that CLMs succeed far more readily in *homogeneous* regions of chemical space: performance decreased as the diversity of the training sample increased. Triterpenoids are a narrow class by natural-product standards (a limited set of skeletons: oleanane, ursane, lupane, dammarane, cycloartane, spirostane), which is favourable, and at 40k there is enough data to cover that space densely. The countervailing factor is sugar combinatorics, which are diverse. The net effect remains untested and is worth measuring directly: compute the corpus's internal diversity and compare against the diversity-stratified curves in [Skinnider2021].

**One published ceiling still applies.** COCONUT-trained CLMs never exceeded 82% valid SMILES at *any* training-set size [Skinnider2021], including 500,000. That ceiling reflects natural-product structural complexity, not data scarcity, so 40k does not buy past it. Expect a validity ceiling in that region and budget generation overhead accordingly (R1).

---

## 7. Decision recommendation (provisional) — Adapt, do not build

### 7.1 Recommendation

**Adapt an existing SMILES chemical language model prior. Do not build a custom architecture for Stage 1.**

> **Revised 2026-09-23 for the 40k-molecule corpus.** The direction of the recommendation is unchanged — adapt a SMILES chemical language model — but the reasoning and the recipe have both changed. At several hundred molecules, transfer learning was the *only* supported option. At 40,000 it is no longer forced, so it now has to earn its place against a from-scratch baseline. It still does, but the margin is an empirical question rather than a foregone conclusion, and the risk profile is different (see §8).

Concretely, the recommended configuration is:

1. **Representation:** isomeric SMILES, stereo descriptors retained. Not SELFIES. Not graphs. Not 3D. *(Unchanged — this rests on [Skinnider2021] and [Skinnider2024], neither of which is dataset-size dependent.)*

2. **Training curriculum — three stages, each a legitimate stopping point:**
   - **Stage 0, pretrain:** the terpenome-wide TeroMOL corpus (~180k [Chen2023]), or COCONUT 2.0 (695k [Chandrasekhar2025]), or COCONUT followed by TeroMOL. Prefer the larger terpenoid classes if subsetting.
   - **Stage 1, adapt:** the 40k triterpenoid + saponin set.
   - **Stage 2, specialise:** the glycosylated subset only, if it proves large enough to fine-tune on without collapse (≥190 by [Amabilino2020], but the more relevant precedent is that thousands, not hundreds, is where complex-NP models become reliable [Skinnider2021]).

   [Loeffler2024] supports staged transfer and curriculum learning natively, so all three stages live in one toolchain.

3. **Run the from-scratch baseline.** Train the same architecture on the 40k set alone, with no pretraining. At several hundred molecules this would have been pointless; at 40k it is a real contender — [Skinnider2021] learned usable metabolome models from 15k–22k — and it is the control that tells you whether pretraining bought anything. **If it matches the pretrained model, prefer it**: a model trained only on in-domain data carries no drug-like or non-terpenoid bias to fight in Stage 2.

4. **Architecture:** 3-layer LSTM or GRU as the baseline [Skinnider2021]; S4 [Ozcelik2024] as the primary challenger for long strings; a decoder-only transformer [Bagal2022] third. **Unchanged, and the case is now stronger**: [Skinnider2021]'s finding that architecture barely matters relative to data volume was established across 1,210 models at exactly this kind of scale.

5. **Augmentation — this recommendation has reversed.** The first draft advised sweeping randomized-SMILES enumeration across {3x, 10x, 20x, 30x} and expecting high factors to win. That was correct for a few hundred molecules. At 40k it is probably wrong: [Skinnider2021] found that for the *most structurally complex* databases, high augmentation factors **degraded** models learned from large training sets, and that augmentation's benefit was "attenuated completely" by 500k. A triterpenoid corpus at 40k sits in exactly the region where over-enumeration starts to bite. **Sweep {1x, 2x, 3x, 5x, 10x} and expect the optimum to be low** — quite possibly no augmentation at Stage 0/1, with augmentation reserved for a small Stage 2 glycoside set.

6. **Evaluation:** the five well-behaved metrics from [Skinnider2021] (% valid, FCD, % stereocentres, Murcko scaffolds, NP-score), plus SEDiv and outlier-bits from MolScore [Thomas2024], plus a **per-sugar composition histogram** (R10). Do not rely on uniqueness or internal diversity [Skinnider2021, Renz2024].


### 7.2 Reasoning, tied to evidence

| Criterion | Evidence | Implication |
|---|---|---|
| **Data availability** | **Revised:** 40k triterpenoids/saponins from TeroKit — ~200x the 190-molecule TL floor [Amabilino2020] and ~1.8x the plant-metabolome model that learned its space successfully [Skinnider2021] | TL is no longer *forced*. Both TL and from-scratch are supported; run both and compare |
| **Architecture ROI** | Hyperparameter/architecture variation almost never matched training-set size in effect [Skinnider2021] | Custom-architecture effort has low expected return |
| **Stereochemistry** | String models represent stereo natively; graph and 3D models discard or post-hoc it (§5) | SMILES CLM |
| **Representation choice** | SMILES beats SELFIES on distribution matching at equal data [Skinnider2021, Skinnider2024]; invalid SMILES act as a beneficial self-filter [Skinnider2024] | Isomeric SMILES, filter invalid outputs post hoc |
| **Molecule size** | MOSES caps at 27 heavy atoms; GuacaMol at 88; GEOM-Drugs means 44. Saponins commonly exceed all three | Graph/3D benchmarks do not cover the target size class |
| **Compute cost** | [Skinnider2021] trained 8,447 CLMs, many at or above 40k molecules; 3D diffusion at GEOM scale is far more expensive | CLM. At 40k a full curriculum plus a from-scratch control plus an augmentation sweep is still a days-scale job, not weeks |
| **Licensing** | REINVENT 4 **Apache 2.0**; NPGPT **MIT**; S4 codebase public; MolScore open-source | No licensing obstacle on the recommended path |
| **Community support & Stage 2 fit** | REINVENT 4 integrates TL, RL and curriculum learning in one framework, in production use [Loeffler2024] | Stage 1 and Stage 2 share one toolchain |
| **Fit to saponin complexity** | COCONUT models cap at 82% validity [Skinnider2021]; DiGress cannot even round-trip some complex GuacaMol molecules [Vignac2023] | Expect a lower validity ceiling than drug-like benchmarks report — plan for it, don't chase it |

### 7.3 Where "build custom" retains a legitimate claim

Three narrow cases. None justifies inventing a new *architecture*, but each is a legitimate custom component, and at 40k molecules all three become more tractable than they were under the low-data assumption — there is now enough data to train and evaluate them properly:

1. **A glycan-aware tokenizer.** [SweetFold2026] demonstrates the principle for structure prediction: parse the sugar portion in a glycan-native notation rather than as generic SMILES. A hybrid tokenizer — aglycone as SMILES, glycosylation pattern as structured tokens — is genuinely novel and addresses a documented representational failure. **This is the single most defensible custom contribution available.**
2. **Anomeric-configuration validity metrics.** No published metric evaluates α/β correctness in generated structures. Building one is cheap and necessary.
3. **A saponin-specific evaluation suite.** MOSES and GuacaMol scores are not transferable (§2). The project needs its own reference distributions.

**Caveat on the recommendation:** it now rests on a dataset described in conversation but not yet inspected — the 40k figure, its aglycone:glycoside split and its stereochemical completeness are all unverified against the actual file. Run the audit script before committing. Separately, the review has not yet covered ≥2 graph VAE/GAN papers at the depth the brief requires (JT-VAE and MolGAN are covered; HierVAE and [Ochiai2023] are not), and [Ochiai2023] is specifically about large, 3D-complex molecules and could change the graph-VAE assessment. **Treat §7 as provisional until Cycle 2 closes that gap.**

---

## 8. Risk register

Risks that would carry over into the saponin use case under the recommended approach, plus the main risks of the rejected alternatives.

### 8.1 Risks inherited by adopting a SMILES CLM prior

| # | Risk | Evidence | Severity | Mitigation |
|---|---|---|---|---|
| R1 | **Validity ceiling.** COCONUT-trained CLMs never exceeded 82% valid SMILES; saponins are at the complex end of COCONUT | [Skinnider2021] | High | Accept it. Oversample and filter — invalid outputs are a *beneficial* low-likelihood filter [Skinnider2024]. Budget ~1.5–2× generation overhead. |
| R2 | **Stereochemistry errors invisible to validity checks.** An RDKit-parseable SMILES with a wrong anomeric configuration is "valid" | [SweetFold2026], [CarbCofolding2026] | **High** | Build the custom anomeric-validity checker (§7.3). Track % stereocentres JSD [Skinnider2021]. |
| R3 | **Over-enumeration.** High SMILES augmentation factors degraded models on structurally complex databases learned from **large** training sets, and the benefit was attenuated completely by 500k | [Skinnider2021] | **Raised to High at 40k** (was Medium at ~hundreds) | Sweep {1x, 2x, 3x, 5x, 10x} and expect a low optimum. Reserve heavy augmentation for a small Stage 2 glycoside set. This reverses the first draft's advice. |
| R4 | **FCD is miscalibrated for this chemistry.** ChemNet was trained on drug-like bioactivity data; small focused datasets produce poor FCD regardless of architecture | [Preuer2018], [Subramanian2023] | Medium | Use FCD for *relative* model ranking only. Never report an absolute FCD as a quality claim. |
| R5 | **Mode collapse onto seed molecules during TL.** Extreme-low-data TL biases hard toward the fine-tuning set; TL duration has no principled stopping rule | [Skinnider2021], [Moret2020] | **Lowered to Low-Medium at 40k** (was Medium-High at ~hundreds) — 40k is far from the regime where [Moret2020]-style seed bias dominates. **Still Medium-High for Stage 2** if the glycoside subset is small | Monitor SEDiv and scaffold diversity per stage [Thomas2024]; early-stop on diversity, not loss. Applies mainly to Stage 2. |
| R6 | **Uniqueness and IntDiv will look excellent and mean nothing.** All models generated unique molecules at >99%; IntDiv misranks chemical-space coverage | [Skinnider2021], [Renz2024] | Medium | Excluded from the metric panel from the start. |
| R7 | **Flat-structure contamination from COCONUT.** COCONUT entries are "flat" NP structures with stereochemical forms attached separately | [Chandrasekhar2025] | **High** | Explicit extraction of stereo-resolved forms during curation. Audit the fraction of the saponin set that has absolute stereochemistry before training. |
| R8 | **Post-filtering bias in Stage 2.** Similarity-based post-filtering of generated molecules introduces new selection biases | [Amabilino2020] | Medium | Constrain during generation (Stage 2 RL scoring), not by post-hoc similarity filtering. |
| R9 | **Long SMILES strings.** Saponin isomeric SMILES may approach or exceed the length cutoffs used in published pipelines (e.g. 250 characters in [Skinnider2021], 100 in GuacaMol preprocessing [Brown2019]) | [Skinnider2021], [Brown2019] | Medium | Measure the length distribution of the saponin corpus first; choose context length accordingly. This is an argument for S4 [Ozcelik2024]. |
| R10 | **Sugar-identity collapse.** Near-isomeric sugars (glucose / galactose / mannose; xylose / arabinose) differ mainly by stereochemistry. In SMILES-as-single-object encodings, rarer sugars have been observed to collapse toward the most frequent one (glucose). Output would pass validity *and* anomeric checks while having the wrong sugar | [SweetFold2026] (mechanism shown for structure prediction, not generation — argument by mechanism) | **High** | Add a per-sugar identity audit to the metric panel: compare the monosaccharide-composition histogram of generated vs training saponins, not just aggregate stereo statistics. This is the concrete failure the §7.3 glycan-aware tokenizer is meant to prevent. |
| R11 | **Aglycone dilution.** If the 40k is mostly bare triterpenoids, the model learns ring systems from 40k examples but glycosylation from far fewer. A prior that rarely emits sugars at all would score well on aggregate metrics while failing the actual Stage 1 goal | [Chen2023] (TeroMOL spans aglycones and glycosides); inference from corpus composition, **not** a published finding | **High** | Measure the split first (audit script). If glycosides are a small minority, consider a glycoside-weighted sampler at Stage 1, or treat Stage 2 as the real prior and Stage 1 as pretraining. |
| R12 | **TeroKit provenance and stereochemistry unverified.** TeroMOL aggregates from multiple sources; the bulk download is a plain SMILES text file and the documentation does not state whether stereochemistry is preserved | [Chen2023]; TeroKit data page | **High** | The audit script reports the fraction of molecules with defined vs undefined stereocentres. If a large fraction is flat, the §5 analysis and R2/R10 all degrade — resolve before training. |
| R13 | **Size mismatch in terpenome pretraining.** Mono- and sesquiterpenoids (C10/C15) are far smaller than glycosylated C30 triterpenoids; training-set size homogeneity has been implicated in unstable extrapolation | [Skinnider2021], [Vignac2023] | Medium | Prefer the larger terpenoid classes when building the Stage 0 corpus; compare a full-terpenome prior against a large-classes-only prior. |

### 8.2 Risks that would have been incurred by the rejected alternatives

| Approach | Carried-over risk |
|---|---|
| **GAN (MolGAN-class)** | Mode collapse to ~2% uniqueness [DeCao2018] — directly defeats the Stage 1 diversity objective. Fixed maximum graph size. |
| **Graph VAE (JT-VAE)** | Substructure vocabulary derived from the training set; post-hoc stereoisomer enumeration that scales combinatorially with stereocentre count [Jin2018]; documented inability to handle large compound structures [Ochiai2023]. |
| **2D graph diffusion (DiGress)** | Lower validity than a SMILES LSTM in a 1.3M-molecule regime; Scaf 14.8 on MOSES; unstable extrapolation; some complex molecules cannot be round-tripped graph↔SMILES at all [Vignac2023]. |
| **3D diffusion (EDM/GeoLDM/MolDiff)** | Molecule stability ≈0% at drug scale [Xu2023]; bonds inferred post hoc [Hoogeboom2022]; requires a 3D conformer corpus that does not exist for saponins at scale. |
| **Custom architecture from scratch** | The dominant failure mode is data, not architecture [Skinnider2021]; a custom model would consume the project's budget for no expected metric gain, and would forfeit Apache-2.0/MIT tooling and community support. |

---

## 9. Appendix A — Metric definitions and which to trust

**The five metrics that tracked model quality across all four databases in** [Skinnider2021] **(Spearman ρ ≥ 0.80):** % valid, Fréchet ChemNet Distance, **% stereocentres** (JSD between generated and training distributions), Murcko scaffolds (JSD of scaffold frequencies), and NP-likeness score (JSD).

**Metrics that failed to track quality** in the same study: % unique (all models exceeded 99%), computed logP, internal diversity, external diversity, % novel, and most single-property Jensen-Shannon distances. The authors also found JSD outperformed both Wasserstein distance and KL divergence as a distribution-comparison measure.

**Standard benchmark metrics:**
- **FCD** [Preuer2018] — Fréchet distance between ChemNet penultimate-layer activation statistics for reference and generated sets. Lower is better raw; GuacaMol reports a transformed score where higher is better.
- **MOSES additions** [Polykovskiy2020] — SNN (mean Tanimoto to nearest test-set neighbour), Frag (BRICS fragment cosine similarity), Scaf (Bemis-Murcko scaffold cosine similarity), IntDiv, Filters (fraction passing dataset-construction filters).
- **GuacaMol** [Brown2019] — V, U, N, KL divergence over physicochemical descriptor distributions, FCD; distribution-learning tasks generate a fixed 10,000 molecules.
- **MolScore / moleval additions** [Thomas2024] — **SEDiv** (sphere exclusion diversity: chemical-space coverage at a Tanimoto threshold; a score of 0.5 means 50% of the sample suffices to describe the space, so higher = more diverse), scaffold uniqueness, scaffold diversity, functional-group and ring-system diversity, **average fraction of outlier bits** ("silliness"), ZINC20 purchasability via molbloom, analogue similarity and coverage.
- **SEDiv vs IntDiv** [Renz2024] — internal diversity demonstrably misranks chemical space coverage (it measured GDB13 as more diverse than GDB17); sphere-exclusion metrics such as SEDiv and #Circles align with chemical intuition.
- **NP-likeness** [Ertl2008] and **SA score** [Ertl2009] — both used as distribution-matching targets rather than filters in [Skinnider2021].

## 10. Appendix B — Dataset size and scope reference

| Dataset | Size | Size range | Note |
|---|---|---|---|
| MOSES [Polykovskiy2020] | ~1.9M (1.6M train) | **8–27 heavy atoms** | ZINC Clean Leads; excludes saponin-sized molecules |
| GuacaMol [Brown2019] | 1,591,378 (1,273,104 train) | **2–88 heavy atoms** | ChEMBL-24; salts removed, charge neutralised, SMILES ≤100 chars, element whitelist, drug-similarity holdout |
| GEOM-Drugs | ~430,000–450,000 | up to 181 atoms, **mean 44.4** | 3D conformer benchmark for diffusion models |
| COCONUT 2.0 [Chandrasekhar2025] | **695,133** unique NP structures | — | 63 sources; 539,350 with preserved stereochemistry; 82,220 without stereocentres; 73,563 with stereocentres but no absolute stereo |
| Plant metabolome CLM [Skinnider2021] | 21,993 | — | Nearest published analogue to a plant-glycoside training set |
| **TeroMOL / TeroKit (full terpenome)** [Chen2023] | ~180,000 (Dec 2022) | mono- through sesterterpenoids, meroterpenoids, steroids; includes glycosides | Candidate Stage 0 pretraining corpus. Bulk download is SMILES text; stereochemistry completeness undocumented |
| **Triterpenoid + saponin set (this project)** | **~40,000 (TeroKit)** | typically >40 heavy atoms | **~200x the TL floor; ~1.8x the plant-metabolome model that succeeded in [Skinnider2021]. Direct training is viable.** Aglycone:glycoside split unmeasured — the key open quantity |

---

*End of Cycle 1 report. See `open_questions.md` for the Cycle 2 agenda and `progress_log.md` for the changelog.*
