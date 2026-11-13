# Forced-move read: checklist for a Haiku or Sonnet reader (requirement R25)

Descriptive only. No trade advice, no entry, no size, no order. Tested 2026-11-13: fading forced moves 0/128 cells pass;
OI build/unwind did not separate spikes that reverse from those that continue (research edge-forced-move-fade-1113).

## Steps
1. Run `python MyTradingSys/tools/live_aid/flow_collector.py --once` (REST only, public data, exits in about 10 s).
2. Read `runtime_data/live_aid/flow_digest.txt` (at most 30 lines, fixed keys). Read nothing else.
3. If the loop is running (`python MyTradingSys/tools/live_aid/flow_collector.py`) the file is rewritten every 60 s: skip step 1 when `T` is under 2 minutes old.
4. Answer in exactly this 6-line shape, copying numbers from the digest, never guessing:
   - State now: the `1H LAST` and `5M LAST` states in words, with dpx / doi.
   - Who is forced: FORCED_BUYING = shorts closing; FORCED_SELLING = longs closing; NEW_LONGS / NEW_SHORTS = fresh positions; FLAT = nothing.
   - Build or unwind: the `1H RUN` / `30M RUN` lines (kind, dir, bars, doi, dpx, from, active). `none` = say none.
   - Large trades side: count BUY vs SELL in the `BIG` lines (500,000 USD or more); `BIG none` = say none.
   - What would change the read: the opposite state on the next closed 5M bar, or the run ending (active=0).
   - Stale feeds: every `STALE` line and any `NOT_IN_DATA`, verbatim.

## Words
| Digest | Meaning |
|---|---|
| state | price and OI both moved 0.1 % or more: price up + OI up NEW_LONGS, price up + OI down FORCED_BUYING, price down + OI up NEW_SHORTS, price down + OI down FORCED_SELLING |
| taker | agree = CVD sign matches price (taker-driven), disagree = absorbed, na = flat |
| RUN BUILD / UNWIND | 3+ bars of OI rising / falling, 0.5 % or more in total |
| cvd | BTC, spot taker delta for the bar (spot CVD) |
| FP 15M / 1H | footprint from the Bybit trade stream: delta BTC, POC, biggest print, large buy / sell counts; NOT_IN_DATA when the loop is not running |

Thresholds are OURS (STEPS.md, "Forced moves rules"). The same picture, colour-coded, is the Forced moves tab on Live Aid.
