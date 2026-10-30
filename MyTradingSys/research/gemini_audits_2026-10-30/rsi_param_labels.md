# Parameter Labels Audit: rsi

Audit of numeric parameter defaults across `MyTradingSys/backtest/layers/rsi/`.

## Parameters

| Parameter | Location | Default Value | Label | Source / Citation / Notes |
| :--- | :--- | :--- | :--- | :--- |
| `rsi_core.period` | `MyTradingSys/backtest/layers/rsi/params/default.json:7` | `14` | `SOURCED` | Wilder's standard RSI 14-period default; `FORMULAS.md` s1 |
| `rsi_ma.length` | `MyTradingSys/backtest/layers/rsi/params/default.json:11` | `14` | `SOURCED` | TradingView standard RSI MA default (SMA 14) |
| `rsi_events.levels` | `MyTradingSys/backtest/layers/rsi/params/default.json:14` | `[70, 50, 30]` | `SOURCED` | Standard Wilder overbought (70), midpoint (50), oversold (30) levels |
| `rsi_events.tolerance` | `MyTradingSys/backtest/layers/rsi/params/default.json:15` | `0` | `OURS` | Internal tolerance band around level |
| `malkan_40_60.lo` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:10` | `40` | `SOURCED` | Malkan (Malkansview), `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md` MLK-R1 / MLK-S1: "whenever in a bullish trend, it won't be able to cross 40" |
| `malkan_40_60.hi` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:11` | `60` | `SOURCED` | Malkan (Malkansview), `research/malkan_rsi_2026-09-28/WEB_RESEARCH.md` MLK-R1 / MLK-S2: "Whenever the market is bearish, it won't be able to cross 60" |
| `malkan_40_60.regime_lookback` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:12` | `20` | `OURS` | Internal lookback window for regime confirmation; NOT_IN_DATA for Malkan |
| `malkan_40_60.event_tolerance` | `MyTradingSys/backtest/layers/rsi/params/malkan_40_60_default.json:13` | `2` | `OURS` | Internal tolerance band for 40/60 level touches; NOT_IN_DATA for Malkan |
| `min_bars` (regular divergence) | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:4` | `3` | `SOURCED` | Malkan (Malkansview), `extract_Wvq1TZh8aF0.md:13`: "How many candles are needed? Three." |
| `max_bars` (regular divergence) | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:5` | `10` | `SOURCED` | Malkan (Malkansview), `extract_Wvq1TZh8aF0.md:13`: "It should be between three and 10." |
| `min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:9` | `0.0` | `SOURCED` | Malkan (Malkansview), `extract_cQ-y1oULkBw.md:15`: "Sometimes there is divergence in decimals and that will also be acceptable." |
| `reverse.min_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:14` | `5` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "number of bar should be between five to fifty" |
| `reverse.max_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:15` | `14` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:379`: "number of bars which are less than 15" |
| `reverse.prd_min_rsi` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:18` | `60.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "both the point should be about sixty if it's a positive edge divergence" |
| `reverse.nrd_max_rsi` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:19` | `40.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "negative reverse divergence it should be below forty" |
| `krown_hidden_bars.min_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:23` | `3` | `OURS` | Inline note: "OURS, KROWN-CONFLUENCE generic hidden divergence, not Malkan" |
| `krown_hidden_bars.max_bars` | `MyTradingSys/backtest/layers/rsi/params/malkan_divergence_default.json:23` | `10` | `OURS` | Inline note: "OURS, KROWN-CONFLUENCE generic hidden divergence, not Malkan" |
| `period` | `MyTradingSys/backtest/layers/rsi/rsi_core.py:7` | `14` | `SOURCED` | Wilder's standard RSI 14-period default; `FORMULAS.md` s1 |
| `length` | `MyTradingSys/backtest/layers/rsi/rsi_ma.py:8` | `14` | `SOURCED` | TradingView standard RSI MA default (SMA 14) |
| `lo` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `40.0` | `SOURCED` | Malkan 40 level (MLK-R1 / MLK-S1) |
| `hi` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `60.0` | `SOURCED` | Malkan 60 level (MLK-R1 / MLK-S2) |
| `lookback` | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:24` | `20` | `OURS` | Internal lookback parameter; NOT_IN_DATA for Malkan |
| `level` (bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:64` | `40.0` | `SOURCED` | MLK-S1: "Bullish candlestick forms at 40 RSI level on daily chart = buy signal" |
| `tolerance` (bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:64` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| `level` (bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:107` | `60.0` | `SOURCED` | MLK-S2: "Bearish candlestick forms at 60 RSI level on daily chart = short signal" |
| `tolerance` (bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_40_60.py:107` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| `level` (MTF bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:53` | `40.0` | `SOURCED` | MLK-S1-MTF: Malkan 40 level |
| `tolerance` (MTF bull setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:53` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| `level` (MTF bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:79` | `60.0` | `SOURCED` | MLK-S2-MTF: Malkan 60 level |
| `tolerance` (MTF bear setup) | `MyTradingSys/backtest/layers/rsi/malkan_mtf.py:79` | `2.0` | `OURS` | Tolerance band; NOT_IN_DATA for Malkan |
| `PRD_MIN_RSI` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:44` | `60.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "both the point should be about sixty if it's a positive edge divergence" |
| `NRD_MAX_RSI` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:45` | `40.0` | `SOURCED` | Malkan (Malkansview), `GbXnw_tNMtw_raw.txt:460`: "negative reverse divergence it should be below forty" |
| `min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/rsi_divergence.py:61` | `0.0` | `SOURCED` | Malkan (Malkansview), `extract_cQ-y1oULkBw.md:15` |
| `min_rsi_diff` | `MyTradingSys/backtest/layers/rsi/krown_hidden_divergence.py:20` | `0.0` | `OURS` | Shared with rsi_divergence |
| `STOP_PCT` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:56` | `0.01` | `OURS` | Standard indicator-layer 1% stop loss bracket (`MTS_USER_GUIDE.md` s4) |
| `TARGET_PCT` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:57` | `0.02` | `OURS` | Standard indicator-layer 2% take profit bracket (`MTS_USER_GUIDE.md` s4) |
| `MAX_BARS` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:58` | `100` | `OURS` | Trade timeout bar horizon |
| `MIN_OOS_N` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:59` | `30` | `OURS` | Sample size threshold for statistical evaluation |
| `MAX_PBO` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:60` | `0.5` | `OURS` | Probability of backtest overfitting cutoff |
| `is_frac` | `MyTradingSys/backtest/layers/rsi/run_rsi_backtest.py:76` | `0.70` | `OURS` | 70/30 chronological IS/OOS split fraction |
| `PRIMARY_H` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:48` | `10` | `OURS` | Primary forward return horizon: docstring `PRIMARY_H = 10 bars and T_MIN = 2.0 are engineering choices (NO-SOURCE)` |
| `MIN_EVENTS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:49` | `300` | `OPERATOR-HYPOTHESIS` | T089 item specification: docstring `fewer than MIN_EVENTS (300, operator rule in the T089 item)` |
| `T_MIN` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:50` | `2.0` | `OURS` | Engineering choice t-statistic hurdle |
| `MIN_YEAR_EVENTS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:51` | `30` | `OURS` | Sub-sample minimum events per calendar year |
| `OPERATOR_MIN_BARS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:52` | `11` | `OPERATOR-HYPOTHESIS` | Operator long-range divergence idea (T091, NO-SOURCE); Malkan rejects this window |
| `OPERATOR_MAX_BARS` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:53` | `60` | `OPERATOR-HYPOTHESIS` | Operator long-range divergence idea (T091, NO-SOURCE); Malkan rejects this window |
| `RSI_PERIOD` | `MyTradingSys/backtest/layers/rsi/run_divergence_mtf.py:54` | `14` | `SOURCED` | Wilder standard 14-period RSI |
