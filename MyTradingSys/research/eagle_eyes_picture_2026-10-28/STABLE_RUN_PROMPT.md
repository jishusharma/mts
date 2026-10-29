# Stable run: execute the corrected MTS picture plan (Sonnet)

## One-line start (paste this in a new session on Sonnet)

```
You are Builder. Read and execute MyTradingSys/research/eagle_eyes_picture_2026-10-28/STABLE_RUN_PROMPT.md from origin/fast-track, steps in order.
```

## Prompt

You are a Builder on Sonnet for MTS. Work end to end; do not ask the operator micro-questions (CLAUDE.md "Never wait on a question"); defaults are given per step.

### Boot (before step 1)
1. `python scripts/dev/sync.py start stable-picture-plan`; work only in the tree it prints. `git fetch`, then merge `origin/fast-track`.
2. Read, in full: `MyTradingSys/research/eagle_eyes_picture_2026-10-28/PICTURE_AND_PLAN.md` (the corrected plan: sections 4 and 5 are your task list), `ALERT_DOCK_SPEC.md` (same folder), `MyTradingSys/system/EAGLE_EYES_BIBLE.md` (the operator's words; never edit its verbatim block), `MyTradingSys/system/ROUTING.md`, `MyTradingSys/system/WORKERS.md` rules 1-11.
3. Re-check before acting: anything the plan says is open may have moved. Run `git log origin/fast-track --oneline -20` and grep for F-GAP-1, carry, E1, alert_inbox; a step already shipped is marked done with its commit, not redone.

### Hard limits (from CLAUDE.md; they outrank this prompt)
- Testnet only. No mainnet order, account or key. Never read `.secrets/` or `.env`.
- Repo is PUBLIC: no balances, positions, order ids, account labels, operator trade numbers in any committed file.
- Builders never deploy, restart processes, touch HALT files or open trades. The live host is DESKTOP-F7IU69N; only its owner deploys.
- Never read a SEALED window (carry 2025-07+, any VALIDATION/HOLDOUT) without a recorded operator approval in `OPERATOR_DECISIONS.md`.
- New tests must fail on the pre-change code once. Ship only through `sync.py ship`; commit body ends with `Result: ...`.

### Steps (in order)

| # | Step | How | Done when | Default if blocked |
|---|---|---|---|---|
| 1 | Carry decision ask | Post the one line from `research/carry_basis_2026-10-18/EXECUTABILITY.md` s.4 to the session that started you (or `desk.py post` to the operator Inbox per CONTROL_ROOM.md). Do NOT run the read. | ask is in the Inbox; `tasks.py` card `carry-sealed-read` exists with `blocked: operator` | leave it parked; continue to step 2 |
| 2 | Fix F-GAP-1 | Card from commit 2daa9c51f (`R3_LIVE_REDTEAM.md` s.1). In `execution/position_manager.py` `_manage_impl`: when the journal shows `entry_filled_total > 0` and no stop, re-place the stop from the plan (or flatten + HALT if that fails), instead of raising "nothing to manage". Port the R3 scratch test into `execution/` as a real test. Also add the CLAUDE.md live-path tests: restart state, API error on re-place. | new tests fail on the old code, pass on the new; `run_all_tests.py --quick` green; shipped; DSA/owner told a deploy is needed | if the stop cannot be derived, flatten + HALT path only, and say so |
| 3 | Live state read request | You cannot read the laptop. Send `mts_signal.py broadcast --cmd` to desktop-f7iu69n asking its owner to post counts only: `alert_counter.txt`, last 7 days of `execution/auto_trades.jsonl` by event x source, `runtime/alerts/*.jsonl` by layer x event x tf, which brake files exist. | broadcast id recorded in your hand-back; when acks arrive, one counts table added to `PICTURE_AND_PLAN.md` s.3.3 | NOT_IN_DATA stays; continue |
| 4 | Alert Dock, logic first | Build `scripts/core/alert_inbox.py` (post, parse, field guard) and the pure grouping/ordering/snooze module with tests AD1, AD3, AD4, AD6, AD7, AD8, AD11 from `ALERT_DOCK_SPEC.md` s.3. No producer is changed in this step. | tests fail first, then pass; shipped | none |
| 5 | Alert Dock window + producer flag | WinForms Dock per spec s.2.3 (Show, NOACTIVATE, TOPMOST, one instance, corner dock, history drawer); producers post to the inbox and keep the legacy popup behind `MTS_ALERT_UI` (default `legacy`). Tests AD2, AD5, AD9, AD10. | tests pass on Windows CI; shipped with default `legacy` so deploy changes nothing; a deploy note for the owner in `DEPLOY_RUNBOOK.md` style (flip to `dock`, rollback = `legacy`) | if AD9 cannot be tested on CI, a manual check line for the owner instead |
| 6 | E1 counts-only power screen | Exactly as `research/fable_runs_2026-10-28/R1_EDGE_OR_STOP.md` s.4 row E1: count DEV events for Krown S5/S8 4h, Malkan RSI 40/60 1d/1w, pitchfork 1d (+ DEV_EXT, ETH/SOL public klines). Read NO outcome column. | result file with n_available vs n_needed per family and the pass rule applied; PASS -> E2 card filed, FAIL -> one line "trading-edge program stops" in `PICTURE_AND_PLAN.md` s.5 | none |
| 7 | Operator trade journal schema | A schema doc + loader that writes to a path OUTSIDE the repo (e.g. `F:/MTS_private/journal/`), with layer readings at entry/exit taken from the existing live feeds. No data committed. | schema + test that refuses an in-repo path; shipped | none |

Stop rule: one card per step; claim it (`sync.py claim`), ship it, then the next. At the WORKERS.md rule 4 cap (40 tool turns) hand over with NEXT_SESSION.md naming the next step number.

### Hand back (final reply, under 10 lines)
- First line: last commit SHA and the step reached.
- One row per step: done (commit) / blocked (why, which default used) / not started.
- Broadcast id from step 3 and any operator ask posted in step 1.
- `Noticed:` lines for gaps found (filed as raw cards the same turn, WORKERS.md rule 11).
