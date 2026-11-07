# Supervisor B handover | written 2026-11-06T19:00Z by JIS-NUC | verify: python scripts/dev/supervisor.py handover --verify

## Goal
Login B on JIS-NUC, eco mode. Operator 11-06: weekly cap 95%, but use the next 10% wisely and keep the last 5% for emergencies: start new work only below 90% weekly; 90-95% is for red CI and emergencies only. Week 88% at write, resets 2026-11-08T17:00Z.
Stop at week >= 90% (new work), CI red you did not fix, or no ready cards.

## Truth
- Supervisor tree is mts-jis-nuc-supervisor-b-20261106; BinanceDataFeed checkout is stale, never use it | `python scripts/dev/sync.py where` | read at 2026-11-06T16:45Z
- Worktrees 33 -> 7 after cleanup; leftovers saved in F:/MTS/gq/_saved | `git worktree list` | read at 2026-11-06T16:35Z
- Trunk CI green after B reverted 80327e0e7 (904cc0b5: market_guide loaded cycle_bottom_flag, whose docstring named the co-trade CLI, so wiring marked it LIVE); docstring reworded 7378431c, conflict-marker gate 3cm in ALWAYS 230845de | `python scripts/dev/sync.py ci` | green 230845de at 2026-11-06T18:55Z
- 5 task cards carried merge markers from revert 8dbd7408f; fixed in ead36982 | `python scripts/dev/tasks.py lint` | read at 2026-11-06T16:40Z
- agy: Argon (low/medium) and Flash (low/medium) both verified online 2026-11-07T14:32Z; assign review tasks across Argon and Flash in low and medium settings in background; a second Gemini governor (F:/MTS/mts-gemini) ships gq branches itself | `python scripts/dev/gemini_queue.py status` | read at 2026-11-07T14:32Z
- 9 symbols of 1m 2022-01..2024-06 on disk at F:/MTS/data/tom_raw/klines (SOL/XRP/LTC miss 7,200 source bars); h3-ny-open-count-10sym queued on Flash | `python scripts/dev/kline_gap_check.py ETHUSDT 2022-01 2024-06` | read at 2026-11-06T16:50Z

## Ruled out
- gpt-oss via agy for re-check cards: fakes or refuses; use sonnet or flash.
- `tasks.py tried --asks` parks a card for the operator: never use it to leave a note; edit the card `note` field.
- Flash build of ship-ignores-context-fold-commits: rejected, it rewrote history inside sync.py ship (card note says how to rebuild).

## Next 3 steps
1. `sync.py start supervisor-B-<date>`; `get_usage`; read the last 20 trunk commits. New work only below 90% weekly.
2. agy Argon (`:low:argon`, `:medium:argon`) and Flash (`:low:flash`, `:medium:flash`) both work; assign review tasks to Argon and Flash in low and medium settings in background (`gemini_queue.py run <card>:low:argon <card>:medium:argon <card>:low:flash <card>:medium:flash`). Half-done card sync-py-ship-tasks-py-done-route-tag-tra sits uncommitted in F:/MTS/gq/sync-py-ship-tasks-py-done-route-tag-tra: finish it on `:high:flash` (the queue reuses that tree) or remove tree + branch.
3. The cycle-bottom market_guide line (80327e0e7) needs a reland by its JIS-NB author; broadcast sent.

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
