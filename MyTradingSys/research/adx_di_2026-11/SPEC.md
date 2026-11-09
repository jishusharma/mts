# SPEC: ADX/DI 2-day cross census (card adx-di-2d-cross-census-1107, M1-M4 of PLAN_ADX_DI_VOLUME_2026-11-07.md)

Source claim (CCU, Steve, video AnAx1PanZm4, 2026-11-05, 2-day chart): after a "red cross" (DI- over DI+) the market takes
"1-3 weeks of consolidation", then falls "straight to the bottom", then "consolidates and then changes trend"; his cases Oct 2025
(36 %), Jan 2026 (37 %), May 2026 (26 %); ADX "tells us the strength of the trend". He names no number: every parameter here is OURS.

## Done when
1. `MyTradingSys/backtest/layers/FORMULAS.md` has a new section "ADX/DI (Wilder)": TR, +DM, -DM, Wilder smoothing (n = 14),
   DI+, DI-, DX, ADX, with a 20-bar toy series and its expected values computed by hand in the section (not from code).
2. `MyTradingSys/backtest/layers/adx/adx.py` (`adx_di(high, low, close, n=14) -> (di_plus, di_minus, adx)`) and `test_adx.py`
   green; the test asserts the hand values from the FORMULAS section and FAILS on the pre-change tree (no module).
3. `MyTradingSys/research/adx_di_2026-11/census.py` writes `CENSUS.md` with:
   (a) one row per 2d DI cross: date, direction (red = DI- over DI+, green = DI+ over DI-), ADX at the cross, ADX 5-bar slope,
       bars to the swing low (red) / swing high (green) within the next 30 2d bars, depth % (extreme / close at the cross - 1),
       whipsaw = opposite cross within 1, 2, 3 bars (three columns);
   (b) per ADX bucket (< 20, 20-40, > 40) x slope sign (falling from a high vs rising): n, whipsaw rate within 3 bars, median
       depth %, median bars to the extreme;
   (c) cascade: for each 2d cross, bars of lead of the first same-direction 1d / 4h / 1h cross inside the previous 10 2d bars
       (or "none"); and the share of 1d / 4h / 1h crosses that are followed by a same-direction 2d cross within 5 2d bars;
   (d) every table prints n; nothing concluded from truncated output.
4. Shipped with `Result: <n crosses, whipsaw rate within 3 bars, bucket with the lowest whipsaw>` and `Next: END: operator reads
   CENSUS.md`; `api_job.py ledger` row appended.

## Data and splits (DECISION OURS, logged in the card note)
- Daily: `MyTradingSys/research/btc_cycles_2026-11/btc_daily.csv` (date, high, low, close). 2d bars via
  `MyTradingSys/backtest/layers/timeframe/tf_resample.py` bucket "2d". 1h / 4h: the F:/MTS klines when present on the
  machine; when absent, (c) runs 1d-vs-2d only and CENSUS.md says so.
- DEV 2020-01-01..2024-06-30 builds table (b); VALIDATION 2024-07-01..2025-06-30 repeats (b) as a check; 2025-07-01..2026-11-07
  is a third table labelled "recent, descriptive, holds CCU's Oct-2025 / Jan-2026 / May-2026 cases"; no parameter is chosen
  from it. No HOLDOUT file of any other study is opened.

## Out of scope
Tom / Fabio / Krown layers, execution code, promoted_setups, volume (M5 is its own card), any order. Context layer only.
