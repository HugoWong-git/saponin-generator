"""Image -> 3D mesh, wrapping Stable Fast 3D (SF3D).

STATUS: wrapper code complete against SF3D's documented API; NOT executed against the
real model in this environment (no GPU here -- SF3D's reference implementation assumes
CUDA). Everything not touching SF3D itself (background removal, mesh post-processing,
the manual-bypass CLI shape) is implemented and covered by tests that do run here.

Per research/summary.md's decision log: Stable Fast 3D is reused as-is, never rebuilt,
because it is feedforward and therefore deterministic and reproducible -- the one
property that matters more than latency for this pipeline. This file is the wrap, not
a reimplementation.

Real API, confirmed against the project's README and run.py (Stability-AI/stable-fast-3d,
https://github.com/Stability-AI/stable-fast-3d):
    from sf3d.system import SF3D
    model = SF3D.from_pretrained(
        "stabilityai/stable-fast-3d", config_name="config.yaml", weight_name="model.safetensors"
    )
    mesh, glob_dict = model.run_image(image, bake_resolution=1024, remesh="none")

That two-line call is the only part of this file that cannot be verified without a GPU
and the model weights. It is isolated in _run_sf3d() below so it is a one-function
patch if the installed sf3d package's signature has since drifted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import trimesh
except ImportError as exc:  # pragma: no cover - exercised only when trimesh missing
    raise ImportError(
        "image_to_mesh requires trimesh (pip install trimesh). This is a real, "
        "lightweight dependency, unlike sf3d itself."
    ) from exc


class SF3DNotAvailableError(RuntimeError):
    """Raised when the sf3d package or a CUDA device is not available.

    This is the expected failure mode in a CPU-only environment. It is a distinct
    exception (not a bare ImportError) so callers -- notably the top-level pipeline's
    --mesh bypass -- can catch it specifically and fall back to a manual mesh, per the
    project's stated design: 'every stage boundary stays bypassable by a manual file
    drop.'
    """


def remove_background(image_path: str, out_path: str | None = None) -> str:
    """Background removal pre-step (M4 checklist item).

    Uses rembg if installed; this is a real, standard background-removal package
    (https://github.com/danielgatis/rembg), not a placeholder. If rembg is not
    installed, passes the image through unchanged with a warning -- SF3D expects a
    clean subject on a plain or transparent background, so skipping this step
    degrades reconstruction quality but does not make the pipeline fail outright.
    """
    out_path = out_path or str(Path(image_path).with_suffix(".nobg.png"))
    try:
        from rembg import remove
        from PIL import Image
    except ImportError:
        print(
            "WARNING: rembg not installed (pip install rembg); passing the image "
            "through without background removal. SF3D reconstruction quality will "
            "suffer on images with cluttered backgrounds.",
            file=sys.stderr,
        )
        return image_path

    with Image.open(image_path) as img:
        result = remove(img)
    result.save(out_path)
    return out_path


def _run_sf3d(image_path: str, bake_resolution: int, remesh: str):
    """The one call into SF3D itself. Isolated so it is the single patch point if the
    installed sf3d package's API has drifted from what is documented here.

    Raises SF3DNotAvailableError if the package is missing or no CUDA device is found,
    rather than letting an ImportError or a slow CPU fallback propagate raw.
    """
    try:
        import torch
    except ImportError as exc:
        raise SF3DNotAvailableError(
            "torch is not installed. SF3D needs it as a base dependency."
        ) from exc
    if not torch.cuda.is_available():
        raise SF3DNotAvailableError(
            "No CUDA device available. SF3D's reference implementation assumes GPU "
            "inference; this environment is CPU-only. Run this on a machine with a "
            "GPU, or use the --mesh bypass to skip stage 1 entirely with a "
            "hand-provided or externally-generated mesh."
        )
    try:
        from sf3d.system import SF3D
        from PIL import Image
    except ImportError as exc:
        raise SF3DNotAvailableError(
            "sf3d is not installed. Install per "
            "https://github.com/Stability-AI/stable-fast-3d (requires accepting the "
            "Stability AI community licence on Hugging Face for the model weights)."
        ) from exc

    model = SF3D.from_pretrained(
        "stabilityai/stable-fast-3d",
        config_name="config.yaml",
        weight_name="model.safetensors",
    )
    model.eval().cuda()
    with Image.open(image_path) as image:
        mesh, _glob_dict = model.run_image(
            image, bake_resolution=bake_resolution, remesh=remesh
        )
    return mesh


def image_to_mesh(
    image_path: str,
    output_path: str | None = None,
    *,
    remove_bg: bool = True,
    bake_resolution: int = 1024,
    remesh: str = "none",
) -> trimesh.Trimesh:
    """Photo -> trimesh.Trimesh, the interface named in research/build_order.md's M4
    checklist. Raises SF3DNotAvailableError if SF3D itself cannot run here; callers
    that want the bypass behaviour should catch that and substitute a manual mesh.
    """
    working_path = remove_background(image_path) if remove_bg else image_path
    raw_mesh = _run_sf3d(working_path, bake_resolution, remesh)

    if isinstance(raw_mesh, trimesh.Scene):
        mesh = trimesh.util.concatenate(
            [g for g in raw_mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
        )
    else:
        mesh = raw_mesh

    if output_path:
        mesh.export(output_path)
    return mesh


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", help="input image path")
    ap.add_argument("--output", default=None, help="output mesh path (.glb/.obj/...)")
    ap.add_argument("--no-remove-bg", action="store_true")
    ap.add_argument("--bake-resolution", type=int, default=1024)
    ap.add_argument("--remesh", default="none", choices=("none", "triangle", "quad"))
    args = ap.parse_args()

    output = args.output or str(Path(args.image).with_suffix(".glb"))
    try:
        image_to_mesh(
            args.image,
            output,
            remove_bg=not args.no_remove_bg,
            bake_resolution=args.bake_resolution,
            remesh=args.remesh,
        )
    except SF3DNotAvailableError as exc:
        print(f"stage 1 unavailable: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(f"wrote {output}")


if __name__ == "__main__":
    main()
