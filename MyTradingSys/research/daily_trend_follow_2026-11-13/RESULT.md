# RESULT: daily trend-following, long and short, 60 coins (edge7-daily-trend-follow-1113)

**Verdict: no rule passes. 0 of 10 combined books pass; every one fails the CI test (VALIDATION mean daily return CI lower bound below 0) and the Sharpe >= 1.0 test, and none survives BH 10 %. Following the daily trend on 60 coins does not give a fee-and-funding-net edge here either.**

Regime mix: BTC daily close vs 200d SMA, 2021-01-01..2026-11: bull 49 % / bear 38 % / range 13 %; 2024-01-01..now (VALIDATION): bull 56 % / bear 29 % / range 15 % (from edge6 capitulation_breadth RESULT.md; the BTC 200d gate of rules 8-10 uses the strict close above/below the SMA).

Data: Binance public spot daily klines (60 coins, PRE_REG.md universe), 2020-07-18 (first day the BTC 200d SMA exists = DEV start) .. 2026-11-12 (last closed bar; the newest bar is excluded). DEV 2020-07-18..2023-12-31, VALIDATION 2024-01-01..2026-11-12 (1047 days). Funding: Bybit v5 linear history for 59 of 60 coins (SHIB not found under SHIB/1000SHIB/10000SHIB, charged by the flat rule); a real record exists for 77-81 % of held coin-days, the rest (before a perp existed, SHIB) take the flat 0.01 %/8 h charge against longs, nothing credited to shorts. Costs: 2 x fees.BINANCE_TAKER + fees.SLIPPAGE_RT_S13 per round trip. Placebo: 1000 draws each (combined = random direction per run; single side = random start date).

## Main table (as pre-registered)
Returns are fractions of equity, additive over days, NOT capped: the pre-registered sizing (1 % risk per coin, 60 coins) runs average gross exposure 1.3x to 10.8x (column "avg gross" below), so "ann. return" and "max DD" are in units of that leverage; max DD above 100 % means the additive curve fell by more than the starting equity, i.e. the book as sized is not survivable. Compare rules by Sharpe, not by raw return. "vs basket" = strategy VAL Sharpe AND mean both above the equal-weight buy-and-hold basket (Sharpe -0.05, -3.5 % a year: the basket lost, so beating it is easy).

