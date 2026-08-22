"""Tests for the parts of image_to_mesh.py that don't need a GPU or the sf3d package.

What's covered: the background-removal fallback, the SF3DNotAvailableError contract,
and the CLI's exit behaviour on that error. What's NOT covered, and can't be from this
sandbox: real SF3D inference. See _run_sf3d's docstring for why that call is isolated.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from stage1_image_to_mesh.image_to_mesh import (
    SF3DNotAvailableError,
    _run_sf3d,
    image_to_mesh,
    remove_background,
)


@pytest.fixture
def sample_image(tmp_path) -> str:
    path = tmp_path / "sample.png"
    Image.new("RGB", (32, 32), color=(200, 100, 50)).save(path)
    return str(path)


def test_remove_background_passes_through_without_rembg(sample_image, monkeypatch):
    """rembg is an optional dependency; its absence must degrade, not crash."""
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **kw):
        if name == "rembg":
            raise ImportError("simulated: rembg not installed")
        return real_import(name, *a, **kw)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    result = remove_background(sample_image)
    assert result == sample_image


def test_run_sf3d_raises_when_cuda_unavailable(sample_image):
    """This environment has no CUDA device -- confirms the real failure mode, not a
    simulated one."""
    import torch

    assert not torch.cuda.is_available(), (
        "this test assumes a CPU-only sandbox; if CUDA is now available here, "
        "the SF3DNotAvailableError path below is no longer what actually executes"
    )
    with pytest.raises(SF3DNotAvailableError, match="CUDA"):
        _run_sf3d(sample_image, bake_resolution=1024, remesh="none")


def test_image_to_mesh_propagates_sf3d_unavailable(sample_image):
    with pytest.raises(SF3DNotAvailableError):
        image_to_mesh(sample_image, remove_bg=False)


def test_cli_exits_nonzero_when_stage_unavailable(sample_image):
    """The --mesh bypass in pipeline.py depends on this exiting with a distinguishable
    non-zero code rather than a raw traceback."""
    result = subprocess.run(
        [sys.executable, "-m", "stage1_image_to_mesh.image_to_mesh", sample_image],
        cwd=Path(__file__).resolve().parents[2],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "stage 1 unavailable" in result.stderr
