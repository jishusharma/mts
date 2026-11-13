# REPORT adx 1d through 25 + Holy Grail (card adx-1d-through25-1113)

Regime mix (close above/below own 200d SMA, pooled 5 symbols): DEV 49% bull / 51% bear (n=5739); VALIDATION 43% bull / 57% bear (n=1825); RECENT 38% bull / 62% bear (n=2500).
PRE_REG.md fixes every rule (committed before any outcome). Fee 10 bps RT. CI = 95% cluster bootstrap over calendar months (10,000, seed 1113), overlapping events kept. ex = excess vs same-symbol/split/side unconditional baseline. U = n<30. Data: Bybit 1d, BTC back-filled from csv before 2020-03-25; last closed bar 2026-11-12.
Reproduction check: BTC csv through-25 longs since 2017 = 33 (source study 34 +-4): OK.

## Verdicts
| Rule | Verdict | VALIDATION pooled |
|---|---|---|
| A: 1d ADX through 25, hold 6 (primary) | **FAIL: VALIDATION excess CI lower bound -5.80% not > 0; h=3/h=12 excess not both > 0** | n=30 net -1.96% ex -1.71% [-5.8%,+1.9%] win 47% |
| B: Holy Grail (EMA20, stop/target/12d) | **UNDERPOWERED (VALIDATION n=0 < 30)** | n=0 |

## Rule A, hold 6 days (primary)
| symbol side | DEV | VALIDATION | RECENT |
|---|---|---|---|
| BTC long | n=15 net +4.01% ex +2.98% [-0.1%,+6.3%] win 67% U | n=2 net +10.43% ex +9.37% win 100% U | n=6 net -0.34% ex +0.08% [-4.1%,+2.5%] win 83% U |
| BTC short | n=18 net +2.61% ex +3.84% [+0.2%,+7.9%] win 33% U | n=3 net -4.74% ex -3.47% win 33% U | n=3 net +14.04% ex +13.82% win 67% U |
| ETH long | n=8 net +4.24% ex +3.65% [-3.3%,+10.8%] win 75% U | n=2 net -5.38% ex -5.33% win 0% U | n=4 net -0.07% ex -0.07% win 25% U |
| ETH short | n=11 net -2.69% ex -1.90% [-6.2%,+1.8%] win 36% U | n=2 net +5.74% ex +5.89% win 100% U | n=2 net +1.85% ex +2.06% win 100% U |
| SOL long | n=8 net +1.17% ex +0.00% [-12.7%,+7.8%] win 38% U | n=4 net +0.50% ex -0.05% win 75% U | n=5 net +4.27% ex +4.70% [+0.8%,+8.4%] win 80% U |
| SOL short | n=9 net +2.84% ex +4.21% [-5.0%,+17.3%] win 44% U | n=7 net -7.24% ex -6.49% [-20.3%,+2.9%] win 43% U | n=3 net +5.40% ex +5.17% win 67% U |
| LINK long | n=14 net -4.46% ex -4.82% [-10.0%,-0.4%] win 43% U | n=2 net +0.79% ex +0.19% win 50% U | n=6 net -0.68% ex -0.68% [-8.8%,+12.5%] win 50% U |
| LINK short | n=14 net -1.94% ex -1.37% [-8.0%,+4.5%] win 50% U | n=3 net -2.17% ex -1.37% win 33% U | n=5 net +2.00% ex +2.19% [-5.6%,+12.5%] win 60% U |
| LTC long | n=16 net -3.45% ex -3.61% [-8.0%,+1.0%] win 38% U | n=2 net -4.29% ex -5.05% win 0% U | n=4 net -0.82% ex -0.34% win 50% U |
| LTC short | n=11 net -1.85% ex -1.49% [-5.4%,+3.1%] win 18% U | n=3 net -1.35% ex -0.38% win 33% U | n=4 net +5.23% ex +4.95% win 100% U |
| **POOLED long** | n=61 net -0.23% ex -0.84% [-4.3%,+2.1%] win 51% | n=12 net +0.42% ex -0.16% [-5.3%,+3.6%] win 50% U | n=25 net +0.47% ex +0.73% [-3.9%,+4.3%] win 60% U |
| **POOLED short** | n=63 net -0.07% ex +0.80% [-1.4%,+3.3%] win 37% | n=18 net -3.55% ex -2.74% [-10.0%,+2.1%] win 44% U | n=17 net +5.47% ex +5.40% [+0.4%,+10.2%] win 76% U |
| **POOLED both** | n=124 net -0.15% ex -0.01% [-1.9%,+2.0%] win 44% | n=30 net -1.96% ex -1.71% [-5.8%,+1.9%] win 47% | n=42 net +2.49% ex +2.62% [+1.0%,+4.0%] win 67% |