| rule | side | trades (VAL) | VAL ann. return | VAL Sharpe | CI of mean (daily, 95%) | DEV Sharpe | max DD (VAL) | vs basket | placebo p | without best 5 coins (ann.) | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 DON20/10 | long | 815 | +31.9% | 0.28 | [-0.332%, +0.572%] | 1.39 | 211.9% | yes | 0.031 | +5.4% | - |
| 1 DON20/10 | short | 969 | -3.7% | -0.04 | [-0.280%, +0.262%] | 0.00 | 193.3% | no | 0.652 | -13.3% | - |
| 1 DON20/10 | combined | 1784 | +28.2% | 0.20 | [-0.394%, +0.586%] | 1.17 | 238.1% | yes | 0.051 | +3.4% | FAIL |
| 2 DON55/20 | long | 335 | +13.2% | 0.17 | [-0.197%, +0.321%] | 1.43 | 122.4% | yes | 0.097 | +1.2% | - |
| 2 DON55/20 | short | 454 | +8.0% | 0.13 | [-0.142%, +0.181%] | -0.09 | 71.6% | yes | 0.221 | -0.5% | - |
| 2 DON55/20 | combined | 789 | +21.2% | 0.23 | [-0.221%, +0.368%] | 1.15 | 121.2% | yes | 0.023 | +8.8% | FAIL |
| 3 TSM30 | long | 912 | +143.1% | 0.52 | [-0.536%, +1.473%] | 1.33 | 355.8% | yes | 0.001 | +83.8% | - |
| 3 TSM30 | short | 967 | +13.3% | 0.03 | [-1.252%, +1.191%] | 0.08 | 429.2% | yes | 0.380 | -22.2% | - |
| 3 TSM30 | combined | 1879 | +156.4% | 0.39 | [-0.880%, +1.794%] | 1.05 | 475.8% | yes | 0.003 | +97.1% | FAIL |
| 4 TSM90 | long | 488 | +76.5% | 0.24 | [-0.794%, +1.391%] | 0.95 | 466.6% | yes | 0.033 | +25.4% | - |
| 4 TSM90 | short | 504 | -53.3% | -0.14 | [-1.361%, +1.036%] | -0.21 | 500.0% | no | 0.958 | -82.0% | - |
| 4 TSM90 | combined | 992 | +23.2% | 0.05 | [-1.289%, +1.542%] | 0.43 | 683.1% | yes | 0.267 | -24.5% | FAIL |
| 5 ADX14 | long | 514 | +70.5% | 0.57 | [-0.245%, +0.721%] | 1.43 | 216.7% | yes | 0.001 | +30.5% | - |
| 5 ADX14 | short | 631 | +7.0% | 0.06 | [-0.271%, +0.294%] | -0.20 | 157.3% | yes | 0.293 | -6.3% | - |
| 5 ADX14 | combined | 1145 | +77.5% | 0.48 | [-0.315%, +0.779%] | 1.09 | 188.2% | yes | 0.002 | +37.7% | FAIL |
| 6 ADX14-3d | long | 205 | -5.9% | -0.06 | [-0.275%, +0.286%] | 1.32 | 109.0% | no | 0.800 | -22.2% | - |
| 6 ADX14-3d | short | 195 | +7.6% | 0.15 | [-0.125%, +0.170%] | -0.71 | 61.7% | yes | 0.162 | +0.9% | - |
| 6 ADX14-3d | combined | 400 | +1.8% | 0.02 | [-0.282%, +0.341%] | 1.02 | 124.4% | yes | 0.388 | -12.9% | FAIL |
| 7 MA20/50 | long | 1658 | +61.3% | 0.16 | [-1.006%, +1.615%] | 1.52 | 691.5% | yes | 0.141 | -52.8% | - |
| 7 MA20/50 | short | 2562 | +67.7% | 0.10 | [-1.620%, +2.042%] | -0.01 | 719.3% | yes | 0.227 | -20.3% | - |
| 7 MA20/50 | combined | 4220 | +129.1% | 0.17 | [-1.673%, +2.608%] | 0.94 | 974.5% | yes | 0.044 | +9.9% | FAIL |
| 8 GATED-DON20/10 | long | 746 | +54.2% | 0.50 | [-0.250%, +0.594%] | 1.48 | 205.5% | yes | 0.001 | +30.3% | - |
| 8 GATED-DON20/10 | short | 841 | -22.9% | -0.33 | [-0.250%, +0.142%] | -0.14 | 164.3% | no | 0.994 | -28.0% | - |
| 8 GATED-DON20/10 | combined | 1587 | +31.3% | 0.24 | [-0.352%, +0.596%] | 1.12 | 274.2% | yes | 0.022 | +10.0% | FAIL |
| 9 GATED-TSM30 | long | 680 | +215.9% | 0.85 | [-0.253%, +1.624%] | 1.79 | 276.9% | yes | 0.001 | +161.0% | - |
| 9 GATED-TSM30 | short | 1022 | -97.0% | -0.38 | [-1.001%, +0.482%] | -0.15 | 550.1% | no | 0.999 | -109.9% | - |
| 9 GATED-TSM30 | combined | 1702 | +118.9% | 0.33 | [-0.803%, +1.571%] | 1.04 | 562.6% | yes | 0.002 | +70.4% | FAIL |
| 10 GATED-ADX14 | long | 412 | +102.9% | 0.85 | [-0.137%, +0.797%] | 1.55 | 164.7% | yes | 0.001 | +63.5% | - |
| 10 GATED-ADX14 | short | 738 | -44.1% | -0.52 | [-0.345%, +0.107%] | -0.12 | 225.1% | no | 1.000 | -47.7% | - |
| 10 GATED-ADX14 | combined | 1150 | +58.8% | 0.40 | [-0.320%, +0.742%] | 1.23 | 238.0% | yes | 0.003 | +27.3% | FAIL |

