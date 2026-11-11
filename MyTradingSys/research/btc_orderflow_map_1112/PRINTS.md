# PRINTS: BTC large prints (A1) and absorption (A2), card btc-of-map-prints-1112, DEV sample only

Frozen definitions: PREREG.md (not changed). Sample: 60 event days = 6 blocks x 10 consecutive days (+37 warm-up days each; OURS, card). DEV only: VALIDATION, GAP, RESERVE, HOLDOUT never opened; cells are therefore marked from DEV alone and no PASS/LEAD is possible.
Net = gross forward bp minus 10 bp round trip, entry next 1m open after the 5m event bar, 60 min de-clustering. Control = PREREG placebo (1,000 draws, seed 1112, hour-matched, same long/short count, same de-clustering) on the same sampled days; z = (obs - control mean) / control sd; t = mean/(sd/sqrt(n)).

| Event | n | fwd 15m net bp | control 15m (p1..p99) | z15 | t15 | fwd 60m net bp | control 60m (p1..p99) | z60 | t60 | gross 60m bp | mark 15m / 60m |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A1 large print (with L) | 204 (L 111 / S 93) | -11.37 | -10.01 (-14.81..-4.45) | -0.61 | -3.38 | -9.19 | -9.73 (-19.98..+0.77) | +0.12 | -1.62 | +0.81 | none / gross only |
| A2 absorption (against delta) | 15 (L 5 / S 10) | -1.23 | -10.18 (-30.98..+7.03) | +1.12 | -0.20 | +1.43 | -11.59 (-54.49..+26.00) | +0.81 | +0.18 | +11.43 | INSUFFICIENT_N / INSUFFICIENT_N |

Minimum n (PREREG): DEV n >= 180 per cell; below that the cell is INSUFFICIENT_N and gets no verdict. The 60-day sample is a sample of DEV, not all of it, so a low n here is a sampling limit, not a statement about the full DEV window.

**A1 large print (with L) by session (n / net60 bp):** Asia 42 / -8.05, Europe 49 / -5.32, US 92 / -14.22, Late 21 / +1.53
**A1 large print (with L) by regime (n / net60 bp):** bull 51 / -6.09, bear 26 / -14.80, range 91 / -7.83, n/a 36 / -12.97
**A2 absorption (against delta) by session (n / net60 bp):** Asia 3 / +18.54, Europe 1 / -21.88, US 9 / -0.02, Late 2 / -6.09
**A2 absorption (against delta) by regime (n / net60 bp):** bull 3 / +19.33, bear 0 / n/a, range 12 / -3.05, n/a 0 / n/a

Regime mix: bull 27%, bear 17%, range 40%, n/a 17% of 60 sampled event days (DEV).

A1 data: 60 event days used, 0 dropped for missing aggTrades windows, 0 days flagged truncated (threshold below a day's stored top 3%). A1 events from aggTrades; A2 from 1m klines with taker delta.
Missing days are listed in NOT_IN_DATA.md when any.
