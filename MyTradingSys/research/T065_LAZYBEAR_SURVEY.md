# T065 - LazyBear survey and shortlist

Session: MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch (Cloud, static). Item: items/T065_lazybear_survey.md.

## 0. Evidence limits (read first)

- The Cloud egress proxy blocks every tradingview.com host (in., my., www.; `EGRESS_BLOCKED`), so the profile page
  https://in.tradingview.com/u/LazyBear/ and the Pine sources were **not opened**. Only web-search snippets were available.
- Consequences: (a) boost/like counts are shown only where a snippet carried one (Squeeze Momentum ~76k); everything else is
  "not shown"; (b) parameters marked **[SEARCH]** appeared in a snippet, **[MEMORY]** come from general knowledge of the
  public script and are **UNVERIFIED against Pine**. Per the provenance rule they must be confirmed from the source page
  (Desktop/LAN or a pasted Pine file) before any layer file is written. Nothing here is a tuned number.
- Evidence tier for all items: T3 practitioner indicator (no MTS backtest). Ranking is a port-cost/fit judgement, not a result.

## 1. Scripts found (search-confirmed to exist and be open source)

| Script | URL | Likes seen | Maps to MTS gap |
|---|---|---|---|
| Squeeze Momentum Indicator | https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/ | ~76k [SEARCH] | volatility compression: GAP (no BB/Keltner code in repo; grep of py/md/java finds none) |
| WaveTrend Oscillator / WT with Crosses | https://in.tradingview.com/v/jFQn4jYZ/ (from T061) | not shown | momentum/divergence: already T061 |
| Volume Flow Indicator (VFI, Katsanos) | https://tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear | not shown | volume/flow: PARTIAL duplicate of CVD (MTS has aggTrade CVD live; VFI is OBV-style on candle volume) |
| Better Volume Indicator (BVI) | https://www.tradingview.com/script/LfVJhuir-Indicators-Better-Volume-Indicator-InstrumentVolume/ | not shown | effort-vs-result volume bars (climax / churn / low): GAP vs absorption flag |
| Impulse MACD | https://in.tradingview.com/script/qt6xLfLi-Impulse-MACD-LazyBear | not shown | trend state: overlaps the 6-state MOMENTUM map in MTS_PLAYBOOK.md:32 and RSI layers. Not shortlisted |
| Others named in the ask (Klinger, Relative Volatility, Chandelier) | - | - | Search returned no LazyBear page for them; not assessed |

## 2. Shortlist (4; each a separate switchable layer, tag [SCREENER], never a Tom filter, read-only contract per PROJECT_VISION)

### S1. Squeeze Momentum (priority 1)
- **Computes:** volatility-compression flag when Bollinger Bands sit inside Keltner Channels, plus a linear-regression momentum
  histogram of price vs the mid of the high/low range and the moving average. Derived from Carter's TTM Squeeze.
- **Parameters:** BB length 20, BB mult 2.0, KC length 20, KC mult 1.5, true-range option [SEARCH]; momentum linreg length 20 [MEMORY].
- **One-line reason:** MTS has no volatility-compression read; BTC "needs to break out" is the operator's ask 1 and a squeeze state is
  the only LazyBear item that says *when a range is loaded*.
- **Port cost:** ~4 h (SMA, stdev, ATR, linreg on klines already in data/klines/).
- **Draft file:** `MyTradingSys/backtest/layers/volatility/squeeze_momentum.py` (+ `test_squeeze_momentum.py`)
- **Source:** https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/

### S2. Better Volume Indicator (priority 2)
- **Computes:** classifies each bar's volume as climax-up, climax-down, high-volume churn or low volume from volume vs recent
  extremes and bar range/volume ratios (port of a TradeStation indicator).
- **Parameters:** lookback and thresholds **[MEMORY, unverified]**; must be read from Pine before building.
- **One-line reason:** "high-volume churn" is effort-without-result at bar level, the klines-only cousin of the absorption flag, so
  it can be backtested on 5m/15m/1h history where aggTrade CVD does not exist.
- **Port cost:** ~3 h.
- **Draft file:** `MyTradingSys/backtest/layers/volume/better_volume.py`
- **Source:** https://www.tradingview.com/script/LfVJhuir-Indicators-Better-Volume-Indicator-InstrumentVolume/

### S3. WaveTrend with Crosses (already open as T061; priority 3)
- **Computes:** hlc3 channel index smoothed twice (EMA 10, EMA 21) with a 4-bar SMA signal and cross markers.
- **Parameters:** n1 10, n2 21, OB 60/53, OS -60/-53 (items/T061, copied from the source by the operator's session).
- **One-line reason:** only oscillator on the list that carries divergence, which the operator named as a gap; do not open a second item.
- **Port cost:** ~3 h (math already written in T061).
- **Draft file:** `MyTradingSys/backtest/layers/momentum/wavetrend.py`
- **Source:** https://in.tradingview.com/v/jFQn4jYZ/

### S4. Volume Flow Indicator (priority 4)
- **Computes:** OBV-style cumulative volume flow on typical price with a volatility cutoff and an excess-volume cap; above zero
  bullish, zero cross is the trigger, divergence is the strongest read.
- **Parameters:** Katsanos suggests coefficient 0.2 for daily and 0.1 for intraday [SEARCH]; length / vcoef / signal [MEMORY].
- **One-line reason:** only worth it as a klines-history stand-in for CVD; on live data aggTrade CVD is the better source, so it is the weakest fit.
- **Port cost:** ~3 h.
- **Draft file:** `MyTradingSys/backtest/layers/volume/volume_flow.py`
- **Source:** https://tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear

## 3. ROI note and next step

Build order S1, S2, S3; S4 only if a klines-only backtest of CVD-like flow is wanted. Total ~10-13 h for S1-S3. Before any build, a
LAN/Desktop session must open the four source pages and paste the Pine (or parameter tables) into the item, replacing every
[MEMORY] tag. No layer touches execution/ or layers/alerts/. Each layer needs a fail-first test (CLAUDE.md gate) and outputs a
flag only; promotion past SCREENER needs a backtest per PROJECT_VISION point 4.
