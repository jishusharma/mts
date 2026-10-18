> **RERUN 2026-10-17 (DEV only, new labels):** DEV-only rerun with DEV = before 2024-07-01 (OFV_DEV_ONLY=1, results_dev_rerun_2026-10-17.json). DIV minus CONTROL, 60-min net, DEV diff (Welch t), old -> new: 1m long -0.023 (-1.6) -> -0.023 (-1.4); 1m short +0.013 (1.0) -> +0.016 (1.1); 5m long +0.041 (1.4) -> +0.017 (0.5); 5m short -0.009 (-0.4) -> -0.022 (-0.9). Pass mark (>= 0.05, t >= 2) met by 0 of 4, as before. OI rows have no DEV data (OI series starts 2025-09). VAL and HOLDOUT not evaluated in the rerun. Verdict unchanged: NEGATIVE.

> **CONTAMINATED (DEV read VALIDATION 2024-07..12)** - study.py split_of() is year-based (DEV = year <= 2024), so DEV includes 2024-07..12 (own copy, not fires_kline). See MyTradingSys/backtest/bigtrade/SPLIT_ALIGNMENT_2026-10-17.md. Numbers below are kept as originally run, not recomputed.

# Price vs CVD divergence on 1m and 5m, with an OI split (BTCUSDT, 2022-01..2026-10-14)

Ask (operator, 2026-10-14, shots c688fa7b068c / a18c65f081d5 / 8adf02ce149d): "The buy in 1 min is quite visible as
price was falling CVD was increasing - verify this. How accurate are our readings ... find clues that will prove us
the EDGE." Script: `study.py` (definition in its header, fixed before the first run). Output: `results.json`,
`today.json`, `bt.out`. All numbers are OURS. One definition, one run, nothing tuned. Fee 0.05% per side.

## 1. Today, checked against Binance fapi (screenshot extract: `research/screenshots/2026-10-14_BTCUSDT_c688fa7b068c.md`)
- **The 1m claim holds.** Binance CVD bottomed at 14:12Z (price low 82001.2). Price then made a lower low of 81622.0 at
  15:08Z (379 points lower) while CVD was 1115 BTC higher; by 15:19Z CVD was +1473 BTC above its low.
- **OI rose into the fall, then dropped on the bounce.** 91.07K BTC at 12:15Z, 93.55K at 15:00-15:10Z (+2.7%), 93.16K
  at 15:20Z while price rose to 82049.8. Rising OI with falling price and rising CVD = aggressive buyers opening into
  passive sellers; the OI drop on the 15:10-15:20 rise fits short covering. The chart OI (93.501K, 93.109K, 93.131K,
  93.134K) matches fapi to 0.06%.
- **Chart readings that are chart artifacts, not market levels:**
  - The 1m VWAP (82643.0) is not a daily VWAP. The 00:00Z VWAP was 82992.6 at 15:17Z; 82643 fits a VWAP started at
    10:46Z, i.e. the first bar the 1m chart loaded. The 5m VWAP (82999.5) matches the 00:00Z VWAP within 15 points.
  - CVD levels depend on where the chart starts: the 5m Binance CVD (-3.038K) fits a start at 13 Oct 14:25Z, the 1m
    CVD a start near 10:46Z. Only CVD shape (higher/lower lows) can be compared across charts and with our data.
  - Aggregated futures CVD and Net Longs / Net Shorts are CoinGlass-built (all exchanges, their own split). We have
    Binance taker volume and Binance total OI only. Net Delta (152.328) still has no known unit (open card
    `identify-the-coinglass-net-delta-panel-u`).

## 2. What our code reads today
- Live CVD: Fabio `cvd_absorption` on 15m and 1h only, and it looks for the opposite shape (CVD lower low while price
  holds). `funding_cvd_fade` on 1h. OI enters only as context (`htf_context_live`, oi_live recorder).
- Nothing live reads 1m or 5m CVD against price swings, and nothing combines price, CVD and OI into one state.
  So the view in these charts is missing from the live read. Section 3 says whether that costs us an edge.

## 3. Backtest: is "price lower low, CVD higher low" an edge?
Rule (S1 = 1m bars, two 15-min halves; S5 = 5m bars, two 60-min halves): at a bar close, price made a lower low in the
recent half, the low is within the last 3 bars, the market fell over the last four halves, and CVD did NOT make a
lower low. CONTROL = the same without the CVD condition. Short = mirror. Entry next 1m open.

Mean net return 60 min after entry (fee included; a coin flip with no edge scores -0.10%):

| scale/side | DIV (n) | CONTROL (n) | DIV - CONTROL, DEV / VAL / HOLDOUT (Welch t) |
|---|---|---|---|
| 1m long | -0.097% (4933) | -0.087% (10921) | -0.023 (-1.6) / +0.026 (1.3) / -0.008 (-0.4) |
| 1m short | -0.095% (5434) | -0.096% (11143) | +0.013 (1.0) / -0.011 (-0.6) / -0.033 (-1.5) |
| 5m long | -0.081% (1411) | -0.094% (5147) | +0.041 (1.4) / -0.037 (-1.2) / +0.001 (0.0) |
| 5m short | -0.098% (1858) | -0.091% (5447) | -0.009 (-0.4) / -0.001 (0.0) / -0.019 (-0.5) |

- Pre-registered pass mark: DIV beats CONTROL by >= 0.05% on DEV with t >= 2 and keeps the sign on VAL and HOLDOUT.
  **0 of 12 arms pass** (4 above plus OI-UP and OI-DOWN for each, 2025-09+; every OI row is within +-0.13%, |t| < 1.6).
- Every arm is about zero before fees. The stop/2R trade version is the same: -0.09% to -0.12% per trade net.
- Today shows why the eye is fooled: the 1m rule fired 21 times between 13:13Z and 15:11Z. The 13:13Z fire was
  followed by -0.73% in 60 min; the 13:58Z and 14:40Z fires were followed by lower prices. Only the last fires (14:5x,
  15:09Z) sat near the bottom. On a finished chart we see the one that worked.

## Verdict
NEGATIVE. The 1m divergence the operator saw is real in the data, and our live read does not show it, but on 4.8 years
of 1m and 5m bars it predicts nothing beyond "price made a lower low in a falling market", with or without the OI
split. Adding it as a live signal is not supported. It can go on the live read as a descriptive line (card
`live-orderflow-state-line-1m-5m-15m-pric`), clearly marked as no-edge, so the operator and the system see the same thing.
Untested here: aggregated (all-exchange) CVD, CoinGlass Net Longs/Shorts, divergence at a level (VAL, band, Tom
level) instead of anywhere; each needs its own pre-registered run.
