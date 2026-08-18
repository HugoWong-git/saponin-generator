# Source snapshot: ohuelab/npgpt README (excerpt, WebFetch-derived summary)

- Source: https://github.com/ohuelab/npgpt (fetched via raw.githubusercontent.com this session)
- Access date: 2026-08-18
- Fetch method: WebFetch tool, prompted to extract architecture/tokenizer/dataset/license/stereo facts

## Extracted facts
- Base pretrained models: two variants — one fine-tuned from "smiles-gpt", one fine-tuned from
  "ChemGPT".
- Dataset: "molecules from the COCONUT natural product library converted to SMILES format."
- Checkpoint availability: "Fine-tuned models trained on the COCONUT dataset are available" via
  Google Drive download links for both variants.
- Additional: a Google Colab notebook is offered for browser-based inference without local
  installation.
- NOT stated in the fetched excerpt: tokenizer detail, max sequence length, whether SMILES are
  canonical/isomeric/randomized, license, any stereochemistry handling notes.

## Follow-up required (see 11_actionable_next_steps.md)
Clone the repo and inspect the fine-tuning/preprocessing scripts directly to resolve
stereochemistry handling and context length before treating NPGPT as production-ready.
