# Dataset and Fine-Tuning Plan

## A. Four-tier data hierarchy

### Tier 1 — General chemical pretraining corpus
- **Lawful public sources**: PubChem (this project's existing REINVENT4 prior, `reinvent_pubchem.prior`,
  is already built on this — in-repo, `priors/README.md`); ChEMBL; ZINC. Any of the pretrained
  checkpoints in `02_candidate_models.csv` (smiles-gpt/PubChem10M, ChemGPT/PubChem10M) count as an
  already-done Tier 1 for candidates C09/C10.
- **License considerations**: PubChem and ChEMBL data are generally open for research use;
  redistribution terms differ by source and were NOT independently re-verified this session — flag
  for confirmation before any redistribution (as opposed to internal training use).
- **Stereochemistry retention**: MUST retain isomeric SMILES at this tier if the goal is a
  stereo-capable model downstream — stripping stereochemistry here (as C07's "67 million" generator
  did) cannot be undone by later fine-tuning tiers.
- **Expected size**: 1M–10M+ molecules, per the existing candidates surveyed.
- **Cleaning/curation needs**: standard sanitize/canonicalize pass (RDKit), remove obvious parsing
  failures; this project's own base prior already reflects this tier and does not need to be
  redone.
- **Duplicate policy**: dedupe on canonical isomeric SMILES (or isomeric InChIKey).
- **Salt/mixture policy**: at Tier 1 scale, keeping multi-fragment entries with a documented flag
  is reasonable (they are useful pretraining signal); Tier 3/4 should exclude or explicitly
  desalt them (see below).
