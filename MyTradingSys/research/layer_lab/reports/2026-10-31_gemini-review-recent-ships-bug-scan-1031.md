# Layer Lab Report: Cross-Vendor Bug Scan of Recent Fast-Track Code Commits

Task: gemini-review-recent-ships-bug-scan-1031
Lane: CODEX
Reviewer: Gemini 3.8 Flash (independent cross-vendor review)
Date: 2026-10-31 (UTC 2026-10-30 / local 2026-10-31)

## Summary of Findings

A cross-vendor diff-vs-Result audit was performed on the last 40 non-merge code commits touching `.py`, `.java`, or `.js` under `MyTradingSys`.

- Total commits analyzed: 40 (SOURCED: `git log --no-merges -40 --format=%h -- MyTradingSys/*.py MyTradingSys/**/*.py ...`)
- Commits with explicit `Result:` lines that faithfully reflect the commit diff: 37 / 40
- Commits without an explicit `Result:` line: 3 / 40 (Rows 26 `737bfb241`, 28 `ee93a23e1`, and 37 `be68493fd` - all three are standard git reverts where the revert tool left only `This reverts commit ...`)
- Commits requiring functional code FIX: 0 / 40
- Full evaluation table: `MyTradingSys/research/gemini_burn_2026-10-31/RECENT_SHIPS_REVIEW.md` (40 rows).

## Detailed Review Breakdown

