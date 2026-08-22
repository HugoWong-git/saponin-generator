# 2-D map folding — results

<!-- Tables between GENERATED markers come from `python -m grid2d.report --inject`. -->

## Go / no-go

**Deliberately not written.** Milestone advancement is the reader's call throughout this
investigation, so no verdict is recorded here. What follows is a factual account of
what was tried and what each test found; `../OVERNIGHT_LOG.md` covers the unattended
overnight run specifically (guardrails, what was fixed, citation checks).

**Status as of the end of this investigation: four hypotheses tested, three ruled out,
one not confirmed by the specific fix tried.** See "Follow-up investigation" below for
the full account. The trained network has not been shown to outperform plain SP-MCTS at
any tested 2-D shape, across every variant of reward, compute, and search-exploration
tried. Two paths remain open and untested: a much larger-scale self-play run (every run
here used <=1,200 self-play games total, versus real AlphaZero's tens of millions — see
the "scale" note in Follow-up investigation), or redesigning the domain itself so
Kawasaki's theorem is a live constraint rather than trivially satisfied on a rectangular
grid. Neither has been attempted.

### Original overnight run — the raw measurements

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

**Status of the ground-truth table below: the `derived` half is partial.** Its oracle run
hit a 5400s wall-clock cap while still working through 6x14, so the **6x14 and 10x10 rows
were never obtained** — 6x6 and 8x8 are complete and were recovered from the run's stdout
by `grid2d/recover_oracle.py` (`partial: true` in the JSON). The `maekawa` half is
complete: it never started before the cap, and was re-run afterwards at its original
parameters, taking 15s.

Those two missing rows were **not** retried at a reduced instance count. 6x14 alone
consumed ~5250s without finishing 120 instances, so a retry at the same protocol would
fail the same way, and changing the instance count mid-table would make the rows
non-comparable. Whether to obtain them at a smaller count is left open.

The `maekawa` rows are worth reading directly: **every one of these instances satisfies
Maekawa's theorem at every interior vertex, and most of the larger ones are still
globally unfoldable** — 139/200 at 4x4 and 174/200 at 4x5. The local theorems are
necessary and not sufficient, measured rather than cited. Note also that the whole 2x4
pattern space is only 128 Maekawa-valid instances, which is why that row has 128 and not
200.

---

## Ground truth

<!-- GENERATED:oracle -->
**Instances derived from a real fold sequence** (seed 11, 165.5s):

| shape | instances | solvable | min folds | expected | mean states | max | complete |
|---|---|---|---|---|---|---|---|
| 6x6 | 120 | 120/120 (1.000) | 10 | 10 | 145 | 1173 | yes |
| 8x8 | 120 | 120/120 (1.000) | 14 | 14 | 618 | 5627 | yes |

**Instances that satisfy Maekawa at every interior vertex** (seed 11, 15.4s):

| shape | instances | solvable | min folds | expected | mean states | max | complete |
|---|---|---|---|---|---|---|---|
| 3x3 | 200 | 176/200 (0.880) | 4 | 4 | 12 | 25 | yes |
| 2x4 | 128 | 112/128 (0.875) | 4 | 4 | 15 | 31 | yes |
| 4x4 | 200 | 61/200 (0.305) | 6 | 6 | 11 | 67 | yes |
| 4x5 | 200 | 26/200 (0.130) | 7 | 7 | 8 | 55 | yes |
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

---

## Follow-up investigation: why doesn't 2-D training work?

The overnight run above established that the trained net doesn't separate from plain
SP-MCTS. Everything below is the systematic, hypothesis-by-hypothesis follow-up, run
afterwards. Tables regenerated verbatim by `python -m grid2d.consolidate_investigation`
from the run JSON — nothing here is typed by hand.

<!-- CONSOLIDATED:hypotheses -->
| hypothesis | test | key result | verdict |
|---|---|---|---|
| 1. Opponent-pool sampling | Compared 1-D's and 2-D's self-play code (both use one live network, no checkpoint pool) | Identical scheme in both; 1-D still learned | **Ruled out** -- not the differentiator |
| 2. Compute/data starvation | Matched 1-D's per-iteration compute (80 episodes, 25 sims) at 6x6 and 6x14 | 6x6: trained 0.945 vs uniform 0.945 vs untrained 0.957. 6x14: trained 0.817 vs uniform 0.820 vs untrained 0.787 | **Ruled out** -- no separation at either shape, including 6x14 where real headroom exists |
| 3. Reward degeneracy (flat reward across ~200k equally-valid orderings) | Candidate-3 diagnostic: canonical-order penalty, lambda=0.1 and lambda=0.5, direct inversion-count measurement | Ordering penalty: untrained 0.4792, lambda=0.1 0.4915, lambda=0.5 0.5114 (all statistically indistinguishable from 0.5 = random ordering) | **Ruled out** -- zero learning of the injected signal at 5x the strength; solve rate moved (lambda=0.5 vs untrained: +0.068 (pooled SD 0.034, beats noise)) with no corresponding ordering improvement |
| 4. Rollout-policy sharpening / search collapse | Epsilon-mixing exploration floor (eps=0.25) on self-play rollout sampling only | Saturation timing unchanged (iter 5 of 6, range 0.963-1.000 -- see table above); solve rate vs untrained: +0.048 (pooled SD 0.032, beats noise); vs uniform: +0.015 (pooled SD 0.037, within noise) | **Not confirmed by this fix.** Correlational evidence (Track C) still stands; this specific eps=0.25 mitigation didn't change the saturation pattern it targeted |
<!-- /CONSOLIDATED:hypotheses -->

