# 2-D map folding — results

<!-- Tables between GENERATED markers come from `python -m grid2d.report --inject`. -->

## Go / no-go

**Deliberately not written.** This run was executed unattended with an explicit
instruction that milestone advancement is the reader's call, so no verdict is recorded
here and no conclusion is drawn about what the numbers reflect. The tables below are the
raw measurements; `../OVERNIGHT_LOG.md` lists what ran, what was fixed, and the open
questions.

Three things a reader should carry into the tables, all factual:

- **The trained arm does not separate from plain SP-MCTS.** Gaps are -0.007, +0.000,
  -0.002 and -0.078 across the four shapes. Only the 10x10 gap exceeds pooled seed noise,
  and it is negative. The trained arm did use fewer expansions per solve at every shape.
- **The untrained-weight control matches or exceeds the trained net at three of four
  shapes** (6x6, 8x8, 10x10). The trained net is ahead only at 6x14, by 0.031.
- **Search itself does separate from random at every shape**, by +0.077 to +0.217, all
  outside pooled seed noise.

Read the learning-curve table alongside the arms table with one caveat: the curve is
measured on 40 instances per shape, so a single point carries roughly +/-0.07 of
binomial noise, whereas the arms table uses 120 instances x 5 seeds.

**Status of the ground-truth table below: partial.** The oracle survey was still running
when this was written and its 6x14 and 10x10 rows, plus the entire `maekawa` family, are
absent. The rows present were recovered from the run's stdout log by
`grid2d/recover_oracle.py` and the JSON is flagged `partial: true`.

---

## Ground truth

<!-- GENERATED:oracle -->
**Instances derived from a real fold sequence** (seed 11, 165.5s):

| shape | instances | solvable | min folds | expected | mean states | max | complete |
|---|---|---|---|---|---|---|---|
| 6x6 | 120 | 120/120 (1.000) | 10 | 10 | 145 | 1173 | yes |
| 8x8 | 120 | 120/120 (1.000) | 14 | 14 | 618 | 5627 | yes |
<!-- /GENERATED:oracle -->

## Arms

<!-- GENERATED:arms -->
Budget is scaled per shape: (m-1)+(n-1)+4. 120 held-out instances per shape, seeds [1, 2, 3, 4, 5]. Solve rate is mean +/- SD across seeds.

| shape | budget | instances | arm | solve rate | per-seed | expansions / solve |
|---|---|---|---|---|---|---|
| 6x6 | 14 | 120 | random rollout | 0.868 +/- 0.018 | 0.867, 0.858, 0.842, 0.883, 0.892 | 10.1 |
| 6x6 | 14 | 120 | SP-MCTS (uniform) | 0.945 +/- 0.015 | 0.958, 0.950, 0.958, 0.917, 0.942 | 10.6 |
| 6x6 | 14 | 120 | SP-MCTS + trained net | 0.938 +/- 0.011 | 0.933, 0.958, 0.933, 0.925, 0.942 | 10.2 |
| 8x8 | 18 | 120 | random rollout | 0.738 +/- 0.030 | 0.742, 0.708, 0.767, 0.700, 0.775 | 14.1 |
| 8x8 | 18 | 120 | SP-MCTS (uniform) | 0.868 +/- 0.023 | 0.883, 0.850, 0.892, 0.833, 0.883 | 15.7 |
| 8x8 | 18 | 120 | SP-MCTS + trained net | 0.868 +/- 0.012 | 0.867, 0.858, 0.858, 0.892, 0.867 | 14.7 |
| 6x14 | 22 | 120 | random rollout | 0.603 +/- 0.029 | 0.592, 0.658, 0.575, 0.600, 0.592 | 18.1 |
| 6x14 | 22 | 120 | SP-MCTS (uniform) | 0.820 +/- 0.032 | 0.800, 0.867, 0.775, 0.817, 0.842 | 21.3 |
| 6x14 | 22 | 120 | SP-MCTS + trained net | 0.818 +/- 0.016 | 0.825, 0.833, 0.808, 0.792, 0.833 | 19.5 |
| 10x10 *(unseen shape)* | 22 | 120 | random rollout | 0.623 +/- 0.019 | 0.617, 0.658, 0.625, 0.608, 0.608 | 18.1 |
| 10x10 *(unseen shape)* | 22 | 120 | SP-MCTS (uniform) | 0.825 +/- 0.022 | 0.792, 0.825, 0.817, 0.833, 0.858 | 20.8 |
| 10x10 *(unseen shape)* | 22 | 120 | SP-MCTS + trained net | 0.747 +/- 0.008 | 0.742, 0.750, 0.733, 0.758, 0.750 | 19.6 |

