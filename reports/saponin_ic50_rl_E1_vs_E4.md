# E1-RL vs E4-RL — IC50‑Guided Reinforcement Learning Comparison

## Overview

Two REINVENT4 DAP RL campaigns were run with identical hyperparameters (DAP, sigma=128, rate=0.0001, batch_size=64, 500 steps, reverse_sigmoid transform high=3/low=-1/k=0.5). The **only difference** was the starting prior:

| Run | Starting Prior | TL Epochs |
|-----|---------------|-----------|
| **E1 RL** | `saponin_prior_46k_reg_epoch1.prior` | 1 epoch (4 blocks) |
| **E4 RL** | `saponin_prior_46k_reg_epoch4.prior` | 4 epochs (16 blocks) |

The IC50 consensus model (10-model ensemble on Morgan fingerprints) was the sole scoring component.

## RL Training Progress

| Metric | E1 RL | E4 RL |
|--------|-------|-------|
| Initial score | 0.02 | 0.02 |
| Final score | **0.77** | **0.78** |
| Final NLL | **13.84** | 11.62 |
| Steps | 500 | 500 |
| Peak memory | — | 1598 MiB |

Both agents converged to similar final scores (~0.77-0.78), indicating comparable IC50 optimisation.

## 10k Sampling Comparison

| Metric | E1 TL Prior | E4 TL Prior | **E1 RL Agent** | **E4 RL Agent** |
|--------|:-----------:|:-----------:|:---------------:|:---------------:|
| **Validity** | 0.8595 | 0.8618 | **0.4973** | 0.3722 |
| **Unique valid** | 8,595 | 8,618 | **4,973** | 3,722 |
| **Novelty** | 99.90% | 99.78% | 100% | 100% |
| **Mean IC50 (µM)** | 13.80 | 13.84 | 1.87 | **1.65** |
| **Median IC50 (µM)** | 13.14 | 13.08 | 1.72 | **1.55** |
| **Min IC50 (µM)** | 2.76 | 2.33 | 0.86 | **0.90** |
| **% IC50 < 2 µM** | 0.0% | 0.0% | 81.6% | **83.6%** |
| **% IC50 < 5 µM** | 1.1% | 1.5% | 99.0% | **99.9%** |

Both RL agents achieve a **~7–8× improvement in mean IC50** over their starting priors. E4 RL has marginally better IC50 stats but **E1 RL has significantly better validity (49.7% vs 37.2%)** and generates **33% more valid unique molecules**.

## NPClassifier Comparison (100 molecules each)

| Level | E1 TL Prior | E4 TL Prior | E1 RL Agent | E4 RL Agent |
|-------|:-----------:|:-----------:|:-----------:|:-----------:|
| **Triterpenoids** | 83.0% | 83.0% | 98.0% | **100%** |
| **Lanostane** | 20.5% | 15.8% | **96.9%** | 79.8% |
| **Oleanane** | 23.4% | 19.3% | — | — |
| **Dammarane** | 5.8% | 14.0% | 1.0% | 15.1% |
| **Cycloartane** | — | 10.5% | 1.0% | 5.0% |
| **Terpenoids (pathway)** | 96.5% | 98.0% | **100%** | **100%** |

### Key finding from NPClassifier

**E1 RL converged more narrowly** — 96.9% of molecules are Lanostane triterpenoids (almost all one class). **E4 RL is structurally more diverse** — 79.8% Lanostane + 15.1% Dammarane + 5.0% Cycloartane.

This is the opposite of what one might expect: starting from a less-trained prior (E1) led to **more focused** optimisation, while starting from a more-trained prior (E4) led to **more diverse** exploration. This suggests E4's broader TL training gave the model a wider landscape of triterpenoid chemistry to explore during RL.

## Descriptor Comparison

| Descriptor | E1 TL | E4 TL | E1 RL | E4 RL |
|-----------|:-----:|:-----:|:-----:|:-----:|
| **MolWt** | 549 | 551 | 743 | 828 |
| **LogP** | 5.36 | 5.46 | 3.55 | 3.71 |
| **TPSA** | 106 | 104 | 194 | 211 |
| **Rings** | 5.0 | 5.0 | 5.9 | 6.0 |
| **Fsp3** | 0.82 | 0.84 | 0.93 | 0.94 |

Both RL agents move toward heavier, more polar, more saturated molecules — consistent with glycosylated triterpenoids. E1 RL generates somewhat **lighter molecules** (MW 743 vs 828) — reflecting its less-trained starting point.

## Conclusions

| Aspect | E1 RL | E4 RL |
|--------|-------|-------|
| **IC50 improvement** | 7.4× | **8.4×** |
| **Validity** | **49.7%** | 37.2% |
| **Structural diversity** | Narrow (97% Lanostane) | **Broader** (80% Lanostane + diverse) |
| **Mol diversity (unique)** | **4,973** | 3,722 |
| **Stability** | **Higher validity, more samples** | Lower validity |

**Recommendation:** E1 RL is preferred if you want a **more robust, higher-validity agent** that still achieves excellent IC50 improvement. E4 RL is preferred if you value **broader triterpenoid subclass diversity** and marginally better IC50 numbers. The TL depth (E1 vs E4) affects **diversity and validity** more than it affects IC50 optimisation — both converge to similar potency.