Basket (equal-weight buy-and-hold of the same coins, VAL): Sharpe -0.05, ann. return -3.5%, cumulative -10.2%


## Reading
- Nothing reaches the CI gate: every combined book has a VALIDATION CI of the mean daily return straddling 0 (lower bounds -0.22 % to -1.67 %), and the one-sided p is 0.22-0.44 for all ten (BH rejects none). VALIDATION Sharpe is 0.02-0.48 (best combined: rule 5 ADX14, 0.48), never 1.0. DEV Sharpe is above 0 for all 10 combined books (0.43 to 1.23; 1.0 or more for rules 1, 2, 3, 5, 6, 8, 9, 10) but VALIDATION does not hold it.
- The long side carries it and the short side does not: long-only books are positive in VALIDATION for 9 of 10 rules (best: rule 9 GATED-TSM30 and rule 10 GATED-ADX14, Sharpe 0.85 each, placebo p 0.001, CI still crossing 0), while short-only books lose for rules 1, 4, 8, 9, 10 (the BTC-gated shorts are the worst: Sharpe -0.33 / -0.38 / -0.52). Survivorship flatters longs and hurts shorts, so the long side is an upper bound.
- The placebo is not the binding gate: 7 of 10 combined books beat the random-direction placebo (p <= 0.05; rules 2, 3, 5, 7, 8, 9, 10 at 0.002-0.044; rule 1 at 0.051). The signal has direction information; it is too small and too lumpy to clear the CI and Sharpe gates.
- Concentration: the best 5 coins make 38-92 % of VALIDATION profit for rules 1, 2, 3, 5, 7, 8, 9, 10 (rules 4 and 6: 205 % and 834 %, i.e. the other 55 coins lose), and the best 10 days exceed 100 % of VALIDATION profit for every rule (159-4176 %): without them the book is negative. Without the best 5 coins the annualised return is -25 % to +97 % (rule 3 stays +97 %, rule 4 -24.5 %, rule 6 -12.9 %).
- Per year: no rule is positive in every year. Rule 9 loses only 2025 (-11.5 %) and rule 2 only 2026 (-12.8 %); gross exposure 4.6x and 1.3x.
- Last 90 days (to 2026-11-12, sum of daily returns, leveraged units): rule 1 +63.8 %, 2 +7.5 %, 3 +0.6 %, 4 -469 %, 5 +110.7 %, 6 -13.7 %, 7 +329.9 %, 8 +65.5 %, 9 +95.8 %, 10 +85.6 %. Most trend books are positive now, but that is 90 days, not a validation; rule 4 -469 % is the weekly-rebalanced 90-day TSM on a sharp reversal.
- Rule 7 (MA 20/50) trades 1471 times a year at 9.7 days average hold with 10.8x gross: +129 % a year on Sharpe 0.17 is leverage and noise, not edge.

