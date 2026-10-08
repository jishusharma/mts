# T055 C1/C2 RERUN, full funding, 2026-10-07

Session: MTS-2026-10-07-1002Z-APP-BLD-research-closeout. Replaces T055_BT_c1_RERUN_2026-10-06.md and T055_BT_c2_RERUN_2026-10-06.md (commit 4c74cd7, research branch) for the verdict.

## Why the 10-06 rerun is not valid
- The 10-06 C1 report states funding history from 1756684800000 ms (2025-09-01), i.e. about 12 months, and an OOS net identical to the 09-29 run (-0.3992%): it did not use the 80 funding files (2020-01..2026-08, 7305 records).
- With all 7305 records loaded, run_t055 c1 crashes: ValueError in trade_costs.funding_paid, funding covers to 1788192000001 (2026-08-31) but bars run to 2026-09-26. Reproduced 2026-10-07.
- Fix (research code, not live): run_t055.load_data keeps only bars that close inside funding coverage. Test: backtest/layers/test_run_t055.py::TestFundingForC2::test_load_data_clips_bars_to_funding_coverage (failed before the fix, 26 pass after). C1 now 35008 15m bars (was 37536), C2 490656 5m bars.
- Command (research worktree mts-research at 5334975 plus the fix, absolute data roots): python -m MyTradingSys.backtest.layers.run_t055 --candidate c1|c2 --data-root <repo>/Dumps/backtest/raw_1m_2022 --data-root2 <repo>/Dumps/backtest/raw. Raw output: BinanceDataFeed_backups/t055_rerun_2026-10-07/.

## Result
| candidate | verdict | OOS n | OOS net mean | OOS net Sharpe | funding coverage | note |
|---|---|---|---|---|---|---|
| C1 funding_cvd_fade | FAIL | 76 | -0.0453% | -0.0346 | from 2020-01, all trades funded | OOS net moved from -0.3992% (09-29 and 10-06) to -0.0453%; verdict unchanged; criteria oos_mean_net, oos_net_sharpe, same_sign fail; still 'provisional' (single year of OOS) |
| C2 session_momentum | FAIL | 299 | +0.0177% | 0.0084 | from 2020-01 | oos_mean_net PASS, Sharpe FAIL, only 1 of 2 OOS years positive; the 10-06 run (n=519, -0.2988%) used the wrong funding window |

Both candidates close under the T055 rule (FAIL closes). Nothing was tuned.

## Raw reports

### C1

#### T055 backtest - C1 (funding_cvd_fade)

Verdict: **FAIL** (provisional: ~12 months of funding, single 70/30 split)

Bars 35008 (IS 24505 / OOS 10503); variants 108; cost: fee 10 bps RT + slip 2 bps RT + funding (included). PBO (CSCV, IS daily net): 0.1385

IS-chosen: `{"params": {"lookback": 90, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}, "horizon": 48}`

| split | n events | gross mean | net mean | hit (gross) | hit (net) | net Sharpe |
|---|---|---|---|---|---|---|
| IS | 129 | 0.5244% | 0.4113% | 0.6047 | 0.5271 | 0.2736 |
| OOS | 76 | 0.0650% | -0.0453% | 0.4868 | 0.4737 | -0.0346 |

Funding coverage (funding history from 1577836800000 ms; trades before it are net of fees+slippage only, no funding): IS: 129 funded / 0 fee-only trades, funded-trade net 0.4113% vs same trades without funding 0.4044%, fee-only-trade net n/a; OOS: 76 funded / 0 fee-only trades, funded-trade net -0.0453% vs same trades without funding -0.0550%, fee-only-trade net n/a

OOS by calendar year: 2026: n=76 net=-0.0453%

## Criteria (runbook step 4)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | FAIL |
| oos_net_sharpe>=0.3 | FAIL |
| pbo<0.5 | PASS |
| same_sign_is_oos | FAIL |

No parameter was tuned on OOS. On FAIL the candidate closes; on PASS register alert-only.

## Top IS grid points (by net mean)

