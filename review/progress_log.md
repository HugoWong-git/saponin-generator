# Progress Log

Changelog across cycles. Newest entry first.

---

## First live corpus + prior audit — Q4a/Q4b closed, two new defects found — 2026-09-24

**Trigger:** the review's Priority 1. `audit_corpus.py` had been written but never
executed — the authoring sandbox could not install RDKit. A fresh container had
RDKit 2026.3.6 available on PyPI, and the `saponin-generator` repository carried
both the corpus and four trained checkpoints, so the whole of Priority 1 became
runnable at once.

**Environment note.** The original working directory did not survive — the
container holding it was reclaimed. The markdown deliverables were recovered from a
user-supplied zip; the generated `.docx`, `.pptx`, `.xlsx` and `.html` were not in
it and have not been rebuilt. Everything is now committed into the
`saponin-generator` repository so this cannot recur.

**`audit_corpus.py` ran clean on first execution.** No debugging was needed, which
was not the expected outcome given the docstring's warning. All 45,966 records
parsed, 100%.

### Q4a — CLOSED. 40.58% glycosides / 59.42% aglycones

18,654 glycosides against 27,312 aglycones. A minority, as feared, but close to the
21,993-molecule plant-metabolome model [Skinnider2021] and far above the ~190
transfer-learning floor [Amabilino2020]. **Stage 2 is viable** — the feared outcome
did not occur.

The more consequential finding is that the corpus is **bimodal**: glycosides mean
MW 987.7 and 8.2 rings, aglycones 515.1 and 5.0. The median molecule has no sugars.

### Q4b — CLOSED. The corpus is stereochemically rich

87.5% carry a tetrahedral marker; 65.71% fully specified, 24.68% partial, 9.61%
flat. Median 10 defined centres, p95 33. The §5 argument for SMILES survives at the
corpus level.

### Q4d — NEW. The 128-token cap is a glycoside-selective filter

`max_sequence_length = 128` is declared in the checkpoints and set in **none** of
the configs — inherited from the upstream PubChem prior, never chosen for saponins.
Tokenised with REINVENT's scheme, **41.4% of glycosides exceed it against 0.7% of
aglycones.** The cap sits at the median glycoside length.

This is R9 realised as a measured defect, and it vindicates the §7.2 correction
(max × 1.2, not p95) — p95 here is 170 tokens and would still truncate the most
glycosylated molecules.

### Q4e — NEW. The pipeline emits no stereochemistry at all

Zero of 8,858 valid generated molecules contain a stereocentre, against 87.5% of the
corpus. Mean probability on the 18 stereo tokens in the model's own vocabulary is
**6.6 × 10⁻⁹ per step**, and it *falls* monotonically from epoch 1 to epoch 4.

`isomeric_smiles = false` in every sampling config is confirmed. That the
transfer-learning step also fails to present isomeric SMILES is **inferred** from
the near-zero token probabilities plus the non-isomeric provenance of the base
prior — not confirmed against REINVENT's data loader, which would need REINVENT4
installed. Recorded as inference, not fact.

This is the most serious finding in the audit. The review's central representational
argument is being nullified by configuration.

### Method — and its limits

The published pipeline could not be re-run (REINVENT4 not installed;
`download.pytorch.org` is blocked by the proxy, though PyPI served torch 2.14.0).
The RNN was instead reconstructed directly from the checkpoint — 3-layer LSTM, 512
hidden, 256 embedding, 131-token vocabulary — and sampled at temperature 1.0.

The reconstruction was validated against the existing epoch report before any
conclusion was drawn from it: validity 88.58% vs 86.97% published, mean MW 553.9 vs
551.30, mean rings 5.06 vs 5.03. Close, but **not the identical code path** —
`randomize_smiles` and canonicalisation differ, and this is stated as a limitation
in the report rather than glossed.

Sugar detection is a **shape heuristic**, not carbohydrate assignment: a 5- or
6-membered all-sp3 non-aromatic ring, one ring oxygen, ≥2 exocyclic oxygens.
Glucose, galactose and mannose are not distinguished — they differ only by
stereochemistry, which is the very thing the model has lost. The glycoside
fractions are consistent relative measures, nothing more.

### What this does to the existing epoch comparison

`reports/46k_prior_epoch_comparison.md` recommends epoch 3, with epoch 4 for
downstream fine-tuning, on validity/novelty/FDD/NLL and seven descriptor KLs. None
of those metrics can see either defect. FDD improves monotonically E1→E4 while the
model sits on the wrong mode of a bimodal distribution — a clean instance of the
loss–quality divergence in §3.3a. Epoch 4 is the most stereochemically degenerate
of the four and the suite ranks it best.

The report attributes the high NumRings KL (0.12–0.14, the worst of seven) to
"diverse non-saponin PubChem molecules". The measured cause is the unlearned
glycoside mode.

`metrics/e1_vs_e4_npc.json` captures NPClassifier superclass, class and pathway but
**not `isglycoside`** — which the same API response returns, per
`references/fcd_npclassifier_api.md`. The one field that would have caught this was
available and discarded.

### Unchanged

The §7 recommendation stays **provisional**: Q1, Q2, Q3 and Q5 are untouched, and
nothing here bears on adapt-vs-build. If anything it strengthens "adapt" — both
defects are configuration, not architecture. The citation checker reports
**unresolved: NONE** across all five documents, 50 keys, before and after this edit.

