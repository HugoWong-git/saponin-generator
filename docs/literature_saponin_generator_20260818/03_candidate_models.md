# Candidate Models — Narrative Comparison

Full structured data: `02_candidate_models.csv` (21 rows × 61 columns). This file is the readable
walkthrough. Every claim below is qualified by its evidence tier from that CSV:
**[repo]** = fetched directly from a GitHub README this session; **[in-repo]** = this project's
own existing files; **[search]** = WebSearch snippet synthesis, not independently read full-text.

## A. Saponin-specific pretrained generators

**None found.** Query sweeps across "saponin generative model", "ginsenoside... generative
adversarial network / variational autoencoder", "triterpenoid glycoside molecular generation",
and "steroidal glycoside molecular generation" (see `01_search_log.md` §2, queries 4, 25, 31)
returned only generic de novo design surveys with zero saponin-specific hits. Per the task's
required exact phrasing:

> **"No verified public pretrained saponin-specific generator was identified as of the search date."**

## B. Natural-product pretrained generators

Three real candidates, none saponin-specific, all with material gaps:

- **NPGPT (C06)** [repo] — fine-tunes either `smiles-gpt` (SMILES) or `ChemGPT` (SELFIES) on
  COCONUT (~326K+ natural products, exact current count NEEDS_LOCAL_VERIFICATION). Checkpoints
  exist as Google Drive links, not a standard model hub. README gives no context-length or
  stereochemistry-preprocessing detail. This is the closest published thing to "a natural-product
  generator" and is already named as under consideration in this project's own scope.
- **The "67 million" LSTM generator (C07)** [search] — trained on 325,535 COCONUT SMILES,
  generated 100M candidates, kept 67M as NP-like. Directly and explicitly **removes
  stereochemistry before training** ("An LSTM model was trained on tokenized SMILES (with
  stereochemistry removed)..."). This is disqualifying for a stereo-faithful saponin generator
  and is kept in the table specifically as a cautionary example, not a candidate to adopt. No
  code or checkpoint URL was found this session — only the generated compound library appears to
  be distributed.
- **NaFM (C08)** [search] — pretrained on ~0.6M COCONUT structures using masked + contrastive
  graph learning. **Generative capability is not confirmed** — the description found this session
  reads like a BERT-style representation/foundation model, not a decoder. No code or checkpoint
  URL found. Flagged `FUTURE_WORK` pending direct verification, not a usable candidate today.

## C. Generic molecular pretrained generators (candidates for further fine-tuning)

Ranked roughly by fit to this project's stated direction and constraints:

1. **smiles-gpt (C09)** [repo, README directly read] — GPT-2 causal LM, 10M PubChem SMILES,
   HuggingFace-compatible (`GPT2Config`/`GPT2LMHeadModel`/`PreTrainedTokenizerFast`). This is the
   literal base checkpoint the project's own stated "SMILES-GPT / causal language-model direction"
   already points at, and it is what NPGPT itself fine-tunes. Context length, license, and
   stereochemistry handling are all unconfirmed from the README alone and need local inspection
   of `config.json` and the tokenizer.
2. **ChemGPT (C10)** [search] — GPT-Neo, SELFIES tokens, three released sizes (4.7M/19M/1.2B),
   10M PubChem molecules / ~300M tokens. Recommended role: the project's **SELFIES
   validity-oriented baseline** (the task explicitly asks for one), not the primary line — zero
   natural-product signal in its pretraining data, and stereo-symbol retention in the PubChem→
   SELFIES conversion used to build it was not confirmed this session.
3. **SAFE-GPT (C15)** [repo, README directly read] — 87M-parameter GPT-2, 1.1B-row fragment-
   reordered SMILES-compatible corpus. Confirmed license split: code Apache-2.0, training data
   CC BY 4.0, **weights CC BY-NC 4.0 (non-commercial)**. Fragment/attachment-point framing is
   conceptually well-suited to the sugar+aglycone assembly problem, but this is unproven for
   saponins and the non-commercial weight license is a real constraint. `FUTURE_WORK`.
