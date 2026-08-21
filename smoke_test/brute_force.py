"""Exhaustive ground truth for small strips.

Enumerates the complete reachable state graph under the legality check, giving three
things the rest of the experiment needs:

  * whether an instance is solvable at all (the denominator for solve rate),
  * the minimum number of folds on a solution,
  * every reachable state, for the P1 cross-check against the independent geometric
    verifier.

Under this action model each action folds exactly one crease, so a solution always has
exactly n-1 folds.  The minimum is computed anyway rather than assumed -- it is a cheap
assertion that the transition function does what the model says.
"""

from __future__ import annotations

from dataclasses import dataclass

from .strip import StripGame, StripState, apply_fold, decode, action_size


@dataclass
class BruteForceResult:
    mv: tuple[str, ...]
    solvable: bool
    min_folds: int | None
    n_states: int
    complete: bool  # False if the state cap was hit before exhausting the graph

    @property
    def n(self) -> int:
        return len(self.mv) + 1


def explore(
    mv: tuple[str, ...], cap: int = 400_000, collect: bool = False
) -> tuple[BruteForceResult, list[StripState]]:
    """Breadth-first sweep of every state reachable from the unfolded strip."""
    game = StripGame(mv)
    root = game.getInitBoard()
    seen = {game.stringRepresentation(root)}
    frontier = [root]
    collected = [root] if collect else []
    min_folds: int | None = None
    n_states = 1
    complete = True

    while frontier:
        nxt: list[StripState] = []
        for state in frontier:
            for a in range(action_size(state.n)):
                child = apply_fold(state, *decode(a))
                if child is None:
                    continue
                key = game.stringRepresentation(child)
                if key in seen:
                    continue
                seen.add(key)
                n_states += 1
                if collect:
                    collected.append(child)
                if child.is_solved and (min_folds is None or child.step < min_folds):
                    min_folds = child.step
                nxt.append(child)
                if n_states >= cap:
                    complete = False
                    break
            if not complete:
                break
        if not complete:
            break
        frontier = nxt

    return (
        BruteForceResult(
            mv=tuple(mv),
            solvable=min_folds is not None,
            min_folds=min_folds,
            n_states=n_states,
            complete=complete,
        ),
        collected,
    )


def solve(mv: tuple[str, ...], cap: int = 400_000) -> BruteForceResult:
    return explore(mv, cap=cap, collect=False)[0]


def main() -> None:
    import argparse
    import itertools
    import json
    import os
    import statistics
    import time

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=6, help="strip length")
    parser.add_argument("--all", action="store_true", help="enumerate every M/V pattern")
    parser.add_argument(
        "--test-sets", action="store_true", help="run the oracle over every test instance"
    )
    parser.add_argument(
        "--out", default=os.path.join(os.path.dirname(__file__), "oracle.json")
    )
    args = parser.parse_args()

    if args.test_sets:
        from .instances import N_VALUES, instances

        summary = []
        t0 = time.time()
        for n in N_VALUES:
            test = instances(n)[1]
            results = [solve(mv) for mv in test]
            assert all(r.complete for r in results), "state cap hit; raise --cap"
            solvable = [r for r in results if r.solvable]
            summary.append(
                {
                    "n": n,
                    "n_instances": len(test),
                    "solvable": len(solvable),
                    "solvable_fraction": len(solvable) / len(test),
                    "min_folds_values": sorted({r.min_folds for r in solvable}),
                    "mean_reachable_states": statistics.mean(r.n_states for r in results),
                    "max_reachable_states": max(r.n_states for r in results),
                }
            )
            print(summary[-1])
        with open(args.out, "w") as fh:
            json.dump({"wall_clock_s": time.time() - t0, "per_n": summary}, fh, indent=2)
        print(f"{time.time() - t0:.0f}s -> {args.out}")
        return

    patterns = (
        list(itertools.product("MV", repeat=args.n - 1))
        if args.all
        else [tuple("MV"[i % 2] for i in range(args.n - 1))]
    )
    t0 = time.time()
    solvable = sum(1 for p in patterns if solve(tuple(p)).solvable)
    print(
        f"n={args.n}  patterns={len(patterns)}  solvable={solvable} "
        f"({solvable / len(patterns):.3f})  {time.time() - t0:.1f}s"
    )


if __name__ == "__main__":
    main()
