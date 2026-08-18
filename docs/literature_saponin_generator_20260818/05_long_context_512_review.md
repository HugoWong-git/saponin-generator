# 512-Token and Tokenization Feasibility Review

## A. Five different things this document keeps distinct

The task brief's "512 tokens" figure conflates several genuinely different quantities. Every claim
below states which one it means:

1. **Raw SMILES character length** — the string length before tokenization.
2. **Atom count** — the chemistry-native size measure, tokenization-independent.
3. **Tokenizer-token length** — the actual model input length, which depends entirely on
   vocabulary/algorithm choice (see B below) and is **not** a fixed multiple of character length.
4. **Model context length** (`n_positions` / `max_position_embeddings`) — the hard ceiling the
   architecture was built and trained with.
5. **Generated sequence length / EOS behavior** — how long the model actually emits before
   stopping, which can be shorter than the context ceiling even for a correct, complete molecule,
   or can hit the ceiling and get silently truncated if EOS handling is not checked.

## B. Why the same saponin can require very different token counts

Evidence found this session (`arxiv.org/pdf/2607.05691`, "Where to cut, how deep: BPE and
Unigram-LM on chemistry SMILES", [search]) directly quantifies this: *"Swapping BPE for
Unigram-LM changes which substructures become atomic embedding units and the effective sequence
length by roughly a third,"* and separately, *"The base tokenizer yields a median of 41 tokens per
string, whereas an extended vocabulary yields 10 tokens"* for a comparable corpus. The same paper
reports **Natural Product BPE (NPBPE)** tokenizers built specifically for natural products at
several vocabulary sizes (60, 100, 1000, 7924, 30000 tokens) — i.e. the field has already
recognized that generic (drug-like-corpus-trained) tokenizers are a poor fit for natural products
and built NP-specific alternatives.

Concretely, for saponin SMILES:

- `Cl`, `Br` — two-character elements; a character-level tokenizer splits these into 2 tokens each
  where a regex/BPE tokenizer typically keeps them as 1.
- `[C@H]`, `[C@@H]` — bracket-atom stereo notation; character-level tokenizers can split these into
  5–7 characters/tokens each, while a chemistry-aware regex tokenizer (e.g. the common
  SMILES-regex pattern used across REINVENT-lineage tools) treats the whole bracket atom as one
  token. A single triterpenoid aglycone can carry 6–8 such stereocenters — the difference between
  "1 token per stereocenter" and "6 tokens per stereocenter" alone can be a 40+ token swing.
- `[nH]` — aromatic NH, same bracket-atom tokenization sensitivity, less relevant for saponins
  specifically (few aromatic N heterocycles) but relevant if any candidate's tokenizer is being
  reused from a drug-like corpus with heterocycle bias.
- Ring-closure digits (and `%nn` for ring closures ≥10) — a pentacyclic triterpenoid aglycone
  alone typically needs 5 ring-closure digit pairs; each glycosylated sugar ring adds one more
  ring closure. A saponin with 3 sugar units plus a pentacyclic aglycone can easily need 8+
  distinct ring-closure symbols, which some regex tokenizers treat as single tokens and some
  (naive character-level) do not.
- Parentheses (branch open/close) — scale with the number of substituents and glycosidic branch
  points; each sugar attached via a branch adds a `(...)` pair, and nested branches (a
  disaccharide/trisaccharide side chain) nest parentheses, which is exactly where SMILES syntax
  errors are most likely if a model has not seen enough long, deeply-branched training examples.
- `/` and `\` (E/Z stereo bonds) — rare in triterpenoid cores (few exocyclic alkenes) but can
  appear in side chains (e.g. dammarane-type side-chain alkenes) and in some sugar substituents;
  same fragility as `@`/`@@` under a naive tokenizer.
- Sugar-ring motifs (pyranose/furanose patterns, e.g. `OC1OC(CO)C(O)C(O)C1O`-style fragments) —
  these are exactly the kind of *repeated substructure* that BPE/Unigram-LM tokenizers learn to
  compress into fewer tokens if (and only if) the training corpus used to build the tokenizer's
  vocabulary contained enough sugar-bearing molecules. A tokenizer trained on ChEMBL/PubChem
  drug-like SMILES (true for essentially every generic candidate in `02_candidate_models.csv`)
  will not have learned this compression, because sugars are rare in drug-like chemical space.
  This is the single most important, concrete reason a generic pretrained tokenizer is likely to
  need **more**, not fewer, tokens per saponin than a natural-product-aware one (NPBPE-style)
  would.

**Bottom line:** two saponins with the same number of heavy atoms can have meaningfully different
token counts depending on stereocenter density and how many sugar-ring repeats they contain, and
the *same* saponin can vary 30%+ in token count purely based on which tokenizer vocabulary a
candidate model ships with. **512 tokens cannot be validated as sufficient by reasoning about the
architecture alone — it must be measured empirically against this project's actual data using each
candidate's actual tokenizer**, per the recommendation in section D below.

## C. Per-candidate context-length findings (from `02_candidate_models.csv`)

| Candidate | Reported max seq length | Released checkpoint context | Configurable? | Evidence for 512 specifically |
|---|---|---|---|---|
| smiles-gpt (C09) | NOT_STATED in README | GPT-2 default `n_positions=1024` unless overridden (NEEDS_LOCAL_VERIFICATION) | Yes — standard GPT2Config field | None found |
| ChemGPT (C10) | NOT_REPORTED | NOT_REPORTED (HuggingFace blocked this session) | GPT-Neo positional embeddings are configurable in principle | None found |
| NPGPT (C06) | NOT_STATED in README | Inherits parent (smiles-gpt or ChemGPT) | Same as parent | None found |
| SAFE-GPT (C15) | NOT_STATED in README (fetched directly) | NOT_STATED in README (fetched directly) | NEEDS_LOCAL_VERIFICATION | None found |
| MolGPT (C11) | NOT_REPORTED | NOT_REPORTED | NEEDS_LOCAL_VERIFICATION | None found |
| SMILES Transformer (C13) | ≤100 **characters** (explicit corpus filter) | NOT_REPORTED | NEEDS_LOCAL_VERIFICATION | **Negative evidence**: this checkpoint's whole training corpus was shorter than what a saponin likely needs |
| REINVENT4 Reinvent RNN (C01) | NOT_REPORTED (RNNs have no hard context ceiling, but do have practical fidelity limits on very long sequences) | n/a (recurrent, not fixed-window) | n/a | This project's own 46k saponin TL run (`reports/46k_prior_epoch_comparison.md`) succeeded end-to-end with default settings, which is in-repo empirical evidence the RNN line handles saponin-length SMILES adequately in practice, though token-length was not explicitly measured in that report |

**No candidate found this session explicitly documents, benchmarks, or justifies a 512-token
figure for natural products or saponins.** The 512 number in the project's stated sampling
defaults (`max_length=512`, from the task brief) should be treated as a **starting hypothesis to
validate empirically**, not a figure with literature support.

## D. Mandatory measurement before fixing any maximum

1. **Compute the training token-length distribution before fixing 512 as final.** For this
   project's actual data (`data/saponin_train_46k_valid.smi` and any future saponin-specific
   corpus), tokenize every molecule with each candidate model's actual tokenizer and record the
   full distribution (min/median/p90/p95/p99/max), not just the mean. Long-tailed distributions
   are the norm for natural products (a few very large polysaccharide-heavy saponins can be much
   longer than the median), and a max-length cutoff chosen from the mean will silently exclude the
   tail.
2. **Never silently truncate a molecule string to fit a length limit.** Mid-SMILES truncation
   almost always produces a syntactically broken string (an open parenthesis or ring-closure digit
   with no matching close) — this is worse than excluding the molecule outright, because it can
   pollute the training signal with garbage sequences rather than simply having a slightly smaller
   dataset.
3. **Separately record every molecule that exceeds the chosen token limit** (do not just drop them
   silently) — this excluded set is itself useful evidence for deciding whether 512 needs to be
   raised, and for the "over-limit policy" decision below.
4. **Justified policy options for over-limit molecules** (pick one per data tier, document the
   choice and rationale — do not mix silently):
   - **Exclude** — simplest, appropriate if the excluded fraction is small (e.g. <2–3% of the
     saponin corpus) and those molecules are disproportionately unusual outliers rather than a
     core saponin subclass.
   - **Longer-context model** — raise `n_positions`/`max_position_embeddings` (see E below) if the
     excluded fraction is large or concentrated in a chemically important subclass (e.g. if most
     trisaccharide/tetrasaccharide saponins are being excluded, that is a real coverage gap, not
     noise).
   - **Scaffold-plus-glycan modular representation** — represent the aglycone scaffold and the
     sugar chain(s) as a linked pair of shorter sequences (conceptually aligned with Group SELFIES'
     fragment-token idea, C14) rather than one long flat string. Highest engineering cost, best
     long-term fit if saponins with many sugar units turn out to be a large fraction of the target
     distribution.
   - **Separate model** — train a dedicated "large saponin" model only if the over-512 population
     is both large and internally coherent enough to justify a second training run; otherwise this
     just fragments an already-small dataset.

## E. If the chosen checkpoint's context length is shorter than needed

If empirical measurement (D.1) shows a meaningful fraction of this project's saponins exceed a
candidate's released context length (e.g. smiles-gpt's likely-1024 default might still be short
for some multi-sugar saponins if actual token counts run higher than expected under its
general-purpose tokenizer per section B):

- **Required model/config changes**: `n_positions` (GPT-2) / `max_position_embeddings` (GPT-Neo/
  other) must be increased in the config, and the corresponding positional embedding table must be
  resized. For a learned absolute positional embedding table (which both GPT-2 and GPT-Neo use),
  this means either (a) **reinitializing** the added embedding rows and training them from
  scratch during fine-tuning, or (b) **interpolating** the existing table to the new length before
  fine-tuning (Position Interpolation / NTK-aware scaling, per the context-length-extension
  literature found this session, [search]).
- **Why arbitrary extension is unsafe**: reinitializing embedding rows for positions the base model
  never saw means the model has *zero* prior knowledge for those positions — fine-tuning has to
  teach it positional structure from scratch for exactly the long-sequence tail that matters most
  for this project, using the smallest, least-abundant part of the training data (the long-tail
  molecules). Naive interpolation without any fine-tuning is known in the general LLM literature to
  degrade quality even when it "runs" without erroring — the search results specifically note that
  reliable extension "requires... minimal fine-tuning" even for interpolation-based methods, and
  that plain zero-shot extrapolation without weight updates is the *weaker* of the two general
  paradigms.
- **Relative-position alternatives**: architectures using relative or rotary positional encoding
  (RoPE) extrapolate more gracefully than GPT-2/GPT-Neo's learned absolute embeddings. None of the
  primary candidates identified this session (smiles-gpt, ChemGPT, NPGPT, SAFE-GPT) were confirmed
  to use RoPE — all are GPT-2/GPT-Neo-family, i.e. learned absolute embeddings — so this option
  would mean choosing a different base architecture, not a config change to an existing candidate.
- **Required validation experiment**: after any context-extension change, do not assume it worked.
  Before/after comparison on a held-out set of long saponin SMILES (length ≥ the old ceiling):
  compare valid-SMILES rate, stereochemistry-completeness rate (per `04_stereochemistry_review.md`
  §C), and perplexity/NLL specifically on the long-tail subset vs. the short-sequence subset. A
  context-extension that "runs" but produces disproportionately low validity or stereo-completeness
  on the long tail has not actually solved the problem.

## F. Recommended policy for this project, pending D.1's actual measurement

Given the evidence gathered this session (no candidate documents a validated 512-token ceiling for
natural products; a generic tokenizer is likely to be token-inefficient on sugar-ring motifs;
this project's own existing REINVENT4/RNN line has no fixed context ceiling and has already
processed the 46k saponin corpus successfully): **treat 512 as provisional**, run the
token-length-distribution measurement (D.1) against this project's real saponin data using both
(a) the current in-repo RNN pipeline's tokenizer and (b) smiles-gpt's tokenizer, before committing
engineering effort to either raising a context window or building a scaffold-plus-glycan modular
representation. This measurement is listed as a concrete, cloud-safe, zero-GPU next step in
`11_actionable_next_steps.md`.
