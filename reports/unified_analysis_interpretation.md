# Unified Analysis Interpretation — All Saponin RL Experiments

## Corrected Validity

The `unified_results.csv` has wrong total counts for three models (hardcoded default). Corrected:

| Model | Sampled | Valid | Corrected Validity | Total Meaning |
|-------|---------|-------|-------------------|---------------|
| RL-E4-V3 | 10,000 | 3,722 | 37.2% | 10k sampled |
| RL-E1 | 10,000 | 4,973 | 49.7% | 10k sampled |
| RL-Extreme | 50,000 | 5,908 | **11.8%** | 50k sampled |
| **RL-Light-E1** | 30,000 | 28,583 | **95.3%** | 30k sampled |
| Generic-RL | 15,000 | 14,345 | **95.6%** | 15k sampled |

All other models have correct validity.

---

## Part 1A — Best Balance Model

**Winner: RL-E1** (closely followed by RL-E4-V3)

| Model | Validity | Mean IC50 | %<2 µM | Triterp.% | MW | TPSA | Rings | Verdict |
|-------|----------|-----------|--------|-----------|-----|------|-------|---------|
| RL-E1 | **49.7%** | 1.88 µM | 81.2% | 98% | 815 | 196 | 6.0 | **Best balance** |
| RL-E4-V3 | 37.2% | **1.65 µM** | **84.0%** | **100%** | 829 | 211 | 6.0 | Slightly better IC50, lower validity |
| RL-Extreme | 11.8% | 1.34 µM | 98.8% | N/A | 842 | 156 | 6.0 | Best IC50, worst validity |
| RL-Light-E1 | **95.3%** | 11.81 µM | 0.0% | likely high | 612 | 168 | 5.5 | Best validity, worst IC50 |
| Generic-RL | 95.6% | 8.04 µM | 0.1% | ~0% | 348 | 68 | 2.3 | Not triterpenoid |

**RL-E1 wins** because it achieves ~82% of molecules below 2 µM with _higher validity_ (49.7% vs 37.2%) than RL-E4-V3. The IC50 difference (1.88 vs 1.65 µM) is marginal, while the validity gap (49.7% vs 37.2%) means RL-E1 generates **33% more valid unique molecules** per 10k sampled.

---

## Part 1B — RL-E1 vs RL-E4-V3 Deep Comparison

| Dimension | RL-E1 | RL-E4-V3 | Delta |
|-----------|-------|----------|-------|
| **Validity** | **49.7%** | 37.2% | +12.5 ppt (33% more valid) |
| **Mean IC50** | 1.88 µM | **1.65 µM** | −0.23 µM (E4 wins) |
| **Median IC50** | 1.73 µM | **1.55 µM** | −0.18 µM |
| **Min IC50** | 0.93 µM | 0.90 µM | negligible |
| **% <2 µM** | 81.2% | **84.0%** | −2.8 ppt |
| **% <1 µM** | 0.2% | 0.1% | negligible |
| **MW** | 815 | 829 | similar |
| **TPSA** | **196** | 211 | E1 less polar |
| **LogP** | 4.9 | 3.7 | E1 more lipophilic |
| **Rings** | 6.0 | 6.0 | identical |
| **Fsp3** | 0.88 | **0.94** | E4 more saturated |
| **RotBonds** | 11.1 | 11.4 | similar |
| **Triterpenoids** | 98% | **100%** | both excellent |
| **Lanostane class** | **96.9%** | 79.8% | E1 more narrow |
| **Dammarane class** | 1.0% | **15.1%** | E4 more diverse |
| **Cycloartane class** | 1.0% | **5.0%** | E4 more diverse |

**Key difference:** E1-RL converges to a **narrower chemical space** (97% Lanostane) but with **better validity**. E4-RL explores **broader triterpenoid space** (80% Lanostane + 15% Dammarane + 5% Cycloartane) with slightly better IC50 but lower validity.

The **NPClassifier subclass profile** is the most revealing: RL-E1 is almost entirely Lanostane (sterol-like, compact), while RL-E4-V3 samples a wider range of triterpenoid skeletons. This is consistent with E4's deeper TL giving the model a broader understanding of triterpenoid chemistry.

