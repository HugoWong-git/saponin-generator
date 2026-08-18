# Model Recommendation — Executive Decision Memo

**Date**: 2026-08-18. **Scope**: which public pretrained model to fine-tune for stereochemically
faithful saponin generation, and what to do if none is fully adequate. Read `00_README.md` first —
this memo's confidence is bounded by that document's network-access limitation.

## Decision framework (weights as specified in the task; not altered)

25% stereochemistry fidelity · 20% natural-product/saponin transfer relevance · 15% 512-token
sequence support · 15% public code/checkpoint reproducibility · 10% compatibility with the
existing SMILES-GPT pipeline · 10% fine-tuning feasibility on available hardware · 5%
validity/robustness.

## Primary recommendation: keep REINVENT4 (C01) as the production line; run smiles-gpt (C09) as the confirmatory second line

This is a **dual-track** recommendation, not a single pick, because the two lines answer different
parts of the weighted criteria and the task's own project context already runs both ("already uses
a SMILES-GPT / causal language-model direction" *and* has an active REINVENT4-based pipeline in
this very repository).

- **REINVENT4/RNN (C01)** scores highest on reproducibility (already working, in-repo, 4 trained
  checkpoints, a full metrics report), hardware feasibility (CPU-feasible, already demonstrated at
  ~6–7 min/10k samples), and compatibility (it *is* the current pipeline). It scores only medium on
  stereochemistry fidelity — representation-level support (`@`/`@@`, `/`\`\``) with **no dedicated
  validation or training signal**, which this review's mandatory validation spec
  (`04_stereochemistry_review.md` §C) is designed to retrofit.
- **smiles-gpt (C09)** is the literal checkpoint the project's own stated direction already points
  at, and is what NPGPT (the closest published natural-product generator found) itself fine-tunes.
  It scores well on natural-product transfer potential (same architecture family as NPGPT) and on
  compatibility with the stated direction, but has **unverified context length, license, and
  stereochemistry preprocessing** — none of which could be resolved from a README alone this
  session.

## Runner-up: ChemGPT (C10), specifically as the SELFIES validity-oriented baseline

Not recommended as the primary line — zero natural-product pretraining signal, and stereo-symbol
retention through its PubChem→SELFIES conversion is unconfirmed — but it directly fills the
task's own required "validity-oriented comparison baseline" role for the benchmark plan
(`07_benchmark_plan.md` §A item 3), and SELFIES' 100%-string-validity guarantee makes it a useful
upper bound on what validity-rate alone can achieve, isolating that metric from the harder
stereochemistry-fidelity question this project actually cares about.

## Validity-oriented comparison baseline: ChemGPT (C10) — see above (same entry serves both roles per the task's own requested structure)

## Graph/3D future-work option: geometry-complete 3D diffusion (GCDM/EDM family, C18)

The only representation family reviewed with a genuine claim to *native* (not per-symbol-fragile)
stereochemistry — explicitly marketed as "chirality-aware" in the source found this session. Not
actionable now: no natural-product/saponin-scale benchmark evidence exists in the literature
surveyed, typical benchmark corpora (QM9, GEOM-Drugs) are well below saponin atom counts, and
training requires GPU resources this project's current phase explicitly excludes. Revisit once
the SMILES-based lines have established a working baseline and dedicated GPU budget is available.

## Approaches to avoid in the current phase

- **MolMIM (C16)** — gated behind NVIDIA's paid/enterprise NIM/BioNeMo platform; violates this
  project's explicit "no paid services" constraint independent of technical merit. NVIDIA has
  reportedly already superseded it with "GenMol" per this session's findings, further reducing its
  relevance.
- **The "67 million" NP generator (C07)** — scale and natural-product focus do not compensate for
  training on stereochemistry-stripped SMILES; adopting it would require a full retrain to even
  begin to meet this project's core stereochemistry requirement, at which point it offers no
  advantage over starting from smiles-gpt/ChemGPT directly.
- **MolGPT (C11), generic Chemformer/MolBART (C12), SMILES Transformer (C13)** — all pretrained at
  drug-like/benchmark scale; SMILES Transformer's explicit ≤100-character corpus cap is a hard
  disqualifier, and the other two have no demonstrated natural-product or long-molecule handling.
- **GraphAF/graph-autoregressive family (C17)** — benchmark-scale (ZINC250k-era) training, unclear
  stereochemistry modeling in this generation of models, no natural-product-scale evidence.
- **SAFE-GPT (C15)** — conceptually the best fit for the sugar+aglycone *fragment-linking* problem
  specifically, but its released weights carry a CC BY-NC 4.0 (non-commercial) license — confirmed
  directly from the repo README this session — which is a hard constraint if this project has any
  commercial dimension; keep as `FUTURE_WORK`, revisit the license question explicitly before any
  engineering investment.
- **NaFM (C08)** — generative capability itself is unconfirmed this session; do not budget
  engineering time against it until that is directly verified.

## Answers to the eight required questions

