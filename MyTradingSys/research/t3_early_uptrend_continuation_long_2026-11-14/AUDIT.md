# AUDIT: T3 early-uptrend continuation long (adversarial look-ahead, fee, stats and test audit, before VAL)

Auditor: third agent, 2026-11-14. Read: PRE_REG.md, t3_study.py, fetch.py, test_t3_study.py. VAL was NOT opened (no `--unlock-val` run; independent checks used DEV trades and raw klines only).
Verdict: no look-ahead, no fee error, and no blocker found. Two MAJOR items (cheap to fix) should be fixed before VAL is opened; six minor items follow.

## Independent checks that PASSED (evidence)
- 60 random DEV RIDE trades recomputed from raw klines with a separate script (ATR14 SMA, S = max(2.5 ATR, 2%), entry = next open, stop gap fill at the worse of stop and open, prior-10-day-low signal exit at next open, day-60 close): 0 mismatches (entry_px, S, stop, exit_px, exit_reason).
- Cell A signal state on all 248 DEV RIDE A trades recomputed with an independent Wilder ADX/DI and a prior-30-day volume median (bars <= signal bar): 0 mismatches, and every one is a true onset (previous bar false).
- BTC phase label recomputed independently from closes <= D-1 for all 1509 DEV trades: 0 mismatches.
- Accounting identities on dev_trades.csv: gross_R = (exit-entry)/S exactly; (gross_R - net_R) x S/entry = 12 bp + funding to 1e-14; min gross_R = -1.0 (no sub -1R fills, plausible on 24/7 spot opens).
- Costs: `COST12 = 2*fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13` = 0.0012, imported (fees.py lines 38, 62), applied once per trade in `_rows` and `pool_for`; `MyTradingSys/backtest/test_no_own_costs.py` passes; only `FLAT_FUND_DAY = 3*0.0001` is typed (the PRE_REG flat funding assumption, not a fee). 6 bp is only `net_R6` / `mean_net_R6`, never in `verdict()`.
- Funding sign: `fund = cf[xi+1] - cf[e]` is the sum of prints over the hold, subtracted from the long's return (positive rate = long pays, negative = long receives). Flat fallback counted per trade (`fund_fallback` = `fund_flat`, `flat_fund_n`).
- R denominator = S/entry (`risk`), used for gross, net and the random pool.
- Tie/gap: stop checked first (stop wins ties), gap-open fills at the open; CAP3R target fills at the target; unresolved-at-end trades have xi = -1 and are dropped before the overlap rule.
- Weekly VWAP anchor: `(day+3)//7` increments on Mondays (1970-01-01 is Thursday): correct, cumulative per week, includes the signal bar only.
- DEV-only mode: bars loaded only to DEV_END + 62 days (2024-03-03); `window_mask`, `pool_for`, `basket_daily` all cut at entry day <= 2023-12-31; `assert_dev_clean` guards the output; `--window val/all` refuses without `--unlock-val`. DEV trades that enter in Dec 2023 see up to 60 days of 2024 prices (stated in PRE_REG).
- Bars 1-8 in `verdict()` match the PRE_REG text (see M-list below for the one wording gap).
- ex_best (drop the 5 highest, ascending sort) correct; BH step-up with reverse cumulative min correct; bootstrap resamples whole weeks (bincount of sums and counts), ISO-week key `(day+3)//7`.
- `pytest test_t3_study.py`: 6 passed. Test file reads no cache and imports nothing from scripts/sched (grep clean; it overrides BRAIN_CSV).

## Findings, ranked

### MAJOR (VAL must not be opened until fixed)

