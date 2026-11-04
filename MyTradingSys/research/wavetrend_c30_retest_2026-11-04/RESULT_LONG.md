Regime mix: 326 weeks: bull 73 (22%) | bear 0 (0%) | range 222 (68%) | n/a 31 (10%) | strict bear 0 ; proxy bear (weekly RSI14 <= 40 alone, below SMA200, OURS) 57 of 326 weeks
Verdict: INCONCLUSIVE (underpowered), not FAIL and not PASS. On the long SPOT DEV window (2018-04-01..2024-06-30) the 48 pooled + 192 session cells (strict `with` gate + one OURS proxy arm, Holm m=48 / 192) produced 0 survivors, so VALIDATION stayed unread and HOLDOUT was never loaded. prereg_gate still BLOCKs every confluence cell (BLOCKED_LONG.md).

# wavetrend_c30_retest long window result (SPOT BTCUSDT, DEV 2018-04-01..2024-06-30, fee-net 0.14 %, exit 12 bars, PRE_REG_LONG.md frozen first, commit f5e2e8fdc)

Reproduce: `python study_long.py --pass count` then `--pass dev` (about 1 and 2 min); tables `dev_cells_long.csv` (column `seg`: long / fresh / old), `counts_long.csv`; tests `test_wiring_long.py` (6, failed first on the missing `study_long.py`).
Data: public SPOT klines, native 15m / 30m / 1h / 1d, NOT spliced with futures. Run 1 used USD-M futures 1m resampled, so the 2022-2024 part ("old") differs slightly from run 1 even with identical rules. History before 2022-01 (fresh, 2018-04..2021-12) is new DEV data; "old" is the run 1 DEV window, already seen; the long window is fresh + old.

## Regime finding
Strict Malkan (weekly AND monthly RSI14 <= 40, below SMA200) never fires: 0 bear weeks over 2017-08..2026-10 and over this window, longer history does not add any. The definition is unchanged. The OURS proxy (weekly RSI14 <= 40 alone, below SMA200) gives 57 of 326 weeks, Proxy is never called Malkan's. 31 weeks are n/a (monthly RSI14 needs 15 months).

## Power gate
15m none (optimistic bound) 580 days PASS (0.294 vs 0.30, m=48); every confirmatory cell BLOCK (15m rsi 413 days 0.322; 30m 0.43-0.48; 1h 0.70-0.79; proxy cells have fewer days). Long history raised event-days about 2.7x but not enough. Table is descriptive.

## Bare dots (conf none, all gates, signal entry, long)
15m buy -0.115 % [-0.192, -0.038], sell -0.186 % [-0.245, -0.127]; 30m buy -0.147, sell -0.229 (CI upper bound -0.000 / -0.128); 1h buy -0.157 [-0.427, +0.112], sell -0.544 [-0.766, -0.323]. Bare dots still lose fee-net on every TF and side, now with tight intervals on 15m.

## Per cell vs run 1 (strict `with` gate, pooled sessions; net % fee-net, n)
| Cell | Run 1 (futures, 2022-24) | Long (n / days) | Long net [95% CI], excess t, Holm | fresh 2018-21 | old 2022-24 (spot) |
|---|---|---|---|---|---|
| 15m sell rsi signal (lead 1) | n257 +0.008 | 651 / 419 | -0.183 [-0.294, -0.072], excess t -0.67, Holm 0.06 | n400 -0.305 | n251 +0.011 |
| 15m sell rsi retest | n234 +0.008 | 608 / 393 | -0.143 [-0.265, -0.021], excess t 0.06, Holm 0.89 | n381 -0.238 | n227 +0.017 |
| 15m buy rsi signal | n238 -0.187 | 675 / 413 | -0.147 [-0.273, -0.020], -0.60, 0.93 | n430 -0.126 | n245 -0.183 |
| 30m buy rsi signal | n126 +0.002 | 343 / 247 | -0.291 [-0.485, -0.096], -2.22, 0.16 | n218 -0.452 | n125 -0.010 |
| 30m sell rsi signal | n131 -0.091 | 359 / 261 | -0.266 [-0.454, -0.079], -1.26, 0.24 | n230 -0.387 | n129 -0.051 |
| 1h sell rsi signal | n70 -0.019 | 194 / 159 | -0.413 [-0.814, -0.013], -1.29, 1.00 | n124 -0.608 | n70 -0.067 |
| 1h sell div signal | n22 +0.804 | 51 / 46 | -0.333 [-1.074, +0.409], -0.45, 1.00 | n29 -0.947 | n22 +0.477 |
| 1h sell div retest (lead 2) | n19 +1.117 | 46 / 41 | -0.225 [-1.058, +0.608], -0.15, 1.00 | n27 -0.891 | n19 +0.722 |
| 1h buy rsi signal | n74 -0.584 | 183 / 144 | -0.388 [-0.719, -0.058], -2.28, 0.89 | n109 -0.283 | n74 -0.543 |
All 24 strict pooled cells are in `dev_cells_long.csv`: 24 of 24 have a negative long net; the least bad are buy div cells (15m div signal -0.018, 30m div retest -0.066), CIs span zero, Holm 1.00.

## The two leads
- 15m sell RSI >= 60 below SMA200: the +0.008 % of run 1 was a 2022-24 feature. The same cell on the new 2018-2021 data is -0.305 % (n 400); old (spot) reproduces +0.011 %. Pooled -0.183 % with a CI entirely below zero. Lead does not hold out of the original window.
- 1h sell + divergence + retest: the old window reproduces it on spot (n 19 / +0.722 %, run 1 +1.117 %), but the 2018-2021 data gives n 27 / -0.891 %. Pooled n 46 -0.225 % [-1.058, +0.608]. The run 1 positive result is not confirmed by an independent period.

## Proxy arm (OURS weekly RSI14 <= 40 alone, below SMA200), strict arm beside it
Buy in the proxy bear regime (oversold-in-downtrend, a counter-trend buy): 15m rsi n 230 / 148 days +0.084 [-0.151, +0.318], excess t 1.88; 15m div n 75 +0.281 [-0.036, +0.599], excess t 2.63; 30m rsi +0.130, 30m div retest +0.283 (CIs wide). All Holm 1.00 (m=48). These are the only positive pooled cells and come mostly from the fresh slice (2018 bear, 15m rsi fresh n 66 +0.208, 15m div fresh n 19 +0.478) with tiny n; 1h proxy buy flips sign by segment (fresh +1.27 on n 17, old -1.13 on n 52). Proxy sells: mostly negative (15m -0.134, 30m -0.208), 1h sell div n 17 +0.738 (n < 30, ineligible). Nothing survives; the proxy buy pattern is a hypothesis for a future, separately pre-registered run, not a finding.

## Sessions
192 session cells, Holm m=192: 0 survivors (dev_survivors_long.json empty).

## What this says
Doubling the history (2.7x event-days) sharpened the picture instead of rescuing it: bare WaveTrend dots lose fee-net, the trend gate plus RSI or divergence confluence reaches zero only inside 2022-2024 and is clearly negative in 2018-2021, and both run 1 leads fail on the new data. This is still a measurement, not a FAIL: the confirmatory cells stay under-powered (BLOCKED_LONG.md), and it concerns BTCUSDT spot, 12-bar exit, taker cost, the strict and proxy regime tags only.

Gaps: spot maintenance gaps (9-25 per series, not filled) can make a 12-bar exit span a gap; 2018 and 2022 dominate the sample (bear/range regimes); the proxy arm was added after run 1 on the coordinator's decision, before any long-window return.
