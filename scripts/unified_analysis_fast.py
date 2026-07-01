#!/usr/bin/env python
"""Fast unified analysis — subsamples large models, computes IC50 + PCA/UMAP."""
import csv, json, subprocess, sys, time, random, os
import numpy as np
import pandas as pd
import requests
from collections import Counter
from rdkit import Chem
from rdkit.Chem import AllChem
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap

ROOT = "."
rng = random.Random(42)
os.makedirs(f"{ROOT}/reports/figures", exist_ok=True)

MODELS = {
    "TL-E1": f"{ROOT}/samples/saponin_prior_46k_reg_epoch1_samples.csv",
    "TL-E4": f"{ROOT}/samples/saponin_prior_46k_reg_epoch4_samples.csv",
    "Generic-Prior": f"{ROOT}/samples/ic50_generic_prior_samples.csv",
    "RL-E4-V3": f"{ROOT}/samples/rl_v3_final_10k.csv",
    "RL-E1": f"{ROOT}/samples/rl_epoch1_10k.csv",
    "RL-Extreme": f"{ROOT}/samples/ic50_extreme_agent_samples.csv",
    "RL-Light-E1": f"{ROOT}/samples/saponin_light_epoch1_agent_samples.csv",
    "Generic-RL": f"{ROOT}/samples/ic50_generic_rl_agent_samples.csv",
}
MODELS = {k: v for k, v in MODELS.items() if os.path.exists(v)}

MAX_SAMPLE = 2000  # subsample to this for speed
color_map = {
    "TL-E1": "#3498db", "TL-E4": "#2980b9",
    "Generic-Prior": "#95a5a6",
    "RL-E4-V3": "#e74c3c", "RL-E1": "#2ecc71",
    "RL-Extreme": "#e67e22",
    "RL-Light-E1": "#1abc9c",
    "Generic-RL": "#9b59b6",
}

desc_names = ["MolWt","LogP","TPSA","NumHDonors","NumHAcceptors","NumRotatableBonds","NumRings","HeavyAtomCount","FractionCSP3"]
from rdkit.Chem import Descriptors, rdMolDescriptors
desc_funcs = [
    lambda m: Descriptors.MolWt(m), lambda m: Descriptors.MolLogP(m), lambda m: Descriptors.TPSA(m),
    lambda m: rdMolDescriptors.CalcNumHBD(m), lambda m: rdMolDescriptors.CalcNumHBA(m),
    lambda m: rdMolDescriptors.CalcNumRotatableBonds(m), lambda m: rdMolDescriptors.CalcNumRings(m),
    lambda m: m.GetNumHeavyAtoms(), lambda m: rdMolDescriptors.CalcFractionCSP3(m),
]

all_metrics = []
combined_fps = []
combined_descs = []
combined_labels = []
all_smiles_for_model = {}

for name, path in MODELS.items():
    print(f"\n{name}")
    smiles = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row.get("SMILES_state", 1)) == 1:
                smiles.append(row["SMILES"].strip())
    
    n_valid = len(smiles)
    total = 10000 if "50000" not in path else 50000
    total = 30000 if "30000" in path else total
    total = 15000 if "15000" in path else total
    validity = n_valid / total
    
    # Subsample for analysis
    sample = rng.sample(smiles, min(MAX_SAMPLE, len(smiles)))
    canon = []
    desc_vals = {n: [] for n in desc_names}
    fps_local = []
    
    for smi in sample:
        m = Chem.MolFromSmiles(smi)
        if m:
            cs = Chem.MolToSmiles(m, canonical=True)
            canon.append(cs)
            for n2, fn in zip(desc_names, desc_funcs):
                try: desc_vals[n2].append(fn(m))
                except: pass
            fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
            fps_local.append(fp)
    
    n_unique = len(canon)
    uniqueness = n_unique / len(sample) if len(sample) > 0 else 0
    
    # IC50 (on subsample)
    print(f"  IC50 scoring {n_unique} mols...", end=" ", flush=True)
    proc = subprocess.run(
        [sys.executable, f"{ROOT}/scripts/ic50_scorer.py"],
        input="\n".join(canon), capture_output=True, text=True, timeout=120
    )
    scores = np.array(json.loads(proc.stdout)["payload"]["predictions"])
    ic50_vals = np.exp(scores)
    print(f"mean={np.mean(ic50_vals):.2f}")
    
    metrics = {
        "model": name, "n_valid": n_valid, "total": total,
        "validity": round(validity, 4), "uniqueness": round(uniqueness, 4),
        "ic50_mean": round(float(np.mean(ic50_vals)), 2),
        "ic50_median": round(float(np.median(ic50_vals)), 2),
        "ic50_min": round(float(np.min(ic50_vals)), 2),
        "pct_lt_1uM": round(float(np.mean(ic50_vals<1)*100), 1),
        "pct_lt_2uM": round(float(np.mean(ic50_vals<2)*100), 1),
        "pct_lt_5uM": round(float(np.mean(ic50_vals<5)*100), 1),
    }
    for n2 in desc_names:
        v = np.array(desc_vals[n2])
        metrics[f"{n2}_mean"] = round(float(np.mean(v)), 1)
    all_metrics.append(metrics)
    
    # Store for DR
    combined_fps.append(np.array(fps_local))
    combined_descs.append(np.array([desc_vals[n] for n in desc_names]).T)
    combined_labels.extend([name] * len(fps_local))
    all_smiles_for_model[name] = (canon, scores, ic50_vals)