No published model was scored against the protocol. Rule 2 holds.

---

## Gap visualisation — deck + page — 2026-09-23

**Trigger:** user asked for the gap to be visualised. First delivered as an artifact page, then corrected — "Wait I mean is ppt" — so the deliverable is a PowerPoint. Both now exist; the deck is the one that was asked for.

**New deliverables:**
- `Saponin_Evaluation_Gap.pptx` — 11 slides, 13.33 × 7.5.
- `gap_visualization.html` — the same eight plates as a self-contained page (published artifact).
- `build_gap_deck.js` — the generator, so the deck is rebuildable rather than hand-edited.

**Nothing new was computed.** Every plotted value comes from `reported_metrics_record.md` or the verdict column of `metric_coverage_gap_analysis.md`.

### Palette

Reused the project palette from the literature-review deck (`2C7A3E` / `C98A1E` / `B5482F`) and re-validated it as a categorical set before charting: lightness band PASS, chroma floor PASS, CVD separation PASS (worst adjacent ΔE 11.6 protan), normal-vision floor PASS (16.8). One WARN — amber contrast 2.87:1 against the surface — which obligates visible labels; every bar and dot in the deck carries its value as a label, so the relief is satisfied rather than waived.

### Two design decisions worth recording

**Dropped status colour from the size chart.** The first draft coloured QM9/MOSES red and GuacaMol amber, inheriting the coverage legend. That asserts something false — MOSES has not *failed* at anything, it is simply small. Benchmarks are now neutral grey and only the project corpus takes the accent, with a dashed open-ended bar because the distribution is unmeasured (Q4a).

**GEOM-DRUGS kept off the heavy-atom axis.** Its 44.2 is *atoms including hydrogens*; MOSES and GuacaMol ranges are *heavy atoms*. Plotting them on one scale would have been a unit error presented as a chart, so 44.2 is a separately-labelled marker carrying the caveat in its own caption.

### Slide inventory

Title · four headline figures · 150-cell coverage grid · 20-row section table · size cliff · 3D stability collapse (native bar + void panel) · MOSES FCD log dot plot · focused-dataset trade-off scatter · sections-touched bar · the four zeros · three consequences.

### QA

`validate.py` PASSED on both builds. Content QA: no placeholder text. Visual QA by a subagent that had not seen the generator, on all 11 rendered slides — it returned 10 defects, all fixed in the generator and re-verified:

- slide 4 title wrapped onto the subtitle → title size 27pt
- slide 8 panel heading overwritten by its own body text → panel widened, heading shortened
- slide 5 marker caption cutting through the axis ticks → moved onto the axis row
- slides 7 and 8 axis titles colliding with the takeaway band → axis title moved beside the tick row (7), plot compressed (8)
- slide 8 annotation overhanging the plot frame → right-aligned inside it
- slide 11 columns misaligned because one heading was a single line → `valign:'top'` on all three
- footers sitting one line-height under the body on five slides → footer moved to y = H − 0.40 and takeaway text tightened

The subagent also confirmed clean: all native-chart category and value labels (no clipping), the largest FCD label, the section-table pills, and the right-pointing arrow on the saponin bar.

---

## Reported-values record — transcription only — 2026-09-23

**Trigger:** user narrowed the previous request — "just record down what they have reported. **No need to compute anything**." That removes the blocker from the gap analysis: transcribing what papers printed needs no model weights and no generation runs.

**Discipline applied:** nothing in either new artefact is computed. No value averaged, rescaled, interpolated or estimated. Where a table could not be fetched, the cell says NOT RETRIEVED rather than being filled from memory — §10 of the record exists so the gaps are visible instead of silently absent.

**New deliverables:**
- `reported_metrics_record.md` — 11 sections, prose + tables, every block marked with a source-confidence tag.
- `reported_metrics.xlsx` — 317 rows in tidy long format (one row per model-metric), three data sheets plus a README sheet. Filterable on section, dataset, model, metric, direction, source and confidence.

### Tables fetched this session

**MOSES** [Polykovskiy2020] — the full baseline tables, 9 models × 15 metrics = 135 rows, mean ± SD over three initialisations. Dataset stated as 4,591,276 molecules, MW 250–350 Da, 8–27 heavy atoms.

**GeoLDM** [Xu2023] Table 1 — QM9 (10 methods) and GEOM-DRUGS (8 methods), carrying [Hoogeboom2022] EDM as a compared method. GEOM-DRUGS average size confirmed from the primary source as **44.2** atoms; an earlier secondary source in this review had said 44.4, and the primary value now stands.

**MolGPT** [Bagal2022] — fetch failed, ACS HTTP 403. Recorded in §10, not paraphrased into a number.

### The finding that came out of a non-result

The single most decision-relevant value in the record is one the field reports **by declining to report it**. [Xu2023] omits molecule stability and uniqueness for GEOM-DRUGS, stating they "are nearly 0% and 100% respectively for all the methods," because larger structures create bond-type prediction errors. Read directly: at an average of 44.2 atoms, essentially no generated molecule is stable, for every 3D method tested. Saponins are larger than that average. This is stronger evidence against 3D diffusion at Stage 1 than any published table, and it is an omission rather than a number — so it is recorded as an explicit "omitted by authors" row in the workbook with the authors' reasoning in the note column, not dropped as missing data.

### Second-order observations recorded

