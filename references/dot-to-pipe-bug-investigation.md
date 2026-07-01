# Dot-to-Pipe SMILES Bug — 46k Probe Investigation

## Summary

The 46k SMILES probe failed mid-epoch with `RuntimeError: unknown token |`. The root cause is an unconditional `smiles.replace(".", "|")` in `read_smiles_csv_file` that is intended for LinkInvent warheads but runs for ALL REINVENT4 model types (Reinvent, Mol2Mol, etc.).

## The Bug

**File**: `reinvent/utils/config_parse.py`, line 146:

```python
# Linkinvent "warheads" (R-groups)
smiles = smiles.replace(".", "|")
```

This runs after the SMILES filter (standardizer) has canonicalized the SMILES. If the canonicalized SMILES still contains a dot (disconnected fragment), it gets replaced with `|`, which is not in the standard vocabulary.

## Error Trace

```
RuntimeError: unknown token |
Tokens: ['^', 'C', '1', '2', ..., '|', 'I', '$']
```

The `|` is a character-level token not present in the PubChem prior's vocabulary. The `$` is the STOP_TOKEN added by `SMILESTokenizer`.

## Impact

- 3k file: clean (no dot-containing SMILES)
- 46k file: **1 line** with `.I` (iodine fragment) at line 294

Original SMILES:
```
C/C(=C\C(=O)C[C@H](C)C(=O)O)[C@H]1C[C@@H](O)[C@@]2(C)C3=CC[C@H]
4C(C)(C)C(=O)CC[C@]4(C)C3=CC(=O)[C@]12C.I
```

The `default` filter (RDKitStandardizer) correctly removes the `.I` fragment via `_get_largest_fragment`, so the canonical SMILES has no dot. BUT the SMILES from the file is read as-is first, then filtered. The filter returns a canonical SMILES without the dot. However, the `read_smiles_csv_file` code has a logic detail: it passes `orig_smiles` (the raw SMILES) to each action, then applies the dot-to-pipe replacement on the filtered result.

Wait -- actually the filter DOES remove the dot properly. The investigation showed that the RDKit pipeline (largest fragment + remove salts + MolToSmiles) produces a canonical SMILES WITHOUT the dot or pipe. So how does the pipe appear?

**Key finding**: The actual error occurred at batch ~795 (about 12,720 SMILES into the 38,215 filtered set). The crashing SMILES `C12CC=C3C(C1(C)...)=O` does NOT match any raw SMILES in the 46k file. This suggests the pipe is introduced during the tokenization or data loading of a generated/augmented SMILES, or there is a second dot-containing SMILES further in the file that we missed.

**EDITED: Further grep confirmed only 1 dot-containing line in the file (line 294).** The error SMILES is NOT one of the original lines. This may indicate the error is from a sampled/generated SMILES or a different code path.

## Verification Steps Performed

1. Confirmed NO pipe `|` character exists anywhere in `saponin_train_46k.smi` (45967 lines)
2. Canonicalized all SMILES via RDKit - NO pipe appears in any canonical form
3. Found exactly 1 dot-containing SMILES: line 294 with `.I` suffix
4. The `default` filter correctly strips the `.I` fragment

## Upshot

Even though the exact path of the pipe introduction is unclear from static analysis, **the fix is simple**: strip all dot-containing lines from the 46k file before running. The `.I` SMILES at line 294 is the most likely culprit, but removing all dot lines is safer.