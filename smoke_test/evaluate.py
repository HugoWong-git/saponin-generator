"""The experiment: three arms x four strip lengths, identical budget, several seeds.

Arms
  random   -- repeated uniform random legal rollouts from the root
  mcts     -- SP-MCTS, uniform priors, uniform rollouts
  mcts+net -- SP-MCTS, policy-head priors and policy-guided rollouts, value-head blend

The budget is counted in *expansions* -- one call to the transition function -- and is
identical for every arm, whether the expansion happens in the tree or inside a rollout.

Every number this prints comes with the seed that produced it; nothing is averaged
across seeds without also reporting the spread.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import time

from .instances import N_VALUES, instances
from .net import NetWrapper
from .sp_mcts import SPMCTS, random_arm
from .strip import StripGame

RESULTS_PATH = os.path.join(os.path.dirname(__file__), "results.json")


def run_arm(arm: str, mv: tuple[str, ...], budget: int, seed: int, net) -> tuple[bool, int]:
    """Returns (solved, expansions spent up to the solution or the whole budget)."""
    game = StripGame(mv)
    root = game.getInitBoard()
    rng = random.Random(seed)
    if arm == "random":
        solved, spent = random_arm(game, root, budget, rng)
        return solved, spent
    mcts = SPMCTS(game, net=net if arm == "mcts+net" else None, rng=rng)
    solved = mcts.run(root, budget)
    spent = mcts.expansions_at_solution if solved else mcts.expansions
    return solved, spent


def evaluate(budget: int, seeds: list[int], checkpoint: str | None, limit: int | None):
    net = None
    if checkpoint:
        net = NetWrapper()
        net.load(checkpoint)

    rows = []
    for n in N_VALUES:
        test = instances(n)[1]
        if limit:
            test = test[:limit]
        for arm in ("random", "mcts", "mcts+net"):
            if arm == "mcts+net" and net is None:
                continue
            per_seed_rate, per_seed_cost, wall = [], [], 0.0
            for seed in seeds:
                t0 = time.time()
                solved_flags, costs = [], []
                for i, mv in enumerate(test):
                    solved, spent = run_arm(arm, mv, budget, seed * 100_003 + i, net)
                    solved_flags.append(solved)
                    if solved:
                        costs.append(spent)
                wall += time.time() - t0
                per_seed_rate.append(sum(solved_flags) / len(test))
                per_seed_cost.append(statistics.mean(costs) if costs else float("nan"))
            rows.append(
                {
                    "n": n,
                    "arm": arm,
                    "budget": budget,
                    "n_instances": len(test),
                    "seeds": seeds,
                    "solve_rate_per_seed": per_seed_rate,
                    "solve_rate_mean": statistics.mean(per_seed_rate),
                    "solve_rate_sd": (
                        statistics.stdev(per_seed_rate) if len(seeds) > 1 else 0.0
                    ),
                    "expansions_per_solve_per_seed": per_seed_cost,
                    "expansions_per_solve_mean": statistics.mean(per_seed_cost),
                    "wall_clock_s": wall,
                }
            )
            print(
                f"n={n:2d} {arm:9s} solve {rows[-1]['solve_rate_mean']:.3f}"
                f" +/- {rows[-1]['solve_rate_sd']:.3f}"
                f"  exp/solve {rows[-1]['expansions_per_solve_mean']:.1f}"
                f"  {wall:.0f}s"
            )
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--budget", type=int, default=40)
    parser.add_argument("--seeds", type=int, nargs="+", default=[1, 2, 3, 4, 5])
    parser.add_argument(
        "--checkpoint",
        default=os.path.join(os.path.dirname(__file__), "checkpoints", "final.pt"),
    )
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--out", default=RESULTS_PATH)
    args = parser.parse_args()

    checkpoint = args.checkpoint if os.path.exists(args.checkpoint) else None
    if checkpoint is None:
        print(f"WARNING: no checkpoint at {args.checkpoint}; skipping the mcts+net arm")

    t0 = time.time()
    rows = evaluate(args.budget, args.seeds, checkpoint, args.limit)
    payload = {
        "args": vars(args),
        "checkpoint_used": checkpoint,
        "wall_clock_s": time.time() - t0,
        "rows": rows,
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"total {time.time() - t0:.0f}s -> {args.out}")


if __name__ == "__main__":
    main()
