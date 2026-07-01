#!/usr/bin/env python3
"""
saponin_design_pilot.py — Saponin Design Platform CLI (Pilot)

Analyze and screen generated saponin molecules by computing
physicochemical properties and ranking by custom criteria.

Design Briefs:
    python saponin_design_pilot.py brief-1   # Sample TL prior -> rank by properties
    python saponin_design_pilot.py brief-2   # Light saponins (MW 600-750, TPSA 120-200)
    python saponin_design_pilot.py brief-3   # RL optimised -> rank by properties
    python saponin_design_pilot.py all        # Run all 3 briefs
    python saponin_design_pilot.py screen --input file.csv  # Screen existing CSV

To add custom scoring (e.g., IC50 prediction), implement a scorer
function and pass scores into the pipeline.
"""

import sys, os, json, time, warnings, argparse
import numpy as np
import pandas as pd
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

warnings.filterwarnings("ignore")

# === CONFIGURABLE PATHS ===
# Point these to your generated sample files
SAMPLES_DIR = Path("samples")
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


def compute_properties(smiles_list):
    """Compute RDKit physicochemical descriptors for a list of SMILES."""
    props_list = []
    for smi in smiles_list:
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            props_list.append({
                "MolWt": None, "LogP": None, "TPSA": None, "HBD": None,
                "HBA": None, "RotBonds": None, "Rings": None,
                "HeavyAtoms": None, "Fsp3": None
            })
        else:
            props_list.append({
                "MolWt": round(Descriptors.MolWt(mol), 2),
                "LogP": round(Descriptors.MolLogP(mol), 2),
                "TPSA": round(Descriptors.TPSA(mol), 1),
                "HBD": rdMolDescriptors.CalcNumHBD(mol),
                "HBA": rdMolDescriptors.CalcNumHBA(mol),
                "RotBonds": rdMolDescriptors.CalcNumRotatableBonds(mol),
                "Rings": rdMolDescriptors.CalcNumRings(mol),
                "HeavyAtoms": mol.GetNumHeavyAtoms(),
                "Fsp3": round(rdMolDescriptors.CalcFractionCSP3(mol), 3),
            })
    return props_list


def screen_csv(filepath, top_n=50):
    """Load a CSV, compute properties, return ranked results."""
    print(f"[PILOT] Loading {filepath}")
    df = pd.read_csv(filepath)
    if "SMILES" not in df.columns:
        print("[ERROR] No SMILES column found")
        return None
    smiles = df["SMILES"].dropna().tolist()
    print(f"[PILOT] {len(smiles)} SMILES loaded")

    # Compute properties
    t0 = time.time()
    props = compute_properties(smiles)
    dt = time.time() - t0
    print(f"[PILOT] Properties: {len(smiles)} mol in {dt:.1f}s ({len(smiles)/dt:.1f} mol/s)")

    # Build result rows
    rows = []
    for smi, prop in zip(smiles, props):
        valid = prop["MolWt"] is not None
        rows.append({"SMILES": smi, "valid": valid, **prop})

    result = pd.DataFrame(rows)
    valid_df = result[result["valid"] == True].copy()
    print(f"[PILOT] Valid: {len(valid_df)}/{len(smiles)}")

    # Sort by MolWt as a basic ranking (override with custom scorer)
    # Replace with your own scoring function here
    valid_df = valid_df.sort_values("MolWt").reset_index(drop=True)
    valid_df["rank"] = range(1, len(valid_df) + 1)

    stem = Path(filepath).stem
    outpath = OUTPUT_DIR / f"{stem}_screened.csv"
    valid_df.to_csv(outpath, index=False)
    print(f"[PILOT] Saved: {outpath}")

    cols = ["rank", "SMILES", "MolWt", "LogP", "TPSA", "Fsp3"]
    print(f"[PILOT] Top {min(5, len(valid_df))} by MW:")
    print(valid_df.head(5)[cols].to_string(index=False))

    if top_n and len(valid_df) > 0:
        top = valid_df.head(min(top_n, len(valid_df)))
        top_path = OUTPUT_DIR / f"{stem}_top{top_n}.csv"
        top.to_csv(top_path, index=False)
        print(f"[PILOT] Top {len(top)}: {top_path}")

    return valid_df


