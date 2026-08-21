# Overnight log — 2026-08-21

Unattended session. **Facts and open questions only. No conclusions drawn, no milestone
called, nothing merged.** Everything below is on branch
`claude/wsl-terminal-origami-5f6j1x`.

---

## 1. Guardrails — status against each hard limit you set

### 1. Iteration / time cap — **already present, plus a wall-clock watchdog added**

The training job was launched with `--iterations 12`, a hard iteration cap. It ran all 12
and exited on its own in **1328s**. As defence in depth I added a wall-clock watchdog at
**2400s (40 min)** for training and **5400s (90 min)** for the oracle, chosen as roughly
2x and 4x the then-observed pace so a stall would be caught without truncating healthy
work. Watchdog decisions and trips are logged to `grid2d/logs/watchdog.log`.

Actual result recorded there:
```
2026-08-21T16:53:45Z train exited on its own before the 2400s cap
```

### 2. Loop detection — no repeated-failure loop occurred

Nothing retried a failing step. Two defects I introduced while editing `brute_force.py`
(missing `import os`; a per-shape timer shadowing the survey start time) were caught by a
verification step **before** the code ran, fixed once each, and confirmed by a test run.
No step was attempted three times.

### 3. Cost / resource ceiling — **no metered compute involved; verified**

- `nvidia-smi` absent; `torch.cuda.is_available()` is `False`. **CPU only.**
- No API-billed calls in any job — the pipeline is numpy + torch CPU + matplotlib.
- The container is ephemeral and per-session; there is no cloud GPU or per-token billing
  attached to these runs.
- **What I cannot verify:** whether your account has an overall session/compute budget at
  the platform level. That is outside anything visible from inside the container. Flagging
  rather than asserting. The wall-clock watchdogs bound runtime regardless.

### 4. Checkpointing — **gap found and closed; one caveat**

| artefact | before | after |
|---|---|---|
| model weights | already per-iteration (`iterNN.pt` + `final.pt`) | unchanged |
| `learning_curve.json` | **end of run only** | written every iteration |
| oracle survey JSON | **end of run only** | written after every shape |
| `RESULTS.md` | manual inject | manual inject (populated at end) |

Both JSON writers now use temp-file + `os.replace`, which is atomic on POSIX, so a kill
mid-write cannot leave truncated JSON.

**Caveat you should know about:** these edits could not retrofit onto the two processes
that were *already running* — Python had the modules loaded. For those two runs the
incremental record is the flushed stdout log captured per job. Nothing was lost; the fix
applies to all future runs.

### 5. No irreversible git operations — **held**

All work is on `claude/wsl-terminal-origami-5f6j1x`. No merge, no force-push, no branch
deletion, no history rewrite. An earlier force-push attempt in this session (before your
instructions) was blocked by the permission layer and never executed.

---

## 2. What ran

| job | parameters | status |
|---|---|---|
| 2-D self-play training | 12 iterations, 30 episodes, 15 sims, pool 60 | completed, 1328s |
| Oracle, `derived` family | shapes 6x6, 8x8, 6x14, 10x10; 120 instances each | see RESULTS.md |
| Oracle, `maekawa` family | shapes 3x3, 2x4, 4x4, 4x5; 200 instances each | see RESULTS.md |
| Evaluation, trained | 4 shapes x 3 arms x 5 seeds, 120 instances/shape | see RESULTS.md |
| Evaluation, untrained control | same, random-weight checkpoint | see RESULTS.md |
| Fold-count vs oracle (8x8) | 25 held-out instances | see section 4 |

Numbers live in `grid2d/RESULTS.md`, regenerated from run JSON by
`python -m grid2d.report --inject`. Nothing there is typed by hand.

---

## 3. What I fixed (all narrow and reversible)

1. **`.gitignore`: `grid2d/checkpoints/`** — training checkpoints were untracked and being
   flagged; matches the existing `smoke_test/checkpoints/` rule.
2. **`.gitignore`: `!grid2d/plots/*.png`** — the repo has a blanket `*.png` that had
   already silently swallowed the 1-D deliverable plots earlier in this session. Fixed
   preemptively for 2-D rather than after the fact.
3. **Incremental run-JSON writes** in `train.py` and `brute_force.py` (see guardrail 4).
4. **Two defects in my own edit** to `brute_force.py`, caught before execution.
5. **Caps in `fold_count.py`** — path enumeration is exponential in principle. Capped at
   200,000 sequences and 2,000,000 nodes per instance. Without this it was a runaway risk;
   even a 6x6 instance turns out to admit tens of thousands of distinct valid sequences.

Each is described in its commit message.

---

## 4. Deliverable: fold count vs oracle minimum

<!-- FOLDCOUNT -->
**Question asked:** on the 8x8 test cases, does the trained policy's fold sequence match
the oracle's minimum-fold-count solution, or does it just reach a valid but non-minimal
solution?

