# CryptoCred 4h/1d count and power (card cryptocred-htf-count-power)

Count only: no exits, no P&L, no VALIDATION/HOLDOUT read. Hypothesis check, no recall claim (LEDGER_FEASIBILITY.md: 0 dated calls, layer stays a hypothesis; PRE_REG_TEMPLATE.md:14).

## Method
- DEV window: 2022-01-01 .. 2024-06-30 (30 months, repo split; bars cut at 2024-07-01 before any signal is computed; 1313280 1m bars from raw_1m_2022). OURS: window choice follows the repo split, not the trader.
- Signals: `run_cc_setups.SETUPS` with current defaults on same-timeframe closes (1m resampled to 1h/4h/1d via tf_resample). 1h is the reference; its count equals the runner's `n_signals` (test_cc_htf_count.py). No tuning, no grid (trial count 0 new).
- Fills (the "1h entry" stand-in): setups 1/2 are resting limits at the level; a fill is counted when a later 1m bar trades through the level by one tick inside the validity window (`find_limit_fill`, BACKTEST_PROTOCOL rule). Setup 3 enters at the signal-bar close, so fills = signals. No separate 1h-bar entry trigger was built: entry stays the level/close, and the fill is checked on 1m, which is stricter than 1h.
- Power: `power_mde.power_mde(p, rr, cost_r, n)` with n = fills, rr = setup target_r (1.5, 1.5, 2.0). cost_r = 2 x Deribit taker 0.0005 / median risk% (all_taker, conservative, from fees.py). Claimed win rate = breakeven p + 0.05 (OURS, a stated-in-advance edge of 5 points; not the trader's). Two-sided 95% CI lower bound > 0 test; MDE is the detectable mean net R at N.
- Rule: N < 100 is written INCONCLUSIVE in advance; additionally N below the N-for-80%-power is INCONCLUSIVE for the claimed edge.

## Results (DEV, 30 months)
| tf | setup | signals | fills | fills/month | median risk % | cost R (all_taker) | breakeven p | power at p+0.05 | MDE net R | N for 80% | status |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1h | setup1_sr_flip | 831 | 801 | 26.70 | 0.10 | 1.00 | 0.800 | 0.98 | 0.088 | 400 | powered |
| 1h | setup2_fib_pullback | 750 | 750 | 25.00 | 0.20 | 0.51 | 0.605 | 0.82 | 0.122 | 710 | powered |
| 1h | setup3_failed_msb_reversal | 100 | 100 | 3.33 | 1.34 | 0.07 | 0.358 | 0.17 | 0.413 | 758 | INCONCLUSIVE (N < N-for-80%) |
| 4h | setup1_sr_flip | 217 | 207 | 6.90 | 0.10 | 1.00 | 0.800 | 0.52 | 0.174 | 400 | INCONCLUSIVE (N < N-for-80%) |
| 4h | setup2_fib_pullback | 200 | 200 | 6.67 | 0.32 | 0.31 | 0.524 | 0.30 | 0.245 | 768 | INCONCLUSIVE (N < N-for-80%) |
| 4h | setup3_failed_msb_reversal | 22 | 22 | 0.73 | 2.82 | 0.04 | 0.345 | 0.08 | 0.876 | 750 | INCONCLUSIVE (N<100) |
| 1d | setup1_sr_flip | 33 | 31 | 1.03 | 0.10 | 1.00 | 0.800 | 0.12 | 0.449 | 400 | INCONCLUSIVE (N<100) |
| 1d | setup2_fib_pullback | 30 | 30 | 1.00 | 0.80 | 0.13 | 0.450 | 0.09 | 0.639 | 785 | INCONCLUSIVE (N<100) |
| 1d | setup3_failed_msb_reversal | 1 | 1 | 0.03 | 17.18 | 0.01 | 0.335 | 0.05 | 4.090 | 744 | INCONCLUSIVE (N<100) |

Source numbers: count_power.json (same folder), produced by `cc_htf_count.py --data-root <raw_1m_2022>`.

## Reading
- 1d: every setup has N <= 31 fills (about 1 per month): INCONCLUSIVE in advance; MDE 0.45 to 4.1 R. A 1d test cannot be run on this window.
- 4h: setups 1 and 2 have 207 and 200 fills (about 7/month), above the N>=100 floor but under N-for-80% (400 and 768); power at +5 points is 0.52 and 0.30. Setup 3 has 22 fills: INCONCLUSIVE. 4h can only detect large effects (MDE 0.17 R and 0.24 R net).
- 1h reference: 801, 750 and 100 fills; setups 1 and 2 exceed their N-for-80% (400 and 710), so 1h is the only powered timeframe; setup 3 (100 fills, 0.17 power) is not.
- Setup 1 cost trap: stop is a fixed 0.1% beyond the level, so median risk is 0.10% and fees alone cost 1.0 R round trip at taker rates; breakeven win rate is 0.80 at 1.5 R. At 4h and 1d the same 0.1% buffer applies, so the structure width does not help. This is a property of the encoded stop (`stop_buffer_pct`), not of the trader's timeframe; widening it is a tuning change and out of scope here (it would be a new trial).
- Pooling 4h setups 1+2 (about 407 fills) would reach the N for setup 1 but they are overlapping signals from one structure, so they are not independent trials; do not pool without a de-duplication rule in the PRE_REG.
- Caveat on swings: `find_swings` defaults to body highs/lows with strict inequality, so a bar whose open equals the previous close ties and is rejected; on gapless synthetic data it finds zero swings (found while building the fixture). Real Binance data has small open gaps, which is why counts above are non-zero, but the swing count is sensitive to that tie rule. Reported, not changed.

## Random-entry null spec (for the later PRE_REG, not run here)
Per setup and timeframe, same data window, same code path as the real run:
1. For each real signal draw one random entry time on that timeframe's bars inside DEV, uniformly, excluding bars within the validity window of another drawn entry for the same side (non-overlapping), side drawn to keep the real long/short ratio.
2. Entry price = that bar's close (setup 3 style) or a level set to the real signal's distance from the close (setups 1/2: same limit offset in R and same validity window), so fill rate matches the real fill rate (match unfilled share, not just N).
3. Same stop distance in % as the real signal it replaces (median-matched risk), same target_r, same exits, same max_bars=1440 timeout, same fees (all_taker and maker_entry variants), same funding.
4. 1000 resamples; null = distribution of mean net R at the real N. Real result must exceed the null 95th percentile AND the CI lower bound > 0 (power_mde test). Seed fixed in the PRE_REG; the draw count is a trial in TRIALS.
5. Report null mean (should sit near -cost_r x (1-p) minus fees, a sanity check on the cost model) and the real/null gap in R.

VERDICT: INCONCLUSIVE in advance for 1d (all setups) and 4h setup 3; 4h setups 1 and 2 underpowered for a +5 point edge (under N-for-80%). No P&L was computed.
