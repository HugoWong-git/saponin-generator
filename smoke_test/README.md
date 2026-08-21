# smoke_test — origami fold-sequencing feasibility test (M1.5)

A go/no-go experiment, not a product. Answers one question:

> Does a learned policy + single-player MCTS find valid physical fold sequences at a
> materially higher rate than random search and than plain MCTS, on a domain where the
> layer-ordering constraint is real?

Findings and pass/fail against the criteria: [`RESULTS.md`](RESULTS.md).

## The domain

A 1×n strip of paper, n unit segments, n−1 creases each labelled mountain or valley
("simple folds / map folding in 1-D", cf. Arkin et al., *When Can You Fold a Map?*).
Geometry is trivial; **layer ordering is still the whole difficulty**, and it is exactly
checkable, so ground truth is obtainable by brute force.

## Layout

```
strip.py        environment: pure apply_fold, exact layer-crossing check, Game interface
verify.py       independent geometric checker (2-D segment intersection), for P1
brute_force.py  exhaustive reachable-state enumeration -- the solvability oracle
instances.py    fixed-seed train/test pools, disjoint by construction
sp_mcts.py      SP-MCTS (max-in-subtree + variance), with and without a net
net.py          padded per-segment MLP, policy + value heads
train.py        self-play loop, a-z-g Coach shape, de-adversarialised
evaluate.py     the experiment: 3 arms x 4 lengths x several seeds
plots.py        learning curve + solve-rate-by-n bar chart
tests/          pytest, including deliberately-broken cases that must be rejected
```

## Reproducing

Every number in `RESULTS.md` comes from one of these, with the seed printed beside it.

```bash
pip install numpy torch matplotlib pytest

python -m pytest smoke_test/tests -q            # P1: environment correctness
python -m smoke_test.brute_force --test-sets    # oracle over every test instance
python -m smoke_test.train --iterations 15 --episodes 80 --sims 25 --seed 7
python -m smoke_test.evaluate --budget 40 --seeds 1 2 3 4 5
python -m smoke_test.plots
```

Dependencies are numpy, torch (CPU) and matplotlib only. No GPU, no dataset downloads,
no external binaries.

## The two design points worth knowing

**The action space is `(crease, side)` and nothing else.** A flap can fold over the top
or under the bottom, and those are different states — but the crease's M/V label plus the
current face orientation of the pair pins that choice uniquely, so the freedom collapses.
Derivation in `strip.py`'s module docstring.

**The layer order is a total order over panels, and it is forced.** A simple fold lifts
the moving flap over (or under) the *entire* stationary stack, so the fold history
determines the stacking completely — nothing is chosen arbitrarily and nothing is
over-constrained. That is what makes the exact non-crossing check cheap here, and it is
also the property that does not survive to 2-D; see the last section of `RESULTS.md`.
