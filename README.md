# Saponin Generator

Generative chemistry pipeline for triterpenoid saponins using [REINVENT4](https://github.com/MolecularAI/REINVENT4).

Train a REINVENT4 model on saponin SMILES, sample novel triterpenoids, and optionally guide generation with custom scoring functions (e.g., predicted potency, physicochemical properties).

## Quick Start

```bash
# 1. Install REINVENT4 (separate step — see reinvent4 repo)
git clone https://github.com/MolecularAI/REINVENT4.git

# 2. Activate REINVENT4 environment, then train
python -m reinvent configs/tl/transfer_learning_saponin_46k_reg.toml

# 3. Sample from the trained prior
python -m reinvent configs/sampling/sampling_epoch4.toml

# 4. Score with physicochemical properties
python scripts/smiles_props.py --input samples/sample.csv --output samples/scored.csv
```

## Repository Structure

```
saponin-generator/
├── configs/
│   ├── tl/           # Transfer learning TOML configs
│   ├── sampling/     # Sampling TOML configs
│   └── rl/           # Reinforcement learning configs (DAP)
├── data/             # Training SMILES datasets
├── scripts/          # Pipeline and analysis scripts
├── templates/        # Reusable config templates
├── priors/           # Pre-trained generative priors
├── metrics/          # Benchmark results
├── reports/          # Analysis reports and findings
└── references/       # Design notes and guidance
```

## Training Pipelines

| Pipeline | Data | Description |
|----------|------|-------------|
| 3k Dry Run | 3,000 SMILES | Quick NLL test (1 epoch) |
| 3k Regularized | 3,000 SMILES | 2-epoch regularized training |
| 46k Probe | 45,966 SMILES | Full NLL probe (1 epoch) |
| 46k 4-Block Pure NLL | 46k in 4 blocks | Sequential block training |
| 46k 4-Epoch x 4-Block Reg | 46k in 4 blocks | 16 total block-epochs, regularized |

## Pre-trained Priors

Four epoch checkpoints (23 MB each) are included in `priors/`:
- `saponin_prior_46k_reg_epoch1.prior` -- Epoch 1
- `saponin_prior_46k_reg_epoch2.prior` -- Epoch 2
- `saponin_prior_46k_reg_epoch3.prior` -- Epoch 3 (best validity/novelty balance)
- `saponin_prior_46k_reg_epoch4.prior` -- Epoch 4 (final, most specialised)

## Scoring Components

The pipeline supports pluggable scoring via REINVENT4's `ExternalProcess`:

- **Physicochemical properties** -- MW, logP, TPSA, HBD, HBA, RotB, Fsp3, rings
- **Synthetic accessibility** -- SAScore (built into REINVENT4)
- **Custom scorers** -- Implement your own via `ExternalProcess` (see `templates/multi_objective_rl_config.toml`)

## Data

The `data/` directory contains triterpenoid saponin SMILES compiled from published literature. Datasets range from 3k to 46k SMILES.

Block files (`_block{1-4}.smi`) partition the 46k dataset into equal quarters for incremental training.

## License

Apache 2.0 -- see `LICENSE`.

## References

| Resource | Link |
|----------|------|
| REINVENT4 | [MolecularAI/REINVENT4](https://github.com/MolecularAI/REINVENT4) |
| FCD (Frechet ChemNet Distance) | [pmed/fcd](https://github.com/pmed/fcd) |