# Supervisor B handover | written 2026-11-06T14:45Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify

## Goal
Login B on JIS-NUC, eco mode. Operator 11-06: work until weekly 95%, do the important things, use every Gemini/agy model (Codex plan exhausted). Week ~84% at write, resets 2026-11-08T17:00Z.
Stop at week >= 95%, CI red you did not fix, or no ready cards.

## Truth
- Supervisor tree: C:/Users/E-ngineers/IdeaProjects/mts-jis-nuc-supervisor-b-20261106 (branch JIS-NUC/supervisor-b-20261106b). The main IdeaProjects/BinanceDataFeed checkout is 1900+ commits behind and dirty: never use it.
- Trunk CI went red 11-06 ~12:50Z from 3 breaks (wt_mtf and wt30_div_short PRE_REG without separate Phase/Session/Entry Context lines; A's 3b5a7c6ee pushed roles/supervisor.md over 7500 B with CRLF). B reverted all three (ae1c5028, 9eac4ad8); 9eac4ad8 green. Both studies relanded clean (ab5bb8a1, 6bdc59c6); A relands its weekly plan.
- agy quota on JIS-NUC: Argon 429 until ~2026-11-09T18:25Z; Claude/GPT pool 429 until ~2026-11-06T17:48Z; Flash works. Quota view only in Antigravity > model menu > View Usage.
- Another Gemini governor runs on this NUC (Antigravity hub, F:/MTS/mts-gemini, author gemini-queue) and ships finished gq branches itself; check trunk before shipping a gq branch (merge conflicts on the card = already shipped).
- Shipped today via B: ~20 Gemini/agy cards (blind reads, re-derives, stale-check, mark_shared weight, sync.py utf-8 decode, C34 NO-LEAD, footprint delta audit), worker studies wt-cycle-clock, wt-mtf FAIL, wt30 BLOCKED, v-recovery INCONCLUSIVE, pre-US failed-break INCONCLUSIVE (n 176 < 250), h3-ny-open 10sym BLOCKED.

## Ruled out
- gpt-oss via agy for re-check cards: fakes or refuses; use sonnet or flash.
- `tasks.py tried --asks` parks a card for the operator: never use it to leave a note; edit the card `note` field.

## Next 3 steps
1. `sync.py start supervisor-B-<date>`; `get_usage`; read `git log origin/fast-track -20`.
2. Review the Flash branches F:/MTS/gq/gateway-prompt-card-must-exist and sync-py-ci-falsely-says-no-ci-run-path-f; ship after review (`tasks.py done` if not closed). After 17:48Z use `:sonnet` again for builds.
3. Worker "B worker: ship-train DESIGN.md fix" holds fetch-1m-klines-9sym-dev (9 symbols of 1m 2022-2024 from data.binance.vision); when it lands, the 10-symbol DEV studies (h3-ny-open-count-10sym, pre-us-failed-break-10sym-dev-run) can run.

## Traps
- MTS_LOGIN=B for supervisor.py, mts_signal.py, sync.py (the account file reads as login A).
- Quick gate misses the PRE_REG context lint: run `python scripts/dev/prereg_context_lint.py` before any PRE_REG ship (card quick-gate-prereg-context-lint).
- New research .py: no FEE/SLIP/MAKER literals (test_no_own_costs), fees from MyTradingSys/backtest/fees.py, regenerate T06 costs.csv with t06_tables.py (test_cost_inventory), data-needing tests must pytest.skip without the cache.
- gemini_queue SKIPs STALE cards: `tasks.py tag <id> --refresh` and ship before queueing. It reuses an existing gq worktree: remove worktree + branch before a rerun.
- MyTradingSys/system/LAYERS.md shows up modified (line endings only) after gates: `git checkout --` it before commit; a dirty tree makes test_sync own-CI test and ships fail.
- Unauthenticated GitHub API: 60 calls/h shared by the machine; poll CI no faster than every 5 min.
- Never `git revert` with a dirty tree; append-only files (VERDICTS.csv, lookahead_allowlist.tsv) conflict on revert: keep trunk rows, drop only the reverted commit's rows.

## Open
- Operator: reload AIBridge extension, refresh DeepSeek tab, tick Hands-free (DSA lane still stopped).

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
