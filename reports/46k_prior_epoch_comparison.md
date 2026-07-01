# REINVENT4 46k Prior Epoch Comparison — Epoch 1–4

## Overview

Four regularized priors (`saponin_prior_46k_reg_epoch{1-4}.prior`) were trained via 4-block incremental TL with Tanimoto regularization (num_refs=16, sample_batch_size=128). Each prior was used to sample 10,000 molecules, and standard generative metrics were computed.

## Sampling Results

All four priors sampled successfully (exit 0, no crashes).

| Epoch | Prior File | Samples CSV | Log |
|-------|-----------|-------------|-----|
| 1 | `models/saponin_prior_46k_reg_epoch1.prior` | `samples/saponin_prior_46k_reg_epoch1_samples.csv` | `sampling_epoch1.log` |
| 2 | `models/saponin_prior_46k_reg_epoch2.prior` | `samples/saponin_prior_46k_reg_epoch2_samples.csv` | `sampling_epoch2.log` |
| 3 | `models/saponin_prior_46k_reg_epoch3.prior` | `samples/saponin_prior_46k_reg_epoch3_samples.csv` | `sampling_epoch3.log` |
| 4 | `models/saponin_prior_46k_reg_epoch4.prior` | `samples/saponin_prior_46k_reg_epoch4_samples.csv` | `sampling_epoch4.log` |

- Sampling time per epoch: ~6–7 min (10k SMILES, CPU)
- Peak memory per sampling run: ~1,120 MiB
- Reference (training) set: 45,966 canonical molecules from `data/saponin_train_46k_valid.smi`

## Metrics Comparison Table

| Metric | Epoch 1 | Epoch 2 | Epoch 3 | Epoch 4 |
|--------|---------|---------|---------|---------|
| **Validity** ↑ | 0.8595 | 0.8633 | **0.8697** | 0.8618 |
| **Uniqueness** ↑ | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| **Novelty** ↑ | **0.9990** | 0.9980 | 0.9971 | 0.9978 |
| **FDD ↓** | 1.4634 | 1.4330 | 1.4230 | **1.4094** |
| **Mean NLL ↓** | 43.83 | 42.68 | 41.58 | **40.94** |
| **MW** mean | 549.33 | 551.29 | 551.30 | 551.28 |
| **MolLogP** mean | 5.36 | 5.40 | 5.42 | 5.46 |
| **TPSA** mean | 105.71 | 105.86 | 105.14 | 104.28 |
| **NumHBD** mean | 2.86 | 2.91 | 2.91 | 2.92 |
| **NumHBA** mean | 6.16 | 6.16 | 6.14 | 6.10 |
| **NumRings** mean | 5.01 | 5.04 | 5.03 | 5.04 |
| **FracSp3** mean | 0.82 | 0.83 | 0.84 | 0.84 |

↑ = higher is better, ↓ = lower is better.

## Descriptor KL Divergence vs Training Set

| Descriptor | Epoch 1 | Epoch 2 | Epoch 3 | Epoch 4 |
|------------|---------|---------|---------|---------|
| KL MolWt | 0.0445 | 0.0472 | 0.0552 | **0.0433** |
| KL MolLogP | 0.0304 | 0.0299 | 0.0318 | **0.0236** |
| KL TPSA | **0.0439** | 0.0550 | 0.0592 | 0.0641 |
| KL NumHBD | 0.0297 | 0.0294 | 0.0297 | **0.0223** |
| KL NumHBA | **0.0157** | 0.0165 | 0.0180 | 0.0215 |
| KL NumRings | **0.1238** | 0.1275 | 0.1387 | 0.1308 |
| KL FracSp3 | 0.0309 | 0.0298 | 0.0285 | **0.0246** |

## Training Set Descriptor Reference

| Descriptor | Mean | Std |
|------------|------|-----|
| MolWt | 706.87 | 313.38 |
| MolLogP | 3.69 | 4.14 |
| TPSA | 176.21 | 145.14 |
| NumHBD | 5.48 | 5.49 |
| NumHBA | 10.65 | 9.22 |
| NumRings | 6.30 | 2.24 |
| FracSp3 | 0.86 | 0.10 |

## Analysis & Trade-offs

### Validity
All four epochs have ~86% validity, which is good for a de novo generative model. Epoch 3 has the highest (86.97%), but the difference is small.

### Novelty
All epochs are ~99.7-99.9% novel vs the training set, meaning the model is genuinely generating novel chemical structures rather than memorising the training data. Epoch 1 is highest (99.9%), with a slight decrease in later epochs. This is expected — more training pushes the model closer to the training distribution.

