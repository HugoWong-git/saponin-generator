# Search Log

Session date: **2026-08-18**. All times/order reflect the sequence performed in this session.

## 0. Pre-search verification (per task instructions)

```
git remote -v         -> origin https://github.com/HugoWong-git/saponin-generator
git branch --show-current -> claude/molecular-generator-prior-review-uchhki
git status             -> clean, on the correct branch
```

Checked for directories the task brief described as pre-existing: `archive/`, `checkpoints/`,
`docs/`, `experiments/`, `external/`, `src/`, `literature/`. **None exist.** Checked for the named
scripts (`scripts/agentic_triterpenoid_train.py`, `src/experiment/finetune_triterpenoid_v1.py`,
`scripts/sample_triterpenoid_dryrun.py`, `scripts/evaluate_generated_triterpenoid.py`,
`scripts/smi_to_csv.py`, `scripts/run_pk_eval_for_run.sh`) via `find` over the whole repo tree —
**none exist**. See `00_README.md` for the resolution of this discrepancy.

Actually-existing repository materials that WERE reused as primary evidence:
- `README.md`, `pyproject.toml` — project identity, dependencies (rdkit, fcd, requests/NPClassifier client)
- `priors/README.md` — describes the 4 epoch checkpoints already trained
- `reports/46k_prior_epoch_comparison.md` — full metrics for the existing REINVENT4 saponin fine-tune
- `references/fcd_npclassifier_api.md` — working NPClassifier API usage notes (endpoint, rate limit, response schema)
- `references/dot-to-pipe-bug-investigation.md` — unrelated to this review's scope, not used
- `configs/tl/*.toml`, `configs/sampling/*.toml` — exact hyperparameters of the current pipeline
- `metrics/e1_vs_e4_npc.json` — existing NPClassifier evaluation output format

## 1. Network reachability testing

Tested `WebFetch` against a spread of domains to determine what could be directly read this
session (as opposed to relying on `WebSearch` snippet synthesis). Results:

| Domain | Status |
|---|---|
| `github.com/MolecularAI/REINVENT4` | OK (README fetched, low technical detail) |
| `huggingface.co` | EGRESS_BLOCKED |
| `raw.githubusercontent.com/ohuelab/npgpt/...` | OK |
| `raw.githubusercontent.com/sanjaradylov/smiles-gpt/...` | OK |
| `raw.githubusercontent.com/ncfrey/molgen/...` | 404 (wrong path guessed, not a block) |
| `raw.githubusercontent.com/datamol-io/safe/...` | OK |
| `link.springer.com` (REINVENT4 paper) | EGRESS_BLOCKED |
| `jcheminf.biomedcentral.com` (same paper, alt host) | EGRESS_BLOCKED |
| `arxiv.org` (Olivecrona 2017) | EGRESS_BLOCKED |
| `pmc.ncbi.nlm.nih.gov` | EGRESS_BLOCKED |
| `www.nature.com` | EGRESS_BLOCKED |
| `pubs.acs.org` | EGRESS_BLOCKED |
| `chemrxiv.org` | EGRESS_BLOCKED |
| `zenodo.org` | EGRESS_BLOCKED |
| `www.biorxiv.org` | EGRESS_BLOCKED |
| `pubs.rsc.org` | EGRESS_BLOCKED |

**Conclusion applied for the rest of the session:** use `WebSearch` (which itself can read these
sites server-side and returns synthesized snippets with source URLs) as the primary research tool;
use `WebFetch` only against `github.com`/`raw.githubusercontent.com` for direct primary-source
confirmation of code repositories.

## 2. Query families run (WebSearch), in order

