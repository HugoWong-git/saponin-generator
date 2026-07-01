#!/usr/bin/env python
"""
Unified analysis of all RL experiments (Plans B, C, D) + baselines.
Computes per-model metrics, NPClassifier, and dimensionality reduction plots.
"""
import csv, json, subprocess, sys, time, random, os, re
import numpy as np
import pandas as pd
import requests
from collections import Counter, defaultdict
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors, AllChem, DataStructs
from rdkit.Chem import rdFingerprintGenerator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
import umap

ROOT = "."
NPC_API = "https://npclassifier.gnps2.org/classify"
rng = random.Random(42)
os.makedirs(f"{ROOT}/reports/figures", exist_ok=True)

# ── Define all models ──────────────────────────────────────────────────
MODELS = {
    "TL-E1":     f"{ROOT}/samples/saponin_prior_46k_reg_epoch1_samples.csv",
    "TL-E4":     f"{ROOT}/samples/saponin_prior_46k_reg_epoch4_samples.csv",
    "RL-E4-V3":  f"{ROOT}/samples/rl_v3_final_10k.csv",
    "RL-E1":     f"{ROOT}/samples/rl_epoch1_10k.csv",
    "RL-Extreme":f"{ROOT}/samples/ic50_extreme_agent_samples.csv",
    "RL-Light-E1":f"{ROOT}/samples/saponin_light_epoch1_agent_samples.csv",
    "Generic-Prior":f"{ROOT}/samples/ic50_generic_prior_samples.csv",
    "Generic-RL":f"{ROOT}/samples/ic50_generic_rl_agent_samples.csv",
}
# Filter to existing files
MODELS = {k: v for k, v in MODELS.items() if os.path.exists(v)}

desc_names = ["MolWt","LogP","TPSA","NumHDonors","NumHAcceptors","NumRotatableBonds","NumRings","HeavyAtomCount","FractionCSP3"]
desc_funcs = [
    lambda m: Descriptors.MolWt(m), lambda m: Descriptors.MolLogP(m), lambda m: Descriptors.TPSA(m),
    lambda m: rdMolDescriptors.CalcNumHBD(m), lambda m: rdMolDescriptors.CalcNumHBA(m),
    lambda m: rdMolDescriptors.CalcNumRotatableBonds(m), lambda m: rdMolDescriptors.CalcNumRings(m),
    lambda m: m.GetNumHeavyAtoms(), lambda m: rdMolDescriptors.CalcFractionCSP3(m),
]

# Training set for novelty
train = set()
with open(f"{ROOT}/data/saponin_train_46k_valid.smi") as f:
    for line in f:
        s = line.strip()
        if s:
            m = Chem.MolFromSmiles(s)
            if m: train.add(Chem.MolToSmiles(m, canonical=True))

# ── Step 1: Per-model metrics ──────────────────────────────────────────
all_metrics = {}
all_mols = {}  # model_name -> (canon_list, fp_matrix, desc_matrix)

for name, path in MODELS.items():
    print(f"\n{'='*60}\n{name}\n{'='*60}")
    smiles = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row.get("SMILES_state", 1)) == 1:
                smiles.append(row["SMILES"].strip())
    
    n_valid = len(smiles)
    total = 10000  # approximate
    validity = n_valid / total if total > 0 else 0
    
    # Canonicalize + descriptors + fingerprints
    canon = []
    desc_vals = {n: [] for n in desc_names}
    fps = []
    
    for smi in smiles:
        m = Chem.MolFromSmiles(smi)
        if m:
            cs = Chem.MolToSmiles(m, canonical=True)
            if cs not in [c for c in canon]:  # keep unique
                canon.append(cs)
                for n2, fn in zip(desc_names, desc_funcs):
                    try: desc_vals[n2].append(fn(m))
                    except: pass
                # ECFP4 fingerprint
                fp = AllChem.GetMorganFingerprintAsBitVect(m, 2, nBits=2048)
                fps.append(fp)
    
    n_unique = len(canon)
    uniqueness = n_unique / n_valid if n_valid > 0 else 0
    novel_set = set(canon) - train
    novelty = len(novel_set) / n_unique if n_unique > 0 else 0
    
    print(f"  Valid: {n_valid}, Unique: {n_unique}, Validity: {validity:.4f}, Uniqueness: {uniqueness:.4f}, Novelty: {novelty:.4f}")
    
    # IC50 scoring
    print(f"  IC50 scoring {n_unique} molecules...", end=" ", flush=True)
    proc = subprocess.run(
        [sys.executable, f"{ROOT}/scripts/ic50_scorer.py"],
        input="\n".join(canon), capture_output=True, text=True, timeout=300
    )
    scores = np.array(json.loads(proc.stdout)["payload"]["predictions"])
    ic50_vals = np.exp(scores)
    print(f"mean={np.mean(ic50_vals):.2f} uM, med={np.median(ic50_vals):.2f}")
    
    metrics = {
        "model": name, "n_valid": n_valid, "n_unique": n_unique,
        "validity": round(validity, 4), "uniqueness": round(uniqueness, 4),
        "novelty": round(novelty, 4),
        "ic50_mean": round(float(np.mean(ic50_vals)), 2),
        "ic50_median": round(float(np.median(ic50_vals)), 2),
        "ic50_min": round(float(np.min(ic50_vals)), 2),
        "pct_lt_0.1uM": round(float(np.mean(ic50_vals<0.1)*100), 1),
        "pct_lt_0.5uM": round(float(np.mean(ic50_vals<0.5)*100), 1),
        "pct_lt_1uM": round(float(np.mean(ic50_vals<1)*100), 1),
        "pct_lt_2uM": round(float(np.mean(ic50_vals<2)*100), 1),
        "pct_lt_5uM": round(float(np.mean(ic50_vals<5)*100), 1),
        "pct_lt_10uM": round(float(np.mean(ic50_vals<10)*100), 1),
    }
    for n2 in desc_names:
        v = np.array(desc_vals[n2])
        metrics[f"{n2}_mean"] = round(float(np.mean(v)), 1)
        metrics[f"{n2}_std"] = round(float(np.std(v)), 1)
    
    all_metrics[name] = metrics
    all_mols[name] = (canon, np.array(fps), np.array([desc_vals[n] for n in desc_names]).T)

