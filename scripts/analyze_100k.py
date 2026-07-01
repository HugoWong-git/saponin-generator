#!/usr/bin/env python
"""Analyze 100k V3 RL sample: validity, descriptors, IC50, NPClassifier."""
import csv, json, subprocess, sys, time, random, os
import numpy as np
import pandas as pd
import requests
from collections import Counter
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

ROOT = "."
CSV_PATH = f"{ROOT}/samples/rl_v3_100k.csv"
NPC_API = "https://npclassifier.gnps2.org/classify"
rng = random.Random(42)

print("Loading 100k V3 RL samples...")
valid_smiles = []
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row["SMILES_state"]) == 1:
            valid_smiles.append(row["SMILES"].strip())

total = 100000
n_valid = len(valid_smiles)
print(f"  Sampled: {total}, Valid: {n_valid}, Validity: {n_valid/total:.4f}")

# Canonical + descriptors
canon = set()
desc_names = ["MolWt","LogP","TPSA","NumHDonors","NumHAcceptors","NumRotatableBonds","NumRings","HeavyAtomCount","FractionCSP3"]
desc_funcs = [
    lambda m: Descriptors.MolWt(m), lambda m: Descriptors.MolLogP(m), lambda m: Descriptors.TPSA(m),
    lambda m: rdMolDescriptors.CalcNumHBD(m), lambda m: rdMolDescriptors.CalcNumHBA(m),
    lambda m: rdMolDescriptors.CalcNumRotatableBonds(m), lambda m: rdMolDescriptors.CalcNumRings(m),
    lambda m: m.GetNumHeavyAtoms(), lambda m: rdMolDescriptors.CalcFractionCSP3(m),
]
desc_vals = {n: [] for n in desc_names}
for smi in valid_smiles:
    m = Chem.MolFromSmiles(smi)
    if m:
        cs = Chem.MolToSmiles(m, canonical=True)
        if cs not in canon:
            canon.add(cs)
            for name, func in zip(desc_names, desc_funcs):
                try: desc_vals[name].append(func(m))
                except: pass

print(f"  Unique canonical: {len(canon)}")

# Novelty
train = set()
with open(f"{ROOT}/data/saponin_train_46k_valid.smi") as f:
    for line in f:
        s = line.strip()
        if s:
            m = Chem.MolFromSmiles(s)
            if m: train.add(Chem.MolToSmiles(m, canonical=True))
novel = canon - train
print(f"  Novelty: {len(novel)/len(canon)*100:.2f}%")

print("\n=== Descriptors ===")
for name in desc_names:
    vals = np.array(desc_vals[name])
    print(f"  {name:20s}  mean={np.mean(vals):8.2f}  std={np.std(vals):8.2f}")

# IC50 scoring (on unique canonical set)
print(f"\n=== IC50 scoring ({len(canon)} molecules) ===")
canon_list = list(canon)
proc = subprocess.run(
    [sys.executable, f"{ROOT}/scripts/ic50_scorer.py"],
    input="\n".join(canon_list), capture_output=True, text=True, timeout=600
)
scores = np.array(json.loads(proc.stdout)["payload"]["predictions"])
ic50 = np.exp(scores)
print(f"  Mean ln(IC50): {np.mean(scores):.3f}")
print(f"  Mean IC50: {np.mean(ic50):.2f} uM")
print(f"  Median IC50: {np.median(ic50):.2f} uM")
print(f"  Min IC50: {np.min(ic50):.2f} uM")
print(f"  % IC50 < 1 uM: {np.mean(ic50<1)*100:.1f}%")
print(f"  % IC50 < 2 uM: {np.mean(ic50<2)*100:.1f}%")
print(f"  % IC50 < 5 uM: {np.mean(ic50<5)*100:.1f}%")
print(f"  % IC50 < 10 uM: {np.mean(ic50<10)*100:.1f}%")

# NPClassifier on 100 random
print(f"\n=== NPClassifier (100 random) ===")
npc_sample = rng.sample(canon_list, min(100, len(canon_list)))
npc_results = {"superclass": [], "class": [], "pathway": []}
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
            if k in r and r[k]: npc_results[t].extend(r[k])
    time.sleep(0.3)
    if (i+1) % 25 == 0: print(f"  {i+1}/{len(npc_sample)} ok={ok}", end="\r")
print(f"\n  Classified: {ok}/{len(npc_sample)}")
for key in ["superclass", "class", "pathway"]:
    items = npc_results[key]
    if items:
        top = Counter(items).most_common(5)
        print(f"  {key}:")
        for name, cnt in top: print(f"    {name:<40s} {cnt/len(items)*100:.1f}%")

# Save analyzed CSV
out_csv = f"{ROOT}/samples/rl_v3_100k_analyzed.csv"
df = pd.DataFrame({"SMILES": canon_list, "ln_IC50": scores, "predicted_IC50_uM": ic50})
for name in desc_names: df[name] = desc_vals[name][:len(df)]
df.to_csv(out_csv, index=False)
print(f"\nSaved: {out_csv} ({os.path.getsize(out_csv)/1e6:.1f} MB)")