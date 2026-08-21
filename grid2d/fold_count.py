"""Fold-count fidelity: does the trained policy find a *minimum*-fold solution?

The question this answers, per instance:

  * what is the oracle's minimum fold count (exhaustive search)?
  * what fold count does the trained policy's own sequence realise?
  * do they match?

It also reports how many *distinct* complete fold sequences each instance admits,
because that decides whether fold count can discriminate between solutions at all.

Read the output as a measurement, not a verdict. This script states what the numbers
are; whether they mean the metric is useful for this project is a judgement left to
the reader.
"""

from __future__ import annotations

import argparse
import json
import random

from .grid import GridGame, apply_fold, decode, legal_actions
from .instances import make_set
from .net import NetWrapper
from .train import budget_for
from smoke_test.sp_mcts import SPMCTS

EVAL_SEED = 500_003  # must match evaluate.py so the instances are the same held-out set


def oracle_solutions(game: GridGame) -> tuple[int | None, int]:
    """Exhaustive search. Returns (minimum fold count, number of distinct sequences).

    Sequences are counted as distinct action paths from the root, so two orders that
    reach the same folded state by different routes count separately -- that is the
    quantity that decides whether the policy had a choice to get wrong.
    """
    best: list[int | None] = [None]
    total = [0]
    seen_dead: set[str] = set()

    def dfs(state, depth: int) -> None:
        if state.is_solved:
            total[0] += 1
            if best[0] is None or depth < best[0]:
                best[0] = depth
            return
        key = game.stringRepresentation(state)
        if key in seen_dead:
            return
        found_before = total[0]
        for action in legal_actions(state):
            nxt = apply_fold(state, *decode(state.m, state.n, action))
            if nxt is not None:
                dfs(nxt, depth + 1)
        if total[0] == found_before:
            seen_dead.add(key)

    dfs(game.getInitBoard(), 0)
    return best[0], total[0]


def policy_sequence(game: GridGame, net, budget: int, rng) -> list[int] | None:
    """Drive the trained policy greedily and return the fold sequence it realises.

    At each step it runs SP-MCTS with the net for the same per-step budget the
    evaluator gives the whole episode, then takes the most-visited legal action. Returns
    None if it reaches a dead end.
    """
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
    ap.add_argument("--shape", default="8x8")
    ap.add_argument("--count", type=int, default=40)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--checkpoint", default="grid2d/checkpoints/final.pt")
    ap.add_argument("--out", default="grid2d/fold_count.json")
    args = ap.parse_args()

    m, n = (int(x) for x in args.shape.lower().split("x"))
    budget = budget_for(m, n)
    net = NetWrapper()
    net.load(args.checkpoint)
    rng = random.Random(args.seed)

    instances = make_set(m, n, args.count, seed=EVAL_SEED, family="derived")
    rows = []
    for i, (hmv, vmv) in enumerate(instances):
        game = GridGame(hmv, vmv)
        oracle_min, n_sequences = oracle_solutions(game)
        seq = policy_sequence(game, net, budget, rng)
        rows.append(
            {
                "instance": i,
                "oracle_min_folds": oracle_min,
                "oracle_distinct_sequences": n_sequences,
                "policy_solved": seq is not None,
                "policy_folds": len(seq) if seq else None,
                "matches_oracle_min": bool(seq) and len(seq) == oracle_min,
            }
        )

    solved = [r for r in rows if r["policy_solved"]]
    matched = [r for r in solved if r["matches_oracle_min"]]
    oracle_mins = sorted({r["oracle_min_folds"] for r in rows if r["oracle_min_folds"]})
    policy_counts = sorted({r["policy_folds"] for r in solved})
    summary = {
        "shape": args.shape,
        "crease_lines": (m - 1) + (n - 1),
        "instances": len(rows),
        "policy_solved": len(solved),
        "policy_matched_oracle_min": len(matched),
        "distinct_oracle_min_values": oracle_mins,
        "distinct_policy_fold_counts": policy_counts,
        "mean_distinct_sequences_per_instance": (
            sum(r["oracle_distinct_sequences"] for r in rows) / max(1, len(rows))
        ),
        "min_distinct_sequences": min(
            (r["oracle_distinct_sequences"] for r in rows), default=0
        ),
        "budget_per_step": budget,
        "seed": args.seed,
        "eval_seed": EVAL_SEED,
        "checkpoint": args.checkpoint,
    }
    with open(args.out, "w") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, indent=2)
    for k, v in summary.items():
        print(f"{k}: {v}")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
