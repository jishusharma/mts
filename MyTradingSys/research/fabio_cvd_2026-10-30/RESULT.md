# U7 + U8 result: Fabio CVD claims on BTC 1m taker delta (2026-11-05)

Card: cvd-coil-and-absorption-u7-u8. Script: `cvd_u7_u8.py` (definitions in its docstring, all OURS except the 0.1% equal-low band from the card).
Data: Binance USD-M BTCUSDT 1m, **DEV only 2022-01-01..2024-06-30** (87,552 15m bars); no VALIDATION or HOLDOUT file opened.
Descriptive, no fees, no edge claim. Delta = 2 x taker buy volume - volume.

## Verdict

| # | Claim | Result |
|---|---|---|
| U7 | CVD slope in a pre-US coil predicts the break side | **Mostly price drift, not CVD.** CVD sign lines up with the first break (59% vs 35% up, all days), but box price direction alone gives 63% vs 27%. Holding price direction fixed, CVD sign adds +6 pp (up boxes) and -5 pp (down boxes): no added information |
| U8 | CVD lower low at a flat price low (absorption) predicts a reversal | **No, the reverse.** Divergence lows reverse in 4h 28.5% vs 31.5% for matched controls, and the low breaks *more* often (65.4% vs 59.2%, z about 3.4). Same sign in each of 2022, 2023, 2024 |

## U7 table: box CVD sign x first break side (A..A+4h)

Events = pre_us_squeeze_2026-10-29 definitions (box A-8h..A, squeeze = BW percentile <= 20% = C17 coil).

| group | CVD sign | n | first up | first down | both/none | up share of up+down |
|---|---|---|---|---|---|---|
| squeeze (C17) | + | 47 | 26 | 12 | 9 | 68% |
| squeeze (C17) | - | 54 | 23 | 24 | 7 | 49% |
| all days | + | 298 | 142 | 99 | 57 | 59% |
| all days | - | 332 | 99 | 187 | 46 | 35% |
| all, strong third (abs CVD/volume top 33%) | + | 95 | 58 | 16 | 21 | 78% |
| all, strong third | - | 115 | 23 | 70 | 22 | 25% |
| all, box price up | + | 257 | 135 | 75 | 47 | 64% |
| all, box price up | - | 72 | 38 | 27 | 7 | 58% |
| all, box price down | + | 41 | 7 | 24 | 10 | 23% |
| all, box price down | - | 260 | 61 | 160 | 39 | 28% |

Price baseline (no CVD): box close > open: up share 63% of 275; box close <= open: 27% of 252.
Squeeze-only gap (68% vs 49%, 38 and 47 directional events) is z about 1.8: too few to separate from the price effect.

## U8 table: equal 15m lows (<= 0.1%, <= 24h apart), forward 4h from the confirming close

Reversal = window never trades below the pair's lower low AND the 4h close is above the reference close.
Control = same equal-low rule with CVD equal or higher; "matched" = re-weighted to the divergence set's distance bins (thirds of 0.1%).

| set | n | reversal 4h | low broken 4h | mean 4h return |
|---|---|---|---|---|
| divergence (CVD lower low) | 1469 | 28.5% | 65.4% | -0.006% |
| control raw | 1439 | 31.4% | 59.3% | +0.009% |
| control distance-matched | 1439 | 31.5% | 59.2% | +0.010% |
| 2022 divergence / control matched | 431 / 505 | 27.6% / 31.8% | 67.3% / 57.5% | -0.030% / -0.072% |
| 2023 divergence / control matched | 711 / 700 | 28.1% / 30.8% | 65.7% / 60.4% | +0.001% / +0.052% |
| 2024 divergence / control matched | 327 / 234 | 30.3% / 32.4% | 62.1% / 58.8% | +0.009% / +0.057% |

## Limits

- Bar-level taker delta, not a footprint: Fabio reads absorption at a price level inside a bar; this tests the bar-close CVD version only.
- U8 swing rule (K=2 bars each side, pair within 24h) and the reversal rule are OURS; a different swing size could change n, not checked.
- Squeeze subset is small (101 days).

## DECISIONS (OURS)

- DEV only; the study refuses rows at or after 2024-07-01 and never opens later files.
- Box price direction added as a baseline because CVD tracks price; without it U7 would read as a CVD effect.

Reproduce: `python MyTradingSys/research/fabio_cvd_2026-10-30/cvd_u7_u8.py` (about 1 min). Test: `MyTradingSys/tests/research/test_cvd_u7_u8.py`.
