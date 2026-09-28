# TEST_PLAN.md — cryptocred layer (cc_structure, cc_retest, cc_setups)

Hand-computed expected values per each module's spec (Dumps/workers/NUC-QUEUE/specs/060/061/062).
Bars use flat candles (o=c=h=l) unless stated otherwise, so body_high/body_low == h/l == o == c.
`t` is taken equal to bar index for readability. A Haiku worker should turn each case below into a
`unittest` method against the real module once built; do not re-derive expected values, use these.

## cc_structure.py

### Case S1 — find_swings, use_body=True, left=1, right=1
bars (o=c=value): idx0=80, idx1=100, idx2=70, idx3=60, idx4=90, idx5=95, idx6=75, idx7=98, idx8=99
Checked indices 1..7 (left=1 .. len-1-right=7).
Expected `find_swings(bars, left=1, right=1, use_body=True)`:
```
[{"i":1,"t":1,"price":100,"kind":"high","confirmed_i":2},
 {"i":3,"t":3,"price":60, "kind":"low", "confirmed_i":4},
 {"i":5,"t":5,"price":95, "kind":"high","confirmed_i":6},
 {"i":6,"t":6,"price":75, "kind":"low", "confirmed_i":7}]
```
(idx2, idx4, idx7 are ties/non-extrema against both neighbors and produce no swing.)

### Case S2 — find_swings, use_body=False (uses h/l, not o/c)
bars: idx0 h=11,l=9; idx1 h=14,l=7; idx2 h=10,l=6; idx3 h=16,l=5; idx4 h=9,l=3 (o=c=midpoint, irrelevant)
left=1,right=1, checked indices 1..3.
Expected: `[{"i":1,"t":1,"price":14,"kind":"high","confirmed_i":2}, {"i":3,"t":3,"price":16,"kind":"high","confirmed_i":4}]`
No swing lows: idx1 l=7 vs neighbors l=9,l=6 → 7<9 true but 7<6 false, fails. idx2 l=6 vs l=7,l=5 → 6<7 true, 6<5 false, fails.

### Case S3 — find_swings raises on bad params
`find_swings(bars, left=0, right=1)` -> raises `ValueError`.

### Case S4 — is_range_extreme, too few lookback bars
bars: idx0 h=10,l=8; idx1 h=12,l=9 (only these two exist before idx1... use i=1: window=bars[max(0,1-3):1]=bars[0:1], only 1 bar).
`is_range_extreme(bars, i=1, lookback=3, extreme_pct=0.25)` -> `False` (fewer than 2 bars in window).

### Case S5 — is_range_extreme, True at top and bottom of range
bars: idx0 h=10,l=8; idx1 h=12,l=9; idx2 h=11,l=7,c=8.0; idx3 h=12,l=11,c=11.8; idx4 h=8.5,l=8,c=8.2
`is_range_extreme(bars, i=3, lookback=3, extreme_pct=0.25)`: window=bars[0:3], range_hi=12, range_lo=7, span=5, top_thresh=12-1.25=10.75, bot_thresh=7+1.25=8.25. c=11.8 >= 10.75 -> `True`.
`is_range_extreme(bars, i=4, lookback=3, extreme_pct=0.25)`: window=bars[1:4], range_hi=max(12,11,12)=12, range_lo=min(9,7,11)=7, span=5, thresholds same 10.75/8.25. c=8.2 <= 8.25 -> `True`.

### Case S6 — classify_msb, default require_prior_sequence=True (bull MSB found, no bear MSB)
Use bars from Case S1 (idx0..idx8, with idx8=99 added), swings from Case S1's result.
swing_highs=[100@i1, 95@i5]: 95<100 -> "lower high" satisfied. Scan bars with index > max(5,6)=6: idx7 close=98>95 -> confirm at k=7.
Expected one event: `{"t":7,"i":7,"direction":"bull","broken_level":95,"broken_swing_i":5,"confirm_i":7,"at_range_extreme":True}`.
(at_range_extreme: window=bars[0:7], range_hi=100, range_lo=60, span=40, top_thresh=100-10=90; c7=98>=90 -> True.)
swing_lows=[60@i3, 75@i6]: 75>60 -> "higher low" satisfied. Scan index>7: idx8=99, close<75? No -> no bear event.
So `classify_msb(bars, swings)` returns exactly the one bull event above.

### Case S7 — classify_msb, require_prior_sequence=False includes a higher-high pair
bars: idx0=70, idx1=80, idx2=65, idx3=90, idx4=60, idx5=95 (o=c=value, left=1,right=1)
swings: `[{"i":1,"price":80,"kind":"high","confirmed_i":2}, {"i":2,"price":65,"kind":"low","confirmed_i":3}, {"i":3,"price":90,"kind":"high","confirmed_i":4}, {"i":4,"price":60,"kind":"low","confirmed_i":5}]`
swing_highs pair (80@i1, 90@i3): 90<80 is False -> NOT a lower-high.
`classify_msb(bars, swings, require_prior_sequence=True)` -> `[]` (no bull event; only one high pair, and low pair 65@i2/60@i4 similarly is not a "higher low" since 60>65 is False, so no bear event either).
`classify_msb(bars, swings, require_prior_sequence=False)` -> scan index > max(3,4)=4: idx5 close=95>90 -> bull event `{"t":5,"i":5,"direction":"bull","broken_level":90,"broken_swing_i":3,"confirm_i":5,"at_range_extreme": <compute per S4/S5 method, window=bars[0:5], range_hi=90,range_lo=60,span=30,top_thresh=90-7.5=82.5, c5=95>=82.5 -> True>}`.

