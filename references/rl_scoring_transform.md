# RL Scoring Transform Guide

## Reverse Sigmoid Transform

Formula: `score = low + (high - low) / (1 + exp(k * (x - midpoint)))` where `midpoint = (high+low)/2`

## Quick Reference by Target IC50

| Target IC50 | high (ln) | low (ln) | midpoint | k | Example mean score | Notes |
|-------------|-----------|----------|----------|---|-------------------|-------|
| ~10 µM (lenient) | 5.0 | 0.0 | 2.5 | 0.5 | ~0.5 from TL prior | Plateaus at ~8 µM mean |
| ~2.7 µM (standard) | 3.0 | -1.0 | 1.0 | 0.5 | ~0.02 from TL prior, climbs to 0.78 | Reaches ~1.6 µM mean |
| ~0.5 µM (extreme) | 1.6 | -0.7 | 0.45 | 0.5 | ~0.10 from RL agent | Validity collapses to 12% |

## Critical Warnings

1. **IC50 model has a prediction floor.** The training data minimum is ~0.9 µM (ln=-0.1). Transforms targeting <0.5 µM (ln=-0.69) are impossible — the model has no training signal below that. The RL will push validity into collapse trying to reach an unachievable target.

2. **Validate validity cost vs IC50 gain.** Extreme transforms cost ~68% of valid molecules for only ~0.26 µM mean IC50 improvement. Calculate the efficiency ratio before running extreme RL.

3. **Aggregator choice is critical with multiple components:**
   - `geometric_mean`: score = (∏ components)^(1/n). If ANY component scores near zero → total score = 0. The RL has no gradient to learn from.
   - `arithmetic_mean`: score = ∑(weight_i × component_i) / ∑(weight_i). Low components are compensated by high ones. **Always use this for multi-objective (IC50 + MW + TPSA + ...) scoring.**

## Transform Math Cheat Sheet

For reverse_sigmoid with k=0.5:

| ln(IC50) | IC50 (µM) | Score (high=5, low=0) | Score (high=3, low=-1) | Score (high=1.6, low=-0.7) |
|----------|-----------|----------------------|----------------------|--------------------------|
| -2.3 | 0.1 | ~0.88 | ~0.98 | ~1.00 |
| -0.69 | 0.5 | ~0.68 | ~0.89 | ~0.95 |
| 0.0 | 1.0 | ~0.50 | ~0.73 | ~0.73 |
| 0.69 | 2.0 | ~0.32 | ~0.50 | ~0.50 |
| 1.61 | 5.0 | ~0.12 | ~0.15 | ~0.05 |
| 2.30 | 10.0 | ~0.05 | ~0.05 | ~0.00 |
| 2.64 | 14.0 | ~0.02 | ~0.02 | ~0.00 |