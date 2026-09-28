# TEST_PLAN.md — rsi layer (rsi_core, rsi_ma, rsi_events, malkan_40_60)

Hand-computed / Python-scratch-verified expected values per the specs (Dumps/workers/NUC-QUEUE/specs/
071/072/073). Values were computed with a standalone Python scratch implementing the definitions in
`MyTradingSys/backtest/layers/FORMULAS.md` (sections 1-6), NOT by importing or reading `bt_rsi.py.new`
or any future layer module. A Haiku worker should turn each case into a `unittest` method against the
real module once built; do not re-derive expected values, use these.

Malkan source: `MyTradingSys/research/malkan_rsi_2026-09-28/WEB_RESEARCH.md` is the only Malkan extract
that exists on disk (the path named in the work order, `extracts/processed/malkan_rsi_2026-09-28`, does
not exist — see report). That file has no publisher rule-id table (unlike the CryptoCred/Tom extracts),
so this TEST_PLAN assigns local ids citing exact line ranges:
- **MLK-R1** (regime / range-shift): WEB_RESEARCH.md lines 39-62, 84-89. Quote: "Whenever the market is
  bearish, it won't be able to cross 60 (in RSI). Whenever in a bullish trend, it won't be able to cross 40."
- **MLK-S1** (bullish 5-star entry, daily RSI touches 40 and bounces): lines 108-134. Quote: "Bullish
  candlestick forms at 40 RSI level on daily chart = buy signal."
- **MLK-S2** (bearish 5-star entry, daily RSI touches 60 and rejects): lines 135-159. Quote: "Bearish
  candlestick forms at 60 RSI level on daily chart = short signal."
- **MLK-GAP1**: the full 5-star setup is multi-timeframe (Monthly/Weekly gate + Daily entry, lines
  99-134); 070-075 builds a single-timeframe module only (D7). `malkan_40_60`'s setup functions here
  implement MLK-S1/S2's entry mechanics (regime + 40/60 bounce/reject + entry candle color) on ONE
  timeframe; the multi-timeframe grandfather-father-son gate is out of scope and must be composed later
  by a caller that runs this module once per timeframe and combines the results.

## rsi_core.py

### Case C1 — rsi_wilder (Wilder RSI), period=5, 15 closes
`rsi_core(closes, period=5)` is textbook Wilder (= TradingView ta.rsi; NOT bt_rsi.py.new, which is off) (avg gain/
loss seeded from the first `period` deltas, then Wilder-smoothed: `avg = (avg*(period-1)+x)/period`).
closes = [100,102,101,103,106,105,107,110,108,112,111,113,116,114,118] (index 0..14).
Expected `rsi_core(closes, period=5)` (None before index 5):
```
idx  0-4: None
idx  5: 77.777778
idx  6: 82.608696
idx  7: 87.644788
idx  8: 70.606532
idx  9: 80.21978
idx 10: 72.781223
idx 11: 77.903574
idx 12: 83.666874
idx 13: 68.728457
idx 14: 78.379232
```
(6 significant figures shown; assert with `abs(got-expected) < 1e-4`.)

### Case C2 — invalid params raise
`rsi_core(closes, period=0)` -> raises `ValueError`. `rsi_core(closes, period=20)` with `len(closes)==15`
(`len(closes) <= period`) -> raises `ValueError`.

### Case C3 — default period is 14 (params file check, not a numeric case)
`layers/rsi/params/default.json`'s `rsi_core.period` == 14. This is asserted directly against the JSON
file, not against a computed series.

### Case C4 — isolation rule (D2): rsi_core default params contain no 40 or 60
Load `layers/rsi/params/default.json`; walk every numeric leaf under `rsi_core` and `rsi_ma`; assert none
equals `40` or `60`. (`rsi_events.levels` in that same file is `[70, 50, 30]` — also no 40/60.) This is
the operator's isolation rule from D2, verbatim: "A unit test asserts that rsi_core and rsi_ma default
params contain no 40 or 60 level."

## rsi_ma.py

RSI input series (synthetic, not chained from Case C1 — decoupled on purpose so MA logic is tested
independently of rsi_core): `rsi = [None, None, None, 50.0, 55.0, 45.0, 60.0, 40.0]` (index 0..7),
`length = 3`. A moving-average value at index i requires `length` CONSECUTIVE non-None rsi values ending
at i (i.e. `rsi[i-length+1 : i+1]` all non-None); otherwise None.

