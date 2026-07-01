# Generic IC50 Challenge — Post-Mortem & Retry

## Failure Analysis: Attempt 1 (two-stage, arithmetic_mean)

**What happened:** The two-stage approach with arithmetic_mean and property constraints failed. Score started at 0.39 but dropped to 0.19 by step 500.

**Root cause:** With arithmetic_mean, 3 components (IC50=0.7 + MW=0.2 + Fsp3=0.1) meant:
- MW (300-1000 double_sigmoid) was trivially satisfied by the generic prior (MW ~350)
- Fsp3 sigmoid gave high scores for generic molecules
- The agent learned to maximize MW/Fsp3 while IC50 drifted

**Lesson learned:** Multi-objective with arithmetic_mean dilutes the IC50 signal. The successful Generic-RL runs all used **single-component geometric_mean**.

## Retry Strategy: Attempt 2

- Single component: IC50 only
- Geometric_mean (trivially reducible to identity with one component)
- Starting from the generic prior
- 2000 steps, sigma=128
- The SAME transform as the successful Generic-RL Extended run (which reached IC50 2.12 µM at 1000 steps and 0.74 µM at 2000 steps)

This is essentially the same approach as the proven Generic-RL Extended/Super Extended runs, but started fresh to independently verify reproducibility.

If this meets or beats the old Generic-RL baseline (mean IC50 8.0 µM), the challenge is won even without beating the 2000-step result (0.74 µM).