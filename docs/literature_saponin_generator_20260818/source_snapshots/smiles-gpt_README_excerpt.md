# Source snapshot: sanjaradylov/smiles-gpt README (excerpt, WebFetch-derived summary)

- Source: https://github.com/sanjaradylov/smiles-gpt (fetched via raw.githubusercontent.com this session)
- Access date: 2026-08-18
- Fetch method: WebFetch tool, prompted to extract architecture/tokenizer/dataset/license/stereo facts
- Note: this is a tool-generated SUMMARY of the fetched README text, not a verbatim copy of the
  full file (WebFetch summarizes rather than returning raw HTML/markdown). Treat quoted fragments
  below as accurate short quotes; treat the rest as paraphrase.

## Extracted facts
- Base architecture: GPT-2, loaded via `GPT2Config.from_pretrained(checkpoint)`.
- Training data: "10M Pubchem SMILES data"; a 10K subset of ChemBERTa's PubChem-10M is bundled
  in the repo's data folder for the demo notebook.
- Checkpoint referenced by name: `checkpoints/benchmark-5m`.
- Tokenizer/config loading pattern: HuggingFace `GPT2Config`, `GPT2LMHeadModel`,
  `PreTrainedTokenizerFast` via `from_pretrained`.
- A supplementary notebook references "AnyGPT for pretraining 1D molecular data" and a
  "selfies-anygpt" notebook, suggesting a SELFIES-capable variant exists in the repo beyond the
  primary SMILES/GPT-2 model.
- NOT stated in the fetched excerpt: n_positions/context length, explicit license, whether
  isomeric SMILES are used, any stereochemistry preprocessing detail.

## Follow-up required (see 11_actionable_next_steps.md)
Clone the repo and inspect `config.json` for the actual checkpoint(s) to resolve context length,
and inspect any preprocessing script for stereochemistry handling.