**Answer: it matches, on all 25 instances — but the comparison cannot distinguish
anything, because every complete solution in this action model has the same length.**

Run: `python -m grid2d.fold_count --shape 8x8 --count 25` (seed 3, held-out eval seed
500003, `checkpoints/final.pt`). Raw output in `grid2d/fold_count.json`.

| measurement | value |
|---|---|
| crease lines on an 8x8 grid | 14 |
| instances | 25 |
| policy solved | 25 / 25 |
| policy fold count matched oracle minimum | 25 / 25 |
| distinct oracle minimum values across all instances | `[14]` |
| distinct policy fold counts across all instances | `[14]` |
| instances where the distinct-sequence count hit the 200,000 cap | 25 / 25 |

**Why the match is structural, not an achievement.** An all-layers simple fold folds
exactly one crease line, and a solved state requires every crease line folded. So any
complete sequence on an 8x8 grid is exactly `(m-1)+(n-1)` = 14 folds. There is no such
thing as a non-minimal complete solution here. The oracle confirms this empirically
rather than by assertion: across every instance it searched, the only minimum-fold value
observed was 14, matching the expected value.

**The fidelity question this leaves open.** Each of the 25 instances admits **at least
200,000 distinct valid fold sequences** — the enumeration hit its cap on every one, so
200,000 is a floor, not a count. All of them are the same length. So fold count cannot
rank them, and the policy's choice among ~10^5+ equally-short sequences is unmeasured by
this metric.

Whether that means the reward needs a different quality term, and what that term should
be, is an architectural decision. **Not made here** — it is the "what does *best route*
mean" question already open in `research/build_order.md`, now with a concrete measurement
attached to it. Note the same degeneracy was found in the 1-D domain, so this is the
second domain in which fold count carries no signal.
<!-- /FOLDCOUNT -->

---

## 5. Citations

`research/benchmarks_verification.md` has the detail. Summary:

| citation | status |
|---|---|
| ORIGAMISPACE | Exists (arXiv:2511.18450, NeurIPS 2025). Appears to be a static multimodal-LLM QA benchmark, not an interactive environment or validity oracle. |
| OrigamiBench | Exists (arXiv:2603.13856). Appears to be an interactive environment with a flat-foldability oracle (Flat-Folder solver) over 366 `.fold` designs. |
| ETH crease pattern dataset | **Could not verify.** No canonical dataset found; the "caps at 23 vertices" claim was not substantiated. |

**Two limitations on all three**, stated fully in that file:

- `research/benchmarks.md` **is not reachable from this container** — it is on your local
  machine and was not uploaded. It could not be updated in place, and I could not check
  the sources against *your wording* of the claims, only against what the sources are.
- The egress proxy blocks `arxiv.org`, `openreview.net`, `doi.org` and
  `research-collection.ethz.ch`. Web search works; fetching those does not. **The findings
  rest on search-engine summaries, not on my reading the papers.**

---

## 6. Open questions — for your review, not decided here

1. **Self-play solve rate sits at or near 1.000 for most of training while held-out solve
   rate stays roughly flat.** Raw numbers are in the learning-curve table. I am not
   characterising what that reflects; flagged as you asked.
2. **The trained arm does not separate from plain SP-MCTS at 6x6, 8x8 or 6x14** — the
   solve rates are within a hundredth of each other. This differs from the 1-D result,
   where the margin was ~10-14 pooled SDs. Raw numbers in RESULTS.md; no interpretation
   offered.
3. **The learning-curve evaluation uses only 40 instances per shape**, so a single curve
   point carries roughly +/-0.07 of binomial noise. The full evaluation (120 instances x 5
   seeds) is the more reliable measurement. Noting the discrepancy in precision, not
   resolving it.
4. **Kawasaki is never exercised in this domain.** A grid's interior vertices have four 90
   degree sectors, so Kawasaki holds identically. Only half of the tier-1 local check is
   live. Structural property of the domain choice, not a bug.
5. **Whether to depend on OrigamiBench** — it appears to provide the validity oracle
   `research/summary.md` ranked as load-bearing unknown #3. Licence, headless callability
   and runtime at Origamizer scale are unconfirmed. Plan decision, untouched.
6. **The ETH citation** may be a misattribution. Was it a specific reference you held, or
   a recollection? That determines whether it can be recovered or should be dropped.

---

## 7. Waiting on you

- Whether the 2-D run counts as a milestone gate — **not called here**.
- Whether to merge this branch. **Nothing merged.**
- Any architectural change (reward shaping, action space, layer-ordering representation).
  **None made.** The environment, reward and action space are exactly as committed before
  this session's overnight work began.
- Whether `research/benchmarks_verification.md` should be folded into your local
  `research/benchmarks.md`, which I cannot reach.
