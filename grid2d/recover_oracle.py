"""Reconstruct an oracle survey JSON from a run's stdout log.

Why this exists: ``brute_force.py`` originally wrote its JSON only at the end of the
whole survey. That was fixed to write after every shape, but the fix could not be
retrofitted onto a process that was already running with the old module loaded. For
such a run, the per-shape rows exist only as flushed stdout lines.

This parses those lines back into the same schema ``brute_force.main`` would have
written, marked ``partial: True`` and ``recovered_from_log: True`` so nobody mistakes a
truncated survey for a complete one.

Usage:
    python -m grid2d.recover_oracle --log <stdout log> --out grid2d/oracle_derived.json
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re

ROW = re.compile(r"^\{'m':.*\}$")


def parse_rows(text: str) -> list[dict]:
    """Each survey row was printed as a Python dict literal, one per line."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if ROW.match(line):
            try:
                rows.append(ast.literal_eval(line))
            except (ValueError, SyntaxError):
                continue
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=11)
    ap.add_argument("--count", type=int, default=120)
    ap.add_argument("--family", default=None, help="defaults to the family in the rows")
    args = ap.parse_args()

    with open(args.log) as fh:
        rows = parse_rows(fh.read())
    if not rows:
        raise SystemExit(f"no survey rows found in {args.log}")

    family = args.family or rows[0].get("family", "unknown")
    rows = [r for r in rows if r.get("family") == family]

    payload = {
        "rows": rows,
        "seed": args.seed,
        "family": family,
        "count": args.count,
        "state_cap": 2_000_000,
        "partial": True,
        "recovered_from_log": True,
        "recovered_from": os.path.basename(args.log),
        "wall_clock_s": round(sum(r.get("seconds", 0) for r in rows), 1),
    }
    with open(args.out, "w") as fh:
        json.dump(payload, fh, indent=2)
    shapes = ", ".join(f"{r['m']}x{r['n']}" for r in rows)
    print(f"recovered {len(rows)} row(s) [{shapes}] for family '{family}' -> {args.out}")


if __name__ == "__main__":
    main()
