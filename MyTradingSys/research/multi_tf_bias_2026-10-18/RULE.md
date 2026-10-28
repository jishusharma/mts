# Multi-TF bias stack: the one written rule (written before study.py ran)

Operator 2026-10-18: the read flips by timeframe. This is ONE fixed stack. HTF (1D) sets location, LTF (1h) sets timing.
All thresholds are OURS (chosen here, DEV only, frozen before the run). Wording of the two setups is only from
`setup_catalog_2026-10-15/SETUP_CATALOG.md`: TOM-2 (SOURCED, line 46: "short trades up here and long trades down here" in balance)
and TOM-7 (SOURCED, line 50: shorts at the top and longs at the bottom of ranges around VWAP). No trade advice: this is a labelling rule.

## Inputs per TF (as-of the decision time t, completed bars only)
| TF | used for | N (bars, OURS) |
|---|---|---|
| 1D | state, range location, direction (sets location) | 20 |
| 12h, 8h | state + direction, veto only | 20 |
| 4h | state, range location, direction (second range, TOM-7) | 20 |
| 1h | flow sign (sets timing) | last completed bar |

* state: efficiency ER = |c[-1]-c[-N]| / sum|c[i]-c[i-1]| over the last N closes. ER >= 0.30 (OURS) = IMB (imbalance/trend), else BAL (balance).
* dir: sign(c[-1]-c[-N]).
* location: pos = (c[-1]-low_N)/(high_N-low_N). HIGH if pos >= 0.85, LOW if pos <= 0.15 (OURS), else MID.
* flow sign: sign of taker delta of the last completed bar = 2*taker_buy_vol - vol (FORMULAS.md s.14); 0 = no flow.
* every TF bar (OHLC, volume, VWAP) is built from the 1m bars; VWAP = sum(typical_1m*vol)/sum(vol), typical=(h+l+c)/3, so it is the same number whichever TF path sums it.

## Output table (first matching row wins)
| # | 1D state | 1D location | other TFs | 1h flow | bias |
|---|---|---|---|---|---|
| 1 | IMB | any | none of 4h/8h/12h is IMB with a direction opposite to 1D | = 1D dir | LONG if dir up, SHORT if dir down (trend continuation) |
| 2 | IMB | any | otherwise (a TF disagrees) or flow differs | any | NO BIAS |
| 3 | BAL | HIGH | - | negative | SHORT (failed-auction watch at the HTF edge, TOM-2) |
| 4 | BAL | LOW | - | positive | LONG (failed-auction watch, TOM-2) |
| 5 | BAL | HIGH or LOW | flow not as above | any | NO BIAS (the lower-TF move is still going) |
| 6 | BAL | MID | 4h location HIGH | negative | SHORT (TOM-7 scalp at the top of the range) |
| 7 | BAL | MID | 4h location LOW | positive | LONG (TOM-7) |
| 8 | BAL | MID | otherwise | any | NO BIAS |

Any missing TF (not enough complete history), or 1h flow 0, gives NO BIAS.

## Test design (DEV only)
BTCUSDT perp 1m klines `F:/MTS/data/tom_raw/klines`, bars opening 2022-01-01..2024-06-30 (DEV cut 2024-07-01 SOURCED layer_lab/LAB_BLOCKED_2026-10-17.md:17; the loader keeps no 1m open >= the cut).
Decision every 4h on the UTC boundary (OURS); entry = open of the 1m bar at t, exit = open of the 1m bar at t+8h (OURS); net = side*return - 12 bps round trip (same as session_flow_context report).
Arms: STACK, 1h-only (side = sign of the last 1h bar delta), 1D-only (side = sign of the last 1D bar delta), ALL-LONG reference. 4 trial rows. Day-clustered SE.
