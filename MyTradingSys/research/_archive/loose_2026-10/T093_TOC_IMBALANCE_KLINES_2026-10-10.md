# T093 - turn-of-candle order imbalance at 4/8/12 h, BTCUSDT 2022-2026 from 1m klines: RESULT (2026-10-10)

**Verdict: NO REPLICATION at 4h, 8h and 12h.** The signed gross edge is +0.5 bp at every window against a 10 bp round-trip taker fee
(0.0005 x 2 legs, backtest/fees.py); net CI95 sits wholly below zero; the gross sign flips between years at every window.
Extends P4 corrected (2024-12..2026-09, NO REPLICATION, `P4_QUARTER_HOUR_IMBALANCE_CORRECTED_2026-10-08.md`) back to 2022-01 with 3x the sample.

Spec and rules: `items/T093_toc_imbalance_klines.md` (operator D08: replace the live 1-minute turn_of_candle test by the 4-12 h imbalance test;
source `TURN_OF_CANDLE_ORIGIN_2026-10-09.md`). Reproduce, one year at a time (3-4 s each), then combine:
```
python MyTradingSys/research/loose_code/t093_toc_imbalance_klines.py part --year 2022     # ... 2026
python MyTradingSys/research/loose_code/t093_toc_imbalance_klines.py combine
```
Data: `F:/MTS/data/tom_raw/klines` (Binance BTCUSDT 1m, 2022-01-01..2026-09-26, zero gaps per the Tom BT load check). Buy = `taker_buy_volume`,
sell = `volume - taker_buy_volume`. No trade-level data (aggTrades) exists on disk, so this is the kline proxy the spec names; the paper's own
variant on trade data is still untested (needs aggTrades, not claimed here).

```
parts 5, years [2022, 2023, 2024, 2025, 2026]
## 4h: n=166041  gross mean +0.51 bp  net mean -9.49 bp  net CI95 [-10.06, -8.94]
   2022: +0.83 (n=35035)  2023: +0.97 (n=35032)  2024: +0.18 (n=35130)  2025: +0.57 (n=35037)  2026: -0.16 (n=25807)
   sign stable across years: False   CI above zero: False   placebo net -9.69 bp CI [-10.17, -9.17]   VERDICT 4h: NO REPLICATION
## 8h: n=166025  gross mean +0.47 bp  net mean -9.53 bp  net CI95 [-10.30, -8.70]
   2022: +0.16  2023: +1.87  2024: +0.40  2025: -0.27  2026: +0.11
   sign stable across years: False   CI above zero: False   placebo net -9.65 bp CI [-10.41, -8.87]   VERDICT 8h: NO REPLICATION
## 12h: n=166009  gross mean +0.52 bp  net mean -9.48 bp  net CI95 [-10.49, -8.43]
   2022: +0.05  2023: +2.24  2024: +0.94  2025: +0.07  2026: -1.15
   sign stable across years: False   CI above zero: False   placebo net -9.79 bp CI [-10.74, -8.89]   VERDICT 12h: NO REPLICATION
```

Reading: the real signal is no better than the shuffled-sign placebo (net -9.5 vs -9.7 bp). A +0.5 bp gross mean is a twentieth of the fee. The
quarter-hour imbalance idea does not survive costs on klines over 4.7 years; the live `layer:turn_of_candle:` (1-minute hold) has no support from
either paper. Nothing was tuned; the horizons, fee and decision rule are the pre-registered P4 ones.
