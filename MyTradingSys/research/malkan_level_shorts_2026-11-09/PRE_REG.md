# PRE_REG: Malkan level-short stack, BTCUSDT 4h (card malkan-level-short-4h-count-1109)

Written BEFORE any count run. Operator points C1,C2,V1,V2,C3 are hand-picked in hindsight (READING.md): a pattern, not an edge.

## Seal (backtest/splits.py, one definition)
- Counts run on PRE_DEV 2017-08..2021-12 and DEV 2022-01..2024-06 only (public Binance spot klines, end exclusive 2024-07-01).
- The card says 2017-2026. DECISION (OURS, conservative): VALIDATION (2024-07..2025-06, one read under a PRE_REG) and HOLDOUT (2025-07..) are NOT read for counts or expectancy. They are reported as "sealed, not read". A later card may spend VALIDATION once on ONE pre-named arm (below).
- The 2026-05..10 klines in `fixture/` exist only for the operator-point recall check (item 0g). No count, hit rate or expectancy is computed on them; the read is logged in research/holdout_reads.csv.

## Context
Regime: gate = daily close vs 200-day SMA (bull > +5 pct, bear < -5 pct, else range) at entry, reported as strata; the daily/weekly RSI gate (layer 5) is part of the stack.
Phase: none, because the stack is a level/structure rule, not a phase rule; phase-first version goes to the testnet forward card after the count.
Session: none, because 4h bars cannot resolve sessions; Malkan's rules are session-free.
Entry: level zone touch + structure (divergence or sweep) + RSI-below-MA trigger + WaveTrend cross + HTF fail; entry on a trade-through of the prior 4h bar's open.

## Stack (every parameter labelled; SOURCED = quote)
| Layer | Rule | Param | Label |
|---|---|---|---|
| 1 Level | confirmed 5/5 pivot-high zone that already rejected price | k=5; zone = pivot high +-0.25 pct (0.5 pct wide); rejection = a low >= 1.0 pct under the pivot within the 5 bars after it; zone life 540 bars; dies on a close above its top | OURS (operator lines are hand-drawn; READING.md) |
| 2 Structure | divergence OR sweep (high > zone pivot, close back under it) | window arm: 3-10 bars inclusive "How many candles are needed? Three." / "It should be between three and 10." (malkan_divergence_default.json); swing arm: last confirmed 3/3 swing high, 3-50 bars ("number of bar should be between five to fifty", GbXnw_tNMtw_raw.txt:460, reverse divergence, borrowed) | window SOURCED; swing arm and 50 cap OURS |
| 2 basis | close-to-close vs wick (high) price compare, RSI at the same bar | both arms | close SOURCED (repo rule), wick OURS |
| 3 Trigger | RSI(14 Wilder) crosses below its SMA14 within 12 bars of the setup bar, RSI >= 60 at some bar since the setup; strict variant also needs RSI < 60 | 12 bars | OURS (READING.md table; V1 shows RSI 76 so "below 60" is the variant) |
| Entry | within 3 bars after the trigger, first bar whose low trades through the prior bar's open; fill min(open, prior open) | 3 bars | OURS (READING.md "trades through the prior candle's open") |
| 4 WaveTrend | LazyBear n1=10 n2=21, wt1 crosses below wt2 between setup-2 and the trigger bar AND (peak of wt1 over the 4 bars to the cross >= 48 (53 band less 5) OR lower high than around the structure reference) | bands 53/60 SOURCED (wavetrend.py Crosses:9-12); near-band tol 5 OURS | mixed |
| 5 HTF | daily RSI < 60 and below the prior daily RSI, OR weekly RSI < 60 with a prior 4-week max >= 60; last CLOSED HTF bar only | 60 | OURS (READING.md) |
| Stop | max high from setup-3 to entry bar, +0.1 pct; skipped if < 0.40 pct from entry (cost rule 0a) | 0.1 pct, 0.40 pct | OURS |
| Exit | target 1R (primary) or 2R; stop first on a same-bar tie; time exit at the close of bar 60 after entry | 60 bars | OURS |
| Fee | 0.04 pct taker per side on entry and exit notional, no funding, no slippage | | task card |

## Arms (trial count = 8 variants, exploratory; a count is not selection)
{window 3-10, swing-to-swing} x {close, wick} x {trigger cross, trigger cross + RSI < 60}; sweep OR'd in every arm. Primary arm (the SOURCED one): window / close / cross, 1R exit.

## Reported
Layer ladder (L1-3, +L4, +L5 counts), firings, non-overlapping trades, hit >= 1R, fee-net expectancy (R) by regime and by year, 1R and 2R exits, power note (N per period; N < 100 = underpowered, never "no edge"), operator-point table (fired or the named miss).

## Kill / next
No testnet card unless fee-net expectancy of the primary arm on DEV+PRE_DEV is > 0 with N >= 30; a positive DEV result still needs ONE VALIDATION read under a new PRE_REG.
