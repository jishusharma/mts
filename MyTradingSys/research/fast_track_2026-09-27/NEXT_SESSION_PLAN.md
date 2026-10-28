# Next session plan - Opus supervisor, auto mode (written 2026-09-29 ~04:30 IST / 23:00Z by supervisor session 3)

Start a new session (+, Opus, auto or bypass mode) and send: **"Supervisor: read NEXT_SESSION_PLAN.md"**.
Read this file + STATUS.md only (`python scripts/dev/make_status.py` first). SUPERVISOR_LOG.md = history, don't re-read.
Previous plan (session 2) is at NEXT_SESSION_PLAN.md.pre_0929 - do not re-read it; everything still open is below.
Never mainnet. Never read .secrets/.env/keys. Never push/merge/rebase/reset.

## 0. First 5 minutes (T0 - scripts only)
1. `python scripts/dev/make_status.py` -> STATUS.md; `git log --oneline -15`.
2. `python scripts/worker/queue_tool.py status`; `ssh -i ~/.ssh/nuc_gate -o BatchMode=yes e-ngineers@192.168.29.110 status`.
3. Tail `research/fast_track_2026-09-27/HOURLY_CHECK_LOG.md` (3 lines) and `GATE_REPORT_2026-09-29.md` (new rows).
4. Processes that should be running on the desktop (check with
   `Get-CimInstance Win32_Process | ? CommandLine -match 'live_runner|loop-supervisor|start-trading-day|statemachine'`):
   - Tom core loop: `start-trading-day.ps1 -Mode armed` + `loop-supervisor.ps1` + Java `statemachine BTCUSDT`.
   - Alert runner (started 2026-09-29 03:46 IST, PID 7920, alert-only, public klines, 60 s poll):
     `python -m MyTradingSys.backtest.layers.alerts.live_runner_cli --poll-seconds 60`,
     logs Dumps/alerts/runner_logs/live_runner_2026-09-29.{out,err}. If dead, restart it the same way (Start-Process, hidden).
   - It must be run as a module (`-m`) from the repo root; `python .../live_runner_cli.py` fails with ModuleNotFoundError.

## 1. Operator decisions already made - do NOT re-ask
- Live testing = BOTH: Tom core testnet order runs + indicator-layer ALERTS (alert-only, never orders/filters).
- Promotion allowed (option A, 2026-09-29): builders may rename .new -> live and commit on fast-track after gates.
- **NEW 2026-09-29: "As and when we have new builds - commit changes - launch new tests - test edge cases as well."**
  Implemented in the hourly check (steps a2/a3, see section 5): every build gets spec-derived edge tests before promotion;
  any execution/ change re-runs the full testnet chain; alert changes re-run the runner --once. Apply the same rule to
  any build you gate by hand.
- Core ATR = plain SMA of TR (FORMULAS.md s12). L6 part 2 deferred for testnet; MUST be built before any mainnet use.
- C2 session = UTC day (1440 m); (params,horizon) = one PBO variant; Sharpe per trade (T055 driver).
- WQ_OAdz-PJ8 / zAwEX_tRUfE: "mostly Tom, maybe a guest" -> rules tagged by speaker; guest/unclear are not TOM rules.
- DSA (chat surface) does extractions by hand when the operator chooses (section 4).
- Still OPEN for the operator: Tom-vs-Fabio override ruling; T058 decisions (history fetch, hedge timing);
  moving the project C: -> F: (not started - needs a quiet window: loop, alert runner and NUC share must be stopped);
  cleanup/deletion list (T057 step 2).