## cc_retest.py

### Case R1 — bull retest found, immediate
msb_event = {"direction":"bull","broken_level":100,"confirm_i":2, ...}. tolerance_pct=0.001, invalidate_pct=0.005, expiry_bars=5.
bars (index 3..7): idx3 l=105,c=106; idx4 l=100.05,c=101; idx5 l=110,c=108 ...
Scan: idx3 l=105 > 100*1.001=100.1 -> no touch; c=106 >= 100*0.995=99.5 -> not invalidated.
idx4 l=100.05 <= 100.1 -> touch. `find_retest(...)` -> `{"t":4,"i":4,"level":100,"bars_since_break":2}`.
`classify_retest_timing(retest, immediate_bars=5)` -> `"immediate"` (2<=5).
`classify_retest_timing(retest, immediate_bars=1)` -> `"rounded"` (2>1).

### Case R2 — bull retest invalidated before touch -> None
Same msb_event. bars: idx3 l=105,c=99 (c=99 < 100*0.995=99.5 -> invalidated at k=3, before any touch); idx4 l=100.05,c=101 (would be a touch but invalidation already happened at an earlier bar).
`find_retest(...)` -> `None`.

### Case R3 — no touch, no invalidation, expires -> None
bars idx3..idx7 all l=110, c=105 (never touches <=100.1, never closes <99.5).
`find_retest(bars, msb_event, tolerance_pct=0.001, invalidate_pct=0.005, expiry_bars=5)` -> `None`.

### Case R4 — bear retest found
msb_event = {"direction":"bear","broken_level":50,"confirm_i":2,...}. tolerance_pct=0.001, invalidate_pct=0.005.
bars: idx3 h=48,c=49 (h < 50*0.999=49.95 -> no touch; c=49 <= 50*1.005=50.25 -> not invalidated); idx4 h=49.97,c=49.5 (h>=49.95 -> touch).
`find_retest(...)` -> `{"t":4,"i":4,"level":50,"bars_since_break":2}`.

### Case R5 — invalid params raise
`find_retest(bars, msb_event, tolerance_pct=0)` -> raises `ValueError`.
`classify_retest_timing(retest, immediate_bars=0)` -> raises `ValueError`.

## cc_setups.py

### Case U1 — setup1_sr_flip, bull
msb_event bull with broken_level=95; retest found at t=10. stop_buffer_pct=0.001, target_r=1.5.
entry_price=95, stop=95*(1-0.001)=94.905, target=95+1.5*(95-94.905)=95+0.1425=95.1425.
Expected signal: `{"side":"long","entry_price":95,"entry_t":10,"stop":94.905,"targets":[(95.1425,1.0)],"meta":{"setup":"sr_flip","rule_id":"C10-E01","msb_i":5,"target_r":1.5}}`.

### Case U2 — setup1_sr_flip, bear
msb_event bear with broken_level=50; retest at t=10. stop_buffer_pct=0.001, target_r=1.5.
entry_price=50, stop=50*(1.001)=50.05, target=50-1.5*(50.05-50)=50-0.075=49.925.
Expected: `{"side":"short","entry_price":50,"entry_t":10,"stop":50.05,"targets":[(49.925,1.0)],"meta":{"setup":"sr_flip","rule_id":"C10-E01","msb_i":<i>,"target_r":1.5}}`.

### Case U3 — setup1_sr_flip, no retest -> skipped
`find_retest` returns `None` for the msb_event -> `setup1_sr_flip` must emit no signal for that event.

### Case U4 — setup2_fib_pullback, bull
Impulse leg P_low=60 (earlier swing low) to H=100 (later swing high). fib_lo=0.618, fib_hi=0.786.
zone = [100 - 0.786*40, 100 - 0.618*40] = [100-31.44, 100-24.72] = [68.56, 75.28].
entry_price = 75.28 (near/top edge), stop = 68.56*(1-0.001) = 68.49144, target_r=1.5.
target = 75.28 + 1.5*(75.28-68.49144) = 75.28 + 10.18284 = 85.46284.
Expected signal fields: `entry_price=75.28, stop=68.49144, targets=[(85.46284,1.0)]`.

### Case U5 — setup3_failed_msb_reversal, bull MSB fails
broken_level=95 confirmed at c=7, post-break high (max h over [i5..i7]) = 98. failure_lookback=2 -> window=bars[8:10].
idx8 h=96 (<=98, no new high), idx9 h=94, c=93 (< broken_level 95 -> failed). stop_buffer_pct=0.001, target_r=2.0 (default, counter-trend per C10-E02).
entry_price=93 (close of last window bar), stop=95*(1.001)=95.095, side="short".
target = 93 - 2.0*(95.095-93) = 93 - 4.19 = 88.81.
Expected: `{"side":"short","entry_price":93,"entry_t":9,"stop":95.095,"targets":[(88.81,1.0)],"meta":{"setup":"failed_msb_reversal","rule_id":"C10-E05","msb_i":7,"target_r":2.0}}`.

### Case U6 — setup3, not enough bars to evaluate -> skipped
If `len(bars) - 1 < c + failure_lookback` for a given msb_event, that event produces no signal (not a failure, not a continuation — undetermined).
