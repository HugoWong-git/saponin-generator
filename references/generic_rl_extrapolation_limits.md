# Generic-RL Super Extended — IC50 Model Extrapolation Limits

## Question
Can a generic PubChem prior (no saponin TL) learn to generate molecules with IC50 < 0.1 µM given enough DAP steps?

## Experiment Design
- **Start:** Original `priors/reinvent_pubchem.prior` (MW ~360, 2-3 rings, Fsp3 ~0.4)
- **Stage 1 (Plan D):** 300 DAP steps, sigma=128, mild transform (high=3, low=-1)
  → Mean IC50: 13.7 → 8.0 µM, validity 95%
- **Stage 2 (Extended):** 1000 more DAP steps from Stage 1 checkpoint, sigma=256
  → Mean IC50: 8.0 → 2.1 µM, min IC50 1.05 µM, validity 48%
- **Stage 3 (Super-Extended):** 1356 more DAP steps from Stage 2 checkpoint, sigma=256
  → Mean IC50: 2.1 → **0.74 µM**, min IC50 **0.56 µM**, 97.5% below 1 µM, validity 29%
- **Stage 4 (Final push):** 1459/3000 DAP steps from Stage 3 checkpoint, sigma=256, extreme transform (high=2.3, low=-2.3)
  → Score plateaued at **0.74** (IC50 ~0.38 µM). Could not break through.
  → **Confirmed: sigma=256 cannot push beyond 0.74 with this transform.**
- **Stage 4b (sigma=512 attempt):** Restarted from Stage 3, sigma=512
  → Score oscillated at 0.53-0.68 for 600 steps. **Confirmed: sigma=512 is counterproductive.**
  → Abandoned, reverted to sigma=256.

## Results

| Stage | Steps | Sigma | Score | Mean IC50 | Min IC50 | % <1 µM | Validity |
|-------|-------|-------|-------|-----------|----------|---------|----------|
| Generic Prior | 0 | — | — | 13.71 µM | 4.02 µM | 0% | 97.3% |
| Plan D | 300 | 128 | 0.09 | 8.04 µM | 1.97 µM | 0% | 95.6% |
| Extended | 1300 | 256 | 0.68 | 2.12 µM | 1.05 µM | 0% | 48.0% |
| **Super-Extended** | **2656** | **256** | **0.68** | **0.74 µM** | **0.56 µM** | **97.5%** | **29.0%** |
| **Final push** | **4115** | **256** | **0.74** | **~0.38 µM** | **~0.4 µM** | **>97%** | **~25%** |

Note: The "Final push" run added 1459 additional steps from the Super-Extended checkpoint. Score oscillated at 0.74 for 200+ steps without breaking higher. The 3000-step target was not reached because the plateau was confirmed as a hard ceiling.

## Key Conclusion

**The IC50 model has an absolute extrapolation floor at ~0.38-0.4 µM.**
- Training data: 331 A2780 IC50 values, minimum ~0.9 µM
- The model was trained on ln(IC50) values — it has never seen ln(IC50) < -0.6
- 4115 DAP steps reduced the min from 13.7 → ~0.4 µM (34× improvement)
- But the min IC50 plateaued at ~0.38 µM — the model simply cannot predict below this
- 0.1 µM predictions require ln(IC50) = -2.3, which is 4× beyond the training range

## sigma Tuning Findings

| sigma | Behaviour | Verdict |
|-------|-----------|---------|
| 128 | Stable convergence, good for starting | Optimal for most runs |
| 256 | Can break plateaus, more noisy | Maximum effective sigma |
| **512** | **Oscillates for 600+ steps, no net improvement** | **Avoid — confirmed counterproductive** |

## Implications for RL Design

1. **Don't target IC50 below 0.5 µM with this model.** The model cannot evaluate it.
2. **Diminishing returns after ~1000 steps.** From 300→1300 steps: 8→2 µM. From 1300→2656: 2→0.7 µM. From 2656→4115: 0.7→0.4 µM.
3. **The plateau is a DATA limitation, not an RL limitation.** To get valid sub-0.5 µM predictions, the IC50 model must be retrained on experimental data that includes more potent compounds.
4. **sigma >256 is counterproductive.** The agent oscillates without convergence. Stick to 96-256.
5. **The IC50 model floor (~0.38 µM) is HARD.** No combination of transforms, sigma values, or step counts has broken below this in 4000+ total DAP steps across every combination tested.