**1. Should the project retain the SMILES-GPT/NPGPT-style causal Transformer as the main line?**
Not as the *sole* main line — run it in parallel with the existing REINVENT4 line, not as a
replacement. The existing REINVENT4 pipeline is a working, in-repo, already-validated asset (4
epoch checkpoints, a full metrics report); discarding it in favor of an unverified alternative
would be a strictly worse starting position. The causal-Transformer line is worth building out
in parallel specifically because it is the more natural fit for future scaffold/property
conditioning (per MolGPT's design, C11) and for eventual SAFE-style fragment-linking of sugars to
aglycones (C15) — capabilities the current RNN-only line does not have.

**2. Which public pretrained checkpoint, if any, should be tested first?**
`sanjaradylov/smiles-gpt` (C09). It is directly reachable (README confirmed via WebFetch this
session), HuggingFace-compatible, matches this project's own stated direction, and is the base
that NPGPT itself already validated for natural-product fine-tuning. Test it by cloning locally
and inspecting `config.json`/tokenizer files first (see `11_actionable_next_steps.md`) before any
GPU-time is spent.

**3. If no suitable public checkpoint is confirmed, what exact pretraining strategy is
recommended?** If local verification shows smiles-gpt's context length, tokenizer, or license are
inadequate, the fallback is: pretrain a GPT-2-scale causal LM from scratch on a Tier 1+Tier 2
corpus (PubChem/ChEMBL general chemistry + COCONUT natural products, per
`06_dataset_and_finetuning_plan.md`) using a **natural-product-aware tokenizer** (an NPBPE-style
vocabulary, per the tokenization evidence in `05_long_context_512_review.md` §B, rather than a
generic drug-like-corpus tokenizer) — this directly addresses the identified risk that generic
tokenizers under-compress the sugar-ring motifs central to saponins.

**4. Should the project use isomeric SMILES, randomized isomeric SMILES, SELFIES, or a hybrid?**
Isomeric SMILES as the base representation (matches the current pipeline and has the most mature
tooling), **plus** randomized isomeric SMILES as a training-time augmentation (per Arus-Pous et al.
2019), **plus** a SELFIES arm run in parallel purely as the validity-oriented baseline required by
the benchmark plan — not as a representation switch for the main line. Group SELFIES is the
correctly-scoped longer-term upgrade once a working baseline exists (see `04_stereochemistry_
review.md` §B).

**5. Is 512 tokens likely sufficient, and what must be measured locally?** Not established either
way by any source found this session — no candidate documents a validated 512-token figure for
natural products. It must be measured directly: tokenize this project's actual saponin corpus
(both the existing 46k set and any curated Tier 3/4 set) with each candidate's actual tokenizer and
record the full length distribution, not just the mean (`05_long_context_512_review.md` §D.1).
This is a concrete, zero-GPU, cloud-safe task and should be done before any other engineering
commitment.

**6. What preprocessing changes are mandatory to prevent stereo loss?** Retain isomeric SMILES at
every tier (never call `MolToSmiles` with `isomericSmiles=False` for anything that will be used as
training data); run the full stereo-validation function (`04_stereochemistry_review.md` §C) on
every training example, not just generated output, so training-data stereo-completeness is known
and reported, not assumed; dedupe and compute novelty on stereo-aware canonical
identifiers/InChIKeys, never connectivity-only canonical SMILES.

**7. What evidence supports the recommendation?** In descending order of confidence: (a) this
project's own existing, in-repo, already-successful REINVENT4 saponin fine-tune
(`reports/46k_prior_epoch_comparison.md` — primary, directly inspected); (b) directly-fetched
GitHub READMEs for smiles-gpt, NPGPT, and SAFE-GPT (primary, directly read this session); (c)
WebSearch-synthesized evidence for every other claim, each individually sourced and URL-linked in
`02_candidate_models.csv` and `09_bibliography.csv`, but **not independently verified against full
primary text** this session due to the network egress policy documented in `00_README.md`.

**8. What uncertainty remains because papers, models, checkpoints, code, or full text were
unavailable?** Substantial, and itemized: essentially every academic publisher/preprint-server
domain was blocked this session, so no paper's methods/results section was directly read — every
non-in-repo, non-README claim is a search-engine synthesis, clearly labeled as such throughout.
Concretely unresolved: smiles-gpt's exact context length and license; ChemGPT's exact context
length and whether its SELFIES conversion retained stereo symbols; SAFE-GPT's stereochemistry
handling and exact training-data source; NaFM's generative capability at all; TeroKit's bulk-
redistribution terms; and every candidate's precise, code-verified maximum atom/token count for a
representative saponin. `11_actionable_next_steps.md` lists each of these as a concrete follow-up
task.

## What this memo explicitly does NOT claim

- Does not call any model "best" without stating the criterion (see weighted framework above).
- Does not claim 512-token support for any candidate — no code, documentation, or paper evidence
  for that specific figure was found this session for any candidate.
- Does not call any model "stereo-aware" where its preprocessing was confirmed (C07) or plausibly
  suspected (several `NEEDS_LOCAL_VERIFICATION` entries) to strip stereochemical markers.
- Does not call MolMIM or any HuggingFace-hosted checkpoint "open source" merely because a paper or
  a model-hub listing exists — access mode is recorded per-candidate in `02_candidate_models.csv`'s
  `access_status` column, distinguishing open code, open weights, gated/paid infrastructure, and
  paper-only.
- Does not claim a saponin-specific pretrained generator exists anywhere. It does not.
