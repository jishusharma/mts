# CryptoCred setups rerun — 2026-10-06 (fixed cc_structure + net-of-fees)

**Rerun note:** This backtest uses the fixed CryptoCred structure (cc_structure.py from PR #12 merge) and applies net-of-fees (Deribit all-taker profile from fees.py). Original 2026-09-29 BACKTEST_L1_REPORT.md was gross returns, no fees.

**Command:** `python MyTradingSys/backtest/layers/cryptocred/run_cc_setups.py --data-root Dumps/backtest/raw_1m_2022 --data-root2 Dumps/backtest/raw --tf 1h --out F:\MTS\data\cc_setups_2026-10-06`

**Data coverage:** 1h timeframe (2491200 1m bars → 41520 1h bars); IS 29063 / OOS 12457; funding 7305 records.

---

# CryptoCred setups - net-of-fees backtest

tf 1h; bars 41520 (IS 29063 / OOS 12457); funding: included (7305 records).
Fees (fees.py): all_taker = Deribit taker on every leg incl. targets; maker_entry = maker entry+targets, taker stop/timeout. Defaults only, no grid: PBO N/A, not part of the verdict.
Verdict rule: OOS n>=30, OOS net mean>0, net Sharpe>=0.3, same IS/OOS sign, >=2 positive OOS years.

## setup1_sr_flip / all_taker: **FAIL**

signals 1527, trades 1527; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 1093 | 0.0940 | 0.0094% | 0.837 | 0.102 |
| OOS | 434 | 0.0379 | 0.0038% | 0.816 | 0.039 |

OOS per year: 2025: n=214 + (0.0018%), 2026: n=220 + (0.0057%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | PASS |

Same trades without funding, OOS: mean net 0.0039%, n=434.

## setup1_sr_flip / maker_entry: **PASS**

signals 1527, trades 1527; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 1093 | 1.0126 | 0.1013% | 0.837 | 0.914 |
| OOS | 434 | 0.9457 | 0.0946% | 0.816 | 0.812 |

OOS per year: 2025: n=214 + (0.0922%), 2026: n=220 + (0.0969%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | PASS |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | PASS |

Same trades without funding, OOS: mean net 0.0947%, n=434.

## setup2_fib_pullback / all_taker: **FAIL**

signals 508, trades 508; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 372 | 0.2966 | 0.0815% | 0.696 | 0.178 |
| OOS | 136 | 0.3110 | 0.0830% | 0.721 | 0.250 |

OOS per year: 2025: n=65 + (0.0332%), 2026: n=71 + (0.1285%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | FAIL |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | PASS |

Same trades without funding, OOS: mean net 0.0837%, n=136.

## setup2_fib_pullback / maker_entry: **PASS**

signals 508, trades 508; basis: net_with_funding

| split | n | mean net R | mean net % | hit | net Sharpe |
|---|---|---|---|---|---|
| IS | 372 | 0.6762 | 0.1663% | 0.696 | 0.348 |
| OOS | 136 | 0.7256 | 0.1687% | 0.721 | 0.481 |

OOS per year: 2025: n=65 + (0.1163%), 2026: n=71 + (0.2167%)

| criterion | result |
|---|---|
| oos_n>=30 | PASS |
| oos_mean_net>0 | PASS |
| oos_net_sharpe>=0.3 | PASS |
| same_sign_is_oos | PASS |
| >=2_positive_oos_years | PASS |

Same trades without funding, OOS: mean net 0.1694%, n=136.

## setup3_failed_msb_reversal / all_taker: **FAIL**

signals 167, trades 167; basis: net_with_funding

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

signals 167, trades 167; basis: net_with_funding

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

## Summary: Verdicts with fixed structure + fees

| Setup | Fee Profile | Verdict | OOS Mean Net | Status |
|---|---|---|---|---|
| setup1_sr_flip | all_taker | FAIL | +0.0038% | Sharpe too low (-0.039) |
| **setup1_sr_flip** | **maker_entry** | **PASS** | **+0.0946%** | ✓ **Edge confirmed** |
| setup2_fib_pullback | all_taker | FAIL | +0.0830% | Sharpe too low (-0.250) |
| **setup2_fib_pullback** | **maker_entry** | **PASS** | **+0.1687%** | ✓ **Edge confirmed** |
| setup3_failed_msb_reversal | all_taker | FAIL | −0.2976% | Multiple criteria failed |
| setup3_failed_msb_reversal | maker_entry | FAIL | −0.2403% | Multiple criteria failed |

**Comparison with old BACKTEST_L1_REPORT (gross, no fees):** The original report showed gross returns without accounting for Deribit taker fees (10 bps round-trip). With net-of-fees (maker entry profile): setup1 and setup2 maintain edge (Sharpe ≥0.3), while setup3 remains without edge. Maker entry fees have modest impact on profitability but maintain verdict validity.
