# PRE_REG: eh-h3-first-touch-sweep (trial T04)

Card: edge-hunt-plan-opus-1109 (wave 2026-11-09). Worker model: claude-haiku-5-5. Frozen before any return is computed.
Trial: **T04** = first-touch sweep-and-reclaim of the prior-day or prior-week high/low, faded from the reclaim close, all four level types, both sides pooled. Primary statistic: mean fee-net R per trade, day-clustered SE.
Exploratory only (cannot promote): repeat-touch arm, by level type, by UTC 4h block, knife flag, by year.

## Hypothesis (one line)
The operator's Friday 74,900 case was a first touch of a daily level, swept and bought back (WICKS_NOTE_2026-11-07.md s2). A first-touch sweep-and-reclaim of PDH/PDL/PWH/PWL, faded, has mean fee-net R > 0 at the frozen exit.

## Rules table (frozen)
| Item | Rule | Label |
|---|---|---|
| Data | BTCUSDT USD-M futures 15m klines + fundingRate, archive 2020-01 .. 2025-06 (2019-09..12 15m files are absent on data.binance.vision: 404) | public archive; data start shift is OURS (documented in RESULT) |
| Level | PDH/PDL = high/low of the prior UTC day (96 bars, closed). PWH/PWL = high/low of the prior ISO week (Mon 00:00 to Mon 00:00, 672 bars). Fixed at the close: a day level is active from D 00:00 UTC to D+1 00:00 UTC; a week level from Mon 00:00 to the next Mon 00:00 | Tom/Fabio prior-session levels SOURCED in kind (POSTMORTEM s2); UTC day and ISO week OURS |
| Approach | close 12 bars before the sweep bar s is strictly inside the level (for high: close < level; for low: close > level) | census rule, OURS |
| Sweep | bar s trades beyond the level (high > PDH/PWH, or low < PDL/PWL) | wick_census.py definition, OURS |
| First touch | s is the first bar beyond the level after its fix time (no earlier bar beyond it in the window). Only one first-touch episode per level window exists by construction (cooldown = one event per level) | operator's "first try" (decision record); threshold OURS |
| Reclaim (V-sweep) | first bar r in [s, s+3] with close back inside the level; r must lie inside the level window | census definition, OURS |
| Entry | close of r (taker) | OURS |
| Stop | sweep extreme: max high (short) / min low (long) over bars s..r, inclusive, no buffer | SOURCED in kind (TOM-072) |
| Target | 2R from entry (distance = |extreme - entry|) | OURS |
| Time stop | close of bar r+96 (24 h) if neither stop nor target trades by then. Stop checked before target on the same bar (stop wins a tie). Bars r+1 .. r+96 only | OURS |
| Side | high sweep = short fade; low sweep = long fade | OURS (fade = trade against the sweep) |
| Trial | T04 = first-touch events, all four level types, both sides pooled | TRIALS.md |
| Repeat arm (exploratory) | the second beyond-episode of the same level window, same rules; at most one per level | OURS |
| Knife flag (exploratory) | the 12 bars before s moved >= 2 % in the sweep direction (down for low sweeps, up for high) AND the largest counter-move (rebound against that direction) < 25 % of that move | OURS |
| Censoring | an event whose hold (r+96) falls beyond the loaded data end is dropped and counted | OURS |

## Fees and R
- Regime A: taker 0.0005 per side (MyTradingSys/backtest/fees.py BINANCE_TAKER / DERIBIT_TAKER = 0.0005), 2 legs = 10 bps round trip, plus 2 bps round-trip slippage (FORMULAS.md s13) = **12 bps round trip**.
- fee_R = 0.0012 / stop_frac, where stop_frac = |extreme - entry| / entry.
- funding_R = side_sign * sum(funding rates with calc_time in (entry close, exit close]) / stop_frac; side_sign = +1 long, -1 short (a long pays a positive rate). 0 before the first archive record (none expected in 2020+).
- net R = gross R - fee_R - funding_R. Gross R = (exit - entry) / |extreme - entry| with the side sign; stop = -1 R, target = +2 R, time stop at its close.

## Statistics and splits (PLAN.md s5)
- DEV = 2020-01-01 .. 2024-06-30 23:45 (data start .. 2024-06-30). VALIDATION = 2024-07-01 .. 2025-06-30, read once and only if DEV screened in. HOLDOUT = 2025-07-01 onward, never loaded. The loader refuses any bar past its split end and a test shows it.
- For VALIDATION the loader also reads the two prior UTC days (2024-06-29 .. 2024-06-30) as warm-up for levels and approach checks. Events are counted only if the sweep bar is in 2024-07-01 .. 2025-06-30. This is OURS.
- SE clustered by UTC day: SE = sqrt(sum_g S_g^2) / n, S_g = sum over trades of day g of (x - mean).
- DEV screen: n >= 30 AND mean net R > 0 AND 95 % CI lower bound > 0.
- VALIDATION: one-sided p for mean net R > 0 (normal approx, cluster SE). Holm at m = 15 across the wave. Holm's first step is Bonferroni 0.05/15 = 0.00333; this worker cannot see other trials' p-values, so the conservative first-step threshold is used. PASS needs p <= 0.00333 AND mean > 0.
- MDE at 80 % power = 2.80 x SE.
- Verdict: PASS = DEV screen and VALIDATION pass. FAIL = DEV mean net R <= 0 AND CI upper bound < MDE. INCONCLUSIVE otherwise.
- A PASS files a raw testnet-forward card; the next step is testnet forward, never a longer backtest.

## Context
- Regime: research_kit.regime_tag (daily SMA side x weekly/monthly RSI band), reported as a regime mix of DEV weeks. Context is recorded, not used as a filter (T04 is not regime-gated). OURS.
- Phase: none, because the rule is level-based and the phase split is exploratory only.
- Session: none, because the level is a daily or weekly UTC level; the 4h-block split is exploratory.
- Entry: reclaim bar r (first close back inside the level within 3 bars of the first beyond bar).

## DECISION (OURS) list (fixed before the return)
1. Data start 2020-01-01 (archive 15m files for 2019-09..12 are absent).
2. UTC day / ISO week levels; a level is active only in its own window.
3. Strict inequalities for "beyond" and "inside"; close exactly at the level counts as not inside.
4. Reclaim window of 3 bars after the sweep bar (s..s+3 inclusive).
5. Fee regime A plus 2 bps RT slippage; funding from the archive.
6. Time stop = close of r+96.
7. Holm first-step threshold 0.05/15 used as the VALIDATION gate.
8. Knife definition (exploratory) as above.
