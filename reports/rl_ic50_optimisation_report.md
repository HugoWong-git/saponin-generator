# REINVENT4 RL Optimisation — IC50-Guided De Novo Design

## Setup

| Parameter | Value |
|-----------|-------|
| **Starting prior** | `models/saponin_prior_46k_reg_epoch4.prior` |
| **RL algorithm** | DAP (Difference of Average Priors) |
| **Sigma** | 128 |
| **Learning rate** | 0.0001 |
| **Batch size** | 64 |
| **Max steps** | 200 (completed all) |
| **Scoring** | ExternalProcess → consensus IC50 model |
| **IC50 model** | `saved_models/consensus_top10_20260626_120216.joblib` (10-model ensemble: 8×CatBoost, 1×XGBoost, 1×RandomForest) |
| **IC50 model features** | Morgan ECFP fingerprints at radii 2-5, sizes 1024-2048, with feature selection |
| **Score transform** | Reverse sigmoid: high=5.0, low=0.0, k=0.5 (maps ln IC50 → score in [0,1]) |
| **Device** | CPU |
| **Peak memory** | 1606 MiB |

## RL Training Progress

- **Initial score (step 16):** 0.49
- **Final score (step 200):** 0.73
- **Agent NLL:** 48.4 → 29.6
- **Validity:** consistently 89-100%

Score steadily increased from 0.49 → 0.73 over 200 steps, demonstrating successful learning of the IC50 objective.

## IC50 Distribution Comparison

| Metric | Epoch4 Prior | RL Agent | Change |
|--------|-------------|----------|--------|
| Mean ln(IC50) | 2.56 | 2.07 | **-0.49** |
| Mean IC50 (µM) | 13.98 | 8.21 | **-5.77** (↓41%) |
| Median IC50 (µM) | 13.11 | 7.95 | **-5.16** (↓39%) |
| Q1 IC50 (µM) | 10.15 | 6.79 | **-3.36** |
| Q3 IC50 (µM) | 16.86 | 9.27 | **-7.59** |
| % with IC50 < 5 µM | 1.3% | 4.5% | **+3.2×** |
| % with IC50 < 10 µM | 23.8% | 84.4% | **+3.5×** |

## Files

| Item | Path |
|------|------|
| RL config | `configs/rl_saponin_ic50_epoch4.toml` |
| RL log | `logs/rl_saponin_ic50_epoch4.log` |
| IC50 scoring wrapper | `scripts/ic50_scorer.py` |
| RL checkpoint (agent) | `models/saponin_ic50_rl_epoch4.chkpt` (23M) |
| RL agent samples (2k) | `samples/rl_agent_samples.csv` |
| Comparison metrics | `metrics/ic50_rl_comparison.json` |

## Observations

1. **IC50 optimisation successful:** The RL agent generates molecules with substantially better predicted IC50 values (median 8.0 µM vs 13.1 µM, a 39% improvement).

2. **Fraction of potent molecules greatly increased:** 84% of RL-generated molecules have IC50 < 10 µM compared to only 24% from the prior.

3. **No mode collapse observed:** The agent maintained diverse triterpenoid chemistry through all 200 steps. Validity remained high (~95-100%).

4. **Caveat:** The IC50 model is a predictive model trained on TeroKit data, not a true biochemical assay. The scores represent predicted potency, which should be validated experimentally. The RL may have found artifacts or adversarial SMILES that exploit the fingerprint model.

5. **Next steps:** Add property constraints (MW, logP, TPSA, synthetic accessibility) as additional scoring components to keep molecules drug-like and synthetically feasible while optimising for potency.
