"""Ground truth for 2-D map folding: exhaustive search over legal fold sequences.

The oracle and the denominator. For every instance it reports whether a full legal
fold sequence exists and how many states are reachable, so solve rates have a
denominator that is known rather than assumed.

Unlike the 1-D strip -- where every instance turned out to be solvable and the metric
was degenerate -- Maekawa-valid grids are frequently *not* solvable. That is the point
of the family: it is the parent project's "local theorems are necessary, not sufficient"
claim, demonstrated on instances this code generates and this oracle judges, rather than
cited from the literature.
"""

from __future__ import annotations

import argparse
import json
import time

from .grid import GridGame, GridState, apply_fold, decode, legal_actions
from .instances import make_set

STATE_CAP = 2_000_000


def explore(game: GridGame) -> tuple[bool, int, int | None, bool]:
    """Exhaustive DFS with a transposition table.

    Returns (solvable, states_seen, min_folds, complete). ``complete`` is False only if
    the state cap was hit, in which case ``solvable`` is a lower bound on the truth.
    """
    seen: set[str] = set()
    best: list[int | None] = [None]
    capped = [False]

    def dfs(state: GridState) -> None:
        if capped[0]:
            return
        if state.is_solved:
            if best[0] is None or state.n_folded < best[0]:
                best[0] = state.n_folded
            return
        key = game.stringRepresentation(state)
        if key in seen:
            return
        if len(seen) >= STATE_CAP:
            capped[0] = True
            return
        seen.add(key)
        for action in legal_actions(state):
            axis, k, side = decode(state.m, state.n, action)
            nxt = apply_fold(state, axis, k, side)
            if nxt is not None:
                dfs(nxt)

    dfs(game.getInitBoard())
    return best[0] is not None, len(seen), best[0], not capped[0]


def survey(shapes, count: int, seed: int, family: str) -> list[dict]:
    rows = []
    for m, n in shapes:
        started = time.time()
        instances = make_set(m, n, count, seed=seed, family=family)
        results = [explore(GridGame(h, v)) for h, v in instances]
        solvable = [r for r in results if r[0]]
        rows.append(
            {
                "m": m,
                "n": n,
                "family": family,
                "n_instances": len(instances),
                "solvable": len(solvable),
                "solvable_fraction": len(solvable) / max(1, len(instances)),
                "min_folds_values": sorted({r[2] for r in solvable}),
                "expected_min_folds": (m - 1) + (n - 1),
                "mean_states": sum(r[1] for r in results) / max(1, len(results)),
                "max_states": max((r[1] for r in results), default=0),
                "all_complete": all(r[3] for r in results),
                "seconds": round(time.time() - started, 1),
            }
        )
        print(rows[-1], flush=True)
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--shapes", default="6x6,8x8,6x14")
    ap.add_argument("--count", type=int, default=200)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--family", default="derived", choices=("derived", "maekawa"))
    ap.add_argument("--out", default="grid2d/oracle.json")
    args = ap.parse_args()

    shapes = []
    for token in args.shapes.split(","):
        m, n = token.lower().split("x")
        shapes.append((int(m), int(n)))

    started = time.time()
    rows = survey(shapes, args.count, args.seed, args.family)
    payload = {
        "rows": rows,
        "seed": args.seed,
        "family": args.family,
        "count": args.count,
        "state_cap": STATE_CAP,
        "wall_clock_s": round(time.time() - started, 1),
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
