"""The 2-D experiment: three arms on held-out map-folding instances.

Arms, all on an identical per-shape fold budget:
  1. random legal-move rollout, restarted until the budget is spent
  2. SP-MCTS with uniform priors
  3. SP-MCTS with the trained policy/value net

Budget scales with the instance -- (m-1)+(n-1)+slack -- because minimum folds varies by
a factor of two across the shapes used. Expansions are counted in transition-function
calls for every arm, so a rollout step and a tree expansion cost the same thing and the
arms are directly comparable.

Held-out instances come from a seed disjoint from the training pool. One shape,
``10x10``, is absent from training entirely, so its row measures generalisation to an
unseen grid shape rather than to unseen instances of a known shape.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import time

from .grid import GridGame
from .instances import make_set
from .net import NetWrapper
from .train import budget_for
from smoke_test.sp_mcts import SPMCTS, random_arm

EVAL_SEED = 500_003  # disjoint from train.TRAIN_SEED and the curve seed
EVAL_SHAPES = [(6, 6), (8, 8), (6, 14), (10, 10)]
UNSEEN_SHAPES = {(10, 10)}  # not in train.TRAIN_SHAPES


def run_arm(arm: str, game: GridGame, budget: int, rng, net) -> tuple[bool, int]:
    state = game.getInitBoard()
    if arm == "random":
        return random_arm(game, state, budget, rng)
    mcts = SPMCTS(game, net=net if arm == "mcts+net" else None, rng=rng)
    solved = mcts.run(state, budget)
    return solved, mcts.expansions


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slack", type=int, default=4)
    ap.add_argument("--count", type=int, default=120)
    ap.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    ap.add_argument(
        "--checkpoint", default=os.path.join(os.path.dirname(__file__),
                                             "checkpoints", "final.pt")
    )
    ap.add_argument("--out", default="grid2d/results.json")
    args = ap.parse_args()

    net = NetWrapper()
    have_net = os.path.exists(args.checkpoint)
    if have_net:
        net.load(args.checkpoint)
    else:
        print(f"WARNING: {args.checkpoint} missing; skipping the trained arm")

    arms = ["random", "mcts"] + (["mcts+net"] if have_net else [])
    started = time.time()
    rows = []
    for m, n in EVAL_SHAPES:
        instances = make_set(m, n, args.count, seed=EVAL_SEED, family="derived")
        budget = budget_for(m, n, args.slack)
        for arm in arms:
            per_seed, spend, arm_started = [], [], time.time()
            for seed in args.seeds:
                rng = random.Random(seed * 7919 + m * 31 + n)
                solved, used = 0, []
                for hmv, vmv in instances:
                    ok, exp = run_arm(arm, GridGame(hmv, vmv), budget, rng, net)
                    solved += ok
                    if ok:
                        used.append(exp)
                per_seed.append(solved / len(instances))
                spend.append(sum(used) / max(1, len(used)))
            rows.append(
                {
                    "m": m,
                    "n": n,
                    "shape": f"{m}x{n}",
                    "unseen_shape": (m, n) in UNSEEN_SHAPES,
                    "arm": arm,
                    "budget": budget,
                    "n_instances": len(instances),
                    "seeds": args.seeds,
                    "solve_rate_mean": statistics.fmean(per_seed),
                    "solve_rate_sd": statistics.pstdev(per_seed),
                    "solve_rate_per_seed": per_seed,
                    "expansions_per_solve_mean": statistics.fmean(spend),
                    "expansions_per_solve_per_seed": spend,
                    "wall_clock_s": time.time() - arm_started,
                }
            )
            print(
                f"{m}x{n} {arm:9s} budget {budget:3d} solve "
                f"{rows[-1]['solve_rate_mean']:.3f} "
                f"+/- {rows[-1]['solve_rate_sd']:.3f}  "
                f"exp/solve {rows[-1]['expansions_per_solve_mean']:.1f}  "
                f"{rows[-1]['wall_clock_s']:.0f}s",
                flush=True,
            )

    with open(args.out, "w") as fh:
        json.dump(
            {
                "rows": rows,
                "eval_seed": EVAL_SEED,
                "slack": args.slack,
                "count": args.count,
                "wall_clock_s": round(time.time() - started, 1),
            },
            fh,
            indent=2,
        )
    print(f"total {time.time() - started:.0f}s -> {args.out}")


if __name__ == "__main__":
    main()