### Case M1 — SMA(3)
idx5: window [50,55,45] (idx3,4,5) -> mean = 50.0. idx6: window [55,45,60] -> mean = 53.333333.
idx7: window [45,60,40] -> mean = 48.333333.
`rsi_ma(rsi, type="SMA", length=3)` -> `[None,None,None,None,None,50.0,53.333333,48.333333]`.

### Case M2 — WMA(3), weights 1,2,3 on oldest..newest
idx5: oldest..newest = [50,55,45], weighted = (50*1+55*2+45*3)/6 = 295/6 = 49.166667.
idx6: [55,45,60] -> (55*1+45*2+60*3)/6 = 325/6 = 54.166667.
idx7: [45,60,40] -> (45*1+60*2+40*3)/6 = 285/6 = 47.5.
`rsi_ma(rsi, type="WMA", length=3)` -> `[None,None,None,None,None,49.166667,54.166667,47.5]`.

### Case M3 — EMA(3), alpha=2/(length+1)=0.5, seed = SMA of first `length` available values
Seed at idx5 = SMA([50,55,45]) = 50.0 (same seeding rule as rsi_core's Wilder warm-up: first value is
an SMA seed, not a recursive EMA from index 0). idx6: ema = (60-50)*0.5+50 = 55.0.
idx7: ema = (40-55)*0.5+55 = 47.5.
`rsi_ma(rsi, type="EMA", length=3)` -> `[None,None,None,None,None,50.0,55.0,47.5]`.

### Case M4 — RMA/SMMA(3), alpha=1/length=1/3, seed = SMA of first `length` available values
Seed at idx5 = 50.0. idx6: rma = (60-50)/3+50 = 53.333333. idx7: rma = (40-53.333333)/3+53.333333 = 48.888889.
`rsi_ma(rsi, type="RMA", length=3)` -> `[None,None,None,None,None,50.0,53.333333,48.888889]`.

### Case M5 — default type/length from params file
`layers/rsi/params/default.json`'s `rsi_ma` == `{"type":"SMA","length":14}` (D2/D4 default: "SMA 14").

### Case M6 — invalid type raises
`rsi_ma(rsi, type="XMA", length=3)` -> raises `ValueError`.

## rsi_events.py

