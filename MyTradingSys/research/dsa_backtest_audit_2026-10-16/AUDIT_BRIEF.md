# DSA backtest audit pack (2026-10-16)

Ten audits of the MTS backtests. Each is one card `dsa-audit-NN-*`, run by one DSA chat (DeepSeek + AIBridge).
Purpose (operator 2026-10-16): find the issues, missing aspects, defects and bugs in the backtesting we do.
Each audit attacks from a different side, with a method no earlier audit used: the input data, time and look-ahead, known-answer inputs, an independent rebuild, placebo nulls, costs and fills, reproducibility, the split and the trial count, backtest-to-live parity, and a failure-mode checklist.

How to use this file: read sections 1-7 in full (they apply to every audit), then only your own part of section 8.
Where this file and the paste prompt differ, this file wins. On safety, DSA_SESSION_PROMPT.md section 0.3 wins over both.
Sections 1-2 come from the coordinator's read of origin/fast-track at 30c4efdc (16 Oct 2026, 04:21 IST). They are evidence, not truth (rule 3.11): check one claim on disk before you build on it.
Paths are relative to the repo root. `R/` = MyTradingSys/research/, `B/` = MyTradingSys/backtest/, `S/` = MyTradingSys/system/.

## 1. Where backtesting stands (16 Oct 2026)

### 1a. The process
- Gate ladder for every idea: G0 sources, G1 extract, G2 catalogue, G3 blind chart read (the operator is reader 1), G4 encode, G5 DEV event study, G6 validate; then shadow, then testnet.
- Main split (R/volume PRE_REG_VOLUME_2026-10-09.md:23): DEV before 2024-07-01. VALIDATION 2024-07-01..2025-06-30, read once per pre-registered hypothesis. HOLDOUT 2025-07-01..2026-09-30, sealed (rule A7: only the operator opens it).
- There is no shared split module. Each script defines its own; 8 schemes are in use:
  - Tom protocol: DEV from 2025-09-01, burned HOLDOUT from 2026-06-26 (R/core_readiness_2026-09-27/BACKTEST_PROTOCOL.md section 2).
  - Qriptal: DEV 2025-09-01..2026-06-25.
  - Footprint track: DEV 2024-12-02..2025-03-31. This lies inside main VALIDATION; each read is logged in R/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv.
  - B/bigtrade/fires_kline.py:79: 2025-01-01 / 2025-07-01 / 2026-10-01.
  - Calendar years: R/orderflow_views_2026-10-14/study.py:213.
  - published_strats: 2021..2023-06.
  - DAX: 2024-11-04..2026-04-10.
  - Floating 70/30 bar-count split: B/layers/run_t055.py:101, rsi/run_rsi_backtest.py:76, fabio/run_backtest.py:64, run_cc_setups.py:250.
- G5 screen pass bar. All five must hold:
  - n >= 200;
  - mean gross >= 0.14% (net >= 0);
  - t_net >= 2;
  - DIFF vs control >= +0.05% with t >= 2;
  - max drawdown no worse than buy-and-hold.

  SE is clustered by day; MDE = 2.8 SE.