# Save metrics
df = pd.DataFrame(all_metrics)
df.to_csv(f"{ROOT}/metrics/unified_results.csv", index=False)
print(f"\nSaved metrics/unified_results.csv")
print(df[["model","validity","ic50_mean","ic50_median","ic50_min","pct_lt_1uM","pct_lt_2uM"]].to_string())

# ── Dimensionality Reduction ──
print("\n=== DR ===")
fp_matrix = np.vstack(combined_fps)
desc_matrix = combined_descs[0] if len(combined_descs) == 1 else np.vstack(combined_descs)
labels = np.array(combined_labels)

# PCA on descriptors
pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(StandardScaler().fit_transform(desc_matrix[:min(5000,len(desc_matrix))]))

# UMAP on descriptors
umap_model = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.3, random_state=42, verbose=False)
umap_coords = umap_model.fit_transform(StandardScaler().fit_transform(desc_matrix[:min(5000,len(desc_matrix))]))

# Plot
fig, axes = plt.subplots(1, 2, figsize=(16, 7))
fig.suptitle("Chemical Space of All RL Experiments", fontsize=16, y=0.98)

for ax, coords, title in [
    (axes[0], pca_coords, "PCA on RDKit Descriptors"),
    (axes[1], umap_coords, "UMAP on RDKit Descriptors"),
]:
    for model_name in np.unique(labels[:len(coords)]):
        mask = labels[:len(coords)] == model_name
        if np.sum(mask) == 0: continue
        idx = np.where(mask)[0][:min(np.sum(mask), len(coords))]
        ax.scatter(coords[idx[:len(idx)], 0], coords[idx[:len(idx)], 1],
                   c=color_map.get(model_name, "#333"),
                   label=model_name, s=5, alpha=0.5, linewidth=0)
    ax.set_title(title)
    ax.legend(markerscale=5, fontsize=7)

plt.tight_layout(rect=[0, 0, 1, 0.94])
plt.savefig(f"{ROOT}/reports/figures/unified_chemical_space.png", dpi=150, bbox_inches="tight")
print("Saved reports/figures/unified_chemical_space.png")

# IC50 bar chart
fig, ax = plt.subplots(figsize=(10, 5))
models = [m["model"] for m in all_metrics]
means = [m["ic50_mean"] for m in all_metrics]
colors = [color_map.get(m, "#333") for m in models]
bars = ax.bar(models, means, color=colors, alpha=0.8)
ax.set_ylabel("Mean IC50 (uM)")
ax.set_title("Predicted IC50 Across Models")
ax.set_xticklabels(models, rotation=30, ha="right")
for bar, v in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3, f"{v:.1f}",
            ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(f"{ROOT}/reports/figures/ic50_comparison.png", dpi=150)
print("Saved reports/figures/ic50_comparison.png")

# Validity chart
fig, ax = plt.subplots(figsize=(10, 5))
vals = [m["validity"]*100 for m in all_metrics]
bars = ax.bar(models, vals, color=colors, alpha=0.8)
ax.set_ylabel("Validity (%)")
ax.set_title("Validity Across Models")
ax.set_xticklabels(models, rotation=30, ha="right")
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{v:.1f}%",
            ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(f"{ROOT}/reports/figures/validity_comparison.png", dpi=150)
print("Saved reports/figures/validity_comparison.png")

print("\n=== ALL DONE ===")