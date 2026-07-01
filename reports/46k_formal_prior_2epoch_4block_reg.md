# Formal 46k Regularized Prior — 4 Epochs × 4-Block Incremental TL

## Starting Point

**Model:** `models/saponin_prior_block4.prior`
- This is the 46k incremental pure-NLL prior, produced by chaining 4 sequential TL runs (pure NLL, num_refs=0) over the 4 balanced blocks starting from the PubChem prior.

## Dataset

Source: `data/saponin_train_46k_valid.smi` (45,966 SMILES)

Split into 4 balanced blocks by deterministic shuffle (seed=12345):

| File | SMILES | Path |
|------|--------|------|
| Block 1 | 11,492 | `data/saponin_train_46k_block1.smi` |
| Block 2 | 11,492 | `data/saponin_train_46k_block2.smi` |
| Block 3 | 11,491 | `data/saponin_train_46k_block3.smi` |
| Block 4 | 11,491 | `data/saponin_train_46k_block4.smi` |
| Total | **45,966** | |

> **Note:** REINVENT4's built-in validity filter reduces these further during training. Actual valid SMILES read per block: ~9,526 (B1), ~9,607 (B2), ~9,524 (B3), ~9,557 (B4).

## TL Scheme — 4-Block-as-1-Epoch

Each "epoch" = training sequentially over blocks 1→2→3→4, chaining the output prior of each block as the input prior of the next.

- **Epoch 1:** block4.prior → B1 → B2 → B3 → B4 → epoch1.prior
- **Epoch 2:** epoch1.prior → B1 → B2 → B3 → B4 → epoch2.prior
- **Epoch 3:** epoch2.prior → B1 → B2 → B3 → B4 → epoch3.prior
- **Epoch 4:** epoch3.prior → B1 → B2 → B3 → B4 → epoch4.prior

## Hyperparameters (per block)

| Parameter | Value |
|-----------|-------|
| `num_epochs` | 1 |
| `save_every_n_epochs` | 1 |
| `batch_size` | 16 |
| `num_refs` | 16 |
| `sample_batch_size` | 128 |
| `pairs.type` | tanimoto |
| `pairs.lower_threshold` | 0.4 |
| `pairs.upper_threshold` | 0.8 |
| `pairs.min_cardinality` | 1 |
| `pairs.max_cardinality` | 199 |

## Config Files

| Block | Config | Log | Input Prior → Output Prior |
|-------|--------|-----|---------------------------|
| E1-B1 | `transfer_learning_saponin_46k_e1b1_reg.toml` | `tl_saponin_46k_e1b1_reg.log` | `block4.prior` → `tmp_e1b1.prior` |
| E1-B2 | `transfer_learning_saponin_46k_e1b2_reg.toml` | `tl_saponin_46k_e1b2_reg.log` | `tmp_e1b1.prior` → `tmp_e1b2.prior` |
| E1-B3 | `transfer_learning_saponin_46k_e1b3_reg.toml` | `tl_saponin_46k_e1b3_reg.log` | `tmp_e1b2.prior` → `tmp_e1b3.prior` |
| E1-B4 | `transfer_learning_saponin_46k_e1b4_reg.toml` | `tl_saponin_46k_e1b4_reg.log` | `tmp_e1b3.prior` → `epoch1.prior` |
| E2-B1 | `transfer_learning_saponin_46k_e2b1_reg.toml` | `tl_saponin_46k_e2b1_reg.log` | `epoch1.prior` → `tmp_e2b1.prior` |
| E2-B2 | `transfer_learning_saponin_46k_e2b2_reg.toml` | `tl_saponin_46k_e2b2_reg.log` | `tmp_e2b1.prior` → `tmp_e2b2.prior` |
| E2-B3 | `transfer_learning_saponin_46k_e2b3_reg.toml` | `tl_saponin_46k_e2b3_reg.log` | `tmp_e2b2.prior` → `tmp_e2b3.prior` |
| E2-B4 | `transfer_learning_saponin_46k_e2b4_reg.toml` | `tl_saponin_46k_e2b4_reg.log` | `tmp_e2b3.prior` → `epoch2.prior` |
| E3-B1 | `transfer_learning_saponin_46k_e3b1_reg.toml` | `tl_saponin_46k_e3b1_reg.log` | `epoch2.prior` → `tmp_e3b1.prior` |
| E3-B2 | `transfer_learning_saponin_46k_e3b2_reg.toml` | `tl_saponin_46k_e3b2_reg.log` | `tmp_e3b1.prior` → `tmp_e3b2.prior` |
| E3-B3 | `transfer_learning_saponin_46k_e3b3_reg.toml` | `tl_saponin_46k_e3b3_reg.log` | `tmp_e3b2.prior` → `tmp_e3b3.prior` |
| E3-B4 | `transfer_learning_saponin_46k_e3b4_reg.toml` | `tl_saponin_46k_e3b4_reg.log` | `tmp_e3b3.prior` → `epoch3.prior` |
| E4-B1 | `transfer_learning_saponin_46k_e4b1_reg.toml` | `tl_saponin_46k_e4b1_reg.log` | `epoch3.prior` → `tmp_e4b1.prior` |
| E4-B2 | `transfer_learning_saponin_46k_e4b2_reg.toml` | `tl_saponin_46k_e4b2_reg.log` | `tmp_e4b1.prior` → `tmp_e4b2.prior` |
| E4-B3 | `transfer_learning_saponin_46k_e4b3_reg.toml` | `tl_saponin_46k_e4b3_reg.log` | `tmp_e4b2.prior` → `tmp_e4b3.prior` |
| E4-B4 | `transfer_learning_saponin_46k_e4b4_reg.toml` | `tl_saponin_46k_e4b4_reg.log` | `tmp_e4b3.prior` → `epoch4.prior` |

All config files live in ``. All logs also in that directory.

## Runtime & Resource Notes

- **Environment:** Ubuntu 26.04 WSL2, Python 3.11.15, CPU-only (PyTorch), 16 GB RAM
- **Per-block runtime:** ~3–5 min for regularized blocks (varied from 2:50 to 5:06)
- **Peak memory:** ~3,650–3,700 MiB per block
- **Total runtime (all 16 blocks):** ~65 min wall time
- **No OOM / kill events** detected (dmesg clean)
- Block timing appeared to **decrease** in later epochs (E1: 3:30–5:06, E4: 2:51–4:04), suggesting the prior becomes more adapted.

## Output Models

| File | Size | Timestamp |
|------|------|-----------|
| `models/saponin_prior_46k_reg_epoch1.prior` | 23M | Jun 29 01:39 |
| `models/saponin_prior_46k_reg_epoch2.prior` | 23M | Jun 29 08:12 |
| `models/saponin_prior_46k_reg_epoch3.prior` | 23M | Jun 29 09:22 |
| `models/saponin_prior_46k_reg_epoch4.prior` | 23M | Jun 29 10:21 |

> **Final formal 46k regularized prior:**
> `models/saponin_prior_46k_reg_epoch4.prior`
> This model was trained with 4 epochs × 4 blocks (16 total TL steps) of regularized Tanimoto transfer learning over the full 46k saponin dataset, starting from the incremental pure-NLL block4 prior.
