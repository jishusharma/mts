# RESULT: BTC order-flow map, assembled (cards btc-native-orderflow-map-1112 + btc-of-level-auction B1), DEV only

Regime mix: clocks 851 DEV days bull 35% / bear 16% / range 42% / n/a 7%; A3 funding 819 events bull 283 / bear 127 / range 344 / n/a 65; A2 170 events bull 51 / bear 10 / range 103 / n/a 6; B1 at level 524 events bull 135 / bear 31 / range 344 / n/a 14 (regime cuts differ by family, OURS; copied from CLOCKS.md, EVENTS.md, B1.md). No per-regime cell passes the fee, so no verdict depends on regime.

DEV = 2022-02-01 .. 2024-05-31. VALIDATION/GAP/RESERVE/HOLDOUT never opened. Fee 10 bp round trip (fees.py). Nothing re-run: every number is copied from CLOCKS.md, PRINTS.md, EVENTS.md and ../btc_of_level_auction_1112/B1.md (full per-bucket tables live there). Net bp = net % x 100.

## Verdict table (60m horizon unless stated)

| Family | Cell | n | Net bp | Verdict |
|---|---|---|---|---|
| Clocks | 24 hour buckets x long/short, best long h22 | 851 | -5.22 | no edge (every long and short cell below 0 after fee) |
| Clocks | best short h01 | 851 | -6.31 | no edge |
| Clocks | funding windows (00Z/08Z/16Z), best 08Z/00Z long | 851 | -8.3 / -8.5 | no edge |
| Clocks | weekdays Mon-Sun, best Mon long | 2904 | -8.16 | no edge |
| Prints A1 | large print, trade with it (60-day sample) | 204 | -9.19 (gross +0.81) | no edge (z60 +0.12 vs placebo; fee eats it) |
| Prints A2 | absorption, 60-day sample | 15 | +1.43 | INSUFFICIENT_N (no verdict) |
| Events A2 | absorption, full DEV | 170 | -3.4 (15m -5.9) | INSUFFICIENT_N (<180) |
| Events A3 | funding extreme | 819 | -7.5 (15m -9.0) | no edge (t -3.8; 15m below placebo band). Count 754 in dda59e2e2, 819 in e84dafc48: unresolved, immaterial to the sign |
| Level B1 | absorption at PDH/PDL/VAH/VAL | 524 | -13.6 (15m -11.5) | no edge, worse than placebo mean |
| Level B1 control | same flow, away from level | 3804 | -9.1 | level adds nothing: at minus away -4.5 bp |
| Level B2 | unfinished auction at 24h extreme (fade), aggTrades on D: | 480 | -15.8 (15m -11.3; gross 60m -5.8, 15m -1.3) | FAIL on DEV (t -3.95 / -5.72; both cells inside the placebo band); VALIDATION not opened. See btc_of_level_auction_1112/B2.md |

## Plain words
BTC's own clocks (hour, weekday, funding window), large prints, absorption and funding extremes show no move big enough to pay the 10 bp fee. The few clock cells that beat a shuffle (h01, h13, h16, h22, funding 16Z) are one-sided noise: the best is still 5 bp short of break-even. Absorption at a prior-day level does worse than absorption anywhere else, so the level is not the edge. Two cells (A2, B2) could not be judged: too few events or no data.

## What would change the verdict
- A2 reaching n >= 180 (more DEV days or window) with net above 0 and |z| >= 2 vs placebo.
- B2: done (btc_of_level_auction_1112/B2.md, FAIL on DEV).
- Liquidation-cascade history (no public feed) and full-DEV aggTrades for A1.
- A cell positive net of fee in DEV, then again in the sealed VALIDATION (not opened here). Fee below 10 bp would not rescue any cell: best gross is +4.8 bp (h22 long).

## Paper slot
NOT_IN_DATA / no edge. No cell passed the PREREG bar, so no rule is frozen and no PAPER_SLOT.md exists. DECISION (OURS): conservative, queue nothing.
