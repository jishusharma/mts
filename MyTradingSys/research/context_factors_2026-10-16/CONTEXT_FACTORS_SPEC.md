# CONTEXT FACTORS SPEC: what a BTC trader sees at the decision moment, built point in time (2026-10-16)

Code: `context_asof.py` (`context_at(bars, t, side)` = replay from bars[0..t]; `context_frame(bars, side)` = vectorised).
Tests: `test_context_asof.py` (synthetic tapes, CI-safe). DEV run: `run_dev.py`. Every number below is a definition, not
a result: no outcome column exists in this folder.

Labels: **SOURCED** = a trader's or the operator's words or a repo formula (file:line or the quoted operator rule);
**OURS** = our judgement, fixed before any count unless the row says "angle b/c fix" (changed after a trader's-eye or
hand check found the first version wrong; still before any outcome). Nothing here is the trader's unless marked SOURCED.

The operator's rules (SOURCED, operator chat 2026-10-16, quoted as given to this session):
- O1 "If a daily candle has moved past the opening of the previous daily candle, the stop would be below the previous daily candle. And if it is too much, then it should be refined for 12 hours or 8 hours."
- O2 "Candlestick pattern will also provide you some confidence."
- O3 "If you are jumping out of the lower band of the Bollinger band, then also there could be some confidence. But it is very dangerous to short in the lower band because there could be a Bollinger band dance."
- O4 Support layers for longs and resistance layers for shorts, from Tom, Fabio and other confluence layers. The phase Bitcoin is in matters. "Everything is based on the probability of what happens when ... and this can be measured in the past historical data."

## 0. Decision time, bars, buckets

| item | definition | label |
|---|---|---|
| decision time T | the close of a 1h bar (a whole UTC hour); entry, if any, is after T | OURS |
| input | Binance USD-M BTCUSDT 1m archive aggregated to 5m (`load_dev_5m`), DEV bar open 2022-01-01 .. 2024-06-30; loader and both builds refuse a bar at/after 2024-07-01 | SOURCED split (gross_effect_screen PRE_REG s.6) |
| buckets | UTC epoch buckets: 1h, 4h (00/04/..), 8h (00/08/16), 12h (00/12), D (00:00), W (Monday 00:00) | SOURCED FORMULAS s.8 |
| completed candle at T | a bucket whose end <= T; the bucket containing T is **partial** (empty when T is its start) | SOURCED FORMULAS s.8 (closed bars only) |
| ATR | plain-SMA ATR14 of true range, per timeframe, completed bars | SOURCED FORMULAS s.12 |
| decisions | every DEV hour from 2022-04-01 (90-day warm-up for the volatility percentile) | OURS |
| replay window | the replay reads at most the last 120 days (Monday-aligned) of bars[0..t]; every lookback below fits inside it (replay == vectorised on all rows proves it) | OURS |

## 1. Level layers (feed F1, F2, F7 sweep)

