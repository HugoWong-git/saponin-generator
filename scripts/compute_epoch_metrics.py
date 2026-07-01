#!/usr/bin/env python
"""Compute comprehensive evaluation metrics for 4 epoch priors.
Metrics per epoch:
  - Sampled count, valid count, unique count
  - Validity, Uniqueness (post-filter), Novelty vs training set
  - RDKit descriptor means (MW, logP, TPSA, HBD, HBA, Rings, Fsp3)
  - Frechet Descriptor Distance (FDD) as FCD proxy
  - KL divergence per descriptor vs training set
"""
import sys, os, json, csv
import numpy as np
import pandas as pd
from collections import Counter
from scipy.spatial.distance import jensenshannon
from scipy.stats import entropy, gaussian_kde
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

ROOT = "."
SAMPLES_DIR = f"{ROOT}/samples"
METRICS_DIR = f"{ROOT}/metrics"
DATA_DIR = f"{ROOT}/data"
TRAINING_SMILES_FILE = f"{DATA_DIR}/saponin_train_46k_valid.smi"

EPOCHS = [1, 2, 3, 4]
DESCRIPTOR_NAMES = ["MolWt", "MolLogP", "TPSA", "NumHBD", "NumHBA", "NumRings", "FracSp3"]
DESCRIPTOR_FUNCS = [
    lambda m: Descriptors.MolWt(m),
    lambda m: Descriptors.MolLogP(m),
    lambda m: Descriptors.TPSA(m),
    lambda m: rdMolDescriptors.CalcNumHBD(m),
    lambda m: rdMolDescriptors.CalcNumHBA(m),
    lambda m: rdMolDescriptors.CalcNumRings(m),
    lambda m: rdMolDescriptors.CalcFractionCSP3(m),
]

# ---- 1. Load training set (canonical) ----
print("Loading training set...")
train_smiles = set()
with open(TRAINING_SMILES_FILE) as f:
    for line in f:
        smi = line.strip()
        if smi:
            m = Chem.MolFromSmiles(smi)
            if m:
                train_smiles.add(Chem.MolToSmiles(m, canonical=True))
print(f"  Training set: {len(train_smiles)} canonical unique molecules")

# ---- 2. Compute training set descriptor distributions ----
print("Computing training set descriptors...")
train_descs = {n: [] for n in DESCRIPTOR_NAMES}
for smi in train_smiles:
    m = Chem.MolFromSmiles(smi)
    if m:
        for name, func in zip(DESCRIPTOR_NAMES, DESCRIPTOR_FUNCS):
            train_descs[name].append(func(m))
train_desc_stats = {}
for name in DESCRIPTOR_NAMES:
    vals = np.array(train_descs[name])
    train_desc_stats[name] = {"mean": float(np.mean(vals)), "std": float(np.std(vals))}

