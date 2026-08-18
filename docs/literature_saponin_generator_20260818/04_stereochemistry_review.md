# Stereochemistry Review

## A. Representation comparison, specifically for saponins

Saponins are a worst case for string-based stereochemistry: a polycyclic triterpenoid or
steroidal aglycone (typically 6–8 stereocenters on the ring system alone) plus one or more sugar
rings, each sugar contributing its own ring stereocenters *and* an anomeric center at the
glycosidic linkage. A representation that "supports" stereochemistry in the abstract can still
fail badly here if it wasn't trained on anything this stereochemically dense.

| Representation | Stereo mechanism | Fit for polycyclic aglycones | Fit for multi-sugar chains | Fit for anomeric/glycosidic stereo | Evidence tier |
|---|---|---|---|---|---|
| Isomeric SMILES | `@`/`@@` (tetrahedral), `/`\`\`` (E/Z) as ordinary characters in the string | Works but every stereocenter is a fragile, order-dependent local annotation; long strings compound the risk of a single dropped/misplaced symbol invalidating or mis-specifying stereochemistry | Same fragility repeated per sugar ring; string gets long and repetitive | Representable, but nothing about SMILES *enforces* that an anomeric center is even specified — omission is silent | This project's current representation (in-repo, C01) |
| Randomized isomeric SMILES | Same tokens, different traversal order/starting atom per sample | Same per-symbol fragility, but training on many random traversals is exactly the augmentation strategy shown to improve chemical-space coverage for RNN-based CLMs (Arus-Pous et al. 2019, [search]) | Same augmentation benefit | Same benefit | Strong external evidence (C_bib: Arus-Pous 2019) |
| SELFIES | Grammar-constrained; syntactically every string decodes to a valid molecular graph | Removes the "invalid SMILES" failure mode entirely; does **not** by itself guarantee a stereocenter is specified — it just guarantees the *string* is valid | Same guarantee, same caveat | Same guarantee, same caveat | [search], C10 |
| Group SELFIES | SELFIES + fragment/group tokens; explicit `=`, `#`, `\`, `/` stereo modifiers on token attachments (confirmed quote, C14) | Best-in-class *in principle*: a custom "sugar ring" or "steroid core" group token could carry its stereochemistry as a unit rather than N independent symbols | Directly designed for exactly this: repeated fragment motifs (multiple sugar units) become single tokens instead of long repeated symbol runs | Same — a "glycosidic linkage" group token could encode the anomeric configuration as part of the token definition | [search], C14 — **no pretrained checkpoint exists in this representation for any domain**, so this is a from-scratch build, not a fine-tune |
| Molecular graph w/ stereo labels | Chiral tags on nodes, cis/trans on edges | Handles ring stereocenters natively; historically many graph generators (this era) did not model stereochemistry at all (C17) | Same | Anomeric stereo is a node-label problem, tractable but unbenchmarked for saponins | [search], C17 — largely unconfirmed for the specific models surveyed |
| 3D coordinates / diffusion | Stereochemistry is an emergent property of 3D geometry, not a separate symbol | Most *faithful* representation in principle (GCDM explicitly markets itself as "chirality-aware", C18) | Same, but computationally far more expensive per sample and validated in the literature found this session only at drug-like/benchmark atom counts, well under a full saponin | Anomeric configuration is a natural 3D-geometric fact, but requires generating a full 3D conformer per sample and correctly deriving 2D+stereo SMILES back out (itself lossy) | [search], C18 — **zero saponin/glycoside benchmark evidence found this session** |

### Key external evidence
Tom et al. 2025 (C21, [search]) directly compared stereochemistry-aware vs. stereochemistry-
unaware string generation and found stereo-aware models "generally perform on par with or
surpass conventional algorithms across various stereochemistry-sensitive tasks" **but** "in
scenarios where stereochemistry plays a less critical role, stereochemistry-aware models may face
challenges due to the increased complexity of the chemical space they must navigate." Read
plainly: modeling stereochemistry is not free — it enlarges the search space the model has to
learn — but for a project whose entire deliverable is "true or highly plausible saponins," that
cost is the right one to pay. This paper's benchmark-task DESIGN (not its specific results, which
were not read in full text) is the recommended template for section C below.

## B. Recommendation for this project

1. **Keep isomeric SMILES as the primary representation now.** It is what this project's existing
   REINVENT4 pipeline already uses (`configs/sampling/*.toml` expose an `isomeric_smiles` flag),
   it has by far the most mature tooling (RDKit round-trips), and switching representations
   entirely is a much bigger project than fixing preprocessing/validation gaps in the current one.
2. **Add randomized isomeric SMILES augmentation for training data**, not just canonical SMILES,
   following Arus-Pous et al. 2019 — but generate the randomizations **before** any train/val/
   test split so augmented variants of the same parent molecule never leak across a split (see
   `06_dataset_and_finetuning_plan.md`).
3. **Build a parallel SELFIES baseline** (using ChemGPT, C10, or a from-scratch SELFIES tokenizer
   over this project's own data) specifically as the validity-oriented comparison arm required by
   the benchmark plan — not as a representation switch for the main line.
4. **Defer Group SELFIES.** It has the best theoretical stereochemistry properties of any string
   representation reviewed (explicit stereo modifiers on fragment tokens, natural fit for repeated
   sugar-ring motifs) but there is no pretrained checkpoint in this representation for any domain,
   so adopting it means designing a saponin-specific fragment/group library and training from
   scratch — real engineering work, correctly scoped as `FUTURE_WORK` once the SMILES-GPT line has
   a working baseline to compare against.
5. **Defer graph/3D models entirely for this phase.** They are the only representations with a
   plausible claim to *native* stereochemical fidelity, but every candidate found this session was
   benchmarked at atom-counts well below a full triterpenoid saponin, and 3D diffusion training is
   explicitly GPU-heavy — directly excluded by this project's current-phase constraints.

## C. Mandatory stereochemical validation specification (RDKit-based)

Every generated SMILES — from any candidate model — must pass through this pipeline before being
counted as a "valid saponin candidate" anywhere in the benchmark plan or downstream screening
module:

```python
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit.Chem.EnumerateStereoisomers import EnumerateStereoisomers

def stereo_validate(smiles: str) -> dict:
    """Returns a structured verdict; never silently coerces a molecule into 'valid'."""
    result = {"input_smiles": smiles, "valid": False}

    # 1. Parse WITHOUT sanitizing first, so we can distinguish parse failure from
    #    sanitization failure (different failure modes, log them differently).
    mol = Chem.MolFromSmiles(smiles, sanitize=False)
    if mol is None:
        result["failure"] = "PARSE_FAILURE"
        return result

    # 2. Sanitize explicitly and catch the exception rather than relying on
    #    MolFromSmiles's default (which silently returns None on failure and
    #    hides WHICH sanitization step failed).
    try:
        Chem.SanitizeMol(mol)
    except Exception as e:
        result["failure"] = f"SANITIZE_FAILURE: {e}"
        return result

    # 3. Reject radicals / open-shell structures explicitly. A generative model
    #    can emit a syntactically valid SMILES for an open-shell species; this is
    #    almost never a real saponin.
    if any(atom.GetNumRadicalElectrons() != 0 for atom in mol.GetAtoms()):
        result["failure"] = "RADICAL_OPEN_SHELL"
        return result

    # 4. Reject disconnected fragments (salts, counter-ions, mixtures) unless the
    #    project's data-quality tier explicitly allows them (see tier policy in
    #    06_dataset_and_finetuning_plan.md).
    frags = Chem.GetMolFrags(mol, asMols=False)
    if len(frags) > 1:
        result["failure"] = "DISCONNECTED_FRAGMENTS"
        result["fragment_count"] = len(frags)
        return result

    # 5. Enumerate stereocenters INCLUDING unassigned ones. This is the step most
    #    generic pipelines skip, and skipping it is exactly how "novelty" gets
    #    silently measured on connectivity alone instead of full stereochemistry.
    stereo_centers = Chem.FindMolChiralCenters(
        mol, includeUnassigned=True, useLegacyImplementation=False
    )
    n_defined = sum(1 for _, tag in stereo_centers if tag not in ("?",))
    n_unassigned = sum(1 for _, tag in stereo_centers if tag == "?")

    # 6. Double-bond (E/Z) stereo, same defined-vs-unassigned split.
    Chem.FindPotentialStereoBonds(mol)
    ez_bonds = [
        b for b in mol.GetBonds()
        if b.GetStereo() != Chem.BondStereo.STEREONONE
        or b.GetStereo() == Chem.BondStereo.STEREOANY
    ]
    n_ez_defined = sum(
        1 for b in mol.GetBonds() if b.GetStereo() in (
            Chem.BondStereo.STEREOE, Chem.BondStereo.STEREOZ,
            Chem.BondStereo.STEREOCIS, Chem.BondStereo.STEREOTRANS,
        )
    )
    n_ez_unassigned = sum(
        1 for b in mol.GetBonds() if b.GetStereo() == Chem.BondStereo.STEREOANY
    )

    # 7. Canonical isomeric SMILES + isomeric InChIKey, for dedup and novelty
    #    checks that are actually stereo-aware (see warning D below).
    canonical_isomeric_smiles = Chem.MolToSmiles(mol, isomericSmiles=True, canonical=True)
    try:
        inchikey = Chem.MolToInchiKey(mol)
    except Exception:
        inchikey = None  # some structures (e.g. certain macrocycles) can fail InChI generation

    result.update({
        "valid": True,
        "n_stereocenters_defined": n_defined,
        "n_stereocenters_unassigned": n_unassigned,
        "n_ez_defined": n_ez_defined,
        "n_ez_unassigned": n_ez_unassigned,
        "fully_stereo_defined": (n_unassigned == 0 and n_ez_unassigned == 0),
        "canonical_isomeric_smiles": canonical_isomeric_smiles,
        "isomeric_inchikey": inchikey,
    })
    return result
```

Required downstream policy built on top of this function:

- **Reject-by-default policy for generation benchmarking**: a generated molecule only counts
  toward "valid saponin candidate" metrics if `valid=True` AND `fully_stereo_defined=True`. Molecules
  with unassigned stereocenters are tracked separately (`n_stereocenters_unassigned` histogram) —
  never silently dropped from reporting, never silently counted as passing.
- **Stereo-aware deduplication**: dedupe on `canonical_isomeric_smiles` (or `isomeric_inchikey`),
  never on a non-isomeric canonical SMILES. Two molecules that differ only in one stereocenter are
  *different* molecules for this project's purposes and must not collapse into one row.
- **Stereo-aware novelty**: "novel vs. training set" must be computed on the same
  `canonical_isomeric_smiles`/`isomeric_inchikey` key used for dedup. A molecule that matches the
  training set in connectivity but differs in stereochemistry is **not** automatically novel or
  automatically a match — it must be reported as its own category ("connectivity-match,
  stereochemistry-differs") because both "silently counted as novel" and "silently counted as a
  training-set match" are misleading in different ways.
- **Chiral-center distribution comparison**: histogram `n_stereocenters_defined` (and separately
  `n_ez_defined`) for generated vs. training molecules. A generator that systematically produces
  fewer defined stereocenters than the training distribution is under-specifying stereochemistry
  even if every individual molecule parses as "valid."
- **Manual chemical review queue**: flag for human review any molecule where
  `n_stereocenters_unassigned > 0` but the model's log-likelihood/confidence was high, and any
  molecule whose implied ring system is chemically implausible (e.g. a "sugar ring" with the wrong
  ring size or a stereocenter pattern inconsistent with any known aglycone family) — motif-rule
  screens can both over- and under-flag, so this queue is advisory input to a person, not an
  automatic accept/reject gate.

## D. Explicit warnings (do not violate these)

1. **Do not strip stereochemistry during training.** The "67 million natural product" generator
   (C07) did exactly this and it is the single clearest disqualifying example found this session:
   scale (67M compounds) and natural-product focus did not compensate for training on
   de-stereochemicalized SMILES. A model trained this way cannot produce stereochemically faithful
   saponins by construction, no matter how it is fine-tuned afterward, because the information was
   never in the training signal.
2. **Do not treat non-isomeric novelty as stereo-aware novelty.** Computing novelty on
   connectivity-only canonical SMILES will systematically overstate how "novel" the model's output
   is, because it collapses every stereoisomer of a training-set molecule into a false match — or,
   just as bad, calling a connectivity-match-but-different-stereochemistry molecule "novel" when
   it is really an unintended stereoisomer error.
3. **Do not generate connectivity and then blindly enumerate all stereoisomers** (e.g. via
   `EnumerateStereoisomers`) to "fill in" missing stereochemistry. This manufactures the
   *appearance* of stereo-completeness without the model having learned anything about which
   stereoisomer is actually plausible or biosynthetically real — it would defeat the entire
   point of a stereochemically faithful generator and must not be used as a substitute for genuine
   stereo-aware generation or genuine (flagged, human-reviewed) imputation.
4. **Do not rely on valid-SMILES rate alone** as a stereochemistry quality signal. A SMILES string
   can be 100% RDKit-valid while having every stereocenter unassigned; validity and stereo-
   completeness are orthogonal metrics and must be reported separately (see the benchmark plan's
   metric list, items 1 and 8–10).
5. **Do not assume a model trained mostly on small drug-like molecules learns sugar
   stereochemistry reliably.** None of the drug-like-scale candidates reviewed (MolGPT, generic
   Chemformer/MolBART, SMILES Transformer) were shown to include meaningful carbohydrate/glycoside
   representation in their pretraining corpora, and general literature on transformer
   stereochemistry (chirality-recognition difficulty for transformer architectures, [search])
   suggests stereo-sensitive generalization is not a free byproduct of general chemical
   pretraining — it needs to be specifically evaluated, and very likely specifically trained for,
   on saponin-like structures.
