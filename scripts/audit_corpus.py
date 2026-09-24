#!/usr/bin/env python3
"""
audit_corpus.py — profile a triterpenoid/saponin SMILES corpus against the
thresholds in the Cycle 1 literature review.

Answers the questions the review flags as unmeasured (Q4, R7, R9, R10, R11, R12):

  1. How many molecules survive parsing?
  2. What is the aglycone : glycoside split?          <- the key open quantity
  3. How complete is the stereochemistry?             <- R12 / R7
  4. Do SMILES lengths exceed published cutoffs?      <- R9
  5. What is the sugar composition?                   <- R10 baseline
  6. How diverse is the corpus?                       <- feeds the §6 homogeneity question

USAGE
    pip install rdkit
    python audit_corpus.py terpenoids.smi
    python audit_corpus.py data.csv --smiles-col canonical_smiles
    python audit_corpus.py data.sdf
    python audit_corpus.py data.smi --out audit_report.json --write-subsets

STATUS
    Written against the RDKit API but NOT executed against a live RDKit install
    (the authoring sandbox could not install it). Treat the first run as a smoke
    test. The sugar detection is a structural heuristic, not a carbohydrate
    assignment tool — see detect_sugar_rings() for exactly what it does and does
    not claim.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from collections import Counter

try:
    from rdkit import Chem, RDLogger
    from rdkit.Chem import Descriptors, rdMolDescriptors
    from rdkit.Chem.Scaffolds import MurckoScaffold
    from rdkit.DataStructs import BulkTanimotoSimilarity
    from rdkit.Chem import rdFingerprintGenerator
except ImportError:
    sys.exit("RDKit not found.  Install it first:  pip install rdkit")

RDLogger.DisableLog("rdApp.*")

# Thresholds quoted in the literature review, for direct comparison.
SMILES_LEN_CUTOFF_SKINNIDER = 250   # Skinnider 2021 preprocessing
SMILES_LEN_CUTOFF_GUACAMOL = 100    # Brown 2019 preprocessing
TL_FLOOR_AMABILINO = 190            # Amabilino 2020 transfer-learning floor
PLANT_METABOLOME_SKINNIDER = 21993  # Skinnider 2021 plant metabolome model
MOSES_MAX_HEAVY = 27                # Polykovskiy 2020 dataset range
GUACAMOL_MAX_HEAVY = 88             # Brown 2019 dataset range


# --------------------------------------------------------------------------
# Loading
# --------------------------------------------------------------------------

def load_molecules(path: str, smiles_col: str | None = None):
    """Yield (identifier, smiles, mol) triples from .smi/.txt/.csv/.tsv/.sdf."""
    ext = os.path.splitext(path)[1].lower()

    if ext == ".sdf":
        supplier = Chem.SDMolSupplier(path)
        for i, mol in enumerate(supplier):
            smi = Chem.MolToSmiles(mol) if mol else ""
            yield (str(i), smi, mol)
        return

    import csv
    with open(path, newline="", encoding="utf-8", errors="replace") as fh:
        if ext in (".csv", ".tsv"):
            delim = "\t" if ext == ".tsv" else ","
            reader = csv.DictReader(fh, delimiter=delim)
            if not reader.fieldnames:
                sys.exit(f"{path}: no header row found")
            col = smiles_col
            if col is None:
                for cand in ("smiles", "SMILES", "canonical_smiles",
                             "Smiles", "structure", "isomeric_smiles"):
                    if cand in reader.fieldnames:
                        col = cand
                        break
            if col is None:
                sys.exit(f"Could not find a SMILES column in {reader.fieldnames}. "
                         f"Pass --smiles-col explicitly.")
            id_col = next((c for c in ("id", "ID", "name", "Name", "terokit_id")
                           if c in reader.fieldnames), None)
            for i, row in enumerate(reader):
                smi = (row.get(col) or "").strip()
                ident = (row.get(id_col) or str(i)) if id_col else str(i)
                yield (ident, smi, Chem.MolFromSmiles(smi) if smi else None)
        else:
            # whitespace-delimited .smi / .txt: SMILES [id]
            for i, line in enumerate(fh):
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                smi = parts[0]
                # skip a header line like "smiles  id"
                if i == 0 and smi.lower() in ("smiles", "canonical_smiles"):
                    continue
                ident = parts[1] if len(parts) > 1 else str(i)
                yield (ident, smi, Chem.MolFromSmiles(smi))


# --------------------------------------------------------------------------
# Sugar / glycoside detection
# --------------------------------------------------------------------------

def detect_sugar_rings(mol):
    """
    Identify carbohydrate-like rings by structure.

    CLAIMS: a ring is counted as sugar-like when it is a 5- or 6-membered ring
    containing exactly one ring oxygen, with all remaining ring atoms sp3
    carbon, and with at least two oxygen substituents on ring atoms.

    DOES NOT CLAIM: to identify WHICH monosaccharide it is. Distinguishing
    glucose from galactose from mannose requires stereocentre-by-stereocentre
    matching against reference structures. The coarse buckets below (hexose-like
    / pentose-like / deoxy / uronic) are shape heuristics only. If the corpus
    audit shows sugars matter, do the real assignment with a carbohydrate-aware
    tool before trusting any per-sugar number.
    """
    ri = mol.GetRingInfo()
    sugar_rings = []

    for ring in ri.AtomRings():
        if len(ring) not in (5, 6):
            continue
        atoms = [mol.GetAtomWithIdx(i) for i in ring]
        oxygens = [a for a in atoms if a.GetSymbol() == "O"]
        carbons = [a for a in atoms if a.GetSymbol() == "C"]
        if len(oxygens) != 1 or len(carbons) != len(ring) - 1:
            continue
        if any(a.GetHybridization() != Chem.HybridizationType.SP3 for a in carbons):
            continue
        if any(a.GetIsAromatic() for a in atoms):
            continue

        # exocyclic oxygen substituents on ring carbons
        exo_o = 0
        has_methyl = False        # 6-deoxy sugars, e.g. rhamnose / fucose
        has_carboxyl = False      # uronic acids, e.g. glucuronic acid
        has_ch2oh = False         # hexose C6 hydroxymethyl
        for c in carbons:
            for nb in c.GetNeighbors():
                if nb.GetIdx() in ring:
                    continue
                if nb.GetSymbol() == "O":
                    exo_o += 1
                elif nb.GetSymbol() == "C":
                    nb_os = [x for x in nb.GetNeighbors()
                             if x.GetSymbol() == "O" and x.GetIdx() not in ring]
                    heavy_nb = [x for x in nb.GetNeighbors() if x.GetAtomicNum() > 1]
                    if len(heavy_nb) == 1:
                        has_methyl = True
                    elif len(nb_os) == 1 and nb.GetTotalNumHs() == 2:
                        has_ch2oh = True
                    elif len(nb_os) == 2:
                        has_carboxyl = True

        if exo_o < 2:
            continue

        if has_carboxyl:
            kind = "uronic-like"
        elif has_methyl:
            kind = "deoxyhexose-like"
        elif len(ring) == 6 and has_ch2oh:
            kind = "hexopyranose-like"
        elif len(ring) == 6:
            kind = "pentopyranose-like"
        else:
            kind = "furanose-like"

        sugar_rings.append({"size": len(ring), "kind": kind, "atoms": set(ring)})

    return sugar_rings


GLYCOSIDIC_BOND = Chem.MolFromSmarts("[C;R]([O;R])[O;!R]")   # anomeric C-O-R


def count_glycosidic_bonds(mol) -> int:
    """Count anomeric centres bearing an exocyclic oxygen (O-glycosidic links)."""
    if GLYCOSIDIC_BOND is None:
        return 0
    return len(mol.GetSubstructMatches(GLYCOSIDIC_BOND))


# --------------------------------------------------------------------------
# Stereochemistry
# --------------------------------------------------------------------------

def stereo_profile(mol):
    """Count defined vs undefined stereocentres and double-bond stereo."""
    try:
        centres = Chem.FindMolChiralCenters(
            mol, includeUnassigned=True, useLegacyImplementation=False)
    except Exception:
        centres = Chem.FindMolChiralCenters(mol, includeUnassigned=True)

    defined = sum(1 for _, lab in centres if lab not in ("?", None))
    undefined = sum(1 for _, lab in centres if lab in ("?", None))

    stereo_bonds = 0
    unspec_bonds = 0
    for b in mol.GetBonds():
        if b.GetStereo() != Chem.BondStereo.STEREONONE:
            stereo_bonds += 1
        elif (b.GetBondType() == Chem.BondType.DOUBLE
              and not b.GetIsAromatic()
              and not b.IsInRing()):
            begin_heavy = len([n for n in b.GetBeginAtom().GetNeighbors()
                               if n.GetAtomicNum() > 1])
            end_heavy = len([n for n in b.GetEndAtom().GetNeighbors()
                             if n.GetAtomicNum() > 1])
            if begin_heavy > 1 and end_heavy > 1:
                unspec_bonds += 1

    return {
        "defined_centres": defined,
        "undefined_centres": undefined,
        "total_centres": defined + undefined,
        "stereo_bonds": stereo_bonds,
        "unspecified_bonds": unspec_bonds,
        "fully_specified": undefined == 0 and unspec_bonds == 0,
        "flat": (defined + stereo_bonds) == 0,
    }


# --------------------------------------------------------------------------
# Diversity
# --------------------------------------------------------------------------

def diversity_metrics(fps, sample_n=3000, sedive_threshold=0.65, seed=0):
    """
    Internal diversity (mean pairwise Tanimoto distance) and a sphere-exclusion
    diversity estimate. Both computed on a random subsample for tractability.

    Per Skinnider 2021 and Renz 2024, internal diversity is a POOR guide to
    chemical-space coverage; it is reported here only because the review's
    homogeneity question is framed in those terms. Prefer SEDiv.
    """
    rng = random.Random(seed)
    if len(fps) > sample_n:
        fps = rng.sample(fps, sample_n)
    n = len(fps)
    if n < 2:
        return {"n_sampled": n, "int_div": None, "sediv": None}

    total, pairs = 0.0, 0
    for i in range(n - 1):
        sims = BulkTanimotoSimilarity(fps[i], fps[i + 1:])
        total += sum(sims)
        pairs += len(sims)
    int_div = 1.0 - (total / pairs) if pairs else None

    # Sphere exclusion: greedily pick centroids no closer than the threshold.
    picked = []
    for fp in fps:
        if not picked or max(BulkTanimotoSimilarity(fp, picked)) < sedive_threshold:
            picked.append(fp)
    return {
        "n_sampled": n,
        "int_div": round(int_div, 4) if int_div is not None else None,
        "sediv": round(len(picked) / n, 4),
        "sediv_threshold": sedive_threshold,
    }


# --------------------------------------------------------------------------
# Reporting helpers
# --------------------------------------------------------------------------

def pct(a, b):
    return 0.0 if not b else round(100.0 * a / b, 2)


def describe(values):
    if not values:
        return {}
    vs = sorted(values)
    n = len(vs)

    def q(f):
        return vs[min(n - 1, max(0, int(round(f * (n - 1)))))]

    return {"min": vs[0], "p25": q(.25), "median": q(.5),
            "p75": q(.75), "p95": q(.95), "max": vs[-1],
            "mean": round(sum(vs) / n, 2)}


def bar(frac, width=34):
    filled = int(round(frac * width))
    return "#" * filled + "." * (width - filled)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description="Audit a triterpenoid/saponin corpus against the review's thresholds.")
    ap.add_argument("path", help="corpus file (.smi/.txt/.csv/.tsv/.sdf)")
    ap.add_argument("--smiles-col", default=None, help="SMILES column for CSV/TSV input")
    ap.add_argument("--out", default=None, help="write full results as JSON")
    ap.add_argument("--write-subsets", action="store_true",
                    help="write glycosides.smi / aglycones.smi next to the input")
    ap.add_argument("--sample", type=int, default=3000,
                    help="subsample size for diversity metrics (default 3000)")
    args = ap.parse_args()

    total = parsed = failed = 0
    glycosides, aglycones = [], []
    sugar_kinds = Counter()
    sugars_per_mol, glyco_bonds_per_mol = [], []
    heavy_atoms, smiles_lens, mws = [], [], []
    n_flat = n_fully_specified = n_partial = 0
    defined_centres, undefined_centres = [], []
    scaffolds = Counter()
    fps = []
    fpgen = rdFingerprintGenerator.GetMorganGenerator(radius=3, fpSize=2048)

    for ident, smi, mol in load_molecules(args.path, args.smiles_col):
        total += 1
        if mol is None:
            failed += 1
            continue
        parsed += 1

        iso = Chem.MolToSmiles(mol, isomericSmiles=True)
        smiles_lens.append(len(iso))
        heavy_atoms.append(mol.GetNumHeavyAtoms())
        mws.append(Descriptors.MolWt(mol))

        rings = detect_sugar_rings(mol)
        nglyco = count_glycosidic_bonds(mol)
        sugars_per_mol.append(len(rings))
        glyco_bonds_per_mol.append(nglyco)
        for r in rings:
            sugar_kinds[r["kind"]] += 1

        (glycosides if rings else aglycones).append((ident, iso))

        st = stereo_profile(mol)
        defined_centres.append(st["defined_centres"])
        undefined_centres.append(st["undefined_centres"])
        if st["flat"]:
            n_flat += 1
        elif st["fully_specified"]:
            n_fully_specified += 1
        else:
            n_partial += 1

        try:
            scaffolds[MurckoScaffold.MurckoScaffoldSmiles(mol=mol)] += 1
        except Exception:
            pass

        if len(fps) < max(args.sample * 4, 20000):
            fps.append(fpgen.GetFingerprint(mol))

    if parsed == 0:
        sys.exit("No molecules parsed — check the file format and --smiles-col.")

    ngly, nagl = len(glycosides), len(aglycones)
    div = diversity_metrics(fps, sample_n=args.sample)
    long_skin = sum(1 for l in smiles_lens if l > SMILES_LEN_CUTOFF_SKINNIDER)
    long_guac = sum(1 for l in smiles_lens if l > SMILES_LEN_CUTOFF_GUACAMOL)
    over_moses = sum(1 for h in heavy_atoms if h > MOSES_MAX_HEAVY)
    over_guac = sum(1 for h in heavy_atoms if h > GUACAMOL_MAX_HEAVY)

    W = 68
    print("\n" + "=" * W)
    print("CORPUS AUDIT".center(W))
    print(os.path.basename(args.path).center(W))
    print("=" * W)

    print(f"\n[1] PARSING")
    print(f"    records read          : {total:,}")
    print(f"    parsed by RDKit       : {parsed:,}  ({pct(parsed, total)}%)")
    print(f"    failed to parse       : {failed:,}  ({pct(failed, total)}%)")

    print(f"\n[2] AGLYCONE : GLYCOSIDE SPLIT   <-- the key open quantity (R11)")
    print(f"    glycosides (>=1 sugar): {ngly:,}  ({pct(ngly, parsed)}%)  {bar(ngly / parsed)}")
    print(f"    aglycones  (no sugar) : {nagl:,}  ({pct(nagl, parsed)}%)  {bar(nagl / parsed)}")
    print(f"    sugars per molecule   : {describe(sugars_per_mol)}")
    print(f"    glycosidic bonds/mol  : {describe(glyco_bonds_per_mol)}")
    print(f"\n    Interpretation against the review's thresholds:")
    for label, n in (("glycoside subset", ngly), ("full corpus", parsed)):
        if n < TL_FLOOR_AMABILINO:
            verdict = f"BELOW the {TL_FLOOR_AMABILINO}-molecule TL floor (Amabilino 2020) -- do not fine-tune on this alone"
        elif n < 5000:
            verdict = "above the TL floor, but well below the ~15-22k where complex-NP models became reliable (Skinnider 2021)"
        elif n < PLANT_METABOLOME_SKINNIDER:
            verdict = f"approaching the plant-metabolome scale ({PLANT_METABOLOME_SKINNIDER:,}) that learned its space successfully"
        else:
            verdict = f"at or above the plant-metabolome scale ({PLANT_METABOLOME_SKINNIDER:,}) -- direct training supported"
        print(f"      {label:18s} n={n:,}: {verdict}")

    print(f"\n[3] SUGAR COMPOSITION  (shape heuristics, NOT monosaccharide assignment)")
    tot_rings = sum(sugar_kinds.values())
    if tot_rings:
        for kind, n in sugar_kinds.most_common():
            print(f"    {kind:22s}: {n:7,}  ({pct(n, tot_rings)}%)  {bar(n / tot_rings, 24)}")
    else:
        print("    no sugar-like rings detected")
    print("    NOTE: glucose/galactose/mannose are NOT distinguished here -- they differ")
    print("          only by stereochemistry. This is the R10 baseline, not the final metric.")

    print(f"\n[4] STEREOCHEMISTRY   <-- R12 / R7")
    print(f"    fully specified       : {n_fully_specified:,}  ({pct(n_fully_specified, parsed)}%)  {bar(n_fully_specified / parsed)}")
    print(f"    partially specified   : {n_partial:,}  ({pct(n_partial, parsed)}%)  {bar(n_partial / parsed)}")
    print(f"    completely flat       : {n_flat:,}  ({pct(n_flat, parsed)}%)  {bar(n_flat / parsed)}")
    print(f"    defined centres/mol   : {describe(defined_centres)}")
    print(f"    UNdefined centres/mol : {describe(undefined_centres)}")
    if pct(n_flat, parsed) > 20:
        print("    >> WARNING: a large flat fraction undermines the review's entire §5")
        print("       stereochemistry argument. Resolve provenance before training.")

    print(f"\n[5] SIZE AND STRING LENGTH   <-- R9")
    print(f"    heavy atoms           : {describe(heavy_atoms)}")
    print(f"    molecular weight      : {describe(mws)}")
    print(f"    isomeric SMILES length: {describe(smiles_lens)}")
    print(f"    longer than 250 chars : {long_skin:,}  ({pct(long_skin, parsed)}%)  [Skinnider 2021 cutoff]")
    print(f"    longer than 100 chars : {long_guac:,}  ({pct(long_guac, parsed)}%)  [GuacaMol cutoff]")
    print(f"    above MOSES max (27 HA): {over_moses:,}  ({pct(over_moses, parsed)}%)")
    print(f"    above GuacaMol max (88): {over_guac:,}  ({pct(over_guac, parsed)}%)")
    if pct(long_skin, parsed) > 5:
        print("    >> Choose model context length from the p95, not the median.")
        print("       This strengthens the case for S4 (Ozcelik 2024) over a plain RNN.")

    print(f"\n[6] DIVERSITY")
    print(f"    unique Murcko scaffolds: {len(scaffolds):,}  ({pct(len(scaffolds), parsed)}% of molecules)")
    top = scaffolds.most_common(5)
    if top:
        print(f"    top scaffold share     : {pct(top[0][1], parsed)}% of the corpus")
    print(f"    internal diversity     : {div['int_div']}   (poor guide -- Skinnider 2021, Renz 2024)")
    print(f"    SEDiv @ Tc<{div.get('sediv_threshold')}       : {div['sediv']}   (higher = better coverage)")
    print(f"    (computed on {div['n_sampled']:,} sampled molecules)")

    print("\n" + "=" * W)
    print("NEXT ACTIONS".center(W))
    print("=" * W)
    actions = []
    if pct(n_flat, parsed) > 20:
        actions.append("Resolve stereochemistry provenance in TeroKit before training (R12).")
    if ngly < TL_FLOOR_AMABILINO:
        actions.append("Glycoside subset is below the TL floor -- Stage 2 is not viable as planned.")
    elif ngly < 5000:
        actions.append("Glycoside subset is small; weight it up at Stage 1 rather than relying on Stage 2.")
    if pct(long_skin, parsed) > 5:
        actions.append("Set context length from the p95 SMILES length; evaluate S4.")
    if pct(ngly, parsed) < 30:
        actions.append("Aglycone-dominated corpus: consider a glycoside-weighted sampler (R11).")
    actions.append("Sweep augmentation over {1x,2x,3x,5x,10x} -- expect a LOW optimum at this corpus size (R3).")
    for i, a in enumerate(actions, 1):
        print(f"  {i}. {a}")
    print()

    if args.write_subsets:
        base = os.path.splitext(args.path)[0]
        for name, rows in (("glycosides", glycosides), ("aglycones", aglycones)):
            out = f"{base}_{name}.smi"
            with open(out, "w", encoding="utf-8") as fh:
                for ident, smi in rows:
                    fh.write(f"{smi}\t{ident}\n")
            print(f"  wrote {out}  ({len(rows):,} molecules)")
        print()

    if args.out:
        payload = {
            "input": args.path,
            "parsing": {"read": total, "parsed": parsed, "failed": failed},
            "split": {"glycosides": ngly, "aglycones": nagl,
                      "glycoside_pct": pct(ngly, parsed)},
            "sugar_kinds": dict(sugar_kinds),
            "sugars_per_mol": describe(sugars_per_mol),
            "stereo": {"fully_specified": n_fully_specified, "partial": n_partial,
                       "flat": n_flat,
                       "defined_centres": describe(defined_centres),
                       "undefined_centres": describe(undefined_centres)},
            "size": {"heavy_atoms": describe(heavy_atoms),
                     "mol_weight": describe(mws),
                     "smiles_len": describe(smiles_lens),
                     "over_250_chars": long_skin, "over_100_chars": long_guac},
            "diversity": {"murcko_scaffolds": len(scaffolds), **div},
        }
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"  wrote {args.out}\n")


if __name__ == "__main__":
    main()
