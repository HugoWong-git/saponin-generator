# RL Configs — Reinforcement Learning (DAP)

These configs demonstrate **Directed Alternative Progeny (DAP)** reinforcement learning using REINVENT4's staged learning framework. Start from a trained TL prior and optimise towards a scoring function.

## Available Configs

| Config | Starting Prior | Scoring | Best For |
|--------|---------------|---------|----------|
| `rl_ic50_epoch1.toml` | Epoch 1 | IC50 (geometric_mean) | Highest validity (49.7%), 98% triterpenoids |
| `rl_ic50_epoch4.toml` | Epoch 4 | IC50 (geometric_mean) | Best potency (1.65 uM), broader subclass diversity |
| `rl_light_saponins.toml` | Epoch 1 | IC50 + MW + TPSA + Rings + Fsp3 (arithmetic_mean) | Light saponins, 95% validity, MW 600-750 |

## How Scoring Works

REINVENT4 supports pluggable scoring components via `ExternalProcess`:

```toml
[[stage.scoring.component]]
[stage.scoring.component.external_process]
[[stage.scoring.component.external_process.endpoint]]
name = "My Scorer"
weight = 1.0
params.executable = "python"
params.args = "path/to/scorer.py"
params.property = "predictions"
```

The scorer script reads SMILES from stdin (one per line) and outputs versioned JSON:
```json
{"version": 1, "payload": {"predictions": [0.5, 0.7, ...]}}
```

## Aggregation

| Type | Behaviour | Use When |
|------|-----------|----------|
| `geometric_mean` | Product^(1/n), collapses to 0 if any component is low | Single-objective RL |
| `arithmetic_mean` | Weighted sum, components compensate each other | Multi-objective RL |

## Built-in REINVENT4 Scorers

| Component | Key | Description |
|-----------|-----|-------------|
| Molecular Weight | `MolecularWeight` | double_sigmoid filter |
| TPSA | `TPSA` | Polarity filter |
| NumRings | `NumRings` | Ring count filter |
| Csp3 | `Csp3` | sp3 fraction |
| SAScore | (registry) | Synthetic accessibility |

## Workflow

1. Train a TL prior (see `configs/tl/`)
2. Run RL: `python -m reinvent configs/rl/rl_ic50_epoch1.toml`
3. Sample from the checkpoint (see `configs/sampling/`)
4. Analyse with `scripts/`