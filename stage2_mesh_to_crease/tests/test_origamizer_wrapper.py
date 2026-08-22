"""origamizer_wrapper.py tests.

Decimation and OBJ export are real logic and tested for real. Origamizer invocation
itself cannot be tested here (no binary, no confirmed CLI) -- those tests confirm the
*honest failure*: OrigamizerNotConfiguredError, naming the M3 spike, not a crash or a
silently wrong result. The --fold bypass is tested for real since it needs no binary.
"""

from __future__ import annotations

import trimesh
import pytest

from stage2_mesh_to_crease.fold_io import write_fold
from stage2_mesh_to_crease.origamizer_wrapper import (
    OrigamizerNotConfiguredError,
    decimate_mesh,
    mesh_to_crease_pattern,
    prepare_obj,
)

SIMPLE_SQUARE = {
    "vertices_coords": [[0, 0], [1, 0], [1, 1], [0, 1]],
    "edges_vertices": [[0, 1], [1, 2], [2, 3], [3, 0]],
    "edges_assignment": ["B", "B", "B", "B"],
}


def test_decimate_reduces_face_count():
    mesh = trimesh.creation.icosphere(subdivisions=3)
    assert len(mesh.faces) == 1280
    out = decimate_mesh(mesh, max_faces=200)
    assert len(out.faces) <= 200


def test_decimate_is_a_noop_below_the_limit():
    mesh = trimesh.creation.box()
    out = decimate_mesh(mesh, max_faces=10_000)
    assert len(out.faces) == len(mesh.faces)


def test_prepare_obj_writes_a_loadable_file(tmp_path):
    mesh = trimesh.creation.icosphere(subdivisions=2)
    obj_path = str(tmp_path / "out.obj")
    prepare_obj(mesh, max_faces=100, obj_out=obj_path)
    reloaded = trimesh.load(obj_path, force="mesh")
    assert len(reloaded.faces) <= 100
    assert len(reloaded.faces) > 0


def test_fold_bypass_skips_origamizer_entirely(tmp_path):
    """The core promise: --fold works with no Origamizer binary anywhere on the
    machine, exercising the actual manual-bypass code path, not just the docstring."""
    fold_path = str(tmp_path / "manual.fold")
    write_fold(SIMPLE_SQUARE, fold_path)
    result = mesh_to_crease_pattern(fold_path=fold_path)
    assert result["edges_assignment"] == SIMPLE_SQUARE["edges_assignment"]


def test_missing_both_mesh_and_fold_is_a_clear_error():
    with pytest.raises(ValueError, match="mesh_path or fold_path"):
        mesh_to_crease_pattern()


def test_running_origamizer_without_config_names_the_m3_spike(tmp_path):
    mesh = trimesh.creation.box()
    mesh_path = str(tmp_path / "box.obj")
    mesh.export(mesh_path)
    with pytest.raises(OrigamizerNotConfiguredError, match="M3 spike"):
        mesh_to_crease_pattern(mesh_path, work_dir=str(tmp_path / "work"))
