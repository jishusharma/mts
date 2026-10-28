# MAINTAINER REPORT 2026-09-29 (first run, standing Opus maintainer)

## 1. Declutter - desktop repo
- New T0 tool `scripts/dev/declutter_backups.py` (dry-run by default, `--apply` moves, never deletes).
  Classes: superseded (content in git history of the base / base committed after the backup / rejected
  worker output / `.new.new` / `.new` identical to live) - staged (in-flight .new) - unknown.
- Moved **163 superseded files** to `Dumps/_archive/2026-09-29/<same path>`; manifest with sha256:
  `Dumps/_archive/2026-09-29/MANIFEST.csv`. Breakdown: 101 content-in-git, 27 base committed later,
  12 `.new.new`, 23 rejected/raw (`_nuc_rejected/`, `qwen_raw_015_017/`, `.rejected_*`, stray `\uf03aTEMP/test_scratch`).
  Note: `qwen_raw_015_017/test_risk_guard.py.new` (import-path variant, STALE_NEW_TRIAGE "unmerged") is archived, recoverable.
- Deleted 26 `__pycache__` dirs. `git status` entries: 161 -> 50 (-> ~40 after .gitignore).
- `.gitignore`: `*.pre_*`, `*.rejected_*`, `*.qwen_raw`, `*.new.new`, `_nuc_rejected/`, plus live runtime state
  (`execution/journal/`, `execution/plans/*.json`, `halt_history/HALT_*`, `execution/*_state.json`,
  `orphan_watchdog.jsonl`, `runtime/alerts/*.jsonl`, `live_alert_state.json`, `runtime_data/ums.log`).
- Still staged (left alone, 11): bt_stats.py, formula_audit.py, test_cc_retest.py, test_cc_structure.py,
  execution/README.md, extract_nuc_files.py, 5 Java datafeed files (`*.java.new`). The 13 other .new in STATUS were identical/in git -> archived.