### Self-play saturation timing — the evidence behind hypothesis 4

Every learning run's self-play solve rate, iteration by iteration. The question this
answers: does self-play settle into a narrow, saturated pattern quickly (as every 2-D
run does), or climb slowly with sustained oscillation before saturating (as the one
successful 1-D run did)?

<!-- CONSOLIDATED:saturation -->
| run | self-play range | first hits 1.000 |
|---|---|---|
| 1-D (15 iter) -- the one that learned | 0.762-1.000 | iter 11 of 15 |
| 2-D original (12 iter, 3 shapes) | 0.900-1.000 | iter 2 of 12 |
| Track A: compute-matched, 6x6 | 0.963-1.000 | iter 3 of 6 |
| Track A2: compute-matched, 6x14 | 0.963-1.000 | iter 2 of 6 |
| Candidate 3, lambda=0.1, 6x14 | 0.950-1.000 | iter 5 of 6 |
| Candidate 3, lambda=0.5, 6x14 | 0.925-1.000 | iter 4 of 6 |
| Hypothesis-2 rollout eps=0.25, 6x14 | 0.963-1.000 | iter 5 of 6 |
<!-- /CONSOLIDATED:saturation -->

Every 2-D variant reaches full saturation by iteration 2-5 of a 6-12 iteration run and
stays there; 1-D spent ten iterations oscillating in a 0.76-0.94 band before first
reaching 1.000 at iteration 11 of 15. The rollout-exploration fix (hypothesis 4) did not
change this pattern — it remains the one plausible mechanism nobody has yet found a
working fix for, not a ruled-out explanation.

### The scale question, left genuinely open

Every 2-D training run in this investigation used at most 480 total self-play games (6
iterations x 80 episodes); the 1-D run that worked used 1,200. Real AlphaZero used tens
of millions; even the toy `alpha-zero-general` reference implementation this project is
modeled on recommends defaults around 100,000 games for a simpler board game (Othello).
"Matching 1-D's budget" was never a test of whether 2-D has *enough* self-play in any
absolute sense — only whether the *ratio* to 1-D mattered. It doesn't rule out that this
domain, or this network size, simply needs an order of magnitude more self-play than
anything tried here. Not attempted in this investigation; flagged as the cheaper of the
two open forks (the other being a domain redesign so Kawasaki's theorem is a live
constraint rather than trivially satisfied on a rectangular grid).

### What was deliberately not done

No large-scale self-play run (held back per explicit direction — this session is
CPU-only regardless, so the decision costs nothing here but stands for future sessions
with GPU access). No hypothesis 4 follow-up at a stronger epsilon or a different
exploration mechanism. Both are legitimate next steps; neither has been started.

### Domain redesign: scoped, not built — why it's bigger than it first looked

The domain flaw is real: a rectangular grid's interior vertices are always four 90°
sectors, so Kawasaki's alternating-sum condition is satisfied identically everywhere,
for every instance, regardless of M/V assignment. It has never been a live constraint
in any run in this investigation. Fixing that looked at first like a parameter change
(vary the sector angles); it isn't, and it's worth recording precisely why, so this
doesn't have to be re-derived.

**A uniform skewed/rhombic grid cannot work.** At any 4-way line crossing, opposite
angles are equal and adjacent ones sum to 180°, so Kawasaki's alternating sum reduces
algebraically to exactly `4*theta - 360` for crossing angle `theta`. That is zero only
at `theta = 90`, i.e. the existing trivial case — every other single skew angle is
flat-*unfoldable* everywhere, not sometimes-foldable. A single global angle parameter
cannot produce a family with some Kawasaki-passing and some Kawasaki-failing instances,
which is what a useful generator needs.

**Genuine per-vertex angle variation requires abandoning straight grid lines
entirely.** `grid2d`'s row/column model works by keeping every vertical (or
horizontal) crease as one straight line spanning the whole grid — that's what lets
folds be expressed as simple integer row/column reflections instead of real geometry.
Independent per-vertex sector angles break that straightness constraint: creases would
need to bend at each vertex they pass through, which means real 2-D vector geometry
(vertex coordinates, angles from vectors, a genuine segment-intersection crossing
check) rather than the integer-coordinate trick this whole codebase has relied on so
far.

**That is a new geometry kernel, not an extension of the existing one** — comparable
in scope to `grid2d` itself, not a small addition to it, and with real correctness
risk: the standard literature on validating such constructions is on arXiv, which this
session's network policy blocks outright, removing the usual way to cross-check the
approach against established results before trusting it.

**Decision:** given the revised scope, this was not started this session. Whoever
picks it up next has the math above as a starting point, and should expect to build
and validate a small rigid-flat-vertex geometry engine — ideally cross-checked against
a known-correct simpler case the way `grid2d`'s row/column model was checked against
`smoke_test`'s 1-D strip — before trusting any results built on top of it.
