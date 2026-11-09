# Malkan level shorts on the 82k-87k range, BTC 4h (2026-08-21 .. 2026-10-23)

**5 operator-marked shorts after the 65.7k -> 87.4k push: all 5 reached >= 1R; only V1 (09-23) fits the repo divergence rule (3-10 bars, close to close). Hand-picked in hindsight, so this describes a pattern; it is not an edge.**

Data: Binance spot BTCUSDT 4h (data-api.binance.vision; the futures API is blocked on JIS-NB), UTC. RSI 14 Wilder, RSI MA = SMA 14, WaveTrend LazyBear n1=10 n2=21 (wt2 = SMA4 of wt1), bands 53/60. Script: `build_indicators.py`. Levels from the operator chart: red 97,932 / 86,807; green 82,177 / 65,750.

## The five points

| # | Bar (UTC) | What price did | RSI | WaveTrend | Repo rule fires? | Entry / stop / best move |
|---|---|---|---|---|---|---|
| C1 | 08-28 00 (3rd push) | wick 81,479 > 08-25 high 81,272; close 79,810 < 08-25 close 80,488 | 76.3 -> 66.2 -> 60.2 falling; 08-28 04 RSI 58.8 < MA 60.0 and below 60 | peak 51.1 < 08-25 62.5 (lower high, under the 53 band); cross down 08-28 04 | NO: high-based only, 15-19 bars (> 10) | 79,660 / 81,560 / -4.3 % (1.8R), stop hit 09-03 |
| C2 | 09-03 20 .. 09-04 12 | touched green 82,177 (high 82,300) after one impulse | 76.7, no divergence; 09-04 12 RSI 52.4 < MA 56.0 | 38.8, no band | NO (no divergence) | 79,429 / 82,382 / -4.3 % (1.1R) |
| V1 | 09-21 20 -> 09-23 00 | close 86,620 -> 86,704 (higher), at red 86,807 | 86.5 -> 76.2 (lower); 09-23 00 RSI 76.2 < MA 76.7 | 75.8 > 60 band, already crossed down | YES: 7 bars, close to close | 86,125 (09-23 04 closes below prior open) / 87,483 / -4.1 % (2.6R) |
| V2 | 10-02 08 -> 10-04 20, trigger 10-06 12 | close 86,425 -> 86,530 (higher) under red | 71.0 -> 68.9 (lower); 10-06 08 back to 60.2 from below, 10-06 12 53.9 < MA 58.5 | 59.8 then 57.4, lower high | NO: 15 bars (> 10) | 85,721 / 87,307 / -6.9 % (3.7R) |
| C3 | 10-21 16 .. 10-22 00 | 84,898 swept the 10-12 high 84,352; lower high vs 85,598 / 86,999 / 87,220 / 87,395 | 4h 68.8 then 51.6 < MA 56.6 at 10-22 00; DAILY 56.8 turned down under 60 | 53.0 = touched the 53 band, cross down 10-22 00 | NO (no divergence) | 82,925 / 84,983 / -8.0 % (3.2R); earlier entry 84,093 at the 10-21 20 close back under 84,352 |

Higher timeframes: monthly RSI 50-53, weekly 55-63 (weekly 63.3 on 09-28, back under 60 by 10-05). Neither is below 40, so the Malkan 5-star short (monthly + weekly bearish) never fired here.

## What the repo already has

| Piece | File | Status |
|---|---|---|
| 40/60 regime + bounce/reject setups (MLK-R1; S1 long at 40, S2 short at 60) | `backtest/layers/rsi/malkan_40_60.py` | built, SOURCED (WEB_RESEARCH.md) |
| 5-star = Grandfather (monthly) / Father (weekly) / Son (daily) | `backtest/layers/rsi/malkan_mtf.py` | built; backtest `rsi_divergence_mtf_gated_2026-11-04` found no edge |
| 7-star | `malkan_mtf.seven_star` | LABEL only, one video, UNVERIFIED: monthly RSI at 60 + daily divergence, or monthly > 60, daily < 40 + divergence; he claims an 80-90 % hit rate; full conditions withheld (paid course) |
| Divergence | `rsi_divergence.py`, params `malkan_divergence_default.json` | close to close, 3-10 bars (SOURCED quote); PRD/NRD reverse divergence |

## Why the repo missed 4 of the 5

1. Window: Malkan's 3-10 bars came from his lower-timeframe examples. On 4h the operator's divergences span 15-19 bars (C1, V2). OURS question: scale the window by timeframe, or go swing to swing.
2. Close vs wick: C1 is a higher high on the wick only; the close was lower. The repo is close to close.
3. No divergence at all (C2, C3): these are level trades. The repo has no "lower high at a defended level" rule.

## The confluence stack (OURS, built from his five reads)

| Layer | Short condition | Seen in |
|---|---|---|
| 1 Level | price at a marked level that already rejected price (his red/green lines) | all 5 |
| 2 Structure | divergence (close or wick, swing to swing) OR a lower high that sweeps the last swing high and closes back under it | C1, V1, V2 / C3 |
| 3 Trigger | RSI closes below its MA and below 60 coming from above; next candle trades through the prior candle's open | all 5 |
| 4 WaveTrend | wt1 crosses below wt2 at or near the 53/60 band, or makes a lower high | C1, V1, V2, C3 |
| 5 Higher TF | daily RSI fails at or under 60, or weekly falls back under 60 | C3 (daily 56.8); V2, C3 (weekly 63 -> 57) |
| Stop | above the swing wick (1.6-2.5 % on these) | all 5 |

## Next

Card `malkan-level-short-4h-count-1109`: code layers 1-5, count every firing on BTC 4h 2017-2026 (fee-net, by regime), then send the current-phase version to testnet forward (phase-first, d-phase-first-method-1106).
