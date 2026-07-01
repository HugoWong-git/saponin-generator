# Sample Naming Convention & Folder Layout

## Root Structure (reinvent4_smoke_test)

```
configs/       — TOML RL/TL configs (tl/, sampling/ subdirs)
data/          — SMILES data files
logs/          — All RL/TL/sampling logs (tl/, sampling/ subdirs)
metrics/       — Evaluation CSVs/JSON
models/        — Prior/chkpt files (23M each)
output/        — RL JSON config outputs (summary CSVs)
priors/        — Base PubChem prior
reports/       — Markdown reports + figures/
samples/       — All with_ic50 CSVs (SMILES + IC50 predictions)
scripts/       — Python analysis scripts
tensorboard/   — All tb_* TensorBoard dirs (42 dirs)
venv/          — Virtual environment
sampling_reinvent.xlsx — Original input file
smiles_physchem_*.csv  — Physicochemical property files
```

## Sample File Naming

Format: `{model}_{suffix}.csv`

### with_ic50 files (definitive — include IC50 predictions)

| File | Model Description |
|------|------------------|
| `tl_e1_with_ic50.csv` | Epoch 1 TL prior (saponin) |
| `tl_e4_with_ic50.csv` | Epoch 4 TL prior (saponin) |
| `rl_e1_with_ic50.csv` | RL agent from E1 prior |
| `rl_e4_v3_with_ic50.csv` | RL agent from E4 prior (best balance) |
| `rl_extreme_with_ic50.csv` | Extreme IC50 push from E4-V3 |
| `rl_light_e1_with_ic50.csv` | Light saponin multi-objective from E1 |
| `generic_prior_with_ic50.csv` | PubChem prior baseline |
| `generic_rl_with_ic50.csv` | Generic 300-step RL |
| `genrl_ext_with_ic50.csv` | Generic 1300-step RL |
| `genrl_superext_with_ic50.csv` | Generic 2656-step RL |
| `generic_final_with_ic50.csv` | Generic 5656-step RL (best) |
| `rl_generic_challenge_v2_with_ic50.csv` | Challenge: 2000 steps from scratch |
| `rl_e4_v1_with_ic50.csv` | RL V1 (200 steps, lenient) |
| `rl_e4_v3_2k_with_ic50.csv` | RL V3 2k sample |
| `rl_e4_v3_100k_with_ic50.csv` | RL V3 100k sample |

### Column Format

Columns: SMILES, SMILES_state, NLL, ln_IC50, IC50_uM

- Invalid molecules have SMILES_state=0 and blank IC50 fields
- IC50 is in µM units

## Key Directories

- `../../` — project root
- `(your IC50 model path)` — IC50 consensus model