- **MOSES publishes its own Tier 0 baseline.** The *Train* row (FCD 0.008 Test, 0.476 TestSF) is exactly the A↔B reference the protocol asks for. Scaf TestSF is **0.0** for the training set by construction — a reminder that some metrics floor at zero rather than one.
- **The two FCD conventions are not interchangeable.** MOSES reports raw FCD (lower better); GuacaMol reports a transformed score (higher better). Encoded as distinct `direction` values in the workbook and asserted in the verification script, because silently mixing them would corrupt any cross-benchmark reading.
- **[Subramanian2023] is the closest published analogue to this project's regime** — on small focused datasets the string model matched the distribution roughly twice as well (FCD 0.60–0.61 vs 0.28–0.32) while losing on novelty (0.55–0.58 vs 0.89–1.00). That trade-off is what to expect at 40k.

### Verification run

- Round-trip check: every numeric value in the workbook re-located in the markdown tables. Six initially flagged as missing were false positives — the harvester's regex split comma-separated thousands (8,447 → 8 + 447); confirmed by inspection, re-run clean with separators stripped. **No transcription errors.**
- Structural checks: 0 duplicate (section, dataset, model, metric) keys; 0 rows missing source or confidence; direction and confidence vocabularies both closed; MOSES completeness 9 × 15 exact.
- Citation integrity across all five markdown documents **and** the workbook's Source column: 23–34 keys cited per document, **unresolved: NONE**.

### What the record shows as a whole

Across nine MOSES baselines, six GuacaMol baselines, ten 3D methods, two focused-dataset models and four optimisation entries — **not one reported value describes a glycoside, a sugar, an anomeric centre, or a ring fusion.** The only stereochemistry metric anywhere is Skinnider's aggregate stereocentre fraction, and [Skinnider2024] found it was the one metric where SMILES did *not* significantly beat SELFIES. The gap the previous analysis inferred from coverage is now visible in the field's own published numbers.

---

## Metric-coverage gap analysis + protocol v3.3 — 2026-09-23

**Trigger:** user asked whether every published model could be analysed against the v3.2 metrics to locate the gap, and to say so if not possible.

**Stated the limit up front:** published models cannot be *scored* on these metrics — that needs each model's weights, ≥100k generated molecules per model, and ~150 computations. Fabricating numbers the papers never reported would be the worst failure mode for a document meant to govern model selection. What *is* possible, and was done, is a **reporting-coverage analysis**: for every model and protocol section, has anyone ever measured this?

**New deliverable: `metric_coverage_gap_analysis.md`.** Every row marked [F] full text / [P] partial / [A] abstract-only, so confidence is visible rather than implied.

### Headline finding

Of ~150 protocol metrics, published generative models collectively report **~25–30**, clustered in core distribution learning (§4) and failure detectors (§11). **Nine of nineteen sections have no published generative-model precedent at all.** The field ceiling is [Skinnider2021] with 23 metrics — which covers §4, §8 and §11 and nothing else in the protocol.

### Two verification findings that changed the documents

**[Tom2025]** *Stereochemistry-aware string-based molecular generation* (PNAS Nexus 4(11):pgaf329) — the one paper dedicated to this. It states current generative models "either ignore stereochemistry or consider it as a postprocessing step," a citable confirmation of the field's treatment. **But it explicitly excludes axial chirality and ring isomers.** Ring-fusion stereochemistry — the A/B, B/C, C/D junctions defining a triterpenoid aglycone's shape — is outside the scope of the state of the art. So protocol metric **S16 has no precedent, and the gap is a stated scope boundary rather than an artefact of my search**.

**[Ozcelik2025]** *How evaluation choices distort the outcome of generative drug discovery* (J Cheminform 17:169) — closest thing in the literature to §19A, and it forced a correction. It shows **library size alone can reverse model rankings**: FCD/FDD fall with library size (plateau above 10⁴–10⁵), and **uniqueness falls as library size rises**, ranking models differently across scales. It independently confirms the Tier 11 position that uniqueness is a sanity check only — the correction the user had already pushed for.

### Protocol v3.3 changes

- **§3.5 / §19A.1:** comparison at **identical library size** is now a precondition, not a reporting detail. §19A had accounted for retraining-seed noise but not for this second, independent confounder.
- **3.1:** uniqueness annotated as size-dependent.
- **R2:** top-*k*/top-*p* separated from temperature — [Ozcelik2025] found restrictive top-*k*/top-*p* causes mode collapse while temperature remains the usable diversity lever. v3.2 had treated them as parallel sweeps.
- **New 2.12** substructure count (size-invariant, ~85× faster than clustering) and **2.13** design frequency — frequently-generated molecules are often simple substructures and unsuitable for prospective use, so frequency is a quality signal.

### The novelty claims, and their weakest link

Three contributions look genuinely novel: NPClassifier applied to generated molecules; the saponin-specific S-series; biosynthetic plausibility of generated structures. **S16 has the clearest claim to being first.**

Recorded honestly in §7 of the analysis: the "no generative paper uses NPClassifier for evaluation" claim rests on **not having found something** in a bounded search. A citation-graph check on [Kim2021] is needed before that is asserted in a write-up — absence of evidence in a bounded search is weaker than a systematic check.

### Two new references, both read in full

[Ozcelik2025] and [Tom2025]. Note [Ozcelik2025] shares a first author with [Ozcelik2024] (S4 chemical language modelling) but is a different paper; both keys flagged in the bibliography to prevent conflation.

---

