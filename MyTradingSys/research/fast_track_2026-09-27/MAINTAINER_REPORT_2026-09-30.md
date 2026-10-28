# MAINTAINER REPORT 2026-09-30 (second run; covers 0707b59..26a8ad2 = 56 commits)
Window: auto_trades.jsonl 2026-09-29T13:00Z -> 22:24Z (9.4 h; last row at run time). Constraints honoured:
NUC thermal hold (read-only gate check only: idle, cpu 6%, no model loaded); layers/alerts/ + execution/ untouched.

## 1. Declutter
- `declutter_backups.py` gained `--exclude <prefix>` (repeatable; also spares __pycache__ there). Applied with
  `--exclude MyTradingSys/backtest/layers/alerts --exclude MyTradingSys/execution`: 4 superseded backups moved to
  `Dumps/_archive/2026-09-30/` (MANIFEST.csv): run_all_tests.py.pre_ratecheck/.pre_timeexit, nuc-worker.ps1.pre_thermal,
  start-dsa-chrome.ps1.pre_fdrive. Note: the __pycache__ sweep of the first pass also covered the excluded dirs
  (harmless: regenerated on import; running processes already loaded) - fixed for next time.
- LEFT for the owning session: 32 superseded backups in execution/ + layers/alerts/ (all content in history;
  includes restore points named in SUPERVISOR_LOG: auto_trader_config.json.pre_collect/.pre_toc, *.pre_adopt,
  *.pre_netretry). Archive them once that session releases the area. 11 staged .new unchanged since 09-29.
- `.gitignore` +2: `MyTradingSys/runtime/*.lock` (dsa_feeder.lock), `.claude/settings.local.json`.
- Untracked, decision needed: `halt_history/.gitkeep`, `plans/.gitkeep` -> commit (owner of execution/);
  `bt_runs/TRIAL_REGISTRY.csv` + `bt_runs/tom_core_20260929/FROZEN.md` -> commit with the modified TOM_CORE_BT.md
  (Tom-core BT owner, WIP 5831ead); `scripts/worker/dump_dom*.py` (7) + dump_challenge.py + watch_stop.py = DSA
  selector-calibration scratch (peer/operator) -> archive or ignore `scripts/worker/dump_*.py`.
  Modified by others, left alone: auto_trader_config.json, TOM_CORE_BT.md, audit_targets.json.

## 2. Latency (11 real entries, all fills on testnet)
| Stage | 2026-09-30 measured | vs 09-29 |
|---|---|---|
| bar close -> decision (n=11) | 15, 22, 28, 32, 40, 45, 51, 57, 59, 68, 69 s (median 45) | median ~48; unchanged (6.3/6.5 not landed) |
| intent -> entry placed -> filled | 0.30 s -> 0.62 s (L-mkt-0929-2215) | same |
| intent -> stop live / target | 1.23 s / 1.87 s | same |
| first subaccount trade S-mkt-0929-1501 | decision 69 s after 15m close; entered 15:01:07Z | PM died 15:55Z, re-attached, time exit 120 min, +0.065 USD |
| turn_of_candle 1m hold | 482 s (8-bar time exit 480 s, fires ~2.7 s late) | new |
Speed items still open: bar-aligned polling (~30 s), auto_trader 20 s -> 5 s poll (~8 s). Both touch live code: proposals.

