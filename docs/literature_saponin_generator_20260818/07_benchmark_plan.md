# Benchmark Plan — First Fair Model-Selection Experiment

## A. Models in the comparison

1. **Current line**: this project's existing REINVENT4 RNN pipeline (C01), continued as-is —
   already has 4 trained epoch checkpoints and a full metrics report in-repo
   (`reports/46k_prior_epoch_comparison.md`) to serve as the reference point.
2. **Best alternative pretrained SMILES model**: smiles-gpt (C09), fine-tuned on the same Tier 4
   saponin data once curated (`06_dataset_and_finetuning_plan.md`).
3. **SELFIES validity-oriented baseline**: ChemGPT (C10), fine-tuned on the same data converted to
   SELFIES.
4. **Graph/3D pilot**: included only if a genuinely accessible implementation + checkpoint is
   confirmed locally (per `05_long_context_512_review.md`'s and `03_candidate_models.md`'s finding
   that no graph/3D candidate surveyed this session has a natural-product-scale checkpoint or a
   confirmed-reachable code repo) — treat as **optional/likely-skipped** for the first round, not
   a firm commitment.

**Explicit non-comparability warning**: models 1–2 use SMILES, model 3 uses SELFIES, and model 4
(if run) uses a graph representation. Metrics that depend on the representation (raw token-length
distributions, tokenizer-specific validity mechanics) are **not** directly comparable across rows
and must be reported with that caveat attached, not silently normalized into one number that hides
the representation difference.

## B. Protocol requirements

- **Same data split** across all models (the aglycone-family-aware split from
  `06_dataset_and_finetuning_plan.md` §C, plus the random split reported alongside for diagnosis).
- **Comparable fine-tuning budget**: match either total gradient steps or total wall-clock time
  across models (not epochs, since dataset-relative epoch counts are not comparable across models
  with very different per-example costs); record whichever was matched and why.
- **Record total AND trainable parameter count** for each model (full fine-tune vs. any
  parameter-efficient scheme, if used).
- **Record compute/hardware used** for each run (CPU vs. GPU, memory, wall-clock) — this project's
  own existing reports show the current RNN line is CPU-feasible at ~6–7 min per 10k-sample
  sampling run (`reports/46k_prior_epoch_comparison.md`), which is a real, already-demonstrated
  data point for comparison.
- **Same sample count**: 5,000 samples per model (per required default below).
- **Same or transparently adjusted sampling strategy**: default `max_length=512`,
  `top_k=50`, `temperature=1.0` for the causal-LM candidates (C09/C10); for the RNN line (C01),
  document the closest equivalent settings actually available in REINVENT4's sampling config
  (this project's own `configs/sampling/*.toml` already show the relevant parameters:
  `num_smiles`, `unique_molecules`, `randomize_smiles`, `temperature`, `isomeric_smiles`) and state
  explicitly where a like-for-like setting does not exist (e.g. `top_k` is not a native REINVENT4
  RNN sampling parameter) rather than forcing a false equivalence.
- **Record random seeds and complete configuration** for every run, committed alongside the
  results (not just the summary numbers).
- **Do not overclaim direct comparability** where representation differs (see warning in A).

## C. Required metrics (per model, per split)

1. Valid SMILES rate (RDKit parse success)
2. RDKit sanitization rate (distinct from parse success — see `04_stereochemistry_review.md` §C
   step 2)
3. Closed-shell / non-radical rate
4. Uniqueness among valid outputs
5. **Stereo-aware uniqueness** (dedup on `canonical_isomeric_smiles`, per §C of the stereochemistry
   review — not the same number as item 4 if any duplicates differ only by stereochemistry)
