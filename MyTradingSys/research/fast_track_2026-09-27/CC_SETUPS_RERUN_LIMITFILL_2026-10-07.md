# CC SETUPS RERUN, limit-fill model, 2026-10-07

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