- Every parameter is labelled SOURCED (the trader's words, quote + file:line) or OURS (judgement or tuned). OURS is allowed but is never called the trader's.
- Cost:
  - New screens: 0.14% round trip, i.e. 2 x (5 bp fee + 2 bp slippage), a literal at screen.py:30.
  - Other studies hard-code 0.10%, 0.12%, 0.20% or 6 bp per fill.
  - B/fees.py:23-28 holds the venue fees: Deribit taker 0.05% / maker 0; Binance taker 0.05% / maker 0.02%.
  - The testnet trades on Deribit test.

### 1b. Latest results (DEV unless named)
| # | Study (folder under R/) | Verdict | Key numbers | Cost |
|---|---|---|---|---|
| 1 | Session-extreme fade + 1m delta (gross_effect_screen_2026-10-15) | INCONCLUSIVE | n_T 40, mean -0.0568%, t -1.51; control n 1439, -0.0081% | 0.14% + flat 1 bp funding |
| 2 | Pre-open tops (opr_preopen_tops_2026-10-16) | INCONCLUSIVE | H1 n 105, -0.0111%; H2 n 104, +0.0373% | 0.14% |
| 3 | MAL BB mid engulf (mal_bb_mid_engulf_2026-10-16) | FAIL | A1 n 1179, +0.0124% gross, t_net -6.02; A2 n 807, +0.0143% | 0.14% |
| 4 | BB MTF centre (opr_bb_mtf_center_2026-10-16) | INCONCLUSIVE | AU n 194, +0.0196%; AD n 282, +0.0322% | 0.14% |
| 5 | Weekly-low round sweep (opr_weekly_low_round_sweep_2026-10-16) | FAIL | RL n 685, +0.0317% (634 of 685 round-number-only); AS n 525, -0.0389% | 0.14% |
| 6 | Weekly-low bounce BB/RSI60 (wlow_bounce_bbrsi60_2026-10-16) | INCONCLUSIVE | n 8, 4h mean -0.293% (1h bars) | 0.14% |
| 7 | Krown/Malkan event counts (krown_malkan_g3_2026-10-16/EVENT_COUNTS.md) | counts only | BTC 1d KR-S1 n 278, MDE 0.24R, ENOUGH; KR-S8 n 29 and every weekly/MAL row THIN | 0.10% |
| 8 | Qriptal calls (qriptal_2026-10-10/SCORECARD.md) | n = 0 scored | 70 candidates; the 2 eligible rows are in HOLDOUT, unread | 0.05%/side |
| 9 | Candle close (layer_lab/candle_close_2026-10-14) | FAIL | 0/126 arms; net means -26.83..-4.68 bp | 0.14% |
| 10 | Levels sizing (levels_sizing_2026-10-14) | FAIL | 8/8 variants lose, -0.195..-0.216 R, 117 campaigns | 6 bp per fill; footprint window |
| 11 | Level hold rates LC1 (levels_confluence_2026-10-14/levels_hold.md) | KEEP 8 of 12 | hold rate vs random lines, no P&L | footprint window |
| 12 | Order-flow views (orderflow_views_2026-10-14) | NEGATIVE | 0/12 arms; DEV, VAL and HOLDOUT all published | 0.10% |
| 13 | EUR low US sweep (eur_low_us_sweep_2026-10-14) | exploratory negative | retested-low days break the low 57% (n 99) vs 26% (n 1027) | 0.05%/side |
| 14 | MFE exits (mfe_exit_2026-10-13) | nothing survives | turn_of_candle gross about +0.3 bp, same as random control | 0.10% + real funding |
| 15 | Published strategies (published_strats_2026-10-13) | FAIL | 0/62 clear DEV at BH q <= 0.10 | 0.10%/side + funding |
| 16 | Tom/Fabio guidance matrix Q33 (tom_fabio_guidance_2026-10-12) | FAIL | 336 cells, 0 survive, min q 0.62 | per report |

Testnet (R/overnight_2026-10-16/MORNING_REPORT.md):
- HALTed; deploy STOP_DIRTY.
- Last 7 days: 486 trades, net -40.81 USD, profit factor 0.38, 97% of exits by time.
- LEDGER_EXIT_AUDIT.md: 17 of 24 "target" exits were really stops. classify_exit is fixed; old rows are not rewritten.
- None of the 20 `pre_pipeline_sources` in MyTradingSys/execution/auto_trader_config.json has a positive out-of-sample verdict. promoted_setups.json is empty.

Tom/Fabio intraday: at the stop sizes the traders state (0.044-0.13% of price), the 0.14% cost is 1.1-3.2 R. Every such row loses by construction (R/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md).

### 1c. Infrastructure
- **Engines:**
  - B/bt/bt_engine.py simulate_trade (CryptoCred, RSI);
  - B/tom_bt.py sim_limit_trade (:175);
  - B/tom_dax_bt.py;
  - B/sim.py;
  - B/layers/run_t055.py with B/layers/positioning/trade_costs.py;
  - B/layers/fabio/run_backtest.py and run_v3_l3.py;
  - B/layers/rsi/run_rsi_backtest.py;
  - B/bigtrade/{fires_kline,exit_policies,capture}.py.

  The new screens are standalone: R/gross_effect_screen_2026-10-15/screen.py, R/chart_read_g5_2026-10-16/common.py, plus one study.py per study folder.
- **Stats:** B/bt/bt_stats.py (PSR, DSR, CSCV-PBO), B/power_mde.py, B/verdict.py.
- **Promotion:** B/layers/promotion/promote.py and registry.py; S/PROMOTION_PIPELINE.md.
- **Parity:** B/parity.py (verdict vs live log), B/bigtrade/parity_kline.py, B/tom_profile_parity.py.
  - No tool compares backtest fills with testnet fills.
  - execution/ records no decision price.
- **Live/testnet signal code:**
  - B/layers/alerts/live_runner_cli.py (build_default_registry, poll_once, fetch_closed_bars);
  - MyTradingSys/execution/auto_trader.py and position_manager.py;
  - auto_trader_config.json.
- **Tests:** B/test_*.py, B/bt/test_*, B/layers/**/test_*, MyTradingSys/tests. Research tests run through scripts/dev/run_extra_tests.py. CI installs only pytest, numpy and tzdata (.github/workflows/ci.yml:58).
- **Duplication:** 25+ kline/funding loaders, 5 session definitions, 8 split schemes, 6+ cost sets.

### 1d. Data on JIS-NB
Dumps/ is in the live tree, C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed/Dumps; F:/MTS/Dumps shows the same folders.
- **1m klines, BTCUSDT USD-M perp:**
  - F:/MTS/data/tom_raw/klines: 89 files, 2022-01-01..2026-09-26.
    - 2,501,280 rows, 2,491,200 unique. The 10,080 duplicates are 2025-09-01..07, present in both the monthly and the daily files.
    - 0 gaps. DEV = 1,313,280 bars.
  - Also Dumps/backtest/raw_1m_2022/klines (2022-01..2025-08) and Dumps/backtest/raw/klines (2025-09-01..2026-10-13).
- **Funding:** Dumps/backtest/raw/fundingRate. 81 monthly files 2020-01..2026-09, 7,395 records, every 8h, no gaps.
- **Footprint** (1m, 10 USD bins, built from aggTrades): F:/MTS/data/orderflow_1m. 666 daily files, 2024-12-02..2026-09-28.
- **OI metrics, bookDepth, markPriceKlines:** Dumps/backtest/raw/{metrics,bookDepth,markPriceKlines}, 2025-09-01..2026-09-26 only. None in DEV.
- **Daily/weekly:**
  - F:/MTS/data/krown_daily is Binance SPOT 2017-08..2026-09. It has microsecond stamps from 2025-01-01 and 8 gap weeks in the published 1w file.
  - Coinbase BTC-USD covers 2015..2026.
- **Also:** Dumps/backtest/raw_1d; F:/MTS/data/tom_snapshots (Tom Java snapshot rows, monthly 2022-01..2026-09); F:/MTS/data/dax_raw (Dukascopy, bid only, parked).

### 1e. Open leads
These are SUSPECTED from the coordinator's code read. The audit that owns a lead confirms or clears it, with evidence.
| Lead | What and where | Owner |
|---|---|---|
| L1 | **Funding reported as NOT_IN_DATA.** screen.py:298 and :400, and R/chart_read_g5_2026-10-16/common.py:19, look for F:/MTS/Dumps/backtest/raw_fund. The data is in Dumps/backtest/raw/fundingRate. The flat +1 bp substitute is charged to both sides, so shorts pay where they often receive. DEV funding ranges about -11.9..+8.8 bp per 8h. | T06 |
| L2 | **Floating 70/30 bar-count out-of-sample split** (run_t055.py:101; the RSI, Fabio and CryptoCred runners). Run on data reaching 2026, the out-of-sample part lies inside the sealed HOLDOUT. | T08 |
| L3 | **Costs hard-coded in 6+ forms** (10/12/14/20 bp, 6 bp per fill), despite fees.py:3 "no file defines its own fee constant". Net numbers are not comparable across studies. | T06 |
| L4 | **B/bt/bt_data.py load_klines (:10-28).** No microsecond-to-millisecond conversion, keeps the first duplicate, no gap check. Used by the RSI, CryptoCred, Fabio, T055, session_levels and tick runners. | T01 |
| L5 | **B/bt/bt_engine.py.** A timeout fills at the last bar's close (:93-96). The gap-through-stop test uses the trade bar's open while the stop hit uses the mark bar (:74, :79). funding=None silently means 0 (:39). | T03 |
| L6 | **Session clocks disagree.** tick_extremes.py session_tag uses fixed UTC minutes. session_levels.py has "US open 14:00 UTC" with no DST. fabio_of_model.py:118-125 and v3/day_gates.py:60-72 are DST-aware. opr_* use New York 09:30. B102 fixed only fabio_of_model. | T02 |
| L7 | **G5 verdict code** (common.py:192-230, screen.py:220-250). Drawdown of summed per-trade % is compared with buy-and-hold % of price. A study passes if any arm passes, with no correction across arms, horizons or the variant grid (40 rows in mal_bb trials.csv). 390-minute holds with a 60-minute cooldown overlap. | T05 |
| L8 | **LC1 controls** (R/levels_confluence_2026-10-14/levels_hold.py:78-93). Real levels count only when touched. Controls are midnight +/- the same distance with a random sign, so half the controls are the real level, and untouched mirror lines count as non-holds. The KEEP verdicts rest on this control. | T05 |
| L9 | **Gate coverage.** Three tracked tests are in no gate list: krown_malkan_g3_2026-10-16/test_event_counts.py, opr_bb_mtf_center_2026-10-16/test_study.py, opr_weekly_low_round_sweep_2026-10-16/test_study.py. chart_read_g5/common.py imports pandas, which CI does not install. | T07 |
| L10 | **Krown daily.** It is spot, not perp, with microsecond stamps from 2025 and 8 gap weeks in the 1w file. | T01 |

## 2. Already audited: do not repeat
Build on these and cite their IDs. A finding that repeats one of them is not a finding. A finding that shows one was wrong, incomplete or never fixed is.
- **R/backtest_gap_review_2026-10-13/REPORT.md, gaps G1-G8.** Power; DAX bid-only bars; synthetic testnet fills; the through_ticks flag; OI/depth data; the trial ledger; stop slippage; Deribit parity.
  - B/tom_bt.py:175 has the through_ticks flag, but run_variant (:228) does not pass it, so runs are still touch-fill. slip=0.0 at :176.
  - Naming trap: gap "G5" (data) is not gate G5 (event study).
- **R/fable_audit_2026-10-16/FABLE_RUNS_AUDIT.md E1-E7.** Count before freeze; one verdict per arm; cost-in-R gate; Holm promotion threshold; decision price on testnet; screen harness; completeness sweep. Also CATALOGUE_AUDIT.md and PROMOTION_REVIEW.md (H1-H3 shipped, M5 open).
- **R/layer_lab/reports/2026-10-15_strategy-direction-audit.md.**
  - N1: the OI arms cannot pass their split.
  - N2: orderflow_views books a gap through the stop at the stop price (unfixed).
  - R1: DIV is a subset of CONTROL.
  - N3: chart_lab.py:138 uses minute-open labels.
  - The footprint "exact" claim is an overclaim.
- **R/mts_flow_audit_2026-10-13/REPORT.md** (0a-9c, F1-F5). 6a: no planted-edge test for any simulator was ever filed. 7c: no kill rule.
- **R/pivot_pattern_audit_2026-10-14/REPORT.md.** engine.py:166 groups by bar-close day.
- **Other audits:**
  - R/layer_lab/candle_close_2026-10-14/INDEPENDENT_AUDIT.md A1-A8;
  - R/layer_lab/reports/2026-10-11_lab-audit-tom-dax-bt.md H1-H8, M1-M6;
  - R/non_core_layer_audit_2026-10-12;
  - R/layer_lab/reports/2026-10-15_gross-screen-gpt-audit.md (counts match; screen.py:259-267 overwrites DATA_MANIFEST);
  - 2026-10-15_gpt-catalog-notstated-audit.md;
  - R/overnight_2026-10-16/LEDGER_EXIT_AUDIT.md;
  - R/tom_fabio_guidance_2026-10-12/GUIDANCE_AUDIT.md.
- **Registers:** R/audits/AUDIT_DIGEST.md and S/LESSONS_LEARNED.md.

## 3. Hard rule: never wait (operator 2026-10-16)

DSA never waits for anything: not for the operator, not for Claude, not for another chat, not for a long job.
1. Until the card is shipped and closed, every reply ends with at least one AIRUN block. A reply without a block stops the run.
2. No questions. Where a choice is open, take the conservative default, write it in the report as `DECISION (OURS): <what, why>`, and go on.
3. A long job goes in task mode (cap 1800 s), split into chunks (one year, one month or one study per step), each chunk writing its own file. The last step merges them.
4. A check that cannot be done (data missing, script crashes twice, a refusal with no allowed equivalent) becomes a finding `BLOCKED: <what> (result #n)`. Then go straight to the next check.
5. No result came back after your blocks: do not wait, and do not resend the same block. Send a read-only heartbeat block: `hostname; (Get-Date).ToUniversalTime().ToString('o')`, the expected output file's existence, size and last line, and `git -C <WORKTREE> status --short`. Continue from what it shows.
6. When the card is shipped and closed, take the next `dsa-audit-*` card at once: `python scripts/dev/tasks.py next --lane DSA-NB` on JIS-NB (then `--lane DSA`). Stop only at the chat limit in section 7.

## 4. Bridge log and recovery (operator 2026-10-16: record how the bridge was used and how each failure was recovered)

### 4a. Bridge log (in every report)
A table with one row per bridge reply: result #, mode (plain or task), blocks sent / run, seconds, outcome, what you did next.
Outcome is one of: OK, NOT RUN, refused <code>, timed_out, out_truncated, STALE_REPLY, lines lost, extension_link, agent_unreachable, no result seen.
Under the table, three lines:
- Worked best: the call pattern that saved the most replies.
- Failed and recovered: each failure, the recipe used (4b) and the result # that proved the recovery.
- Rule for the next chat: one sentence.
A failure mode that is not already in MyTradingSys/system/LESSONS_LEARNED.md gets a lesson there and its one-line rule in LESSONS_DIGEST.md (DSA prompt 5c), shipped with the card.

### 4b. Recovery recipes
| What happened | What to do |
|---|---|
| `timed_out`, or a task step FAIL on time | It may have half-run. Heartbeat (rule 5). Rerun only the missing part, smaller, each chunk to its own file. Never resend an unchanged block. |
| `out_truncated` or a [TRUNCATED...] marker | Not a result. Write the output to a file, then read a count or a range of it. |
| `NOT RUN: block K ended with ...` | Fix block K first; then resend only the blocks that did not run. |
| `refused <code>` | Quote the code, use the allowed equivalent (DSA prompt 0.3 and 0.5), go on. |
| `STALE_REPLY`, or a result header whose command is not yours | Discard it; heartbeat; continue from what is on disk. |
| `lines=N` lower than the lines you sent | A line was lost: resend that block once. |
| `ERROR extension_link` / `ERROR agent_unreachable` | One line naming which (operator presses F5 / runs F:\AIBridge\scripts\start-agent.ps1 -Watch). In the SAME reply re-emit the pending block, so it runs the moment the bridge is back. Meanwhile write the report parts you can from results already in this chat. |
| The chat crashed, filled up, or the page lost it | Resume from the progress file (4c). |
| The same gate fails twice | STOP rule (DSA prompt 5e): `tasks.py` close as failed with "needs-Claude: <card>: <gate error>", post it `--target CLAUDE`, take the next card. |

### 4c. Progress file (crash recovery)
After every finished step, overwrite `Tnn_PROGRESS.md` in the task folder: worktree path, claim slug, card id, steps done (each with its result #), files written, the next step, open findings so far.
A new chat resumes with the words `RESUME dsa-audit-<nn>`: it finds the file with
`Get-ChildItem C:\Users\E-ngineers\IdeaProjects\mts-dsa-*\MyTradingSys\research\dsa_backtest_audit_2026-10-16\T*_PROGRESS.md`,
reuses that worktree (the crashed chat no longer uses it), checks `git -C <worktree> status --short` and the claim (`sync.py start` lists it), and continues from the next step. It never redoes a step whose output file is on disk and complete.

## 5. Audit rules
1. **Report; do not fix.**
   - Change nothing outside the task folder MyTradingSys/research/dsa_backtest_audit_2026-10-16/: no study code, no result file, no ledger row (except the exposure row in rule 3).
   - A fix is a card (rule 7).
   - Reruns write to scripts/<Tnn>/out/ or %TEMP%, never over a result file.
2. **Time windows.**
   - DEV only (before 2024-07-01) for anything that computes a return, a price statistic or a signal.
   - Footprint data only inside 2024-12-02..2025-03-31.
   - Checks on timestamps, row counts, file lists, column names and schemas may cover all dates.
   - Never read VALIDATION or HOLDOUT returns. From a result file that holds them, read dates, counts and column names only.
3. **Footprint reads.** Each read of the footprint window appends one row to R/gross_effect_screen_2026-10-15/EXPOSURE_LEDGER.csv, in its existing column format.
4. **Reruns.** A rerun reproduces; it never changes a verdict. A different number is a finding, not a new result.
5. **Evidence.** Every finding carries:
   - file:line at the fast-track sha you started from;
   - the bridge result # that showed it;
   - the script that reproduces it (under scripts/<Tnn>/, run from the worktree root).

   CONFIRMED = reproduced by a script. SUSPECTED = read in code, not reproduced.
6. **Severity.**
   - S1: could flip a verdict, or touches testnet decision code.
   - S2: changes a published number by more than 10% relative, or by more than 0.01 percentage points of mean return.
   - S3: nothing changes now; a risk later.
7. **Cards for S1 and S2.** Each S1 and S2 finding gets a raw card:
   `python scripts/dev/tasks.py new "<fix title>" --lane SONNET --prio 2 --ref MyTradingSys/research/dsa_backtest_audit_2026-10-16/<Tnn>_<slug>.md`

   For live-path code (MyTradingSys/execution/, live_runner_cli.py), post to Claude instead:
   `python scripts/dev/desk.py post "<title>" --need "<finding id + file:line>" --done-when "<the test that proves the fix>" --target CLAUDE`
8. **Data is read-only.** Synthetic and crafted files go under C:/Users/E-ngineers/AppData/Local/Temp/dsa_audit/<Tnn>/, never into F:/MTS/data or Dumps.
9. **The live tree** (C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed) is read-only for you. Read its files and count its rows; run code only from your worktree.
10. **Small and fast first.** A 20-line script that answers yes or no beats a framework.
    - To reproduce a number, use the study's own loader.
    - For the independent check, write your own.
    - Seed every random draw and print the seed.
11. **Report style.** The report opens with 3 plain lines a non-programmer can read. English only. No emoji.

## 6. Report format and close
File: MyTradingSys/research/dsa_backtest_audit_2026-10-16/<Tnn>_<slug>.md, with these sections:
1. **Summary:** 3 plain lines (what was checked, what was wrong, what it changes).
2. **Scope:** a table of what you checked (study or file, window, method, result #).
3. **Findings:** a table with these columns:
   - ID (Tnn-F1, Tnn-F2, ...);
   - severity S1/S2/S3;
   - CONFIRMED or SUSPECTED;
   - evidence (file:line, result #, script);
   - the verdicts or numbers it affects, with the measured size of the change;
   - the fix in one line;
   - the card id.
4. **Leads** from section 1e that you own: CONFIRMED, CLEARED (with the evidence) or BLOCKED.
5. **Not checked:** what you could not do and why (BLOCKED rows).
6. **Decisions taken:** `DECISION (OURS): ...` lines.
7. **Bridge log:** section 4a.
8. **Handover:** 5 lines for whoever fixes it: the top fix, the file, the test that proves it, the risk, what to rerun after.

Close, in this order:
1. `python scripts/dev/tasks.py done <card id> --result "<Tnn>: k findings (S1 a, S2 b, S3 c); <headline>"`. It rewrites S/LAYERS.md: commit that too.
2. `python scripts/dev/dsa.py commit "<Tnn> backtest audit: <headline>" --result "<same line>" --files <report> <scripts> <csv files> MyTradingSys/system/tasks/<card id>.json MyTradingSys/system/LAYERS.md <new raw cards>`
3. `# AIRUN task=mts-ship repo=<WORKTREE> timeout=1800` must end in TASK RESULT: PASS.
4. `git fetch origin`, then `git cherry origin/fast-track HEAD`. It must print nothing. Only then is the report shipped.
5. `python scripts/dev/sync.py release <slug>` only if step 3 shipped without `--release`.

## 7. Chat limit and order
- One chat runs at most 2 audit cards, or about 60 bridge results, whichever comes first. Then it follows DSA_SESSION_PROMPT.md section 12, with progress files current and every claim released.
  - The last reply says: "DSA chat done; next: new chat, session paste plus the next audit prompt".
- Cards run in any order. 01 to 10 is the suggested order.
- Two chats never run the same card: the claim decides. `sync.py start` lists open claims.
  - The prompt's card is already claimed or done: take the next ready one with `python scripts/dev/tasks.py next --lane DSA-NB` and say which.
- T10 runs last. Its playbook part merges the bridge logs of the reports shipped by then and lists the missing ones. It does not wait for them.

## 8. The ten audits

### T01. Data forensics: are the bars the studies read the bars that happened? (card `dsa-audit-01-data-forensics`, lane DSA-NB)

**Why this can find what earlier audits missed.** Earlier audits checked study logic and statistics. None tested the input files themselves, row by row, against invariants. A duplicate week, a microsecond stamp read as milliseconds, or taker volume confused with volume moves every number built on it. No test catches it, because all studies reuse the same few loaders.

**Method.**
1. Inventory every source in section 1d: files, first and last timestamp, rows, unique rows, time unit (ms or microseconds), interval, gaps. Write data_inventory.csv. All dates are allowed here (timestamps and counts only).
2. Bar invariants on DEV 1m klines:
   - OHLC order: low <= open, close <= high;
   - volume >= 0, and 0 <= taker_buy_volume <= volume;
   - quote_volume / volume lies inside [low, high];
   - trades >= 1 when volume > 0;
   - the close[t] to open[t+1] jump distribution (flag > 0.5%);
   - runs of frozen bars (high == low with volume 0).
   Count every violation and list the 20 worst with timestamps.
3. Cross-source checks:
   - DEV 1m resampled to 1d vs Dumps/backtest/raw_1d (each OHLCV field);
   - footprint total volume per minute vs kline volume per minute on 2024-12-02..2025-03-31: ratio distribution and worst days (log the exposure row, rule 5.3);
   - every 8h funding stamp present on DEV; rates beyond +/-0.75% flagged.
4. Loader torture test. Find every kline and funding loader (`git grep -n -E "def load_|read_csv|loadtxt"` under B/ and R/). Feed each a crafted file in %TEMP% with:
   - (a) a microsecond-stamped row;
   - (b) a duplicate row;
   - (c) a missing minute;
   - (d) a header row;
   - (e) an unsorted pair.
   Record raise, warn or silent for each. Leads L4 and L10 are yours.
5. Impact: for each defect, which studies read the affected rows (`git grep` the path or loader), and how many of their DEV events fall on affected bars or days. Recount one published event count with the defect removed.
6. Delta sign. Find every place that builds delta or CVD (`git grep -n taker_buy`, B/layers/fabio/orderflow_bars.py, the screens). Check the convention is the same everywhere (buy minus sell = 2 x taker_buy - volume), with a 3-bar hand example from the raw file.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T01_data_forensics.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T01/`.
**Done when.** T01_data_forensics.md is shipped, with:
- data_inventory.csv;
- invariant counts per source;
- the loader table (each loader x 5 crafted defects);
- the impact recount;
- leads L4 and L10 resolved;
- every S1/S2 finding carded.

### T02. Look-ahead and time: does any signal know the future? (card `dsa-audit-02-lookahead-time`, lane DSA-NB)

**Why this can find what earlier audits missed.** Look-ahead hides in resample labels, centred rolling windows, pivot confirmation and higher-timeframe joins. Reading code finds some of it. A mechanical test finds all of it: a detector that uses only the past gives the same answer at t with the future cut off or replaced by garbage.

**Method.**
1. List every detector or signal function used by a study in section 1b and by the testnet layers (live_runner_cli.build_default_registry): file, function, input bars, timeframe. One row each.
2. Truncation test. Draw 200 random DEV timestamps (fixed seed, printed). Run each detector:
   - on the full DEV data;
   - on the data cut after the last bar CLOSED at t.
   Every signal at or before t must be identical. Any difference is look-ahead: record the bar and the field.
3. Poison test. Replace every bar after t with NaN, then with price x 10. Signals at or before t must not change.
4. Static sweep with `git grep`. Classify each hit as safe or unsafe, with the line:
   - resample( without label/closed;
   - rolling(..., center=True);
   - shift(-;
   - iloc[i+1];
   - find_peaks or argrelextrema;
   - merge_asof direction;
   - higher-timeframe joins keyed on a bar's open time for a bar that closes later.
5. Clocks (lead L6). For each loader and study: is a bar stamped by its open or its close, and how are sessions defined (fixed UTC or DST-aware New York/London)? For each study that uses a session or a clock time, count the DEV events whose session label changes under the other convention.
6. Entry timing. In every study, the entry must be at or after the close of the signal bar (next open or a stated limit). Check entry index vs signal index in code, and on 10 events per study by hand.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T02_lookahead_time.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T02/`.
**Done when.** T02_lookahead_time.md is shipped, with:
- the detector table, each detector PASS/FAIL on truncation and poison;
- the static-sweep table;
- the clock table with changed-label counts;
- the entry-timing check;
- lead L6 resolved;
- S1/S2 carded.

### T03. Planted edges: do the simulators return answers we know? (card `dsa-audit-03-planted-edges`, lane DSA-NB)

**Why this can find what earlier audits missed.** No simulator in this repo has ever been given an input whose right answer is known in advance. Flow audit 6a found this and it was never carded. A harness that returns +0.30% for a planted +0.30% edge, and zero for no edge, can be trusted. One that does not is the bug, whatever its tests say.

**Method.**
1. Harnesses: find the smallest entry point that takes bars and events for each of:
   - bt_engine.simulate_trade;
   - tom_bt.sim_limit_trade;
   - the run_t055 pipeline with trade_costs.net_return;
   - gross_effect_screen screen.py;
   - chart_read_g5 common.py;
   - one opr_* study.py;
   - levels_sizing probe.py;
   - orderflow_views study.py trade().
2. Canary markets built in %TEMP% (seeded random walk, 1m bars, about 30 days each):
   - (a) zero drift;
   - (b) a planted +0.30% move over the hold after each event;
   - (c) the move inside the signal bar (must NOT be captured with next-bar entries);
   - (d) the move one bar after the exit (must not be captured);
   - (e) funding settlements crossed at a known rate, +0.01% and -0.01%, long and short;
   - (f) a gap through the stop (the next open beyond the stop);
   - (g) stop and target both inside one bar;
   - (h) a timeout exit.
3. Expected numbers come from a short formula in your own script, never from the harness code (B/layers/FORMULAS.md where it covers the case). For each harness x canary: expected, got, PASS/FAIL. A harness that cannot take a canary is BLOCKED with the reason.
4. Statistics rebuilt independently for mal_bb A1 and the gross screen T arm:
   - mean;
   - day-clustered SE;
   - t;
   - MDE = 2.8 SE;
   - the DIFF test vs control.
   Compare with the published numbers. Check every pass-bar threshold at its boundary (>= vs >, n exactly 200, t exactly 2.00, DIFF exactly +0.05%) by feeding constructed results to the verdict code.
5. Lead L5 is yours: the timeout fill at the last close, the gap test on the wrong bar, funding=None meaning 0. Show each with a canary.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T03_planted_edges.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T03/`.
**Done when.** T03_planted_edges.md is shipped, with:
- the harness x canary table (expected, got, PASS/FAIL/BLOCKED);
- the independent statistics rebuild vs the published numbers;
- the boundary tests;
- lead L5 resolved;
- the canary scripts under scripts/T03/, re-runnable;
- S1/S2 carded.

### T04. Clean-room twin: rebuild two studies from their spec alone (card `dsa-audit-04-clean-room-twin`, lane DSA-NB)

**Why this can find what earlier audits missed.** Every number so far comes from one implementation per study. A second implementation written from the spec alone shows two things. Where the code does something the spec never said. And where the spec is too loose for two people to code the same way. Neither shows up in a single-implementation audit.

**Method.**
1. Studies: R/mal_bb_mid_engulf_2026-10-16 (arm A1) and R/opr_weekly_low_round_sweep_2026-10-16 (arm RL).
   - Read only each PRE_REG.md and section 1d of this brief.
   - Do NOT open study.py, ledger.csv or test_study.py until step 4.
   - Keep an ambiguity log: each point where the spec allowed more than one reading, and the reading you chose (DECISION (OURS)).
2. Write scripts/T04/twin_<study>.py from the spec only, with your own loader. Run it on DEV. Output an event list: timestamp, side, entry price, exit time, exit price, net return.
3. Diff against the shipped study's ledger.csv, event by event. Classes:
   - matched;
   - twin-only;
   - shipped-only;
   - matched but return differs by more than 0.001 percentage points.
   Give counts per class and 10 examples of each.
4. Now read study.py. Classify each difference as spec ambiguity, shipped bug or twin bug. Fix twin bugs and rerun. What remains is the finding.
5. Measure the arm's mean, t and verdict on three event sets:
   - the shipped events;
   - the twin's events;
   - the corrected set.
   Does any verdict change?
6. Time left: a third twin for R/opr_preopen_tops_2026-10-16 arm H2 (the only positive mean among the 10-16 screens).

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T04_clean_room_twin.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T04/`.
**Done when.** T04_clean_room_twin.md is shipped, with:
- the ambiguity log;
- per-study diff counts by class;
- every difference classified;
- the verdict on shipped, twin and corrected events;
- the twins under scripts/T04/;
- S1/S2 carded. Spec ambiguities go in as S3 findings for PRE_REG_TEMPLATE.md.

### T05. Placebo nulls: what does chance alone produce here? (card `dsa-audit-05-placebo-nulls`, lane DSA-NB)

**Why this can find what earlier audits missed.** The published t-statistics assume independent day clusters, and assume the control is a fair null. A placebo distribution measures the null directly, without trusting any formula. It uses the same study code on fake events matched on clock time, weekday and spacing, so it includes the overlap, the clustering and the grid of arms that were tried.

**Method.**
1. Studies: the gross screen, mal_bb, opr_bb_mtf_center, opr_weekly_low_round_sweep, opr_preopen_tops, and candle_close.
   - Take each arm's DEV events.
   - Draw 1,000 placebo sets of the same size, matched on 15-minute time-of-day slot and weekday, with the same cooldown rule. Seed and print the seed.
   - Compute the same statistic (mean net, t) with the study's own return function.
2. Per arm, report:
   - the empirical p (the real result's rank among the placebos);
   - the placebo SD / published SE ratio (above 1.2 means the published SE is too small);
   - the placebo mean vs the published control.
3. Overlap:
   - per arm, the share of events whose hold overlaps another event's hold;
   - effective n;
   - t from a week-block bootstrap (2,000 draws).
   Lead L7: the 390-minute holds with a 60-minute cooldown.
4. Multiple testing:
   - Count every arm x horizon x variant actually computed per study (trials.csv files, the 126 candle_close arms, the mal_bb grid).
   - Build the best-of-N null: the max statistic over N placebo arms.
   - State the bar a single arm would need, vs the bar used.
   Lead L7: any-arm pass with no correction.
5. Stability: sign and size per DEV half-year (2022H1..2024H1) for each arm with n >= 100.
6. LC1 (lead L8).
   - Rebuild the control as a fair null: random lines with the same distance distribution from midnight, both signs, counted only when touched, exactly like real levels, on the footprint window (exposure row).
   - Recompute the 12 level-family hold rates and the KEEP list.
   - Report which KEEP verdicts survive.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T05_placebo_nulls.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T05/`.
**Done when.** T05_placebo_nulls.md is shipped, with:
- the per-arm table (empirical p, SD ratio, placebo mean, overlap share, effective n, bootstrap t);
- the best-of-N bar per study;
- half-year signs;
- the fair LC1 rerun;
- leads L7 and L8 resolved;
- S1/S2 carded.

### T06. Costs and fills: what would we really have paid and got? (card `dsa-audit-06-cost-fill-realism`, lane DSA-NB)

**Why this can find what earlier audits missed.** Earlier audits each saw one cost set. Nobody has put every cost, slippage, funding and fill rule from all studies side by side, or asked how far each result is from break-even under the costs we would really pay on the venue that would trade it.

**Method.**
1. Cost inventory (lead L3). `git grep` every fee, slippage, spread and funding constant under B/ and R/ (0.0005, 0.0002, 0.0007, 0.001, 0.0012, 0.0014, 0.002, bp, fee, slip, cost, funding). For each, record:
   - file:line and value;
   - per side or round trip;
   - maker or taker;
   - what it is applied to;
   - whether it imports B/fees.py.
   Write costs.csv.
2. Venue. The testnet trades Deribit, but the backtests use Binance USD-M data. Per study, which venue's fees it charges vs which would trade it. Use B/fees.py values, cited.
3. Funding (lead L1).
   - Confirm the path miss.
   - Rerun the gross screen and the four chart-read G5 screens on DEV with real 8h funding from Dumps/backtest/raw/fundingRate, signed per side (longs pay positive rates, shorts receive them).
   - Report the change in mean net per arm, and any verdict change.
4. Fill rules, as an engine x rule table:
   - entry at the next open vs the signal close;
   - stop and target in the same bar (which wins; is it the conservative one?);
   - a gap through the stop (stop price vs open);
   - limit fills (touch vs through; gap G4 is known, only say where it still applies);
   - the timeout exit price;
   - partial fills.
   N2 (orderflow_views gap stop) is known: only confirm whether it is still unfixed.
5. Break-even:
   - for every arm in section 1b with a mean, the round-trip cost at which mean net = 0, vs the cost charged;
   - for the best arm, the slippage that turns it negative.
6. Stop-based testnet layers. For each layer in auto_trader_config.json (size_usd, max_loss_usd, max_fee_to_stop), the fee as a share of the stop distance at its size. This extends Fable E3 (Tom/Fabio only) to every other layer.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T06_cost_fill_realism.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T06/`.
**Done when.** T06_cost_fill_realism.md is shipped, with:
- costs.csv;
- the venue table;
- the real-funding rerun with per-arm changes;
- the engine x fill-rule table;
- break-even per arm;
- fee-to-stop per testnet layer;
- leads L1 and L3 resolved;
- S1/S2 carded.

### T07. Stale verdicts: do the published numbers still come out of today's code? (card `dsa-audit-07-stale-verdicts`, lane DSA-NB)

**Why this can find what earlier audits missed.** A verdict is a claim about code at one commit. A later change to a shared loader, a cost constant or a fixed bug silently makes old verdicts stale, and no one reruns them. Rerunning and diffing every number is the only way to know the published table still holds.

**Method.**
1. Provenance. For each verdict in section 1b, and the testnet source verdicts (the reasons in auto_trader_config.json):
   - the publishing commit (`git log --format="%h %ad %s" -- <result file>`);
   - every later commit that changed the study script or any repo file it imports (static import walk).
   A verdict whose inputs changed after it was written is STALE-CANDIDATE.
2. Rerun on DEV, into scripts/T07/out/, never over result files:
   - the six newest studies (five G5 screens and wlow_bounce);
   - the four STALE-CANDIDATEs with the most changed lines.
   Diff every published number (n, mean, SE, t, verdict) with tolerance 0 for counts and 1e-6 for returns. Write rerun_diff.csv.
3. Determinism:
   - run one study twice;
   - `git grep` random draws with no seed, set or dict iteration that feeds an order, and time.now() inside a study.
4. CI (lead L9):
   - Python, pandas and numpy versions on JIS-NB vs what CI installs;
   - which study tests import pandas;
   - which tracked tests are in no gate list (scripts/dev/run_extra_tests.py EXTRA, MyTradingSys/tests/test_gate_discovery_b150.py).
5. Doc drift. Numbers in S/LAYERS.md, S/layer_map.json, the Research Map DATA block (S/artifacts/research_map.html) and research/STATUS.md vs the result files. List each mismatch with both values.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T07_stale_verdicts.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T07/`.
**Done when.** T07_stale_verdicts.md is shipped, with:
- the provenance table with STALE-CANDIDATEs;
- rerun_diff.csv for ten results;
- the determinism result;
- the CI table;
- the doc-drift list;
- lead L9 resolved;
- S1/S2 carded.

### T08. Split integrity and hidden trials: how much out-of-sample is really left? (card `dsa-audit-08-split-trials`, lane DSA-NB)

**Why this can find what earlier audits missed.** The split is enforced only by each script refusing dates. A floating 70/30 cut, a calendar-year split, or one study tuning on another study's VALIDATION leaks out-of-sample data in a way no single study can see. Every variant tried but not logged makes the survivor look stronger than it is.

**Method.**
1. Static map. `git grep` every date filter and split constant under B/ and R/ (2024-07-01, 2025-07-01, 2026-06-26, is_frac, train, test, DEV, HOLDOUT, Timestamp("20, datetime(20). Table: file:line, scheme, windows.
2. Dynamic. For each study with a published verdict, log the min and max timestamp of the data its loader actually returns per phase. Wrap the loader in a copy; do not edit the study.
   Lead L2: for each 70/30 runner, where the out-of-sample part starts given the data it loads today, and given the data present when its result was committed (`git log` of the result file).
3. Contamination calendar:
   - month x study, marking which windows each study has read with returns;
   - each overlap of a tuning or DEV window with main VALIDATION or HOLDOUT;
   - whether EXPOSURE_LEDGER.csv has every footprint-window read.
4. HOLDOUT seal. List every committed file under R/ that holds timestamps >= 2025-07-01 together with return or P&L columns. Read dates and column names only, never values. Each one is a seal-breach candidate, with its commit and author line.
5. True trial count:
   - per study, from `git log -p` of its PRE_REG, params and trials files, count the variants actually computed;
   - compare with R/TRIAL_LEDGER.csv (8 rows) and the study's own trials file;
   - give the haircut bar sqrt(2 ln N) with the true N vs the t used.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T08_split_trials.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T08/`.
**Done when.** T08_split_trials.md is shipped, with:
- the split map;
- the dynamic window table;
- the contamination calendar;
- the seal-breach candidate list;
- the true-N table with haircut bars;
- lead L2 resolved;
- S1/S2 carded.

### T09. Backtest-to-live parity: do testnet layers trade what was tested? (card `dsa-audit-09-live-parity`, lane DSA-NB)

**Why this can find what earlier audits missed.** Backtests and testnet run different code for the same layer. If the live layer fires on a different bar, enters at a different price or exits by a different rule, the backtest verdict says nothing about the trades. The testnet's 97% time exits and profit factor 0.38 make this urgent. No tool compares them: parity.py compares a verdict with the live log, not the code.

**Method.**
1. Map. For each account in auto_trader_config.json, build a table:
   - the layer (turn_of_candle, rsi_events 5m/15m/1h, malkan bull/bear, session, positioning, fabio x4, cryptocred x4, tom, plus wlow_bounce and fabio_v3 from live_runner_cli);
   - the live function (build_default_registry);
   - the backtest function that produced its verdict;
   - the parameters on each side, with every difference.
2. Deployed code, read-only:
   - `git -C C:/Users/E-ngineers/IdeaProjects/BinanceDataFeed rev-parse HEAD`;
   - `git diff <that sha> origin/fast-track --stat -- MyTradingSys/backtest/layers MyTradingSys/execution`.
   The replay must match what runs. Name the sha you replay.
3. Replay in your worktree.
   - Call poll_once (or each layer function) with a fake fetch_fn that serves DEV closed bars from the kline files, bar by bar, for 30 fixed DEV days (printed; a mix of trend, range and high-volatility days).
   - Patch default_fetch_klines, _wlow_default_fetch, _wlow_default_oi and any funding fetch to raise, so no network call can happen.
   - Point every state or log path at %TEMP%.
   - Record each signal: layer, bar time, side, price.
4. Run each layer's backtest function on the same 30 days. Diff signal by signal:
   - same bar;
   - off by one bar;
   - live-only;
   - backtest-only.
   Give counts per layer and 5 examples each.
5. Exits. Compare the exit rules the testnet applies with each layer's backtest exits (stop, target, hold, time exit):
   - auto_trader.py and position_manager.py;
   - the config's max_hold_minutes, max_age_bars, max_loss_usd, max_fee_to_stop.
   Explain the 97% time exits from the rules, with numbers.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T09_live_parity.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T09/`.
**Done when.** T09_live_parity.md is shipped, with:
- the layer map with parameter diffs;
- the deployed sha;
- the signal diff per layer on 30 DEV days;
- the exit-rule diff;
- the time-exit explanation.
Live-path findings go to the desk --target CLAUDE; the others are carded.

### T10. Missing aspects: the failure modes nobody here has checked, and the bridge playbook (card `dsa-audit-10-missing-aspects`, lane DSA-NB)

**Why this can find what earlier audits missed.** The other nine audits test what we already suspect. This one asks what we never thought of. The model lists the ways crypto backtests fail from its own knowledge and from published work (Search on for this card only), then checks each one against each study. It also turns the bridge logs of all the audits into a playbook for the next DSA chats.

**Method.**
1. The list. Write at least 30 distinct ways an intraday crypto-perpetual backtest can mislead. Cover:
   - data;
   - time;
   - costs and fills;
   - statistics;
   - regime and market structure (listing, halving, ETF flows, exchange outages, liquidation cascades);
   - selection;
   - implementation;
   - operations.
   For each: one line, how it shows, one test. Use web search for recent published lists of backtest pitfalls and cite the URL for each item taken from one. Mark items already covered by section 2 or by T01-T09, and say by which.
2. Matrix. Each failure mode x each study in section 1b and each testnet layer: HANDLED (file:line), NOT HANDLED, N/A or UNKNOWN. Write matrix.csv; summarise by row and by column.
3. Demonstrate the 5 worst NOT HANDLED cells. For each, a small script that shows the effect on DEV as a number (e.g. the result with and without the effect), not an argument.
4. Bridge playbook:
   - Read the bridge-log section of every T report shipped so far, and list the ones missing.
   - Merge them into BRIDGE_PLAYBOOK.md:
     - the call patterns that saved the most replies;
     - each failure mode with its recovery and the result that proved it;
     - 10 rules for the next DSA audit chat.
   - A rule that belongs in DSA_SESSION_PROMPT.md is proposed with `desk.py post ... --target CLAUDE`, not edited.

**Output.** `MyTradingSys/research/dsa_backtest_audit_2026-10-16/T10_missing_aspects.md` plus scripts under `MyTradingSys/research/dsa_backtest_audit_2026-10-16/scripts/T10/`.
**Done when.** T10_missing_aspects.md is shipped, with:
- the 30+ failure-mode list with sources;
- matrix.csv and its summaries;
- 5 demonstrations with numbers;
- BRIDGE_PLAYBOOK.md;
- S1/S2 carded and prompt changes posted to Claude.
