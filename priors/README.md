# Pre-trained Priors

Four epoch checkpoints (23 MB each) from the 46k 4-epoch × 4-block regularized transfer learning pipeline.

| File | Description |
|------|-------------|
| `saponin_prior_46k_reg_epoch1.prior` | Epoch 1 — early training |
| `saponin_prior_46k_reg_epoch2.prior` | Epoch 2 — continued |
| `saponin_prior_46k_reg_epoch3.prior` | Epoch 3 — best validity/novelty balance |
| `saponin_prior_46k_reg_epoch4.prior` | Epoch 4 — final, most specialised |

Use these with REINVENT4's sampling or as starting points for RL (DAP).

**Note:** You also need the original PubChem prior from REINVENT4 to use these (`reinvent_pubchem.prior` — download from the [REINVENT4 releases](https://github.com/MolecularAI/REINVENT4/releases) or train from scratch with the configs in `configs/tl/`).