**M1. Trades open when a coin's data ends early are silently dropped (favourable survivorship), t3_study.py:296-334, 448, 475 and 659-667.**
The rule "unresolved by the last closed bar is dropped" is applied per segment end, not only at 2026-11-13. Coins whose archive ends inside the VAL window: WAVES and OMG (2024-06-17), OCEAN (2024-07-01), MATIC (2024-09-10), FTM (2025-01-13), EOS (2025-05-26), MKR (2025-09-15), plus XMR (2024-02-20), FTT#1 (2022-11-15) and LUNA#1 (May 2022). A signal fired in the last 60 days before a delisting or wind-down that has not resolved is removed from the signal set and from the random pool, so the crash-to-delist loss never enters the mean. That is exactly the tail that hurts a long. PRE_REG says only that survivorship is a stated limit; it does not cover dropping open trades at a coin's own last bar.
Fix: for any segment whose last bar is before 2026-11-13, force-exit still-open positions at the last bar's close (reason `DELIST`, counted in RESULT), applied identically to signals, random pool and CAP3R; report the number of such trades per window. Do the same for the DEV run for symmetry. Keep dropping only at the global end date (as frozen). If the lead prefers not to change the simulator, minimum: report the count of signal-bar entries dropped at each segment end, for VAL and DEV, next to the verdict.

