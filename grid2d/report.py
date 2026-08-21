"""Render the 2-D result tables from the run JSON.

Every number in RESULTS.md comes through here, so nothing in that file is typed by
hand. ``python -m grid2d.report --inject`` rewrites the GENERATED blocks in place.
"""

from __future__ import annotations

import json
import math
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


def _shape_order(rows):
    seen = {}
    for r in rows:
        seen.setdefault(r["shape"], (r["m"], r["n"]))
    return sorted(seen, key=lambda s: seen[s])


def oracle_table() -> str:
    out = []
    for name, caption in (
        ("oracle_derived.json", "Instances derived from a real fold sequence"),
        ("oracle_maekawa.json", "Instances that satisfy Maekawa at every interior vertex"),
    ):
        data = _load(name)
        if not data:
            continue
        lines = [
            f"**{caption}** (seed {data['seed']}, {data['wall_clock_s']}s):",
            "",
            "| shape | instances | solvable | min folds | expected | mean states | max | complete |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in data["rows"]:
            folds = ", ".join(str(v) for v in r["min_folds_values"]) or "-"
            lines.append(
                f"| {r['m']}x{r['n']} | {r['n_instances']} | "
                f"{r['solvable']}/{r['n_instances']} ({r['solvable_fraction']:.3f}) | "
                f"{folds} | {r['expected_min_folds']} | {r['mean_states']:.0f} | "
                f"{r['max_states']} | {'yes' if r['all_complete'] else 'NO (capped)'} |"
            )
        out.append("\n".join(lines))
    return "\n\n".join(out) if out else "_oracle JSON missing_"


def arms_table() -> str:
    data = _load("results.json")
    if not data:
        return "_results.json missing_"
    rows = data["rows"]
    lines = [
        f"Budget is scaled per shape: (m-1)+(n-1)+{data['slack']}. "
        f"{data['count']} held-out instances per shape, seeds {rows[0]['seeds']}. "
        "Solve rate is mean +/- SD across seeds.",
        "",
        "| shape | budget | instances | arm | solve rate | per-seed | expansions / solve |",
        "|---|---|---|---|---|---|---|",
    ]
    for shape in _shape_order(rows):
        for r in [x for x in rows if x["shape"] == shape]:
            per_seed = ", ".join(f"{v:.3f}" for v in r["solve_rate_per_seed"])
            tag = " *(unseen shape)*" if r.get("unseen_shape") else ""
            lines.append(
                f"| {shape}{tag} | {r['budget']} | {r['n_instances']} | "
                f"{ARM_LABEL[r['arm']]} | {r['solve_rate_mean']:.3f} "
                f"+/- {r['solve_rate_sd']:.3f} | {per_seed} | "
                f"{r['expansions_per_solve_mean']:.1f} |"
            )
    lines += ["", f"Wall clock: {data['wall_clock_s']}s total."]
    return "\n".join(lines)


def margin_check() -> str:
    data = _load("results.json")
    if not data:
        return "_results.json missing_"
    rows = data["rows"]
    lines = [
        "| shape | comparison | gap in solve rate | pooled SD | gap > SD? | expansions/solve |",
        "|---|---|---|---|---|---|",
    ]
    for shape in _shape_order(rows):
        by_arm = {r["arm"]: r for r in rows if r["shape"] == shape}
        for hi, lo in (("mcts", "random"), ("mcts+net", "mcts")):
            if hi not in by_arm or lo not in by_arm:
                continue
            a, b = by_arm[hi], by_arm[lo]
            gap = a["solve_rate_mean"] - b["solve_rate_mean"]
            pooled = math.hypot(a["solve_rate_sd"], b["solve_rate_sd"])
            lines.append(
                f"| {shape} | {ARM_LABEL[hi]} - {ARM_LABEL[lo]} | {gap:+.3f} | "
                f"{pooled:.3f} | {'yes' if gap > pooled else 'no'} | "
                f"{a['expansions_per_solve_mean']:.1f} vs "
                f"{b['expansions_per_solve_mean']:.1f} |"
            )
    return "\n".join(lines)


def control_table() -> str:
    trained, untrained = _load("results.json"), _load("results_untrained.json")
    if not trained or not untrained:
        return "_results.json or results_untrained.json missing_"
    uniform = {r["shape"]: r for r in trained["rows"] if r["arm"] == "mcts"}
    fresh = {r["shape"]: r for r in untrained["rows"] if r["arm"] == "mcts+net"}
    learned = {r["shape"]: r for r in trained["rows"] if r["arm"] == "mcts+net"}
    lines = [
        "| shape | SP-MCTS uniform | same net, random weights | trained net |",
        "|---|---|---|---|",
    ]
    for shape in _shape_order(trained["rows"]):
        if shape not in fresh:
            continue
        lines.append(
            f"| {shape} | {uniform[shape]['solve_rate_mean']:.3f} "
            f"+/- {uniform[shape]['solve_rate_sd']:.3f} | "
            f"{fresh[shape]['solve_rate_mean']:.3f} "
            f"+/- {fresh[shape]['solve_rate_sd']:.3f} | "
            f"{learned[shape]['solve_rate_mean']:.3f} "
            f"+/- {learned[shape]['solve_rate_sd']:.3f} |"
        )
    return "\n".join(lines)


def curve_table() -> str:
    data = _load("learning_curve.json")
    if not data:
        return "_learning_curve.json missing_"
    history = data["history"]
    shapes = sorted(history[0]["held_out"])
    lines = [
        f"Training args: `{data['args']}`.",
        "",
        "| iteration | loss | self-play solve rate | "
        + " | ".join(f"held-out {s}" for s in shapes)
        + " | seconds |",
        "|---" * (4 + len(shapes)) + "|",
    ]
    for h in history:
        loss = "-" if h["loss"] is None else f"{h['loss']:.4f}"
        sp = (
            "-"
            if h["self_play_solve_rate"] is None
            else f"{h['self_play_solve_rate']:.3f}"
        )
        held = " | ".join(f"{h['held_out'][s]:.3f}" for s in shapes)
        lines.append(
            f"| {h['iteration']} | {loss} | {sp} | {held} | {h['seconds']:.0f} |"
        )
    return "\n".join(lines)


BLOCKS = {
    "oracle": oracle_table,
    "arms": arms_table,
    "margin": margin_check,
    "control": control_table,
    "curve": curve_table,
}


def inject(path: str = os.path.join(HERE, "RESULTS.md")) -> None:
    with open(path) as fh:
        text = fh.read()
    for name, fn in BLOCKS.items():
        start, end = f"<!-- GENERATED:{name} -->", f"<!-- /GENERATED:{name} -->"
        i, j = text.find(start), text.find(end)
        if i < 0 or j < 0:
            raise SystemExit(f"marker for {name} missing from {path}")
        text = text[: i + len(start)] + "\n" + fn() + "\n" + text[j:]
    with open(path, "w") as fh:
        fh.write(text)
    print(f"injected {', '.join(BLOCKS)} -> {path}")


if __name__ == "__main__":
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which == "--inject":
        inject()
    else:
        for name, fn in BLOCKS.items():
            if which in ("all", name):
                print(f"\n### {name}\n")
                print(fn())