4. **MolGPT (C11)**, **Chemformer/MolBART (C12)** [search only] — architecturally interesting
   (scaffold+property conditioning; BART denoising pretraining from the same organization —
   MolecularAI — that maintains this project's existing REINVENT4 dependency) but both are
   pretrained at drug-like/benchmark scale (MOSES, GuacaMol, or unstated ChEMBL-scale corpora),
   which is a poor length/complexity match for triterpenoid saponins. `NOT_RECOMMENDED` as a
   starting checkpoint; Chemformer is worth a second look for a future lead-optimization module.
5. **SMILES Transformer (C13)** [search] — **not a generator** (a fingerprint-extraction
   autoencoder). Included specifically as a documented counterexample for the 512-token question:
   its ChEMBL24 pretraining corpus was explicitly capped at ≤100 characters, well under what a
   polycyclic saponin needs.
6. **MolMIM (C16)** [search] — technically interesting (latent-space CMA-ES optimization) but
   distributed only via NVIDIA's hosted NIM/BioNeMo platform — a paid/enterprise infrastructure
   gate that conflicts with this project's explicit "no paid cloud services" constraint,
   independent of technical merit. `NOT_RECOMMENDED`.
7. **GraphAF / graph-autoregressive family (C17)** and **3D graph diffusion / GCDM-EDM family
   (C18)** [search only] — the two representation paradigms that sidestep SMILES tokenization
   entirely. Both were validated in the literature found this session at drug-like/benchmark
   atom-counts well below a full triterpenoid saponin (60–100+ heavy atoms), and 3D diffusion in
   particular requires GPU training explicitly excluded by this project's current-phase
   constraints. `NOT_RECOMMENDED` now / `FUTURE_WORK` (3D diffusion is the correct long-term
   direction for true native stereochemistry, just not the near-term one).

## D. Models that classify/predict but do not generate

- **NPClassifier (C20)** [in-repo, already integrated] — pathway/superclass/class classifier plus
  an `isglycoside` boolean. Already wired into this project (`references/fcd_npclassifier_api.md`,
  `scripts/compute_npc_quick.py`, `scripts/compute_fcd_npc.py`, `metrics/e1_vs_e4_npc.json`).
  Recommended role: the saponin-enrichment/screening oracle in the benchmark plan, not a
  generator.
- **TeroKit (C19)** [search] — a terpenoid database + virtual-screening web server, not a model at
  all. Already named in this project's own context as the source of its triterpenoid dataset.
  Relevant question going forward is bulk-download/redistribution licensing, not fine-tuning.

## E. Methodology / reference-only entries (not reusable checkpoints)

- **Olivecrona 2017 (C03)** and **Segler 2018 (C04)** — foundational RL/transfer-learning methods
  that REINVENT4 (already in this project) directly descends from. No standalone checkpoint
  worth adopting over the maintained REINVENT4 codebase.
- **Moret/Grisoni 2020 (C05)** — the strongest available *evidence* that PubChem/ChEMBL→natural-
  product transfer learning works in a low-data regime, i.e. direct external validation of this
  project's own overall strategy, even though its target space (MEGx) is not saponins.
- **Tom et al. 2025, "Stereochemistry-aware string-based molecular generation" (C21)** — the most
  directly relevant *methodology* paper found this session for how to design a stereochemistry
  benchmark; feeds directly into `04_stereochemistry_review.md` and `07_benchmark_plan.md`. Not a
  reusable model.

## F. What this table does NOT establish

Because nearly every primary paper was network-blocked this session (see `00_README.md`), this
table cannot certify exact parameter counts, exact context lengths, or exact stereochemistry
preprocessing for most candidates beyond what a GitHub README stated outright. Every such gap is
marked `NOT_REPORTED`, `NOT_FOUND`, or `NEEDS_LOCAL_VERIFICATION` in `02_candidate_models.csv`
rather than guessed. Treat this document as a well-evidenced **shortlist and elimination pass**,
not a final verified spec sheet — `11_actionable_next_steps.md` lists exactly what to verify
before any engineering commitment.
