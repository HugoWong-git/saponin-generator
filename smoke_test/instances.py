"""Fixed-seed instance generation.

SCOPE NOTE -- the task asks for >= 200 held-out test instances per n.  That is not
achievable at n=6 or n=8: the entire space of M/V assignments is 2^(n-1), i.e. only 32
and 128 patterns respectively.  Rather than pad the test set with duplicates, or shrink
it to carve out a training split, those two lengths use their *complete* pattern space
as the test set and contribute nothing to training.  The net is trained on n=10 and n=12
only, which makes n=6 and n=8 out-of-distribution generalisation tests and keeps
train/test disjointness true by construction at every n.

Patterns are deduplicated within a length, so no pattern is scored twice.
"""

from __future__ import annotations

import random

MASTER_SEED = 20260821
N_VALUES = (6, 8, 10, 12)
TRAIN_LENGTHS = (10, 12)
N_TEST = 200
N_TRAIN = 400


def _pool(n: int, size: int, seed: int) -> list[tuple[str, ...]]:
    rng = random.Random(seed)
    space = 2 ** (n - 1)
    seen: set[tuple[str, ...]] = set()
    out: list[tuple[str, ...]] = []
    while len(out) < size and len(seen) < space:
        mv = tuple(rng.choice("MV") for _ in range(n - 1))
        if mv in seen:
            continue
        seen.add(mv)
        out.append(mv)
    return out


def instances(n: int) -> tuple[list[tuple[str, ...]], list[tuple[str, ...]]]:
    """Return (train, test) pattern lists for strip length n, disjoint by construction."""
    if n not in TRAIN_LENGTHS:
        return [], _pool(n, 2 ** (n - 1), MASTER_SEED + n)
    pool = _pool(n, N_TEST + N_TRAIN, MASTER_SEED + n)
    test, train = pool[:N_TEST], pool[N_TEST:]
    assert not (set(test) & set(train))
    return train, test


def train_pool() -> list[tuple[str, ...]]:
    """Every training pattern, across the lengths that contribute to training."""
    return [mv for n in TRAIN_LENGTHS for mv in instances(n)[0]]


if __name__ == "__main__":
    for n in N_VALUES:
        train, test = instances(n)
        print(
            f"n={n:2d}  space=2^{n - 1}={2 ** (n - 1):5d}  "
            f"train={len(train):3d}  test={len(test):3d}"
        )
    print(f"total training patterns: {len(train_pool())}")
