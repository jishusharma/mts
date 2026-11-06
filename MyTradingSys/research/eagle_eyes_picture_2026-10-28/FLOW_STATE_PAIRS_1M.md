# C2 flow-state pairs on 1m (BTCUSDT): what followed

Card `flow-state-pairs-on-1m-oi-up-negative-de`. Source: operator shot 9ee7ea307f1e (10-28 22:23Z).
Tier: DESCRIPTIVE, SEEN window, no fees, no out-of-sample split. Observation only: not an edge, not trade advice.
Script: `flow_state_pairs_1m.py` (rerun prints every event). Tests: `test_flow_state_pairs_1m.py`.

## Data and rules (all thresholds OURS)
- Binance USD-M BTCUSDT 1m klines + 5m OI (`data.binance.vision` daily zips), 10-22 00:00Z to 11-04 23:59Z: 14 days asked, 13 with bars (18,720). The archive has no 10-28 USD-M klines (daily, monthly, 3m and aggTrades all missing).
- DECISION (OURS): CoinGlass 1m OI history is not on disk and has no keyless API. A 1m bar's OI direction = the change over the last 5m OI bucket that ends at or before the bar's close (no look-ahead; lags up to 4 min). A first run used the bucket holding the bar, which ends up to 4 min after the close; the look-ahead lint caught it and those numbers are discarded.
- Net delta = 2 x taker buy - volume (BTC); CVD = running sum.
- Burst: |net delta| at or above P95 of the window = 120.9 BTC. OI up / down: bucket change at or above +0.05 % / at or below -0.05 %.
- A: negative burst, OI up. B: positive burst, OI up, green bar, 5-bar CVD change > 0 ("all positive"). C: positive burst, OI down.
- Forward move = close 15 / 30 / 60 min later vs the bar close.

## Result (10-22..11-04, minus 10-28)

| Case | n | n, 1 per 15 min | 15m median | 15m up | 30m median | 30m up | 60m median | 60m up |
|---|---|---|---|---|---|---|---|---|
| A: OI up, sell burst | 160 | 99 | +0.030 % | 57 % | +0.004 % | 51 % | +0.063 % | 53 % |
| B: OI up, all positive | 128 | 90 | -0.005 % | 49 % | -0.026 % | 46 % | +0.029 % | 54 % |
| C: buy burst, OI down | 177 | 104 | -0.061 % | 39 % | -0.054 % | 44 % | -0.072 % | 42 % |

Read: A and B sit near zero (46-57 % up). C leans down at every horizon (39-44 % up, medians -0.05 to -0.07 %): a buy burst while OI falls (short covering) tended to give back. Bars overlap (104 independent C events), one symbol, 13 days, no baseline drift removed: an observation to test, not an edge.

Cited bars (case, time, delta BTC, OI 5m, fwd 15/30/60):
- A 10-22 02:04Z -180, +0.14 %: -0.40 / -0.57 / -0.51 %. A 10-27 21:42Z -140, +0.27 %: -0.15 / -0.17 / -0.21 %.
- B 10-22 09:14Z +320, +0.10 %: -0.14 / -0.11 / +0.20 %. B 10-27 21:41Z +137, +0.27 %: -0.23 / -0.27 / -0.32 %.
- C 10-22 01:39Z +317, -0.54 %: -0.40 / -0.51 / -1.02 %. C 10-27 21:31Z +1918, -0.73 %: -0.16 / -0.33 / -0.32 %.

## The three 10-28 instances (Bybit linear trades: the Binance archive gap)
10-28 read from the public Bybit trade dump (1m taker delta) with Binance 5m OI. Venue switch, so its own burst bar: day P95 = 53.8 BTC. That day: A 8, B 6, C 12.

| Shot label | Bar | Delta (BTC) | 5-bar CVD | OI 5m | Our case | Fwd 15 / 30 / 60 |
|---|---|---|---|---|---|---|
| A (OI up, sell burst) | 20:46Z, 81,063 to 80,951 | -95.3 | -84.6 | +0.275 % | A | +0.39 / +0.56 / +0.42 % |
| B (OI up, all positive) | 20:56Z, 81,170 to 81,233 | +80.0 | +115.7 | +0.077 % | B | +0.04 / +0.04 / +0.12 % |
| C (buy burst, OI down) | 20:00Z, 81,549 to 81,664 | +85.0 | +199.5 | -0.125 % | C | -0.54 / -0.72 / -0.44 % |

All three shot labels are reproduced by the rules. 20:46Z A bounced (unlike the A median, which is flat); 20:00Z C faded, in line with the C row.

## Spot-check (test)
`test_spot_check_three_cases_against_raw` recomputes the first A, B and C events (delta, OI change, 60m move) from the raw cached klines and OI: all match.

## Limits
- 5m OI proxy, not CoinGlass 1m OI. A cleaner test needs 1m OI (CoinGlass aggregated or a recorded Binance/Bybit 1m OI feed).
- One symbol, 13 days, one regime. Thresholds were set once and not tuned.