def brief_1():
    """TL prior samples -> properties -> top N."""
    print("=" * 60)
    print("BRIEF 1: TL prior -> properties -> top N")
    print("=" * 60)
    candidates = sorted(SAMPLES_DIR.glob("*.csv"))
    for c in candidates:
        print(f"  Found: {c.name}")
    if candidates:
        return screen_csv(candidates[0], top_n=50)
    print("[PILOT] No sample CSV found in SAMPLES_DIR")
    return None


def brief_2():
    """Light saponins: MW 600-750, TPSA 120-200."""
    print("=" * 60)
    print("BRIEF 2: Light saponins (MW 600-750, TPSA 120-200)")
    print("=" * 60)
    files = list(SAMPLES_DIR.glob("*.csv"))
    if not files:
        print("[PILOT] No CSV files found")
        return None
    fp = files[0]
    df = pd.read_csv(fp)
    smiles = df["SMILES"].dropna().tolist()
    print(f"[PILOT] {len(smiles)} SMILES loaded")

    props = compute_properties(smiles)
    rows = [{"SMILES": smi, "valid": p["MolWt"] is not None, **p}
            for smi, p in zip(smiles, props)]
    merged = pd.DataFrame(rows)
    valid_df = merged[merged["valid"] == True].copy()

    filtered = valid_df[
        (valid_df["MolWt"].between(600, 750)) &
        (valid_df["TPSA"].between(120, 200))
    ].copy()
    filtered = filtered.sort_values("MolWt").reset_index(drop=True)
    filtered["rank"] = range(1, len(filtered) + 1)

    outpath = OUTPUT_DIR / "brief2_light_saponins.csv"
    filtered.to_csv(outpath, index=False)
    print(f"[PILOT] Filtered: {len(filtered)} / {len(valid_df)} valid")
    print(f"[PILOT] Saved: {outpath}")
    cols = ["rank", "SMILES", "MolWt", "LogP", "TPSA", "Fsp3"]
    print(filtered.head(5)[cols].to_string(index=False))
    return filtered


def brief_3():
    """RL optimised -> properties screen."""
    print("=" * 60)
    print("BRIEF 3: RL optimised -> properties screen")
    print("=" * 60)
    files = sorted(SAMPLES_DIR.glob("rl*.csv"))
    if not files:
        files = sorted(SAMPLES_DIR.glob("*.csv"))
    if not files:
        print("[PILOT] No CSV files found")
        return None
    return screen_csv(files[0], top_n=50)


def run_all():
    r1 = brief_1()
    r2 = brief_2()
    r3 = brief_3()
    print("\n" + "=" * 60)
    print("PILOT SUMMARY")
    print("=" * 60)
    for name, r in [
        ("brief-1 (TL prior)", r1),
        ("brief-2 (light saponins)", r2),
        ("brief-3 (RL optimised)", r3),
    ]:
        if r is not None:
            print(f"  {name}: {len(r)} mol valid")
        else:
            print(f"  {name}: SKIPPED")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Saponin Design Platform Pilot")
    parser.add_argument("command", choices=["brief-1", "brief-2", "brief-3", "all", "screen"])
    parser.add_argument("--input", help="Input CSV for screen command")
    parser.add_argument("--top-n", type=int, default=50)
    args = parser.parse_args()

    cmds = {
        "brief-1": brief_1,
        "brief-2": brief_2,
        "brief-3": brief_3,
        "all": run_all,
        "screen": lambda: screen_csv(args.input, args.top_n) if args.input else print("Need --input"),
    }
    cmds[args.command]()