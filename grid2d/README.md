# grid2d — 2-D map folding

The next rung after `smoke_test/`, which validated the search machinery on a 1-D strip
but explicitly did not touch the parent project's named blocker: how a layer ordering is
represented and updated by a fold in 2-D.

**Status: environment complete and validated; the learning experiment is built but has
not been run.** Everything below the "Findings" heading is measured. The three-arm
comparison at full scale, the training run, and a RESULTS.md are not done.

## Why a grid, and not a single vertex

The obvious next rung is a single interior vertex. It is the wrong rung, for two reasons
that only became clear once the geometry was worked through:

1. **Layer order does not independently obstruct there.** All sectors around one vertex
   meet *at* the vertex, so they all overlap and the stacking is still a total order.
   Worse, single-vertex flat-foldability is fully characterised by local conditions
   (Kawasaki + Maekawa + big-little-big): given a valid M/V assignment, a consistent
   layer ordering is *guaranteed* to exist. The thing being tested cannot fail.
2. **Simple folds are not well-defined on it.** A single vertex sits in the interior of
   a disc, so folding one crease to ±180° forces the paper to deform elsewhere. There is
   no "flip one side" action of the kind the 1-D environment uses.

A grid has neither problem. It is genuinely 2-D, simple folds are well-defined, and it
generalises the validated 1-D code — a 1×n grid *is* the strip, which turns out to be
the strongest correctness check available.

## The model

`m × n` unit cells; `m−1` horizontal and `n−1` vertical crease lines; all-layers simple
folds (pick a line and a side, that side flips as one rigid block carrying its layers).

Geometry stays 1-D per axis — x depends only on the column, y only on the row. **What
couples them is the layer order**, which both axes share. A vertical fold's legality
depends on ranks that horizontal folds produced. That coupling is the 2-D content,
isolated from everything else.

Assignments live on crease *segments*, not lines. This is forced, not a choice: a grid's
interior vertex has four 90° sectors, so Kawasaki is automatic, but Maekawa needs
|M − V| = 2. A uniform label per line would make every vertex see two copies of two
labels, giving |M − V| ∈ {0, 4} — no grid would ever be foldable. Real maps fold, so
labels must vary along a line.

**The interesting constraint.** An all-layers fold is one rigid rotation, so there is a
single global over/under bit, and each row's segment realises a label determined by that
bit and that row's face orientation. The fold is only available when every segment agrees
on the same bit. Since row orientations flip as horizontal folds happen, *which vertical
folds are available changes as horizontal folds are made*. Order matters, in a way it
never did in 1-D.

## Findings so far

**The environment is correct where it can be checked against something independent.**
A 1×n grid reproduces `smoke_test/strip.py` exactly on **64,618 reachable states**
(n = 2..8, all M/V patterns), and an m×1 grid does the same on the transposed axis,
exercising the horizontal code path. Two implementations written months apart in
different shapes, walked in lockstep, never diverging on geometry, ranks, or legality.

**Local theorems are demonstrably not sufficient — in this domain, unlike the last one.**
Grids satisfying Maekawa at every interior vertex exist that admit no legal fold sequence
at all (37/40 solvable at 3×3 and 2×4; 9/30 at 4×4). The 1-D domain could never show this
— every instance there was solvable. This is the parent project's headline claim
demonstrated on instances this code generates and this oracle judges.

**Every instance derived from a real fold sequence satisfies Maekawa automatically**,
which is the converse direction and a good consistency check on the model.

**All-layers folding is search-easy at a generous budget.** At budget 40 random rollout
solves ~100% of solvable instances up to 6×6; state spaces are small (mean 13–268 nodes).
The domain only has search difficulty at a *scaled* budget, (m−1)+(n−1)+4, where random
drops to 0.45–0.70. Any experiment here must scale the budget with the instance; a fixed
number would be measuring the wrong thing.

**Search helps, at that scaled budget** (3 seeds, 60 instances/shape):

| shape | random | SP-MCTS |
|---|---|---|
| 6×6 | 0.86 | 0.96 |
| 8×8 | 0.75 | 0.89 |
| 6×14 | 0.59 | 0.74 |

Unlike 1-D, the margin holds at *every* size — there is no ceiling effect, because even
the smallest grid here is not saturated at a scaled budget.

## What is built but not run

`net.py`, `train.py`, `evaluate.py` and `brute_force.py` are complete and smoke-tested
end to end (1 training iteration, a 15-instance evaluation). Not yet run at full scale:
the multi-iteration training run, the three-arm × four-shape × five-seed evaluation, the
untrained-net control, plots, or a RESULTS.md. No numbers from those exist, and none are
claimed.

```bash
python -m pytest grid2d/tests -q
python -m grid2d.brute_force --shapes 6x6,8x8,6x14 --count 200
python -m grid2d.train --iterations 12 --episodes 30 --sims 15
python -m grid2d.evaluate --count 120 --seeds 1 2 3 4 5
```

## Known limitations

- **Kawasaki is never exercised.** A grid's 90° sectors satisfy it identically, so only
  half the tier-1 reward is live. A domain with irregular sector angles would be needed.
- **All-layers folds only.** Some-layers folds (fold a subset of the stack) are the
  physically richer model and where map folding gets genuinely hard; they would also
  break the per-axis geometry simplification this module leans on.
- **Not a GNN.** Same reasoning as 1-D: a grid's crease graph is a regular lattice.
  This says nothing about whether a GNN helps on an Origamizer-sized irregular graph.
- **Layer order is still a total order.** Panels share a rank, so the taco-taco and
  taco-tortilla constraints appear, but tortilla-tortilla is trivially satisfied. The
  full partial-order-per-overlap-region problem needs non-simple folds.

`smoke_test/sp_mcts.py` is shared, not forked — it was made generic over the Game
interface so 1-D and 2-D run the same search. The 1-D results were re-run after that
refactor and are identical on every solve rate, per-seed value and expansion count.
