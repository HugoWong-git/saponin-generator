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


if __name__ == "__main__":
    import argparse
    import itertools
    import time

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=6, help="strip length")
    parser.add_argument("--all", action="store_true", help="enumerate every M/V pattern")
    args = parser.parse_args()

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