6. Novelty vs. the fine-tuning dataset, using canonical isomeric identifiers (never connectivity-
   only — see the stereochemistry review's explicit warning)
7. Novelty vs. a known-saponin reference set, where available (Tier 3/4 corpus minus the training
   split)
8. Fraction with no unassigned stereocenters (`fully_stereo_defined` from the validation function)
9. Defined stereocenter-count distribution (generated vs. training-set histogram comparison)
10. E/Z assignment rate
11. Molecular-weight distribution
12. Token-length distribution (per-model tokenizer, per `05_long_context_512_review.md`)
13. Fraction reaching the length cutoff (i.e. generation stopped by hitting `max_length` rather
    than emitting EOS — a proxy for "the model wanted to keep going," worth tracking separately
    from validity)
14. Ring-count distribution
15. Sugar-unit count distribution (requires the sugar-detection logic from
    `06_dataset_and_finetuning_plan.md` §B)
16. Glycosidic-linkage plausibility proxy (rule-based: is there at least one detected glycosidic
    C–O–C bond connecting a sugar-ring match to a non-sugar-ring match? — a proxy, not a ground
    truth; see the operational saponin-likeness score below for the same caveat)
17. Aglycone-family distribution (per the family-classification rules from
    `06_dataset_and_finetuning_plan.md` §A Tier 3)
18. NPClassifier pathway/superclass/class distribution (this project's existing integration —
    `scripts/compute_npc_quick.py`, `scripts/compute_fcd_npc.py` — reused directly; note the ~2
    req/sec rate limit documented in `references/fcd_npclassifier_api.md` means 5,000 samples ×
    N models will take real wall-clock time to classify — budget for it, e.g. ~5,000/2 ≈ 42 min
    per model at the documented rate)
19. Saponin-enrichment rate using the documented operational definition below
20. Structural diversity: Bemis-Murcko scaffold count/distribution; fingerprint diversity (e.g.
    mean pairwise Tanimoto on ECFP4); nearest-neighbor similarity to training molecules
21. Manual expert-review set: a random sample, a sample of the highest-scoring outputs by the
    operational saponin-likeness score, and a sample of boundary/failure cases (e.g. valid but
    stereo-incomplete, or high saponin-likeness score but flagged as chemically implausible)
22. Memorization checks: exact isomeric-SMILES matches against the training set; nearest-neighbor
    similarity; scaffold overlap — reported together, since a model can pass an exact-match check
    while still substantially over-fitting to near-duplicates
23. Optional 3D/conformer feasibility check, only for a shortlisted subset of molecules (not all
    5,000) — e.g. can RDKit's `EmbedMolecule` generate a reasonable 3D conformer at all, as a cheap
    sanity check before any deeper structural claim

**Explicit critique noted from the literature** (search-sourced, `09_bibliography.csv`): validity,
FCD, and KL-divergence-style distribution-learning scores have been reported as anti-correlated
with novelty, i.e. optimizing purely for these metrics can trade away exactly the novelty this
project wants. No single metric above should be used in isolation to pick a winner; report the
full table and make the recommendation call using the weighted framework in
`08_model_recommendation.md`.

## D. Operational saponin-likeness score (explicitly not ground truth)

A composite, documented, and versioned rule-based score combining:
- aglycone-like core evidence (matches one of the named scaffold families, per Tier 3 rules)
- sugar-ring evidence (≥1 detected pyranose/furanose-like ring per the sugar-detection logic)
- glycosidic-linkage evidence (metric 16 above)
- stereo completeness (`fully_stereo_defined`)
- NPClassifier support (`isglycoside=True` and/or a Triterpenoid/Steroid-family class result)
- molecular-size/oxygenation plausibility (MW and O-count in the range this project's own existing
  epoch-comparison report already characterizes for its current generator: MW ~549–551,
  TPSA ~104–106, per `reports/46k_prior_epoch_comparison.md`)

**Clear warning, required to accompany every use of this score**: this is a **motif-rule proxy**,
not a validated saponin classifier. It will have false positives (molecules matching the surface
rules — a sugar-like ring near a polycyclic core — without being biosynthetically plausible
saponins) and false negatives (real, unusual saponins that don't match the specific scaffold/sugar
rules encoded). Use it to **rank and triage** candidates for the manual review queue (metric 21),
never as a sole automated accept/reject gate, and never report it to stakeholders without this
caveat attached.

## E. Reproducibility requirements

- Fixed seed for the primary run of each model; multiple-seed replicates (recommend ≥3) "where
  practical" per the task brief — practical here means: cheap for the RNN line (already CPU-fast
  per this project's own reports) and should be explicitly budgeted for the transformer lines
  given their likely higher per-sample cost.
- All configs, seeds, and exact code versions committed alongside results (not just summary
  numbers) — this benchmark run itself should produce its own dated subdirectory of raw outputs,
  analogous to how `reports/46k_prior_epoch_comparison.md` already documents this project's
  existing epoch comparison.

## F. Stopping rules for this benchmark

- The benchmark is complete when all in-scope models (§A) have all applicable metrics (§C) computed
  on both the aglycone-family split and the random split, with the manual-review sample (metric 21)
  actually reviewed by a person (not just generated and left unreviewed).
- If a candidate cannot be run within this project's stated constraints (no GPU, no paid services —
  e.g. this rules out MolMIM/C16 entirely, and likely rules out any graph/3D pilot per §A), record
  that explicitly as the stopping reason for that candidate rather than silently omitting it from
  the results table.
