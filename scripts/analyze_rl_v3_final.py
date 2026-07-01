#!/usr/bin/env python
"""Full analysis of RL V3 final 10k sample: validity, descriptors, IC50, NPClassifier."""
import csv, json, subprocess, sys, time, random
import numpy as np
import pandas as pd
import requests
from collections import Counter
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

ROOT = "."
CSV_PATH = f"{ROOT}/samples/rl_v3_final_10k.csv"
NPC_API = "https://npclassifier.gnps2.org/classify"
rng = random.Random(42)

print("Loading V3 RL samples...")
valid_smiles = []
all_nll = []
with open(CSV_PATH) as f:
    reader = csv.DictReader(f)
    for row in reader:
        if int(row["SMILES_state"]) == 1:
            valid_smiles.append(row["SMILES"].strip())
            if "NLL" in row:
                all_nll.append(float(row["NLL"]))

total_sampled = 10000
n_valid = len(valid_smiles)
validity = n_valid / total_sampled
print(f"  Sampled: {total_sampled}, Valid: {n_valid}, Validity: {validity:.4f}")
print(f"  Mean NLL: {np.mean(all_nll):.2f}" if all_nll else "")

# Canonicalize
canon = set()
for smi in valid_smiles:
    m = Chem.MolFromSmiles(smi)
    if m:
        canon.add(Chem.MolToSmiles(m, canonical=True))
print(f"  Unique canonical: {len(canon)}")

# Novelty vs training set
train = set()
with open(f"{ROOT}/data/saponin_train_46k_valid.smi") as f:
    for line in f:
        smi = line.strip()
        if smi:
            m = Chem.MolFromSmiles(smi)
            if m:
                train.add(Chem.MolToSmiles(m, canonical=True))
novel = canon - train
print(f"  Novelty: {len(novel)/len(canon)*100:.2f}%")

# Descriptors
desc_names = ["MolWt","LogP","TPSA","NumHDonors","NumHAcceptors","NumRotatableBonds","NumRings","HeavyAtomCount","FractionCSP3"]
desc_funcs = [
    lambda m: Descriptors.MolWt(m),
    lambda m: Descriptors.MolLogP(m),
    lambda m: Descriptors.TPSA(m),
    lambda m: rdMolDescriptors.CalcNumHBD(m),
    lambda m: rdMolDescriptors.CalcNumHBA(m),
    lambda m: rdMolDescriptors.CalcNumRotatableBonds(m),
    lambda m: rdMolDescriptors.CalcNumRings(m),
    lambda m: m.GetNumHeavyAtoms(),
    lambda m: rdMolDescriptors.CalcFractionCSP3(m),
]
desc_vals = {n: [] for n in desc_names}
for smi in canon:
    m = Chem.MolFromSmiles(smi)
    if m:
        for name, func in zip(desc_names, desc_funcs):
            try: desc_vals[name].append(func(m))
            except: pass

print("\n=== Physicochemical Descriptors ===")
for name in desc_names:
    vals = np.array(desc_vals[name])
    print(f"  {name:20s}  mean={np.mean(vals):8.2f}  std={np.std(vals):8.2f}  min={np.min(vals):8.2f}  max={np.max(vals):8.2f}")

# IC50 scoring
print("\n=== Scoring with IC50 model ===")
proc = subprocess.run(
    [sys.executable, f"{ROOT}/scripts/ic50_scorer.py"],
    input="\n".join(list(canon)), capture_output=True, text=True
)
scores = np.array(json.loads(proc.stdout)["payload"]["predictions"])
ic50 = np.exp(scores)
print(f"  Mean ln(IC50): {np.mean(scores):.3f}")
print(f"  Mean IC50: {np.mean(ic50):.2f} uM")
print(f"  Median IC50: {np.median(ic50):.2f} uM")
print(f"  Min IC50: {np.min(ic50):.2f} uM")
print(f"  Max IC50: {np.max(ic50):.2f} uM")
print(f"  % IC50 < 1 uM: {np.mean(ic50<1)*100:.1f}%")
print(f"  % IC50 < 2 uM: {np.mean(ic50<2)*100:.1f}%")
print(f"  % IC50 < 5 uM: {np.mean(ic50<5)*100:.1f}%")

# NPClassifier on 100 random samples
print("\n\n=== NPClassifier (100 random molecules) ===")
npc_sample = rng.sample(list(canon), min(100, len(canon)))
npc_results = {"superclass": [], "class": [], "pathway": []}

def classify_one(smiles, retries=2):
    for a in range(retries):
        try:
            r = requests.get(NPC_API, params={"smiles": smiles}, timeout=15)
            if r.status_code == 200: return r.json()
        except:
            if a < retries - 1: time.sleep(1)
    return None

ok = 0
for i, smi in enumerate(npc_sample):
    result = classify_one(smi)
    if result:
        ok += 1
        for k in ["superclass_results", "class_results", "pathway_results"]:
            target = k.replace("_results", "")
            if k in result and result[k]:
                npc_results[target].extend(result[k])
    time.sleep(0.3)
    if (i+1) % 25 == 0:
        print(f"  {i+1}/{len(npc_sample)} (ok={ok})", end="\r")

print(f"\n  Classified: {ok}/{len(npc_sample)}")
for key in ["superclass", "class", "pathway"]:
    items = npc_results[key]
    if items:
        top = Counter(items).most_common(5)
        print(f"  {key}:")
        for name, cnt in top:
            print(f"    {name:<35s} {cnt/len(items)*100:.1f}%")

# Save comprehensive CSV
print("\n\nSaving comprehensive results...")
results_df = pd.DataFrame({
    "SMILES": list(canon),
    "ln_IC50": scores[:len(canon)],
    "predicted_IC50_uM": ic50[:len(canon)],
})
for name in desc_names:
    results_df[name] = desc_vals[name][:len(canon)]

out_csv = f"{ROOT}/samples/rl_v3_final_10k_analyzed.csv"
results_df.to_csv(out_csv, index=False)
print(f"Saved: {out_csv}")
print(f"File size: {__import__('os').path.getsize(out_csv)/1e6:.1f} MB")