# Save metrics table
# Sort rows: TL first, then RL
ordered = ["TL-E1", "TL-E4", "Generic-Prior", "RL-E4-V3", "RL-E1", "RL-Extreme", "RL-Light-E1", "Generic-RL"]
ordered = [m for m in ordered if m in all_metrics]
metrics_df = pd.DataFrame([all_metrics[m] for m in ordered])
metrics_csv = f"{ROOT}/metrics/unified_results.csv"
metrics_df.to_csv(metrics_csv, index=False)
print(f"\nSaved: {metrics_csv}")

# ── Step 2: NPClassifier on subset ──
print("\n=== NPClassifier ===")
npc_results = {}
for name, path in MODELS.items():
    canon = all_mols[name][0]
    sample = rng.sample(canon, min(100, len(canon)))
    print(f"{name}: classifying {len(sample)}...", end=" ", flush=True)
    npc = {"superclass": [], "class": [], "pathway": []}
    ok = 0
    for i, s in enumerate(sample):
        for a in range(2):
            try:
                r = requests.get(NPC_API, params={"smiles": s}, timeout=10)
                if r.status_code == 200:
                    ok += 1
                    for k in ["superclass_results","class_results","pathway_results"]:
                        t = k.replace("_results","")
                        if k in r and r[k]: npc[t].extend(r[k])
                    break
            except: time.sleep(0.5)
        time.sleep(0.2)
    print(f"ok={ok}")
    npc_results[name] = {k: Counter(v).most_common(5) for k, v in npc.items()}
    for key in ["superclass", "class"]:
        items = npc[key]
        if items:
            top = [(n, round(c/len(items)*100,1)) for n,c in Counter(items).most_common(3)]
            print(f"  {key}: {top}")

npc_json = f"{ROOT}/metrics/unified_npc.json"
with open(npc_json, "w") as f:
    json.dump({k: {k2: list(v2) for k2, v2 in v.items()} for k, v in npc_results.items()}, f, indent=2)
print(f"Saved: {npc_json}")

# ── Step 3: Dimensionality reduction ──
print("\n=== Dimensionality Reduction ===")

# Combine all molecules into one matrix with labels
all_mol_list = []
all_labels = []
all_fp_list = []
all_desc_list = []

for name in ordered:
    canon, fps, descs = all_mols[name]
    n = len(canon)
    all_mol_list.extend(canon)
    all_labels.extend([name] * n)
    all_fp_list.append(fps)
    all_desc_list.append(descs)

# Combined fingerprint matrix (stack sparse)
# Use subset since full may be large
max_per_model = 2000
combined_fps = []
combined_descs = []
combined_labels = []

for name in ordered:
    canon, fps, descs = all_mols[name]
    n = min(len(canon), max_per_model)
    if n == 0: continue
    idx = rng.sample(range(len(canon)), n)
    combined_fps.append(fps[idx])
    combined_descs.append(descs[idx])
    combined_labels.extend([name] * n)

fp_matrix = np.vstack(combined_fps)
desc_matrix = np.vstack(combined_descs)
labels = np.array(combined_labels)

print(f"Combined: {len(labels)} molecules from {len(ordered)} models")

# Scale descriptors
scaler = StandardScaler()
desc_scaled = scaler.fit_transform(desc_matrix)

