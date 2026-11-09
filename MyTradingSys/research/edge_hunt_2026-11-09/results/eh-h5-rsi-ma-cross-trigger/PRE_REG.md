# PRE_REG: eh-h5-rsi-ma-cross-trigger (trial T06)

Card: edge-hunt-plan-opus-1109 wave 2026-11-09. Frozen in TRIALS.md: T06 = RSI14 back under its SMA14 and under 60 after a >= 60 reading within 6 bars (mirror over 40 after <= 40), confirmed when the next bar trades through the prior bar's open; stop at the 6-bar swing, 2.5R, 30 bars; both sides pooled. Fee regime A. Data BTCUSDT + ETHUSDT spot 4h, 2017-08 .. 2025-06-30.

Written before any return is computed. This file is the rules table; the code implements exactly this.

## Rules (frozen)

| Item | Short | Long (mirror) | Label |
|---|---|---|---|
| RSI | Wilder RSI14 on 4h closes (rsi_core.py semantics) | same | SOURCED repo layers/rsi/rsi_core.py |
| RSI MA | SMA14 of RSI14 | same | SOURCED (READING.md header, per brief) |
| Armed | RSI14 >= 60 on any of the 6 bars before the signal bar (t-6 .. t-1) | RSI14 <= 40 on any of the 6 bars before the signal bar | 60/40 SOURCED (malkan_40_60.py MLK-R1); 6 bars OURS |
| Signal bar t | RSI14[t] < SMA14(RSI)[t] AND RSI14[t] < 60 | RSI14[t] > SMA14(RSI)[t] AND RSI14[t] > 40 | READING.md layer 3 (OURS from his reads) |
| Signal event | only the FIRST bar of a run where the signal condition holds (condition false on t-1) | same | OURS (avoids counting one state many times) |
| Confirmation / entry | bar t+1 trades below open[t]: sell-stop. Fill = min(open[t+1], open[t]) (gap fill at open) | bar t+1 trades above open[t]: buy-stop. Fill = max(open[t+1], open[t]) | READING.md layer 3 (OURS); stop-order fill rule OURS |
| No confirmation | bar t+1 does not trade through open[t]: no trade | same | OURS |
| Stop | max(high[t-5..t]) (6-bar swing incl. signal bar) | min(low[t-5..t]) | OURS (READING.md "stop above the swing wick") |
| Risk R | stop - fill (short); fill - stop (long); must be > 0 | same | OURS |
| Target | fill - 2.5R (short) | fill + 2.5R (long) | SOURCED-ish: TRIALS.md T06 (2.5R) |
| Time stop | 30 bars counting the entry bar t+1; exit at close of bar t+30 (taker) | same | OURS |
| Same-bar rule | on the entry bar, stop checked before target (conservative); stop wins a tie | same | OURS, brief s5 |
| Open trade | one open trade per symbol and side; a signal whose entry bar falls inside an open trade is skipped (not queued) | same | OURS |
| Trial | T06 = both sides, both symbols pooled | | TRIALS.md |
| Exploratory (not promotable) | per side; with / without the daily RSI14 below 60 (short) / above 40 (long) on the last CLOSED daily bar | | OURS |

## Fees, funding, R

- Regime A: taker 0.0005 per side (fees.py DERIBIT_TAKER / BINANCE_TAKER value; 10 bps RT) plus 2 bps RT slippage (FORMULAS s13) = 12 bps RT. All legs taker (stop-order entry, target, time stop).
- fee_r = 12 bps / stop distance in bps. Funding R = (funding cost as fraction of entry) / (stop distance as fraction of entry), cost sign from fees side convention (backtest/bt/bt_data.py funding_cost_pct: side x sum of rates over settlements in (entry, exit]; short side -1 receives a positive rate).
- Net R = gross R - fee_r - funding R. Gross R is -1 at stop, +2.5 at target, (entry-close)/R at time stop (short; mirrored for long).
- Funding: perp funding archive exists from 2019-09. Spot-history bars: funding applied where the archive exists, 0 before 2019-09 (stated in RESULT).

## Statistics and splits

- DEV = 2017-08-01 .. 2024-06-30 23:59 UTC (data start .. 2024-06-30). VALIDATION = 2024-07-01 .. 2025-06-30, read once, only if DEV screen passes. HOLDOUT = 2025-07-01 onward, never loaded; data fetched only to 2025-06-30.
- Note: backtest/splits.py DEV_START is 2022-01-01 (the repo's operator-sourced DEV). The brief fixes DEV = data start .. 2024-06-30 for the wave, so this study uses its own constants (DECISION (OURS) in RESULT).
- Clustering: SE clustered by ISO week (4h trades). Mean net R, cluster-robust SE, 95 % CI from the cluster SE.
- DEV screen: n >= 30 AND mean net R > 0 AND 95 % CI lower bound > 0.
- VALIDATION: one-sided p for mean net R > 0 (normal approximation on the cluster SE); Holm at m = 15 (TRIALS.md).
- Verdict: PASS = DEV screen and VALIDATION Holm-significant with mean > 0; FAIL = DEV mean net R <= 0 with CI upper bound below the MDE; INCONCLUSIVE otherwise.
- MDE at 80 % power = 2.8 x SE (power_mde / research_kit.mde convention).

## Context

- Regime: none for the trigger itself, because the trigger is a 4h momentum event and the wave's regime is reported as a mix line (Regime mix:), not as a gate; the RSI-only rule is tested without a regime gate.
- Phase: none, because the rule has no phase label; the RSI-level phase view is T15 / exploratory only.
- Session: none, because 4h bars cover all sessions and the source does not gate by time of day.
- Entry: stop-order entry on the next bar through the signal bar's open (the trigger's confirmation), no retest.

Regime mix: computed per DEV week from daily SMA200 side + weekly/monthly RSI14 band (research_kit.regime_tag rule, re-implemented in rsi_ma_cross.py), in the RESULT.
