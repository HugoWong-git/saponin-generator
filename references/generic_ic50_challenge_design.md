# Generic IC50 Challenge — Two-Stage RL Design

## Motivation

Previous Generic-RL runs (300-5656 steps) starting from the PubChem prior showed that:
- Single-stage RL with mild transforms learns slowly (0.02 for first 100 steps)
- The agent must simultaneously learn IC50 relevance AND chemistry — too many tasks at once
- Property constraints (MW, Fsp3) help but `geometric_mean` collapses when IC50 scores near zero

## Two-Stage Strategy

**Stage 1 — "Explore & Learn" (500 steps, sigma=96):**
- Mild IC50 transform (high=4, low=0, k=0.5) — wide range, gentle gradient
- MW constraint (300-1000 Da) — loose, prevents extreme molecules
- Fsp3 encouragement (sigmoid) — nudges toward NP-like saturation  
- Scoring: `arithmetic_mean` (prevents zero-collapse)
- Conservative sigma=96 to avoid early divergence

**Stage 2 — "Push & Refine" (1000 steps, sigma=128):**
- Tighter IC50 transform (high=2.5, low=-1.0, k=0.5) — targets 0.5-2 µM
- Lighter constraints — agent has already learned basic SAR
- Standard sigma=128 for exploration

## Why This Differs from Previous Runs

| Aspect | Old Generic-RL | Old Extreme | **Two-Stage** |
|--------|---------------|-------------|---------------|
| Scoring | geometric_mean | geometric_mean | **arithmetic_mean** |
| Constraints | None | None | MW + Fsp3 |
| First 25 steps score | 0.02 | 0.63 (from E4 ckpt) | **0.41** |
| Steps | 300 | 500 | **1500** |
| sigma | 128 | 256 | **96 → 128** |

## Config

`configs/rl_ic50_generic_challenge.toml`

## Key Innovation

Using `arithmetic_mean` allows property constraints to **guide** the agent from early steps without collapsing the total score. The mild Stage 1 transform maps the generic prior's broad IC50 range (2-30 µM) to meaningful scores (0.2-0.6), giving the agent a useful gradient from the very first step.