**M2. Tests do not pin the look-ahead-critical timing, and cell B has no test, test_t3_study.py (flat_bars at line 59, sig_override at 156 and 196).**
I applied 22 one-line mutants to a copy of t3_study.py and ran test_t3_study.py. The six named mutants in the docstring are caught (reproduced: lookahead, stop tie, gap fill, funding sign, cost, planted sign, greedy). These SURVIVED (6 passed):
 - `e = sig` (entry at the signal bar's open instead of next open): flat_bars sets open = close = 100, so entry timing is invisible. This is the single most important look-ahead and nothing guards it.
 - RIDE signal exit filled at the signal bar's close instead of the next open (`fill[sg] = cj[sg]`).
 - RIDE time exit 59 days instead of 60 (`HOLD`).
 - Weekly VWAP anchor off by one day (`(day+4)//7`).
 - Hilega Milega rule `|` instead of `&` (WMA21 below BOTH lines); VWAP leg removed from cell B; ADX DI+ > DI- leg removed from cell A (cell B is only ever fed zero signals).
 - 250-bar warm-up removed (`idx >= 0`); basket label shifted one day; DEV window widened by 100 days; BH multiplier broken (`q = p*m`); `ex_best` dropping the worst 5 instead of the best 5; volume median including the current bar.
Fix (tests only, synthetic data): (a) a test with o != c where the entry price must equal open[s+1] and not close[s]/open[s]; (b) RIDE signal-exit test (close below prior-10-day low on bar j, exit price = open[j+1], bar j+1 low irrelevant); (c) time-exit test (exit at the close of day 60 and day 30 for CAP3R, i.e. xi = e+59 / e+29); (d) a cell B test built from a hand-computed RSI9/EMA3/WMA21 series and a two-week VWAP with a Monday reset (hand number) and an A test that DI- > DI+ blocks; (e) `bh_q([0.01, 0.04]) == [0.02, 0.04]`, `ex_best` on a known vector, `week_boot` on two weeks; (f) DEV mode: world with bars extending past 2024 gives identical DEV rows to a world truncated at DEV_END+62d. Then re-run the mutant list (script in the scratchpad of this audit: `scratchpad/mut.py`; the lead can re-create it from the table above) and require every mutant to be caught.

### MINOR (fix or state in RESULT; none blocks VAL on its own)

**m1. Lint false positives (not edited, per instruction).** `python scripts/dev/lookahead_lint.py --new` (the tool takes no path; the study's hits are listed in the global output) flags t3_study.py:90, 104, 116, 118, 142, 146, 148 (indicator output index alignment: writes `out[i+1]`, no future bar read), 259 (the deliberate `STUDY_BUG` centred median, a test hook), 375-376 (percentile of the bootstrap distribution, not of market data), 430-431 and 476 (`cf[xi+1]`, outcome-label funding window of an already-fired signal), and test_t3_study.py:75, 97, 129, 150 (synthetic-data construction). All are false positives: reasons for the allowlist rows: index-alignment writes in recursive indicator, test hook behind env flag, bootstrap percentile, outcome-window label, synthetic data builder. Lead to add the rows with reviewed reasons; better, move the deliberate bug at t3_study.py:258-260 out of production code (see m2).

**m2. `STUDY_BUG` hook lives in production code, t3_study.py:25, 258-260, 181.** An exported `STUDY_BUG=1` in the shell would silently run a look-ahead VAL; `meta.study_bug` records it but nothing refuses. Fix: in `main()` refuse (exit 2) when `BUG` is true and `--unlock-val` is given, or drop the hook and have the test patch `coin_features`.

**m3. PRE_REG vs data: no 2017 UP_E days.** PRE_REG line 15 lists DEV UP_E days "2017-09..2017-12". BTC data starts 2017-08-17, so SMA200 first exists around 2018-03 and that epoch has no label; dev_summary shows 415 UP_E calendar days, all in 2020-05..2021-11 (the coin 250-bar warm-up would exclude 2017 anyway). DEV therefore is one episode. State in RESULT; bar 7 is a sign check on a single bull run.

**m4. Weekly-cluster CI is anti-conservative for 60-day holds.** Spec-compliant (clusters = entry ISO week), but RIDE trades last up to 60 days, so adjacent weekly clusters share the same market path and are dependent. Bars 3 and 4 (CI low, BH q) lean on that CI. Suggested (non-verdict) sensitivity row: month-block bootstrap or clusters of 8 weeks; report next to the verdict, do not change the frozen bars.

**m5. Verdict label gap vs PRE_REG, t3_study.py:636-637.** PRE_REG: "FAIL = any of 2-8 breached with n >= 30"; code returns FAIL only for bars 2-7 and `SINGLE-EPISODE (bars 1-7 met)` for bar 8 or the ONE-YEAR flag. Bar 8's own text ("otherwise a pass is labelled single-episode and cannot count as PASS") supports the code; the two sentences conflict. Either way it cannot be a PASS. State the reading in RESULT.

**m6. Funding timestamp convention vs test.** Real prints carry millisecond offsets (e.g. 00:00:00.001, LUNA/MATIC files), and `searchsorted(side="right")` puts a 00:00 print into the interval after the boundary, i.e. the print at the entry open is paid and the one at the exit open is not; the test uses exact 8 h timestamps (boundary print counted in the interval ending there). Effect is one print (about 1 bp, about 0.001-0.002 R), symmetric across trades; the stop/target day also charges the whole exit day (conservative). Add a ms-offset print to the funding test so both conventions are pinned. Also the random baseline marks occupied `[signal i, xi]` while signal trades allow a new signal on bar xi, so random draws are marginally more restricted (negligible).

**m7. CI collision risk for the test file.** `test_t3_study.py` + `import study` collides by name with `mal_bb_mid_engulf_2026-10-16/test_t3_study.py`+t3_study.py and `multi_tf_bias_2026-10-18/test_t3_study.py`+t3_study.py if the three are collected in one pytest session (sys.modules cache), and run_all_tests.py runs research tests only from an explicit list. Rename to `test_t3_study.py` importing a uniquely named module (e.g. `t3_study.py`), and register it in the list the lead uses for research tests. Also `random_baseline` returns `mean([])` = NaN with a warning if the pool is exhausted before n draws; guard it.

## What I could not verify
Funding coverage of the nkp1 copies in 2025-26 (flat days are counted per trade, not per day; RESULT should give the flat share). Survivorship from the hindsight candidate list remains a stated limit.

Files: F:/MTS/wt/t3-early-uptrend-continuation/MyTradingSys/research/t3_early_uptrend_continuation_long_2026-11-14/t3_study.py, test_t3_study.py, fetch.py, PRE_REG.md (unedited).
