# O3 — Overhead cut: stop-doing list for non-research commits

Card `opus-o3-overhead-cut`. Measured from 7 days of `origin/fast-track` with
`MyTradingSys/research/overhead_cut_2026-10-28/count_commit_mix.py` (parse-then-count, same
classification as `make_status.get_commit_mix`). No cut touches a safety gate or live-path check.

## Before (7 days, 2026-10-22 .. 2026-10-29)

| bucket | commits | share |
|---|---|---|
| research | 543 | 29 % |
| claim/release | 37 | 2 % |
| **other** | **1285** | **69 %** (OVER 30 % CAP) |
| total non-merge | 1865 | |

`other` per day: 68, 147, 63, 192, 196, 163, 453, 3 (the 453-day is the heavy ship day).

### The `other` bucket by producer family (7 days)

| family | 7d | /day | file / producer | notes |
|---|---|---|---|---|
| genuine dev work ("other-work") | 468 | 66.9 | scripts/, tests, system docs | **not a stop-doing** — real work |
| **fold-context** | 369 | 52.4 | `context_gap.py:fold` auto-commit at ship | **cut target** |
| card-json-only (task stamps) | 191 | 27.3 | `tasks/*.json` done/READY stamps | cut target (rank 2) |
| desk notes / desk-queue | 88 | 12.5 | `desk_queue/`, `desk assign` | ranked |
| handover files | 59 | 8.4 | `handover/SUPERVISOR_*.md` | ranked |
| session handover (SUPER_SESSION/NEXT_SESSION/OP DEC) | 42 | 6.0 | `SUPER_SESSION.md` etc | ranked |
| lease pipeliner renew | 28 | 4.0 | `lease/pipeliner.json` | ranked |
| lane-health pings | 22 | 3.1 | `codex_run.py`/`lane_health.py` | ranked |
| tasks done/READY stamps | 20 | 2.9 | subject `tasks: <id> ->` | ranked |

## The fold-context family (369 / 7d = 52.4/day) — cut analysis

The ship-time hook (`preship.py hook_ship` → `context_gap.fold`) re-writes the working card's
`context` and commits it. Measured sub-splits of those 369:

| sub-split | 7d | what it is | safe to skip |
|---|---|---|---|
| **CUT1** same-context re-fold | 156 | card already carries this exact `context`; only the `folded` timestamp would change | yes — writes nothing new |
| **CUT2** terminal card | 130 | target card is `done`/`dropped`; its context is a closed record, never read-first again | yes |
| **CUT3** zero-read fold | 36 | the session read nothing before its first edit; `reads` is empty = no handover value | yes |
| union (any of CUT1–3) | **240** | fold commits that carry no new information | **all three applied** |

Overlapping, so the disjoint contribution is CUT1 156 + CUT2 73 + CUT3 11 = 240.

## CUTS.md — ranked stop-doing list

| # | cut | commits/day now | saved (7d) | risk | applied |
|---|---|---|---|---|---|
| 1 | **CUT1** skip a fold whose `context` is byte-identical apart from the `folded` timestamp | 22.3/day (156) | 156 | low — no data lost; card already had the values | **yes** |
| 2 | **CUT2** skip a fold onto a terminal (`done`/`dropped`) card | 10.4/day (73) | 73 | low — closed cards are not read-first again | **yes** |
| 3 | **CUT3** skip a fold with an empty `reads` list | 1.6/day (11) | 11 | low — an empty context is not a handover | **yes** |
| 4 | coalesce card-json-only task stamps (done/READY) into one commit per session-ship | 27.3/day | ~191 (upper bound) | medium — stamps carry state the planner reads; would need planner + tasks.py changes | no (rank 2, bigger change) |
| 5 | stop desk_queue/lead-note one-line commits when nothing changed | 21/day | ~149 | medium — operator-facing notes | no (rank 3, bigger change) |
| 6 | reduce lease-pipeliner renew commit cadence | 4.0/day | ~28 | low | no (small, rank 4) |

CUT1–CUT3 are the three cheapest: they live entirely inside `context_gap.py:fold`, change no gate,
touch no live path, and are covered by a fixture test each. Applied here.

## After (projected)

Applying CUT1–CUT3 removes 240 of the 1285 `other` commits over 7 days.

| bucket | before | after (projected) |
|---|---|---|
| other | 1285 (69 %) | 1045 → **64 %** |
| research | 543 (29 %) | 543 → **33 %** |
| total | 1865 | 1625 |

Non-research (other) share **now 69 % → projected 64 %** from the three applied cuts; research share
**29 % → 33 %**. The remaining gap to the 30 % cap is dominated by genuine dev work (468, off-limits)
plus the task-stamp and note families (CUT4–5), which are cheaper than cutting research but bigger
than a context_gap tweak — they are the next-ranked stop-doing candidates, not removed in this run.

None of the three applied cuts reduces research commits. The 30 % cap is not reached by 3 cuts; the
list ranks the next candidates for a follow-up run.

## Verification

- `count_commit_mix.py` reproduces every number above (run it; parse-then-count, never truncated).
- `test_context_gap.py` CUT1/CUT2/CUT3 tests fail on the pre-change code and pass now (verified via
  `git checkout` + re-run). No `fold context into card` commit is written for a no-change re-fold, a
  terminal card, or an empty-read session.