| layer | levels at T | tags (names) | static/dynamic | label |
|---|---|---|---|---|
| prior_dw | prior completed D high and low; prior completed W high and low | prior_dw | static (created at the bucket end) | OURS selection |
| session | developing UTC-day high and low from bars < T, only once T is >= 4 h into the day | session | dynamic | OURS (angle b fix: traders see today's extremes; angle c fix: not in the first 4 h) |
| pd_va | POC, VAH, VAL of the prior completed D (5m bars, 10 USD bins, 70 % value area) | tom, fabio | static | SOURCED: Tom "prior day/week value" (SETUP_CATALOG.md:340), value area 70 % (FORMULAS 18.1, Tom 1utSjHs_Mq8:19), Fabio FAB-4 "edge of the previous day's value area" (SETUP_CATALOG.md:1228); bins OURS |
| pw_va | POC, VAH, VAL of the prior completed W | tom, vp | static | SOURCED Tom (same row); OURS weekly |
| krown | 4h fractal pivots (n = 2, strict, usable only after bar i+2 closed) whose bar opened in the last 60 days, chained on price when consecutive gaps <= 0.25 x ATR14(D); a zone needs >= 2 pivots; price = mean of its pivots; created = the second confirmation | krown | static | SOURCED ">= 2": "where the price turned at least twice" (Krown, extract_qEfES84jwwo.md:65 via KRW-RANGE-BB-MAP.md:24); fractal FORMULAS 18.2; n, 60 d, 0.25 OURS |
| vwap | session VWAP (hlc3 of 5m bars, UTC day) once >= 4 h into the day; weekly VWAP once >= 1 day into the week | vwap | dynamic | OURS (angle b fix: a 1-hour-old VWAP is just the last hour's mean) |
| round | nearest multiple of 1,000 USDT strictly below and strictly above the close | round | static (touch window 30 days) | OURS |
| bb4h | BB(20) mid of the completed 4h closes | operator | dynamic | OPERATOR idea (OPR-BB-MTF-CENTER draft); OURS timeframe |
| Malkan | none | - | - | DROPPED: the Malkan draft searched "support"/"resistance" in his six transcripts (MAL-BB-RSI-4060.md:35) and lists no price-level rule; his 40/60 are RSI levels, not prices |

Same price in two layers: ties go by the layer order above. pd_va and pw_va carry two names each: the same computed
price is "Tom" and "Fabio" (or "Tom" and "VP"), which matters for F2 (two confluence counts, below).

## F1 Side-aware levels

- **Definition.** Long at T: supports = all layer levels strictly below the close c_T. Short: resistances strictly above.
  A level flips role only when a completed 1h close is on the other side of it (c_T is that close, so a wick through
  does not flip it). Nearest = highest support / lowest resistance; `f1_dist_atr` = distance / ATR14(1h);
  `f1_at_level` = distance <= 1.0 ATR14(1h).
- **Variant (angle e).** Role needs the 1h close AND the last completed 4h close on the same side (levels between them are
  "contested" and excluded): `f1_n_levels_v4h`.
- **Trap.** Assigning the role with a later close (the level that "held" in hindsight). **Test:** planted leak
  `f1_future_close` (role from the next 1h close) fails truncation invariance (`test_planted_leak_is_caught`).
- **Trader sees.** "Below me: yesterday's VAL at X, today's low at Y, 30,000 round; above me: yesterday's high."

| parameter | value | label |
|---|---|---|
| role flip | 1h close through | OURS (variant: + 4h close) |
| at a level | 1.0 x ATR14(1h) | OURS |

## F2 Confluence and level quality

- **Definition.** Zone = nearest level +- 0.5 x ATR14(1h), same side only. `f2_conf_obj` = number of distinct layers in the
  zone (CHOSEN); `f2_conf_name` = number of distinct names (Tom and Fabio counted separately). Quality of the nearest
  level: `f2_age_h` (hours since created; NaN for round/dynamic), `f2_touches` = completed 1h bars since creation (round:
  last 720 h) whose range contains the level, including the bar ending at T; `f2_touch_cat` untested (0) / first (1) /
  retest (>= 2) / dynamic.
- **Why layers, not names (angle e).** pd_va is one computation that both Tom and Fabio use; counting names makes every
  prior-day VA level "2 traders agree" by construction (5,457 vs 4,532 events with >= 2, trials.csv).
- **Trap.** Counting touches after T. **Test:** planted leak `f2_future_touches` (touches over the whole future) is caught.

| parameter | value | label |
|---|---|---|
| zone half-width | 0.5 x ATR14(1h) | OURS |
| round touch window | 720 h | OURS |

## F3 The operator's daily-candle stop ladder

- **Definition.** Prior D = last completed D (o, h, l). `f3_armed` (rule O1 condition) = long: c_T > prior D open; short:
  c_T < prior D open. Stop candidates (no buffer): long below the low, short above the high, of the prior completed D,
  then the last completed 12h, then the last completed 8h; width w in % of c_T (NaN if on the wrong side of price).
  Ladder (O1 "if it is too much, refine"): take D if W_min <= w_D <= W_max; if w_D > W_max go to 12h, then 8h, same test;
  if a width is below W_min or invalid, stop there with **no stop** (`f3_stop_tf = none`). `f3_cost_R` = 0.14 / w.
- **W_min = 0.56 %** = cost 0.14 % / 0.25 R: a stop whose round-trip cost exceeds 0.25 R is not taken (OURS 0.25; cost
  SOURCED). **W_max = 1.0 x ATR14(D) in % of price** ("too much" = wider than a typical day's range; OURS; variant fixed
  3.0 % in trials.csv: 5,743 vs 5,598 events with a stop).
- **Angle b fix.** The first version also descended when the D stop was too *tight*, which picked a wider 8h extreme
  (2022-08-23 21:00 short: D 0.37 % -> 8h 0.92 %). O1 refines a stop that is too wide, so it now stops at "none".
- **Armed variant (angle e).** Partial-day extreme past the prior D open (`f3_armed_B`): 5,196 vs 3,795 armed events.
- **Trap.** Using the current day's final OHLC as "the previous daily candle". **Test:** `f3_final_day` caught.
- **Trader sees.** "Today has already traded above yesterday's open, so my long stop goes under yesterday's low at X
  (Y % away); that is more than a day's range, so I use the 12h low instead."

## F4 Candle patterns (completed candles only; D, 12h, 8h, 4h)

| pattern | definition on the last completed candle (0) and the one before (1) | label |
|---|---|---|
| bull_engulf / bear_engulf | colours flip and the close passes the previous open (bull: prev red, cur green, c0 > o1) | OPERATOR (MAL-BB-MID-ENGULF.md M2, close below the previous green open; mirrored); Malkan names "a bearish engulfing" at sell signals (Q8, extract_2HcJ3NeZmEQ.md:84) |
| outside / inside | h0 > h1 and l0 < l1 / h0 <= h1 and l0 >= l1 | SOURCED concept Tom TOM-15 (SETUP_CATALOG.md:1000-1002); OURS strictness |
| pin_bull / pin_bear | lower (upper) wick >= 0.6 x range and body <= 0.3 x range | OURS; Malkan names a "shooting star" (Q8) |
| three_up / three_down | three same-colour candles | SOURCED concept Tom TOM-15 "three in a line" |
| doji | body <= 0.1 x range | OURS |

Priority when several hold: engulf, outside, inside, pin, three, doji, none. `f4_<tf>_align` = with (bull_engulf or
pin_bull for a long; mirrored), against, none. Classic body engulf kept as `f4_<tf>_eng_cls` (variant).
- **Angle b fix (engulf).** On 24/7 BTC a candle opens 0.1-4.4 USD away from the previous close in 449 of 911 DEV daily
  candles (2,742 of 5,471 4h candles). The classic rule "open at/below the previous close" is then decided by tick noise,
  so the operator's close-past-open rule is CHOSEN (977 vs 716 D engulfs on the trade side, trials.csv).
- **Trap.** Reading the pattern on the candle that is still forming. **Test:** `f4_partial_candle` caught.
- **Trader sees.** "Yesterday was a bullish engulf; the last 8h candle is a hammer."

## F5 Bollinger state (1h and 4h, completed bars)

- **Definition.** BB(20, 2 population SD) on completed closes; bandwidth bw = (up - lo) / mid. At the last completed bar j:
  walk_lower = the last 3 closes at/below the lower band AND bw_j > bw_{j-3}; break_lower = close at/below the lower band
  (not a walk); reenter_lower = close back above after a close at/below at j-1; mirrored upper; else inside.
  `f5_conf` = long with reenter_lower (O3 "jumping out of the lower band ... confidence"), short with reenter_upper.
  `f5_veto` = short while the 1h state is walk_lower (as the session prompt defines it), long while walk_upper (OURS mirror).
- **Conflict found (report).** The operator's "dance" is NOT a walk: in his own words the price "takes support at this
  lower band, and price is bought up, and then again it just bounces between the lower and the center line"
  (MAL-BB-RSI-4060.md:106). His warning (O3) is about shorting into that bounce; a walk (Bollinger rule 8 continuation)
  is where a short is *not* dangerous. Both readings are counted (trials.csv: prompt veto vs any lower-band state).
- **Parameters.** 20/2 SOURCED (bollinger_2026-10-14/SOURCES.md:10, [1]); N = 3 closes OURS on a T3 habit (SOURCES.md:9);
  cushion %b <= 0.05 variant OURS (SOURCES.md:9: "any cushion ... would be our own choice").
- **Trap.** Bands that include a bar the trader has not seen close. **Test:** `f5_next_bar` caught.
- **Trader sees.** "Three 1h closes under the lower band and the bands are opening: that is a walk, I do not short into it"
  or "price just closed back inside the lower band".

## F6 Bitcoin phase (closed bars only)

| definition | rule | label |
|---|---|---|
| A (CHOSEN) | completed weekly close vs SMA10 of weekly closes, slope = SMA10 now minus 2 weeks earlier: above & rising = markup, above & not rising = distribution, below & falling = markdown, below & not falling = accumulation | OURS (Weinstein-style; operator: "the phase matters") |
| B (variant) | completed daily: 30-day return >= +7.5 % markup, <= -7.5 % markdown (tom_bt.trend_tag, tom_bt.py:270), else position in the 90-day high-low range: top third distribution, bottom third accumulation, else balance | SOURCED threshold (tom_bt default), OURS range rule |
| intraday | Kaufman efficiency ratio of the last 24 1h closes >= 0.3: trend_up/trend_down by sign, else balance | OURS |

Why A: B's trend part IS the `trend` key of the context_null baseline (`context_null.py` imports `tom_bt.trend_tag`),
so a B-phase effect would be matched away by construction. Chosen before any count. A and B agree on only 45.7 % of
the DEV decision events (crosstab in ANGLES.md): "phase" is not one thing. **Trap.** Using the current week's final
close. **Test:** `f6_final_week` caught.

## F7 Additions (kept / dropped)

| factor | definition at T | label | kept? |
|---|---|---|---|
| f7_volreg | ATR14(1h)/close vs the previous 2,160 1h values: share below; < 1/3 low, < 2/3 mid, else high | OURS | kept; collides with the null's `vol` key (match it off when testing it) |
| f7_squeeze | 4h bandwidth vs the previous 180 4h values: share below <= 0.2 = squeeze | OURS | kept |
| f7_session | hour of the decision bar: asia 00-08, london 08-13, ny 13-21, late 21-24 UTC | OURS | kept; collides with the null's `hour` key |
| f7_weekend | Saturday/Sunday UTC | OURS | kept |
| f7_approach | move over the last 3 1h closes toward the level, in ATR14(1h): >= 1.5 fast, > 0 slow, else away | OURS | kept |
| f7_sweep | a same-side level lies inside the last 1h bar's wick (long: low < L) after a close beyond it the bar before, and c_T is back on the right side | OURS (Krown R5 "close back inside" concept, KRW-RANGE-BB-MAP.md R5) | kept |
| f7_htf_align | count of {D close vs SMA20(D), 4h close vs SMA20(4h)} on the trade side: 0/1/2 | OURS | kept |
| f7_funding | last settled 8h funding before T: neg / low (< 0.01 %) / base (0.01 %) / high | SOURCED base 0.01 % (archive) | kept |
| open interest | - | - | DROPPED: metrics archive starts 2025-09 (gross_effect_screen PRE_REG s.2) |
| liquidations, news | - | - | DROPPED: no DEV data, no timestamps |
| footprint / delta at the level | - | - | DROPPED from this task: klines carry only bar-level taker volume; covered by other studies |

**Traps.** Full-sample percentile ranks (`f7_fullsample_vol`, caught) and pivots used before their right-hand bars close
(`f7_krown_unconfirmed`, caught).

## Tests (all in `test_context_asof.py`)
- `test_replay_equals_vectorised`: >= 40 decision hours on a 110-day synthetic tape with gaps, both sides, every key.
- `test_truncation_invariance_clean`: the vectorised row at T from bars[0..t] equals the one from bars[0..t+2100].
- `test_planted_leak_is_caught[...]`: eight planted leaks (one per factor + two for F7); each changes the leaky build and
  is detected by the truncation test, while the clean build passes at the same hours.
- Hand values: candle patterns (incl. the 0.1-tick engulf case), Krown chaining, BB state, phase A map, W_min = 0.56 %.
- Real DEV data: replay == vectorised on all 39,458 rows and the boundary truncation check (redteam.py R1) are in ANGLES.md.
