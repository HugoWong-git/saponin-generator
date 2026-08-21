"""Plots for the 2-D map-folding experiment. Reads only the run JSON, never hardcodes."""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(__file__)
PLOT_DIR = os.path.join(HERE, "plots")

ARM_LABEL = {
    "random": "random rollout",
    "mcts": "SP-MCTS (uniform)",
    "mcts+net": "SP-MCTS + trained net",
}
ARM_COLOR = {"random": "#888888", "mcts": "#1f77b4", "mcts+net": "#d62728"}


def _load(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def learning_curve() -> str | None:
    data = _load("learning_curve.json")
    if not data:
        return None
    history = data["history"]
    iterations = [h["iteration"] for h in history]
    shapes = sorted(history[0]["held_out"])

    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    for shape in shapes:
        ax.plot(
            iterations,
            [h["held_out"][shape] for h in history],
            marker="o",
            label=f"held-out {shape}",
        )
    self_play = [
        (h["iteration"], h["self_play_solve_rate"])
        for h in history
        if h["self_play_solve_rate"] is not None
    ]
    if self_play:
        ax.plot(
            [i for i, _ in self_play],
            [v for _, v in self_play],
            marker="s",
            linestyle="--",
            color="#999999",
            label="self-play (training)",
        )
    args = data["args"]
    ax.set_xlabel("self-play iteration")
    ax.set_ylabel("solve rate")
    ax.set_title(
        "2-D map folding: held-out solve rate vs self-play iteration\n"
        f"scaled budget (m-1)+(n-1)+4, {args['curve_per_shape']} instances/shape, "
        f"seed {args['seed']}"
    )
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, "learning_curve.png")
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


def solve_rate_by_shape() -> str | None:
    data = _load("results.json")
    if not data:
        return None
    rows = data["rows"]
    shapes = sorted({r["shape"] for r in rows}, key=lambda s: rows[
        [r["shape"] for r in rows].index(s)
    ]["m"] * 100 + rows[[r["shape"] for r in rows].index(s)]["n"])
    arms = [a for a in ("random", "mcts", "mcts+net") if any(r["arm"] == a for r in rows)]

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    width = 0.8 / len(arms)
    for i, arm in enumerate(arms):
        by_shape = {r["shape"]: r for r in rows if r["arm"] == arm}
        xs = [j + i * width for j in range(len(shapes))]
        ax.bar(
            xs,
            [by_shape[s]["solve_rate_mean"] for s in shapes],
            width=width,
            yerr=[by_shape[s]["solve_rate_sd"] for s in shapes],
            capsize=3,
            label=ARM_LABEL[arm],
            color=ARM_COLOR[arm],
        )
    unseen = {r["shape"] for r in rows if r.get("unseen_shape")}
    labels = [f"{s}\n(unseen shape)" if s in unseen else s for s in shapes]
    ax.set_xticks([j + width * (len(arms) - 1) / 2 for j in range(len(shapes))])
    ax.set_xticklabels(labels)
    ax.set_ylabel("solve rate")
    ax.set_ylim(0, 1.05)
    ax.axhline(1.0, color="black", linewidth=0.8, linestyle=":")
    ax.set_title(
        "2-D map folding: solve rate by grid shape\n"
        f"scaled budget (m-1)+(n-1)+{data['slack']}, seeds "
        f"{rows[0]['seeds']}, error bars = SD across seeds"
    )
    ax.grid(axis="y", alpha=0.3)
    ax.legend(loc="lower left")
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, "solve_rate_by_shape.png")
    fig.savefig(out, dpi=140)
    plt.close(fig)
    return out


if __name__ == "__main__":
    os.makedirs(PLOT_DIR, exist_ok=True)
    for path in (learning_curve(), solve_rate_by_shape()):
        print(path if path else "skipped (missing run JSON)")