## 3. Signal-flow gate (>= 1 protected trade per routed family; window 9.4 h, not 24 h)
Routing is read from auto_trader_config.json (the brief's "fabio jishu_1" is stale since 7058bc2 at 01:53 IST):
toc -> jishu_1, fabio -> jishu_3, rsi 15m -> jishu_2, rsi other -> jishu_3, other layers -> jishu_4, Tom -> main.
| Family / account | Trades | Result | Why not / note |
|---|---|---|---|
| Tom / main | 0 | FAIL | 1 Tom alert (tom#70 short 20:10Z) skipped by AUTO_PAUSE left on by the dead adopt builder |
| fabio / jishu_3 | 0 | FAIL | 1 alert (cvd_absorption 1h 19:00Z) skipped by the same AUTO_PAUSE; 15m fabio wired only 20:23Z |
| rsi 15m / jishu_2 | 2 | PASS | S-1501 (stop resting while unmanaged 15:55-~16:40Z), L-1815 +0.0045 |
| rsi other / jishu_3 | 1 | PASS | rsi 5m L-2135 +0.0057; malkan_bull 1h 19:00Z skipped (AUTO_PAUSE) |
| other layers / jishu_4 | 0 | FAIL | no alert reached auto_trader: cryptocred/session/positioning all QUIET (rate check below) |
| turn_of_candle / jishu_1 | 8 | PASS | 8/8 losses, -0.064 USD total = ~round-trip fee per 10 USD trade; C3 found no edge |
Rejections/skips since 13:00Z: 23 `unmapped turn_of_candle:toc_m14` (13:01-20:15Z, before the side went live - resolved),
3 `skipped_auto_pause` (above). No skipped_busy (sub-accounts freed the slot). OPERATOR_ALERTS.log does not exist
(no respawn exhaustion). halt_history: only 09-29 entries (watchdog_false 21:07 IST, xferfix pair) - no new HALT.
- `alert_rate_check.py` CRASHED (KeyError '5m': TF map lacked the new 5m tf). Fixed (+5m, 4h) with a regression test
  that reads the runner's `--tfs` default as text (fails on the old code). Output now: rsi_events 5m "DEAD" (2 vs 11.6
  expected/12 h) is an artefact - 5m is live only ~2 h of the 12-h window; recheck after 12 h.

## 4. Accuracy notes (proposals only - live areas)
- turn_of_candle collection trades are fee-determined (1m, 8-min hold, taker both sides): the ledger will show fee
  drag, not signal. Propose: mark as collection-only in config/log; longer hold or maker entry before any edge claim.
- Open from 09-29 and still open: per-layer brackets from backtest; 15m RSI alerts carry null rsi values; size
  multiple-of-10 check in new_plan.

## 5. New incidents since 09-29 report (LESSONS_LEARNED section G, 10 entries)
Known five (watchdog heartbeat dir, PM URLError freed slot, stale line-number tick, concurrent execution/ edits,
NUC 98 C) plus: adopt builder died (API 401) after in-place auto_trader.py edits and left AUTO_PAUSE ~2 h (3 signals
lost); execution/journal/ vanished (cause unknown); hourly check ran a backfill after the thermal pause; 5m tf broke
alert_rate_check; turn_of_candle sided + live 3.5 h after the no-edge verdict; stale routing in the maintainer brief.

## 6. Rules applied
- CLAUDE.md +3 lines (Hard rules): one session per live area + AUTO_PAUSE owner/expected end; new tf/family ->
  grep every TF/family map.
- Memory updated (no new files): live-tree-staging (repeat + AUTO_PAUSE + area ownership), supervisor-thinking-
  checklist 12 -> 15 items, continuous-work-schedulers (thermal hold limit, weekly cap, gpt-oss removed), MEMORY.md index.
- Gate: `run_all_tests.py --quick` ALL PASS; test_alert_rate_check 3/3 (new test fails on pre-change code).

## 7. Next run
- Signal-flow gate on a full 24 h: Tom main, fabio jishu_3, jishu_4 families had 0 trades; if still 0, check
  alert rates for cryptocred/session/positioning (QUIET) and whether Tom produced any alert.
- Re-run `alert_rate_check.py` once 5m/15m have 12 h of history (5m "DEAD" expected to clear).
- Archive the 32 execution/ + layers/alerts/ backups after the Deribit-smoke session releases those areas
  (`declutter_backups.py --apply`, no excludes; keep .pre_collect until the collection window ends).
- Owners decide: commit .gitkeeps, bt_runs/ with TOM_CORE_BT.md; ignore or archive scripts/worker/dump_*.py.
- Supervisor: AUTO_PAUSE owner/expiry mechanism (file content: owner + until) - live code, stage .new.
- Journal-dir loss: still unexplained; confirm execution/journal/ holds each open plan's file.
- NUC: re-enable filler only after operator reports < 85 C under load; operator TEMP > 30 d sweep still pending.
- Latency table again after bar-aligned polling / faster auto_trader poll land.