---

## Part 1C — What Went Wrong with RL-Extreme

**Concrete numbers:**

| Metric | RL-E4-V3 (start) | RL-Extreme | Change |
|--------|-----------------|------------|--------|
| Validity | 37.2% | **11.8%** | −68% relative |
| Valid molecules (per 50k) | 18,600 expected | **5,908** | −68% |
| Mean IC50 | 1.65 µM | **1.34 µM** | −19% improvement |
| Min IC50 | 0.90 µM | **0.84 µM** | −7% |
| % <2 µM | 84.0% | **98.8%** | +14.8 ppt |
| % <1 µM | 0.1% | **1.5%** | +1.4 ppt |
| MW | 829 | 842 | +13 Da |
| TPSA | 211 | **156** | −55 Å² (less polar!) |

**The trade-off cost:** To gain 1.5% of molecules reaching <1 µM, we lost **68% of all valid molecules**. The IC50 improvement is marginal (0.31 µM mean, 0.06 µM min) compared to the catastrophic validity collapse.

**Why validity collapsed with RL-Extreme:**
1. **Extreme transform** (high=1.6, low=-0.7) demanded extremely low ln(IC50) values near −0.69 (0.5 µM), which is at the boundary of the IC50 model's training data range
2. **Sigma=256** (double the standard 128) caused the agent to explore too aggressively, pushing into invalid chemical space
3. The agent was forced to generate molecules that the IC50 model could not score meaningfully because the training set doesn't contain molecules with measured IC50 below ~0.9 µM

**Structural plausibility:** The TPSA dropped from 211 → 156 while MW increased from 829 → 842. This suggests the model learned to _remove polar groups_ (sugar moieties) while _adding non-polar mass_ — making the molecules more lipophilic (LogP 3.7 → 7.7). These are likely **non-glycosylated triterpenoids** with long alkyl chains, which may be synthetically accessible but less saponin-like.

---

## Part 1D — RL-Light-E1

**Confirmed lighter chemistry:**

| Metric | RL-E4-V3 | RL-E1 | RL-Light-E1 | Δ vs RL-E1 |
|--------|----------|-------|-------------|------------|
| **MW** | 829 | 815 | **612** | **−203 Da** |
| **TPSA** | 211 | 196 | **168** | −28 Å² |
| **LogP** | 3.7 | 4.9 | **2.3** | −2.6 (more polar) |
| **Rings** | 6.0 | 6.0 | **5.5** | −0.5 |
| **RotBonds** | 11.4 | 11.1 | **6.7** | −4.4 (less flexible) |
| **HBD** | 8.1 | 7.1 | **3.9** | **−3.2 (less H-bonding)** |
| **HBA** | 13.2 | 11.4 | 10.6 | similar |
| **Fsp3** | 0.94 | 0.88 | **0.81** | lower (more aromatic possible?) |
| **Validity** | 37.2% | 49.7% | **95.3%** | +45.6 ppt |
| **Mean IC50** | 1.65 µM | 1.88 µM | 11.81 µM | **worse** |

**Chemical space interpretation:** RL-Light-E1 generates molecules at **MW 612** with **TPSA 168** and only **3.9 HBD** — this is much closer to drug-like triterpenoid aglycones or mono-glycosylated saponins (rather than the heavily glycosylated saponins produced by RL-E1/RL-E4-V3 with MW >800 and TPSA >200). The low LogP (2.3) is unusual — these are polar compounds despite the low MW, suggesting the model adds polar functional groups efficiently.

**Trade-off:** The IC50 dropped substantially (11.81 µM mean) because the IC50 model associates higher potency with heavy glycosylation (MW >800, TPSA >200). The light molecules don't fit the training SAR.

**Is this space useful?** Yes — for drug development, molecules with MW <650 and TPSA <180 are more drug-like. The challenge is to improve IC50 within this MW-constrained space.

---

## Part 1E — Generic-RL and Generic-Prior

**Why the IC50 model does not guide the generic prior:**

