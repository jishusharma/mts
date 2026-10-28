# Rolling-chain links: why each takes 15-25 min, and which lever to pull first. Design note, 2026-10-28

Card `rolling-chain-background-wait-design-rev` (design only, no code). Sibling: `2026-10-28_coordinator-idle-during-background-wait.md` (what the coordinator does while it waits; this note is about the link's own cycle).

Operator question: why do rolling-chain background Agents each sit 15-25 min? The card's goal names the cycle, not idle wait: read the brief, edit, run the gate (`run_all_tests.py`), re-verify pinned numbers, commit, `sync.py ship` (CI gate).

## Baseline (measured, not guessed)
| what | n | p50 / p90 / max (min) | source |
|---|---|---|---|
| worker Agent link | 255 | 5 / 34 / 181 | `research/bg_process_audit_2026-10-28/AUDIT.md`, "All tasks" list |
| `sync.py ship` | 198 | 5 / 40 / 140 | same |
| `run_all_tests` | 40 | 12 / 52 / 75 | same |

- A 15-25 min link is therefore the upper-middle of the real distribution (p50 5 min, p90 34 min), not a typical one. The long tail is ship and tests, not the Agent's own edits.
- Ship tail: AUDIT.md "ship" row: "every lost push race re-merges and re-gates (up to 5x); then a 10-min CI wait". 17 of 29 ships over 30 min were useful but late.
- Gate step times, `runtime_data/gate_timing.jsonl` (JIS-NB desktop copy, 180 rows, 2026-10-17 to 10-19, written by `run_all_tests.record_timing`, read by `mts_doctor.py:250` `ship_time`):
  - two full-gate runs: 726f59ea (57 step rows, 1,571 s summed) and 614bbc88 (123 step rows, 10,212 s summed). Sums are step seconds, not wall time, because pytest shards run in parallel.
  - slowest single steps (p50 s): 3xt extra tests 773, 5b layer tests 720 (71 modules), 3k sync.py parallel ship tests 313, pytest shards 4/5 and 3/5 about 360-380, 3ds DSA CLI 282.
  - the file holds no `ship` rows (`sync.record_ship_timing`, step "ship"): ship wall time is not logged on this copy, so ship timing here rests on the AUDIT transcript parse. Open item below.
  - the file is 9 days old: refresh it before any fix is sized.

## Levers
| # | lever | cost | risk | evidence it leans on |
|---|---|---|---|---|
| L1 | Smaller cards: S (20 turns) instead of M | Planner splits more; one extra ship (~5 min p50) per split | more ships = more push races (the ship tail above); a split can leave two cards on one central file (D3: one editor per central file) | worker p50 5 vs p90 34 min: short cards already finish at p50; the long links are the multi-step ones |
| L2 | Raise `MAX_RUNNING` past 2 (`usage_reminder.py:22`, OURS) | one constant | does not shorten one link; adds waiting: `sync.py` `GATE_SLOTS = 2` (`sync.py:190`) lets only 2 gates run at once per machine, and D3 records that two gates side by side already pushed tests past the 240 s cap; spends the 5 h window faster | D3 allows more than 2 workers only with a logged justification (Pacing SPEND/NORMAL, window under 60 %, last smoke gate under 5 min). Last smoke gate time is not in `gate_timing.jsonl` (see above), so the safe-to-raise evidence does not exist yet |
| L3 | Cheaper gate scope: `docs`/`smoke` instead of `full` | none to build: `gate_select.py` already returns `none/docs/smoke/full` | a path the selector does not know, or any live-path file (`FULL_RE`), forces `full` by design (fail closed) | `gate_select.py:1-13`: `docs` = no local steps; `smoke` = matching tests + ALWAYS steps. Design-only and data-only cards under `MyTradingSys/research/` and `system/` are already `docs`. The slow cards are code cards on live-path or unknown paths |
| L4 | Batch several small cards into one dispatch and one gate | one gate run and one ship for N cards; the link reads N briefs | one failing card holds the batch; a batch spans files, so it collides with D3's one-editor rule; ships carry several `Result:` lines | AUDIT: ship p90 40 min and gate steps in the 300-770 s range make the fixed per-ship cost the largest single item; batching amortises exactly that |

Correction to the card's framing: lever "use `--quick` where paths allow" is already the default (`gate_select`), so the lever left is to stop cards touching paths that force `full` (keep a card's `files` list out of `FULL_RE` where the work allows), not to add a flag.

## Default (OURS)
**L4 with L3 discipline, no L2.** Concretely:
1. Batch up to 3 ready S/M cards whose `files` do not overlap and none is live-path into one Agent dispatch, one gate run, one `sync.py ship`, one commit per card (the commit body keeps one `Result:` per card). OURS: 3 is a judgement, not tuned; label it so and re-check it once 30 batched links exist.
2. A card whose `files` hit `FULL_RE` or an unknown path ships alone.
3. `MAX_RUNNING` stays 2 (OURS, unchanged) until `gate_timing.jsonl` is current and shows the last smoke gate under 5 min (D3 condition).
4. L1 is applied by the Planner only for cards over `est_turns` 20, not as a general rule.

Why not L2: more workers on 2 gate slots buys waiting, and the per-link cost is the cycle, not parallelism. Why not L1 first: each split adds a ship, and ship is the slowest repeated step.

## Left open (card did not settle, no code here)
- `usage_reminder.py` `check` counts every Agent/Task/Workflow spawn toward `MAX_RUNNING` (it has no read-only or Haiku exemption), while D3 says "Read-only and Haiku Agents do not count (max 5)". Doc and hook disagree; the hook is stricter.
- `gate_timing.jsonl` has no `ship` rows and nothing after 2026-10-19 on the JIS-NB desktop copy: either `record_ship_timing` is not being reached from `ship`, or ship runs elsewhere. A follow-up card should confirm, because L2's evidence rule needs it.
- The 3-card batch size and the "over 20 turns" split point are OURS, not measured.

## Follow-up implementation card
Opened with this ship (`tasks.py new`), pointing at this note: batched dispatch of non-overlapping small cards (one gate, one ship, one `Result:` per card). Markable done only when shipped with passing tests and the test output attached to its result field.
