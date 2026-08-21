"""Self-play training loop -- alpha-zero-general's Coach shape, de-adversarialised.

No sign flips on the value backup and no player alternation: every example in an episode
carries the same terminal score, because there is only one agent and its reward is the
reward.  Checkpoints and the learning curve are written each iteration.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time

from .instances import instances, train_pool
from .net import NetWrapper
from .sp_mcts import SPMCTS
from .strip import StripGame, apply_fold, decode

CHECKPOINT_DIR = os.path.join(os.path.dirname(__file__), "checkpoints")
CURVE_PATH = os.path.join(os.path.dirname(__file__), "learning_curve.json")

TEMPERATURE_MOVES = 4  # sample early for exploration, then act greedily


def self_play_episode(game: StripGame, net: NetWrapper, sims: int, rng: random.Random):
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
        state = apply_fold(state, *decode(action))


def evaluate_curve_point(net: NetWrapper, budget: int, per_n: int, seed: int) -> dict:
    """Held-out solve rate, for the learning curve. Small subsets, kept cheap."""
    out = {}
    for n in (10, 12):
        test = instances(n)[1][:per_n]
        solved = 0
        for i, mv in enumerate(test):
            game = StripGame(mv)
            mcts = SPMCTS(game, net=net, rng=random.Random(seed + i))
            solved += mcts.run(game.getInitBoard(), budget)
        out[str(n)] = solved / len(test)
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=12)
    parser.add_argument("--episodes", type=int, default=60, help="self-play games / iter")
    parser.add_argument("--sims", type=int, default=25, help="MCTS sims per move")
    parser.add_argument("--eval-budget", type=int, default=40)
    parser.add_argument("--eval-per-n", type=int, default=60)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--window", type=int, default=4, help="iters of replay buffer")
    args = parser.parse_args()

    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    rng = random.Random(args.seed)
    pool = train_pool()
    net = NetWrapper()
    buffer: list[list] = []
    curve = []
    t0 = time.time()

    point = evaluate_curve_point(net, args.eval_budget, args.eval_per_n, args.seed)
    curve.append({"iteration": 0, "loss": None, "selfplay_solve_rate": None, **point})
    print(f"iter  0 (untrained)  held-out {point}  {time.time() - t0:.0f}s")

    for it in range(1, args.iterations + 1):
        fresh, solved = [], 0
        for _ in range(args.episodes):
            mv = rng.choice(pool)
            examples, score = self_play_episode(StripGame(mv), net, args.sims, rng)
            fresh.extend(examples)
            solved += score >= 1.0
        buffer.append(fresh)
        buffer = buffer[-args.window :]
        loss = net.train_on([e for chunk in buffer for e in chunk])

        net.save(os.path.join(CHECKPOINT_DIR, f"iter{it:02d}.pt"))
        point = evaluate_curve_point(net, args.eval_budget, args.eval_per_n, args.seed)
        curve.append(
            {
                "iteration": it,
                "loss": loss,
                "selfplay_solve_rate": solved / args.episodes,
                **point,
            }
        )
        print(
            f"iter {it:2d}  loss {loss:.4f}  self-play {solved / args.episodes:.3f}  "
            f"held-out {point}  {time.time() - t0:.0f}s"
        )
        with open(CURVE_PATH, "w") as fh:
            json.dump(
                {"args": vars(args), "wall_clock_s": time.time() - t0, "curve": curve},
                fh,
                indent=2,
            )

    net.save(os.path.join(CHECKPOINT_DIR, "final.pt"))
    print(f"done in {time.time() - t0:.0f}s -> {CURVE_PATH}")


if __name__ == "__main__":
    main()
