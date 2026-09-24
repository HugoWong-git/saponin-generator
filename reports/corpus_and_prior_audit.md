# Corpus and Prior Audit — 46k Saponin Pipeline

**Date:** 2026-09-24
**Corpus:** `data/saponin_train_46k_valid.smi` (45,966 SMILES)
**Model:** `priors/saponin_prior_46k_reg_epoch{1,3,4}.prior`
**Toolkit:** RDKit 2026.3.6, PyTorch 2.14.0 (CPU)

All numbers below were computed in this session. Nothing is estimated or
carried over from a previous run. Where a figure comes from an existing
document it is labelled as such.

---

## Summary

The trained prior has largely collapsed onto the **aglycone** subpopulation of
its training set, and emits **no stereochemistry at all**. Both failures are
traceable to configuration, not to the corpus and not to the architecture:

| | Training corpus | Generated (epoch 3) |
|---|---|---|
| Glycoside fraction | **40.58%** | **23.38%** |
| Sugars per molecule (mean) | **1.27** | **0.38** |
| Molecules with ≥4 sugars | **14.7%** | **0.23%** |
| Mean MW | 706.9 | 553.9 |
| Mean ring count | 6.3 | 5.06 |
| Any stereocentre | **87.5%** | **0.0%** |

The corpus is healthy. The pipeline is discarding most of what makes these
molecules saponins.

---

## 1. What was run

`audit_corpus.py` had never been executed against a live RDKit install (see
its own docstring). It was run here for the first time and completed without
error on all 45,966 records.

Generated molecules were obtained by reconstructing the REINVENT RNN directly
from the checkpoint (3-layer LSTM, 512 hidden, 256 embedding, 131-token
vocabulary) and sampling 10,000 SMILES at temperature 1.0. The reconstruction
reproduces the published pipeline closely enough to trust:

| Metric | `reports/46k_prior_epoch_comparison.md` (epoch 3) | This session |
|---|---|---|
| Validity | 86.97% | 88.58% |
| Mean MW | 551.30 | 553.9 |
| Mean NumRings | 5.03 | 5.06 |

Sugar detection is a **shape heuristic** — a 5- or 6-membered all-sp3
non-aromatic ring with exactly one ring oxygen and ≥2 exocyclic oxygens on its
carbons. It does not assign monosaccharide identity, and glucose, galactose
and mannose are not distinguished (they differ only by stereochemistry). Treat
the glycoside fractions as consistent relative measures, not as curated
carbohydrate annotation.

---

## 2. Q4a — the aglycone : glycoside split

**Answer: 40.58% glycosides (18,654) / 59.42% aglycones (27,312).**

Glycosides are a minority of the corpus, but 18,654 is a large absolute number
— close to the 21,993-molecule plant-metabolome model in the literature, and
two orders of magnitude above the ~190-molecule transfer-learning floor. The
feared outcome, that the glycoside subset would be too small to fine-tune on,
**does not occur**. A glycoside-only specialisation stage is viable.

The two subpopulations are chemically distinct, which matters for everything
that follows:

| | Glycosides (n=18,654) | Aglycones (n=27,312) |
|---|---|---|
| Mean MW | 987.7 | 515.1 |
| Median MW | 943.1 | 486.7 |
| Mean rings | 8.2 | 5.0 |

The corpus is **bimodal**. The median molecule in it has zero sugars.

## 3. Q4b — is stereochemistry preserved?

**Answer: yes, the corpus is stereochemically rich.**

