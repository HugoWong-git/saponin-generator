# 46k Pure NLL 4-Block Chain — Completed Run (2026-06-29)

Starting prior: `priors/reinvent_pubchem.prior`
Each block: 1 epoch, batch_size=16, num_refs=0 (pure NLL)

| Block | Config | Log | SMILES Read | Time | Output Prior |
|-------|--------|-----|-------------|------|-------------|
| 1 | `transfer_learning_saponin_block1_pure.toml` | `tl_saponin_block1_pure.log` | 9,526 | 3:30 | `models/saponin_prior_block1.prior` (23M) |
| 2 | `transfer_learning_saponin_block2_pure.toml` | `tl_saponin_block2_pure.log` | 9,607 | 3:39 | `models/saponin_prior_block2.prior` (23M) |
| 3 | `transfer_learning_saponin_block3_pure.toml` | `tl_saponin_block3_pure.log` | 9,524 | 3:37 | `models/saponin_prior_block3.prior` (23M) |
| 4 | `transfer_learning_saponin_block4_pure.toml` | `tl_saponin_block4_pure.log` | 9,557 | 3:31 | `models/saponin_prior_block4.prior` (23M) |

Total wall time: ~14 min. Peak memory: ~1,300–1,450 MiB per block.

**Final prior:** `models/saponin_prior_block4.prior`