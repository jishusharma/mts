# CC SETUPS RERUN, limit-fill model, 2026-10-07 (trade-through rerun appended 2026-10-09 at the end)

Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Replaces the b3dbe74 numbers (CC_SETUPS_RERUN_2026-10-06.md) for the verdict.
Run: research worktree C:/Users/E-ngineers/IdeaProjects/mts-research at 5334975 (origin/claude/project-thread-7gvyfy merged, runner has the resting-limit fill, 37e34ba), 1h, defaults only, data from this repo Dumps/backtest (raw_1m_2022 + raw). Raw output: BinanceDataFeed_backups/cc_rerun_2026-10-07/ (json + md).

## Verdict change
| setup | b3dbe74 maker_entry | this run maker_entry | this run all_taker |
|---|---|---|---|
| setup1_sr_flip | PASS (hit 0.84) | FAIL (hit 0.373, OOS net -0.0382%) | FAIL |
| setup2_fib_pullback | PASS (+0.1687% OOS, Sharpe 0.481) | FAIL (OOS +0.0331%, Sharpe 0.091, 1 positive year) | FAIL |
| setup3_failed_msb_reversal | FAIL | FAIL | FAIL |

The earlier PASS on setups 1 and 2 was the post-close fill bias, confirmed: with a limit that has to be touched after placement, setup 1's hit rate falls from 0.84 to 0.373 and 50 of 1527 limits go unfilled. UNVERIFIED mark removed; the result is FAIL for all three.

## Open observations (not resolved, named)
- setup2 OOS shows mean net R -0.7079 (maker_entry) / -1.8558 (all_taker) next to a positive mean net %. R divides by a very small risk (stops ~0.1% wide), so R-means are tail-dominated; the percent column is the stable one. Not investigated.
- setup2 reports 0 unfilled limits out of 508 signals; check whether its entry can be filled by construction before relying on that count.
- All stops and the 1.5R target are NO-SOURCE (B143); this verdict is about unsourced values and selects nothing.

## Run output
### Raw report

tf 1h; bars 41520 (IS 29063 / OOS 12457); funding: included (7305 records).
Fees (fees.py): all_taker = Deribit taker on every leg incl. targets; maker_entry = maker entry+targets, taker stop/timeout. Defaults only, no grid: PBO N/A, not part of the verdict.
Verdict rule: OOS n>=30, OOS net mean>0, net Sharpe>=0.3, same IS/OOS sign, >=2 positive OOS years.

## setup1_sr_flip / all_taker: **FAIL**

signals 1527, trades 1477, unfilled limits 50; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 1056 | -1.0668 | -0.1067% | 0.373 | -0.882 |
| OOS | 421 | -1.0683 | -0.1068% | 0.373 | -0.883 |

