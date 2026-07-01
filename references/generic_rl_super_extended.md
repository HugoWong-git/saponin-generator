# Generic RL Super-Extended — Limits of Extrapolation

## Run Summary

Started from the Generic-RL Extended checkpoint (1300 steps, mean IC50 2.12 µM, min 1.05 µM) and continued for another 1356+ steps (3000 total from PubChem prior, 5656 total across all generic runs).

## Config

- **File:** `configs/rl_ic50_generic_final.toml`
- **Initial attempt:** sigma=512 — too aggressive, oscillated at 0.53-0.68 for 600 steps → KILLED
- **Restarted with:** sigma=256 — stable convergence starting from score 0.65

## Score Trajectory (sigma=256 version)

| Step | Score | IC50 (approx) |
|------|-------|---------------|
| 1    | 0.65  | ~0.55 µM |
| 196  | 0.68  | ~0.50 µM |
| 509  | **0.73** | ~0.40 µM |
| 851  | 0.70  | ~0.45 µM |
| 968  | 0.72  | ~0.42 µM |
| 1392 | **0.74** | ~0.38 µM  (new peak) |
| 1919 | 0.68  | ~0.50 µM |
| ~2700 | 0.68  | ~0.50 µM |

## Key Finding

Even after **5656 total DAP steps** from the PubChem prior, and after trying **every combination** of:
- Sigma: 128, 256, 512
- Transforms: mild (high=3, low=-1) through extreme (high=2.3, low=-2.3)
- Steps: 300, 1000, 2000, 3000

...the **absolute minimum IC50 achieved is ~0.38 µM (score 0.74)**. The IC50 model has zero training data below ~0.9 µM. All predictions below that are blind ML extrapolation. The model cannot differentiate molecules at this range because the Morgan fingerprints for "0.4 µM" vs "0.1 µM" were never learned.

**Verdict: The IC50 model cannot predict 0.1 µM — period.** This is a fundamental data limitation, not a training or hyperparameter issue. The A2780 training dataset (331 compounds) simply does not contain any compound with IC50 < 0.9 µM.
