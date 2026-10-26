# T065 - LazyBear survey and shortlist

Session: MTS-2026-10-05-1600Z-CLD-ANA-cloud-haiku-batch (Cloud, static). Item: items/T065_lazybear_survey.md.

## 0. Evidence status (updated 2026-10-05, Desktop, session MTS-2026-10-05-1650Z-APP-BLD-desktop-sonnet-finish)

- TradingView reachable from Desktop (built-in browser). The four shortlisted Pine sources were **opened and read** (Source code tab). Every parameter below tagged **[PINE]** is from that source;
  the earlier [SEARCH]/[MEMORY] tags are replaced. Corrections to the Cloud draft are in section 2 under "Correction".
- Not verified: the Squeeze Momentum author's *updated* source (pastebin.com/UCpcX8d7, see S1) was not opened; boost/like counts are as displayed on the page, label meaning (views vs boosts) not confirmed.
- Evidence tier for all items: T3 practitioner indicator (no MTS backtest). Ranking is a port-cost/fit judgement, not a result. Nothing here is a tuned number.

## 1. Scripts found (search-confirmed to exist and be open source)

| Script | URL | Likes seen | Maps to MTS gap |
|---|---|---|---|
| Squeeze Momentum Indicator | https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/ | page shows 116.8K / 680 [PINE page] | volatility compression: GAP (no BB/Keltner code in repo; grep of py/md/java finds none) |
| WaveTrend Oscillator / WT with Crosses | https://in.tradingview.com/v/jFQn4jYZ/ (from T061) | not shown | momentum/divergence: already T061 |
| Volume Flow Indicator (VFI, Katsanos) | https://tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear | not shown | volume/flow: PARTIAL duplicate of CVD (MTS has aggTrade CVD live; VFI is OBV-style on candle volume) |
| Better Volume Indicator (BVI) | https://www.tradingview.com/script/LfVJhuir-Indicators-Better-Volume-Indicator-InstrumentVolume/ | not shown | effort-vs-result volume bars (climax / churn / low): GAP vs absorption flag |
| Impulse MACD | https://in.tradingview.com/script/qt6xLfLi-Impulse-MACD-LazyBear | not shown | trend state: overlaps the 6-state MOMENTUM map in MTS_PLAYBOOK.md:32 and RSI layers. Not shortlisted |
| Others named in the ask (Klinger, Relative Volatility, Chandelier) | - | - | Search returned no LazyBear page for them; not assessed |

## 2. Shortlist (4; each a separate switchable layer, tag [SCREENER], never a Tom filter, read-only contract per PROJECT_VISION)

### S1. Squeeze Momentum (priority 1)
- **Computes:** volatility-compression flag when Bollinger Bands sit inside Keltner Channels (sqzOn = lowerBB > lowerKC and upperBB < upperKC; sqzOff the opposite), plus a linear-regression momentum
  histogram: `linreg(close - avg(avg(highest(high,20), lowest(low,20)), sma(close,20)), 20, 0)`. Derived from Carter's TTM Squeeze. Source: close.
- **Verified parameters [PINE]:** BB length 20, BB mult 2.0, KC length 20, KC mult 1.5, useTrueRange true (KC range = TR, SMA 20), momentum linreg length 20 (= KC length), offset 0.
- **Correction (vs Cloud draft):** the draft's momentum linreg length "20 [MEMORY]" is confirmed. **Bug in the displayed source:** `dev = multKC * stdev(...)` uses the KC multiplier (1.5) for the BB deviation; the author's note (2014-09-29) says the BB multiplier
  was stuck at 1.5 and points to an updated pastebin (not opened). Build with BB dev = 2.0 * stdev(close,20) (the `mult` input), not the as-displayed code.
- **One-line reason:** MTS has no volatility-compression read; BTC "needs to break out" is the operator's ask 1 and a squeeze state is
  the only LazyBear item that says *when a range is loaded*.
- **Port cost:** ~4 h (SMA, stdev, ATR/TR, linreg on klines already in data/klines/).
- **Draft file:** `MyTradingSys/backtest/layers/volatility/squeeze_momentum.py` (+ `test_squeeze_momentum.py`)
- **Source:** https://www.tradingview.com/script/nqQ1DT5a-Squeeze-Momentum-Indicator-LazyBear/