OOS per year: 2025: n=207 - (-0.1022%), 2026: n=214 - (-0.1113%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.1068%, n=421.

## setup1_sr_flip / maker_entry: **FAIL**

signals 1527, trades 1477, unfilled limits 50; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 1056 | -0.3802 | -0.0380% | 0.373 | -0.262 |
| OOS | 421 | -0.3819 | -0.0382% | 0.373 | -0.263 |

OOS per year: 2025: n=207 - (-0.0327%), 2026: n=214 - (-0.0435%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.0381%, n=421.

## setup2_fib_pullback / all_taker: **FAIL**

signals 508, trades 508, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 372 | -0.3363 | -0.0659% | 0.414 | -0.167 |
| OOS | 136 | -1.8558 | -0.0383% | 0.434 | -0.112 |

OOS per year: 2025: n=65 - (-0.0964%), 2026: n=71 + (0.0149%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.0380%, n=136.

## setup2_fib_pullback / maker_entry: **FAIL**

signals 508, trades 508, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 372 | 0.0167 | 0.0049% | 0.414 | 0.012 |
| OOS | 136 | -0.7079 | 0.0331% | 0.434 | 0.091 |

OOS per year: 2025: n=65 - (-0.0302%), 2026: n=71 + (0.0910%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net 0.0334%, n=136.

## setup3_failed_msb_reversal / all_taker: **FAIL**

signals 167, trades 167, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 119 | -0.0431 | 0.1595% | 0.403 | 0.079 |
| OOS | 48 | -0.2514 | -0.2976% | 0.333 | -0.193 |

OOS per year: 2025: n=19 - (-0.6676%), 2026: n=29 - (-0.0553%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | FAIL |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.2945%, n=48.

## setup3_failed_msb_reversal / maker_entry: **FAIL**

signals 167, trades 167, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 119 | 0.0431 | 0.2201% | 0.420 | 0.109 |
| OOS | 48 | -0.1745 | -0.2403% | 0.333 | -0.155 |

OOS per year: 2025: n=19 - (-0.6150%), 2026: n=29 + (0.0052%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | FAIL |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.2372%, n=48.



---

# Rerun 2026-10-09: trade-through by 1 tick (B151 partial fix, origin 05cee8e)

Session: MTS-2026-10-09 JIS-NB. Run: worktree mts-cc at origin/fast-track 8b5522b (find_limit_fill needs a trade-through by TICK=0.1; open_at_end counted). 1h, defaults only, 1m klines from the JIS-NB Dumps/backtest (raw_1m_2022 + raw), 2,507,040 1m bars, funding included.
Note: the data window is 264 hours longer than the 10-07 run (41784 vs 41520 1h bars: IS 29248 / OOS 12536), so the numbers are not a pure like-for-like on the fill rule.

## Verdict: the earlier PASS verdicts do not survive, and nothing flips
The PASS for S/R flip and fib pullback (b3dbe74 numbers) was already withdrawn by the 10-07 touch-fill run. The trade-through rerun keeps all three setups at FAIL, on both fee variants.

| setup | fee variant | OOS n | OOS net % | net Sharpe | positive OOS years | verdict |
|---|---|---|---|---|---|---|
| setup1_sr_flip | maker_entry | 423 | -0.0380% | -0.262 | 0 of 2 | FAIL |
| setup1_sr_flip | all_taker | 423 | -0.1067% | -0.881 | 0 of 2 | FAIL |
| setup2_fib_pullback | maker_entry | 143 | +0.0416% | 0.106 | 1 of 2 | FAIL (Sharpe, years) |
| setup2_fib_pullback | all_taker | 143 | -0.0298% | -0.080 | 1 of 2 | FAIL |
| setup3_failed_msb_reversal | maker_entry | 48 | -0.2403% | -0.155 | 1 of 2 | FAIL |
| setup3_failed_msb_reversal | all_taker | 48 | -0.2976% | -0.193 | 0 of 2 | FAIL |

## What changed versus the touch-fill run
- setup1: 1536 signals, 1486 trades, 50 unfilled (10-07: 1527 / 1477 / 50). Hit 0.372/0.374 (was 0.373). Trade-through by one tick moved the result by well under 0.01 percentage points: the fill rule is not what separates this setup from an edge, its stop/target geometry loses after fees either way.
- setup2: 516 trades, 0 unfilled (10-07: 508 / 0). OOS maker_entry +0.0416% (was +0.0331%), Sharpe 0.106 (was 0.091), still one positive year of two. Still reports zero unfilled limits: that is the B151 gap (a), a bar that blows through the zone makes no signal, so the zero is by construction and the setup2 numbers remain an upper bound.
- setup3: identical to 10-07 (it enters at the signal close, no limit).
- open_at_end: the runner counts it in stats, but the report/json do not print the count, so it is NOT_IN_DATA here (follow-up: surface it in the report).

Conclusion: S/R flip is a clear fail; fib pullback is a marginal positive in the percent column on maker fees only and fails the Sharpe >= 0.3 and 2-positive-year gates; nothing here is evidence for a CryptoCred edge. All stops and the 1.5R target remain NO-SOURCE (B143), so this verdict selects nothing.

## Raw output of this rerun
# CryptoCred setups - net-of-fees backtest

tf 1h; bars 41784 (IS 29248 / OOS 12536); funding: included (7305 records).
Fees (fees.py): all_taker = Deribit taker on every leg incl. targets; maker_entry = maker entry+targets, taker stop/timeout. Defaults only, no grid: PBO N/A, not part of the verdict.
Verdict rule: OOS n>=30, OOS net mean>0, net Sharpe>=0.3, same IS/OOS sign, >=2 positive OOS years.

## setup1_sr_flip / all_taker: **FAIL**

signals 1536, trades 1486, unfilled limits 50; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 1063 | -1.0707 | -0.1071% | 0.372 | -0.886 |
| OOS | 423 | -1.0666 | -0.1067% | 0.374 | -0.881 |

OOS per year: 2025: n=200 - (-0.1025%), 2026: n=223 - (-0.1104%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.1066%, n=423.

## setup1_sr_flip / maker_entry: **FAIL**

signals 1536, trades 1486, unfilled limits 50; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 1063 | -0.3849 | -0.0385% | 0.372 | -0.265 |
| OOS | 423 | -0.3799 | -0.0380% | 0.374 | -0.262 |

OOS per year: 2025: n=200 - (-0.0330%), 2026: n=223 - (-0.0424%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.0379%, n=423.

## setup2_fib_pullback / all_taker: **FAIL**

signals 516, trades 516, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 373 | -0.3465 | -0.0671% | 0.410 | -0.171 |
| OOS | 143 | -1.7832 | -0.0298% | 0.434 | -0.080 |

OOS per year: 2025: n=64 - (-0.0940%), 2026: n=79 + (0.0221%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.0295%, n=143.

## setup2_fib_pullback / maker_entry: **FAIL**

signals 516, trades 516, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 373 | 0.0051 | 0.0035% | 0.410 | 0.008 |
| OOS | 143 | -0.6767 | 0.0416% | 0.434 | 0.106 |

OOS per year: 2025: n=64 - (-0.0275%), 2026: n=79 + (0.0976%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net 0.0419%, n=143.

## setup3_failed_msb_reversal / all_taker: **FAIL**

signals 167, trades 167, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 119 | -0.0431 | 0.1595% | 0.403 | 0.079 |
| OOS | 48 | -0.2514 | -0.2976% | 0.333 | -0.193 |

OOS per year: 2025: n=19 - (-0.6676%), 2026: n=29 - (-0.0553%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | FAIL |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.2945%, n=48.

## setup3_failed_msb_reversal / maker_entry: **FAIL**

signals 167, trades 167, unfilled limits 0; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 119 | 0.0431 | 0.2201% | 0.420 | 0.109 |
| OOS | 48 | -0.1745 | -0.2403% | 0.333 | -0.155 |

OOS per year: 2025: n=19 - (-0.6150%), 2026: n=29 + (0.0052%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | FAIL |
| >=2_positive_oos_years | FAIL |

Same trades without funding, OOS: mean net -0.2372%, n=48.


## Rerun 2026-10-10 (B151 closed in code): bear fib zone fixed, blow-through bars fill, targets need a tick through

Changes since the 2026-10-09 trade-through rerun (commit cc16a73): (a) `setup2_fib_pullback` built its bear zone descending, so the
bear branch never emitted a signal (the earlier fib numbers were long-only); it now emits shorts. A bar that blows through the whole zone fills
the resting limit and is no longer dropped. (b) `bt_engine.simulate_trade(target_through=)`: a resting target fills only when price trades one tick
(0.1) through it, as entries already did. (d) The report prints open-at-end trades.

Data: BTCUSDT 1m 2022-01-01..2026-09-26 (F:/MTS/data/tom_raw/klines, 2,491,200 bars, zero gaps), 1h bars 41,520, funding 7,395 records. Defaults only, no grid.
```
setup1_sr_flip           all_taker  FAIL  trades 1477 (unfilled 50, open at end 0)  OOS n=421  mean net -0.1069 %  Sharpe -0.883
                         maker      FAIL                                           OOS n=421  mean net -0.0382 %  Sharpe -0.263
setup2_fib_pullback      all_taker  FAIL  trades 1382 (unfilled 0,  open at end 0)  OOS n=398  mean net -0.0940 %  Sharpe -0.316
                         maker      FAIL                                           OOS n=398  mean net -0.0275 %  Sharpe -0.087
setup3_failed_msb_rev    all_taker  FAIL  trades 167  (unfilled 0,  open at end 0)  OOS n=48   mean net -0.2981 %  Sharpe -0.194
                         maker      FAIL                                           OOS n=48   mean net -0.2408 %  Sharpe -0.156
```
Reading: the fib pullback's earlier OOS +0.042 % (maker, n 143) does not survive: with shorts included and blow-through fills counted, OOS n is 398 and the
mean is -0.0275 % (maker) / -0.094 % (taker); its "0 unfilled" is now true by construction of the fill rule rather than by dropped signals. No CryptoCred setup
passes under either fee variant. The stop buffer and target values stay NO-SOURCE (B143); nothing here selects them.