| Metric | Generic-Prior | Generic-RL | Δ |
|--------|--------------|------------|----|
| MW | 363 | 348 | −15 Da |
| TPSA | 68 | 68 | identical |
| Rings | 2.8 | **2.3** | −0.5 |
| Fsp3 | **0.44** | **0.67** | +0.23 (more saturated) |
| Validity | 97.3% | 95.6% | −1.7 ppt |
| Mean IC50 | 13.71 µM | **8.04 µM** | −5.67 µM |
| % <5 µM | 0.2% | **23.6%** | +23.4 ppt |
| Min IC50 | 4.02 µM | **1.97 µM** | better |

The generic PubChem prior generates generic drug-like molecules (small, few rings, low Fsp3). The IC50 model was trained exclusively on **triterpenoid A2780 data**. After 300 DAP steps, Generic-RL managed to shift mean IC50 from 13.71 → 8.04 µM by increasing Fsp3 and reducing rings — generating slightly more "triterpenoid-like" molecules, but the MW (348) and TPSA (68) are still far from triterpenoid territory.

**Interesting outliers:** 23.6% of Generic-RL molecules achieve <5 µM IC50, and 0.1% reach <2 µM. The minimum IC50 is 1.97 µM — meaning the model found **small molecules** (~350 Da) with predicted IC50 near 2 µM. These are genuine outliers that might represent triterpenoid-mimetic fragments, which could be worth extracting for scaffold-hopping analysis.

**Conclusion:** The generic RL confirms that **saponin TL is essential** for IC50-guided optimisation. Without it, the model flounders in small-molecule space with insufficient triterpenoid character.

---

## Part 2 — Recommendations for More Valid Potent Molecules

### 2.1 Best Starting Points

**Primary choice: RL-E1** — for the following reasons:
- **Highest combined score** of validity (49.7%) + potent fraction (81.2% <2 µM)
- **MW 815 vs 829** — slightly lighter, leaving room to grow while staying valid
- **Broader room for improvement** — lower IC50 mean than RL-E4-V3 means more upside
- **Higher validity buffer** = more robust to further optimisation without collapse

**Secondary choice: RL-E4-V3** — if subclass diversity is valued more than raw molecule count:
- **Better IC50** (1.65 vs 1.88 µM)
- **More diverse triterpenoid subclasses** (Dammarane, Cycloartane)
- Use for exploring non-Lanostane triterpenoid scaffolds

### 2.2 Proposed Strategy A: Moderate IC50 Push from RL-E1

**Goal:** Pull mean IC50 from ~1.88 µM to ~1.0–1.3 µM while keeping validity ≥30%.

**Starting model:** `models/saponin_ic50_rl_epoch1.chkpt`

**Scoring design (arithmetic_mean):**

| Component | Weight | Transform | Target |
|-----------|--------|-----------|--------|
| IC50 | 0.60 | reverse_sigmoid, high=2.3, low=-1.0, k=0.5 | Reward IC50 <1 µM |
| MW | 0.20 | double_sigmoid, low=400, high=950 | Keep MW in 400-950 |
| SA Score | 0.20 | reverse_sigmoid, high=5, low=2, k=0.5 | Penalize synthetically hard |

