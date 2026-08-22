"""Top-level orchestration: photo -> mesh -> crease pattern -> (fold sequence).

Chains stage1_image_to_mesh and stage2_mesh_to_crease for real. Stage 3 is
deliberately NOT wired in here as a working call, and that omission is the important
part of this file, not an afterthought:

Stage 3 (crease pattern -> fold sequence) is the pipeline's one novel component, and
this session's own investigation (see grid2d/RESULTS.md and OVERNIGHT_LOG.md) found
that the learned-policy approach does not yet work on 2-D patterns -- the trained
network never beat plain search, across every variant tried (reward shaping, rollout
exploration, compute scale). That is an open, unresolved result, not a finished module.
Calling into it here as if it were done would misrepresent the actual state of the
project. Once Stage 3 has a result worth shipping, wire it in where marked below.

Every boundary stays bypassable by a manual file drop, per research/README.md's stated
design ("every stage boundary stays bypassable by a manual file drop; it is the main
debugging tool"): --mesh skips Stage 1, --pattern skips Stage 1 and 2.
"""

from __future__ import annotations

import argparse
import sys

from stage1_image_to_mesh.image_to_mesh import SF3DNotAvailableError, image_to_mesh
from stage2_mesh_to_crease.origamizer_wrapper import (
    OrigamizerNotConfiguredError,
    mesh_to_crease_pattern,
)


def run(
    image: str | None = None,
    mesh: str | None = None,
    pattern: str | None = None,
    *,
    work_dir: str = "pipeline_work",
) -> dict:
    """Returns the FOLD-schema crease pattern dict. Exactly one of image/mesh/pattern
    should be the actual entry point; earlier ones are ignored once a later-stage
    input is supplied, mirroring the bypass semantics each stage wrapper already has.
    """
    if pattern is not None:
        print(f"[pipeline] bypassing stages 1-2, loading pattern directly: {pattern}")
        return mesh_to_crease_pattern(fold_path=pattern)

    if mesh is None:
        if image is None:
            raise ValueError("must supply one of image, mesh, or pattern")
        print(f"[pipeline] stage 1: {image} -> mesh")
        mesh_obj = image_to_mesh(image, output_path=f"{work_dir}/mesh.glb")
        mesh = f"{work_dir}/mesh.glb"
        print(f"[pipeline]   wrote {mesh}")
    else:
        print(f"[pipeline] bypassing stage 1, using supplied mesh: {mesh}")

    print(f"[pipeline] stage 2: {mesh} -> crease pattern")
    crease_pattern = mesh_to_crease_pattern(mesh, work_dir=work_dir)
    print(f"[pipeline]   crease pattern has {len(crease_pattern['edges_vertices'])} edges")

    print(
        "[pipeline] stage 3 (crease pattern -> fold sequence) is NOT wired in here. "
        "Its self-play approach is unresolved on 2-D patterns as of this session's "
        "investigation -- see grid2d/RESULTS.md and OVERNIGHT_LOG.md. Returning the "
        "crease pattern; fold-sequencing it is manual for now."
    )
    return crease_pattern


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--image", default=None)
    ap.add_argument("--mesh", default=None, help="bypass stage 1")
    ap.add_argument("--pattern", default=None, help="bypass stages 1 and 2")
    ap.add_argument("--work-dir", default="pipeline_work")
    args = ap.parse_args()

    try:
        run(args.image, args.mesh, args.pattern, work_dir=args.work_dir)
    except (SF3DNotAvailableError, OrigamizerNotConfiguredError) as exc:
        print(f"[pipeline] stopped: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except ValueError as exc:
        ap.error(str(exc))


if __name__ == "__main__":
    main()
