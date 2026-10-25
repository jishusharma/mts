# JISHU METHOD NOTES — 2026-09-20

Verbatim operator direction, session MTS-2026-09-20-0541Z.
Source tag family: [JISHU-NNN] (new; added per MTS_DICTIONARY SOURCE TAGS rule 1,
do not rename existing families).

## Verbatim (2026-09-20 ~09:45Z)

"look what i drew for you - these pull backs and ranges must be used for entires
and exits and lower and higher lows as well. Aldo for profit booking! I showed a
simple rsi divergece on 1 min and it is always effective in a down trend - need
confirmations that we will discuss when time come. And our system can look for
these on evey time frames!!! These are my(jishu) thoughts and store them verbatim
where needed!"

## What was drawn on the chart

1m BTCUSDT, 07:45-10:00 UTC. Zigzag vertices approximately:
  80330 (top, 08:05) -> 80150 (low, 08:50) -> 80210 (shelf, 09:00) -> 80524 (top, 09:40).
The 08:50 low was a lower low; the 09:00 shelf was a higher low. RSI 1m printed
bullish divergence at the 08:50 low. Pullback inside the move: 80524 -> 80499.

## Requirements implied for MTS

1. Track higher lows and lower lows per timeframe (1m, 5m, 15m, 1h, 4h, 1d).
2. Use pullbacks inside ranges as entries and exits, not as WAIT conditions.
3. Use pullbacks for profit booking (partial exit at swing highs).
4. RSI divergence detection on every timeframe, long and short.
5. Confirmation rules to be designed before any layer goes live.

## Gaps in MTS today (from disk, 2026-09-20)

- No RSI layer live. MalkanView RSI is [MALKAN-NNN] planned only.
- No wave trend layer.
- structure block in snapshot carries swing_high / swing_low per timeframe but
  does not track sequences of higher / lower lows across bars.
- No profit-booking rule in the verdict path.
- net_rr >= 2.0 gate blocks every daily VAL long (see B058).
- Rank-1 zone drifts with post-funding window (see B059).