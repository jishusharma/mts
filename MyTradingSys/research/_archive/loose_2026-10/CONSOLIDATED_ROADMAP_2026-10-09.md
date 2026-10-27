# CONSOLIDATED ROADMAP AND STATE (2026-10-09)

Built from: STATUS.md, PROJECT_VISION.md, MyTradingSys/archive/worker_roadmap_2026-10-15/WORKER_ROADMAP.md, SUPERVISOR_LOG/INBOX, AUDIT_MAJOR_GAPS_2026-10-09.md, BUGS.md,
bigtrade PLAN/FINDINGS/BIGMOVES/FIRES_B1/CAPTURE_MATRIX_SPOT. Not a spec; a pointer. Verbatim operator text in PROJECT_VISION.md is untouched.

## 1. Corrected vision (one paragraph)
Tom's core is the engine; every other system (RSI/Malkan, CryptoCred, Fabio, session, positioning, probability) is a switchable,
read-only module that never gates the core (PROJECT_VISION doctrine 2026-09-23, Q1-Q3 2026-09-25). Two things changed since that text:
1. 2026-10-09 operator directive: backtesting exists so layers FIRE on big, profitable trades; parameters may be tuned toward that
   (labelled BT-TUNED, never written to live files by a worker). It is no longer only a pass/fail edge gate.
2. 2026-10-06 provenance ruling: the NO-SOURCE 0.1 % stop floor was removed. Nothing replaced it (B146). Provenance still applies to
   everything except the tuning override above.
Stale doc, resolved 2026-10-15 (WORKER_ROADMAP.md archived to MyTradingSys/archive/worker_roadmap_2026-10-15/WORKER_ROADMAP.md): it routed work to the decommissioned NUC/Qwen lane (decommissioned 2026-10-01);
what_is_next.md is from 2026-09-16 and open_loops_status.md from 2026-09-16 (both superseded by this file + BUGS.md).

## 2. What is being worked on right now
| Thread | State |
|---|---|
| Big-trade backtest (PLAN.md A-F) | A (big-move ground truth) done, B1 (kline fire history, spot rerun, parity 92-100 %) done, capture matrix done. B2 (order-flow/Tom/funding fires), C (exit-policy), D (walk-forward tuning), E (gap list), F (chart observations) not finished. |
| Audit action list (SUPERVISOR_INBOX 2026-10-09) | B148, B146, B147 requested first. All still OPEN. Operator asked for a freeze on new audit docs and new layers until they report. |
| Options module (Deribit) | Collector, engine, DSA task 2301-2303 pushed to origin. Separate layer. |
| Volume study | Finished: NO-EDGE verdict, holdout sealed. |
| Git | The 4 merge conflicts were resolved by another session (merge 921d70d, 08:13 IST). fast-track is 8 ahead / 14 behind origin; shipped via the mts-push worktree. |
| Runtime | NUC worker heartbeat 36 h old, DSA worker 198 h old (both unused since the NUC lane was retired; remove from STATUS). Live runner was dark 23 of 120 h in the parity window (F-BT-19). |

## 3. Accuracy: is MTS being optimised for it? Honest answer: not yet
- Capture matrix (spot, r 1.5 k 3): 0 of 34 layer/side rows have lift >= 1.15 at 96 bars. At k 5 only fabio:escalation 15m and malkan_bear 1h
  reach 1.2 / 1.17 (n 322-347 / 138); best leg capture of any layer is 14-17 % (cryptocred sr_flip 15m), and that layer's fires are
  49-100 % fee-dominated (stop under round-trip fee, F-BT-22). Most layers sit at lift ~1.0 = same as picking a random bar.
- Tom core: gross R -0.15 [-0.29, +0.04] before fees; net -2.9 R is inflated by tiny stops (B146) but the sign is robust. Live rule: 0 signals
  vs 19 in the older run on the same history, unexplained (B147). Holdout for Tom is burned.
- Live testnet 2026-09-28..10-08: 333 closed, 262 are turn_of_candle 1m (net -3.02 USD, 100 % time_exit), only rsi 1h reached targets (3 trades, +9.75).
  turn_of_candle FAILED its backtest yet is 79 % of trades (F-BT-02, needs operator yes/no).
- Therefore: the system is being measured for accuracy now, but no layer is yet tuned or proven. Steps C and D are the accuracy work; they are not done.

## 4. Gaps: four classes (PROJECT_VISION) mapped to open work
| Class | Open items |
|---|---|
| 1 Rule not extracted | Tom transcripts still extracting; DSA recon tasks 2111-2113 PARTIAL/BLOCKED. No coverage audit exists. |
| 2 Extracted wrong | Extraction gate (verify_extract_quotes) exists; no systematic re-audit; B142-B145 NO-SOURCE params flagged, not resolved. |
| 3 Implemented wrong | B146 stop floor, B147 Tom rule, B141 htf balance null, F-BT-09 Java volume profile does not conserve volume (300-690 pts POC error), F-BT-14 naked POC frozen since 2026-08-28, F-BT-12 vwap anchor mismatch, F-BT-20 swing ties, F-BT-21 duplicate alert rows. |
| 4 Wired wrong | B148 daily-loss re-auth as MAIN, B150 test gate is a hand-kept allow-list, B152 retention deletes data other tools read, B136 OI/LS/taker endpoints dead since 2026-09-24 (verify closed), F-BT-10/11 OI hourly-stepped and 46 h holes. |
| Evidence | B151 CryptoCred fill optimism, B154 no regime or session stratified verdict, trial registry has 20 rows vs 36 cited (branch research/agenda-2026-10-06 unmerged). |
Open bug counts in BUGS.md: HIGH 7, MED 24, LOW 7. HIGH = B090 (credit plan), B132, B138, B140 (WHEA disk), B146, B147, B148.
Nothing has been closed by the 2026-10-09 audit; the gaps are filed, not closing yet.

