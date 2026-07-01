# RL Configs — Reinforcement Learning with REINVENT4 DAP

These configs demonstrate **Directed Alternative Progeny (DAP)** reinforcement learning with REINVENT4's staged learning framework.

## Architecture

Each config follows this pattern:

```toml
[stage.scoring]
type = "geometric_mean"  # or "arithmetic_mean"

[[stage.scoring.component]]
[stage.scoring.component.external_process]
[[stage.scoring.component.external_process.endpoint]]
name = "<scorer-name>"
weight = <float>
params.executable = "python"
params.args = "path/to/scorer.py"
params.property = "predictions"
```

## IC50 Scoring

Several configs reference `../../scripts/ic50_scorer.py` via ExternalProcess. This scorer is a **custom component that you must provide yourself**. The repo does not include it because the IC50 consensus model used in our work was trained on published literature data and is not redistributable.

To use IC50-guided RL:

1. Train or source your own IC50 prediction model
2. Wrap it as a script that reads SMILES from stdin and outputs versioned JSON:
   ```json
   {"version": 1, "payload": {"predictions": [scores]}}
   ```
3. Point `params.args` to your wrapper script
4. Tune the reverse_sigmoid transform midpoint to match your potency target

## Scorer Types (Available in REINVENT4)

| Type | Key | Description |
|------|-----|-------------|
| External Process | `external_process` | Your Python model via stdin/stdout JSON |
| Molecular Weight | `MolecularWeight` | MW filter (double_sigmoid) |
| TPSA | `TPSA` | Polarity filter (double_sigmoid) |
| NumRings | `NumRings` | Ring count filter (double_sigmoid) |
| Csp3 Fraction | `Csp3` | sp3 carbon fraction (sigmoid) |
| SAScore | (in registry) | Synthetic accessibility (reverse_sigmoid) |

## Multi-Objective Scoring

For constraining generation on multiple properties, use `arithmetic_mean` aggregation (NOT `geometric_mean`). See `rl_saponin_light_epoch1.toml` for a reference implementation that combines:

- IC50 (0.35 weight)
- Molecular Weight (0.25)
- TPSA (0.20)
- Ring count (0.12)
- Fsp3 (0.08)

A reusable template is available at `templates/multi_objective_rl_config.toml`.

## Available Configs

| Config | Description | Scoring |
|--------|-------------|---------|
| `rl_saponin_ic50_epoch1.toml` | IC50 RL from epoch 1 prior | IC50 (geometric_mean) |
| `rl_saponin_ic50_epoch4.toml` | IC50 RL from epoch 4 prior | IC50 (geometric_mean) |
| `rl_saponin_ic50_epoch4_v3.toml` | Tuned version from epoch 4 | IC50 (geometric_mean) |
| `rl_saponin_light_epoch1.toml` | Light saponins, multi-objective | IC50 + MW + TPSA + Rings + Fsp3 |
| `rl_saponin_ic50_extreme.toml` | Aggressive IC50 push from E4 | IC50 (double sigma) |
| `rl_ic50_generic_*.toml` | IC50 RL from PubChem prior (baseline) | IC50 (various) |