1. `REINVENT prior model SMILES RNN generative chemistry pretrained prior transfer learning`
2. `Segler 2018 generating focused molecule libraries recurrent neural network transfer learning fine-tuning`
3. `catastrophic forgetting fine-tuning chemical language model small dataset molecular generative model few-shot`
4. `generative model natural products terpenoid saponin de novo design deep learning`
5. `Moret Grisoni generative molecular design low data regimes transfer learning temperature sampling chemical language model`
6. `Reinvent 4 Mol2Mol similarity pairs transfer learning Tanimoto threshold molecular transformer`
7. `MOSES GuacaMol benchmark molecular generative models validity uniqueness novelty Frechet ChemNet distance critique`
8. `effect of pretraining dataset ChEMBL ZINC PubChem on generative prior quality molecular language model`
9. `Olivecrona molecular de novo design augmented likelihood prior regularization reinforcement learning sigma mode collapse diversity filter`
10. `natural product likeness score Ertl NPClassifier ontology natural product classification generative model evaluation`
11. `SELFIES SAFE molecular representation 100% validity generative model comparison SMILES`
12. `chemical language model stereochemistry glycosides macrocycles limitations SMILES generation complex natural products`
13. `MolGPT GPT molecule generation Bagal 2021 conditional generation SMILES transformer architecture`
14. `ChemGPT Frey neural scaling deep chemical models GPT-neo SELFIES pretraining PubChem10M`
15. `Chemformer Irwin 2022 BART pretrained molecular transformer SMILES masked span`
16. `SMILES Transformer Honda 2019 pretrained molecular representation autoencoder`
17. `smiles-gpt GitHub sanjaradylov pretrained GPT2 SMILES tokenizer model card`
18. `Group SELFIES Cheng 2023 fragment-based molecular string representation stereochemistry`
19. `SAFE sequential attachment-based fragment embedding Noutahi datamol GPT2 molecular generation GitHub`
20. `MolMIM NVIDIA BioNeMo molecular generative model mutual information machine controlled generation`
21. `GraphINVENT GraphAF graph autoregressive molecule generation stereochemistry chirality node`
22. `TeroKit terpenoid database machine learning virtual screening triterpenoid`
23. `tetrahedral chirality generation deep learning molecular graph 3D diffusion stereocenter assignment correctness`
24. `"Stereochemistry-aware string-based molecular generation" PNAS Nexus 2025 method isomeric SMILES SELFIES chirality`
25. `saponin generative model deep learning "saponin" AND (generat* OR "de novo") molecule design 2023 2024 2025`
26. `"67 million natural product" molecular language processing SMILES GPT dataset generation methodology architecture`
27. `"Learning the chemical language of natural products" Nature Machine Intelligence 2026 generative model`
28. `positional embedding extension context length transformer interpolation RoPE long sequence fine-tuning small model`
29. `SMILES string length distribution natural products glycosides token count tokenizer BPE character-level chemical language model`
30. `NaFM natural products foundation model Guo Rava Walker 2026 architecture SMILES stereochemistry pretraining`
31. `ginsenoside triterpenoid glycoside generative adversarial network variational autoencoder de novo design machine learning`
32. `REINVENT4 Reinvent prior RNN architecture GRU three-layer 512 hidden units vocabulary PubChem training set size`
33. `stereochemistry stripped removed preprocessing SMILES generative model common practice canonicalization RDKit RemoveStereochemistry training data`

Plus direct `WebFetch` reads of: `github.com/MolecularAI/REINVENT4` (README),
`raw.githubusercontent.com/sanjaradylov/smiles-gpt/master/README.md`,
`raw.githubusercontent.com/ohuelab/npgpt/main/README.md`,
`raw.githubusercontent.com/datamol-io/safe/main/README.md`.

## 3. Key outcomes and dead ends

- **No saponin-specific, triterpenoid-glycoside-specific, or steroidal-glycoside-specific
  pretrained generator was found by query #25 or any other query this session.** This directly
  supports the required statement in `08_model_recommendation.md`: *"No verified public
  pretrained saponin-specific generator was identified as of the search date."*
- Query #4 and #31 (saponin/ginsenoside + generative model) returned only generic de novo design
  surveys with no saponin-specific hits — a genuine negative result, not a search failure (the
  same query pattern reliably surfaces specific papers for other topics in this log).
- The single closest match is **NPGPT** (query #17/#6 area) — a natural-product generator (COCONUT-
  trained), not saponin-specific, with undocumented stereochemistry handling in its README.
- `raw.githubusercontent.com/ncfrey/molgen/main/README.md` returned 404 — this was a guessed path
  for the ChemGPT training-code repository, not a confirmed dead link for the project itself;
  ChemGPT's actual checkpoints are HuggingFace-hosted (`ncfrey/ChemGPT-*`), which could not be
  fetched directly (HuggingFace blocked).
- DOIs were largely NOT independently confirmed this session, since resolving a DOI typically
  requires fetching the publisher page (blocked). Where a DOI is stated in `09_bibliography.csv`
  or `02_candidate_models.csv` it is marked `NOT_VERIFIED_THIS_SESSION`/`NEEDS_LOCAL_VERIFICATION`
  rather than asserted as confirmed.

## 4. Sources NOT consulted (out of the allowed list, or simply not reached)

- Europe PMC, OpenAlex, Crossref, DOAJ, Figshare — not queried directly this session (WebSearch's
  synthesis effectively substituted for a first pass across indexed literature, but a systematic
  Crossref/OpenAlex API sweep was not performed and would be a reasonable follow-up).
- No Sci-Hub, Library Genesis, or any paywall-bypass method was used or considered, per the task's
  legal/ethical source policy.
