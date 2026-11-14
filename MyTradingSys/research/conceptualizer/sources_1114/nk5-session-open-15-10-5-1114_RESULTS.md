# RESULT nk5-session-open-15-10-5-1114

**VERDICT: FAIL. No row passes the gates. Best row NY-asia (12 bp) has mean net R +0.074 on VALIDATION but day-cluster CI lower -0.151, placebo p 0.000 (signal beats random entries, which lose more), ex-best-5-days -0.108, BH q 1.00. All 2h/4h rows are negative net of fees.**

Source: NK video cmH38Uo4sYM (concept nifty-gap-rsi). Pre-registered in PRE_REG.md (committed before any outcome). 20 Binance spot coins, 5m data 2019 on, DEV <2024-01-01, VALIDATION >=2024-01-01. Parameters: 15m RSI14 touch 30/70 zone (SOURCED zone; 35/65 band and 4-bar window OURS); HM = RSI9, EMA3 vs WMA21 (reconstruction OURS; red-below-green = buying SOURCED); anchors NY cash close and UTC close (mapping OURS); stop = max(0.5%, 0.6 x ATR14 1h) (OURS minimum-stop rule); fees 12 bp primary, 6 bp maker row NY-4h.

## Matched rows (phase-matched direction, VALIDATION)
| row | fee | n DEV/VAL | win % | mean net R | CI low (trade) | CI low (day) | placebo p | ex-best-5 | BH q | fee/R | median stop | gate |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NY-2h | 12bp | 2599/1663 | 40.8 | -0.154 | -0.209 | -0.266 | 0.065 | -0.232 | 1.00 | 0.18 | 0.67% | FAIL |
| NY-4h | 12bp | 2599/1663 | 38.5 | -0.082 | -0.152 | -0.228 | 0.006 | -0.187 | 1.00 | 0.18 | 0.67% | FAIL |
| NY-4h | 6bp | 2599/1663 | 40.1 | +0.006 | -0.065 | -0.129 | 0.008 | -0.098 | 1.00 | 0.09 | 0.67% | FAIL |
| NY-asia | 12bp | 2599/1663 | 30.7 | +0.074 | -0.036 | -0.151 | 0.000 | -0.108 | 1.00 | 0.18 | 0.67% | FAIL |
| UTC-2h | 12bp | 2011/1571 | 36.8 | -0.244 | -0.301 | -0.351 | 0.887 | -0.317 | 1.00 | 0.18 | 0.63% | FAIL |
| UTC-4h | 12bp | 2011/1571 | 31.9 | -0.286 | -0.354 | -0.411 | 0.974 | -0.364 | 1.00 | 0.18 | 0.63% | FAIL |

Fee is 0.16-0.18 R at 12 bp (median stop 0.63-0.67% of price, the 0.5% floor binds often), so the minimum stop cut fee drag versus the earlier 15m RSI fails but did not remove it. The NY-asia row is the only positive mean; its 30% win rate means it is a few large winners, and it dies on both CI gates and best-5-days.

## Control rows (mismatched direction, 12 bp, VALIDATION, not gated)
| row | n | win % | mean net R |
|---|---|---|---|
| NY-2h | 773 | 44.2 | -0.074 |
| NY-4h | 773 | 38.6 | -0.102 |
| NY-asia | 773 | 26.3 | -0.045 |
| UTC-2h | 684 | 41.8 | -0.041 |
| UTC-4h | 684 | 32.6 | -0.243 |

## Context
Phase labelled per coin-day from data to prior close: UP = ADX14>=20, +DI>-DI, SMA20 5-day slope>0; DOWN = mirror; else RANGE. UP trades longs only, DOWN shorts only, RANGE fades both ways; mismatched direction is control only.

Regime mix: coin-days DEV RANGE 36.0% / DOWN 32.3% / UP 31.7%; VAL RANGE 39.9% / DOWN 35.6% / UP 24.6%. VAL NY-4h matched trades by phase: DOWN 435, RANGE 949, UP 279 (shorts 869, longs 794). Most trades are RANGE fades.

## Read
The signal is better than random same-phase entries (placebo mean about -0.18 to -0.20 R vs signal -0.08 to -0.15 on 2h/4h) but not enough to pay 12 bp; at 6 bp the NY-4h row is +0.006 R (CI low -0.065). Only the long hold (to 08:00 UTC, ~11-12 h) is positive, which is trend carry in 2024-26 rather than a session-open read. Limitations: stop fills at the stop price (no gap slippage); HM reconstruction unverified against NK's chart; 10m bars built from 5m.

## BTC today (descriptive, no advice)
Data ends 2026-11-13 21:00 UTC (5m close 68,868). Phase label for the day: DOWN (ADX regime from the 11-12 close). Last closed daily bar 11-12: high 74,217, low 71,113, close 71,460; SMA20 77,340. 15m RSI14 last four closed: 52, 49, 48, 48 (no 30/65 touch); 10m HM and 5m HM both in sell state. So the setup is not active: no RSI extreme, so neither the DOWN-phase short (needs RSI >= 65 touch plus HM sell) nor any long signal.

Files: study.py, test_study.py (causality test passes; fails under STUDY_BUG=1), results.csv, run.log.
