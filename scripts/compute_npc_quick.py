#!/usr/bin/env python
"""Quick NPClassifier analysis: 50 random molecules per epoch."""
import sys, os, json, csv, time, random
import numpy as np
import pandas as pd
import requests
from collections import Counter
from rdkit import Chem

ROOT = "."
SAMPLES_DIR = f"{ROOT}/samples"
METRICS_DIR = f"{ROOT}/metrics"
EPOCHS = [1, 2, 3, 4]
NPC_API = "https://npclassifier.gnps2.org/classify"
rng = random.Random(42)

def classify_one(smiles, retries=2):
    for a in range(retries):
        try:
            r = requests.get(NPC_API, params={"smiles": smiles}, timeout=15)
            if r.status_code == 200:
                return r.json()
        except:
            if a < retries - 1:
                time.sleep(1)
    return None

npc_all = {ep: {"superclass": [], "class": [], "pathway": []} for ep in EPOCHS}

for ep in EPOCHS:
    csv_path = f"{SAMPLES_DIR}/saponin_prior_46k_reg_epoch{ep}_samples.csv"
    smiles = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["SMILES_state"]) == 1:
                smiles.append(row["SMILES"].strip())
    sample = rng.sample(smiles, min(50, len(smiles)))
    print(f"Epoch {ep}: {len(sample)} molecules...", end=" ", flush=True)
    ok = 0
    for i, smi in enumerate(sample):
        r = classify_one(smi)
        if r:
            ok += 1
            for k in ["superclass_results", "class_results", "pathway_results"]:
                target = k.replace("_results", "")
                if k in r and r[k]:
                    npc_all[ep][target].extend(r[k])
        time.sleep(0.3)
    print(f"classified {ok}")

# Summary
npc_rows = []
for ep in EPOCHS:
    row = {"epoch": ep}
    for key in ["superclass", "class", "pathway"]:
        items = npc_all[ep][key]
        if items:
            top = Counter(items).most_common(5)
            for name, cnt in top:
                pct = round(cnt / len(items) * 100, 1)
                row[f"{key}_{name[:25]}"] = pct
    npc_rows.append(row)

npc_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_npclassifier.csv"
pd.DataFrame(npc_rows).to_csv(npc_csv, index=False)
print(f"\nSaved NPClassifier to {npc_csv}")

# Combined metrics
basic = pd.read_csv(f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_basic.csv")
fcd_df = pd.read_csv(f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_fcd.csv")
combined = basic.merge(fcd_df, on="epoch")
combined_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_combined.csv"
combined.to_csv(combined_csv, index=False)
print(f"Saved combined metrics to {combined_csv}")

print("\n=== FINAL METRICS ===")
cols = ["epoch", "validity", "novelty", "FCD_vs_train", "FDD_vs_train", "mean_NLL"]
print(combined[cols].to_string(index=False))

print("\n=== NPClassifier Summary ===")
for row in npc_rows:
    print(f"\nEpoch {row['epoch']}:")
    for k, v in sorted(row.items()):
        if k != "epoch" and v:
            print(f"  {k}: {v}%")