# PCA on descriptors
pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(desc_scaled)
print(f"PCA variance: {pca.explained_variance_ratio_[0]:.3f}, {pca.explained_variance_ratio_[1]:.3f}")

# UMAP on descriptors
umap_model = umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.3, random_state=42)
umap_desc = umap_model.fit_transform(desc_scaled)
print("UMAP (descriptors) done")

# PCA on ECFP (using PCA to reduce 2048 bits first)
from sklearn.decomposition import TruncatedSVD
svd = TruncatedSVD(n_components=50, random_state=42)
fp_50 = svd.fit_transform(fp_matrix)
pca_fp = PCA(n_components=2, random_state=42)
fp_pca = pca_fp.fit_transform(fp_50)
print(f"FP PCA variance: {pca_fp.explained_variance_ratio_[0]:.3f}, {pca_fp.explained_variance_ratio_[1]:.3f}")

# UMAP on fingerprints
umap_fp = umap.UMAP(n_components=2, n_neighbors=15, min_dist=0.1, random_state=42)
fp_umap = umap_fp.fit_transform(fp_50)
print("UMAP (fingerprints) done")

# Colors for models
color_map = {
    "TL-E1": "#3498db", "TL-E4": "#2980b9",
    "Generic-Prior": "#95a5a6",
    "RL-E4-V3": "#e74c3c", "RL-E1": "#2ecc71",
    "RL-Extreme": "#e67e22",
    "RL-Light-E1": "#1abc9c",
    "Generic-RL": "#9b59b6",
}

# ── Plot 1: PCA (descriptors) ──
fig, axes = plt.subplots(2, 2, figsize=(16, 14))
fig.suptitle("Chemical Space of All RL Experiments", fontsize=16, y=0.98)

for ax, coords, method, space in [
    (axes[0,0], pca_coords, "PCA", "descriptors"),
    (axes[0,1], umap_desc, "UMAP", "descriptors"),
    (axes[1,0], fp_pca, "PCA", "ECFP4 fingerprints"),
    (axes[1,1], fp_umap, "UMAP", "ECFP4 fingerprints"),
]:
    for model_name in ordered:
        mask = labels == model_name
        if np.sum(mask) == 0: continue
        ax.scatter(coords[mask, 0], coords[mask, 1],
                   c=color_map.get(model_name, "#333333"),
                   label=model_name, s=3, alpha=0.5, linewidth=0)
    ax.set_title(f"{method} on {space}")
    ax.set_xlabel(f"{method}1")
    ax.set_ylabel(f"{method}2")
    ax.legend(markerscale=5, fontsize=8)

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.savefig(f"{ROOT}/reports/figures/unified_chemical_space.png", dpi=150, bbox_inches="tight")
print("Saved: reports/figures/unified_chemical_space.png")

# ── Plot 2: IC50 comparison bar chart ──
fig, ax = plt.subplots(figsize=(12, 6))
models_plot = ordered
means = [all_metrics[m]["ic50_mean"] for m in models_plot]
medians = [all_metrics[m]["ic50_median"] for m in models_plot]
mins = [all_metrics[m]["ic50_min"] for m in models_plot]

x = np.arange(len(models_plot))
width = 0.25
ax.bar(x - width, means, width, label="Mean IC50", color="#e74c3c", alpha=0.8)
ax.bar(x, medians, width, label="Median IC50", color="#3498db", alpha=0.8)
ax.bar(x + width, mins, width, label="Min IC50", color="#2ecc71", alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels(models_plot, rotation=30, ha="right")
ax.set_ylabel("IC50 (uM)")
ax.set_title("Predicted IC50 Comparison Across Models")
ax.legend()
plt.tight_layout()
plt.savefig(f"{ROOT}/reports/figures/ic50_comparison.png", dpi=150, bbox_inches="tight")
print("Saved: reports/figures/ic50_comparison.png")

# ── Plot 3: Validity comparison ──
fig, ax = plt.subplots(figsize=(10, 5))
vals = [all_metrics[m]["validity"]*100 for m in models_plot]
colors = [color_map.get(m, "#333") for m in models_plot]
bars = ax.bar(models_plot, vals, color=colors, alpha=0.8)
ax.set_ylabel("Validity (%)")
ax.set_title("Validity Comparison Across Models")
ax.set_xticklabels(models_plot, rotation=30, ha="right")
for bar, v in zip(bars, vals):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1, f"{v:.1f}%",
            ha="center", va="bottom", fontsize=8)
plt.tight_layout()
plt.savefig(f"{ROOT}/reports/figures/validity_comparison.png", dpi=150, bbox_inches="tight")
print("Saved: reports/figures/validity_comparison.png")

print("\n=== ANALYSIS COMPLETE ===")
print(f"Models analyzed: {len(ordered)}")
print(f"Total molecules in plots: {len(labels)}")
print(f"Results saved to metrics/unified_results.csv")
print(f"Figures saved to reports/figures/")