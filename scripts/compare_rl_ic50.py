#!/usr/bin/env python
"""Compare IC50 distributions: Epoch4 prior vs V1 RL vs V3 RL."""
import csv, json, subprocess, sys, random
import numpy as np

random.seed(42)

root = "."

with open(f"{root}/samples/rl_agent_v3_samples.csv") as f:
    v3_smiles = [row["SMILES"] for row in csv.DictReader(f) if int(row["SMILES_state"]) == 1]
with open(f"{root}/samples/rl_agent_samples.csv") as f:
    v1_all = [row["SMILES"] for row in csv.DictReader(f) if int(row["SMILES_state"]) == 1]
v1_sample = random.sample(v1_all, min(len(v3_smiles), len(v1_all)))
with open(f"{root}/samples/saponin_prior_46k_reg_epoch4_samples.csv") as f:
    ep4_all = [row["SMILES"] for row in csv.DictReader(f) if int(row["SMILES_state"]) == 1]
ep4_sample = random.sample(ep4_all, min(len(v3_smiles), len(ep4_all)))
print(f"V3 RL: {len(v3_smiles)}  V1 RL: {len(v1_sample)}  Epoch4: {len(ep4_sample)}")

def score_set(smiles_list):
    proc = subprocess.run(
        [sys.executable, f"{root}/scripts/ic50_scorer.py"],
        input="\n".join(smiles_list), capture_output=True, text=True
    )
    return np.array(json.loads(proc.stdout)["payload"]["predictions"])

v3_s = score_set(v3_smiles)
v1_s = score_set(v1_sample)
ep4_s = score_set(ep4_sample)
v3_i, v1_i, ep4_i = np.exp(v3_s), np.exp(v1_s), np.exp(ep4_s)

print(f"\n{'Metric':<25} {'Epoch4':>10} {'V1 RL':>10} {'V3 RL':>10}")
print("-"*55)
for name, a, b, c in [
    ("Mean ln(IC50)", np.mean(ep4_s), np.mean(v1_s), np.mean(v3_s)),
    ("Mean IC50 (uM)", np.mean(ep4_i), np.mean(v1_i), np.mean(v3_i)),
    ("Median IC50 (uM)", np.median(ep4_i), np.median(v1_i), np.median(v3_i)),
    ("Min IC50 (uM)", np.min(ep4_i), np.min(v1_i), np.min(v3_i)),
    ("% IC50 < 1uM", np.mean(ep4_i<1)*100, np.mean(v1_i<1)*100, np.mean(v3_i<1)*100),
    ("% IC50 < 2uM", np.mean(ep4_i<2)*100, np.mean(v1_i<2)*100, np.mean(v3_i<2)*100),
    ("% IC50 < 5uM", np.mean(ep4_i<5)*100, np.mean(v1_i<5)*100, np.mean(v3_i<5)*100),
    ("% IC50 < 10uM", np.mean(ep4_i<10)*100, np.mean(v1_i<10)*100, np.mean(v3_i<10)*100),
]:
    print(f"{name:<25} {c:>10.2f} {b:>10.2f} {a:>10.2f}")

data = {
    "epoch4": {"ln_mean": float(np.mean(ep4_s)), "ic50_mean": float(np.mean(ep4_i)), "ic50_med": float(np.median(ep4_i))},
    "v1_rl":  {"ln_mean": float(np.mean(v1_s)), "ic50_mean": float(np.mean(v1_i)), "ic50_med": float(np.median(v1_i))},
    "v3_rl":  {"ln_mean": float(np.mean(v3_s)), "ic50_mean": float(np.mean(v3_i)), "ic50_med": float(np.median(v3_i))},
}
with open(f"{root}/metrics/ic50_rl_v3_comparison.json", "w") as f:
    json.dump(data, f, indent=2)
print(f"\nSaved metrics/ic50_rl_v3_comparison.json")