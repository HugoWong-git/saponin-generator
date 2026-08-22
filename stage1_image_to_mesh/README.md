# Stage 1 — image → mesh

Wraps [Stable Fast 3D](https://github.com/Stability-AI/stable-fast-3d) (SF3D), per
`research/summary.md`'s decision to reuse it as-is: it is feedforward, hence
deterministic and reproducible, which matters more here than latency.

## Status

**Wrapper code complete; not executed against the real model in this environment.**
This sandbox is CPU-only (no `nvidia-smi`, `torch.cuda.is_available()` is `False`), and
SF3D's reference implementation assumes a CUDA device. Everything that doesn't need
SF3D itself is implemented for real and covered by tests that run here:

| piece | status |
|---|---|
| background removal (`rembg`) | real, with a documented graceful fallback if `rembg` isn't installed |
| the SF3D call itself | implemented per the package's documented API; isolated in one function (`_run_sf3d`) so it's a one-spot patch if the installed version's signature has drifted |
| `SF3DNotAvailableError` | real, tested — confirms the actual CPU-only failure mode in this sandbox, not a simulated one |
| CLI (`--output`, `--no-remove-bg`, `--bake-resolution`, `--remesh`) | real, tested |

Run `python -m stage1_image_to_mesh.image_to_mesh <image>` on a machine with a GPU and
the `sf3d` package installed to actually generate a mesh.

## Dependencies

```
trimesh          # required; installed and used for real in this repo's tests
rembg            # optional; background-removal pre-step degrades gracefully without it
sf3d             # required for real inference; needs a CUDA GPU and accepting the
                 # Stability AI community licence on Hugging Face for the model weights
torch            # sf3d's own dependency
```

## Tests

`python -m pytest stage1_image_to_mesh/tests -q` — covers the fallback path, the
error contract, and the CLI's exit behaviour. Does not and cannot cover real SF3D
inference from this sandbox.
