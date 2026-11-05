# RESULT: big-candle stories, top-trader read, phase (descriptive, fee-free, no trade rule)

Operator ask 2026-11-05 (d-bigcandle-story-toptraders-1105). Pre-registration: PRE_REG.md (frozen before any outcome column was read). Full tables: tables.md; 11-04 detail: walkthrough.md; rerun: `python MyTradingSys/research/bigcandle_story_2026-11-05/study.py` (data: fetch_data.py).

**Headline: the story is worth reading, the odds are not a signal.** A big hour tells you what the money did (new longs, short covering, long liquidation). It does not tell you where price goes next: continuation stays 43-60 % against a 45-50 % baseline, and the cell the operator asked about (size long / accounts short after a big up candle) is not different from baseline.

Regime mix: 1h events bull 27 % / bear 27 % / range 46 % (30-day band); weekly streak groups R3+ 124, R1-2 350, G1-2 286, G3+ 83 events. 843 big 1h events, 3,991 big 5m events (12-bar lockout), 21,831 1h bars as baseline. DEV 2022-01-03 .. 2024-06-30 only; holdout not read.

## 1. The 2026-11-04 walk-through (Eagle_Eyes hand read, reproduced)

| Hand read | Recomputed | Match |
|---|---|---|
| 02:55-03:00Z flush to 76,019, new shorts: OI +381 BTC, taker delta -3,278 | two bars 02:55+03:00: close 76,019, OI +381, delta -3,279 | yes (1 BTC rounding) |
| "the day's bottom" | the 03:05 bar wicks lower, 75,690; 76,019 is the 03:00 bar close | partly: the low is 329 lower |
| top-trader accounts ratio rose 2.68 -> 2.80 over the flush | class over the hour is BU (positions and accounts both up) | direction yes |
| 14:35-15:10 rally 78.6k -> 80.8k mostly short covering, OI -2,862 over the big bars | OI on the four big-OI bars 14:35, 15:00, 15:05, 15:10 = -2,862 (4 bars, not 5; all 7 bars sum -1,299) | yes |
| 14:40 one new-longs bar, delta +3,471 | 14:40 bar: price +0.96 %, OI +207, delta +3,471, story UP/UP/BUY | yes |
| day OI -2,814 BTC | -2,815 (stamps 00:05 to 23:55; the 11-05 file is not published yet) | yes |
| top-trader positions 1.72 -> 1.92 | 1.72 -> 1.92 | yes |
| top-trader accounts 2.43 -> 1.48; global accounts 2.31 -> 1.39 | 2.43 -> 1.48; 2.31 -> 1.39 | yes |
| 4 consecutive red weeks 10-05..10-26, week of 11-02 green | red weeks 10-05, 10-12, 10-19, 10-26 = 4 (week of 09-28 was green); week of 11-02 open 78,313, last close 80,466 = green | yes; the operator's "5" does not match Binance futures: it is 4 |
| 11-05 12:00-13:00Z drop (CoinGlass screenshot) | UNREPRODUCED: data.binance.vision has not published 11-05 yet | no |

Reading of the day, plain words: the 02:55 dump was sellers opening new shorts, while the top traders (size and head count) were adding longs that hour, the opposite side of the dump. The 14:40-15:10 rally was mostly shorts closing, with one genuine new-longs bar; through the rally the big accounts' size went longer while the head count went shorter (class SL every hour 14:00-16:00). Over the whole day size went longer (1.72 -> 1.92) while accounts went much shorter (2.43 -> 1.48): a few big long positions against many short accounts. Phase at 11-04: 4 red weeks behind it (R3+); the 30-day band was bear early in the day, then range.

What the DEV table says about those hours (same pick order the page uses; n >= 30 only):

| 11-04 hour | story | top class | cell used | n | price continues 1h / 4h / 24h |
|---|---|---|---|---|---|
| 02:00 | DOWN/DOWN/SELL | both up | story + class | 91 | 43 % / 50 % / 45 % |
| 04:00 | UP/DOWN/BUY | size long / accounts short | + band range | 37 | 35 % / 35 % / 49 % |
| 14:00 | UP/UP/BUY | size long / accounts short | story + class | 43 | 44 % / 56 % / 60 % |
| 15:00 | UP/DOWN/BUY | size long / accounts short | + band range | 37 | 35 % / 35 % / 49 % |

## 2. Base rates (1h bars; 95 % Wilson CI; n < 30 THIN; continue = close H later beyond the event close in the event direction)

Baseline, every 1h bar: UP bars continue 47 % / 48 % / 50 % at 1h / 4h / 24h (n 11,064); DOWN bars 45 % / 47 % / 48 % (n 10,767). Phase barely moves it (every band and streak 44-51 %).

| Cell (big 1h hour) | n | 1h | 4h | 24h | read |
|---|---|---|---|---|---|
| UP/UP/BUY new longs, rally | 180 | 52 % [45-59] | 59 % [51-66] | 58 % [50-64] | the one cell above baseline at 4h (+11 pp); 1 of about 25 cells looked at, so a lead |
| UP/DOWN/BUY short covering | 223 | 46 % [40-53] | 45 % [39-52] | 51 % [44-57] | baseline |
| DOWN/DOWN/SELL long liquidation | 269 | 43 % [37-49] | 46 % [40-52] | 46 % [41-52] | baseline; only 3 % are fully retraced within 1h, 28 % within 24h (baseline 44 %): a flush hour mostly stays flushed |
| DOWN/UP/SELL new shorts | 117 | 44 % [35-53] | 44 % [36-54] | 45 % [37-54] | baseline |
| DOWN/DOWN/SELL x size short / accounts long | 46 | 41 % [28-56] | 33 % [21-47] | 39 % [26-54] | below baseline at 4h, a lead only |
| the other 3 stories | 10-16 | | | | THIN |

