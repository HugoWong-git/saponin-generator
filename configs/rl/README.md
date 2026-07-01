# RL Configs — Reinforcement Learning (DAP)

These configs demonstrate **Directed Alternative Progeny (DAP)** reinforcement learning using REINVENT4's staged learning framework. Start from a trained TL prior and optimise generation towards a scoring function.

## Available Configs

| Config | Starting Prior | Scoring | Description |
|--------|---------------|---------|-------------|
| `rl_epoch1.toml` | Epoch 1 | SAScore (built-in) | Example single-objective RL |
| `rl_epoch4.toml` | Epoch 4 | SAScore (built-in) | Example single-objective RL |
| `rl_light_saponins.toml` | Epoch 1 | MW + TPSA + Rings + Fsp3 (arithmetic_mean) | Multi-objective: drug-like saponins |

## Custom Scoring

Replace the built-in scorer with your own via `ExternalProcess`:

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

The scorer script reads SMILES from stdin (one per line) and outputs:
```json
{"version": 1, "payload": {"predictions": [0.5, 0.7, ...]}}
```

## Aggregation

| Type | Behaviour | Use When |
|------|-----------|----------|
| `geometric_mean` | Product^(1/n), collapses to 0 if any component is low | Single-objective |
| `arithmetic_mean` | Weighted sum, components compensate each other | Multi-objective |

## Built-in REINVENT4 Scorers

| Component | Key | Description |
|-----------|-----|-------------|
| Molecular Weight | `MolecularWeight` | double_sigmoid filter |
| TPSA | `TPSA` | Polarity filter |
| NumRings | `NumRings` | Ring count filter |
| Csp3 | `Csp3` | sp3 fraction |
| SAScore | `SAScore` | Synthetic accessibility |

## Workflow

1. Train a TL prior: `python -m reinvent configs/tl/tl_46k_reg.toml`
2. Run RL: `python -m reinvent configs/rl/rl_epoch1.toml`
3. Sample from the checkpoint: `python -m reinvent configs/sampling/sampling_rl_epoch1.toml`
4. Analyse with scripts in `scripts/`