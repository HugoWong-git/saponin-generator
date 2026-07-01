# IC50 Consensus Model Screening

## Model Location
`(your IC50 model path)`

### Files
- `screen_consensus.py` — main screening script
- `saved_models/consensus_top10_20260626_120216.joblib` — model bundle (10-model ensemble)
- `saved_models/feature_index_map.joblib` — feature index map for ECFP fingerprints

### Setup
```bash
pip install joblib catboost xgboost lightgbm scikit-learn
```

### Usage
```bash
# IC50 model path (not included in this repo)
mkdir -p screening_input

# Place your CSV (must have a "SMILES" column) at:
#   screening_input/Hermes_Screening_SMILES.csv

python screen_consensus.py \
  --input screening_input/Hermes_Screening_SMILES.csv \
  --smiles-col SMILES \
  --bundle saved_models/consensus_top10_20260626_120216.joblib \
  --feature-map saved_models/feature_index_map.joblib \
  --output-dir output
```

### Output CSV columns
- `SMILES` — original input SMILES
- `valid_smiles` — True/False (RDKit parse success)
- `ensemble_avg_prediction` — ln(IC50) averaged across 10 models
- `ensemble_std` — standard deviation across models
- `predicted_IC` — IC50 in µM (exp of avg_prediction)
- `IC_lower` / `IC_upper` — confidence interval
- `ranking` — rank by predicted_IC (lower IC50 = better rank)
- `final_cat_C1` through `final_cat_C10` — individual model predictions

### Completed Run
- Input: 33,982 unique SMILES from all 4 epoch priors
- Output: `output/Screening_TeroKit_V2.5_Triterpenoid_20260629_145846.csv`
- IC50 range: 1.56–105.36 µM, mean 13.81 µM
- Top 5 most potent: 1.56, 2.14, 2.17, 2.33, 2.45 µM