Generic level/line interaction detector with a tolerance band. `level = 60`, `tolerance = 2` ->
band = [58, 62]. Classify each non-None bar as `"above"` (rsi > 62), `"below"` (rsi < 58), or `"band"`
(58 <= rsi <= 62, inclusive both ends). Algorithm (single left-to-right pass, `None` entries skipped
without resetting state — this is the mechanical handling for both warm-up bars and mid-series data
gaps, D3's two edge cases "warm-up bars (no RSI yet)" and "first bar after a data gap"):
- Track `prev_side` (side of the last non-band bar seen) and an open "band run" (`run_start`,
  `run_entry_side` = `prev_side` at the moment the run opened, possibly None for the very first bars).
- On entering band from non-band: open a run, remember `run_entry_side`.
- On leaving band to side `S`: if `run_entry_side is None`, emit nothing (undetermined, e.g. the series
  starts inside the band). Else if `S == run_entry_side`: emit `"support"` if `S=="above"` (approached
  from above, dipped into the band, closed back above), `"rejection"` if `S=="below"` (approached from
  below, poked into the band, closed back below). Else (`S != run_entry_side`): emit `"failure"` (the
  band did not hold; price closed through to the other side).
- On a non-band bar immediately following another non-band bar of the OPPOSITE side with no band run in
  between: emit `"cross"` (RSI jumped across the whole band in a single bar without ever registering a
  touch — D3's "RSI jumps across the band inside one bar").
- A band run still open at the end of the series (no exit bar) emits NOTHING (D3's "several bars inside
  the band" with no resolution yet — ambiguous, not reported).
- `penetration` for `support`/`rejection` = max(|v - level|) over the run's band bars (deepest dip into
  the band, always <= tolerance). `penetration` for `failure`/`cross` = |resolution_value - level| (how
  far past the level the resolving/crossing bar closed).
- `t` on every event = the timestamp of the RESOLVING bar (the bar that exits the band, or the crossing
  bar itself for `cross`).

### Case E1 — full walk, level=60, tolerance=2, one series covering every D3 edge case
`rsi` and `t` (t = bar index) for indices 0..25:
```
i:   0    1    2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21   22  23  24  25
rsi: -    -   50  55  59  61  57  56  65  64  61  59  63  63  60  56  55  58  60  60  57   -   59  65  60  61
```
(i=0,1: None = warm-up; i=21: None = a data gap mid-series.)

Walk-through (side classification uses band=[58,62]):
- i2=50(below), i3=55(below), i4=59(band, run_start=4, entry_side=below), i5=61(band, still).
- i6=57(below): run ends, side==entry_side(below) -> **rejection** @ t=6. penetration = max(|59-60|,|61-60|)=1.
- i7=56(below, no run open, prev_side stays below, no cross since same side).
- i8=65(above, prev_side was below at i7, no run open) -> **cross** @ t=8, direction up. penetration=|65-60|=5.
- i9=64(above).
- i10=61(band, run_start=10, entry_side=above), i11=59(band, still).
- i12=63(above): run ends, side==entry_side(above) -> **support** @ t=12. penetration=max(|61-60|,|59-60|)=1.
- i13=63(above).
- i14=60(band, run_start=14, entry_side=above).
- i15=56(below): run ends, side!=entry_side -> **failure** @ t=15. penetration=|56-60|=4.
- i16=55(below).
- i17=58(band, run_start=17, entry_side=below), i18=60(band, exact level, still), i19=60(band, flat on
  level again, still — D3's "RSI flat on the level").
- i20=57(below): run ends, side==entry_side(below) -> **rejection** @ t=20. penetration=max(|58-60|,|60-60|,|60-60|)=2.
- i21=None (data gap): skipped; `prev_side` stays "below" (from i20) across the gap.
- i22=59(band, run_start=22, entry_side=below — carried across the i21 gap per the stated gap rule; this
  is D3's "first bar after a data gap").
- i23=65(above): run ends, side!=entry_side(below) -> **failure** @ t=23. penetration=|65-60|=5.
- i24=60(band, run_start=24, entry_side=above [from i23]), i25=61(band, still) -> series ends with the
  run still open -> NO event for it (D3's "several bars inside the band" with no resolution).

Expected `rsi_events(rsi, ts=list(range(26)), level=60, tolerance=2)` (ascending by t):
```
[{"t":6, "event":"rejection","level_value":60,"tolerance_used":2,"penetration":1},
 {"t":8, "event":"cross",    "level_value":60,"tolerance_used":2,"penetration":5,"direction":"up"},
 {"t":12,"event":"support",  "level_value":60,"tolerance_used":2,"penetration":1},
 {"t":15,"event":"failure",  "level_value":60,"tolerance_used":2,"penetration":4},
 {"t":20,"event":"rejection","level_value":60,"tolerance_used":2,"penetration":2},
 {"t":23,"event":"failure",  "level_value":60,"tolerance_used":2,"penetration":5}]
```
This single series exercises: exact touch (i18/i19 exactly on 60), touch-and-close-back both directions
(support @12, rejection @6/@20), close-through-band failure (@15, @23), a same-bar band-skip (cross @8),
several bars inside the band both resolving (i4-6, i10-12, i14-15, i17-20, i22-23) and NOT resolving
(i24-25 tail), RSI flat on the level (i18-19), warm-up (i0-1, no events, no crash), and a data gap (i21,
state carried through per the documented rule) -- this doubles as the "double and triple touches at the
same level produce separate events" case: 4 support/rejection events plus 2 failures, all at level 60,
none merged into one.

### Case E2 — isolation check on the 40/60 numbers (cross-reference to Case C4)
`rsi_events` itself takes `level`/`tolerance` as plain parameters (it is generic, per D2: "Works on any
level (70/50/30, 40/60) or on the rsi_ma line"), so it is not itself restricted -- the isolation rule
(D2) is about DEFAULT PARAMS FILES, not the function. This test only re-asserts Case C4's params-file
check to document why `rsi_events` has no isolation logic of its own.

### Case E3 — invalid params raise
`rsi_events(rsi, ts, level=60, tolerance=0)` -> raises `ValueError` (tolerance must be > 0, matching
cc_retest's precedent for tolerance_pct).

## malkan_40_60.py

### Case D1 — malkan_regime, lo=40, hi=60, lookback=3 (mirrors bt_rsi.py.new's rsi_regime exactly)
`rsi = [None,None,65,62,58,42,38,45,55,63]` (index 0..9). A regime value at i needs exactly `lookback`
consecutive non-None rsi values ending at i.
```
i=2: window=[65] only 1 value -> None (not enough)
i=3: window=[65,62] only 2 -> None
i=4: window=[58,62,65] min=58,max=65 -> min>=40 and max>=60 -> BULL
i=5: window=[42,58,62] min=42,max=62 -> min>=40 and max>=60 -> BULL
i=6: window=[38,42,58] min=38,max=58 -> min>=40? no. max<=60 and min<=40? 58<=60 and 38<=40 -> BEAR
i=7: window=[45,38,42] min=38,max=45 -> max<=60 and min<=40 -> BEAR
i=8: window=[55,45,38] min=38,max=55 -> max<=60 and min<=40 -> BEAR
i=9: window=[63,55,45] min=45,max=63 -> min>=40 and max>=60 -> BULL
```
`malkan_regime(rsi, lo=40, hi=60, lookback=3)` [MLK-R1] ->
`[None,None,None,None,"BULL","BULL","BEAR","BEAR","BEAR","BULL"]`.

### Case D2 — malkan_regime invalid thresholds/lookback raise
`malkan_regime(rsi, lo=60, hi=40)` -> raises `ValueError` (lo must be < hi). `malkan_regime(rsi, lookback=0)`
-> raises `ValueError`.

### Case D3 — bull setup (MLK-S1): regime BULL + rsi_events "support" @ 40 + bullish entry candle
Bars (o,c only matter for candle color) and rsi at index 12: rsi[12]=39 (band, entering from above,
level=40,tolerance=2 -> band=[38,42]), rsi[11]=44(above), rsi[13]=43(above, run resolves same side "above"
-> **support** event @ t=13 per rsi_events, penetration=|39-40|=1). `regime[13] == "BULL"` (given).
bars[13] = {"o":100,"c":103} (bullish candle, c>o).
`malkan_setup_bull(bars, rsi, regime, level=40, tolerance=2)` [MLK-S1] -> one signal:
`{"t":13,"side":"long","rule_id":"MLK-S1","event":"support","level_value":40,"regime":"BULL"}`.

### Case D4 — bull setup skipped: support event present but regime is not BULL
Same rsi_events "support" @ t=13, but `regime[13] == "RANGE"`.
`malkan_setup_bull(bars, rsi, regime, level=40, tolerance=2)` -> `[]` (regime gate fails, per MLK-S1's
requirement that the setup only fires "when Monthly and Weekly RSI is above 60" -- simplified here, per
MLK-GAP1, to "this timeframe's own regime is BULL").

### Case D5 — bull setup skipped: support event present, regime BULL, but entry candle is bearish
Same as Case D3 but `bars[13] = {"o":103,"c":100}` (c<o, bearish candle).
`malkan_setup_bull(...)` -> `[]` (candle-color gate fails; `require_bullish_candle_for_bull_setup=true`
per `malkan_40_60_default.json`).

### Case D6 — bear setup (MLK-S2): regime BEAR + rsi_events "rejection" @ 60 + bearish entry candle
rsi[20]=61 (band, entering from below, level=60,tolerance=2 -> band=[58,62]), rsi[19]=57(below),
rsi[21]=56(below, resolves same side "below" -> **rejection** @ t=21, penetration=|61-60|=1).
`regime[21] == "BEAR"`. `bars[21] = {"o":50,"c":47}` (bearish candle).
`malkan_setup_bear(bars, rsi, regime, level=60, tolerance=2)` [MLK-S2] -> one signal:
`{"t":21,"side":"short","rule_id":"MLK-S2","event":"rejection","level_value":60,"regime":"BEAR"}`.

### Case D7 — malkan_40_60 default params isolation (cross-reference)
`layers/rsi/params/malkan_40_60_default.json` DOES contain 40 and 60 (`lo`, `hi`) -- this is the ONE
file allowed to, per D2 ("40/60 live ONLY here"). Test asserts the opposite of Case C4: this file's
`malkan_40_60.lo == 40` and `malkan_40_60.hi == 60` are present, while confirming (Case C4) that no OTHER
params file in the repo under `layers/rsi/params/` contains those numbers.