Wall clock: 524.8s total.
<!-- /GENERATED:arms -->

### Margins against seed noise

<!-- GENERATED:margin -->
| shape | comparison | gap in solve rate | pooled SD | gap > SD? | expansions/solve |
|---|---|---|---|---|---|
| 6x6 | SP-MCTS (uniform) - random rollout | +0.077 | 0.024 | yes | 10.6 vs 10.1 |
| 6x6 | SP-MCTS + trained net - SP-MCTS (uniform) | -0.007 | 0.019 | no | 10.2 vs 10.6 |
| 8x8 | SP-MCTS (uniform) - random rollout | +0.130 | 0.038 | yes | 15.7 vs 14.1 |
| 8x8 | SP-MCTS + trained net - SP-MCTS (uniform) | +0.000 | 0.026 | no | 14.7 vs 15.7 |
| 6x14 | SP-MCTS (uniform) - random rollout | +0.217 | 0.043 | yes | 21.3 vs 18.1 |
| 6x14 | SP-MCTS + trained net - SP-MCTS (uniform) | -0.002 | 0.036 | no | 19.5 vs 21.3 |
| 10x10 | SP-MCTS (uniform) - random rollout | +0.202 | 0.029 | yes | 20.8 vs 18.1 |
| 10x10 | SP-MCTS + trained net - SP-MCTS (uniform) | -0.078 | 0.023 | no | 19.6 vs 20.8 |
<!-- /GENERATED:margin -->

### Control: is it the learning, or just the extra machinery?

<!-- GENERATED:control -->
| shape | SP-MCTS uniform | same net, random weights | trained net |
|---|---|---|---|
| 6x6 | 0.945 +/- 0.015 | 0.957 +/- 0.010 | 0.938 +/- 0.011 |
| 8x8 | 0.868 +/- 0.023 | 0.895 +/- 0.027 | 0.868 +/- 0.012 |
| 6x14 | 0.820 +/- 0.032 | 0.787 +/- 0.027 | 0.818 +/- 0.016 |
| 10x10 | 0.825 +/- 0.022 | 0.835 +/- 0.044 | 0.747 +/- 0.008 |
<!-- /GENERATED:control -->

## Learning curve

<!-- GENERATED:curve -->
Training args: `{'iterations': 12, 'episodes': 30, 'sims': 15, 'pool': 60, 'curve_per_shape': 40, 'curve_seed': 777001, 'seed': 7, 'window': 4}`.

| iteration | loss | self-play solve rate | held-out 6x14 | held-out 8x8 | seconds |
|---|---|---|---|---|---|
| 0 | - | - | 0.700 | 0.900 | 40 |
| 1 | 3.3467 | 0.967 | 0.650 | 0.850 | 221 |
| 2 | 2.9894 | 1.000 | 0.750 | 0.900 | 341 |
| 3 | 2.9123 | 1.000 | 0.725 | 0.950 | 480 |
| 4 | 1.4295 | 0.967 | 0.825 | 0.925 | 598 |
| 5 | 0.8724 | 0.967 | 0.675 | 0.900 | 719 |
| 6 | 0.6899 | 1.000 | 0.725 | 0.875 | 810 |
| 7 | 0.3207 | 1.000 | 0.725 | 0.900 | 897 |
| 8 | 0.3409 | 0.900 | 0.750 | 0.925 | 998 |
| 9 | 0.0760 | 0.967 | 0.725 | 0.900 | 1084 |
| 10 | 0.0384 | 0.967 | 0.675 | 0.850 | 1164 |
| 11 | 0.1004 | 1.000 | 0.725 | 0.825 | 1246 |
| 12 | 0.0374 | 0.967 | 0.725 | 0.850 | 1328 |
<!-- /GENERATED:curve -->