## Gates and descriptives (combined book)
Gates (combined book): g1 CI>0, g2 Sharpe VAL>=1 & DEV>0, g3a beats basket, g3b placebo p<=0.05, g4 BH 10%
| rule | g1 | g2 | g3a | g3b | g4 | one-sided p | DEV ann. | last 90d sum | avg hold d | trades/yr | avg gross | best-5 share | best-10-days share | top5 coins | funding cov. |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 DON20/10 | n | n | Y | n | n | 0.3762 | +154.2% | +63.8% | 27.7 | 622 | 2.26 | +87.8% | +354.9% | ZEC DOGE TRX XTZ XLM | 77% |
| 2 DON55/20 | n | n | Y | Y | n | 0.3264 | +99.4% | +7.5% | 51.7 | 275 | 1.31 | +58.7% | +323.9% | ZEC RVN BNB ETH KAVA | 79% |
| 3 TSM30 | n | n | Y | Y | n | 0.2709 | +393.6% | +0.6% | 33.9 | 655 | 8.10 | +37.9% | +173.3% | ETH DYDX SHIB DOGE GRT | 79% |
| 4 TSM90 | n | n | Y | n | n | 0.4355 | +161.3% | -469.0% | 60.8 | 346 | 8.10 | +205.4% | +1095.6% | SHIB TRX GALA HBAR NEAR | 81% |
| 5 ADX14 | n | n | Y | Y | n | 0.2245 | +175.5% | +110.7% | 25.2 | 399 | 2.13 | +51.4% | +158.8% | TRX ZEC ENJ XLM DOGE | 77% |
| 6 ADX14-3d | n | n | Y | n | n | 0.4398 | +92.8% | -13.7% | 70.7 | 139 | 1.27 | +833.8% | +4176.0% | AR BNB ZEC TRX NEAR | 79% |
| 7 MA20/50 | n | n | Y | Y | n | 0.3618 | +705.4% | +329.9% | 9.7 | 1471 | 10.83 | +92.3% | +410.6% | ZEC RLC THETA CVC XLM | 79% |
| 8 GATED-DON20/10 | n | n | Y | Y | n | 0.3381 | +138.5% | +65.5% | 20.5 | 553 | 1.42 | +68.2% | +316.8% | ZEC DOGE XLM XTZ GALA | 79% |
| 9 GATED-TSM30 | n | n | Y | Y | n | 0.2787 | +370.5% | +95.8% | 24.1 | 593 | 4.57 | +40.8% | +226.0% | SHIB DOGE ETH BNB ENS | 80% |
| 10 GATED-ADX14 | n | n | Y | Y | n | 0.2633 | +187.3% | +85.6% | 18.4 | 401 | 1.41 | +53.6% | +205.3% | TRX ZEC BNB XLM DOGE | 78% |

Per-year return (sum of daily returns, combined book):
| rule | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|
| 1 DON20/10 | +58.9% | +296.5% | +15.5% | +162.4% | +66.0% | -46.6% | +61.4% |
| 2 DON55/20 | +31.0% | +233.7% | +4.6% | +74.1% | +42.0% | +31.7% | -12.8% |
| 3 TSM30 | +124.6% | +888.0% | -50.4% | +398.5% | +288.1% | +209.7% | -49.1% |
| 4 TSM90 | -6.0% | +371.2% | +320.1% | -127.4% | +528.0% | +67.6% | -529.0% |
| 5 ADX14 | +61.7% | +410.0% | -59.5% | +194.7% | +132.0% | +12.4% | +77.9% |
| 6 ADX14-3d | +8.3% | +321.3% | -23.1% | +14.4% | -13.3% | +45.2% | -26.9% |
| 7 MA20/50 | +206.7% | +1644.1% | +596.9% | -8.9% | +262.3% | +174.6% | -66.7% |
| 8 GATED-DON20/10 | +77.8% | +228.6% | +101.9% | +70.3% | +48.8% | -75.8% | +116.8% |
| 9 GATED-TSM30 | +221.1% | +533.8% | +404.5% | +121.7% | +120.8% | -11.5% | +231.6% |
| 10 GATED-ADX14 | +68.5% | +296.8% | +78.6% | +203.8% | +99.9% | -58.4% | +127.1% |

## Limits
Survivorship (PRE_REG.md): long numbers are upper bounds, short numbers lower bounds. Spot prices stand in for perp prices. The sizing and the no-gross-cap rule are pre-registered and drive the leverage and drawdown figures; a gross-capped book would have a smaller return and drawdown at the same Sharpe (Sharpe is scale-free, so the verdict does not depend on it). One universe, one run, no tuning; seed 20261113.
