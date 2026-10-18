# Tom DAX naked-chart cross-check (2026-10-18, text only)

Question: do the levels and concepts Tom draws on his DAX charts match what we extracted and encoded for BTC? Sources: only repo files
(no DAX data, no backtest, no holdout day read). The "naked chart" reading = what he draws and says, not what an engine computes.

## 1. Levels he draws on DAX (TOM_TRADE_LEDGER.csv, entry/stop/target, FDAX points)
Computed from the ledger rows (entry, stop, target), one per canonical trade; `T4` is the one long (gap pullback).
| Trade | Stop (pts) | Target (pts) | Target/stop | Stop % of price |
|---|---|---|---|---|
| T1 | 4 (initial, later moved; ledger shows 24485) | 59 | 14.8 | 0.016 |
| T2 | 20 | 122 | 6.1 | 0.079 |
| T2b | 22 | 142 | 6.5 | 0.087 |
| T3 | 36 | 118 | 3.3 | 0.149 |
| T3b | 20 | 105 | 5.2 | 0.083 |
| T4 (long) | 30 | 75 | 2.5 | 0.126 |
| T5 | 63 | 506 | 8.0 | 0.255 |
| T11 | 46 | 158 | 3.4 | 0.174 |
| T12 | 23 | 142 | 6.2 | 0.092 |
Reading: his stops are 0.02-0.26 % of price (median 0.09 %) with targets 2.5-15 times the stop. The BTC fee floor is a stop of at least
0.40 % (taker legs) or 0.20 % (maker entry) (TOM_ON_BTC.md section 1, spec section 11). So the same drawn structure on BTC needs a stop
2-5 times wider in percent; his DAX stop is a level, its width an output, and on BTC that output is below the fee floor in 8 of 9 rows
(only T5, 0.255 %, clears the 0.20 % maker floor; none clears 0.40 %).

## 2. Concepts: DAX drawn/said vs BTC extraction
Match = same concept, same observable on both. Source ids are in the spec, TOM_ON_BTC.md section 2 and zone_identification_rules.md.
| Concept he uses on DAX | In the BTC extraction? | Cross-check |
|---|---|---|
| Idea: oversized impulse leg from the session start (A-C1) | yes (rank vs prior sessions) | Match on concept. DAX has a real auction open (07:00 pre-market, 09:00 cash); BTC has none: the "open" is an OURS choice (TOM_ON_BTC.md section 3 item 6). The only concept that does not transfer as is |
| Above the prior day / week value (A-C2) | yes, range form | Match. Coded stricter than his words on both feeds (prior day HIGH, RECALL_DAX_V2.md:40-41) |
| Thin top, volume below (A-C3) | now coded (SpikeFadeProfile, 2026-10-18) | Match on BTC. DAX CFD volume cannot be compared to his FDAX histogram (shape parity NOT_IN_DATA, PROFILE_PARITY.md); his drawn histogram is the only DAX evidence |
| P shape with failed breakout; lower b shape (A-P3, A-P8) | now coded | Same as A-C3: transfer is by shape, not by price |
| Prior-day high / pre-market high ledge (A-P5) | yes | Match: both are plain OHLC levels |
| Entry at the session extreme (A1), pullback (A2), range break (A3) | yes | Match: the entry is a drawn level on both feeds |
| Stop above the seller / above the bell (a level) | yes (A-S1, A-S2 20 points) | Level concept matches; the 20-point DAX fallback (his T2: 20 pts) is a distance and has no BTC equal. BTC stop = a level with a 0.40 % floor |
| Target = start of the impulse, first node / VPOC | yes (A-T1) | Match. Ratio on DAX 2.5-15x; BTC at a 0.40 % stop needs a leg of 1 %+ to give the same 2.5x |
| Partials, stop to no-loss, one re-entry (A-M3..M5) | re-entry coded; partials and no-loss NEVER (TOM_ON_BTC.md section 2.4) | Gap on both feeds, shown in his rows T1-p1, T2b-p1/p2, T12-m1 |
| Finished auction, selling surplus (A-P1, A-P6) | BTC only (aggressor data) | One-sided: DAX CFD has none (delta forced to 0, dax_data.py:100-106). His footprint evidence is what the chart lab (TOM_ON_BTC.md T2-T3) can read on BTC and not on DAX |
| Gap close long (T4) | no (spec section 4 parked) | Does not transfer: BTC has no gaps (operator 2026-10-11) |
| Other markets not confirming, retail sentiment (A-C4, A-P10) | BTC yes (ETH, long/short ratios), DAX NOT_IN_DATA | One-sided in BTC's favour |
Also on his non-DAX charts: T7 (ES) and T8 (gold) use the same fade structure, so the concept is not DAX-only; that is the one text-only
cross-market support in the ledger (two rows, one candidate, no fills: not a count).

## 3. Verdict (text only, no number tested)
- Concepts transfer: of the 12 table rows, 8 match on both feeds, 1 is a gap on both (partials, no-loss), 2 are one-sided by data (A-P1/P6, A-C4/P10), 1 does not transfer (gap close).
- Prices do not transfer: his stop widths are below the BTC fee floor in 8 of 9 rows, so any BTC edge must come from a wider-level version
  of the same structure, not his sizes. This is already the position of spec section 11; the table above is the ledger evidence for it.
- Nothing here needs DAX data, a backtest or a purchase. Nothing was read from any date on or after 2026-04-11.
- Open point, not done: whether the BTC "open" should be 00:00 UTC, the London or the US cash open (OURS, TOM_ON_BTC.md section 3 item 6).
