#!/usr/bin/env python
"""
smiles_props.py — Reusable SMILES-to-physicochemical-properties pipeline.

Computes 9+ RDKit descriptors for any list of SMILES strings.
Usage:
    python smiles_props.py --input data.csv --smiles-col SMILES --id-col Name --output results.csv
    python smiles_props.py --input data.xlsx --sheet Sheet1 --smiles-col SMILES --output results.csv
    # Or import in Python:
    from smiles_props import compute_properties, smiles_props_pipeline
"""

import argparse
import sys
import os
import pandas as pd
import numpy as np
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors


# ── Descriptor definitions ──────────────────────────────────────────────
DESCRIPTOR_INFO = {
    "MolWt":            ("Molecular weight (Da)",       lambda m: Descriptors.MolWt(m)),
    "LogP":             ("Wildman-Crippen logP",         lambda m: Descriptors.MolLogP(m)),
    "TPSA":             ("Topological polar surface area", lambda m: Descriptors.TPSA(m)),
    "NumHDonors":       ("H-bond donors",                lambda m: rdMolDescriptors.CalcNumHBD(m)),
    "NumHAcceptors":    ("H-bond acceptors",              lambda m: rdMolDescriptors.CalcNumHBA(m)),
    "NumRotatableBonds":("Rotatable bonds",              lambda m: rdMolDescriptors.CalcNumRotatableBonds(m)),
    "FormalCharge":     ("Net formal charge",            lambda m: Chem.GetFormalCharge(m)),
    "NumRings":         ("Ring count",                   lambda m: rdMolDescriptors.CalcNumRings(m)),
    "HeavyAtomCount":   ("Heavy (non-H) atoms",          lambda m: m.GetNumHeavyAtoms()),
    "FractionCSP3":     ("Fraction sp3 carbons",         lambda m: rdMolDescriptors.CalcFractionCSP3(m)),
    "NumAromaticRings": ("Aromatic rings",               lambda m: rdMolDescriptors.CalcNumAromaticRings(m)),
    "NumSaturatedRings":("Saturated rings",              lambda m: rdMolDescriptors.CalcNumSaturatedRings(m)),
    "MaxPartialCharge": ("Max partial charge (Gasteiger)", lambda m: _max_partial_charge(m)),
}


def _max_partial_charge(mol):
    """Compute max absolute Gasteiger partial charge."""
    try:
        Chem.rdmolops.AssignAtomChiralTagsFromStructure(mol)
        from rdkit.Chem import AllChem
        AllChem.ComputeGasteigerCharges(mol)
        charges = [float(atom.GetPropsAsDict().get("_GasteigerCharge", 0))
                   for atom in mol.GetAtoms()]
        return max(abs(c) for c in charges) if charges else 0.0
    except Exception:
        return 0.0


def compute_properties(smiles_list):
    """Compute physicochemical properties for a list of SMILES strings.
    
    Args:
        smiles_list: list of SMILES strings
        
    Returns:
        pd.DataFrame with columns: SMILES, valid, error_msg, MolWt, LogP, ...
    """
    rows = []
    for i, smi in enumerate(smiles_list):
        smi = str(smi).strip()
        row = {"row_index": i, "SMILES": smi, "valid": False, "error_msg": ""}
        
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            # Try with sanitization off
            mol = Chem.MolFromSmiles(smi, sanitize=False)
            if mol is None:
                row["valid"] = False
                row["error_msg"] = "RDKit could not parse SMILES"
                rows.append(row)
                continue
        
        # Sanitize
        try:
            Chem.SanitizeMol(mol)
        except Exception as e:
            row["valid"] = False
            row["error_msg"] = f"Sanitization failed: {str(e)[:100]}"
            rows.append(row)
            continue
        
        row["valid"] = True
        for name, (_, func) in DESCRIPTOR_INFO.items():
            try:
                val = func(mol)
                row[name] = round(float(val), 4) if isinstance(val, (int, float, np.floating)) else val
            except Exception as e:
                row[name] = None
                if not row["error_msg"]:
                    row["error_msg"] = f"Descriptor '{name}' failed: {str(e)[:80]}"
        
        rows.append(row)
    
    return pd.DataFrame(rows)


def smiles_props_pipeline(input_path, smiles_col="SMILES", id_col=None, 
                           sheet_name=None, output_path=None):
    """End-to-end pipeline: read file -> compute properties -> return/save.
    
    Args:
        input_path: path to .csv or .xlsx file
        smiles_col: name of the SMILES column
        id_col: optional name of an identifier column to keep
        sheet_name: sheet name for .xlsx files
        output_path: optional path to save CSV results
        
    Returns:
        pd.DataFrame with original columns + computed properties
    """
    # 1. Read input
    ext = os.path.splitext(input_path)[1].lower()
    if ext == ".xlsx":
        if sheet_name:
            df_in = pd.read_excel(input_path, sheet_name=sheet_name)
        else:
            xl = pd.ExcelFile(input_path)
            df_in = pd.read_excel(input_path, sheet_name=xl.sheet_names[0])
    elif ext == ".csv":
        df_in = pd.read_csv(input_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")
    
    if smiles_col not in df_in.columns:
        raise ValueError(f"SMILES column '{smiles_col}' not found. Columns: {df_in.columns.tolist()}")
    
    # 2. Compute properties
    props = compute_properties(df_in[smiles_col].tolist())
    
    # 3. Merge back with original data
    # Keep the original columns plus the computed properties
    cols_to_keep = [c for c in df_in.columns if c != smiles_col]
    if id_col and id_col in df_in.columns:
        merge_cols = [id_col, smiles_col]
    else:
        merge_cols = [smiles_col]
    
    result = df_in[merge_cols].copy()
    # Add computed property columns (drop the redundant SMILES from props)
    for col in props.columns:
        if col not in ("row_index", "SMILES"):
            result[col] = props[col].values
    
    # 4. Save if requested
    if output_path:
        result.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")
    
    return result


# ── CLI entry point ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Compute physicochemical properties from SMILES")
    parser.add_argument("--input", required=True, help="Input CSV or XLSX file")
    parser.add_argument("--smiles-col", default="SMILES", help="SMILES column name")
    parser.add_argument("--id-col", default=None, help="Optional identifier column")
    parser.add_argument("--sheet", default=None, help="Sheet name for XLSX files")
    parser.add_argument("--output", default=None, help="Output CSV path")
    args = parser.parse_args()
    
    df = smiles_props_pipeline(
        input_path=args.input,
        smiles_col=args.smiles_col,
        id_col=args.id_col,
        sheet_name=args.sheet,
        output_path=args.output,
    )
    
    print(f"\nProcessed {len(df)} molecules.")
    n_valid = df["valid"].sum()
    n_invalid = (~df["valid"]).sum()
    print(f"  Valid: {n_valid}")
    print(f"  Invalid: {n_invalid}")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst 5 rows:")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 200)
    print(df.head(5).to_string())


if __name__ == "__main__":
    main()