### The size-long / accounts-short question (class SL after a big UP candle)

| Set | n | 1h | 4h | 24h | baseline UP |
|---|---|---|---|---|---|
| 1h, price itself big, UP, SL | 51 | 45 % [32-59] | 53 % [40-66] | 51 % [38-64] | 47 / 48 / 50 |
| ... streak R1-2 | 30 | 43 % [27-61] | 50 % [33-67] | 53 % [36-70] | 46 / 48 / 50 |
| ... streak R3+ (where 11-04 sits) | 3 | THIN | THIN | THIN | |
| ... streak G1-2 / G3+ | 12 / 6 | THIN | THIN | THIN | |
| ... band range / bull / bear | 27 / 20 / 4 | THIN | THIN | THIN | |
| 5m bars, price big, UP, SL (60-min lockout) | 136 | 46 % [38-55] | 45 % [37-53] | 45 % [37-54] | 49 / 50 / 50 |
| ... streak G1-2 | 52 | 46 % [33-60] | 35 % [23-48] | 42 % [30-56] | 49 / 50 / 50 |
| ... streak R1-2 | 47 | 40 % [28-55] | 47 % [33-61] | 41 % [28-56] | |
| ... streak G3+ / R3+ | 29 / 8 | THIN | | | |

**Answer: no.** The CI of every measured SL cell contains the baseline (47-50 %), except the 5m / streak G1-2 / 4h cell (35 %, CI 23-48, below 50 %), one of dozens of cells, so a lead and not a finding. In the phase the operator highlighted (3+ red weeks) there are only 3 (1h) and 8 (5m) such events in the DEV window: effectively UNMEASURED. Short-covering rallies carrying the SL class (UP/DOWN/BUY/SL, n 60) continue less at 1h (37 %, CI 26-49; baseline 47 %): the page's 15:00 hour cell.

### 5m bars (n large, 60-min lockout)
Big 5m long-liquidation flushes (DOWN/DOWN/SELL, n 1,437) continue only 42 % at 1h (CI 40-45) and 41 % at 4h against a 48 % DOWN baseline; big 5m short-covering rallies (UP/DOWN/BUY, n 1,273) 45 % / 45 % against 49 % / 50 %. Big 5m bars lean 4-7 pp toward partial give-back in both directions. Descriptive, fee-free: at 0.05 % a side this is not a trade.

## 3. How to read it, and limits
- Top-trader ratios are blank for most of 2022: top-trader classes exist only from about 2022-12 to 2024-06 (303 of 843 hourly events are NA, 302 of them in 2022). Cells with a top-trader class are 19 months of data.
- 1h events: 4h and 24h outcomes overlap between neighbouring hours, so the CIs are optimistic. Many cells were read; about 5 % of them will look different by chance.
- DEV is a 2022 bear, 2023 recovery and early-2024 bull; 2026 conditions are not tested here. Holdout untouched, so nothing here is out-of-sample for a later use.
- Story signs use the plain sign of price, OI change and delta; if the quiet one of the three is tiny, its sign is noise. Not filtered (OURS, stated).
- Prior art: no earlier top-trader outcome study on trunk (only the data fetch backtest/fetch_futures_metrics.py). CoinGlass pages were not opened in this tree; its top-trader long/short charts are believed to redisplay Binance's own top-trader ratios, the series used here (to verify when a browser session is free).
- Other-venue top-trader data (Bybit, OKX): UNMEASURED, no history on disk.

## 4. Parameters
| Parameter | Value | Label |
|---|---|---|
| BTCUSDT USD-M 1m klines, metrics 5m (OI, top-trader positions / accounts ratio) | Binance | SOURCED |
| Metrics stamp = bar close | data.binance.vision format | SOURCED |
| Big = abs z >= 3 vs trailing 30 days, prior bars only | 3 sd, 30 d | OURS |
| 5m event lockout | 12 bars | OURS |
| Top-trader flat band | 0.2 % relative change over 60 min | OURS |
| Phase band | +-10 % over 30 days (as anticipation_map) | OURS |
| Weekly streak | futures 5m closes vs opens, Monday 00:00 UTC, groups R3+/R1-2/G1-2/G3+ | OURS |
| Outcome horizons | 1h, 4h, 24h; continue and undone definitions in PRE_REG | OURS |
| THIN | n < 30 | OURS |
| Wilson 95 % CI | z 1.96 | SOURCED (standard) |

## 5. Runtime wiring and source of truth
- Rates file: MyTradingSys/tools/live_aid/bigcandle_rates.js (built by study.py; 1h cells: story, story + class, + 30-day band, + weekly streak, direction x class, baselines). Page panel "Big candle story" in live_aid.html beside "Same data, other readings": the live hour's story, top-trader class (Binance futures/data topLongShortPositionRatio and topLongShortAccountRatio over the last 60 min), phase (1d and 1w klines), then the most specific cell with n >= 30 (MEASURED), else THIN (not used) or UNMEASURED, plus the same-direction baseline. Tests: test_live_aid.py -k bigcandle; research/bigcandle_story_2026-11-05/test_bigcandle_story.py (in run_all_tests.py PYTEST_LAYER_PATHS). The page is not the live tree: nothing in .mts_live or any live runner changed.
- Not wired (needs a coordinator deploy and a pre-registered rule): the live runner / engine consuming these cells. Raw card filed (positioning family).
- Index: layer_map.json backtest row `BIGCANDLE-STORY-1H-20261105` (layer oi_delta, positioning family) shows in LAYERS.md; the operator decision is d-bigcandle-story-toptraders-1105 in system/OPERATOR_DECISIONS.md.
