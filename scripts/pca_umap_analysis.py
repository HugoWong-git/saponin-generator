#!/usr/bin/env python
"""PCA + UMAP analysis of 33k generated molecules by physicochemical properties."""
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import umap

ROOT = "."
CSV_PATH = f"{ROOT}/smiles_physchem_properties_full.csv"
OUT_DIR = f"{ROOT}/reports"

os.makedirs(OUT_DIR, exist_ok=True)

# 1. Load data
print("Loading data...")
df = pd.read_csv(CSV_PATH)
print(f"  {len(df)} molecules")

# 2. Select descriptor columns
desc_cols = ['MolWt','LogP','TPSA','NumHDonors','NumHAcceptors',
             'NumRotatableBonds','FormalCharge','NumRings','HeavyAtomCount',
             'FractionCSP3','NumAromaticRings','NumSaturatedRings','MaxPartialCharge']

X = df[desc_cols].values
print(f"  Descriptor matrix: {X.shape}")

# 3. Standardize
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 4. PCA
print("Running PCA...")
pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(X_scaled)
df['PC1'] = pca_coords[:, 0]
df['PC2'] = pca_coords[:, 1]
explained = pca.explained_variance_ratio_
print(f"  PC1: {explained[0]:.3f}, PC2: {explained[1]:.3f}, total: {explained.sum():.3f}")

# PCA loadings
loadings = pd.DataFrame(pca.components_.T, index=desc_cols, columns=['PC1','PC2'])
print("\nPCA Loadings (top contributors):")
for pc in ['PC1','PC2']:
    sorted_idx = loadings[pc].abs().sort_values(ascending=False).head(5).index
    print(f"  {pc}: {[(c, round(loadings.loc[c, pc], 3)) for c in sorted_idx]}")

# 5. UMAP (sample to 10k for speed, then predict rest)
print("\nRunning UMAP on 10k sample...")
rng = np.random.RandomState(42)
sample_idx = rng.choice(len(df), size=10000, replace=False)
mask = np.zeros(len(df), dtype=bool)
mask[sample_idx] = True

umap_model = umap.UMAP(n_components=2, n_neighbors=30, min_dist=0.3, 
                        random_state=42, verbose=False)
umap_sample = umap_model.fit_transform(X_scaled[mask])

# Transform the rest
print("  Transforming full dataset...")
umap_full = umap_model.transform(X_scaled)
df['UMAP1'] = umap_full[:, 0]
df['UMAP2'] = umap_full[:, 1]

# 6. Plots
sns.set_style("whitegrid")
fig, axes = plt.subplots(2, 3, figsize=(20, 14))
fig.suptitle("Physicochemical Space of 33,982 Generated Molecules", fontsize=16, y=0.98)

# Row 1: PCA colored by MW, LogP, TPSA
scatter_kws = dict(s=3, alpha=0.4, linewidth=0)
for ax, col, cmap, title in zip(
    axes[0],
    ['MolWt', 'LogP', 'TPSA'],
    ['viridis', 'plasma', 'coolwarm'],
    ['PCA — colored by MW', 'PCA — colored by LogP', 'PCA — colored by TPSA']
):
    im = ax.scatter(df['PC1'], df['PC2'], c=df[col], cmap=cmap, **scatter_kws)
    ax.set_xlabel(f"PC1 ({explained[0]:.1%})")
    ax.set_ylabel(f"PC2 ({explained[1]:.1%})")
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label=col)

# Row 2: UMAP colored by MW, LogP, TPSA
for ax, col, cmap, title in zip(
    axes[1],
    ['MolWt', 'LogP', 'TPSA'],
    ['viridis', 'plasma', 'coolwarm'],
    ['UMAP — colored by MW', 'UMAP — colored by LogP', 'UMAP — colored by TPSA']
):
    im = ax.scatter(df['UMAP1'], df['UMAP2'], c=df[col], cmap=cmap, **scatter_kws)
    ax.set_xlabel("UMAP1")
    ax.set_ylabel("UMAP2")
    ax.set_title(title)
    plt.colorbar(im, ax=ax, label=col)

plt.tight_layout(rect=[0, 0, 1, 0.96])
pca_plot = f"{OUT_DIR}/pca_umap_physchem.png"
plt.savefig(pca_plot, dpi=150, bbox_inches='tight')
print(f"\nSaved: {pca_plot}")

# 7. Additional: PCA + UMAP faceted by binned properties
fig2, axes2 = plt.subplots(2, 4, figsize=(22, 10))
fig2.suptitle("UMAP — Property Distributions Across Chemical Space", fontsize=14, y=0.98)

props = ['MolWt', 'LogP', 'TPSA', 'NumRings', 'FractionCSP3', 'NumHDonors', 'NumHAcceptors', 'HeavyAtomCount']
for ax, prop in zip(axes2.flatten(), props):
    im = ax.scatter(df['UMAP1'], df['UMAP2'], c=df[prop], cmap='Spectral', s=2, alpha=0.4, linewidth=0)
    ax.set_title(prop, fontsize=10)
    ax.set_xticks([])
    ax.set_yticks([])
    plt.colorbar(im, ax=ax, shrink=0.8)

plt.tight_layout(rect=[0, 0, 1, 0.96])
umap_props_plot = f"{OUT_DIR}/umap_property_facets.png"
plt.savefig(umap_props_plot, dpi=150, bbox_inches='tight')
print(f"Saved: {umap_props_plot}")

# 8. Save coordinates CSV
coords_csv = f"{ROOT}/smiles_physchem_coordinates.csv"
df[['SMILES', 'PC1', 'PC2', 'UMAP1', 'UMAP2'] + desc_cols].to_csv(coords_csv, index=False)
size_mb = os.path.getsize(coords_csv) / 1e6
print(f"Saved coordinates: {coords_csv} ({size_mb:.1f} MB)")

# 9. Print summary
print(f"\n{'='*60}")
print(f"PCA + UMAP Analysis Complete")
print(f"{'='*60}")
print(f"Molecules: {len(df)}")
print(f"Descriptors: {len(desc_cols)}")
print(f"PCA variance: PC1={explained[0]:.2%}, PC2={explained[1]:.2%}")
print(f"PCA loading top contributors:")
for pc in ['PC1','PC2']:
    top = loadings[pc].abs().sort_values(ascending=False).head(3)
    for name, val in top.items():
        direction = "positive" if loadings.loc[name, pc] > 0 else "negative"
        print(f"  {pc}: {name} ({loadings.loc[name, pc]:+.3f}, {direction})")