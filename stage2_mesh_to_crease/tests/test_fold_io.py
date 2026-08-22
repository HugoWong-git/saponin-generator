"""fold_io.py tests -- pure format logic, no external tools needed."""

from __future__ import annotations

import json

import pytest

from stage2_mesh_to_crease.fold_io import FoldFormatError, read_fold, validate, write_fold

SIMPLE_SQUARE = {
    "vertices_coords": [[0, 0], [1, 0], [1, 1], [0, 1]],
    "edges_vertices": [[0, 1], [1, 2], [2, 3], [3, 0], [0, 2]],
    "edges_assignment": ["B", "B", "B", "B", "M"],
    "faces_vertices": [[0, 1, 2], [0, 2, 3]],
}


def test_valid_pattern_passes():
    validate(SIMPLE_SQUARE)


def test_round_trip(tmp_path):
    path = str(tmp_path / "square.fold")
    write_fold(SIMPLE_SQUARE, path)
    loaded = read_fold(path)
    assert loaded["vertices_coords"] == SIMPLE_SQUARE["vertices_coords"]
    assert loaded["edges_assignment"] == SIMPLE_SQUARE["edges_assignment"]
    assert loaded["file_spec"] == 1.1
    assert loaded["file_creator"] == "origami-ai-pipeline"


def test_write_produces_valid_json(tmp_path):
    path = str(tmp_path / "square.fold")
    write_fold(SIMPLE_SQUARE, path)
    with open(path) as fh:
        json.load(fh)  # must not raise


def test_missing_required_key_rejected():
    bad = {"edges_vertices": [[0, 1]]}
    with pytest.raises(FoldFormatError, match="vertices_coords"):
        validate(bad)


def test_out_of_range_edge_vertex_rejected():
    bad = {
        "vertices_coords": [[0, 0], [1, 0]],
        "edges_vertices": [[0, 5]],
    }
    with pytest.raises(FoldFormatError, match="out of range"):
        validate(bad)


def test_edge_not_a_pair_rejected():
    bad = {
        "vertices_coords": [[0, 0], [1, 0]],
        "edges_vertices": [[0, 1, 1]],
    }
    with pytest.raises(FoldFormatError, match="not a pair"):
        validate(bad)


def test_assignment_length_mismatch_rejected():
    bad = {
        "vertices_coords": [[0, 0], [1, 0], [1, 1]],
        "edges_vertices": [[0, 1], [1, 2]],
        "edges_assignment": ["M"],
    }
    with pytest.raises(FoldFormatError, match="edges_assignment"):
        validate(bad)


def test_invalid_assignment_letter_rejected():
    bad = {
        "vertices_coords": [[0, 0], [1, 0]],
        "edges_vertices": [[0, 1]],
        "edges_assignment": ["X"],
    }
    with pytest.raises(FoldFormatError, match="invalid edges_assignment"):
        validate(bad)


def test_out_of_range_face_vertex_rejected():
    bad = {
        "vertices_coords": [[0, 0], [1, 0], [1, 1]],
        "edges_vertices": [[0, 1]],
        "faces_vertices": [[0, 1, 9]],
    }
    with pytest.raises(FoldFormatError, match="faces_vertices"):
        validate(bad)


def test_read_rejects_malformed_file(tmp_path):
    path = tmp_path / "bad.fold"
    path.write_text(json.dumps({"edges_vertices": []}))
    with pytest.raises(FoldFormatError):
        read_fold(str(path))