| | Share |
|---|---|
| Fully specified | 65.71% |
| Partially specified | 24.68% |
| Completely flat | 9.61% |
| Any tetrahedral marker (`@`) | 87.5% |
| Any double-bond marker (`/`, `\`) | 15.9% |

Defined stereocentres per molecule: median 10, p95 33, max 67.

The argument for choosing SMILES *because* it carries stereochemistry natively
therefore survives at the corpus level. The problem is downstream (§5).

The residual 9.61% flat and 24.68% partial entries are still worth attention:
a third of the corpus teaches the model that stereocentres may be left
unspecified, with a mean of 2.44 undefined centres per molecule (p95 = 15).

---

## 4. The 128-token cap is a glycoside-selective filter

The checkpoint declares `max_sequence_length = 128` tokens. This value appears
in **none** of the configs in `configs/` — it is inherited unchanged from the
upstream `reinvent_pubchem.prior` (metadata: `PubChem 2024-06-03`). It was
never a decision made for saponins.

Tokenising the corpus with REINVENT's own scheme (bracket atoms, `%NN` ring
closures, `Br`/`Cl`, then single characters; +2 for BOS/EOS):

| | median | p95 | max | **over 128 tokens** |
|---|---|---|---|---|
| Glycosides | 122 | 195 | 342 | **41.4%** |
| Aglycones | 69 | 96 | 323 | **0.7%** |
| Whole corpus | 82 | 170 | 342 | 17.2% |

The cap sits essentially **at the median glycoside length**. It removes 41.4%
of sugar-bearing molecules while leaving aglycones untouched — a 59-fold
difference in exclusion rate between the two subpopulations.

At sampling time the cap is a hard stop on generation steps, so the model
*cannot emit* a SMILES longer than 128 tokens regardless of what it learned.
In this session's run, **5.46% of sampled sequences hit the cap without ever
emitting an end token** — truncated mid-string, and therefore invalid. That
accounts for a substantial share of the ~12% invalidity that has been stable
across all four epochs.

### The resulting distribution collapse

| Sugars/molecule | Training | Generated |
|---|---|---|
| 0 | 59.4% | 76.6% |
| 1 | 9.1% | 12.2% |
| 2 | 8.1% | 8.3% |
| 3 | 8.8% | 2.7% |
| 4 | 6.6% | 0.2% |
| 5 | 3.8% | 0.03% |
| 6+ | 4.3% | 0.01% |

Mono- and di-glycosides survive. Everything above three sugars is essentially
gone: 14.7% of the training set carries ≥4 sugars, against 0.23% of output —
a **64-fold collapse**, concentrated exactly where the token cap bites.

---

## 5. The model emits no stereochemistry

Of 8,858 valid generated molecules, **zero** contain a stereocentre, against
87.5% of the training corpus.

This is not sampling luck. The vocabulary contains 18 stereo tokens
(`[C@H]`, `[C@@H]`, `[C@]`, `[C@@]`, …). Measuring the probability the model
assigns to them at every generation step:

| Prior | Peak P(stereo token) at any step | Mean P(stereo token) per step |
|---|---|---|
| Epoch 1 | 2.97 × 10⁻⁵ | 1.23 × 10⁻⁸ |
| Epoch 3 | 1.73 × 10⁻⁵ | 6.59 × 10⁻⁹ |
| Epoch 4 | 1.48 × 10⁻⁵ | 5.59 × 10⁻⁹ |

The model has learned that these tokens never occur — and **further transfer
learning makes it more certain**, monotonically from epoch 1 to epoch 4.

Four epochs of transfer learning on a corpus that is 87.5% stereochemically
specified produced a model with P(stereo) ≈ 6 × 10⁻⁹. The stereochemistry is
being stripped before the model ever sees it: the base PubChem prior was
trained on non-isomeric SMILES, and the transfer-learning step is not
presenting isomeric SMILES to override that.

Compounding it, every sampling config sets `isomeric_smiles = false`, so even
if the model did emit stereo tokens the output would be flattened on write.
Stereochemistry is absent end-to-end.

For a project about triterpenoid saponins — molecules whose shape is defined
by their A/B, B/C and C/D ring-fusion stereochemistry, and whose sugars differ
from one another *only* by stereochemistry — this is the most serious defect
in the pipeline. Glucose and galactose are indistinguishable in this model's
output by construction.

---

## 6. What this means for the existing epoch comparison

`reports/46k_prior_epoch_comparison.md` recommends epoch 3 as the sweet spot,
with epoch 4 preferred for downstream fine-tuning, on validity, novelty, FDD,
NLL and seven descriptor KL divergences. None of those metrics can see either
failure above:

- **FDD improves monotonically E1→E4 (1.463 → 1.409)** while the model is
  sitting on the wrong mode of a bimodal distribution. Matching aggregate
  descriptor moments does not require matching the glycosylation distribution.
- **NumRings carries the highest KL of any descriptor (0.12–0.14).** The report
  attributes this to "diverse non-saponin PubChem molecules alongside the 46k
  saponins". The measured cause is different: the corpus ring distribution is
  bimodal (aglycone 5.0, glycoside 8.2) and the model reproduces only the
  lower mode.
- **Epoch 4 is the most stereochemically degenerate of the four**, and the
  metric suite ranks it best.

The epoch ranking is not wrong so much as blind. It is selecting among four
checkpoints that share the same two structural defects.

`metrics/e1_vs_e4_npc.json` records NPClassifier `superclass`, `class` and
`pathway`, and reports 100% Triterpenoids at epoch 4 — but does not record
`isglycoside`, which the same API response provides (see
`references/fcd_npclassifier_api.md`). The one available field that would have
surfaced the glycoside collapse was returned by the API and not captured.

---

## 7. Recommended fixes, in order

1. **Raise `max_sequence_length`.** The corpus maximum is 342 tokens; a cap of
   ~410 (max × 1.2) covers the full distribution. Setting it from the p95 (170)
   would still truncate the most heavily glycosylated molecules — precisely the
   compounds of interest. This must be set explicitly in the TL config rather
   than inherited from the PubChem prior.

2. **Retrain on isomeric SMILES.** Verify that the transfer-learning step
   presents stereochemistry to the model, and set `isomeric_smiles = true` in
   the sampling configs. Until both hold, the pipeline cannot represent a
   saponin's defining features. Note that the inherited PubChem vocabulary
   already contains the 18 stereo tokens, so no vocabulary change is required.

3. **Re-run the epoch comparison with glycosylation metrics in the suite** —
   at minimum glycoside fraction, sugars-per-molecule distribution, and
   NPClassifier `isglycoside`. Without these, checkpoint selection is being
   made on metrics that cannot see the dominant failure mode.

4. **Consider up-weighting or staging the glycoside subset.** With n=18,654 a
   glycoside-only specialisation stage is viable, and it directly addresses the
   59.4% aglycone majority. This is worth doing only after fix 1 — otherwise
   the token cap removes 41.4% of that subset.

5. **Clean the 93 molecules containing out-of-vocabulary tokens** (157 tokens
   total), and decide a policy for the 9.61% flat and 24.68% partially
   specified entries before retraining on stereochemistry.

---

## 8. Limitations

- Sugar detection is a shape heuristic, not carbohydrate assignment (§1).
- Generated molecules come from a reconstruction of the REINVENT RNN, not from
  REINVENT itself. It matches the published validity, MW and ring statistics
  closely (§1) but is not the identical code path; `randomize_smiles` and
  canonicalisation settings differ.
- The claim that the transfer-learning step strips stereochemistry is inferred
  from the model's near-zero probability on stereo tokens plus the
  non-isomeric provenance of the base prior. It has not been confirmed by
  instrumenting REINVENT's own data loader, which would require installing
  REINVENT4.
- No claim is made here about which epoch is best. The argument is that the
  current metric suite cannot answer that question.
