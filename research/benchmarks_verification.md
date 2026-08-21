# Citation verification — ORIGAMISPACE, OrigamiBench, ETH crease pattern dataset

**Date checked:** 2026-08-21
**Checked by:** overnight unattended session
**Status of this file:** findings only. No decision or plan change is proposed here.

---

## Two limitations to read first

**1. `research/benchmarks.md` is not reachable from this environment.** It lives in your
local `~/origami-ai-pipeline/research/`, and this session runs in an isolated cloud
container with no access to your machine. It was not among the files uploaded to this
session. **So this file could not be updated in place**, and — more importantly — I could
not check the claims *as you actually worded them*. The task asked whether each source
"matches the claims I attributed to it"; I could not read those attributions. What follows
is what each source **is**, so you can compare it against your own text.

**2. Primary sources could not be fetched.** The network egress proxy blocks
`arxiv.org`, `browse-export.arxiv.org`, `openreview.net`, `doi.org`, and
`research-collection.ethz.ch` — every host that would let me read the papers directly.
Web *search* works; fetching those pages does not. **Everything below therefore rests on
search-engine summaries of the sources, not on my having read them.** Treat it as
"strong evidence the work exists and is roughly as described", not as verified content.
Anything you intend to rely on should be confirmed against the PDF.

---

## 1. ORIGAMISPACE — exists; likely mismatched to the use the plan implies

| | |
|---|---|
| **Verification status** | **Exists** (identifier and venue consistent across independent results) |
| **Identifier** | arXiv:2511.18450 |
| **Title** | *ORIGAMISPACE: Benchmarking Multimodal LLMs in Multi-Step Spatial Reasoning with Mathematical Constraints* |
| **Venue** | NeurIPS 2025 poster; also on OpenReview (`y7ahj9RoXQ`) |

**What it actually is:** a **static evaluation benchmark for multimodal LLMs**. Reported
contents: 350 data instances, each with a crease-pattern diagram, compiled flat pattern,
folding process and folded-shape image; four task types totalling **1,500 multiple-choice
questions and 120 code-generation questions**. Constraints referenced include Kawasaki's
theorem and the Huzita-Hatori axioms.

**Discrepancy to check against your text.** `research/summary.md` lists as load-bearing
unknown #3: *"an interactive environment with a physical-validity oracle would supply the
hardest part of the reward function for free."* ORIGAMISPACE does not appear to be that.
A multiple-choice and code-generation benchmark for MLLMs supplies no callable validity
oracle and no environment to step. If benchmarks.md describes it as a source of training
signal or a reward oracle, that reading looks wrong. As a *held-out evaluation set of
crease patterns* it may still be useful.

## 2. OrigamiBench — exists, and appears to be the oracle the plan was hoping for

| | |
|---|---|
| **Verification status** | **Exists** |
| **Identifier** | arXiv:2603.13856 (March 2026) |
| **Title** | *OrigamiBench: An Interactive Environment to Synthesize Flat-Foldable Origamis* |

**What it actually is:** an **interactive environment** in which a model iteratively
proposes folds and receives feedback on **physical validity** and similarity to a target.
Reported to validate geometric feasibility using the **Flat-Folder solver**, which checks
Maekawa's and Kawasaki's theorems and searches for a valid folded state; an action counts
as valid only if the solver finds at least one feasible solution. Reported corpus: **366
origami designs** taken from the public Flat-Folder project, encoded in **`.fold`**
format (`vertices_coords`, `edges_vertices`, `edges_assignment`, `faces_vertices`).
Reported finding: current vision-language models fail to produce coherent multi-step
folding strategies, and scale alone does not fix it.

**Why this matters to the plan.** This is the load-bearing unknown #3 that
`research/summary.md` ranked as having the largest upside. On this evidence the answer is
that such an environment **does** exist, uses the same `.fold` interchange format the
scaffold already targets, and wraps a solver that does exactly the global
flat-foldability check `validity.py` currently stubs out. **I am flagging this, not
acting on it** — whether to depend on it is a plan decision and is yours.

Worth confirming directly before relying on it: the licence, whether the solver is
callable headlessly as a library, and its per-pattern runtime at Origamizer scale.

## 3. ETH crease pattern dataset — could not verify as described

| | |
|---|---|
| **Verification status** | **Could not verify** |

No evidence surfaced for a canonical, widely-used "ETH crease pattern dataset" for
origami machine learning. Specifically, I could not substantiate the claim recorded in
`research/summary.md` that **"ETH patterns cap at 23 vertices."** Nothing in the search
results supports or contradicts that number; it simply did not appear.

The nearest candidate found is an ETH Research Collection deposit,
**doi:10.3929/ethz-b-000743348**, described as a training dataset of origami crease
patterns associated with *Inverse Design of Origami for Trajectory Following Using Deep
Learning* (ASME J. Mechanisms and Robotics). If that is the source behind the citation,
note it is aimed at **origami mechanism design for trajectory following**, which is a
different problem from fold sequencing, and its patterns are likely shaped by that goal.
I could not open the deposit page to confirm size, vertex counts, licence or format.

`data/fetch_eth_dataset.py` still has `DATASET_DOI`, `ARCHIVE_NAME`, `ARCHIVE_SHA256` and
`ARCHIVE_SIZE_BYTES` set to `None`, so nothing in the codebase pins this down either.

**Open question for you:** was "ETH crease pattern dataset" a specific resource you had a
reference for, or a recollection? If the former, the reference itself would settle this in
a minute. If the latter, it may need to be dropped or replaced — and OrigamiBench's 366
`.fold` designs may already cover the need.

---

## Incidental: other origami datasets that surfaced

Not requested, listed only because they appeared while checking the three above and are
plausibly relevant. Same caveat — search summaries, not read.

| Name | Identifier | Reported contents |
|---|---|---|
| OrigamiCode | (via Learn2Fold, arXiv:2603.29585) | 25 object classes, 5,760 folding-process sequences, 75,000 trajectories, parameterised CP graphs + JSON fold specs |
| GamiBench | arXiv:2512.22207 | 186 instances; 2D crease pattern, a deliberately *impossible* crease pattern, and two 3D renderings each |
| COrigami | arXiv:2606.26299 | Already cited in `stage3_fold_sequence_rl.md` as read-for-architecture |
| OrigamiSet1.0 | arXiv:2101.05470 | Origami image datasets (classification-oriented, not crease patterns) |

The "impossible crease pattern" half of GamiBench is a ready-made source of negative
examples, which the current test suite has to hand-build.

---

## Summary table

| Citation | Status | One-line finding |
|---|---|---|
| ORIGAMISPACE | Exists | Real, NeurIPS 2025 — but a static MLLM QA benchmark, not an environment or oracle |
| OrigamiBench | Exists | Real, and *is* an interactive environment with a flat-foldability oracle over 366 `.fold` designs |
| ETH crease pattern dataset | Could not verify | No canonical dataset found; "23 vertices" unsubstantiated; nearest candidate targets a different problem |

**Waiting on you:** whether to merge this into `research/benchmarks.md` (I cannot reach
that file), and what to do about the ETH citation.
