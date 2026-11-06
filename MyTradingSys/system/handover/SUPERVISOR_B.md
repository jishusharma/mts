# Supervisor B handover | written 2026-11-06T16:45Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify

## Goal
Login B on JIS-NUC, eco mode. Operator 11-06: weekly cap 95%, but use the next 10% wisely and keep the last 5% for emergencies: start new work only below 90% weekly; 90-95% is for red CI and emergencies only. Week 86% at write, resets 2026-11-08T17:00Z.
Stop at week >= 90% (new work), CI red you did not fix, or no ready cards.

## Truth
- Supervisor tree is mts-jis-nuc-supervisor-b-20261106; BinanceDataFeed checkout is stale, never use it | `python scripts/dev/sync.py where` | read at 2026-11-06T16:45Z
- Worktrees 33 -> 7 after cleanup; leftovers saved in F:/MTS/gq/_saved | `git worktree list` | read at 2026-11-06T16:35Z
- Trunk CI green after B reverts ae1c5028, 9eac4ad8 and relands ab5bb8a1, 6bdc59c6; first 11-06 hand-over reverted (1f5e82723), this is the re-land | `python scripts/dev/sync.py ci` | green d563daf0 at 2026-11-06T17:00Z
- 5 task cards carried merge markers from revert 8dbd7408f; fixed in ead36982 | `python scripts/dev/tasks.py lint` | read at 2026-11-06T16:40Z
- agy: Argon 429 until ~11-09T18:25Z, Claude/GPT pool back ~11-06T17:48Z, Flash works; a second Gemini governor (F:/MTS/mts-gemini) ships gq branches itself | Antigravity > View Usage | read at 2026-11-06T14:40Z
- 9 symbols of 1m 2022-01..2024-06 on disk at F:/MTS/data/tom_raw/klines (SOL/XRP/LTC miss 7,200 source bars); h3-ny-open-count-10sym queued on Flash | `python scripts/dev/kline_gap_check.py ETHUSDT 2022-01 2024-06` | read at 2026-11-06T16:50Z

## Ruled out
- gpt-oss via agy for re-check cards: fakes or refuses; use sonnet or flash.
- `tasks.py tried --asks` parks a card for the operator: never use it to leave a note; edit the card `note` field.
- Flash build of ship-ignores-context-fold-commits: rejected, it rewrote history inside sync.py ship (card note says how to rebuild).

## Next 3 steps
1. `sync.py start supervisor-B-<date>`; `get_usage`; read the last 20 trunk commits.
2. Review Flash results: F:/MTS/gq/agent-brief-report-file-write and F:/MTS/gq/h3-ny-open-count-10sym; ship after review (`tasks.py done` if not closed). After 17:48Z `:sonnet` works again for builds.
3. Then pre-us-failed-break-10sym-dev-run on the 9-symbol data, if the week is under 90%.

## Traps
- MTS_LOGIN=B for supervisor.py, mts_signal.py, sync.py. No git command words in system/ docs (test_2_no_forbidden_refs).
- Before a PRE_REG ship run `python scripts/dev/prereg_context_lint.py` (quick gate misses it).
- New research .py: fees from MyTradingSys/backtest/fees.py (no literals), regenerate T06 costs.csv, data tests pytest.skip without the cache.
- gemini_queue SKIPs STALE cards (`tasks.py tag <id> --refresh` first) and reuses a gq worktree (remove worktree + branch before a rerun).
- Restore LAYERS.md (line endings only) before committing. A ship that says "unrelated histories" made an orphan route-tag commit: branch again from the real reflog commit.
- GitHub API is unauthenticated (60 calls/h per machine): poll CI no faster than every 5 min.

## Open
- Operator: reload AIBridge extension, refresh DeepSeek tab, tick Hands-free (DSA lane still stopped).

## Missed last time
(machine-written by `context_gap.py fold` at the next ship)