## Evaluation protocol v3.2 — training dynamics and decision procedure — 2026-09-23

**Trigger:** user asked whether overfitting and robustness were covered, and stated the protocol will be **the sole basis for judging every model built**. That last point raises the bar: a sole standard needs a decision rule, not only measurements.

Audited before answering. Overfitting had **three lines** (L3 NLL gap, gate G15, a note on early stopping). Robustness (R1–R8) covered *sampling* robustness but not *retraining*. Model comparison was **absent entirely**.

### §15A — training dynamics, overfitting and checkpoint selection (F1–F10)

The key point v3.0 missed: **validation NLL and sample quality can diverge.** Likelihood rewards putting probability mass on real molecules; it does not reward covering the space. A model can keep improving on held-out loss while its samples become more conservative and less diverse — so **selecting a checkpoint on validation loss alone can select against Stage 1's actual goal**. This is the deeper reason behind the existing "early-stop on diversity, not loss" instruction, which v3.0 asserted without explaining.

Added: train/validation curves (F1); generative-quality curves recomputed every N epochs (F2); the **loss–quality divergence epoch**, reported explicitly (F3); a pre-declared checkpoint-selection criterion (F4); **augmentation memorisation** — held-out loss can look healthy while the model has memorised randomised variants (F5); **learning curve versus dataset size** (F6), which answers "more data or different method?" and given [Skinnider2021]'s central finding is the highest-value single experiment here; parameter/corpus ratio (F7); convergence evidence (F8); **per-token-type loss** (F9) — if stereo descriptors and ring-closure digits carry disproportionate loss, the R2/R10 failures are visible directly in the training signal rather than inferred from output; epoch-wise memorisation trace (F10).

### §19A — model comparison and the decision procedure

The most consequential addition, given the stated use.

- **Noise floor first (19A.1).** Train one configuration from scratch ≥3 times and measure the spread. Any difference smaller than that is not evidence. Routinely skipped, and with ~150 metrics some will always look impressive by chance.
- **Pre-registered metric hierarchy (19A.2)** — gates (binary) / primary (ranks) / secondary (breaks ties, explains) / diagnostic (never ranks). Default: gates filter → PC1 composite ranks → SEDiv and the S-series break ties.
- **An explicit decision rule (19A.3)**, including the proviso that a primary-metric gain accompanied by a large secondary-metric loss usually means target chemistry was traded for generic quality — the wrong trade here, and invisible to the primary alone.
- **Multiple-comparison handling (19A.4).**
- **Per-model record (19A.5)**, with the instruction to **re-run the controls at every evaluation** — they detect harness drift, e.g. an RDKit version change silently shifting every number.

### Robustness extended

R9 retraining variance (distinct from R3, which varies only the sampling seed), R10 checkpoint sensitivity, R11 distribution-shift on a source- or organism-held-out slice, R12 data-order sensitivity.

### Also

Gates G23–G25 (noise floor established; divergence epoch reported; learning curve run). Four failure modes: chasing noise, silent overfitting, augmentation memorisation, harness drift. Gates now 28; F-series 10, R-series 12. Contents restructured; all ID namespaces machine-checked for duplicates — none.

---

## Evaluation protocol v3.1 — stereochemistry and length gaps closed — 2026-09-23

**Trigger:** user asked whether four specific things were covered — (1) stereochemistry of generated output, (2) sugar presence, (3) saponin subclass balance per NPClassifier, (4) token length sufficient to generate a whole molecule without truncation.

Audited each against v3.0 rather than assuming. **Two were well covered; two were not.**

| Question | Verdict |
|---|---|
| **2. Sugar presence** | ✅ Covered — S1 (glycosylation rate), S2 (sugars per molecule), O5 (NPClassifier `isglycoside` cross-check), D11 (corpus ratio), gate G8 |
| **3. Subclass balance** | ✅ Covered — O1/O2/O3 pathway/superclass/class JSD, O6 coverage, D13 reference distribution, gate G7. **But it surfaced an unaddressed design question** (below) |
| **1. Stereochemistry** | ⚠️ **Partially — real gap found** |
| **4. Length / truncation** | ⚠️ **Covered, but the protocol's own advice was wrong** |

### Gap 1 — stereochemistry was measured only in aggregate

Every stereo metric inherited from the literature is aggregate: % stereocentres [Skinnider2021], stereo completeness (S7), stereocentre count (S11). They confirm stereochemistry is **present and abundant**; none confirms it is **correct**. A model can score perfectly on all three and produce the wrong enantiomer at every centre.

Added:
- **S15 — absolute configuration / enantiomer check.** Triterpenoids are single-enantiomer natural products; a model can emit the mirror image with correct count, correct fraction, full specification and full validity. Note that *ent*- series do occur in terpenoids, so the target is the reference rate rather than zero.
- **S16 — ring-fusion stereochemistry** at the A/B, B/C, C/D junctions. The most chemically decisive stereo feature of a triterpenoid skeleton and invisible to any count-based metric.
- **S17 — position-resolved stereo accuracy**: correct R/S *at each mapped position* for a given scaffold.
- **S18 — E/Z double-bond geometry.**
- **S19 — sugar ring integrity**, distinct from S3 identity: a well-formed pyranose/furanose versus a sugar-*shaped* ring.

New hard stop **G11b** (enantiomer rate within ±5% of reference) and **G11c** (ring-fusion JSD). Implementation note recorded: S16/S17 need scaffold-level atom mapping and are the most demanding items in the protocol; start with S15, which is cheapest and catches the worst failure.

