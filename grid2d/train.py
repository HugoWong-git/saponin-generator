"""Self-play training loop for 2-D map folding.

Same de-adversarialised Coach shape as the 1-D run: no sign flips on the value backup,
no player alternation, every example in an episode carrying the same terminal score.

Instances are drawn from a training pool disjoint from the held-out shapes and seeds
used by ``evaluate.py``. Because instance *shape* varies here (unlike 1-D, where only
the length varied), the training pool mixes shapes so the padded encoder sees all of
them; generalisation to an unseen shape is reported separately by the evaluator.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time

from .grid import AXIS_H, AXIS_V, GridGame, decode
from .instances import make_set
from .net import NetWrapper
from smoke_test.sp_mcts import SPMCTS

CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "checkpoints")
CURVE_PATH = os.path.join(os.path.dirname(__file__), "learning_curve.json")

TEMPERATURE_MOVES = 4

TRAIN_SHAPES = [(6, 6), (8, 8), (6, 14)]
TRAIN_SEED = 900_001  # disjoint from the evaluation seed
CURVE_SHAPES = [(8, 8), (6, 14)]


def parse_shapes(spec: str) -> list[tuple[int, int]]:
    """'6x6,8x8' -> [(6, 6), (8, 8)]."""
    out = []
    for token in spec.split(","):
        m, n = token.strip().lower().split("x")
        out.append((int(m), int(n)))
    return out


def _write_curve(args: dict, history: list, path: str = CURVE_PATH) -> None:
    """Atomically write the learning curve so far.

    Temp file plus rename: os.replace is atomic on POSIX, so a kill between the
    two never leaves a half-written learning_curve.json behind.
    """
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump({"args": args, "history": history}, fh, indent=2)
    os.replace(tmp, path)


def budget_for(m: int, n: int, slack: int = 4) -> int:
    """Fold budget scaled to the instance.

    A fixed budget is wrong here: minimum folds is (m-1)+(n-1), which ranges from 10 to
    18 across the shapes used, so one number would be generous for small grids and tight
    for large ones. Every arm gets the same scaled budget, which is what keeps them
    comparable.
    """
    return (m - 1) + (n - 1) + slack


def _count_inversions(ks: list[int]) -> int:
    """Pairs out of ascending order -- O(L^2), fine for L <= ~20 crease lines."""
    return sum(1 for i in range(len(ks)) for j in range(i + 1, len(ks)) if ks[i] > ks[j])


def canonical_order_penalty(actions: list[int], m: int, n: int) -> float:
    """Candidate 3 diagnostic (cheap path): inversions against ascending crease index.

    CANDIDATE-3-DIAGNOSTIC: makes no physical-plausibility claim. It exists only to test
    whether self-play can respond to ANY non-flat terminal signal in a domain where every
    complete sequence currently scores identically (see grid2d/RESULTS.md, fold_count.json
    -- >=200,000 equally-valid orderings per 8x8 instance). A positive result here shows
    the pipeline CAN learn an arbitrary target, not that it has learned anything about
    real fold quality. See research/benchmarks_verification.md for why OrigamiBench's IoU
    metric could not supply a real one: it scores distance-to-target, and every complete
    map-folding sequence reaches the identical target, so IoU is 1.0 for all of them.

    Counts inversions separately per axis (vertical creases 0..n-2, horizontal creases
    0..m-2), normalised by the maximum possible for that axis's sequence length, so the
    penalty is comparable across the two axis lengths and across grid shapes.
    """
    v_ks = [decode(m, n, a)[1] for a in actions if decode(m, n, a)[0] == AXIS_V]
    h_ks = [decode(m, n, a)[1] for a in actions if decode(m, n, a)[0] == AXIS_H]
    inv_v, inv_h = _count_inversions(v_ks), _count_inversions(h_ks)
    max_v = len(v_ks) * (len(v_ks) - 1) / 2
    max_h = len(h_ks) * (len(h_ks) - 1) / 2
    max_total = max_v + max_h
    return (inv_v + inv_h) / max_total if max_total > 0 else 0.0


def self_play_episode(
    game: GridGame,
    net: NetWrapper,
    sims: int,
    rng: random.Random,
    canon_lambda: float = 0.0,
):
    state = game.getInitBoard()
    trace = []
    actions_taken: list[int] = []
    while True:
        score = game.getGameEnded(state)
        if score != 0.0:
            # Cheap-path reward shaping ONLY: this adjusts the training target written
            # into the replay examples below. It does NOT touch getGameEnded, GridState,
            # or stringRepresentation, so SPMCTS.search()'s own tree search and rollout
            # -- which call game.getGameEnded directly -- see only the raw 0/1 score,
            # exactly as before. Only genuine solves (score > 0) are shaped; the
            # terminal-failure branch of getGameEnded is untouched.
            if score > 0.0 and canon_lambda > 0.0:
                penalty = canonical_order_penalty(actions_taken, game.m, game.n)
                score = score - canon_lambda * penalty
            return [(s, pi, score) for s, pi in trace], score
        mcts = SPMCTS(game, net=net, rng=rng)
        for _ in range(sims):
            mcts.search(state)
        temperature = 1.0 if len(trace) < TEMPERATURE_MOVES else 0.25
        pi = mcts.policy(state, temperature)
        trace.append((state, pi[: game.getActionSize()]))
        r, cumulative = rng.random(), 0.0
        action = len(pi) - 1
        for a, p in enumerate(pi):
            cumulative += p
            if r <= cumulative:
                action = a
                break
        actions_taken.append(action)
        state = game.getNextState(state, 1, action)[0]


def evaluate_curve_point(
    net: NetWrapper, per_shape: int, seed: int, shapes=None
) -> dict:
    """Held-out solve rate for the learning curve. Small subsets, kept cheap."""
    out = {}
    for m, n in shapes or CURVE_SHAPES:
        test = make_set(m, n, per_shape, seed=seed, family="derived")
        solved = 0
        for i, (hmv, vmv) in enumerate(test):
            game = GridGame(hmv, vmv)
            mcts = SPMCTS(game, net=net, rng=random.Random(seed + i))
            solved += mcts.run(game.getInitBoard(), budget_for(m, n))
        out[f"{m}x{n}"] = solved / max(1, len(test))
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=12)
    ap.add_argument("--episodes", type=int, default=60)
    ap.add_argument("--sims", type=int, default=25)
    ap.add_argument("--pool", type=int, default=60)
    ap.add_argument("--curve-per-shape", type=int, default=40)
    ap.add_argument("--curve-seed", type=int, default=777_001)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--window", type=int, default=4)
    # Shape selection is config, not algorithm. Defaults reproduce the original run
    # exactly, so an ablation can restrict shapes without changing anything else.
    ap.add_argument("--train-shapes", default=",".join(f"{m}x{n}" for m, n in TRAIN_SHAPES))
    ap.add_argument("--curve-shapes", default=",".join(f"{m}x{n}" for m, n in CURVE_SHAPES))
    ap.add_argument("--curve-path", default=CURVE_PATH)
    ap.add_argument("--checkpoint-dir", default=CHECKPOINT_DIR)
    ap.add_argument("--tag", default="", help="suffix for checkpoint filenames")
    ap.add_argument(
        "--canon-lambda", type=float, default=0.0,
        help="Candidate-3 diagnostic weight (0.0 = original behaviour, unshaped)",
    )
    args = ap.parse_args()

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    rng = random.Random(args.seed)
    net = NetWrapper()

    train_shapes = parse_shapes(args.train_shapes)
    curve_shapes = parse_shapes(args.curve_shapes)
    os.makedirs(args.checkpoint_dir, exist_ok=True)

    pool = []
    for m, n in train_shapes:
        pool += [(m, n, h, v) for h, v in make_set(m, n, args.pool, seed=TRAIN_SEED)]
    if not pool:
        raise SystemExit("training pool is empty")

    started = time.time()
    history = [
        {
            "iteration": 0,
            "loss": None,
            "self_play_solve_rate": None,
            "held_out": evaluate_curve_point(
                net, args.curve_per_shape, args.curve_seed, curve_shapes
            ),
            "seconds": round(time.time() - started, 1),
        }
    ]
    print(f"iter  0 (untrained)  held-out {history[0]['held_out']}  "
          f"{history[0]['seconds']:.0f}s", flush=True)

    recent: list = []
    for iteration in range(1, args.iterations + 1):
        examples, solved = [], 0
        for _ in range(args.episodes):
            m, n, hmv, vmv = rng.choice(pool)
            episode, score = self_play_episode(
                GridGame(hmv, vmv), net, args.sims, rng, args.canon_lambda
            )
            examples += episode
            solved += score > 0
        recent.append(examples)
        recent[:] = recent[-args.window :]

        flat = [e for batch in recent for e in batch]
        loss = net.train_on(flat)
        held = evaluate_curve_point(
            net, args.curve_per_shape, args.curve_seed, curve_shapes
        )
        history.append(
            {
                "iteration": iteration,
                "loss": loss,
                "self_play_solve_rate": solved / args.episodes,
                "held_out": held,
                "seconds": round(time.time() - started, 1),
            }
        )
        net.save(os.path.join(args.checkpoint_dir, f"iter{iteration:02d}{args.tag}.pt"))
        net.save(os.path.join(args.checkpoint_dir, f"final{args.tag}.pt"))
        # Write the curve every iteration, not just at the end: a crash or a
        # watchdog kill should cost at most the iteration in flight, never the
        # whole history. Written to a temp file and renamed so a kill mid-write
        # cannot leave truncated JSON on disk.
        _write_curve(vars(args), history, args.curve_path)
        print(
            f"iter {iteration:2d}  loss {loss:.4f}  "
            f"self-play {solved / args.episodes:.3f}  held-out {held}  "
            f"{history[-1]['seconds']:.0f}s",
            flush=True,
        )

    _write_curve(vars(args), history, args.curve_path)
    print(f"done in {time.time() - started:.0f}s -> {args.curve_path}")


if __name__ == "__main__":
    main()
