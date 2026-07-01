#!/usr/bin/env python
"""4-way comparison: E1 TL, E4 TL, E1-RL, E4-RL — IC50, descriptors, NPC."""
import csv, json, subprocess, sys, time, random, os
import numpy as np
import pandas as pd
import requests
from collections import Counter
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

ROOT = "."
NPC_API = "https://npclassifier.gnps2.org/classify"
rng = random.Random(42)

models = {
    "E1 TL Prior": f"{ROOT}/samples/saponin_prior_46k_reg_epoch1_samples.csv",
    "E4 TL Prior": f"{ROOT}/samples/saponin_prior_46k_reg_epoch4_samples.csv",
    "E1 RL Agent": f"{ROOT}/samples/rl_epoch1_10k.csv",
    "E4 RL Agent": f"{ROOT}/samples/rl_v3_final_10k.csv",
}
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

results = {}
for name, path in models.items():
    print(f"\n{'='*60}")
    print(f"Processing: {name}")
    print('='*60)
    
    smiles = []
    with open(path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row.get("SMILES_state", 1)) == 1:
                smiles.append(row["SMILES"].strip())
    
    n_valid = len(smiles)
    total = 10000
    validity = n_valid / total
    
    # Canonical + descriptors
    canon = set()
    desc_vals = {n: [] for n in desc_names}
    for smi in smiles:
        m = Chem.MolFromSmiles(smi)
        if m:
            cs = Chem.MolToSmiles(m, canonical=True)
            if cs not in canon:
                canon.add(cs)
                for n2, fn in zip(desc_names, desc_funcs):
                    try: desc_vals[n2].append(fn(m))
                    except: pass
    
    n_unique = len(canon)
    uniqueness = n_unique / n_valid if n_valid > 0 else 0
    novel = canon - train
    novelty = len(novel) / n_unique if n_unique > 0 else 0
    
    print(f"  Validity: {n_valid}/{total} = {validity:.4f}")
    print(f"  Unique: {n_unique}, Uniqueness: {uniqueness:.4f}")
    print(f"  Novelty: {novelty:.4f}")
    
    # IC50
    print(f"  Scoring {n_unique} unique molecules with IC50 model...")
    proc = subprocess.run(
        [sys.executable, f"{ROOT}/scripts/ic50_scorer.py"],
        input="\n".join(list(canon)), capture_output=True, text=True, timeout=600
    )
    scores = np.array(json.loads(proc.stdout)["payload"]["predictions"])
    ic50 = np.exp(scores)
    
    print(f"  Mean IC50: {np.mean(ic50):.2f} uM")
    print(f"  Median IC50: {np.median(ic50):.2f} uM")
    print(f"  Min IC50: {np.min(ic50):.2f} uM")
    print(f"  % < 2 uM: {np.mean(ic50<2)*100:.1f}%")
    print(f"  % < 5 uM: {np.mean(ic50<5)*100:.1f}%")
    
    # Descriptors
    print(f"  Descriptors:")
    desc_stats = {}
    for n2 in desc_names:
        v = np.array(desc_vals[n2])
        desc_stats[n2] = {"mean": float(np.mean(v)), "std": float(np.std(v))}
        print(f"    {n2:20s} mean={np.mean(v):8.2f}  std={np.std(v):8.2f}")
    
    # NPClassifier
    print(f"  NPClassifier (200 random)...")
    npc_sample = rng.sample(list(canon), min(200, len(canon)))
    npc_res = {"superclass": [], "class": [], "pathway": []}
    def classify_one(s, retries=2):
        for a in range(retries):
            try:
                r = requests.get(NPC_API, params={"smiles": s}, timeout=15)
                if r.status_code == 200: return r.json()
            except:
                if a < retries - 1: time.sleep(1)
        return None
    ok = 0
    for i, s in enumerate(npc_sample):
        r = classify_one(s)
        if r:
            ok += 1
            for k in ["superclass_results", "class_results", "pathway_results"]:
                t = k.replace("_results", "")
                if k in r and r[k]: npc_res[t].extend(r[k])
        time.sleep(0.3)
    print(f"    Classified: {ok}/{len(npc_sample)}")
    npc_summary = {}
    for key in ["superclass", "class", "pathway"]:
        items = npc_res[key]
        if items:
            top = Counter(items).most_common(3)
            for n2, cnt in top:
                npc_summary[f"{key}_{n2[:30]}"] = round(cnt/len(items)*100, 1)
            print(f"    {key}: {[(n[:25], round(c/len(items)*100,1)) for n,c in top]}")
    
    results[name] = {
        "validity": round(validity, 4), "n_valid": n_valid,
        "n_unique": n_unique, "uniqueness": round(uniqueness, 4),
        "novelty": round(novelty, 4),
        "ic50_mean": round(float(np.mean(ic50)), 2),
        "ic50_median": round(float(np.median(ic50)), 2),
        "ic50_min": round(float(np.min(ic50)), 2),
        "pct_lt_2uM": round(float(np.mean(ic50<2)*100), 1),
        "pct_lt_5uM": round(float(np.mean(ic50<5)*100), 1),
        "descriptors": desc_stats,
        "npc": npc_summary,
    }

# Save JSON
with open(f"{ROOT}/metrics/e1_vs_e4_comparison.json", "w") as f:
    json.dump(results, f, indent=2)

# Print summary table
print(f"\n\n{'='*80}")
print(f"SUMMARY: E1 vs E4 — TL Priors and RL Agents")
print(f"{'='*80}")
print(f"{'Metric':<20} {'E1 TL':>10} {'E4 TL':>10} {'E1 RL':>10} {'E4 RL':>10}")
print('-'*60)
for metric in ["validity", "novelty", "ic50_mean", "ic50_median", "ic50_min", "pct_lt_2uM", "pct_lt_5uM"]:
    vals = [results[m][metric] for m in models.keys()]
    print(f"{metric:<20} {vals[0]:>10} {vals[1]:>10} {vals[2]:>10} {vals[3]:>10}")

print(f"\nDescriptors (mean):")
for desc in desc_names:
    vals = [results[m]["descriptors"][desc]["mean"] for m in models.keys()]
    print(f"{desc:<20} {vals[0]:>10.1f} {vals[1]:>10.1f} {vals[2]:>10.1f} {vals[3]:>10.1f}")

print(f"\nNPClassifier (% Triterpenoids):")
for m in models.keys():
    trit = results[m]["npc"].get("superclass_Triterpenoids", "?")
    print(f"  {m:<20} {trit}")