### Gap 2 — the context-window advice was wrong

v3.0 said set the context window from the **p95** sequence length. **That is wrong for this corpus.** A p95 window truncates 5% of molecules, and in a saponin set the longest molecules are the most heavily glycosylated — precisely the ones the project exists to model. Corrected to **max × ~1.2**.

Also separated two things v3.0 conflated:
- **T7** input truncation (corpus molecules too long to train on)
- **T11** output truncation — samples hitting the context limit without emitting EOS, discarded as invalid. The model's longest generations are its most glycosylated, so a non-trivial rate means the prior cannot finish exactly the molecules that matter.
- **T12** generated-vs-training length JSD — catches a model that has adequate window but quietly generates short, i.e. avoids complexity. Visible nowhere else.

Gate G20 extended to cover all three.

### Design question surfaced by Q3

O3 rewards **matching** the training class distribution. If TeroKit is oleanane-dominated (D13 will show this), a model faithfully reproducing that imbalance is doing exactly what distribution learning asks — and is a poor foundation for a generator whose stated goal is diversity. §7 now sets out the match-versus-rebalance trade-off explicitly, with the instruction to decide and record it before training (GV5), because it changes how O3 and G7 are read. If rebalancing, report JSD against both the corpus and the intended distribution.

### Also added

Five entries to the failure-mode catalogue: wrong enantiomer, wrong ring fusion, right-stereocentres-wrong-assignment, short-generation bias, faithful imbalance. Saponin metrics 14 → 19; gates 22 → 25.

---

## Evaluation protocol v3.0 — full scope — 2026-09-23

**Trigger:** user asked for all-round coverage — completeness of *consideration*, explicitly accepting that some tools (NPClassifier and others) cannot be run from here and will be implemented on their side.

Restructured from 10 flat tiers into **seven parts, 19 sections, ~142 named metrics, 22 gates**. New material, in rough order of how much it was missing:

### Entirely new areas

- **§2 Corpus readiness and data quality (D1–D20).** Evaluate the data before the model — most apparent model failure is corpus failure. Covers InChIKey deduplication (not string-level), salt/mixture handling, tautomer canonicalisation, element whitelist, valence scan, the length-cap decision, class balance via NPClassifier on the *training* set, source-database overlap, and frozen pre-registered splits.
- **§3.3 Controls (C1–C6).** The part most protocols omit. A ceiling (real held-out data scored as if generated), a memorisation floor, an **off-target floor** (random COCONUT non-terpenoids), a **trivial-model floor** (character n-gram), the from-scratch control, and a **deliberately broken model** — which tests the *evaluation harness* rather than the model. If a broken model passes the gates, the gates are wrong.
- **§5 Chemical and physical validity beyond parsing (V1–V10).** RDKit-parseable is a low bar. Adds **3D embeddability (ETKDG success)** — a molecule that cannot be embedded cannot exist, rarely reported, and directly relevant to strained fused polycyclics — plus Bredt's-rule and trans-cycloalkene violations, aromaticity and InChI round-trips, and stereochemical self-consistency at ring fusions.
- **§9 Synthesizability and biosynthetic plausibility (A1–A3, B1–B4).** For saponins the *biological* question matters more than the synthetic one. SA score and RAscore [Thakkar2021] are both drug-calibrated and must be read against `base`, with the key test being that generated molecules should **not** score better than real saponins. BioNavi-NP [Zheng2022] supplies pathway findability. **The strongest project-specific opportunity: TeroENZ already ships 13,462 enzymes and 4,293 reactions inside TeroKit** [Chen2023] — a ready-made substrate for glycosyltransferase and terpenoid-cyclisation plausibility that nobody has built.
- **§16 Tokenisation and sequence diagnostics (T1–T10).** Under-examined and high-risk for this chemistry. Stereo-token segmentation (`[C@@H]` as one token or several), **two-digit ring closures (`%10`, `%11`)** — a classic silent failure in ring-rich molecules — truncation rate, context window set from the p95, and augmentation–tokenisation interaction.
- **§17 Engineering and operational (E1–E8).** Led by **inference throughput**, which is the real constraint on Stage 2 RL. Also RDKit version pinning: validity numbers are not comparable across RDKit versions.
- **§18 Governance, licensing, reproducibility (GV1–GV7).** Model card, and **data licensing for derived models** — what TeroKit and COCONUT permit for a model that might be published. Resolve before training, not after.
- **§20 Failure-mode catalogue.** Thirteen named failure modes mapped to the metrics that catch each, so they can be tested for rather than hoped about.

### Expanded

- Saponin-specific metrics **12 → 14** (added aglycone ring-system integrity, free hydroxyl/carboxyl pattern).
- Coverage adds property-manifold coverage; memorisation adds an **augmentation-leakage** check specific to randomised-SMILES training.
- Likelihood adds perplexity, per-position entropy, and NLL of known target saponins.
- Optimisability adds harness validation against published PMO numbers before trusting saponin results, and a **warm-start advantage** measure quantifying what pretraining actually bought.
- Robustness (R1–R8) now its own section: temperature and top-k/top-p sweeps, seed variance, degenerate repetition, EOS calibration, fp16/fp32 agreement, batch-size invariance.
- Qualitative review adds a **blind real-vs-generated test** and an adversarial-review step.
- Gates **17 → 22**, including a physical-embeddability gate, an n-gram-baseline gate, a tokeniser gate and a throughput gate. Hard stops remain G9 (sugar identity) and G10 (anomeric validity), plus G0 (leakage).