| params | horizon | n | net mean |
|---|---|---|---|
| `{"lookback": 90, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 129 | 0.4113% |
| `{"lookback": 90, "n": 50, "hi": 0.99, "lo": 0.01, "use_divergence": true}` | 48 | 43 | 0.4109% |
| `{"lookback": 60, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 119 | 0.4081% |
| `{"lookback": 60, "n": 50, "hi": 0.99, "lo": 0.01, "use_divergence": true}` | 48 | 44 | 0.3931% |
| `{"lookback": 180, "n": 50, "hi": 0.99, "lo": 0.01, "use_divergence": true}` | 48 | 54 | 0.3816% |
| `{"lookback": 180, "n": 50, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 134 | 0.3105% |
| `{"lookback": 90, "n": 50, "hi": 0.9, "lo": 0.1, "use_divergence": true}` | 48 | 191 | 0.2642% |
| `{"lookback": 60, "n": 50, "hi": 0.9, "lo": 0.1, "use_divergence": true}` | 48 | 202 | 0.2322% |
| `{"lookback": 180, "n": 50, "hi": 0.9, "lo": 0.1, "use_divergence": true}` | 48 | 204 | 0.1177% |
| `{"lookback": 60, "n": 20, "hi": 0.95, "lo": 0.05, "use_divergence": true}` | 48 | 202 | 0.0943% |


### C2

#### T055 backtest - C2 (session_momentum)

Verdict: **FAIL**

Bars 490656 (IS 343459 / OOS 147197); variants 16; cost: fee 10 bps RT + slip 2 bps RT + funding (included). PBO (CSCV, IS daily net): 0.0000

IS-chosen: `{"params": {"bar_min": 5, "session_start_min": "ny", "first_min": 60, "entry_min": 60, "min_abs": 0.001}, "horizon": "session"}`

| split | n events | gross mean | net mean | hit (gross) | hit (net) | net Sharpe |
|---|---|---|---|---|---|---|
| IS | 731 | 0.2193% | 0.0999% | 0.5075 | 0.4788 | 0.0356 |
| OOS | 299 | 0.1358% | 0.0177% | 0.5084 | 0.4749 | 0.0084 |

Funding coverage (funding history from 1577836800000 ms; trades before it are net of fees+slippage only, no funding): IS: 731 funded / 0 fee-only trades, funded-trade net 0.0999% vs same trades without funding 0.0993%, fee-only-trade net n/a; OOS: 299 funded / 0 fee-only trades, funded-trade net 0.0177% vs same trades without funding 0.0158%, fee-only-trade net n/a

OOS by calendar year: 2025: n=157 net=0.0636%, 2026: n=142 net=-0.0332%

## Criteria (runbook step 4)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | FAIL |
| pbo<0.5 | PASS |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | FAIL |

No parameter was tuned on OOS. On FAIL the candidate closes; on PASS register alert-only.

## Top IS grid points (by net mean)

| params | horizon | n | net mean |
|---|---|---|---|
| `{"bar_min": 5, "session_start_min": "ny", "first_min": 60, "entry_min": 60, "min_abs": 0.001}` | session | 731 | 0.0999% |
| `{"bar_min": 5, "session_start_min": "ny", "first_min": 60, "entry_min": 60, "min_abs": 0.0}` | session | 843 | 0.0506% |
| `{"bar_min": 5, "session_start_min": "ny", "first_min": 30, "entry_min": 30, "min_abs": 0.001}` | session | 686 | 0.0463% |
| `{"bar_min": 5, "session_start_min": "ny", "first_min": 30, "entry_min": 30, "min_abs": 0.0}` | session | 844 | 0.0438% |
| `{"bar_min": 5, "session_start_min": 0, "first_min": 30, "entry_min": 30, "min_abs": 0.0}` | session | 1192 | -0.0800% |
| `{"bar_min": 5, "session_start_min": 0, "first_min": 30, "entry_min": 1410, "min_abs": 0.001}` | session | 818 | -0.1103% |
| `{"bar_min": 5, "session_start_min": 0, "first_min": 30, "entry_min": 1410, "min_abs": 0.0}` | session | 1192 | -0.1155% |
| `{"bar_min": 5, "session_start_min": 0, "first_min": 60, "entry_min": 1410, "min_abs": 0.0}` | session | 1192 | -0.1270% |
| `{"bar_min": 5, "session_start_min": 0, "first_min": 60, "entry_min": 1410, "min_abs": 0.001}` | session | 946 | -0.1299% |
| `{"bar_min": 5, "session_start_min": "ny", "first_min": 30, "entry_min": 1410, "min_abs": 0.001}` | session | 539 | -0.1338% |

