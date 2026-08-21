# M1.5 smoke test — results

<!-- Tables between GENERATED markers come from `python -m smoke_test.report`. -->

## Go / no-go

_(filled in once every run has completed — see the tables below)_

---

## What was actually run

<!-- GENERATED:oracle -->
<!-- /GENERATED:oracle -->

<!-- GENERATED:arms -->
<!-- /GENERATED:arms -->

<!-- GENERATED:margin -->
<!-- /GENERATED:margin -->

<!-- GENERATED:curve -->
<!-- /GENERATED:curve -->

---

## Deviations from the task spec, and why

Stated up front rather than buried, because each one changes how a number should be read.

**1. Bundle files were not present in the environment.** The session's working directory
was a different repository (`saponin-generator`); `README.md`, `research/`,
`stage3_fold_sequence_rl/` and the rest were supplied as uploads and read in the order
the prompt specifies, but there was no repo to build inside. `smoke_test/` was therefore
built standalone, keeping the interface names the prompt lists: `Game` /
`getInitBoard` / `getNextState` / `getValidMoves` / `getGameEnded` /
`stringRepresentation`, `player` pinned to 1, `getCanonicalForm` the identity, and
`getGameEnded` returning a continuous score in [-1, 1] with 0.0 reserved for
"not terminal". No existing stage-3 stub was modified — there were none on disk to
modify.

**2. The held-out set cannot reach 200 instances at n = 6 or n = 8.** The entire space of
M/V assignments is `2^(n-1)`, i.e. 32 and 128 patterns. Rather than pad with duplicates
or shrink the test set to carve out a training split, those two lengths use their
*complete* pattern space as the test set and contribute nothing to training. The net is
trained on n = 10 and n = 12 only, which makes n = 6 and n = 8 out-of-distribution
generalisation tests and keeps train/test disjointness true by construction. n = 10 and
n = 12 do have 200 held-out instances each, disjoint from 312 and 400 training patterns.

**3. "Mean folds vs the brute-force optimum" is degenerate in this action model.** Each
action folds exactly one previously-unfolded crease, and an instance is solved when all
n−1 creases are folded, so *every* solution has exactly n−1 folds. The brute-force
oracle confirms this rather than assuming it (`min folds` column above). The metric
carries no information here and the sequence-length half of the M2 exit criterion cannot
be tested in this domain. Node expansions per solve is reported in its place, and is what
P3 is judged on alongside solve rate.

**4. Kawasaki and Maekawa are not exercised at all.** A 1-D strip has no interior
vertices, so neither theorem has anything to apply to. The prompt's two-tier reward
therefore collapsed to a single tier in this domain: the "expensive global check" (layer
crossing) is the only check, and it happens to be cheap. This is the part of the parent
design that this smoke test does *not* test — see the last section.

**5. The stretch target (single-vertex 2-D patterns) was not attempted.** The 1-D
deliverable took the budget. Nothing about the 2-D case is claimed here.

---

## Design notes worth carrying forward

**The action space collapses to `(crease, side)`.** A flap can fold over the top or under
the bottom, and those give genuinely different stackings — but the crease's M/V label
plus the current face orientation of the two adjacent segments pins the choice uniquely.
Derivation in `strip.py`'s module docstring. So the discrete action is exactly
(which crease, which side moves), `2(n−1)` actions, which is what the prompt specified;
the over/under degree of freedom is not a free parameter, it is determined.

**The layer order is a total order over panels, and the fold history forces it.** A panel
is a maximal run of segments whose connecting creases are still unfolded; it is straight,
so all its segments share a height. A simple fold lifts the moving flap over (or under)
the *entire* stationary stack and reverses the flap's internal order, because a 180°
rotation about the crease reflects x and z together. Nothing is chosen arbitrarily, so
the total order is not an over-constraining linearisation — it is the physics.

**Orientation and direction are the same number.** Because a fold reflects x and z
together, a segment's face-up flag and its forward direction along the paper flip at
exactly the same moments. Both start at +1, so one field serves both, which is what lets
a crease be placed on the correct side of a cell without extra bookkeeping.

---

## What would break at 2-D scale

The honest read on which parts of this generalise to Origamizer-sized patterns (hundreds
of faces) and which are artefacts of the 1-D reduction.

**Artefacts — these do not survive.**

- **The exact legality check is cheap only because the layer order is total and forced.**
  This is the big one. In 1-D under simple folds, the moving flap goes entirely above or
  below the stationary stack, so a fold implies its stacking with zero search. In 2-D the
  faces overlap in a planar arrangement and the layer order is a *partial* order per
  overlap region, subject to the taco-taco / taco-tortilla / tortilla-tortilla
  constraints; deciding whether a consistent assignment exists is exactly where the
  NP-hardness of flat-foldability lives (Bern & Hayes 1996). The check that this smoke
  test leans on throughout is the one thing that will not port. `M1`'s named blocker —
  how the layer ordering is represented and updated incrementally — is *not* answered by
  this result; it is sidestepped by the reduction.
- **The two-tier reward was never exercised.** With no interior vertices there is no
  cheap local filter, so the whole design of "prune in-rollout with local theorems,
  rescore at terminal" went untested. At 2-D scale that split is load-bearing, and this
  experiment says nothing about whether it works.
- **Episode length is fixed at n−1.** Real patterns need variable-length episodes and a
  meaningful notion of a shorter route. The step-budget and shortest-route parts of the
  reward design are untested.
- **Every instance is solvable.** The oracle found no unsolvable pattern at any n. In 2-D
  many crease patterns are not simple-foldable, so solve rate acquires an unknown
  denominator and a low score stops being interpretable. Here 100% is a known ceiling;
  there it will not be.
- **The MLP.** Padding per-segment features to a fixed `MAX_N` does not scale to hundreds
  of faces, and a strip's crease graph is a path, so nothing in this result speaks to
  whether a GNN over a real crease graph learns anything. (A GNN was deliberately not
  used here — torch-geometric would have been a heavyweight dependency for a path graph.)

**Likely to survive.**

- **The single-player framing and the de-adversarialised `Coach`.** No sign flips, no
  player alternation, continuous terminal score with 0.0 reserved as the non-terminal
  sentinel. This worked without friction and nothing about it is 1-D-specific.
- **SP-MCTS's max-in-subtree term.** The goal is one good sequence, not robust average
  play, and the max term is what keeps a mostly-failing branch alive. That argument is
  domain-independent.
- **`stringRepresentation` must include the layer stack.** Two states with the same
  folded silhouette and different stacking are different states. This is more true in 2-D,
  not less — though canonicalising a 2-D layer order is itself non-trivial, which is a
  new problem the 1-D version does not have.
- **Search budget accounted in transition-function calls.** Making rollout steps and tree
  expansions cost the same is what makes the arms comparable; the same accounting works
  at any scale.

**One methodological trap worth recording.** The first version of the net arm used a pure
value-head leaf evaluation with no rollout, as AlphaZero proper does. It solved *nothing*
at these budgets: with a fold budget of a few dozen expansions the tree cannot reach the
depth n−1 where solutions live, whereas the uniform arm's rollouts reach terminal states
constantly and so find solutions almost incidentally. Comparing those two would have
measured the presence of rollouts, not the value of learning. Both arms therefore roll
out, and the net arm's advantage has to come from better priors and a better rollout
distribution. Anyone repeating this at larger scale should expect the same trap: at small
budgets, rollouts dominate, and an arm without them looks catastrophically bad for
reasons that have nothing to do with the network.
