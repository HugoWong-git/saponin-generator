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

from .grid import GridGame
from .instances import make_set
from .net import NetWrapper
from smoke_test.sp_mcts import SPMCTS

CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "checkpoints")
CURVE_PATH = os.path.join(os.path.dirname(__file__), "learning_curve.json")

TEMPERATURE_MOVES = 4

TRAIN_SHAPES = [(6, 6), (8, 8), (6, 14)]
TRAIN_SEED = 900_001  # disjoint from the evaluation seed
CURVE_SHAPES = [(8, 8), (6, 14)]


def budget_for(m: int, n: int, slack: int = 4) -> int:
    """Fold budget scaled to the instance.

    A fixed budget is wrong here: minimum folds is (m-1)+(n-1), which ranges from 10 to
    18 across the shapes used, so one number would be generous for small grids and tight
    for large ones. Every arm gets the same scaled budget, which is what keeps them
    comparable.
    """
    return (m - 1) + (n - 1) + slack


def self_play_episode(game: GridGame, net: NetWrapper, sims: int, rng: random.Random):
    state = game.getInitBoard()
    trace = []
    while True:
        score = game.getGameEnded(state)
        if score != 0.0:
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
        state = game.getNextState(state, 1, action)[0]


def evaluate_curve_point(net: NetWrapper, per_shape: int, seed: int) -> dict:
    """Held-out solve rate for the learning curve. Small subsets, kept cheap."""
    out = {}
    for m, n in CURVE_SHAPES:
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
    args = ap.parse_args()

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    rng = random.Random(args.seed)
    net = NetWrapper()

    pool = []
    for m, n in TRAIN_SHAPES:
        pool += [(m, n, h, v) for h, v in make_set(m, n, args.pool, seed=TRAIN_SEED)]
    if not pool:
        raise SystemExit("training pool is empty")

    started = time.time()
    history = [
        {
            "iteration": 0,
            "loss": None,
            "self_play_solve_rate": None,
            "held_out": evaluate_curve_point(net, args.curve_per_shape, args.curve_seed),
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
            episode, score = self_play_episode(GridGame(hmv, vmv), net, args.sims, rng)
            examples += episode
            solved += score > 0
        recent.append(examples)
        recent[:] = recent[-args.window :]

        flat = [e for batch in recent for e in batch]
        loss = net.train_on(flat)
        held = evaluate_curve_point(net, args.curve_per_shape, args.curve_seed)
        history.append(
            {
                "iteration": iteration,
                "loss": loss,
                "self_play_solve_rate": solved / args.episodes,
                "held_out": held,
                "seconds": round(time.time() - started, 1),
            }
        )
        net.save(os.path.join(CHECKPOINT_DIR, f"iter{iteration:02d}.pt"))
        net.save(os.path.join(CHECKPOINT_DIR, "final.pt"))
        print(
            f"iter {iteration:2d}  loss {loss:.4f}  "
            f"self-play {solved / args.episodes:.3f}  held-out {held}  "
            f"{history[-1]['seconds']:.0f}s",
            flush=True,
        )

    with open(CURVE_PATH, "w") as fh:
        json.dump({"args": vars(args), "history": history}, fh, indent=2)
    print(f"done in {time.time() - started:.0f}s -> {CURVE_PATH}")


if __name__ == "__main__":
    main()
