# Generic IC50 RL Campaigns — Comparison Table

## All Generic-Based Models (10k sampling)

| Metric | Generic-Prior | Old Generic-RL | Gen-RL Ext. | Gen-RL SuperExt | **Gen-RL Final** | Challenge V1 | **Challenge V2** |
|--------|:------------:|:--------------:|:-----------:|:---------------:|:----------------:|:------------:|:----------------:|
| **Steps from generic** | 0 | 300 | 1,300 | 2,300 | **5,300** | 1,500 | 2,000 |
| **Validity** | 97.3% | 95.6% | 48.0% | 29.0% | **17.9%** | 36.5% | **36.5%** |
| **Mean IC50 (µM)** | 13.71 | 8.04 | 2.12 | 0.74 | **0.67** | ? | **2.49** |
| **Median IC50 (µM)** | 13.34 | 6.91 | 2.08 | 0.72 | **0.67** | ? | 2.45 |
| **Min IC50 (µM)** | 4.02 | 1.97 | 1.05 | 0.56 | **0.49** | ? | 1.34 |
| **% < 0.5 µM** | 0% | 0% | 0% | 0% | **0.1%** | ? | 0% |
| **% < 1 µM** | 0% | 0% | 0% | 97.5% | **99.7%** | ? | 0% |
| **% < 2 µM** | 0% | 0.1% | 38.7% | 100% | **100%** | ? | 8.9% |
| **% < 5 µM** | 0.2% | 23.6% | 99.8% | 100% | **100%** | ? | 99.7% |

## Key Insights

1. **Generic-RL Final (3000 more steps from Super Extended)** achieved the best IC50 of any generic-based model: **mean 0.67 µM, min 0.49 µM, 99.7% below 1 µM**. This is the crown jewel of the generic line.

2. **Validity decreases as IC50 improves** — a clear tradeoff: 97% → 96% → 48% → 29% → 18%.

3. **More steps = better IC50** — but with diminishing returns after ~2000 total effective steps.

4. **Challenge V2** (fresh 2000 steps from generic prior) reached 2.49 µM — beat the old Generic-RL (8.04 µM) but couldn't match the step-accumulated advantage of Gen-RL Final (which had 5300 total effective steps).

5. **The best generic model still cannot match saponin TL + RL (1.65 µM with 37% validity from RL-E4-V3)** for combined validity+potency, but it proves the IC50 model can guide even a generic prior to produce molecules it scores as potent — they're just not triterpenoids.
