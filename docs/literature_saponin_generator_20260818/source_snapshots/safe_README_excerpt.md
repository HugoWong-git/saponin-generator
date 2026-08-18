# Source snapshot: datamol-io/safe README (excerpt, WebFetch-derived summary)

- Source: https://github.com/datamol-io/safe (fetched via raw.githubusercontent.com this session)
- Access date: 2026-08-18
- Fetch method: WebFetch tool, prompted to extract architecture/tokenizer/dataset/license/stereo facts

## Extracted facts
- SAFE-GPT model: "87M params", GPT2-like, "12 layers, each with 12 attention heads per layer,
  and a hidden state size of 768."
- Training dataset: "1.1B rows" / "250GB", distributed as the HuggingFace dataset
  `datamol-io/safe-gpt`. Exact source database (ZINC/PubChem/etc.) not stated in the excerpt.
- Tokenizer: a `safe.split` function is provided to "tokenize a SAFE string to build a generative
  model"; implementation detail not given in the excerpt.
- License: code Apache-2.0; training data CC BY 4.0; **model weights CC BY-NC 4.0
  (non-commercial, research purposes only)**.
- NOT stated in the fetched excerpt: context length / max_position_embeddings, whether isomeric
  SMILES are retained through SAFE encoding/decoding.

## Follow-up required (see 11_actionable_next_steps.md)
Confirm whether the CC BY-NC 4.0 weight license is compatible with this project's intended use
before any engineering investment; inspect the SAFE encoder/decoder source for stereochemistry
handling.
