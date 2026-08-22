# Stage 2 — mesh → crease pattern

Wraps [Origamizer](https://origami.c.u-tokyo.ac.jp/~tachi/software/) (Demaine & Tachi,
SoCG 2017) — the only pipeline component with a correctness *proof* (any polyhedron is
foldable). Per `research/summary.md`: never reimplement, only wrap.

## Status

**Mesh preprocessing is complete and tested for real. The Origamizer invocation itself
is not, and that's not an oversight — it's an accurately-reported unknown.**

`research/build_order.md`'s M3 checklist names "can Origamizer run headlessly?" as a
load-bearing unknown to spike *before* writing wrapper code. Web research done
alongside writing this module confirms why that caution was warranted: Origamizer is
described as proprietary, non-commercial-licence-gated software that "hasn't been
updated for a long time," primarily GUI-based, with no documented CLI found anywhere
searched. Writing a subprocess call against invented flags would have meant fabricating
an API. Instead:

| piece | status |
|---|---|
| mesh decimation (`decimate_mesh`) | real, tested — verified 1280→200 faces via `trimesh` + `fast_simplification`, still watertight |
| OBJ export (`prepare_obj`) | real, tested — Origamizer's documented input format |
| FOLD read/write (`fold_io.py`) | real, tested — 10 tests covering the schema (`vertices_coords`, `edges_vertices`, `edges_assignment`, `faces_vertices`) against the spec at https://github.com/edemaine/fold/blob/main/doc/spec.md |
| the manual `--fold` bypass | real, tested — the pipeline runs end to end on a hand-supplied `.fold` file with zero dependency on Origamizer |
| the actual Origamizer call | **not implemented.** `ORIGAMIZER_COMMAND_TEMPLATE` is `None`; any code path needing it raises `OrigamizerNotConfiguredError` naming the M3 spike explicitly, rather than guessing |

**What the M3 spike still needs to determine**, before `ORIGAMIZER_COMMAND_TEMPLATE`
can be filled in: whether Origamizer runs at all without its GUI (native binary,
Wine, or some batch-mode build), and if so, its actual command-line syntax. This has
to be done on a machine that can actually run Windows binaries or Wine — this sandbox
cannot.

## Dependencies

```
trimesh              # required; installed and used for real in this repo's tests
fast_simplification  # required by trimesh's simplify_quadric_decimation
```

## Tests

`python -m pytest stage2_mesh_to_crease/tests -q` — 16 tests: FOLD schema validation
and round-tripping, real mesh decimation and OBJ export, the `--fold` bypass working
with no Origamizer present, and `OrigamizerNotConfiguredError` firing correctly (rather
than a crash or a silent wrong answer) when Origamizer would be needed.
