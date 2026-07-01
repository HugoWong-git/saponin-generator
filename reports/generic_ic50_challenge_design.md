# Generic IC50 Challenge — Design Document

## Goal
Beat the previous Generic-RL line (mean IC50 8.0 µM, validity 95.6%) by designing a better RL strategy starting from the original generic PubChem prior, WITHOUT reusing any saponin TL priors or existing RL agents.

## Key Insights from Previous Runs

1. **Generic-RL (300 steps, sigma=128)**: Score stuck at 0.09 — far too few steps for the generic prior to learn triterpenoid SAR.

2. **Generic-RL Extended (1000 steps)**: Score rose to 0.68, IC50 2.12 µM — proving that **many steps** are needed.

3. **Generic-RL Super Extended (2000 steps)**: Score 0.68, IC50 0.74 µM — more steps helped but plateaued.

4. **Generic-RL Final (3000 steps, currently running)**: Score **0.76 at step 2979** — best yet.

5. **Problem with multi-component scoring**: `geometric_mean` of IC50 + property constraints collapsed when IC50 scored near zero. Need `arithmetic_mean`.

6. **Problem with extreme transforms**: Too-tight transforms (high=2.3, low=-2.3) create vanishing gradients when the agent is far from target.

## Design Strategy

### Two-Stage Staged Learning

**Stage 1 — "Explore & Learn"** (500 steps):
- Mild IC50 transform that gives meaningful gradient across the generic prior's initial range
- Gentle MW constraint to prevent wild exploration
- SA Score to prevent synthetically impossible molecules
- Conservative sigma=96

**Stage 2 — "Push & Refine"** (1000 steps):
- Tighter IC50 transform targeting 0.5-2 µM range
- Lighter property constraints (agent has already learned basic SAR)
- Standard sigma=128

### Scoring Function

Using `arithmetic_mean` to prevent any single low-scoring component from killing the total score (unlike geometric_mean which was problematic in multi-objective settings).

### RL Hyperparameters

- DAP as the learning strategy
- sigma=96 (Stage 1), sigma=128 (Stage 2) — conservative to avoid collapse
- rate=0.0001 throughout
- batch_size=64
- temperature=1.0
- unique_sequences filter via distance_threshold=100

## Comparison with Previous Runs

| Aspect | Old Generic-RL | Old Extreme | **New Challenge** |
|--------|---------------|-------------|-------------------|
| Starting prior | Generic | E4-V3 agent | **Generic** |
| Stages | 1 | 1 | **2** |
| Transform | high=3, low=-1 | high=1.6, low=-2.3 | **mild→tight** |
| Scoring | geometric_mean | geometric_mean | **arithmetic_mean** |
| Property constraints | None | None | **MW + SA Score** |
| Steps | 300 | 500 | **1500** |
| sigma | 128 | 256 | **96 → 128** |
