# Code and Checkpoint Links — Quick Reference

One line per major candidate from `02_candidate_models.csv`. "Verified" = directly reached via
WebFetch this session (github.com / raw.githubusercontent.com only — see `00_README.md`).
Everything else is a URL surfaced by WebSearch and not independently confirmed reachable/accurate
this session.

| Candidate | Code | Checkpoint | Verified? |
|---|---|---|---|
| REINVENT4 (C01/C02) | https://github.com/MolecularAI/REINVENT4 | Zenodo (linked from README, host blocked this session) | Code repo page: yes. Zenodo checkpoint page: no. |
| REINVENT v1 (C03) | https://github.com/MarcusOlivecrona/REINVENT | none found | No |
| Moret/Grisoni (C05) | https://github.com/ETHmodlab/virtual_libraries | none found | No |
| NPGPT (C06) | https://github.com/ohuelab/npgpt | Google Drive links referenced in-repo | README: yes (see source_snapshots/npgpt_README_excerpt.md) |
| smiles-gpt (C09) | https://github.com/sanjaradylov/smiles-gpt | in-repo `checkpoints/benchmark-5m` | README: yes (see source_snapshots/smiles-gpt_README_excerpt.md) |
| ChemGPT (C10) | none found this session | https://huggingface.co/ncfrey/ChemGPT-4.7M , -19M , -1.2B | No (huggingface.co blocked) |
| MolGPT (C11) | URL not independently confirmed this session | none found | No |
| Chemformer / MolBART (C12) | https://github.com/MolecularAI/Chemformer , https://github.com/MolecularAI/MolBART | not confirmed this session | No |
| SMILES Transformer (C13) | https://github.com/DSPsleeporg/smiles-transformer | not confirmed this session | No |
| Group SELFIES (C14) | likely https://github.com/aspuru-guzik-group/group-selfies (inferred, unverified) | n/a (representation, not a model) | No |
| SAFE-GPT (C15) | https://github.com/datamol-io/safe | https://huggingface.co/datamol-io/safe-gpt (per WebSearch) | Code repo: yes (see source_snapshots/safe_README_excerpt.md). HF checkpoint page: no. |
| MolMIM (C16) | https://github.com/NVIDIA-BioNeMo-blueprints/generative-virtual-screening (framework only) | https://build.nvidia.com/nvidia/molmim-generate (gated NIM endpoint) | No |
| TeroKit (C19) | n/a (web server, not code) | n/a | No (site not reached this session) |
| NPClassifier (C20) | already in use — see `references/fcd_npclassifier_api.md` in this repo | hosted API: https://npclassifier.gnps2.org/classify | Yes — this repo's own working integration |

Every URL above is also present, with full context, in `02_candidate_models.csv`
(`code_url`/`checkpoint_url`/`model_card_url` columns).
