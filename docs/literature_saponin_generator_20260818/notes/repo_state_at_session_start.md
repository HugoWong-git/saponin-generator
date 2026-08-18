# Repository State at Session Start (2026-08-18)

Recorded verbatim from `git status`, `git branch --show-current`, `git remote -v`, and `find`
at the very start of this session, before any files were created — see `01_search_log.md` §0
for the full commands.

- origin: https://github.com/HugoWong-git/saponin-generator
- branch: claude/molecular-generator-prior-review-uchhki
- status: clean (no uncommitted changes)
- top-level entries: .gitignore, LICENSE, README.md, configs/, data/, metrics/, priors/,
  pyproject.toml, references/, reports/, scripts/
- confirmed NOT present: archive/, checkpoints/, docs/ (before this session created it),
  experiments/, external/, src/, literature/
- existing scripts/: compute_epoch_metrics.py, compute_fcd_npc.py, compute_npc_quick.py,
  pca_umap_analysis.py, saponin_design_pilot.py, smiles_props.py
- existing priors/: 4 .prior checkpoint files (saponin_prior_46k_reg_epoch{1..4}.prior) + README.md
- existing data/: saponin_train_3k.smi, saponin_train_46k_block{1..4}.smi, saponin_train_46k_valid.smi
- existing reports/: 46k_prior_epoch_comparison.md
- existing references/: dot-to-pipe-bug-investigation.md, fcd_npclassifier_api.md
- existing metrics/: e1_vs_e4_npc.json

This note exists so future sessions don't have to re-derive this baseline from scratch, and so the
discrepancy noted in `00_README.md` (task brief described files that do not exist) is traceable to
a concrete, timestamped check rather than an assertion.
