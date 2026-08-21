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

Both outcomes recorded there:
```
2026-08-21T16:53:45Z train exited on its own before the 2400s cap
2026-08-21T18:00:08Z WATCHDOG TRIP: oracle exceeded 5400s (elapsed 5414s); sending SIGTERM
```
The oracle cap **did** fire. See section 2 for what that cost and what I did about it.

### 2. Loop detection — no repeated-failure loop occurred

Nothing retried a failing step. When the oracle hit its cap mid-shape I did **not** retry
that shape, precisely because a retry at the same protocol would fail the same way. Two defects I introduced while editing `brute_force.py`
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
| `RESULTS.md` | manual inject | manual inject (populated; regenerated from JSON) |

Both JSON writers now use temp-file + `os.replace`, which is atomic on POSIX, so a kill
mid-write cannot leave truncated JSON.

**Caveat, and it mattered:** these edits could not retrofit onto the two processes that
were *already running* — Python had the modules loaded. The oracle then hit its cap and
died having written no JSON at all, exactly the failure the fix was meant to prevent. Its
completed rows were recovered from the flushed stdout log via `grid2d/recover_oracle.py`,
which I wrote **before** the cap fired rather than after. Nothing was lost. The fix
applies to all future runs.

### 5. No irreversible git operations — **held**

All work is on `claude/wsl-terminal-origami-5f6j1x`. No merge, no force-push, no branch
deletion, no history rewrite. An earlier force-push attempt in this session (before your
instructions) was blocked by the permission layer and never executed.

---

## 2. What ran

| job | parameters | status |
|---|---|---|
| 2-D self-play training | 12 iterations, 30 episodes, 15 sims, pool 60 | **completed** all 12, 1328s, inside the 2400s cap |
| Oracle, `derived` family | shapes 6x6, 8x8, 6x14, 10x10; 120 instances each | **cap-tripped at 5414s.** 6x6 and 8x8 complete; 6x14 and 10x10 never obtained |
| Oracle, `maekawa` family | shapes 3x3, 2x4, 4x4, 4x5; 200 instances each | **completed**, 15s (see note below) |
| Evaluation, trained | 4 shapes x 3 arms x 5 seeds, 120 instances/shape | **completed**, 525s |
| Evaluation, untrained control | same, random-weight checkpoint | **completed**, 792s |
| Fold-count vs oracle (8x8) | 25 held-out instances | **completed** (section 4) |
| Plots | learning curve, solve rate by shape | **completed** |

### The one job that did not finish, and what I did about it

The oracle's watchdog fired exactly as designed:

```
2026-08-21T18:00:08Z WATCHDOG TRIP: oracle exceeded 5400s (elapsed 5414s); sending SIGTERM
```

Verified this was the cap and not a crash: disk 40% used, 13.5 GB memory free, exit 144 is
the wrapper propagating SIGTERM. It spent roughly 5250s inside the single 6x14 shape
without finishing its 120 instances.

**Consequences and what I decided, so you can audit the judgement:**

1. **6x14 and 10x10 `derived` rows: not obtained, and deliberately not retried.** A retry
   at the same protocol would fail identically, and retrying a step that already failed
   is precisely the loop you asked me to avoid. Obtaining them at a *smaller* instance
   count would work, but that changes the protocol mid-table and makes rows
   non-comparable — a methodology change I am not making unattended. **Left for you.**
2. **`maekawa` family: re-run, and I want to flag this as a judgement call.** It was part
   of the launched job but never started, because the cap killed the wrapper during the
   first family. I re-ran only that portion, at its original parameters, under a 900s
   timeout. It took **15 seconds**. My reasoning: it is completing the job you launched
   rather than new work, it is bounded and read-only, and it produces the single most
   substantive oracle result. If you would rather I had left it, it is one commit to
   revert.
3. **Recovery path built before the cap hit**, not after: `grid2d/recover_oracle.py`
   rebuilds a survey JSON from stdout, since the process pre-dated the incremental-write
   fix and would otherwise have written nothing at all. Its output is flagged
   `partial: true` and `recovered_from_log: true` so a truncated survey cannot be mistaken
   for a complete one.

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

1. **Self-play solve rate sits at or near 1.000 from iteration 2 onward while held-out
   solve rate stays roughly flat**, and training loss falls from 3.35 to 0.037 over the
   same span. Raw numbers in the learning-curve table. I am not characterising what that
   reflects; flagged as you asked.
2. **The trained arm does not separate from plain SP-MCTS at any shape.** Gaps: -0.007
   (6x6), +0.000 (8x8), -0.002 (6x14), -0.078 (10x10). Only the 10x10 gap exceeds pooled
   seed noise, and it is negative. This differs from the 1-D result, where the margin was
   ~10-14 pooled SDs. No interpretation offered.
2b. **The untrained-weight control matches or exceeds the trained net at 6x6, 8x8 and
   10x10** (0.957 vs 0.938; 0.895 vs 0.868; 0.835 vs 0.747). The trained net is ahead
   only at 6x14, by 0.031. Both arms share the same architecture and rollout blending and
   differ only in weights. Stated as measured; what it reflects is yours to judge.
3. **The learning-curve evaluation uses only 40 instances per shape**, so a single curve
   point carries roughly +/-0.07 of binomial noise. The full evaluation (120 instances x 5
   seeds) is the more reliable measurement. Noting the discrepancy in precision, not
   resolving it.
4. **Maekawa-valid instances are frequently unfoldable**, now measured at scale:
   139/200 unfoldable at 4x4 and 174/200 at 4x5, every one of them satisfying Maekawa at
   every interior vertex. The local theorems are necessary and not sufficient. This is a
   measurement, not a plan change.
5. **Kawasaki is never exercised in this domain.** A grid's interior vertices have four 90
   degree sectors, so Kawasaki holds identically. Only half of the tier-1 local check is
   live. Structural property of the domain choice, not a bug.
6. **Whether to depend on OrigamiBench** — it appears to provide the validity oracle
   `research/summary.md` ranked as load-bearing unknown #3. Licence, headless callability
   and runtime at Origamizer scale are unconfirmed. Plan decision, untouched.
7. **The ETH citation** may be a misattribution. Was it a specific reference you held, or
   a recollection? That determines whether it can be recovered or should be dropped.

---

## 7. Waiting on you

- Whether the 2-D run counts as a milestone gate — **not called here**.
- Whether to obtain the missing 6x14 and 10x10 `derived` oracle rows at a reduced
  instance count, which would change the protocol mid-table. **Not decided here.**
- Whether re-running the `maekawa` family after the cap trip was the right call
  (section 2). One commit to revert if not.
- Whether to merge this branch. **Nothing merged.**
- Any architectural change (reward shaping, action space, layer-ordering representation).
  **None made.** The environment, reward and action space are exactly as committed before
  this session's overnight work began.
- Whether `research/benchmarks_verification.md` should be folded into your local
  `research/benchmarks.md`, which I cannot reach.
