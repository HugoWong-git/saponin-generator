"""Direct test of whether Candidate 3's signal was learned, independent of solve rate.

Solve rate cannot distinguish "learned to solve" from "learned to solve *well-ordered*"
-- the canonical-order penalty only discriminates among solved sequences, so it can be
invisible in a solve-rate comparison even if the policy internalised it perfectly, and
equally invisible if it learned nothing at all. This measures the one quantity the
diagnostic actually targets: the mean canonical-order penalty of sequences the trained
policy produces, against the same measurement for the untrained network.
"""

from __future__ import annotations

import argparse
import json
import random

from .grid import GridGame
from .instances import make_set
from .net import NetWrapper
from .train import budget_for, canonical_order_penalty
from smoke_test.sp_mcts import SPMCTS

EVAL_SEED = 500_003  # matches evaluate.py, so instances are the same held-out set


def policy_sequence(game: GridGame, net: NetWrapper, budget: int, rng) -> list[int] | None:
    """Drive the policy greedily via SP-MCTS; return the realised fold sequence."""
    state = game.getInitBoard()
    sequence: list[int] = []
    while not state.is_solved:
        valid = [a for a, v in enumerate(game.getValidMoves(state)) if v]
        if not valid:
            return None
        mcts = SPMCTS(game, net=net, rng=rng)
        for _ in range(budget):
            mcts.search(state)
        pi = mcts.policy(state, temperature=0.0)
        action = max(valid, key=lambda a: pi[a])
        sequence.append(action)
        state = game.getNextState(state, 1, action)[0]
    return sequence


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shape", default="6x14")
    ap.add_argument("--count", type=int, default=60)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--checkpoint", required=True)
    ap.add_argument("--label", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    m, n = (int(x) for x in args.shape.lower().split("x"))
    budget = budget_for(m, n)
    net = NetWrapper()
    net.load(args.checkpoint)
    rng = random.Random(args.seed)

    instances = make_set(m, n, args.count, seed=EVAL_SEED, family="derived")
    penalties, solved = [], 0
    for hmv, vmv in instances:
        game = GridGame(hmv, vmv)
        seq = policy_sequence(game, net, budget, rng)
        if seq is not None:
            solved += 1
            penalties.append(canonical_order_penalty(seq, m, n))

    mean_penalty = sum(penalties) / len(penalties) if penalties else None
    result = {
        "label": args.label,
        "checkpoint": args.checkpoint,
        "shape": args.shape,
        "instances": len(instances),
        "solved": solved,
        "mean_canonical_penalty": mean_penalty,
        "penalties": penalties,
    }
    print(f"{args.label}: solved {solved}/{len(instances)}, "
          f"mean canonical-order penalty = {mean_penalty}")
    if args.out:
        with open(args.out, "w") as fh:
            json.dump(result, fh, indent=2)


if __name__ == "__main__":
    main()