### Defect found and fixed during verification

Section 18's governance items were numbered G1–G7, colliding with the gate IDs G0–G22 in §21. Renamed to GV1–GV7. All 13 ID namespaces were then machine-checked for duplicates — none remain.

### New references, both verified

[Thakkar2021] RAscore (*Chem Sci* 12:3339–3349) and [Zheng2022] BioNavi-NP (*Nat Commun* 13:3342 — 90.2% pathway success on 368 compounds). **Not extractable for [Thakkar2021]:** comparison against SA score/SCScore, natural-product performance, repository location, applicability-domain caveats. Flagged in both the bibliography and §9.1.

---

## Evaluation protocol v2.0 — comprehensive — 2026-09-23

**Trigger:** user asked for a comprehensive reference version rather than a first pass, and challenged two specific things: the exclusion of **uniqueness**, and the absence of **NPClassifier**. Both challenges were correct.

### Corrections made

- **Uniqueness, internal diversity and novelty reinstated** as a new **Tier 3 — failure detectors**. v1.0 banned them outright, which was too strong. The defensible position: they have **no quality gradient** (every model in [Skinnider2021] exceeded 99% uniqueness) but they do have a **floor**, and MolGAN's ~2% uniqueness [DeCao2018] is exactly the failure a Stage 1 diversity prior must catch. Report always; gate only on an alarm threshold (G4). Uniqueness is now reported as a **curve over sample size** rather than a single endpoint, since the saturation point is informative when the endpoint is not.
- **New Tier 4 — chemical ontology.** NPClassifier [Kim2021] was a genuine omission: it is NP-native, returns a three-level pathway/superclass/class ontology, ships an **`isglycoside`** flag, and is MIT/CC0 with a Dockerised local deployment. It largely supersedes the hand-rolled S6 aglycone-class metric from v1.0. ClassyFire [Djoumbou2016] added as a secondary cross-check.

### Also added in v2.0

- **Tier 5 expanded 7 → 12** saponin-specific metrics (sugar chain topology, O-/C-glycoside ratio, sugar acylation, stereocentre count, aglycone:sugar mass ratio).
- **New Tier 6** — property panel (12 properties), with the explicit caveat that QED and SA score are drug-calibrated and a "good" QED means drift away from saponin space.
- **New Tier 7** — memorisation, near-duplicates, canonicalisation collapse and train/test leakage. v1.0 had no memorisation check at all, which was a serious gap since leakage invalidates every Tier 8 number.
- **New Tier 9** — qualitative and expert review, including chemist inspection of 100–200 unfiltered structures and a biosynthetic-plausibility spot-check.
- **Tier 8 expanded** — NLL calibration curve, σ prior-drift sensitivity sweep, conditional-generation probe, multi-objective sample-efficiency probe.
- **§2.3 sampling requirements** — ≥100,000 samples (prefer 500,000), ≥3 seeds. [Skinnider2021] found some property-distribution metrics unstable below 100k; v1.0 specified no sample size at all.
- **Source-organism split** added alongside random and scaffold splits.
- **Gates 9 → 17.** Hard stops remain G8 (sugar identity) and G9 (anomeric validity), joined by G0 (no train/test leakage).
- Minimum-viable subset removed — superseded by the comprehensive version.

### New references, both verified

[Kim2021] NPClassifier (*J Nat Prod* 84(11):2795–2807) and [Djoumbou2016] ClassyFire (*J Cheminform* 8:61, ChemOnt = 4,825 categories, up to 11 levels). **Not extractable for [Kim2021]:** per-level category counts, per-class F1, and aglycone-vs-sugar weighting — ACS 403 and PMC CAPTCHA. Flagged in both the bibliography and protocol §6.1 with an instruction to validate the classifier on corpus half A before gating on class-level metrics.

---

## Stage 1 evaluation protocol v1.0 — 2026-09-23

**Trigger:** user asked which metrics determine whether the Stage 1 prior can act as the foundation of the saponin generator.

**Added `evaluation_protocol.md`** — a four-tier metric set with acceptance gates.

The organising insight, and the reason the protocol is not just a metric list: in a REINVENT-family pipeline the prior's likelihood term stays **inside the Stage 2 RL loss** [Guo2024], so the prior is a persistent regulariser rather than a discarded initialisation. Prior quality therefore bounds what Stage 2 can produce. That makes "is it a good prior *for optimisation*" a separate question from "does it learn the distribution" — and it is the question no standard metric suite answers.

