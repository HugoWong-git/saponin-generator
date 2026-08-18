# Literature & Model-Selection Review — Saponin Generator (2026-08-18)

## Scope

This directory is a research deliverable, not code. It answers one question in depth:
**which public pretrained molecular-generation model (if any) is the best starting point for
fine-tuning a stereochemically faithful, saponin-focused de novo generator**, and lays out the
dataset, tokenization, and benchmark plan needed to test that choice.

No training, fine-tuning, sampling, package installation, GPU workload, or Docker workflow was
run. No existing repository file was edited, renamed, moved, or deleted. All new files live
under this directory, `docs/literature_saponin_generator_20260818/`.

## Search date

All searches and access checks in this review were performed on **2026-08-18** (single session).
Where a source's content could plausibly change (GitHub READMEs, HuggingFace model cards, web
databases), treat findings as a snapshot from that date, not a live status.

## A critical, load-bearing limitation: network egress policy

This session's outbound network access goes through an egress proxy that **blocks essentially
every academic publisher and preprint-server domain** that was tested:

| Domain | Result |
|---|---|
| `arxiv.org` | EGRESS_BLOCKED |
| `nature.com` / `www.nature.com` | EGRESS_BLOCKED |
| `pubs.acs.org` | EGRESS_BLOCKED |
| `pubs.rsc.org` | EGRESS_BLOCKED |
| `link.springer.com`, `jcheminf.biomedcentral.com` | EGRESS_BLOCKED |
| `pmc.ncbi.nlm.nih.gov` | EGRESS_BLOCKED |
| `chemrxiv.org`, `biorxiv.org` | EGRESS_BLOCKED |
| `zenodo.org` | EGRESS_BLOCKED |
| `huggingface.co` | EGRESS_BLOCKED |
| `github.com`, `raw.githubusercontent.com` | **reachable** |

Practical consequence: **no paper's full text was directly read this session.** Every literature
claim in these documents is sourced from a general web-search tool's AI-synthesized snippets
(citing the underlying URLs, which are recorded), **except** for a handful of GitHub repository
READMEs that were fetched directly and are labeled `primary_repo_readme_fetched` in the evidence
tables, and this repository's own existing files, labeled `primary_repo_artifact`. This is stated
explicitly and repeatedly in `01_search_log.md`, `02_candidate_models.csv`
(`source_type`/`confidence` columns), and `09_bibliography.csv` (`access_status` column), per the
task's own instruction never to claim full text was read when only a snippet or abstract was
available.

**Consequently, zero PDFs were downloaded** (`10_open_access_pdf_manifest.csv` has a header row
only). Most of the papers cited are in fact open access (arXiv, PMC, PNAS Nexus, RSC Digital
Discovery, Nature journals with OA articles) — the block is this session's network policy, not a
paywall — but that distinction could not be exploited without a working egress path. This is
recorded per-reference in the bibliography rather than mislabeled as `PAYWALLED_NO_LEGAL_FULLTEXT_FOUND`,
which is a different failure mode.

## A second finding worth flagging: the task's assumed "existing" repository materials do not exist

The task brief asserted a set of pre-existing repository conventions and files — `archive/`,
`checkpoints/`, `docs/`, `experiments/`, `external/`, `src/`, `literature/*.md`, and scripts named
`scripts/agentic_triterpenoid_train.py`, `src/experiment/finetune_triterpenoid_v1.py`,
`scripts/sample_triterpenoid_dryrun.py`, `scripts/evaluate_generated_triterpenoid.py`,
`scripts/smi_to_csv.py`, `scripts/run_pk_eval_for_run.sh`. A directory listing and targeted greps
at the start of this session confirmed **none of these exist** in `HugoWong-git/saponin-generator`
as of this session (verified via `git status`, `ls`, and `find`; see `01_search_log.md` §0). The
repository's actual current structure is `configs/`, `data/`, `metrics/`, `priors/`, `references/`,
`reports/`, `scripts/` (with different script names: `compute_epoch_metrics.py`,
`compute_fcd_npc.py`, `compute_npc_quick.py`, `pca_umap_analysis.py`, `saponin_design_pilot.py`,
`smiles_props.py`), plus `README.md`, `LICENSE`, `pyproject.toml`.

This review proceeds using the **actual** repository state, reuses the two real existing
reference files that do exist (`references/fcd_npclassifier_api.md`,
`references/dot-to-pipe-bug-investigation.md`, plus `reports/46k_prior_epoch_comparison.md` and
`priors/README.md`) as primary evidence wherever relevant, and does not fabricate content to match
the non-existent files described in the brief. If the "existing" files were meant to exist in a
different branch, fork, or a planned future commit, that should be reconciled by a human before
these documents are treated as a full picture of "what already exists."

## Directory contents

| File | Purpose |
|---|---|
| `00_README.md` | This file. |
| `01_search_log.md` | Search engines used, query families, dates, outcomes, blocked sources. |
| `02_candidate_models.csv` | 21-row structured candidate table (61 columns per the required schema). |
| `03_candidate_models.md` | Readable narrative version of the candidate comparison. |
| `04_stereochemistry_review.md` | Representation comparison + mandatory validation spec + warnings. |
| `05_long_context_512_review.md` | Tokenization and 512-token feasibility analysis. |
| `06_dataset_and_finetuning_plan.md` | Four-tier data hierarchy, metadata schema, split/augmentation plan. |
| `07_benchmark_plan.md` | The first fair model-selection experiment: metrics, baselines, protocol. |
| `08_model_recommendation.md` | Executive decision memo answering the 8 required questions. |
| `09_bibliography.csv` | 27 references with access-status labeling. |
| `10_open_access_pdf_manifest.csv` | Empty (header only) — see explanation above. |
| `11_actionable_next_steps.md` | Two-week plan split by execution environment. |
| `open_access_pdfs/` | Empty — no PDF could be legally fetched given the network policy this session. |
| `source_snapshots/` | Plain-text snapshots of the few primary sources actually fetched this session (GitHub READMEs). |
| `code_and_checkpoint_links/` | One short note per major candidate repository/checkpoint. |
| `notes/` | Miscellaneous working notes (in-repo primary-source extracts). |

## How to extend this review

1. If network access to `arxiv.org`, `nature.com`, `pubs.acs.org`, `pubs.rsc.org`,
   `pmc.ncbi.nlm.nih.gov`, `chemrxiv.org`, `zenodo.org`, and `huggingface.co` becomes available
   (e.g. from a non-sandboxed machine), re-run the searches in `01_search_log.md` §2 and replace
   every `search_engine_synthesis` / `EGRESS_BLOCKED_THIS_SESSION` marker in
   `02_candidate_models.csv` and `09_bibliography.csv` with directly-verified values.
2. Clone `sanjaradylov/smiles-gpt`, `ohuelab/npgpt`, and `datamol-io/safe` locally and inspect
   `config.json` / tokenizer files directly to resolve every `NEEDS_LOCAL_VERIFICATION` context-
   length and stereochemistry-preprocessing field in the candidate table — this was explicitly out
   of scope for this cloud-only, no-cloning, no-package-installation session.
3. Before large-scale bulk extraction from TeroKit, confirm redistribution/bulk-download terms
   directly with the maintainers or the site's terms of use (not confirmed this session).
4. Re-run `01_search_log.md`'s query list roughly every 3–6 months; this is a fast-moving field
   (three of the papers cited here are dated 2025–2026).