## 2. Readiness - where we stand (verified 2026-09-29 ~03:45 IST)
| # | State | Evidence |
|---|---|---|
| R1 exec math | DONE | 08f5ea0, 61e55f3 |
| R2 full gate | DONE (session 2); `--quick` today: all green except Step 5b = test_turn_of_candle (module not built yet) |
| R3 testnet | **DONE again today**: base 6/6, G1/G2 4/4, FT-2 4/4 (14/14), no HALT left, account flat (size 0, equity ~99.9999) | testnet_runs/ft2_run_2026-09-29_a.log |
| R4 L6 | DONE (part 2 deferred) | |
| R5 layers + formula audit | Layers DONE. **Formula audit NOT done**: 082 BLOCKED (verdict FAIL, 2/5 expected, 1 unknown file); 083/084 never packed | Dumps/workers/NUC-QUEUE/done/082-* |
| R6 backtest baseline | DONE | BACKTEST_L1_REPORT.md: only 1h RSI-40 tol 0.5 robust (PBO 0.03), edge < fees; CryptoCred no edge |
| Alerts | LIVE (alert-only) | 085/086 promoted 0817968; --once today: 15 alerts, 0 errors |
**Testnet go-live (Tom orders + layer alerts): GO.** Orders are placed by the operator via `mts plan -> mts check -> mts guard -> mts trade`
(MTS_USER_GUIDE). The armed loop produces signals; it does not place orders by itself.

## 3. Work queue (cheapest tier first; agents return <=15 lines; spot-check one claim each)
- **Q1 (T1 Qwen, running next)** 0989-t055-c3-turn-of-candle-r2 = 0988 repacked (0988 died at 3072 output tokens on
  gpt-oss, which burns tokens on reasoning) with qwen3-coder:30b, OUTPUT_TOKENS 6144. Spec: nuc_specs/0989-*.md. The worker
  claims by name: 107 was already running at 04:00 IST, so 0989 runs right after it, before 108-111. When it lands, the hourly check gates it (its test already exists:
  layers/turn_of_candle/test_turn_of_candle.py) -> Step 5b goes green.
- **Q2 (T3 Sonnet) T055 backtest** once 0989 is promoted: promote run_t055.py.new + test_run_t055.py.new (22 stub tests),
  ADD FUNDING to C2/C3 net (holds can cross 00/08/16 UTC; data exists 2025-09+) - required before any pass is
  accepted - then run C1/C2/C3 (commands in T055 runbook; `--tf 1h` = C1 alt). Output T055_BT_c<n>.md. Any passing
  setup -> ALERT layer only, never a Tom filter.
- **Q3 (T3 Sonnet) Fabio backtest (W4)**: driver MyTradingSys/backtest/layers/fabio/run_backtest.py is UNTRACKED and has
  never been run; fabio_escalation is now promoted (a408fa6), so it is unblocked. Gate the driver, run it, write
  FABIO_L1_REPORT.md. Operator's question: "is core MTS + Fabio producing quality setups?"
- **Q4 (T2/T3) R5 formula audit**: find why 082 failed (verdict lists 1 unknown file name + 3 missing EXPECT lines), re-split
  to <=5k prompt tokens, OUTPUT_TOKENS big enough for the whole reply, pack 082r/083/084 on qwen3-coder.
- **Q5 (T2 Haiku) Fabio extraction holds** - after the quote-checker fix (section 6):
  - 103 (8CWKfoSJu3c): all 9 quotes are verbatim; 6 have the wrong BEGIN/MIDDLE/END tag. Retag each to the third the
    checker reports, re-run the check, commit.
  - 104 (FawPr chunk a): BLOCKED at the output cap -> repack with a bigger OUTPUT_TOKENS on qwen3-coder.
  - 105 (FawPr chunk b): re-run the check after the fix (1 problem left). Haiku wrote an unscoped file
    extracts/processed/fabio_valentini/FawPrRUGNpk/extract_FawPrRUGNpk_2of3.md (uncommitted) - review it before use.
  - 099 PARTIAL (out-of-scope extract not written) - check the verdict and repack if it is worth it.
- **Q6** T040 tick layer: modules 091-093 are promoted, but the full-history tier table (tiers.json / bounds) has NOT been
  computed on real data yet -> Sonnet runs tick_extremes on Dumps/backtest/raw_1m_2022 (+ recent months) and the OI metrics,
  writes the tiers, then 093 flagger can run live (flags = context only, never gate Tom).
