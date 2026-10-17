# Candle pattern event table - DEV (1h, 4h)

Result: DEV 1h 12,219 pattern rows (doji 2,407 / engulfing 4,136 / inside_bar 4,367 / pin_bar 1,309), 12,195 OK; 4h 3,308 rows (729 / 1,054 / 1,258 / 267), 3,298 OK; every gap or short window is NOT_IN_DATA (1h 24, 4h 10); no rules, no tuning.

## Method
- Source `F:/MTS/data/bigtrade/cache/perp/klines_1h.npz`, DEV = bar open < 2024-07-01 (1719792000000 ms); mask applied to the arrays before bar dicts exist (`event_table.py` `load_dev_npz`); nothing on/after the split read. 4h = four consecutive 1h bars from a 00/04/08/12/16/20 UTC boundary, incomplete buckets skipped.
- Detectors `patterns.py` (closed bars), definitions `MyTradingSys/research/candle_patterns_2026-10-04/PRE_REG_CANDLE_PILOT.md:41-48` (engulf, hammer/inv-hammer pin shape, doji `body<=0.1*rng`), `:56` (inside bar, doji, zero-range never signals).
- Event stamped at the signal bar close (`close_t` = open + bar length); forward path starts at the next bar; MFE/MAE in R, R = signal bar high-low (OURS), entry = signal close, horizon 20 bars (OURS), gross, no costs.
- Side: engulfing/pin bar carry their detector sign; inside bar and doji are non-directional in the module, so side = bar colour (OURS); a flat-close bar has side 0 and is NOT_IN_DATA.
- Gap rule: with `step` set, a forward window with a missing bar or fewer than `horizon` bars is NOT_IN_DATA, never bridged or zero-filled.

## Counts and means (horizon 20, `python .../event_table.py --timeframe 1h|4h`)
| tf | pattern | rows | OK | NOT_IN_DATA | mean MFE R | mean MAE R |
|---|---|---|---|---|---|---|
| 1h | doji | 2407 | 2395 | 12 | 3.906 | 4.064 |
| 1h | engulfing | 4136 | 4132 | 4 | 3.215 | 3.120 |
| 1h | inside_bar | 4367 | 4361 | 6 | 4.203 | 4.217 |
| 1h | pin_bar | 1309 | 1307 | 2 | 3.425 | 3.523 |
| 4h | doji | 729 | 727 | 2 | 4.207 | 3.769 |
| 4h | engulfing | 1054 | 1050 | 4 | 3.304 | 3.320 |
| 4h | inside_bar | 1258 | 1255 | 3 | 5.032 | 4.521 |
| 4h | pin_bar | 267 | 266 | 1 | 3.607 | 3.496 |

MFE and MAE are roughly equal in every cell: the large R values come from small signal-bar ranges (doji/inside bars), not from an edge. Descriptive only.

## Tests
`python -m pytest MyTradingSys/research/layer_lab/candle_pattern_event_table/test_patterns.py -q` -> 11 passed (6 existing + 5 new, written red first: 5 failed before the loader/gap code). `lookahead_lint.py --new`: 0 new hits in this module.

## Defaults taken
Horizon 20, colour-oriented inside bar/doji, 4h MFE/MAE on 4h bars; `dev_split_guard`/`forward_excursion` helpers not imported (the module's own mask and excursion code already do this and are tested). No CSV written.
