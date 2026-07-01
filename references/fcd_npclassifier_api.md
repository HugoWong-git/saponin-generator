# FCD Computation Notes

## Package
`pip install fcd` — version 1.2.2 installed.

## API Quirk (critical)
`fcd.get_predictions(model, smiles_list)` returns a **numpy ndarray** of activations (shape: [n_molecules, 512]), NOT a tuple of (mu, sigma).

**Correct usage:**
```python
import fcd
import numpy as np

ref_model = fcd.load_ref_model()
acts_a = fcd.get_predictions(ref_model, smiles_a)
acts_b = fcd.get_predictions(ref_model, smiles_b)

mu_a = np.mean(acts_a, axis=0)
sigma_a = np.cov(acts_a, rowvar=False)
mu_b = np.mean(acts_b, axis=0)
sigma_b = np.cov(acts_b, rowvar=False)

fcd_val = fcd.calculate_frechet_distance(mu_a, sigma_a, mu_b, sigma_b)
```

The naive `mu, sigma = get_predictions(...)` will raise `ValueError: too many values to unpack`.

## Training set reference
Use `data/saponin_train_46k_valid.smi` (45,966 molecules). For computational efficiency, take a random 10k subset as the FCD reference:
```python
rng = random.Random(42)
train_fcd = rng.sample(all_train_smiles, 10000)
```

## NPClassifier API
Endpoint: `https://npclassifier.gnps2.org/classify`
Method: GET with `smiles` query parameter
Rate limit: ~2 req/sec recommended
Response: `{"superclass_results": [...], "class_results": [...], "pathway_results": [...], "isglycoside": bool}`

Usage:
```python
import requests
r = requests.get("https://npclassifier.gnps2.org/classify", params={"smiles": "CCO"})
data = r.json()
print(data["superclass_results"])  # e.g. ["Triterpenoids"]
```