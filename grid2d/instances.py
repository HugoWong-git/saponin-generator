"""Instance generation for 2-D map folding, and the local (Maekawa) filter.

Two families, because they answer different questions.

``derived`` -- run a random legal fold sequence forward on an *unlabelled* grid,
choosing the over/under bit at each step, and read off the label each crease segment
must have carried. The instance is then solvable by construction, and solvable by the
real transition function rather than by a separate model of it. This mirrors the 1-D
setup, where every instance was solvable and the denominator was known.

``maekawa`` -- sample labels uniformly at random and keep only those satisfying
Maekawa's theorem at every interior vertex. These are *locally* valid by construction
and globally anything at all. This is the family that tests the parent project's
headline claim directly: the local theorems are necessary, not sufficient. If some of
these instances turn out to be unsolvable, that is the claim demonstrated on real
instances rather than asserted from the literature.

Kawasaki is not a filter here and cannot be. A grid's interior vertices have four 90
degree sectors, so the alternating sum is 90 - 90 + 90 - 90 = 0 identically. Every grid
satisfies Kawasaki at every vertex. That is a real limitation of this domain, noted
rather than papered over: it means only half the tier-1 reward gets exercised.
"""

from __future__ import annotations

import random

from .grid import (
    AXIS_H,
    AXIS_V,
    MOUNTAIN,
    VALLEY,
    GridState,
    check_no_crossing,
    fold_with_over,
    initial_state,
)


def maekawa_ok(
    hmv: tuple[tuple[str, ...], ...], vmv: tuple[tuple[str, ...], ...]
) -> bool:
    """|M - V| == 2 at every interior vertex.

    Interior vertex (r, c) is the grid point shared by cells (r,c), (r,c+1), (r+1,c),
    (r+1,c+1). Its four incident crease segments are the two halves of vertical line c
    above and below it, and the two halves of horizontal line r left and right of it.
    """
    m = len(vmv)
    n = len(hmv[0]) if hmv else len(vmv[0]) + 1
    for r in range(m - 1):
        for c in range(n - 1):
            around = (vmv[r][c], vmv[r + 1][c], hmv[r][c], hmv[r][c + 1])
            mountains = sum(1 for a in around if a == MOUNTAIN)
            if abs(mountains - (4 - mountains)) != 2:
                return False
    return True


def _label_for(state: GridState, axis: int, k: int, side: int, over: bool) -> list[str]:
    """What each segment of crease (axis, k) must be for this fold to use ``over``.

    Inverts ``fold_goes_over``: over == ((label == VALLEY) == (face > 0)), so
    label is VALLEY exactly when ``over`` agrees with the sign of that segment's face.
    """
    if axis == AXIS_V:
        moving_col = k if side == 0 else k + 1
        return [
            VALLEY if (over == (state.face(r, moving_col) > 0)) else MOUNTAIN
            for r in range(state.m)
        ]
    moving_row = k if side == 0 else k + 1
    return [
        VALLEY if (over == (state.face(moving_row, c) > 0)) else MOUNTAIN
        for c in range(state.n)
    ]


def derived_instance(
    m: int, n: int, rng: random.Random, tries: int = 200
) -> tuple[tuple[tuple[str, ...], ...], tuple[tuple[str, ...], ...]] | None:
    """Generate a solvable instance by folding first and labelling afterwards.

    Returns (hmv, vmv), or None if no full sequence was found within ``tries``.
    """
    for _ in range(tries):
        hmv = [[None] * n for _ in range(m - 1)]
        vmv = [[None] * (n - 1) for _ in range(m)]
        # Labels are irrelevant to fold_with_over, so a placeholder grid is fine here;
        # the real instance gets replayed through apply_fold by the caller.
        placeholder_h = tuple(tuple(MOUNTAIN for _ in range(n)) for _ in range(m - 1))
        placeholder_v = tuple(tuple(MOUNTAIN for _ in range(n - 1)) for _ in range(m))
        state = initial_state(placeholder_h, placeholder_v)

        moves = [(AXIS_V, k) for k in range(n - 1)] + [
            (AXIS_H, k) for k in range(m - 1)
        ]
        rng.shuffle(moves)
        ok = True
        for axis, k in moves:
            options = [(side, over) for side in (0, 1) for over in (True, False)]
            rng.shuffle(options)
            for side, over in options:
                candidate = fold_with_over(state, axis, k, side, over)
                if not check_no_crossing(candidate)[0]:
                    continue
                labels = _label_for(state, axis, k, side, over)
                if axis == AXIS_V:
                    for r in range(m):
                        vmv[r][k] = labels[r]
                else:
                    hmv[k] = list(labels)
                state = candidate
                break
            else:
                ok = False
                break
        if ok and state.is_solved:
            return (
                tuple(tuple(row) for row in hmv),
                tuple(tuple(row) for row in vmv),
            )
    return None


def maekawa_instance(
    m: int, n: int, rng: random.Random, tries: int = 5000
) -> tuple[tuple[tuple[str, ...], ...], tuple[tuple[str, ...], ...]] | None:
    """Uniformly random labels, rejected unless Maekawa holds at every interior vertex."""
    for _ in range(tries):
        hmv = tuple(
            tuple(rng.choice((MOUNTAIN, VALLEY)) for _ in range(n))
            for _ in range(m - 1)
        )
        vmv = tuple(
            tuple(rng.choice((MOUNTAIN, VALLEY)) for _ in range(n - 1))
            for _ in range(m)
        )
        if maekawa_ok(hmv, vmv):
            return hmv, vmv
    return None


def make_set(
    m: int, n: int, count: int, seed: int, family: str = "derived"
) -> list[tuple]:
    """A deduplicated instance set. Seeds are the reproducibility contract."""
    rng = random.Random(seed)
    gen = derived_instance if family == "derived" else maekawa_instance
    seen: set[tuple] = set()
    out: list[tuple] = []
    guard = 0
    while len(out) < count and guard < count * 400:
        guard += 1
        inst = gen(m, n, rng)
        if inst is not None and inst not in seen:
            seen.add(inst)
            out.append(inst)
    return out
