"""Render the result tables from the JSON the runs emit.

Exists so that no number in RESULTS.md is typed by hand.  Run it after evaluate.py,
train.py and `brute_force.py --test-sets`, and paste the output into RESULTS.md between
the generated-table markers.
"""

from __future__ import annotations

import json
import os

HERE = os.path.dirname(__file__)
ARM_LABEL = {
    "random": "random rollout",
    "mcts": "SP-MCTS (uniform)",
    "mcts+net": "SP-MCTS + trained net",
}


def _load(name):
    path = os.path.join(HERE, name)
    if not os.path.exists(path):
        return None
    with open(path) as fh:
        return json.load(fh)


def oracle_table() -> str:
    data = _load("oracle.json")
    if not data:
        return "_oracle.json missing_"
    lines = [
        "| n | test instances | solvable | min folds | mean reachable states | max |",
        "|---|---|---|---|---|---|",
    ]
    for row in data["per_n"]:
        folds = ", ".join(str(v) for v in row["min_folds_values"])
        lines.append(
            f"| {row['n']} | {row['n_instances']} | "
            f"{row['solvable']}/{row['n_instances']} "
            f"({row['solvable_fraction']:.3f}) | {folds} | "
            f"{row['mean_reachable_states']:.0f} | {row['max_reachable_states']} |"
        )
    lines.append("")
    lines.append(f"Wall clock: {data['wall_clock_s']:.0f}s.")
    return "\n".join(lines)


def arms_table(filename: str = "results.json") -> str:
    data = _load(filename)
    if not data:
        return f"_{filename} missing_"
    rows = data["rows"]
    budget = rows[0]["budget"]
    seeds = rows[0]["seeds"]
    lines = [
        f"Budget {budget} expansions per instance, seeds {seeds}. "
        f"Solve rate is mean +/- SD across seeds; expansions/solve is the mean spend "
        f"on instances that were solved.",
        "",
        "| n | instances | arm | solve rate | per-seed | expansions / solve |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        per_seed = ", ".join(f"{v:.3f}" for v in row["solve_rate_per_seed"])
        lines.append(
            f"| {row['n']} | {row['n_instances']} | {ARM_LABEL[row['arm']]} | "
            f"{row['solve_rate_mean']:.3f} +/- {row['solve_rate_sd']:.3f} | "
            f"{per_seed} | {row['expansions_per_solve_mean']:.1f} |"
        )
    lines.append("")
    lines.append(f"Wall clock: {data['wall_clock_s']:.0f}s total.")
    return "\n".join(lines)


def curve_table() -> str:
    data = _load("learning_curve.json")
    if not data:
        return "_learning_curve.json missing_"
    lines = [
        f"Training args: `{data['args']}`.",
        "",
        "| iteration | loss | self-play solve rate | held-out n=10 | held-out n=12 |",
        "|---|---|---|---|---|",
    ]
    for point in data["curve"]:
        loss = "-" if point["loss"] is None else f"{point['loss']:.3f}"
        sp = (
            "-"
            if point["selfplay_solve_rate"] is None
            else f"{point['selfplay_solve_rate']:.3f}"
        )
        lines.append(
            f"| {point['iteration']} | {loss} | {sp} | "
            f"{point['10']:.3f} | {point['12']:.3f} |"
        )
    lines.append("")
    lines.append(f"Wall clock: {data['wall_clock_s']:.0f}s.")
    return "\n".join(lines)


def margin_check(filename: str = "results.json") -> str:
    """P2 and P3: is the gap bigger than the seed spread?"""
    data = _load(filename)
    if not data:
        return f"_{filename} missing_"
    by = {(r["n"], r["arm"]): r for r in data["rows"]}
    ns = sorted({r["n"] for r in data["rows"]})
    lines = [
        "| n | comparison | gap in solve rate | pooled SD | gap > SD? | "
        "expansions/solve |",
        "|---|---|---|---|---|---|",
    ]
    for n in ns:
        for better, worse in (("mcts", "random"), ("mcts+net", "mcts")):
            if (n, better) not in by or (n, worse) not in by:
                continue
            a, b = by[(n, better)], by[(n, worse)]
            gap = a["solve_rate_mean"] - b["solve_rate_mean"]
            pooled = (a["solve_rate_sd"] ** 2 + b["solve_rate_sd"] ** 2) ** 0.5
            cost = (
                f"{a['expansions_per_solve_mean']:.1f} vs "
                f"{b['expansions_per_solve_mean']:.1f}"
            )
            lines.append(
                f"| {n} | {ARM_LABEL[better]} - {ARM_LABEL[worse]} | {gap:+.3f} | "
                f"{pooled:.3f} | {'yes' if gap > pooled else 'no'} | {cost} |"
            )
    return "\n".join(lines)


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    blocks = {
        "oracle": oracle_table,
        "arms": arms_table,
        "curve": curve_table,
        "margin": margin_check,
    }
    for name, fn in blocks.items():
        if which in ("all", name):
            print(f"\n### {name}\n")
            print(fn())
