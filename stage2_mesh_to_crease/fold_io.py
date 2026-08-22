"""Read/write the FOLD (.fold) JSON format.

FOLD is the crease-pattern interchange format research/summary.md fixes as the
Stage 2 <-> Stage 3 boundary ("keeps Stage 2<->3 decoupled and lets patterns be
hand-written for tests"). This module is deliberately format-level only: it knows
the FOLD schema, not what a crease pattern *means* -- that belongs to
stage3_fold_sequence_rl/origami/crease_pattern.py's OrigamiState, whose own
from_fold_file/to_fold_file are still stubbed there (M1, not this file's scope).

Field names and semantics verified against the spec at
https://github.com/edemaine/fold/blob/main/doc/spec.md :
    file_spec, file_creator      -- format metadata
    vertices_coords               -- [[x, y] or [x, y, z], ...]
    edges_vertices                -- [[v0, v1], ...]
    edges_assignment               -- one of "M", "V", "F", "U", "B" per edge
    edges_foldAngle (optional)    -- degrees in [-180, 180]; + valley, - mountain, 0 flat
    faces_vertices                -- [[v0, v1, v2, ...], ...] per face, CCW
"""

from __future__ import annotations

import json

VALID_ASSIGNMENTS = {"M", "V", "F", "U", "B"}
REQUIRED_KEYS = ("vertices_coords", "edges_vertices")
CURRENT_FILE_SPEC = 1.1


class FoldFormatError(ValueError):
    """A .fold file is missing required keys or has an internally inconsistent shape."""


def validate(data: dict) -> None:
    """Raise FoldFormatError on structural problems worth catching before Stage 3 ever
    sees this data. Does not (and cannot, without the geometry these describe) check
    Kawasaki/Maekawa -- that is validity.py's job on the loaded OrigamiState, not this
    module's.
    """
    missing = [k for k in REQUIRED_KEYS if k not in data]
    if missing:
        raise FoldFormatError(f"missing required key(s): {missing}")

    n_vertices = len(data["vertices_coords"])
    for i, edge in enumerate(data["edges_vertices"]):
        if len(edge) != 2:
            raise FoldFormatError(f"edges_vertices[{i}] is not a pair: {edge}")
        for v in edge:
            if not 0 <= v < n_vertices:
                raise FoldFormatError(
                    f"edges_vertices[{i}] references vertex {v}, "
                    f"out of range [0, {n_vertices})"
                )

    assignments = data.get("edges_assignment")
    if assignments is not None:
        if len(assignments) != len(data["edges_vertices"]):
            raise FoldFormatError(
                f"edges_assignment has {len(assignments)} entries, "
                f"edges_vertices has {len(data['edges_vertices'])}"
            )
        bad = set(assignments) - VALID_ASSIGNMENTS
        if bad:
            raise FoldFormatError(f"invalid edges_assignment value(s): {bad}")

    faces = data.get("faces_vertices")
    if faces is not None:
        for i, face in enumerate(faces):
            for v in face:
                if not 0 <= v < n_vertices:
                    raise FoldFormatError(
                        f"faces_vertices[{i}] references vertex {v}, "
                        f"out of range [0, {n_vertices})"
                    )


def write_fold(data: dict, path: str, *, creator: str = "origami-ai-pipeline") -> None:
    """Serialise ``data`` (a FOLD-schema dict) to ``path`` as FOLD JSON.

    Fills in file_spec/file_creator if absent rather than requiring every caller to
    remember them; validates before writing so a malformed pattern fails here, at the
    stage-2/stage-3 boundary, rather than silently downstream inside Stage 3's search.
    """
    payload = dict(data)
    payload.setdefault("file_spec", CURRENT_FILE_SPEC)
    payload.setdefault("file_creator", creator)
    validate(payload)
    with open(path, "w") as fh:
        json.dump(payload, fh, indent=2)


def read_fold(path: str) -> dict:
    """Load and validate a .fold file. Raises FoldFormatError on structural problems."""
    with open(path) as fh:
        data = json.load(fh)
    validate(data)
    return data