## Rule A robustness, pooled both sides
| hold | DEV | VALIDATION | RECENT |
|---|---|---|---|
| 3 | n=124 net -0.31% ex -0.19% [-2.2%,+1.6%] win 52% | n=30 net -2.41% ex -2.23% [-3.9%,-0.3%] win 33% | n=43 net +2.40% ex +2.52% [+0.7%,+4.5%] win 56% |
| 6 | n=124 net -0.15% ex -0.01% [-1.9%,+2.0%] win 44% | n=30 net -1.96% ex -1.71% [-5.8%,+1.9%] win 47% | n=42 net +2.49% ex +2.62% [+1.0%,+4.0%] win 67% |
| 12 | n=124 net -0.20% ex -0.01% [-4.0%,+3.8%] win 52% | n=30 net -0.59% ex -0.17% [-7.7%,+6.0%] win 47% | n=42 net +3.04% ex +3.20% [+0.7%,+5.5%] win 50% |

## Rule B (Holy Grail), one exit rule
| symbol side | DEV | VALIDATION | RECENT |
|---|---|---|---|
| BTC long | n=0 | n=0 | n=0 |
| BTC short | n=0 | n=0 | n=0 |
| ETH long | n=0 | n=0 | n=2 net -5.58% ex -5.60% win 50% U |
| ETH short | n=1 net -4.80% ex -3.82% win 0% U | n=0 | n=1 net -4.79% ex -4.61% win 0% U |
| SOL long | n=0 | n=0 | n=1 net +4.48% ex +5.17% win 100% U |
| SOL short | n=0 | n=0 | n=0 |
| LINK long | n=0 | n=0 | n=0 |
| LINK short | n=0 | n=0 | n=0 |
| LTC long | n=0 | n=0 | n=0 |
| LTC short | n=0 | n=0 | n=1 net +7.35% ex +6.68% win 100% U |
| **POOLED long** | n=0 | n=0 | n=3 net -2.22% ex -2.01% win 67% U |
| **POOLED short** | n=1 net -4.80% ex -3.82% win 0% U | n=0 | n=2 net +1.28% ex +1.04% win 50% U |
| **POOLED both** | n=1 net -4.80% ex -3.82% win 0% U | n=0 | n=5 net -0.82% ex -0.79% [-8.4%,+4.3%] win 60% U |
Rule B trades with no target available: 3 of 6 (stop/time exit only).

## Current state (last closed bar)
- BTC 2026-11-12: ADX 23.3 +DI 11.0 -DI 27.8; A: last A signal 2026-08-22 long, 82 d ago; B filter off, no B setup
- ETH 2026-11-12: ADX 26.6 +DI 12.1 -DI 29.7; A: last A signal 2026-11-11 short, 1 d ago (6d hold still open); B filter off, no B setup
- SOL 2026-11-12: ADX 38.9 +DI 8.7 -DI 30.3; A: last A signal 2026-08-23 long, 81 d ago; B filter ON, no B setup
- LINK 2026-11-12: ADX 27.6 +DI 10.6 -DI 24.4; A: last A signal 2026-11-08 short, 4 d ago (6d hold still open); B filter off, no B setup
- LTC 2026-11-12: ADX 36.0 +DI 8.9 -DI 25.2; A: last A signal 2026-08-23 long, 81 d ago; B filter ON, no B setup
