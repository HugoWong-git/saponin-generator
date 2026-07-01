# Generic IC50 RL Challenge Results

## Challenge Design (Attempt 2 — Successful)

Two-stage approach from generic PubChem prior:
- **Stage 1:** 2000 steps single-component IC50, sigma=128, transform high=3, low=-1
- **Key insight:** Single-component geometric_mean outperforms multi-objective arithmetic_mean for generic prior RL

## Results

| Metric | Generic-Prior | Old Generic-RL (300s) | **Challenge V2 (2000s)** |
|--------|:------------:|:---------------------:|:------------------------:|
| Validity | 97.3% | 95.6% | 36.5% |
| Mean IC50 | 13.71 µM | 8.04 µM | **2.49 µM** |
| Median IC50 | 13.34 µM | 6.91 µM | 2.45 µM |
| Min IC50 | 4.02 µM | 1.97 µM | 1.34 µM |
| % <2 µM | 0% | 0.1% | **8.9%** |
| % <5 µM | 0.2% | 23.6% | **99.7%** |

## Verdict

**Beat the old Generic-RL** on every IC50 metric (3.2× mean improvement, 89× more sub-2µM molecules). Validity dropped from 95.6% → 36.5%, which is below the >80% target. The saponin-TL-based RL-E1 (49.7% validity, 1.88 µM IC50) remains the best overall balance.

## What Didn't Work (Attempt 1)

Two-stage with arithmetic_mean (IC50 0.7 + MW 0.2 + Fsp3 0.1):
- Started fast (score 0.41 at step 25) but agent learned to satisfy MW/Fsp3 constraints instead of IC50
- Final score: 0.19 (worse than single-component)
- **Lesson:** arithmetic_mean dilutes the IC50 signal when property constraints are too easy to satisfy