# Saponin Generator

Generative chemistry pipeline for triterpenoid saponins using [REINVENT4](https://github.com/MolecularAI/REINVENT4).

Train a REINVENT4 model on saponin SMILES, sample novel triterpenoids, and optionally guide generation with custom scoring functions (e.g., synthetic accessibility, physicochemical properties).

## Quick Start

```bash
# 1. Install REINVENT4 (separate step — see reinvent4 repo)
git clone https://github.com/MolecularAI/REINVENT4.git

# 2. Activate REINVENT4 environment, then train
python -m reinvent configs/tl/tl_46k_reg.toml

# 3. Sample from the trained prior
python -m reinvent configs/sampling/sampling_tl_epoch4.toml

# 4. Compute physicochemical properties
python scripts/smiles_props.py --input samples/sample.csv --output samples/scored.csv
```

## Repository Structure

```
saponin-generator/
├── configs/
│   ├── tl/           # Transfer learning configs
│   ├── sampling/     # Sampling configs
│   └── rl/           # Reinforcement learning (DAP) configs
├── data/             # Training SMILES datasets
├── scripts/          # Pipeline and analysis scripts
├── templates/        # Reusable config templates
├── priors/           # Pre-trained generative priors
├── metrics/          # Benchmark results
├── reports/          # Analysis reports
└── references/       # Design guidance
```

## Pipeline Overview

| Step | Config | Description |
|------|--------|-------------|
| **Transfer Learning** | `configs/tl/tl_3k.toml` | Minimal demo (3k SMILES, 1 epoch) |
| | `configs/tl/tl_3k_reg.toml` | Small-scale regularised (3k, 2 epochs) |
| | `configs/tl/tl_46k.toml` | Full NLL baseline (46k, 1 epoch) |
| | `configs/tl/tl_46k_probe.toml` | Quick data quality check |
| | `configs/tl/tl_46k_reg.toml` | **Main result** — 4 epochs, regularised (46k) |
| **Sampling** | `configs/sampling/sampling_tl_epoch3.toml` | Sample from epoch 3 prior |
| | `configs/sampling/sampling_tl_epoch4.toml` | Sample from epoch 4 prior (final) |
| | `configs/sampling/sampling_tl_3k.toml` | Sample from 3k demo prior |
| | `configs/sampling/sampling_rl_epoch1.toml` | Sample from RL-optimised agent |
| | `configs/sampling/sampling_rl_light.toml` | Sample from light saponin RL agent |
| **RL (DAP)** | `configs/rl/rl_epoch1.toml` | Single-objective optimisation (SAScore) |
| | `configs/rl/rl_epoch4.toml` | Single-objective optimisation (SAScore) |
| | `configs/rl/rl_light_saponins.toml` | Multi-objective: MW + TPSA + Rings + Fsp3 |

## Pre-trained Priors

Four epoch checkpoints (23 MB each) are included in `priors/`:
- `saponin_prior_46k_reg_epoch1.prior` — Epoch 1
- `saponin_prior_46k_reg_epoch2.prior` — Epoch 2
- `saponin_prior_46k_reg_epoch3.prior` — Epoch 3 (best validity/novelty balance)
- `saponin_prior_46k_reg_epoch4.prior` — Epoch 4 (final, most specialised)

Use these directly for sampling, or as starting points for RL.

## Scoring Components

The pipeline supports pluggable scoring via REINVENT4's `ExternalProcess`:

- **Physicochemical properties** — MW, logP, TPSA, HBD, HBA, RotB, Fsp3, rings
- **Synthetic accessibility** — SAScore (built into REINVENT4)
- **Custom scorers** — Implement your own via `ExternalProcess` (see `configs/rl/` and `templates/multi_objective_rl_config.toml`)

## Data

The `data/` directory contains triterpenoid saponin SMILES compiled from published literature. Datasets range from 3k to 46k SMILES.

## License

Apache 2.0 — see `LICENSE`.

## References

| Resource | Link |
|----------|------|
| REINVENT4 | [MolecularAI/REINVENT4](https://github.com/MolecularAI/REINVENT4) |
| FCD (Frechet ChemNet Distance) | [pmed/fcd](https://github.com/pmed/fcd) |