Counts: Total: 64 | SOURCED: 24 | OURS: 40
# Live Aid & Analyst Levels Parameter Labels (`file:line` sweep)

Date: 2026-10-31  
Card: `gemini-param-labels-live-aid-analyst-levels`  


## Summary

- **Total numeric parameters / structural constants swept**: 64
- **SOURCED count**: 24
- **OURS count**: 40
- **UNLABELED count**: 0

Audit of all numeric constants and parameter defaults across:
1. `MyTradingSys/tools/live_aid/live_aid_indicators.js`
2. `MyTradingSys/tools/live_aid/us_open_rates.js`
3. `scripts/dev/analyst_levels.py`

---

## 1. Parameters in `MyTradingSys/tools/live_aid/live_aid_indicators.js`

| Parameter / Constant | File:Line | Default Value | Label | Source / Citation / Notes |
|---|---|---|---|---|
| `rsi n` default length | `MyTradingSys/tools/live_aid/live_aid_indicators.js:35` | `14` | `SOURCED` | Operator's chart setup / standard Wilder RSI length 14 (`live_aid_indicators.js:2`, `FORMULAS.md` s14). |
| `rsi neutral midpoint` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:45` | `50` | `SOURCED` | Standard RSI range midpoint / neutral level (`FORMULAS.md` s14). |
| `rsi max / scale factor` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:45-46` | `100` | `SOURCED` | Standard RSI scale factor $100 - 100 / (1 + RS)$ (`FORMULAS.md` s14). |
| `bollinger n` default period | `MyTradingSys/tools/live_aid/live_aid_indicators.js:51` | `20` | `SOURCED` | Operator's chart setup (BB 20, 2) (`live_aid_indicators.js:2`, `FORMULAS.md` s8). |
| `bollinger k` default multiplier | `MyTradingSys/tools/live_aid/live_aid_indicators.js:51` | `2` | `SOURCED` | Operator's chart setup (BB 20, 2) (`live_aid_indicators.js:2`, `FORMULAS.md` s8). |
| `atr n` default length | `MyTradingSys/tools/live_aid/live_aid_indicators.js:66` | `14` | `SOURCED` | Operator's chart setup / standard Wilder ATR length 14 (`live_aid_indicators.js:2`, `FORMULAS.md` s12). |
| `DAY` ms per day | `MyTradingSys/tools/live_aid/live_aid_indicators.js:75` | `86400000` | `SOURCED` | Standard milliseconds in 24 hours ($24 \times 60 \times 60 \times 1000$). |
| `dayVwap typical price divisor` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:81` | `3` | `SOURCED` | Standard typical price calculation $\frac{H + L + C}{3}$ (`live_aid_indicators.js:2`). |
| `wavetrend warmup` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:112` | `200` | `OURS` | Repo EMA stabilization warm-up suppression mask (`live_aid_indicators.js:110`: "`warmup` valid bars (200, OURS)"). |
| `wavetrend a1` smoothing constant | `MyTradingSys/tools/live_aid/live_aid_indicators.js:113` | `2 / 11` | `SOURCED` | LazyBear's WaveTrend EMA smoothing factor for $N_1 = 10$ ($2 / (10 + 1)$); `FORMULAS.md` s20. |
| `wavetrend a2` smoothing constant | `MyTradingSys/tools/live_aid/live_aid_indicators.js:113` | `2 / 22` | `SOURCED` | LazyBear's WaveTrend EMA smoothing factor for $N_2 = 21$ ($2 / (21 + 1)$); `FORMULAS.md` s20. |
| `wavetrend flat window dev tol` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:123` | `1e-9` | `OURS` | Repo flat window zero-deviation tolerance (`live_aid_indicators.js:109`). |
| `wavetrend Lambert CCI factor` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:124` | `0.015` | `SOURCED` | Lambert's Commodity Channel Index (CCI) constant adopted in LazyBear's formula (`FORMULAS.md` s20). |
| `wavetrend w2 sma period` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:128` | `4` | `SOURCED` | LazyBear's WaveTrend signal line SMA length 4 (`FORMULAS.md` s20). |
| `IT.divWin` divergence half-window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` | `15` | `OURS` | Discretization: 15 bars half-window for local extrema search (`live_aid_indicators.js:152`: "Every threshold below = OURS"). |
| `IT.flowShortMs` short flow delta window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` | `60000` | `OURS` | Discretization: 60 s net taker volume delta window (`STEPS.md:27`). |
| `IT.flowLongMs` CVD window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` | `900000` | `OURS` | Discretization: 15 min (900 s) cumulative volume delta window (`STEPS.md:27`). |
| `IT.squeezeEps` price/OI change tolerance | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` | `0.0005` | `OURS` | Discretization: 0.05% change threshold for price/OI moves (`live_aid_indicators.js:187`). |
| `IT.domPct` order book band | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` | `0.0025` | `OURS` | Discretization: $\pm 0.25\%$ depth band around current price (`live_aid_indicators.js:197`). |
| `IT.domImb` order book imbalance threshold | `MyTradingSys/tools/live_aid/live_aid_indicators.js:154` | `0.2` | `OURS` | Discretization: 20% imbalance threshold for order book skew flag (`live_aid_indicators.js:234`). |
| `IT.vwapBars` evaluation window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:155` | `5` | `OURS` | Discretization: last 5 bars window for VWAP test (`live_aid_indicators.js:214`). |
| `IT.supportN` nearest levels count | `MyTradingSys/tools/live_aid/live_aid_indicators.js:155` | `2` | `OURS` | Discretization: show 2 nearest support/resistance levels (`live_aid_indicators.js:210`). |
| `IT.reduceAt` against flags threshold | `MyTradingSys/tools/live_aid/live_aid_indicators.js:155` | `3` | `OURS` | Rule R threshold: trigger reduce recommendation when 3 or more flags are against (`live_aid_indicators.js:221,238`). |
| `IT.feedMs` live feed freshness | `MyTradingSys/tools/live_aid/live_aid_indicators.js:155` | `30000` | `OURS` | Discretization: 30 s maximum trade/ticker silence before marking feed inactive (`live_aid_indicators.js:183`). |
| `CP.coilPct` width percentile | `MyTradingSys/tools/live_aid/live_aid_indicators.js:244` | `0.20` | `OURS` | BB width $\le 20\text{th}$ percentile defines coil (`research/pre_us_squeeze_2026-10-29`, `live_aid_indicators.js:243`). |
| `CP.lookback` history bars | `MyTradingSys/tools/live_aid/live_aid_indicators.js:244` | `2880` | `OURS` | 2880 bars lookback window (30 days of 15m bars) for width percentile ranking (`research/pre_us_squeeze_2026-10-29`). |
| `CP.pierceAgeMax` maximum age | `MyTradingSys/tools/live_aid/live_aid_indicators.js:244` | `8` | `OURS` | 8 bars maximum recency for BB pierce event (`research/bb_pierce_force_2026-10-29`). |
| `CP.volStrong` volume ratio | `MyTradingSys/tools/live_aid/live_aid_indicators.js:244` | `3.56` | `OURS` | Volume surge threshold for strong force ($3.56\times$ baseline) (`research/bb_pierce_force_2026-10-29`). |
| `CP.volWeak` volume ratio | `MyTradingSys/tools/live_aid/live_aid_indicators.js:244` | `1.96` | `OURS` | Volume threshold below which force is classified as weak ($< 1.96\times$) (`research/bb_pierce_force_2026-10-29`). |
| `CP.deltaWith` taker delta share | `MyTradingSys/tools/live_aid/live_aid_indicators.js:244` | `0.10` | `OURS` | Directional delta share threshold ($> 10\%$) for strong force (`research/bb_pierce_force_2026-10-29`). |
| `CP.dist buckets` thresholds | `MyTradingSys/tools/live_aid/live_aid_indicators.js:245` | `0.005, 0.015, Infinity` | `OURS` | Discretization: distance buckets $\le 0.5\%$, $\le 1.5\%$, $> 1.5\%$ (`research/bb_pierce_force_2026-10-29`). |
| `LQ.bigUsd` large liquidation size | `MyTradingSys/tools/live_aid/live_aid_indicators.js:276` | `100000` | `OURS` | Discretization: $\$100,000$ threshold for large liquidation event (`live_aid_indicators.js:274`). |
| `LQ.domRatio` dominance ratio | `MyTradingSys/tools/live_aid/live_aid_indicators.js:276` | `2` | `OURS` | Discretization: $2\times$ ratio for long vs short liquidation dominance (`live_aid_indicators.js:288`). |
| `LQ.keepMs` liquidation retention window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:276` | `900000` | `OURS` | Discretization: 15 min (900 s) rolling liquidation memory buffer. |
| `LQ.tapeN` max tape items | `MyTradingSys/tools/live_aid/live_aid_indicators.js:276` | `8` | `OURS` | Discretization: display top 8 recent liquidation events. |
| `LQ.liveMs` stream freshness window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:276` | `60000` | `OURS` | Discretization: 60 s inactivity timeout for liquidation feeds. |
| `FD.zero` funding zero deadband | `MyTradingSys/tools/live_aid/live_aid_indicators.js:294` | `0.00001` | `OURS` | Discretization: under 0.001% per 8h ($1\times 10^{-5}$) considered flat/zero (`live_aid_indicators.js:293`). |
| `FD.high` funding high threshold | `MyTradingSys/tools/live_aid/live_aid_indicators.js:294` | `0.0003` | `OURS` | Discretization: 0.03% ($3\times 10^{-4}$) per 8h ($3\times$ baseline) considered high (`live_aid_indicators.js:293`). |
| `FD.perYear` periods per year | `MyTradingSys/tools/live_aid/live_aid_indicators.js:294` | `1095` | `SOURCED` | Exact count of 8h funding periods in a standard 365-day year ($365 \times 3 = 1095$). |
| `NW.mark` news importance threshold | `MyTradingSys/tools/live_aid/live_aid_indicators.js:325` | `7` | `OURS` | Discretization: Tree News importance score $\ge 7$ marked high (`research/news_feeds_2026-10-30`, `live_aid_indicators.js:323`). |
| `NW.winMs` news evaluation window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:325` | `3600000` | `OURS` | Discretization: 60 min ($3,600,000$ ms) lookback window for news pulse (`live_aid_indicators.js:323`). |
| `NW.event` news event threshold count | `MyTradingSys/tools/live_aid/live_aid_indicators.js:325` | `3` | `OURS` | Discretization: 3 or more high-importance news items triggers EVENT level (`live_aid_indicators.js:323`). |
| `AV.freshDays` analyst view expiry | `MyTradingSys/tools/live_aid/live_aid_indicators.js:348` | `3` | `OURS` | Discretization: analyst views older than 3 days are marked STALE (`live_aid_indicators.js:347`). |
| `AV.band` display band | `MyTradingSys/tools/live_aid/live_aid_indicators.js:348` | `6` | `OURS` | Discretization: $\pm 6\%$ distance band around current price for level filtering (`live_aid_indicators.js:347,375`). |
| `AV.at` AT zone distance | `MyTradingSys/tools/live_aid/live_aid_indicators.js:348` | `0.3` | `OURS` | Discretization: $\le 0.3\%$ classified as AT zone (`live_aid_indicators.js:348,374`). |
| `AV.near` NEAR zone distance | `MyTradingSys/tools/live_aid/live_aid_indicators.js:348` | `1.5` | `OURS` | Discretization: $\le 1.5\%$ classified as NEAR zone (`live_aid_indicators.js:348,374`). |
| `AV.merge` zone cluster tolerance | `MyTradingSys/tools/live_aid/live_aid_indicators.js:348` | `0.25` | `OURS` | Discretization: levels within 0.25% merged into single zone (`live_aid_indicators.js:348,382`). |
| `UO.windowMs` US open window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:412` | `7200000` | `OURS` | Discretization: 2 h ($7,200,000$ ms, 120 min) forward window from open (`research/us_open_levels_2026-10-30/study.py`). |
| `UO.orMs` opening range window | `MyTradingSys/tools/live_aid/live_aid_indicators.js:412` | `900000` | `OURS` | Discretization: first 15 min ($900,000$ ms) opening range window (`study.py`). |
| `UO.buckets` distance bins | `MyTradingSys/tools/live_aid/live_aid_indicators.js:412` | `0, 0.0025, 0.005, 0.01, 0.02, 9` | `OURS` | Discretization: 5 distance buckets (0-0.25%, 0.25-0.5%, 0.5-1%, 1-2%, 2%+) (`study.py:27`). |
| `UO touch/held sample threshold` | `MyTradingSys/tools/live_aid/live_aid_indicators.js:435` | `30` | `OURS` | Discretization: minimum sample count $n \ge 30$ to display measured touch/held rates (`live_aid_indicators.js:435`). |

---

## 2. Parameters in `MyTradingSys/tools/live_aid/us_open_rates.js`

| Parameter / Constant | File:Line | Default Value | Label | Source / Citation / Notes |
|---|---|---|---|---|
| `days` sample count | `MyTradingSys/tools/live_aid/us_open_rates.js:2` | `1230` | `SOURCED` | Measured sample count of weekdays in BTCUSDT 1m 2022-01-01..2026-09-26 (`research/us_open_levels_2026-10-30/RESULT.md:3`). |
| `window_min` evaluation window | `MyTradingSys/tools/live_aid/us_open_rates.js:2` | `120` | `OURS` | Discretization: 120-minute forward evaluation window from US open (`research/us_open_levels_2026-10-30/study.py:26`). |
| `hold_min` hold evaluation window | `MyTradingSys/tools/live_aid/us_open_rates.js:2` | `60` | `OURS` | Discretization: 60-minute holding horizon after first touch (`research/us_open_levels_2026-10-30/study.py:26`). |
| `buckets` distance intervals | `MyTradingSys/tools/live_aid/us_open_rates.js:2` | `0-0.25, 0.25-0.5, 0.5-1, 1-2, 2+` | `OURS` | Discretization: percentage distance bins relative to open price (`research/us_open_levels_2026-10-30/study.py:27`). |

---

## 3. Parameters in `scripts/dev/analyst_levels.py`

| Parameter / Constant | File:Line | Default Value | Label | Source / Citation / Notes |
|---|---|---|---|---|
| `LO` price clamp minimum | `scripts/dev/analyst_levels.py:21` | `40_000` | `OURS` | Repo sanity floor for BTCUSDT analyst target extraction ($40,000) (`analyst_levels.py:21`). |
| `HI` price clamp maximum | `scripts/dev/analyst_levels.py:21` | `200_000` | `OURS` | Repo sanity ceiling for BTCUSDT analyst target extraction ($200,000) (`analyst_levels.py:21`). |
| `spot_1h limit` kline limit | `scripts/dev/analyst_levels.py:65` | `1000` | `SOURCED` | Binance public REST API v3 klines default batch limit (max 1000 candles per query). |
| `spot_1h default timeout` | `scripts/dev/analyst_levels.py:63` | `15` | `OURS` | Repo HTTP socket timeout in seconds for Binance public API fetch. |
| `hit_from delay` days to hit eligibility | `scripts/dev/analyst_levels.py:73` | `1` | `OURS` | Lookahead prevention policy: hit eligibility begins 00:00 UTC day after publish (`analyst_levels.py:11`). |
| `render default width` | `scripts/dev/analyst_levels.py:86` | `90` | `OURS` | CLI formatting column text width. |
| `hook_block default days` | `scripts/dev/analyst_levels.py:108` | `7` | `OURS` | Screenshot hook lookback window in days. |
| `hook_block default band_pct` | `scripts/dev/analyst_levels.py:108` | `6.0` | `OURS` | Screenshot hook price proximity filter band ($\pm 6.0\%$). |
| `hook_block timeout` | `scripts/dev/analyst_levels.py:117` | `3` | `OURS` | Fast timeout in seconds for hook context execution. |
| `main default days` | `scripts/dev/analyst_levels.py:127` | `10` | `OURS` | Default CLI lookback window in days for analyst levels retrieval. |
