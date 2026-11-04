# Wall ledger (offline) - RESULT 2026-11-05

Card: wall-ledger-for-the-live-dashboard-place. Result: `wall_ledger.py` builds a placed / pulled / filled
ledger from depth snapshots; 15/15 hand-derived tests pass; 4/4 scratch mutations (threshold `>`, filled/pulled
swap, persistence off, cell edge inclusive) each fail at least one test. No real-data rate yet (needs recorded
depth: separate run card). No live wiring, no order path.

## Rule
- Cell: price floored to the grid; cell value = sum(price x qty) of the side's levels inside the cell.
- Candidate: a cell with value >= threshold.
- Placed: a candidate present in PERSIST consecutive snapshots; placed_ts = first snapshot it was seen.
- Touched: best bid, best ask or any trade print inside the cell while the wall rested (including the snapshot it vanished).
- Filled: the cell dropped below threshold and trade volume printed inside the cell during its life.
- Pulled: the cell dropped below threshold with no trade volume inside it.
- Pulled before touch: pulled and never touched. Rate = pulled_before_touch / (pulled + filled); open walls excluded.
- A dip below threshold closes the wall; reappearing starts a new row (repeated rows at one level = the FAQ's spoof signature).

## Parameters
| Name | Value | Label | Source |
|---|---|---|---|
| THRESHOLD_USD | 1,500,000 per cell | OURS (adopted) | CoinGlass BTC wall minimum, SOURCED in FIELD_GUIDE.md "Wall" row |
| GRID_USD | 10 | OURS (adopted) | CoinGlass BTC default row size, FIELD_GUIDE.md "Price grid" row |
| PERSIST | 3 snapshots | OURS | CoinGlass says only "persist across consecutive updates" |

## Ledger schema (one row per wall life)
| Field | Meaning |
|---|---|
| side | bid / ask |
| level | cell floor price |
| placed_ts | ts of first snapshot over threshold |
| end_ts | ts of the snapshot it vanished (None while open) |
| outcome | open / pulled / filled |
| max_usd | largest cell value seen |
| distance_pct | (level - mid) / mid x 100 at placed_ts |
| age_s | end_ts (or last snapshot ts) - placed_ts |
| touched | bool, see rule |

`summary(rows)` returns placed, open, pulled, filled, pulled_before_touch, pulled_before_touch_rate.

## Reference number (not ours)
CoinGlass Wall events 11-01, about 2 days: 191 placed, 1 filled, 176 pulled (FIELD_GUIDE.md, SEEN). Our own rate
comes from the run card on recorded Binance depth.