# ---- 3. Metrics per epoch ----
results = []
for ep in EPOCHS:
    print(f"\n=== Epoch {ep} ===")
    csv_path = f"{SAMPLES_DIR}/saponin_prior_46k_reg_epoch{ep}_samples.csv"
    
    # Read sampled SMILES
    total_sampled = 10000
    valid_smiles = []
    nlls = []
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            smi = row["SMILES"].strip()
            state = int(row["SMILES_state"])
            nll = float(row["NLL"])
            if state == 1:  # VALID
                valid_smiles.append(smi)
                nlls.append(nll)
    
    n_valid = len(valid_smiles)
    validity = n_valid / total_sampled
    
    print(f"  Sampled: {total_sampled}, Valid: {n_valid}, Validity: {validity:.4f}")
    
    # Canonicalize for uniqueness
    canon_smiles = set()
    for smi in valid_smiles:
        m = Chem.MolFromSmiles(smi)
        if m:
            canon_smiles.add(Chem.MolToSmiles(m, canonical=True))
    
    n_unique = len(canon_smiles)
    uniqueness = n_unique / n_valid if n_valid > 0 else 0
    
    print(f"  Unique canonical: {n_unique}, Uniqueness: {uniqueness:.4f}")
    
    # Novelty vs training set
    novel = canon_smiles - train_smiles
    n_novel = len(novel)
    novelty = n_novel / n_unique if n_unique > 0 else 0
    print(f"  Novel: {n_novel}, Novelty: {novelty:.4f}")
    
    # Compute descriptors
    desc_vals = {name: [] for name in DESCRIPTOR_NAMES}
    for smi in canon_smiles:
        m = Chem.MolFromSmiles(smi)
        if m:
            for name, func in zip(DESCRIPTOR_NAMES, DESCRIPTOR_FUNCS):
                try:
                    desc_vals[name].append(func(m))
                except:
                    pass
    
    desc_stats = {}
    kl_divs = {}
    fdd_components = []
    
    for name in DESCRIPTOR_NAMES:
        vals = np.array(desc_vals[name])
        desc_stats[name] = {
            "mean": float(np.mean(vals)),
            "std": float(np.std(vals)),
            "p5": float(np.percentile(vals, 5)),
            "p95": float(np.percentile(vals, 95)),
        }
        
        # KL divergence (approximated via binned histogram)
        train_vals = np.array(train_descs[name])
        all_vals = np.concatenate([train_vals, vals])
        bins = np.linspace(np.percentile(all_vals, 1), np.percentile(all_vals, 99), 51)
        
        train_hist, _ = np.histogram(train_vals, bins=bins, density=True)
        samp_hist, _ = np.histogram(vals, bins=bins, density=True)
        
        # Add small epsilon to avoid log(0)
        train_hist = train_hist + 1e-10
        samp_hist = samp_hist + 1e-10
        train_hist /= train_hist.sum()
        samp_hist /= samp_hist.sum()
        
        kl = entropy(samp_hist, train_hist)
        kl_divs[name] = float(kl)
        
        # FDD component: Frechet distance for a single dimension
        mu_diff = np.mean(vals) - np.mean(train_vals)
        var_train = np.var(train_vals)
        var_samp = np.var(vals)
        fdd_c = (mu_diff**2 + var_samp + var_train - 2 * np.sqrt(var_samp * var_train)) / (var_train + 1e-10)
        fdd_components.append(0.5 * fdd_c)
    
    fdd = sum(fdd_components)
    
    # Mean NLL
    mean_nll = float(np.mean(nlls)) if nlls else 0
    
    row = {
        "epoch": ep,
        "total_sampled": total_sampled,
        "n_valid": n_valid,
        "validity": round(validity, 4),
        "n_unique": n_unique,
        "uniqueness": round(uniqueness, 4),
        "n_novel": n_novel,
        "novelty": round(novelty, 4),
        "mean_NLL": round(mean_nll, 2),
        "FDD_vs_train": round(fdd, 4),
    }
    for name in DESCRIPTOR_NAMES:
        row[f"{name}_mean"] = round(desc_stats[name]["mean"], 2)
        row[f"{name}_std"] = round(desc_stats[name]["std"], 2)
        row[f"KL_{name}"] = round(kl_divs[name], 4)
    
    results.append(row)

# Save basic metrics
df = pd.DataFrame(results)
basic_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_basic.csv"
df.to_csv(basic_csv, index=False)
print(f"\nSaved basic metrics to {basic_csv}")

# Save FDD + descriptor table
fdd_csv = f"{METRICS_DIR}/saponin_prior_46k_reg_epoch_metrics_fdd.csv"
fdd_cols = ["epoch", "FDD_vs_train", "mean_NLL"] + [f"KL_{n}" for n in DESCRIPTOR_NAMES]
df[fdd_cols].to_csv(fdd_csv, index=False)
print(f"Saved FDD metrics to {fdd_csv}")

print("\n=== FINAL SUMMARY TABLE ===")
summary_cols = ["epoch", "validity", "uniqueness", "novelty", "FDD_vs_train", "mean_NLL",
                "MolWt_mean", "MolLogP_mean", "TPSA_mean", "NumHBD_mean", "NumHBA_mean",
                "NumRings_mean", "FracSp3_mean"]
print(df[summary_cols].to_string(index=False))

print(f"\nTraining set descriptor stats:")
for name in DESCRIPTOR_NAMES:
    s = train_desc_stats[name]
    print(f"  {name}: mean={s['mean']:.2f}, std={s['std']:.2f}")