- For the supervisor (untracked, NOT backups - decide commit vs ignore): 4 layer tests
  (positioning/test_funding_cvd_fade, test_trade_costs, session/test_session_momentum, tick/test_tick_extremes),
  bt/_spec_checks/, backtest_xcheck/*.py (7), nuc_specs/0985-0988 + 130-132-SONNET, review/OPUS_PREMAINNET_AUDIT.md,
  HOURLY_CHECK_LOG / L1_WIRING_SLICE / S3_SUPERVISION / S5_MAINNET_FLAG.md, qwen_011_test_bt_data.py.txt,
  root CODE_MODE_BRIEF.md, NUC_SETUP_COMMANDS.txt, validate_runbook.py, `research/` (root, l1 tarball),
  scripts/setup/, scripts/worker/qwen_feeder.cmd, 2 raw transcripts + 1 extract, `.claude/`.

## 2. NUC (gate v3)
- Disk: C: 46.3 / 236.7 GB free; F: 200.4 / 238.9 GB free. Models on F:\ollama\models (qwen3.6:35b 21.1 GB,
  qwen3-coder:30b 17.3 GB) - untouched.
- C:\MTS-Worker\logs: 10 files, 0.1 MB, none > 7 days -> nothing to rotate.
- Scheduled tasks: removed finished `MTS-GateJob-nucsetup`, `MTS-GateJob-pull36` (both rc 0). Kept
  MTS-NUC-Worker, MTS-Ollama (both Running; MTS-Ollama now exists - earlier assumption f is resolved).
- **User TEMP = 38.8 GB, of which 36.9 GB (6,474 entries) older than 30 days** (Chrome `scoped_dir*` from
  2021-22, Diagnostics, Outlook Logging 1 GB). PROPOSE: operator approves `ps` script deleting TEMP entries
  > 30 days (not done: permanent delete, not MTS-owned). AppData 50.8 GB total, Downloads 5.7 GB.
- Warning noise: every ssh prints a post-quantum KEX warning (OpenSSH on NUC is old) - harmless; filter `^\*\*`.

## 3. Laptop (no access) - operator
- Nothing required for MTS. Optional: `git status` there if it holds a clone; archive `.pre_*` the same way.

## 4. Desktop disk
- C: 24 GB free of 122 GB (81% used). Repo: Dumps 1.1 GB (Dumps/backtest 1.0 GB), runtime_data 150 MB, .git 28 MB.
- PROPOSE (not done): move `Dumps/backtest` raw archives to an external/NUC F: share (~1 GB); run the same
  TEMP > 30 d sweep on the desktop (size not measured - du timed out); compare with Dumps/disk_baseline_2026-09-26T1805Z.md.

## 5. Latency - live path (from auto_trades.jsonl + journal L-mkt-0929-0200)
| Stage | Measured | Driver |
|---|---|---|
| bar close -> alert written | 0-60 s (avg ~30) | live_runner_cli `--poll-seconds 60` fixed sleep |
| alert -> auto_trader decision | 0-20 s (avg ~10) | auto_trader 20 s poll |
| bar close -> decision, fresh signals (n=10) | 7, 22, 46, 46, 47, 48, 61, 67, 70, 70 s | sum of the two polls |
| intent -> entry order placed -> filled | 0.33 s -> 0.63 s | Deribit REST |
| intent -> stop live | 1.27 s (target +1.9 s) | executor |
| new_plan + executor subprocess start | ~1-2 s (python start + imports x2) | subprocess.run chain |
| stale signals | 53 of 63 layer signals were 6-83 h old | backlog re-emit (fixed 6ad9fd0) |
| slot occupancy | one 15m trade held 6.9 h -> 6 skipped_busy | `--hours` = entry window, no time exit |

Qwen pipeline (156 tasks since 09-27): queue wait median 514 s (p90 2.0 h); model time median 328 s
(p90 1,202 s); reply -> verdict file median ~6 h (verdict mtime, approximate); NUC idle 28.7 h of a 45.3 h span
(63%, gaps > 10 min). Mix: qwen3-coder 149, qwen3.6 4, gpt-oss 3.

## 6. Top 5 optimizations (gain / effort / risk)
1. **Free the single slot**: real max-hold time exit in position_manager (or per-layer sub-accounts, operator Q2).
   Gain HIGH (6 lost signals today) / effort M / risk M (safety path: Opus review, fail closed).
2. **Map `rsi:failure`** (12 rejections today) - needs a research decision per level (failure at 60 -> short?,
   at 40 -> long?) from backtest, then one `layer_rules` line. Gain M / effort S / risk M.
3. **Bar-aligned alert polling**: sleep until next bar close + 3 s instead of fixed 60 s. Gain ~30 s avg
   latency / effort S / risk L (alert-only process; restart by operator).
4. **Auto-verify Qwen replies on arrival** (background watcher calling `queue_tool.py verify`) + feeder keeps
   >= 2 tasks queued. Gain: ~6 h verdict lag and 63% NUC idle / effort S / risk L.
5. **auto_trader poll 20 s -> 5 s** (or alert-file mtime check). Gain ~8 s avg / effort S / risk L.
   (In-process new_plan/executor would save ~1-2 s: low gain, not worth touching live code.)

## 7. Accuracy - signal -> plan mis-translation risks (proposed only)
- `rsi:failure` unmapped; `rsi:cross` maps up->long / down->short regardless of level (40 vs 60 semantics differ).
- 15m RSI alerts carry `"rsi": null, "rsi_ma": null` - no value audit trail for post-trade review.
- Layer bracket fixed 1% stop / 2% target / 100 USD for every layer and tf - not from each layer's backtest.
- `--hours` reads like a time exit but is only the entry window (see 6.1).
- `t_close` is the bar OPEN time (commented in code; naming trap for new code).
- Units: size_usd -> BTC-PERPETUAL amount in USD (100/200 are valid multiples of 10); a non-multiple config
  value should be refused in new_plan - not verified that it is.
- Reject text uses `alert.get('event')` while the key uses the event/kind/sub fallback (cosmetic).
- No Sonnet fix applied: every candidate touches a live-imported file (auto_trader, live_runner_core) and would
  need a restart, which this role may not do. Stage as .new in a batch the supervisor schedules.

## 8. Lessons + rule changes applied
- LESSONS_LEARNED.md section F: 11 entries (seed a-i verified: fixes 1542151, 6ad9fd0 exist; MTS-Ollama task
  exists now) + recurring pattern (14 commits on false halt/stale/fail-open) + `--hours` naming trap.
- CLAUDE.md +8 lines: live-tree rule in every builder brief; live-path tests (restart/reset/transfer/API error,
  fail closed); no conclusions from truncated output; declutter tool.
- Memory: new `live-tree-staging.md`, `supervisor-thinking-checklist.md`; `nuc-ssh-gate.md` updated (tasks,
  models path); MEMORY.md index fixed (mojibake, gate v3 summary). Item d already covered by operator-tasks-verify-yourself.

### Supervisor thinking checklist
1. Verify before asserting; quote the number. 2. Read full output, never truncated. 3. Parse the real format before
counting. 4. Does a running process import this file? -> stage .new. 5. Ask restart/reset/transfer/partial fill/API
error for live changes. 6. Safety checks fail closed; empty model reply = failure. 7. Check operator tasks yourself.
8. Confirm infra exists before relying on it. 9. Read what a parameter does, not its name. 10. Check summaries item by
item vs the request. 11. Spot-check one claim per worker report. 12. Cheapest tier; Opus reviews safety ordering.

## 9. Next run
- Supervisor decision on the untracked list in section 1 (commit tests/specs/audit or ignore).
- Operator: approve NUC TEMP > 30 d sweep (36.9 GB); desktop TEMP size check.
- Schedule batch: time-exit / sub-account slot (6.1), bar-aligned polling (6.3), auto-verify watcher (6.4).
- Research: rsi:failure mapping + per-layer brackets from backtest.
- Re-run `python scripts/dev/declutter_backups.py` (dry run first); regenerate STATUS.md.
- Re-measure latency table after 6.3/6.5 land (needs >= 20 fresh signals).