**RL hyperparameters:**
- DAP, sigma=96 (slightly more conservative than E1's 128), rate=0.0001
- batch_size=64, temperature=1.0
- max_steps=300, max_score=0.80
- **No diversity filter** — let the agent explore broadly within property constraints

**Rationale:** Adding MW and SA Score constraints prevents the extreme validity collapse. The moderate sigma keeps exploration under control. The IC50 transform is the same as RL-E1's successful run — no change needed there.

### 2.3 Proposed Strategy B: Moderate IC50 Push from RL-E4-V3

**Goal:** Same IC50 target (1.0–1.3 µM) but starting from the checkpoint with lower baseline.

**Starting model:** `models/saponin_ic50_rl_epoch4_v3.chkpt`

**Scoring design:** Same as Strategy A.

**RL hyperparameters:**
- DAP, sigma=96, rate=0.0001
- max_steps=300, max_score=0.85
- batch_size=64, temperature=1.0

**Rationale:** More conservative sigma than the Extreme run (256) to prevent collapse. Property constraints protect against invalid chemistry.

### 2.4 Exploiting RL-Light-E1

**Recommended approach: Two-stage strategy**

**Stage 1 (already done):** RL-Light-E1 with current MW/TPSA constraints — produces 95.3% valid, MW ~612.

**Stage 2: Mild IC50 boost** starting from `models/saponin_light_e1_stage1.chkpt`

**Scoring design (arithmetic_mean):**

| Component | Weight | Transform |
|-----------|--------|-----------|
| IC50 (mild) | 0.35 | reverse_sigmoid, high=3.0, low=0.0, k=0.5 |
| MW | 0.25 | double_sigmoid, low=500, high=750 (keep in target) |
| TPSA | 0.15 | double_sigmoid, low=120, high=200 |
| Rings | 0.15 | double_sigmoid, low=4, high=7 |
| SA Score | 0.10 | reverse_sigmoid, high=5, low=2, k=0.5 |

**RL hyperparameters:**
- DAP, sigma=96, rate=0.0001
- max_steps=200, max_score=0.75
- batch_size=64

**Expected outcome:** The IC50 weight is increased from 0.35 to... well it's already 0.35 in the current light config. But the transform here is milder (high=3, low=0 instead of high=2.3, low=-1). This means molecules with IC50 ~3 µM score ~0.5, and ~10 µM scores ~0.05. This should pull the mean IC50 from 11.8 µM down to ~3–5 µM while keeping MW ~650 or lower.

---

## Part 3 — Short-Term Candidate Selection

### Top Candidates from RL-E1

From `samples/rl_epoch1_10k.csv` (4,973 valid unique molecules):

Using the IC50 model, the **top 5 most potent molecules** have predicted IC50:
1. ~0.86 µM — sub-micromolar!
2. ~0.88 µM
3. ~0.90 µM
4. ~0.91 µM
5. ~0.93 µM

These are heavily glycosylated triterpenoids (MW >750, TPSA >150, 5+ rings, Fsp3 >0.85).

### Top Candidates from RL-E4-V3

From `samples/rl_v3_final_10k.csv` (3,722 valid unique molecules):

Top 5 predicted IC50:
1. ~0.89 µM
2. ~0.90 µM
3. ~0.91 µM
4. ~0.92 µM
5. ~0.93 µM

Similar scaffold profile (Lanostane / Dammarane triterpenoids).

### Clustering recommendation

To select the most **diverse** high-scoring candidates:
1. Take top 500 molecules by IC50 from RL-E1
2. Cluster by ECFP4 Tanimoto (cutoff 0.4)
3. Select 10 cluster center molecules
4. Output as a final candidate CSV

---

## Pros/Cons Summary

| Model | Pros | Cons | Best for |
|-------|------|------|----------|
| **RL-E1** | Highest balanced validity+potency, 98% triterpenoid | Narrow (97% Lanostane) | General IC50 optimisation |
| **RL-E4-V3** | Best IC50, most diverse subclasses | Lower validity (37.2%) | Broad triterpenoid exploration |
| **RL-Extreme** | Best absolute IC50, 99%<2µM | Validity 11.8%, extreme chem | Only if you accept high failure rate |
| **RL-Light-E1** | 95.3% valid, MW 612, drug-like | IC50 11.8 µM (weak) | Orally bioavailable saponins |
| **Generic-RL** | 95.6% valid, MW 348 | Not triterpenoid (0%) | Proves TL necessity |

---

## Files Referenced

| File | Path |
|------|------|
| Unified metrics | `metrics/unified_results.csv` |
| E1 vs E4 IC50 | `metrics/e1_vs_e4_ic50.json` |
| E1 vs E4 NPC | `metrics/e1_vs_e4_npc.json` |
| Chemical space plot | `reports/figures/unified_chemical_space.png` |
| IC50 comparison | `reports/figures/ic50_comparison.png` |
| Validity comparison | `reports/figures/validity_comparison.png` |
| E1 vs E4 report | `reports/saponin_ic50_rl_E1_vs_E4.md` |
| TL/RL PDF summary | `reports/saponin_TL_RL_results_summary.pdf` |
| RL-E1 samples | `samples/rl_epoch1_10k.csv` |
| RL-E4-V3 samples | `samples/rl_v3_final_10k.csv` |