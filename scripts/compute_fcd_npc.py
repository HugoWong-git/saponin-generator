#!/usr/bin/env python
"""Compute FCD and NPClassifier analysis for all 4 epoch priors."""
import sys, os, json, csv, time, random
import numpy as np
import pandas as pd
import requests
from rdkit import Chem
import fcd

ROOT = "."
SAMPLES_DIR = f"{ROOT}/samples"
METRICS_DIR = f"{ROOT}/metrics"
DATA_DIR = f"{ROOT}/data"
TRAINING_SMILES_FILE = f"{DATA_DIR}/saponin_train_46k_valid.smi"
EPOCHS = [1, 2, 3, 4]
NPC_API = "https://npclassifier.gnps2.org/classify"

# 1. Load training SMILES (canonical)
print("Loading training set...")
train_smiles_list = []
with open(TRAINING_SMILES_FILE) as f:
    for line in f:
        smi = line.strip()
        if smi:
            m = Chem.MolFromSmiles(smi)
            if m:
                train_smiles_list.append(Chem.MolToSmiles(m, canonical=True))

rng = random.Random(42)
if len(train_smiles_list) > 10000:
    train_fcd_sample = rng.sample(train_smiles_list, 10000)
else:
    train_fcd_sample = train_smiles_list
print(f"  Training set: {len(train_smiles_list)} canonical, using {len(train_fcd_sample)} for FCD")

# 2. Compute FCD
print("\nLoading ChemNet model...")
ref_model = fcd.load_ref_model()
print("  ChemNet loaded")

def compute_fcd(ref, smi_a, smi_b):
    acts_a = fcd.get_predictions(ref, smi_a)
    acts_b = fcd.get_predictions(ref, smi_b)
    mu_a = np.mean(acts_a, axis=0)
    sigma_a = np.cov(acts_a, rowvar=False)
    mu_b = np.mean(acts_b, axis=0)
    sigma_b = np.cov(acts_b, rowvar=False)
    return float(fcd.calculate_frechet_distance(mu_a, sigma_a, mu_b, sigma_b))

fcd_results = {}
for ep in EPOCHS:
    csv_path = f"{SAMPLES_DIR}/saponin_prior_46k_reg_epoch{ep}_samples.csv"
    gen_smiles = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            smi = row["SMILES"].strip()
            if int(row["SMILES_state"]) == 1:
                gen_smiles.append(smi)
    print(f"\nEpoch {ep}: FCD on {len(gen_smiles)} molecules...")
    fcd_results[ep] = compute_fcd(ref_model, gen_smiles, train_fcd_sample)
    print(f"  FCD = {fcd_results[ep]:.4f}")

print("\n=== FCD Results ===")
for ep in EPOCHS:
    print(f"  Epoch {ep}: FCD = {fcd_results[ep]:.4f}")

fcd_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_fcd.csv"
pd.DataFrame([{"epoch": ep, "FCD_vs_train": fcd_results[ep]} for ep in EPOCHS]).to_csv(fcd_csv, index=False)
print(f"Saved FCD to {fcd_csv}")

# 3. NPClassifier on a subset
print("\n\n=== NPClassifier ===")
npc_sample_size = 500
npc_all = {ep: {"superclass": [], "class": [], "pathway": []} for ep in EPOCHS}

def classify_one(smiles, retries=3):
    for a in range(retries):
        try:
            r = requests.get(NPC_API, params={"smiles": smiles}, timeout=30)
            if r.status_code == 200:
                return r.json()
        except:
            if a < retries - 1:
                time.sleep(2)
    return None

for ep in EPOCHS:
    csv_path = f"{SAMPLES_DIR}/saponin_prior_46k_reg_epoch{ep}_samples.csv"
    gen_smiles = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            smi = row["SMILES"].strip()
            if int(row["SMILES_state"]) == 1:
                gen_smiles.append(smi)
    sample = rng.sample(gen_smiles, min(npc_sample_size, len(gen_smiles)))
    print(f"\nEpoch {ep}: classifying {len(sample)} molecules...")
    ok = 0
    for i, smi in enumerate(sample):
        r = classify_one(smi)
        if r:
            ok += 1
            for k in ["superclass_results", "class_results", "pathway_results"]:
                if k in r and r[k]:
                    target = k.replace("_results", "")
                    npc_all[ep][target].extend(r[k])
        if (i+1) % 25 == 0:
            print(f"  {i+1}/{len(sample)} (ok={ok})", end="\r")
        time.sleep(0.5)
    print(f"\n  Done: {ok}/{len(sample)} classified")

# Summarize NPClassifier
npc_rows = []
for ep in EPOCHS:
    row = {"epoch": ep}
    for key in ["superclass", "class", "pathway"]:
        items = npc_all[ep][key]
        if items:
            from collections import Counter
            top = Counter(items).most_common(3)
            for name, cnt in top:
                row[f"{key}_{name[:20]}"] = round(cnt / len(items) * 100, 1)
    npc_rows.append(row)

npc_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_npclassifier.csv"
pd.DataFrame(npc_rows).to_csv(npc_csv, index=False)
print(f"\nSaved NPClassifier to {npc_csv}")
for row in npc_rows:
    print(f"\nEpoch {row['epoch']}:")
    for k, v in sorted(row.items()):
        if k != "epoch":
            print(f"  {k}: {v}%")

# 4. Combined metrics
basic = pd.read_csv(f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_basic.csv")
fcd_df = pd.read_csv(fcd_csv)
combined = basic.merge(fcd_df, on="epoch")
combined_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_combined.csv"
combined.to_csv(combined_csv, index=False)
print(f"\nSaved combined metrics to {combined_csv}")
cols = ["epoch", "validity", "uniqueness", "novelty", "FCD_vs_train", "FDD_vs_train", "mean_NLL"]
print("\n=== FINAL ===")
print(combined[cols].to_string(index=False))