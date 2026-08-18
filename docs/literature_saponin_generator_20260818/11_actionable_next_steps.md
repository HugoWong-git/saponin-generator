# Actionable Next Steps — Two Weeks

Organized by execution environment, per the task's required structure. Each item states which
document it follows up on.

## Cloud-safe tasks (no GPU, no training, no package installation beyond what's already available)

- [ ] Re-run the blocked WebFetch/primary-source reads from a network context where
  `arxiv.org`, `nature.com`, `pubs.acs.org`, `pubs.rsc.org`, `pmc.ncbi.nlm.nih.gov`,
  `chemrxiv.org`, `zenodo.org`, and `huggingface.co` are reachable, and replace the
  `EGRESS_BLOCKED_THIS_SESSION` / `search_engine_synthesis` markers in `02_candidate_models.csv`
  and `09_bibliography.csv` with directly-verified values, especially the HuggingFace model cards
  for ChemGPT-4.7M/19M/1.2B (C10) and the exact license/context-length fields.
- [ ] Query COCONUT and LOTUS directly (their web portals were not reached this session) to get
  current, exact record counts and confirm their redistribution license terms for Tier 2 of
  `06_dataset_and_finetuning_plan.md`.
- [ ] Confirm TeroKit's bulk-download/redistribution terms with the maintainers or published terms
  of use before any large-scale scraping (Tier 3 data source, `06_dataset_and_finetuning_plan.md`).
- [ ] Read the 2026 Natural Product Reports review, "Chemical language models for natural product
  discovery" (DOI in `09_bibliography.csv`), as a first pass to catch any candidate this session's
  search queries missed.

## Local-machine tasks (clone + inspect, still no training)

- [ ] Clone `sanjaradylov/smiles-gpt`, `ohuelab/npgpt`, and `datamol-io/safe` and directly inspect
  `config.json` / tokenizer files to resolve every `NEEDS_LOCAL_VERIFICATION` context-length field
  in `02_candidate_models.csv` (rows C06, C09, C15). This is the single highest-value follow-up —
  it directly answers recommendation question 2/5 in `08_model_recommendation.md`.
- [ ] Tokenize this project's existing `data/saponin_train_46k_valid.smi` with (a) smiles-gpt's
  actual tokenizer and (b) a character-level baseline, and record the full token-length
  distribution (min/median/p90/p95/p99/max) per `05_long_context_512_review.md` §D.1. This
  directly tests whether 512 is an adequate ceiling before any other engineering commitment.
- [ ] Inspect smiles-gpt's and NPGPT's actual preprocessing code (not just the README) to confirm
  whether isomeric SMILES are retained end-to-end, resolving the `stereochemistry_removed_in_
  preprocessing` = `NOT_STATED` fields for C06/C09.

## GPU tasks (explicitly deferred — do not start without separate authorization)

- [ ] Fine-tune smiles-gpt on a curated Tier 4 saponin corpus (once §"data-curation tasks" below
  is complete) and run the benchmark protocol in `07_benchmark_plan.md`.
- [ ] Fine-tune ChemGPT (SELFIES) on the same corpus as the validity-oriented baseline.
- [ ] Any pilot of a graph/3D generator (C18) — correctly scoped as `FUTURE_WORK`, not a two-week
  item.

## Data-curation tasks

- [ ] Build the Tier 3 aglycone-family classification rule set (Bemis-Murcko + SMARTS per named
  skeleton: oleanane, ursane, lupane, dammarane, lanostane, cycloartane, cucurbitane, steroidal/
  spirostane/furostane) per `06_dataset_and_finetuning_plan.md` §A Tier 3.
- [ ] Build the sugar-ring / glycosidic-linkage detection logic needed for the
  `sugar_identity_list`, `glycosidic_linkage_annotations`, and `glycosylation_positions` metadata
  fields (§B of the same document) — scope this as its own sub-task, it is nontrivial.
- [ ] Run the full stereo-validation function (`04_stereochemistry_review.md` §C) over the existing
  `data/saponin_train_46k_valid.smi` to establish a baseline stereo-completeness rate for the data
  this project already has, before curating anything new.
- [ ] Assemble the aglycone-family/scaffold-aware split (§C of the dataset plan) for whatever
  Tier 4 corpus results, alongside the random split, for the memorization-risk comparison.

## Manual chemical-review tasks

- [ ] Once any benchmark run (per `07_benchmark_plan.md`) produces output, manually review the
  three required samples: random outputs, high-scoring outputs (by the operational saponin-
  likeness score), and boundary/failure outputs — this cannot be automated and is explicitly
  required before trusting the operational score for anything beyond triage.
- [ ] Spot-check the Tier 3 aglycone-family classification rules against a handful of known
  reference saponins per family, before trusting the automated Tier 3/4 labeling at scale.

## Tasks that must wait for baseline results

- [ ] The choice between "exclude," "longer-context model," "scaffold-plus-glycan modular
  representation," or "separate model" for over-512-token saponins (`05_long_context_512_review.md`
  §D.4) — this is a data-dependent decision that cannot be made until the token-length measurement
  above is complete.
- [ ] Any positional-embedding-extension work (`05_long_context_512_review.md` §E) — only worth
  doing if the measurement shows a meaningful fraction of real saponins actually exceed the chosen
  checkpoint's context length.
- [ ] Committing to SAFE-GPT (C15) despite its non-commercial weight license, or to Group SELFIES
  (C14) despite requiring a from-scratch build — both are `FUTURE_WORK` calls that should be
  revisited only after the smiles-gpt/REINVENT4 dual-track baseline (per
  `08_model_recommendation.md`) has real benchmark numbers to compare against.
