"""Learning curve and solve-rate-by-n bar chart, from the JSON the runs emit."""

from __future__ import annotations

import json
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(__file__)
PLOT_DIR = os.path.join(HERE, "plots")
ARM_STYLE = {
    "random": ("#888888", "random rollout"),
    "mcts": ("#1f77b4", "SP-MCTS (uniform)"),
    "mcts+net": ("#d62728", "SP-MCTS + trained net"),
}


def learning_curve(path: str = os.path.join(HERE, "learning_curve.json")) -> None:
    with open(path) as fh:
        data = json.load(fh)
    curve = data["curve"]
    iters = [p["iteration"] for p in curve]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for n, colour in (("10", "#1f77b4"), ("12", "#d62728")):
        ax.plot(iters, [p[n] for p in curve], "o-", color=colour, label=f"n = {n}")
    selfplay = [p["selfplay_solve_rate"] for p in curve]
    ax.plot(
        [i for i, s in zip(iters, selfplay) if s is not None],
        [s for s in selfplay if s is not None],
        "s--", color="#888888", alpha=0.7, label="self-play (training)",
    )
    ax.set_xlabel("self-play iteration")
    ax.set_ylabel("solve rate")
    ax.set_title(
        f"Held-out solve rate vs self-play iteration\n"
        f"budget {data['args']['eval_budget']} expansions, "
        f"{data['args']['eval_per_n']} instances/n, seed {data['args']['seed']}",
        fontsize=10,
    )
    ax.set_ylim(0, 1.02)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=9)
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, "learning_curve.png")
    fig.savefig(out, dpi=140)
    print(out)


def solve_rate_by_n(path: str = os.path.join(HERE, "results.json")) -> None:
    with open(path) as fh:
        rows = json.load(fh)["rows"]
    ns = sorted({r["n"] for r in rows})
    arms = [a for a in ARM_STYLE if any(r["arm"] == a for r in rows)]
    width = 0.8 / len(arms)

    fig, ax = plt.subplots(figsize=(7, 4.2))
    for k, arm in enumerate(arms):
        vals = [next(r for r in rows if r["n"] == n and r["arm"] == arm) for n in ns]
        xs = [i + (k - (len(arms) - 1) / 2) * width for i in range(len(ns))]
        colour, label = ARM_STYLE[arm]
        ax.bar(
            xs, [v["solve_rate_mean"] for v in vals], width,
            yerr=[v["solve_rate_sd"] for v in vals], capsize=3,
            color=colour, label=label,
        )
    ax.set_xticks(range(len(ns)))
    ax.set_xticklabels([f"n = {n}" for n in ns])
    ax.set_ylabel("solve rate")
    ax.set_ylim(0, 1.02)
    ax.axhline(1.0, ls=":", c="k", lw=1)
    ax.text(len(ns) - 0.5, 1.005, "every instance is solvable", fontsize=8, ha="right")
    budget = rows[0]["budget"]
    seeds = rows[0]["seeds"]
    ax.set_title(
        f"Solve rate by strip length\nbudget {budget} expansions, "
        f"seeds {seeds}, error bars = SD across seeds",
        fontsize=10,
    )
    ax.grid(axis="y", alpha=0.3)
    ax.legend(fontsize=9, loc="lower left")
    fig.tight_layout()
    out = os.path.join(PLOT_DIR, "solve_rate_by_n.png")
    fig.savefig(out, dpi=140)
    print(out)


if __name__ == "__main__":
    os.makedirs(PLOT_DIR, exist_ok=True)
    learning_curve()
    solve_rate_by_n()
