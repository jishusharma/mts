SOUND — RSI and Bollinger Bands match; WaveTrend formula agrees when display warmup is disabled, while default display is unavailable on the 60-bar slice.

## Checked

- `MyTradingSys/backtest/layers/FORMULAS.md:10-25` (Wilder RSI), `:554-558` (population Bollinger), and `:516-528` (WaveTrend formula and 200-bar output warmup).
- `MyTradingSys/tools/live_aid/live_aid_indicators.js:1-4, 29-83, 112-143` (defaults and indicator implementations; lines may vary with subsequent edits).
- `MyTradingSys/tools/live_aid/fixture_klines.json` (first 60 rows selected from its 300-row BTCUSDT 1m fixture; bars used: `klines[-60:]`, ending open time 1793077140000).
- Command: `node -e` requiring the fixture and module, slicing `klines[-60:]`, converting with `columns`, and evaluating RSI(14), Bollinger(20,2), and WaveTrend(10,21,4) at index 59. Default WT warmup produced `NaN`; a second call with `warmup=1` exposed its formula result for comparison.
- Independent arithmetic followed the written recurrences in FORMULAS.md, using close deltas for RSI, the final 20 closes for Bollinger and hlc3 for WaveTrend. No DEV market data was needed; no bars beyond the fixture's final bar were used.

## Results

| Indicator | Independent result, last bar | JS result | Verdict |
|---|---:|---:|---|
| RSI(14) | 61.07642488667503 | 61.07642488667503 | SAME (delta 0 at shown precision) |
| BB(20,2) | mid 79654.35; upper 79713.09076948764; lower 79595.60923051237 | same | SAME (deltas 0 at shown precision) |
| WaveTrend wt1 / wt2 | 12.685705290075076 / -3.612935767307628 | same with explicit `warmup=1`; default `warmup=200` returns NaN for both on this 60-bar slice | DIFF in availability: default output is absent; formula math matches when made observable. No numerical delta can be asserted against a default value. |

WaveTrend's default warmup means the code requires 200 contiguous valid bars before exposing a value. Thus the requested last-60-bars-only input cannot yield a numeric default WT value. The 1-bar-warmup call is a diagnostic comparison, not a claim that the default is numeric. This is a scoped availability finding, not evidence the deployed default formula is numerically wrong.

## Parameter provenance

| Parameter / convention | Tag | Basis |
|---|---|---|
| RSI length 14 | SOURCED | operator chart setup, JS header `live_aid_indicators.js:2`; FORMULAS.md section 1 specifies Wilder RSI |
| RSI SMA seed across first 14 deltas; Wilder recursion | SOURCED | FORMULAS.md `:12-25` |
| Flat RSI maps to 50 | OURS | explicit deviation in FORMULAS.md `:20-24` and JS `rsi` |
| BB length 20, multiplier 2 | SOURCED | operator chart setup, JS header; FORMULAS.md `:556` |
| BB standard deviation is population (divide by n) | SOURCED | TradingView `ta.bb` convention stated in FORMULAS.md `:556` |
| WaveTrend ap=hlc3, ESA 10, deviation EMA 10, CI scale 0.015, WT1 EMA 21, WT2 SMA 4 | SOURCED | LazyBear formula as recorded in FORMULAS.md `:518-521` |
| WaveTrend EMA seeds on first valid value | OURS | FORMULAS.md `:522` |
| WaveTrend 200-valid-bar warmup | OURS | FORMULAS.md `:522`; JS default at `wavetrend` |
| WaveTrend near-zero deviation cutoff `1e-9*abs(ap)` | OURS | FORMULAS.md `:522`; JS `wavetrend` |

## Findings

| Severity | Location | Finding and evidence | Proposed fix |
|---|---|---|---|
| LOW | `MyTradingSys/tools/live_aid/live_aid_indicators.js` (`wavetrend`, comment above function); `MyTradingSys/backtest/layers/FORMULAS.md:522` | MATCH: a 60-bar diagnostic call with warmup 1 returns wt1 12.685705290075076 and wt2 -3.612935767307628, matching independent recurrence; default 200-bar setting returns NaN. The fixture itself has 300 bars, so the full fixture can support default-warmup evaluation, but the specifically requested last-60 slice cannot. | For a numeric parity check, calculate on the full fixture and compare its final output, or explicitly label the last-60 calculation as formula-only. No code change filed. |

Follow-up cards created: none.