| Row | Commit | Subject | Verdict | Key File:Line Cited |
|---|---|---|---|---|
| 1 | `30ac62e9f` | live_aid: Now table on top, click-through detail pages, news headlines with a BTC reading | OK | `MyTradingSys/tools/live_aid/live_aid_indicators.js:1` |
| 2 | `f00f800eb` | C26 arms run once per pre-registration: ride-to-level and fade-swept-take-out both NO | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/c26_arms.py:1` |
| 3 | `3b0aab742` | C26: 15m held retest of a high/low, then take-out: base rates vs control, IS/OOS | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/failed_retest_takeout.py:1` |
| 4 | `a69ee9a96` | SpikeFade: prior-day-high proxy beyond 3% cap returns null (no high+20); replay gate and A-C2 comments aligned | OK | `src/main/java/datafeed/SpikeFadeProfile.java:88` |
| 5 | `3a4f332e9` | cbp: re-land all-10-analysts + verdicts + weekday x2/Sat/Sun schedule with the 3 red tests updated | OK | `MyTradingSys/tests/test_cbp_query.py:124` |
| 6 | `9cf5a2191` | auto_trader fail-closed tests (19, 19/19 mutants caught) + vacuous-test audit of last 30 test commits | OK | `MyTradingSys/execution/test_auto_trader_failclosed.py:1` |
| 7 | `7f33c6067` | live_aid replay: money tile reads window.LIVEAID_OI; 10-30 18:50Z flush replayed through the rendered page | OK | `MyTradingSys/tools/live_aid/live_aid.html:813` |
| 8 | `4d0cc2def` | test_gemini_claim_skip: patch card_gate (run_job now gates on card state) | OK | `MyTradingSys/tests/test_gemini_claim_skip.py:20` |
| 9 | `f498acdcd` | ship: 4 file(s) (sim desk page click test) | OK | `MyTradingSys/research/sim_desk/test_page_click.py:1` |
| 10 | `4f9c3e6a4` | AIBridge B209/B210: INDEX status, doc-test safe wording | OK | `MyTradingSys/items/B209_dsa_aibridge_session_performance_defects.md:4` |
| 11 | `a101f3fd2` | revert 0e0a47879: cbp tests follow the new code, but Supervisor A reverted that code | OK | `MyTradingSys/tests/test_cbp_query.py:124` |
| 12 | `dbfea8616` | C25: Stoch RSI vs plain RSI on BTC 15m/1h/4h/1d, fee-net IS/OOS; Bible ask row | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/stochrsi_vs_rsi.py:1` |
| 13 | `12b43fe17` | AIBridge 0.7.3: run-lock expiry (B210), task gate FAILED=FAIL, kind from command, open-only tasks list (B209) | OK | `DSA_SESSION_PROMPT.md:90` |
| 14 | `0e0a47879` | fix red CI: cbp tests follow verdict window + new schedule | OK | `MyTradingSys/tests/test_cbp_query.py:127` |
| 15 | `908cbb858` | gemini_queue: serialise git worktree setup with lock + retry; GOLAS-B indicator relations | OK | `MyTradingSys/tests/test_gemini_queue_lock.py:1` |
| 16 | `b49677883` | live_aid: "What the money is doing" tile (price vs OI per venue, flush/squeeze, trapped side, C24 line) | OK | `MyTradingSys/tools/live_aid/test_oi_money.py:1` |
| 17 | `bb7731974` | ship: 7 file(s) (nextHighEvent + macro strip) | OK | `MyTradingSys/tools/live_aid/live_aid_indicators.js:1` |
| 18 | `bf3fcb862` | Eagle_Eyes: C24 OI path after a long flush vs next 1h/4h (operator 'OI is favouring what?') | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/oi_after_flush.py:1` |
| 19 | `e31013dfb` | T058 per-TF break event study re-land (ledger P0-45): W/1D/4h/1h/15m, DEV/VAL, fee-net from fees.py | OK | `MyTradingSys/research/tf_break_event_study_2026-10-30/RESULT.md:15` |
| 20 | `d05de4ef0` | research: re-land C21 lint-clean + C23 daily divergence / BB-mid-rejection shorts | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/daily_div_mid_reject.py:1` |
| 21 | `740540935` | Revert 3d777c49d (C21/C22 research): CI red at Step 4, test_lookahead_lint fwd-index hits | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/BACKTEST_CANDIDATES.md:27` |
| 22 | `3d777c49d` | research: C21 lower-BB pierce in breakdowns (15m/30m/4h) + C22 volume/positioning ideas from the 10-30 flush | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/bb_lower_pierce_breakdown.py:1` |
| 23 | `92aa0ab3d` | ship: 6 file(s) (Live aid fixture replay) | OK | `MyTradingSys/tools/live_aid/test_live_aid_replay.py:1` |
| 24 | `2b69616cd` | research: re-land C20 BB + RSI divergence study on shared fee model; score 13:20 pre-US map | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/bb_rsi_div_switch.py:1` |
| 25 | `0036c3445` | B163 v2 re-land: rename fee_R keys (cost inventory), catalogue row + artifact for the export | OK | `MyTradingSys/research/setup_alpha_beta_v2_2026-10/result_numbers.json:57` |
| 26 | `737bfb241` | Revert "Revert B163 v2 alpha/beta study..." | UNVERIFIED | `git show 737bfb241` |
| 27 | `afc08114b` | Revert B163 v2 alpha/beta study (a43b9fbff, 14502d93b): CI red at Step 3xt | OK | `MyTradingSys/research/setup_alpha_beta_v2_2026-10/setup_v2.py:1` |
| 28 | `ee93a23e1` | Revert "Revert splits guard + DEV-only BB map..." | UNVERIFIED | `git show ee93a23e1` |
| 29 | `067b81238` | Revert splits guard + DEV-only BB map (46cb4255e): CI red at Step 3w wiring gate | OK | `MyTradingSys/backtest/splits.py:1` |
| 30 | `2877e1fed` | G7: BTCUSDT stop-slippage proxy from public aggTrades by volatility tercile (DEV, 12 days) | OK | `MyTradingSys/research/gap_g7_stop_slippage_2026-10-18/SLIPPAGE.md:16` |
| 31 | `a43b9fbff` | B163 v2: run Alpha vs buy-and-hold and Beta per-sweep on DEV/VAL; RESULT, export, verdict rows | OK | `MyTradingSys/research/setup_alpha_beta_v2_2026-10/RESULT.md:1` |
| 32 | `e6c30a6f3` | Revert "research: C20 BB + RSI divergence direction-switch study on 15m BTC" | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/bb_rsi_div_switch.py:1` |
| 33 | `46cb4255e` | splits module + holdout guard; BB state map re-run DEV-only | OK | `MyTradingSys/backtest/splits.py:1` |
| 34 | `3478f85eb` | research: C20 BB + RSI divergence direction-switch study on 15m BTC (operator chart 10-30) | OK | `MyTradingSys/research/eagle_eyes_picture_2026-10-28/bb_rsi_div_switch.py:1` |
| 35 | `92ba795ed` | research: BB state map run on DEV 2022-2025 (map.csv + counts) | OK | `MyTradingSys/research/bb_state_map_2026-10/MAP.md:1` |
| 36 | `122323253` | live_aid: US open ladder (if up / if down) with measured reach and hold odds | OK | `MyTradingSys/research/us_open_levels_2026-10-30/RESULT.md:1` |
| 37 | `be68493fd` | Revert "T053 step 3: hedge variants backtest (1m BTC, DEV, taker fees)" | UNVERIFIED | `git show be68493fd` |
| 38 | `4a36c8a38` | T053 step 3: hedge variants backtest (1m BTC, DEV, taker fees) | OK | `MyTradingSys/research/t053_hedge_variants_2026-10-30/hedge_bt.py:1` |
| 39 | `1448911c7` | live_aid: verdict board + analysts panel (every roster analyst, levels as NOW/NEXT/LATER zones) | OK | `MyTradingSys/tools/live_aid/build_analyst_data.py:1` |
| 40 | `f8c5e4895` | live_aid: news headline panel, pulse tile, word tags (Tree News REST) | OK | `MyTradingSys/tools/live_aid/live_aid.html:116` |