### S2. Better Volume Indicator (priority 2)
- **Computes:** per bar, splits volume into an up/down share by range (`range = true range`; `v1` = buy-share formula chosen by close>=open, `v2 = v - v1`), builds 22 derived series (v1..v22: volume x range, volume / range, differences,
  and 2-bar sums over `highest(high,2)-lowest(low,2)`), and flags a bar when a series equals its `length`-bar extreme (c1..c20). Classes: climax-up (red), climax-down (white), churn (green), climax-churn (purple #8B008B), low volume (yellow), default cyan. Plots volume columns coloured by class plus `sma(volume, length)`.
- **Verified parameters [PINE]:** length (Lookback) = 8; use2Bars = true; lowVol / climaxUp / climaxDown / churn / climaxChurn = true; enableBarColors = false. 2-bar window = `highest(high,2)`/`lowest(low,2)`. No other numeric constants except `(2+(range*range)/10)` inside the v1 formula.
- **Correction (vs Cloud draft):** the draft's "lookback and thresholds [MEMORY, unverified]" is wrong on two points: lookback is 8 and there are **no thresholds**; classification is "series equals its 8-bar extreme". The v1 expression is long and has an operator-precedence quirk in the down-bar branch
  (`... / (2+(range*range)/10) * range + (close - open)`); port it literally, then test, or the layer will not match TradingView.
- **One-line reason:** "high-volume churn" is effort-without-result at bar level, the klines-only cousin of the absorption flag, so
  it can be backtested on 5m/15m/1h history where aggTrade CVD does not exist.
- **Port cost:** ~4 h (revised up from 3: 22 series and 20 conditions).
- **Draft file:** `MyTradingSys/backtest/layers/volume/better_volume.py`
- **Source:** https://www.tradingview.com/script/LfVJhuir-Indicators-Better-Volume-Indicator-InstrumentVolume/

### S3. WaveTrend with Crosses (already open as T061; priority 3)
- **Computes:** `ap = hlc3; esa = ema(ap, n1); d = ema(abs(ap - esa), n1); ci = (ap - esa) / (0.015 * d); wt1 = ema(ci, n2); wt2 = sma(wt1, 4)`; cross markers where wt1 crosses wt2, bar colour on cross.
- **Verified parameters [PINE]:** n1 (Channel Length) 10, n2 (Average Length) 21, obLevel1 60, obLevel2 53, osLevel1 -60, osLevel2 -53, signal SMA length 4 (hard-coded), 0.015 constant. Matches the T061 numbers; no correction.
- **Provenance flag:** the page at in.tradingview.com/v/jFQn4jYZ/ is listed as an indicator **by lonestar108** (a republish dated 2016-02-21); the code header says `@author LazyBear`. LazyBear's own WaveTrend Oscillator [WT] page was not opened here; the math and defaults are the standard LazyBear WT.
- **One-line reason:** only oscillator on the list that carries divergence, which the operator named as a gap; do not open a second item.
- **Port cost:** ~3 h (math already written in T061).
- **Draft file:** `MyTradingSys/backtest/layers/momentum/wavetrend.py`
- **Source:** https://in.tradingview.com/script/jFQn4jYZ-WaveTrend-with-Crosses-LazyBear/

### S4. Volume Flow Indicator (priority 4)
- **Computes:** Katsanos VFI: `typical = hlc3; inter = log(typical) - log(typical[1]); vinter = stdev(inter, 30); cutoff = coef * vinter * close; vave = sma(volume, length)[1]; vmax = vave * vcoef; vc = min(volume, vmax);
  mf = typical - typical[1]; vcp = vc if mf > cutoff, -vc if mf < -cutoff, else 0; vfi = sum(vcp, length) / vave` (optional 3-bar SMA); signal `vfima = ema(vfi, signalLength)`; optional histogram vfi - vfima.
- **Verified parameters [PINE]:** length 130, coef 0.2, vcoef (max volume cutoff) 2.5, signalLength 5, smoothVFI false (3-bar SMA when true), stdev window 30 (hard-coded), showHisto false.
- **Correction (vs Cloud draft):** the draft's "coefficient 0.2 for daily and 0.1 for intraday [SEARCH]" describes Katsanos' guidance; the script default is 0.2 for all timeframes. length 130 and vcoef 2.5 replace the [MEMORY] values; signal 5 is new. Page shows 27K / 106.
- **One-line reason:** only worth it as a klines-history stand-in for CVD; on live data aggTrade CVD is the better source, so it is the weakest fit.
- **Port cost:** ~3 h.
- **Draft file:** `MyTradingSys/backtest/layers/volume/volume_flow.py`
- **Source:** https://www.tradingview.com/script/MhlDpfdS-Volume-Flow-Indicator-LazyBear/

## 3. ROI note and next step

Build order S1, S2, S3; S4 only if a klines-only backtest of CVD-like flow is wanted. Total ~10-13 h for S1-S3. The four source pages were opened on Desktop 2026-10-05 and the [MEMORY]/[SEARCH] tags replaced (section 0); still open: the Squeeze updated pastebin and the BB-mult fix. No layer touches execution/ or layers/alerts/. Each layer needs a fail-first test (CLAUDE.md gate) and outputs a
flag only; promotion past SCREENER needs a backtest per PROJECT_VISION point 4.