Structure:
- **Tier 0** — the A-vs-B reference baseline on a *scaffold* split. Every distance metric is uninterpretable without it, and absolute FCD is known to look poor on small focused NP datasets regardless of model quality [Subramanian2023].
- **Tier 1** — the five metrics validated at rho >= 0.80 across four databases [Skinnider2021].
- **Tier 2** — coverage that works (SEDiv, #Circles, scaffold/ring/functional-group diversity, outlier bits), with uniqueness, IntDiv and novelty explicitly banned [Skinnider2021, Renz2024].
- **Tier 3** — seven saponin-specific metrics (S1-S7) that no published suite provides: glycosylation rate, sugars per molecule, monosaccharide composition, anomeric validity, regiochemistry, aglycone class, stereo completeness.
- **Tier 4** — fitness as a Stage 2 prior: held-out NLL broken down by subgroup, scaffold recovery, a PMO-protocol sample-efficiency probe [Gao2022], diversity collapse under RL, temperature response.
- **Nine acceptance gates**, of which G5 (sugar identity) and G6 (anomeric validity) are hard stops and are the two specific to this project.
- A **minimum viable subset**: seven numbers plus a baseline.

**Two new references**, both read in full: [Gao2022] (PMO benchmark — AUC top-10 vs oracle calls; REINVENT first of 25 algorithms) and [Guo2024] (Augmented Memory — the prior-in-the-loss mechanism and RL mode collapse).

---

## Dataset-size revision — 2026-09-23

**Trigger:** the user identified the corpus as **~40,000 triterpenoids and saponins retrieved from TeroKit**, with the wider TeroMOL terpenome also available. Cycle 1 had assumed "several hundred structures from COCONUT/KNApSAcK" — the figure carried over from the original brief. That assumption underpinned §6 and §7, so both were rewritten.

### What changed in the recommendation

| | Cycle 1 (assumed ~hundreds) | Revised (actual ~40,000) |
|---|---|---|
| From-scratch training | "Contraindicated by the evidence" | **Viable** — 40k is ~1.8x the plant-metabolome model that succeeded in [Skinnider2021]. Now a required control, and preferred if it matches the pretrained model |
| Transfer learning | "The only regime with published support" | Still recommended, but must now **earn its place** against the from-scratch baseline |
| SMILES augmentation | Sweep {3x, 10x, 20x, 30x}, expect high factors to win | **Reversed.** Sweep {1x, 2x, 3x, 5x, 10x}, expect a LOW optimum — [Skinnider2021] found high factors *degrade* complex-chemistry models at large training sizes |
| Binding constraint | Whether a prior can be trained at all | **What the 40k is made of** — the aglycone:glycoside ratio |
| R5 mode collapse | Medium-High | **Lowered to Low-Medium** for Stages 0/1; stays Medium-High for a small Stage 2 |
| R3 over-enumeration | Medium | **Raised to High** |

Direction of the recommendation is unchanged: adapt a SMILES chemical language model. Family verdicts in §3 are unchanged — 40k is still ~33x smaller than the GuacaMol/MOSES sets that graph diffusion needs.

### Added

- **§6 rewritten** — the 40k regime, the aglycone:glycoside problem, terpenome pretraining, the homogeneity caveat now cutting favourably, and the 82% validity ceiling that data volume does not buy past.
- **§7.1 rewritten** — a **three-stage curriculum** (terpenome-wide → triterpenoid/saponin → glycosylated-only), plus an explicit from-scratch control, plus the reversed augmentation advice.
- **§7.2 / §7.3 / Appendix B** updated for the new size.
- **Three new risks:** R11 (aglycone dilution), R12 (TeroKit provenance and stereochemistry unverified), R13 (size mismatch in terpenome pretraining).
- **`audit_corpus.py`** — a new deliverable. Profiles the corpus against every threshold quoted in the review: parse rate, aglycone:glycoside split, sugar-shape composition, stereochemistry completeness, SMILES-length distribution vs the 250/100-character cutoffs, heavy-atom range vs MOSES/GuacaMol, Murcko scaffold count, internal diversity and a SEDiv estimate. Writes glycoside/aglycone subsets and a JSON report.
- **Two new references:** [Zeng2020] (TeroKit, JCIM 60(4):2082–2090) and [Chen2023] (TeroENZ/TeroMAP, *Database* 2023:baad020 — the source for TeroMOL's ~180,000 molecules and its coverage of glycosides).
- **`open_questions.md`** — Q4 superseded by **Q4a** (aglycone:glycoside split), **Q4b** (stereochemistry completeness) and **Q4c** (terpenome pretraining ablations). Q4a and Q4b are gating.

### Caveats on this revision

- The 40k figure, the aglycone:glycoside split and the stereochemical completeness are all **described in conversation, not verified against the file**. The audit script exists to close that gap and should be run before anything is committed.
- `audit_corpus.py` was **written against the RDKit API but not executed against a live RDKit install** — the authoring sandbox could not install RDKit (PyPI unreachable from the shell). Its pure-Python helpers were unit-tested; the chemistry paths were not. Treat the first run as a smoke test.
- The sugar detection in that script is a **structural heuristic, not carbohydrate assignment**. It cannot distinguish glucose from galactose from mannose — precisely the distinction R10 is about. It establishes a baseline, not the final metric.

---

## Cycle 1 — 2026-09-22

**Scope run:** full scope (not the scope-limited option offered in the prompt's notes). All six required model families covered at survey depth; the SMILES/chemical-language-model family, natural-product-specific work and glycoside/stereochemistry questions covered in depth.

### Added

- **`literature_review_report.md`** — created. Sections: executive summary; master comparison table (21 entries); family-by-family synthesis (6 families); three explicit sub-question sections (pretrained-prior overlap, stereochemistry per architecture, minimum dataset sizes); provisional adapt-vs-build recommendation; risk register (10 risks + rejected-alternative risks); two appendices (metric definitions, dataset size reference).
- **`bibliography.md`** — created. 39 numbered entries plus secondary sources and a "consulted, not relevant" section. Per-entry verification status.
- **`bibliography.bib`** — created. 34 BibTeX entries with `note` fields carrying verification status.
- **`open_questions.md`** — created. 10 open questions, 3 flagged as gating; coverage-versus-brief table; resolved-questions section.
- **`progress_log.md`** — this file.

### Key findings established

1. Data volume dominates architecture choice in the low-data regime ([Skinnider2021], 8,447 models).
2. Transfer-learning floor is ≥190 molecules ([Amabilino2020]); direct-training floor for complex NP chemistry is ~15,000 ([Skinnider2021]). The project's dataset sits between them, so transfer learning is the only evidence-supported path.
3. COCONUT-trained CLMs cap at 82% validity — the project should plan for a lower validity ceiling than drug-like benchmarks report.
4. SMILES beats SELFIES for distribution matching; invalid SMILES are a beneficial self-filter ([Skinnider2024]).
5. No saponin-, triterpenoid-glycoside- or steroidal-glycoside-specific generative model found. Closest prior art is NP-wide: NPGPT ([Sakano2024]) and the [Skinnider2021] metabolome models.

### Provisional recommendation

**Adapt, do not build** — a SMILES chemical language model, NP-pretrained (COCONUT), transfer-learned onto saponins with randomized-SMILES augmentation, isomeric SMILES throughout. Marked provisional pending Q1/Q2 in `open_questions.md`.

### Coverage against the brief's minimum bar

Met for SMILES/CLM (7 papers) and diffusion (4 papers). Nominally met but substantively weak for graph VAE/GAN — [Jin2018] and [DeCao2018] are covered properly, but [Ochiai2023] and HierVAE are abstract-level only. **This is why the recommendation is flagged provisional**, per the brief's instruction to flag under-covered categories.

---

## Cycle 1 — citation-verification pass — 2026-09-22 (same session)

Ran after the report was drafted, to check that every citation key corresponds to a real, correctly attributed source.

### Corrected

- **`[Koch2024]` → `[Renz2024]`** (4 occurrences). The sphere-exclusion-diversity paper is by **Renz, Luukkonen & Klambauer**, *JCIM* 64(15), 5756–5761, DOI 10.1021/acs.jcim.4c00519. The original key was a fabricated author attribution on my part and is now corrected throughout the report and bibliography. Authorship confirmed via the ICLR 2024 GEM workshop record.

### Confirmed correct (keys I had provisionally planned to rename, then verified instead)

- **`[Subramanian2023]`** — verified correct: Akshay Subramanian, Kevin P. Greenman, Alexis Gervaix, Tzuhsiung Yang, Rafael Gómez-Bombarelli, arXiv 2303.08272. Renaming it would have introduced an error.
- **`[SweetFold2026]`** — verified: **Sundar & Yang (2026)**, bioRxiv, DOI 10.64898/2026.07.16.738959.
- **`[Xu2023]`** (GeoLDM) — author list verified via arXiv 2305.01140.

### Left unresolved and marked as such

- **`[CarbCofolding2026]`** — author list could not be resolved (ACS 403; PMC/PubMed CAPTCHA; Crossref and Europe PMC rate-limited). Key is topic-based rather than author-based; the BibTeX entry deliberately has **no author field** rather than a guessed one. Venue, volume, issue, page, PMID and PMCID are confirmed. Tracked as Q3.
- **`[Madhawa2019]`** (GraphNVP) — first two authors confirmed via the Semantic Scholar record; remainder unresolved. Marked partial in both bibliography files. Low-relevance citation.

### Content added as a by-product of verification

- **§3.3** — replaced the qualitative summary of [Subramanian2023] with the actual Table 1 figures (RNN+SELFIES: KL 0.96–0.98, FCD 0.60–0.61; JT-VAE: KL 0.75–0.87, FCD 0.28–0.32) and added the interpretation that JT-VAE's novelty advantage is a defect rather than a feature for a distribution-learning prior, plus the observation that the string model won *despite* being handicapped with SELFIES.
- **§5** — added the mechanism from [SweetFold2026]: SMILES-as-single-object encoding causes "context dilution", and sugars differing mainly by stereochemistry "collapse into most trained common entities" (galactose/mannose → glucose). Mapped explicitly onto saponin sugar chemistry, with an honest caveat that this is demonstrated for structure prediction rather than generation.
- **Risk register** — added **R10 (sugar-identity collapse)**, severity High, with a per-sugar composition audit as mitigation. This is now the concrete failure mode the §7.3 glycan-aware-tokenizer proposal is designed to prevent.
- **Report header** — records the verification convention (topic-based keys where authorship is unresolved; no guessed author names) and the `[Koch2024]` correction.

### Tooling note

Crossref and Europe PMC metadata APIs rate-limited this session; PubMed and PMC served CAPTCHA interstitials to the fetch tool; ACS returned 403. The sandbox shell cannot reach these hosts (outbound HTTPS is allowlisted to package registries), so `curl` is not an alternative route. The technique that worked repeatedly was **resolving authorship from the reference list of a different paper that cites the work** — this is how [Ochiai2023], [Mercado2020], [ArusPous2019] and [Bemis1996] were confirmed. Recommended first move for Q3 in Cycle 2.

---

## Cycle 2 — not yet run

Agenda is in `open_questions.md`. Gating items: Q1 ([Ochiai2023] in full), Q2 (HierVAE primary paper), Q3 (re-resolve [CarbCofolding2026] authorship). Q4 is project work rather than literature search but has the highest decision impact of anything outstanding.