- Later (filed, not started): T054 US session/correlation/news, T053 two-account hedge research, T058 broken extremes
  (research doc T058_BROKEN_EXTREMES.md done; decisions open), T048 satellite, T057 declutter (inventory -> operator list).

## 4. DSA pack (operator runs by hand) - Dumps/workers/DSA_PACK_2026-09-29/
**DONE 2026-09-29: all 4 extracts committed (35 rules, all quotes verbatim; 14 GPS tags retagged to the checker's third).
3 rules use `Topic: exit`, which is outside the topic list (map it to management/target when consolidating). Next: consolidate FAB-/T- rules (supervisor review; guest-speaker check found none).**
README.md + 4 paste files (instructions + full transcript, 9-24 KB each): Fabio 0KyIEdvVKMQ (replaces NUC 100/101),
Fabio 0jM5Y31YJak (replaces 102), Tom-channel WQ_OAdz-PJ8 and zAwEX_tRUfE (never extracted; speaker tags).
The operator saves each reply to the path in the README and runs verify_extract_quotes.py. When one appears: re-run the
check, then commit (one commit per video). Canonical transcripts for these 4 were added to raw_transcripts_canonical/
(timestamps stripped). Tom 7BQ/96i/HyS/aud/gWj/hQ8/pgd were ALREADY extracted and committed (01d0eed, all PASS):
duplicate tasks 112-120 were withdrawn to Dumps/workers/NUC-QUEUE/held/withdrawn_dup_tom_2026-09-29/ (saves ~5 NUC hours).
Don't re-queue them.

## 5. Automation that runs without you
- Scheduled task `mts-hourly-builder-check` (~:42 each hour; file ~/.claude/scheduled-tasks/mts-hourly-builder-check/SKILL.md):
  Haiku gates new Qwen replies, promotes + commits passes, HOLDs the rest, logs HOURLY_CHECK_LOG.md.
  Updated 2026-09-29: (a2) spec-derived edge tests (4-10) before promotion; (a3) execution changes -> HALT check + full
  testnet chain, commit only on 6/6+4/4+4/4; alert changes -> runner --once, errors>0 = rollback; (b) extraction list =
  fabio 099-111 only.
- NUC: qwen3-coder:30b + gpt-oss:20b; FLASH_ATTENTION=1 and KV q8_0 set (machine env, verified via ssh `env`).
  Queue after tonight: 0989, 107-111 (Fabio). Keep it non-empty: when < 2 waiting, write the next specs (Q4, Q6, T054).
- Desktop power: display/sleep never, screensaver off, CONSOLELOCK 0 (verified by operator). The Claude app must stay open.

## 6. Session 3 close-out (2026-09-29, ~03:40-04:40 IST)
- Testnet chain 14/14 PASS again (log in testnet_runs/). Account flat. No HALT files.
- Alert runner started continuously (section 0).
- Quote checker bug FIXED: verify_extract_quotes.py treated caption markers like "[0:02]" as words, so any quote that
  crossed a marker was reported MISSING (the cause of the 103/105 "bad quotes" holds; Qwen's quotes were verbatim).
  New test scripts/dev/test_verify_extract_quotes.py (5 tests; 2 fail on the old code, 5/5 pass on the new).
  All 7 committed Tom extracts still PASS.
- Sonnet gate agent on the 5 real stale builds (edge tests written for each):
  - bt_rsi PASS d30a57c (13 + 11 edge). Real bug fixed: the seed divided by the count of nonzero moves, not by `period`
    (FORMULAS s1). Supervisor hand-checked: period 4 on 1,2,1,2,1,2 gives 50.0 then 62.5.
  - prob_table PASS 8614eaa (12 + 9 edge): skips records with no ts; log-loss averaged over scored records.
  - fabio_escalation PASS a408fa6 (4 + 10 edge): import fixed; only the FIRST absorption counts (escalation could never fire);
    empty bars -> ValueError.
  - cc_retest/cc_structure .new tests NOT promoted: they differ only by a loader for non-existent .new modules; live 20/20 pass.
  - extract_nuc_files.py.new HOLD: needs a spec-derived test.
  - run_all_tests.py: Step 4 now pytest-collects the bt_rsi/prob_table tests; new Step 3d = quote checker tests.
    `--quick` after all of it: every step PASS except 5b (test_turn_of_candle, waits on 0989).
- The other ~20 `.new` files listed in STATUS.md are byte-identical leftovers of already-committed builds (gitignored). They
  are harmless; delete only with operator OK (T057). execution/README.md.new differs from live: review, don't auto-promote.
- run_t055.py.new / test_run_t055.py.new wait on 0989 (Q2).

## 7. Gotchas (new in session 3; older ones are in LESSONS_LEARNED / SUPERVISOR_LOG)
- Line-based chunking breaks on single-line transcripts: 113/116/119 "-a" chunks held only the 4 header lines. Chunk by
  characters/words, or send the whole transcript when it fits (<= ~5k tokens).
- gpt-oss:20b spends output tokens on reasoning; code specs on it need about 2x OUTPUT_TOKENS, or use qwen3-coder.
- The hourly check's verdicts are only as good as the checker - when many quotes fail at once, test the checker first.
- `python path/to/live_runner_cli.py` fails; use `python -m ...` from the repo root.

## 8. Operator asks, last 24 h (2026-09-28 03:00Z -> 2026-09-29) - status
| Ask | Status |
|---|---|
| Execute CODE_MODE_BRIEF / FIX3; remove "left for me" steps | DONE - FIX3 verified (116 offline OK, suites green); supervisor now runs testnet suites itself |
| Cheap-worker roadmap; Qwen-first; token efficiency; Opus-supervisor session model | DONE - WORKER_ROADMAP.md, memory notes, hourly scheduled Haiku gate |
| Malkan RSI as its own layer + 5-star setup (web first, then videos) | Web research DONE (malkan_rsi_2026-09-28/WEB_RESEARCH.md; 5-Star = Grandfather/Father/Son); malkan_40_60 + malkan_mtf layers committed (079 ae30eda). No video extraction yet |
| Lessons -> DSA/instructions updated continuously | DONE through 2026-09-28 (LESSONS_LEARNED + CLAUDE.md); session-3 lessons in section 7, to fold in |
| Backtest everything; Qwen for backtest work; 1m history back to 2022 | 1m 2022-01..2025-08 downloaded (44 files, 210 MB). L1 backtest DONE. Fabio + T055 backtests PENDING (Q2, Q3) |
| FORMULAS.md for every formula | FORMULAS.md exists (s1-16). The audit of code against it (R5) is NOT done (Q4) |
| NUC: SSH control, keep-alive, CPU/GPU tuning, new model | DONE - ssh gate, FLASH_ATTENTION + KV q8_0, gpt-oss:20b pulled (weak on code specs, see 7) |
| MTS User Guide + script automation (less AI-dependent) | DONE - mts.ps1 + MTS_USER_GUIDE + guide checker in gate (309d115) |
| Android phone -> Code mode (`claude rc`) | `claude` CLI is not on PATH in PowerShell; not resolved in the repo. Use the app's Remote Control badge instead |
| Tick indicators: all-time extremes of CVD/OI/net delta per 1-15m -> tiers -> live flags (T040) | Code DONE (091-093 promoted); the full-history tier run is NOT done (Q6) |
| Is the project cluttered / deductive / optimized? (T057) | Filed + plan; T0 inventory tools promoted (094-096); cleanup needs the operator's list approval |
| Fabio work now + market read | Fabio detectors 087/089 committed, escalation being gated, backtest PENDING (Q3); market read was given in chat 2026-09-28 |
| "All possible changes to go live" | DONE - testnet GO (section 2) |
| Research per MTS protocols; discard legacy junk | DONE - research gate v3 (b9d0dcb), T055 research remediated |
| Regular Qwen audits that feed Claude | DONE - T056 + 094-096 promoted; the hourly check backfills audits when the queue is idle |
| Use NUC SSD as memory | Advice only (not actionable as RAM); no change made |
| Move project C: -> F:; restore points | Restore points reduced by operator (15% -> 5%). Move NOT started (section 1) |
| T053 / T054 / T055 / T058 research items | Filed. T055 research done (T055a/b) + modules 0985-0987 committed, C3 in queue; T058 research doc done; T053/T054 not started |
| RSI-40 setting for live alerts = backtested one | DONE - runner uses 1h/15m RSI-40 tol 0.5 (0817968) |
| Permissions: stop asking | settings.local.json allow rules + bypass mode (operator toggled) |
| Keep the PC awake overnight | DONE (display/sleep never, verified) |
| 2026-09-29: go live -> launch as many testnet tests as possible | DONE - 14/14 testnet PASS, alert runner live, offline gate green except C3 |
| 2026-09-29: give DSA pending extractions | DONE - section 4 |
| 2026-09-29: new builds -> commit, test, edge cases | DONE - hourly check updated; 3 stale builds promoted with 30 edge tests, which found 3 real bugs (RSI seed, prob_table log-loss, escalation never firing) |

## 9. TESTNET AUTO-TRADING - LIVE since 2026-09-29 04:12 IST (operator: "trade now with what works; every new layer gets fresh trades")
- `MyTradingSys/execution/auto_trader.py` (d77d67c): orchestrator only -> new_plan --yes -> executor --go -> position_manager.
  Tom: SETUP_FORMING/CONFIRMED, net R:R >= 2, alert <= 5 min old, limit at ENTRY with the alert's stop/target, 200 USD / max loss 25.
  Layers: any alert in MyTradingSys/runtime/alerts/*.jsonl with a side (rsi support/rejection/cross mapped in config; others need a
  "side" field) -> market, 1% stop, 2% target, 100 USD / max loss 10. One trade at a time; skipped_busy/rejected logged per source.
  Log: MyTradingSys/execution/auto_trades.jsonl (`mts autolog`); state auto_trader_state.json; manager logs journal/auto_manager_logs/.
  Config overrides: MyTradingSys/execution/auto_trader_config.json (optional; keys tom/layers/layer_rules/disabled_layers).
- Running detached (Dumps/alerts/runner_logs/*.out/.err): auto_trader (PID 21908), daily_loss_monitor (PID 7312, 500 USD cap),
  live_runner_cli (restarted by the wiring agent with more layers - see its commit), Tom core loop (armed).
  The hourly check (step 3b) restarts any of them that dies (never after HALT_DAILY_LOSS), wires newly promoted layers
  into the runner via a Sonnet agent, and logs a per-source scoreboard.
- Smoke trade through the real path: L-mkt-0928-2240-2 long 100 USD filled 83450, stop 83200, target 83700 (manager PID 22584).
  While it is open, the auto-trader's next attempt is refused by the R8 one-position preflight (logged entry_failed) - expected.
- Parallel agents launched 04:15 IST: (1) wire fabio_volume_fvg / fabio_escalation / session_momentum / funding_cvd_fade /
  malkan / cryptocred into live_runner_cli with side fields; (2) Fabio L1 backtest -> FABIO_L1_REPORT.md; (3) T055 C1/C2 backtest
  with funding -> T055_BT_c1/c2.md. Check their commits (git log) - each ends with a recommendation for live sampling.
- QUESTIONS FOR THE OPERATOR (noted, not blocking - defaults in use):
  Q1 Layer bracket 1% stop / 2% target / 100 USD for every layer - or per-layer brackets from the backtests once reports land?
  Q2 One testnet account = one slot: Tom and layers compete. Use a Deribit testnet SUB-ACCOUNT per layer family so layers never
     block Tom? (needs new testnet keys from you; executor supports one account today).
  Q3 Layers with "no edge" in backtests (CryptoCred, RSI cross): keep sampling on testnet or disable (config disabled_layers)?
  Q4 Daily-loss cap stays 500 USD on testnet?