## 5. Ordered plan (cheapest tier that can do it; no NUC)
Order is by risk to money first, then by evidence quality, then by new capability.
| # | Work | Tier | Gate / note |
|---|---|---|---|
| 0 | DONE 2026-10-09: conflicts resolved (921d70d); ship via mts-push | T2 | |
| 1 | B148 daily-loss monitor: stop main-account re-auth, fail closed on account-list read error | T2 write + T3 test, T4 review | stage .new, fail-first test, supervisor deploy |
| 2 | B146 stop-width vs fee, pre-registered buckets; derive fee-based admission rule (no NO-SOURCE constant). Same cells as backtest D `stop_buffer_atr` | T2 | closes F-BT-01, F-BT-22 |
| 3 | B147 attribute Tom row drop 120,892 to 90,699; close B135; merge/archive research/agenda-2026-10-06 | T2 | until done: "insufficient N" for the Tom live rule |
| 4 | Operator decisions: net_rr floor (restore 2.0 / expiry / pause Tom); turn_of_candle keep-as-volume-generator yes/no | operator | blocks 5 and live slot share |
| 5 | Backtest C: exit policies on the existing fires (time_exit vs bracket vs BE+trail vs hold-to-structure), net of Deribit fees, limit-fill model | T2 | fires_spot already on disk |
| 6 | Backtest B2 (fabio v3, funding_cvd_fade, Tom rows) then D walk-forward tuning with trial registry + PBO, one HOLDOUT look per layer | T2/T3 | needs 5 first |
| 7 | B150 gate discovery (auto-find tests, blocklist-restore guard); B152 retention exclusions; B149 L6 settlement gap; B151 fill model | T2 | each with fail-first test |
| 8 | Gap list E finished: malkan_40_60/mtf, tick/OI extremes, HTF context, consensus writer, 1m big-move truth (F-BT-08) | T2 | feeds the next layer decisions |
| 9 | Java fixes F-BT-09, -12, -14: stage and deploy in a window with `mvn compile` + restart | T3 + T4 review | live path |
| 10 | Housekeeping: B140 swap SATA cable/port and back up D:, B138 Dumps copies, remove dead NUC lines from STATUS, mark stale docs in section 1 superseded | T0/operator | |
Freeze (operator request, still standing): no new layers and no new audit documents until items 1-3 report.

## 6. Where truth lives (read order for a new session)
1. STATUS.md (regenerate) 2. this file 3. BUGS.md (OPEN rows) 4. AUDIT_MAJOR_GAPS_2026-10-09.md 5. bigtrade_2026-10-09/PLAN.md + FINDINGS.md
6. SUPERVISOR_LOG.md claims (live-path ownership) 7. PROJECT_VISION.md (direction, verbatim, operator edit only).

## 7. Execution log (same day, after the first write of this file)
| Step | Result |
|---|---|
| 0 merge conflicts | Resolved (921d70d); shipped to origin/fast-track. |
| 1 B148 | Parts 1-4 DONE and DEPLOYED to the live tree 08:42-08:45 IST (daily_loss_monitor + auto_trader restarted by kill; supervisor revived both; trading resumed). Part 5 (heartbeat-age liveness) open. |
| 2 B146 | Measured: stops < 0.10 % = 57 % of Tom sim trades, 3.8-7.6 R fees each; gross R negative in every bucket. Gate `tom.max_fee_to_stop` deployed but OFF (recommend 0.3; operator enables). Java still builds tiny stops. |
| 3 B147 | Docs corrected, holdout recorded burned for Tom, Oct-7 FROZEN.md + 36-row registry on trunk. Row-drop attribution, B135 re-run, Tom DSR/PBO still open. |
| 4 operator decisions | NOT made (net_rr floor, turn_of_candle). Backtest C now answers the second: ToC nets -11 bp/trade = its cost, no exit policy changes it. |
| 5 Backtest C | Done: EXIT_POLICIES_REPORT.md. 1 of 114 cells positive in both splits (noise-level). Exit management is not the accuracy problem; the fires lack edge. |
| 6 B2 / D | B2 not started. D (tuning) NOT justified by C for existing fires. |
| 7 B150 / B152 | Gate discovery test + ungated safety tests wired; retention keeps audit data, archives trimmed heads. B149 L6 settlement gap, B151 fill model open. |
| 8-10 | Open: gap list E, Java fixes F-BT-09/12/14, B140 disk, B153 owner/end date. |
Uncommitted work of other sessions NOT shipped by this session: backtest/bigtrade/ (bigmoves, capture, fires_kline) and research/bigtrade_2026-10-09/ reports sit untracked in the live tree; their owner session should `sync.py ship` them.
