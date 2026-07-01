# E1 vs E4 RL Comparison

Two REINVENT4 DAP campaigns run with identical hyperparameters (sigma=128, rate=0.0001, 500 steps, reverse_sigmoid high=3/low=-1/k=0.5). Only difference: starting prior.

## Quick Reference Table

| Metric | RL-E1 | RL-E4-V3 | Difference |
|--------|-------|----------|------------|
| Start prior | Epoch 1 TL | Epoch 4 TL | — |
| Final score | 0.77 | 0.78 | negligible |
| Validity | **49.7%** | 37.2% | E1 wins (+12ppt) |
| Unique valid (10k) | **4,973** | 3,722 | E1: 33% more |
| Mean IC50 | 1.88 µM | **1.65 µM** | E4 wins (−0.23µM) |
| % <2 µM | 81.2% | **84.0%** | E4 wins |
| Triterpenoids | 98% | **100%** | similar |
| **Lanostane** | **96.9%** | 79.8% | E1 narrower |
| Dammarane | 1.0% | **15.1%** | E4 diverse |
| Cycloartane | 1.0% | **5.0%** | E4 diverse |
| MW | 815 | 829 | similar |
| TPSA | 196 | 211 | E1 less polar |
| Fsp3 | 0.88 | **0.94** | E4 more saturated |

## Recommendation

**RL-E1 is the best balance** for generating molecules for experimental follow-up:
- Higher validity → more candidates per sampling round
- Slightly worse IC50 but still 81% below 2 µM
- Narrower subclass (Lanostane) means more focused SAR

**RL-E4-V3** when subclass diversity is needed:
- Samples Dammarane and Cycloartane scaffolds
- Better absolute IC50
- Use for exploring non-Lanostane triterpenoid space

## Files

- Checkpoint: `models/saponin_ic50_rl_epoch1.chkpt`, `models/saponin_ic50_rl_epoch4_v3.chkpt`
- Configs: `configs/rl_saponin_ic50_epoch1.toml`, `configs/rl_saponin_ic50_epoch4_v3.toml`
- 10k samples: `samples/rl_epoch1_10k.csv`, `samples/rl_v3_final_10k.csv`
- Full report: `reports/saponin_ic50_rl_E1_vs_E4.md`