- **Tautomer / charged-species / disconnected-fragment / radical / isotope policy**: follow
  whatever policy the base checkpoint (e.g. smiles-gpt's PubChem10M source) already used; not
  independently re-derivable this session without cloning and inspecting its preprocessing code.
- **QC**: spot-check a random sample against RDKit sanitize + the stereo-validation function in
  `04_stereochemistry_review.md` §C.

### Tier 2 — Natural-product adaptation corpus
- **Lawful public sources**: COCONUT (used by NPGPT/C06, the "67M" generator/C07, and NaFM/C08);
  LOTUS (structure–organism pairs, 750,000+ per WebSearch synthesis this session).
- **License considerations**: COCONUT and LOTUS are both described in the literature found this
  session as open/community resources; exact redistribution license text was NOT independently
  read this session (COCONUT's own site was not reachable) — confirm before redistributing a
  derived dataset externally.
- **Stereochemistry retention**: **mandatory** — this is exactly the tier where C07's mistake
  (stripping stereo before training) must not be repeated. If sourcing SMILES from COCONUT,
  verify isomeric SMILES are pulled, not a de-stereochemicalized export.
- **Expected size**: COCONUT is commonly cited in the low-hundred-thousands to ~600K+ range across
  the sources found this session (NaFM's ~0.6M figure, the "67M" generator's 406,919-molecule
  snapshot at the time of that study); exact current count needs a direct COCONUT query, not
  performed this session (site unreachable).
- **Cleaning/curation needs**: NPClassifier pass (already available in this project — see
  `references/fcd_npclassifier_api.md`) to tag pathway/superclass/class and the `isglycoside` flag,
  which is directly useful for pre-filtering toward saponin-relevant entries before Tier 3/4.
- **Duplicate policy / salt / tautomer / charged / disconnected / radical / isotope policy**: same
  principles as Tier 1, applied to the NP subset; natural products more frequently include salts
  (e.g. glycoside salts) and charged species than drug-like corpora, so this policy needs explicit
  documentation rather than inheriting Tier 1's defaults unexamined.
- **Molecular-weight and token-length distribution requirements**: compute and record explicitly
  (this is also required for the 512-token analysis in `05_long_context_512_review.md` §D.1) —
  natural products have a much longer right tail than drug-like corpora, and Tier 2 is where that
  tail first appears.

### Tier 3 — Curated triterpenoid/steroidal aglycone corpus
- **Lawful public sources**: TeroKit (already named in this project's context as the origin of its
  existing triterpenoid dataset — C19); LOTUS filtered to terpenoid/steroid biosynthetic classes.
- **License considerations**: TeroKit is described as free for **academic use**; bulk-download/
  redistribution rights were NOT confirmed this session (site not reached) — treat as a required
  manual/legal check before large-scale scraping, not an assumption.
- **Stereochemistry retention**: mandatory, same as Tier 2.
- **Expected size**: TeroKit's TeroMOL module is described as ~180,000 terpenome molecules
  (WebSearch synthesis) across all terpenoid classes, of which the triterpenoid/steroid-relevant
  subset (and further, the subset with a plausible saponin-precursor aglycone) is a smaller
  fraction not quantified this session.
- **Cleaning/curation needs**: this is the tier where aglycone-family labeling matters most —
  classify each entry into the families the project already names (oleanane, ursane, lupane,
  dammarane, lanostane, cycloartane, cucurbitane, steroidal/spirostane/furostane) using a
  combination of NPClassifier's class-level output (already returns e.g. "Lanostane, Tirucallane
  and Euphane triterpenoids" per this project's own `metrics/e1_vs_e4_npc.json`) and rule-based
  scaffold matching (Bemis-Murcko + substructure SMARTS for each named skeleton), documented as an
  explicit, versioned rule set — not a black box.
- **Duplicate / salt / tautomer / charged / disconnected / radical / isotope policy**: same
  principles as Tier 2; this tier's smaller size makes manual/spot-check QC more feasible per
  entry than at Tier 1/2 scale.

### Tier 4 — Verified saponin fine-tuning corpus
- **Lawful public sources**: the saponin-specific subset of Tier 3 (aglycone confirmed AND at
  least one sugar residue attached via a glycosidic linkage, per this project's own working
  definition of a saponin), further checked against `isglycoside=True` from NPClassifier.
- **License considerations**: inherits Tier 3's constraints.
- **Stereochemistry retention**: mandatory, with the full validation pipeline from
  `04_stereochemistry_review.md` §C applied to every entry, including explicit tracking of how
  many entries have fully-defined stereochemistry vs. partial/unassigned — this project's actual
  training signal quality depends entirely on this tier being clean.
- **Expected size**: smallest tier by construction; this project's existing 46k-molecule TL corpus
  (`data/saponin_train_46k_valid.smi`) is **not** itself a verified-saponin-only corpus (per this
  project's own `reports/46k_prior_epoch_comparison.md`, the training set is a broader PubChem-
  derived TL set filtered toward triterpenoid-like chemistry, not a strict saponin definition) —
  building a true Tier 4 is new work, not something already done in this repository.
- **Cleaning/curation needs**: this is where sugar-count, sugar-identity, and glycosidic-linkage
  annotation happen (see metadata schema below) — the highest-value, highest-effort curation tier.
- **Duplicate / salt / tautomer / charged / disconnected / radical / isotope policy**: strictest —
  Tier 4 should generally exclude disconnected fragments, radicals, and non-neutral species unless
  a specific, documented reason exists to keep them (e.g. a known bioactive saponin salt form).

## B. Recommended metadata schema for the Tier 4 saponin dataset

```
molecule_id, source_database, source_accession, name,
isomeric_smiles, canonical_isomeric_smiles, inchikey,
molecular_formula, exact_mass, molecular_weight,
aglycone_family, aglycone_scaffold, steroidal_or_triterpenoid,
number_of_sugar_units, sugar_identity_list, glycosidic_linkage_annotations,
glycosylation_positions,
NPClassifier_pathway, NPClassifier_superclass, NPClassifier_class,
stereocenter_count, unassigned_stereocenter_count, double_bond_stereo_count,
token_length, data_quality_tier, split_group, source_reference
```

Notes on fields that need a defined procedure, not just a column name:
- `aglycone_scaffold` — recommend Bemis-Murcko scaffold SMILES of the aglycone *after* removing
  sugar substituents (requires a glycosidic-bond-cleaving preprocessing step, not just a generic
  scaffold function on the whole molecule, which would keep sugars attached).
- `sugar_identity_list` / `glycosidic_linkage_annotations` / `glycosylation_positions` — these
  require either (a) provenance metadata from the source database (if TeroKit/LOTUS/COCONUT
  records carry this), or (b) a rule-based sugar-ring detection + substructure match against known
  monosaccharide patterns (glucose, arabinose, rhamnose, xylose, glucuronic acid, etc., the common
  saponin sugar units) plus glycosidic-oxygen bond identification. This is nontrivial cheminformatics
  work and should be scoped as its own task, not assumed to be a one-line RDKit call.
- `token_length` — must be computed per the tokenizer actually used by whichever candidate model
  is under test (see `05_long_context_512_review.md`), not a single fixed number across all
  models being benchmarked.
- `data_quality_tier` — records which of Tiers 1–4 (or a finer sub-grade) an entry belongs to,
  so downstream training/eval code can filter by quality without re-deriving it.

## C. Split strategy

**Primary split: aglycone-family/scaffold-aware.** Group all molecules sharing an `aglycone_scaffold`
(or, more coarsely, `aglycone_family`) into the same split (train, validation, or test) — never
split within a family. **Secondary split: random**, computed independently, kept only for
diagnostic comparison against the primary split.

**Why random-only splitting overestimates performance for closely related saponins**: saponins
within the same aglycone family very often differ only in sugar composition/count or minor
oxidation pattern — i.e. they are near-duplicates in the chemically relevant sense even when their
full SMILES differ. A random split will frequently place near-duplicate saponins on both sides of
the train/test boundary, so a model can appear to "generalize" to the test set by essentially
memorizing a close relative it saw in training. The scaffold/family-aware split is the only one
that actually tests whether the model has learned the *general* rules of a saponin family (sugar
attachment patterns, plausible substitution positions) rather than interpolating between near-
duplicate training examples. Report **both** splits' results side by side, and treat a large gap
between them as a memorization warning sign, not just report the higher (random-split) number.

## D. Augmentation

- **Randomized isomeric SMILES**, generated from each Tier 4 parent molecule, per Arus-Pous et al.
  2019 (`09_bibliography.csv`) — the augmentation must preserve full stereochemistry (i.e. use
  RDKit's `doRandom=True` with `isomericSmiles=True`, never `isomericSmiles=False`).
- **Practical maximum augmentations per parent molecule**: recommend starting at 5–10x per parent
  for Tier 4 (small, high-value dataset) rather than the 100x+ sometimes used for large drug-like
  corpora — Tier 4 is expected to be small enough that over-augmenting risks the model
  over-weighting a handful of parent scaffolds' *specific* randomized traversals rather than
  learning general structure. Tune based on the actual Tier 4 size once curated.
- **Split before augmenting**: assign each *parent* molecule to train/val/test (per the
  aglycone-family split in C) **before** generating any randomized variants, and keep all variants
  of a given parent in the same split. Augmenting before splitting is a direct and easy-to-miss
  source of train/test leakage — if a model sees one random traversal of a molecule in training and
  a different random traversal of the *same* molecule in test, the "novelty"/"generalization"
  metrics on that molecule are meaningless.
