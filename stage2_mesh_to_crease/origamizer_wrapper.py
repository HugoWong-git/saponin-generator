"""Mesh -> crease pattern, wrapping Origamizer (Demaine & Tachi, SoCG 2017).

STATUS: mesh preprocessing (decimation, OBJ export) is implemented and tested here.
The Origamizer invocation itself is NOT: research/build_order.md's M3 checklist names
"can Origamizer run headlessly?" as an unresolved load-bearing unknown to spike BEFORE
writing wrapper code, and web research done alongside this file confirms why -- the
tool is described as proprietary, non-commercial-licence-gated, primarily GUI-based,
"hasn't been updated for a long time," with no documented CLI found. Writing a
confident subprocess call against invented flags would misrepresent what is actually
known. See ORIGAMIZER_COMMAND_TEMPLATE below: this is the one thing the M3 spike still
needs to fill in.

Origamizer is never reimplemented (research/summary.md: "only component with a
correctness proof... never reimplement"). Everything here either prepares its input or
consumes its output; the algorithm itself stays a black box.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import trimesh
except ImportError as exc:  # pragma: no cover
    raise ImportError("origamizer_wrapper requires trimesh (pip install trimesh)") from exc

from .fold_io import read_fold, write_fold

# Filled in once the M3 spike determines how Origamizer is actually driven --
# e.g. a native Windows binary via subprocess, `wine Origamizer.exe {obj} {fold}`, or a
# batch script wrapping the GUI. None means "not configured"; every call path that would
# need it raises OrigamizerNotConfiguredError with this exact gap named, rather than
# guessing at flags.
ORIGAMIZER_COMMAND_TEMPLATE: list[str] | None = None

DEFAULT_MAX_FACES = 500  # placeholder pending the M3 checklist's "empirically find the
# face-count ceiling Origamizer tolerates" -- not measured, since that requires running
# the real tool. Override via --max-faces once that number is known.


class OrigamizerNotConfiguredError(RuntimeError):
    """Raised when Origamizer needs to run but ORIGAMIZER_COMMAND_TEMPLATE is unset.

    Distinct from a generic error so the top-level pipeline's --pattern bypass can
    catch it specifically, per the project's 'every stage boundary stays bypassable by
    a manual file drop' design.
    """


def decimate_mesh(mesh: trimesh.Trimesh, max_faces: int) -> trimesh.Trimesh:
    """Reduce ``mesh`` to at most ``max_faces`` faces via quadric decimation.

    Real logic, not a stub -- Stable Fast 3D output can run to tens of thousands of
    faces, and Origamizer's practical ceiling is almost certainly far lower (it adds
    substantial crease-pattern complexity per face). No-ops if already under the limit;
    simplify_quadric_decimation would otherwise raise on some inputs when asked to
    "reduce" to a face count it is already below.
    """
    if len(mesh.faces) <= max_faces:
        return mesh
    return mesh.simplify_quadric_decimation(face_count=max_faces)


def prepare_obj(mesh_path_or_mesh: str | trimesh.Trimesh, max_faces: int, obj_out: str) -> str:
    """Load (if needed), decimate, and export a mesh as OBJ -- Origamizer's documented
    input format. Returns ``obj_out``.
    """
    mesh = (
        mesh_path_or_mesh
        if isinstance(mesh_path_or_mesh, trimesh.Trimesh)
        else trimesh.load(mesh_path_or_mesh, force="mesh")
    )
    decimated = decimate_mesh(mesh, max_faces)
    decimated.export(obj_out)
    return obj_out


def _run_origamizer(obj_path: str, fold_out: str) -> None:
    if ORIGAMIZER_COMMAND_TEMPLATE is None:
        raise OrigamizerNotConfiguredError(
            "ORIGAMIZER_COMMAND_TEMPLATE is not set -- this is the M3 spike "
            "(research/build_order.md): confirm whether Origamizer can run headlessly "
            "(native binary / Wine / a batch-mode build) and what its actual CLI "
            "syntax is, then set ORIGAMIZER_COMMAND_TEMPLATE to a list like "
            "['wine', 'Origamizer.exe', '{obj}', '{fold}']. Until then, use the "
            "--fold bypass to supply a crease pattern produced some other way."
        )
    command = [
        part.format(obj=obj_path, fold=fold_out) for part in ORIGAMIZER_COMMAND_TEMPLATE
    ]
    if shutil.which(command[0]) is None:
        raise OrigamizerNotConfiguredError(
            f"configured Origamizer command '{command[0]}' not found on PATH"
        )
    subprocess.run(command, check=True)
    if not os.path.exists(fold_out):
        raise RuntimeError(
            f"Origamizer command exited successfully but did not produce {fold_out}"
        )


def mesh_to_crease_pattern(
    mesh_path: str | None = None,
    *,
    fold_path: str | None = None,
    max_faces: int = DEFAULT_MAX_FACES,
    work_dir: str | None = None,
) -> dict:
    """mesh -> FOLD-schema dict, the Stage 2 entry point.

    If ``fold_path`` is given, Origamizer is skipped entirely and that file is loaded
    directly -- the manual-bypass path, for a pattern produced by hand, by a different
    tool, or by a run of Origamizer done outside this wrapper. Otherwise decimates
    ``mesh_path``, exports it as OBJ, and invokes Origamizer (see _run_origamizer for
    why that call is not yet confirmed to work).
    """
    if fold_path is not None:
        return read_fold(fold_path)
    if mesh_path is None:
        raise ValueError("must supply either mesh_path or fold_path")

    work = Path(work_dir) if work_dir else Path(mesh_path).with_suffix("")
    work.mkdir(parents=True, exist_ok=True)
    obj_path = str(work / "decimated.obj")
    fold_out = str(work / "pattern.fold")

    prepare_obj(mesh_path, max_faces, obj_path)
    _run_origamizer(obj_path, fold_out)
    return read_fold(fold_out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mesh", nargs="?", default=None, help="input mesh path")
    ap.add_argument("--fold", default=None, help="bypass: load this .fold directly")
    ap.add_argument("--max-faces", type=int, default=DEFAULT_MAX_FACES)
    ap.add_argument("--output", default=None, help="where to write the resulting .fold")
    ap.add_argument("--work-dir", default=None)
    args = ap.parse_args()

    try:
        pattern = mesh_to_crease_pattern(
            args.mesh, fold_path=args.fold, max_faces=args.max_faces,
            work_dir=args.work_dir,
        )
    except OrigamizerNotConfiguredError as exc:
        print(f"stage 2 unavailable: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    if args.output:
        write_fold(pattern, args.output)
        print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