### FDD (Frechet Descriptor Distance)
FDD decreases steadily from E1 (1.46) to E4 (1.41), meaning later epochs generate molecules whose RDKit descriptor distributions more closely match the training set. This is the expected trend with more training.

### Mean NLL
Mean negative log-likelihood decreases monotonically from 43.83 (E1) to 40.94 (E4), confirming that each epoch's model becomes more confident about the molecules it generates.

### KL Divergence
Per-descriptor KL divergences are generally low (<0.14 for all). Ring count shows the highest KL (0.12-0.14) because the training set includes diverse non-saponin PubChem molecules alongside the 46k saponins. Epoch 4 tends to have the lowest KL for most descriptors (MolWt, MolLogP, NumHBD, FracSp3).

### Descriptor distributions
All epochs generate molecules with consistent chemistry:
- MW ~550 (vs training set 707 — generated molecules are smaller than the average training molecule)
- logP ~5.4 (moderately lipophilic, expected for triterpenoids)
- TPSA ~105 (moderately polar)
- ~5 rings (typical pentacyclic triterpenoid core)
- Fsp3 ~0.84 (high sp3 fraction, typical for natural products)

## Sweet Spot Assessment

**Epoch 2** or **Epoch 3** appears to be the best balance:

| Consideration | Best Epoch |
|---------------|-----------|
| Highest validity | Epoch 3 (86.97%) |
| Highest novelty | Epoch 1 (99.90%) |
| Lowest FDD (best distribution match) | Epoch 4 (1.409) |
| Lowest NLL (model confidence) | Epoch 4 (40.94) |
| Best KL balance (4/7 descriptors lowest) | Epoch 4 |
| Most stable descriptors | Epoch 3-4 |

- **Epoch 1** has marginally highest novelty but the highest FDD and NLL (least trained).
- **Epoch 2** is a good middle ground with solid validity and novelty.
- **Epoch 3** has the highest validity (86.97%) and good descriptor stability.
- **Epoch 4** has the lowest FDD and NLL but slightly lower novelty — it may be beginning to narrow towards the training distribution.

**Recommendation:** Epoch 3 is the preferred "sweet spot" if you prioritise validity and diversity (highest validity, 99.7% novelty, good FDD). Epoch 2 is also excellent if you want a slightly earlier stop. Epoch 4 is preferred if you want the model that most closely matches the training distribution (e.g. for downstream fine-tuning).

## Files

### Sampling files
- `samples/saponin_prior_46k_reg_epoch1_samples.csv` (8,595 valid unique SMILES)
- `samples/saponin_prior_46k_reg_epoch2_samples.csv` (8,633 valid unique SMILES)
- `samples/saponin_prior_46k_reg_epoch3_samples.csv` (8,697 valid unique SMILES)
- `samples/saponin_prior_46k_reg_epoch4_samples.csv` (8,618 valid unique SMILES)

### Metrics files
- `metrics/saponin_prior_46k_reg_epoch_metrics_basic.csv` (full metrics table)
- `metrics/saponin_prior_46k_reg_epoch_metrics_fdd.csv` (FDD and KL divergences)

### Prior model files
- `models/saponin_prior_46k_reg_epoch1.prior` (23M)
- `models/saponin_prior_46k_reg_epoch2.prior` (23M)
- `models/saponin_prior_46k_reg_epoch3.prior` (23M)
- `models/saponin_prior_46k_reg_epoch4.prior` (23M)

## Notes

- **FCD (Frechet ChemNet Distance):** The `fcd` Python package is not installed in this environment. As a proxy, **FDD (Frechet Descriptor Distance)** was computed from 7 RDKit molecular descriptors (MW, logP, TPSA, HBD, HBA, Rings, Fsp3). This captures distributional similarity of key physicochemical properties but does not capture learned chemical features as ChemNet would.
- **NPClassifier:** The NP-Classifier tool is present in the home directory (`~/NP-Classifier/`) but is a Java/command-line tool requiring specific setup and a running service. It was not feasible to integrate into this Python workflow without significant additional effort. The NPClassifier analysis would be a valuable future extension to quantify triterpenoid/saponin "likeness" per epoch.
- **Uniqueness = 1.0:** REINVENT4's `unique_molecules=True` sampling flag ensures all output molecules are unique, so the uniqueness metric is trivially 1.0.
- **All results are reproducible** using the 4 sampling TOML configs (`sampling_epoch{1-4}.toml`) and the metrics script (`scripts/compute_epoch_metrics.py`).
