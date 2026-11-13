# ADX/DI inventory, 2026-11-13 (card adx-inventory-1113)

Read-only inventory of what MTS already holds. No new run, no new number. SOURCED = a named person says it; OURS = our inference/choice.
Paths are relative to `MyTradingSys/`. Next card: adx-di-synthesis-1113.

## 1. What was already studied

| # | Study | Timeframe | Rule / question | n | Result | Fee-net? | Verdict (OURS) |
|---|---|---|---|---|---|---|---|
| 1 | Cross census `research/adx_di_2026-11/CENSUS.md`, DEV 2020-01..2024-06 | 2d (BTC daily-derived) | every DI cross: whipsaw <=3 bars, depth, bars to swing extreme | 56 (red 28, green 28) | whipsaw 32.1%, median depth 14.8%, 16 bars to extreme | No (no entry, no cost) | descriptive only |
| 2 | Same, VALIDATION 2024-07..2025-06 | 2d | same | 15 | whipsaw 46.7%, depth 17.3%, 9 bars | No | descriptive; tiny n |
| 3 | Same, RECENT 2025-07..2026-11 | 2d | same | 17 (16 with whipsaw window) | whipsaw 50.0%, depth 15.0%, 16 bars | No | descriptive; holds CCU cases |
| 4 | ADX bucket x slope (<20, 20-40, >40; falling/rising) | 2d | does ADX at the cross predict whipsaw | DEV: <20 falling 22, 20-40 falling 28, rising 5, >40 1 | whipsaw DEV 31.8% (<20 falling) vs 35.7% (20-40 falling); VALIDATION 14.3% (n 7) vs 75.0% (n 8): ranking flips | No | NO stable bucket effect; >40 and "rising" cells n 0-4 |
| 5 | CCU check, red crosses 2020-01..2025-06 | 2d | where is the low after a red cross | 35 | low within 1-3 bars 37.1% (median -3.6%); 4-7: 20.0%; 8-12: 8.6%; 13-20: 14.3%; 21-30: 20.0% (median -22.9%) | No | a red cross is not reliably followed by a deep fall |
| 6 | CCU's three cases vs census rows | 2d | Oct-2025, Jan-2026, May-2026 | 3 | red 2025-10-09 depth -28.5% (CCU "about 36 %"); red 2026-01-07 -34.1% (CCU 37 %); red 2026-05-23 -25.0% (CCU 26 %). Our depth = 30-bar low vs cross close; his base is not stated | No | his cases are real; they are 3 of the red crosses in the census |
| 7 | Cascade 1d -> 2d, `CENSUS.md` (c) | 1d vs 2d | 2d cross preceded by same-direction 1d cross within 20 days | 56 / 15 / 17 | 92.9% / 80.0% / 88.2% (median lead 4.0 / 8.5 / 13.0 days); 1d crosses followed by a 2d cross within 5 2d bars: 74 of 165 (44.8%) | No | 1d leads 2d; 55% of 1d crosses never reach 2d |
| 8 | Formula check `research/adx_di_2026-11/TV_CROSSCHECK.md` | 1d | adx.py vs TradingView DMI 14/14 | 2 bars x 3 values | match to 0.01; last bar differs 0.80 (partial csv row) | n/a | VERIFIED-TV for 1d. 2d NOT verified (paywalled on his plan) |
| 9 | Live Aid review `research/live_aid_review_2026-11-11/tables.md`, `RESULT.md` | 15m, 1h | ADX/DI side (ADX >= 20) "agrees" with an idea flag | adx15 agrees 234 / against 263; adx1h agrees 296 / against 264 | right after 1h: 50% vs 46%; 49% vs 45%. 4+ of 6 readings agree: 51% (n 144) | No (move %, no fee) | ADX/DI adds nothing to flag hit-rate; RESULT.md: "none feeds a flag or a weight" |
| 10 | Base rates `tools/live_aid/base_rates.js` | 15m, 1h | combos with adx15 / adx1h | e.g. adx15 alone n 1, adx1h+vfi15 n 10 | LOW_N = 30 in base_rates.py: ADX combos seen are below it | No | noise |

Never measured (checked in the files above): any entry/exit rule on ADX/DI, any fee-net or R result, any scalp horizon, any 5d or weekly ADX, any "ADX > x then trade" test.

## 2. What CCU says (SOURCED, copied from `research/cbp/PLAN_ADX_DI_VOLUME_2026-11-07.md` section 1 and `research/adx_di_2026-11/SPEC.md`)

Source video: CCU (Steve), AnAx1PanZm4, 2026-11-05, "WARNING: HISTORY IS REPEATING". No extract file for this video is on trunk: the id appears only in SPEC, PLAN, USAGE_adx.md and two other-topic files, so the quotes below are the PLAN's copies from the caption store, not re-verified here (timestamps UNKNOWN).
`research/cbp/ccu_DXntdN3jfTg_extract.md` is a different video (bull flag, 2026-10-20), captions unavailable (HTTP 429): no ADX content. `research/yt_feed_2026-10-31/CCU_RULES_2026-10-31.md` has no ADX/DI row; its 2-day items are 50/200 MA golden cross, 200 MA reclaim, 21 SMA retest (WaveTrend is on the 12-day).

| Item | What he says | Label |
|---|---|---|
| Chart | 2-day, ADX + DI | SOURCED |
| Settings | none stated (our runs use Wilder n = 14) | UNKNOWN for him; OURS for us |
| Direction | red DI above green = "sellers are in control"; a red cross is "rare" | SOURCED |
| Three steps after a red cross | "1-3 weeks of consolidation", then "falling straight to the bottom", then "the market consolidates and then changes trend" | SOURCED |
| ADX | yellow line = trend strength: "if it rises very high, it means that the trend strength is very powerful" | SOURCED |
| Threshold | no numeric ADX threshold anywhere | SOURCED (absence, PLAN s1) |
| Cases | Oct 2025 about 36 %, "a little over a month"; Jan 2026 about 37 %, "a little less than a month", "the strongest trend in the last few years" on ADX; May 2026 26 % from the cross, 30 % swing to swing | SOURCED |
| Fading | "These dips aren't getting stronger, they're getting a little weaker" | SOURCED |
| 11-05 cross | "less than 24 hours later the lines crossed back"; three possibilities; "watch which signal will actually be confirmed" | SOURCED |
| Trade type | a bearish regime / cycle call over weeks; no entry, stop, long or scalp rule given | OURS (reading of the quotes) |
| "Rare" | census splits sum to 44 red 2d crosses 2020-2026 (DEV 28, VALIDATION 7, RECENT 9); "rare" is his word, we do not confirm it | OURS |

## 3. Where ADX/DI is computed or shown today

| Place | What | TFs | Thresholds | Feeds a flag? |
|---|---|---|---|---|
| `backtest/layers/adx/adx.py` | Wilder `adx_di(n = 14)`, `crosses()`; hand toy FORMULAS s30 | any bars; used for 2d / 1d | none in code | No, research only |
| `research/adx_di_2026-11/census.py` | writes CENSUS.md | 2d, 1d | buckets 20 / 40, slope 5 bars, whipsaw k 1-3 (all OURS) | No |
| `tools/live_aid/indread.js` (own JS port `adx()`) | per-TF cell: value, side, strong | `TFS` = 15m frame, 1h bias, 4h context | `adxTrend` 20, `adxStrong` 25 (OURS, "the usual ADX reading"); side counted only if ADX >= 20 | display text ("1h trend up, strong"; "No trend on 15m or 1h: range, levels matter more than indicators") |
| `tools/live_aid/setup_board.js` line 30 | `adx_di` layer = sign of `adx.v` | cells passed in (15m / 1h) | same 20 | Yes: one of 10 board layers (`LAYERS`) in the board count |
| `tools/live_aid/home.js` lines 418-444 | READINGS `adx15`, `adx1h`, label "Trend (ADX/DI)" | 15m, 1h | same 20 | counted in the six-reading agree count on Home |
| `tools/live_aid/base_rates.py` lines 71-72 | adx15 / adx1h agree if abs >= 20 | 15m, 1h | 20 | analysis only |

Notes: (a) two implementations (Python adx.py, JS indread.js); this inventory did not find a test that compares them (UNKNOWN; `test_indread.py` not read). (b) Live Aid uses "side of DI when ADX >= 20", a level state, not a cross, so it is not CCU's signal. (c) No ADX on 2d, 1d or 1w in Live Aid; 4h is computed but only 15m and 1h reach the board and Home readings.

## 4. Gaps

| Timeframe | Tested? | Detail |
|---|---|---|
| 5m | No | not computed anywhere |
| 15m | Live Aid only | ADX >= 20 side vs idea-flag hit-rate (study 9); no cross or scalp test |
| 1h | Live Aid only | same; 1h crosses in the cascade were planned (PLAN M4) but NOT run: no 1h/4h BTC kline file on that machine (CENSUS top) |
| 4h | Display only | computed in indread.js; no study; cascade NOT run |
| 1d | Partly | 1d crosses only used as leads to 2d (study 7); no standalone 1d outcome table; formula VERIFIED-TV |
| 2d | Yes, descriptive | studies 1-6; our epoch-even-day buckets unverified vs TradingView |
| 5d | No | not computed anywhere |
| 1w | No | not computed anywhere |

| Rule never tested | Why it matters |
|---|---|
| Entry rule from a cross (long on green, short on red) with stop, hold time, fee/slippage, R | the census has no trade; nothing is fee-net |
| ADX level filter on trades (only trade if ADX 20-25+) | bucket n too small (>40: 1 cross); ranking flips between splits |
| ADX rising vs falling (his "very powerful" and the operator's exhaustion idea H1) | slope cells n 0-5 in DEV, 0 in VALIDATION |
| +DI / -DI level or spread (not cross), e.g. -DI spike then fade | only crosses and ADX-at-cross studied |
| ADX < 20 as range regime, mean-reversion in range (Wilder-style regime switch) | USAGE_adx.md calls it Wilder-sourced; no MTS test |
| Swing long: green cross after a red with ADX falling | green crosses studied for whipsaw/depth only, no long P&L |
| Scalp: DI cross on 5m/15m gated by higher-TF ADX | zero data |
| Other symbols (ETH etc.), bear-only windows | census is BTC only |
| Wait-for-confirmation after a cross (his "watch which signal will actually be confirmed") | whipsaw 32-50% within 3 bars says it matters; never turned into a rule |

## 5. Problems found in prior files (for the synthesis)

| File | Problem |
|---|---|
| `research/tv_favorites_2026-11/USAGE_adx.md` s2 source 4 | says "Lowest whipsaw occurs in 20-40 regime" and "ADX falling from >40 signal exhaustion"; CENSUS shows 20-40 falling at 35.7% (DEV) and 75.0% (VALIDATION), above <20 falling in both; >40 has n 1. Unsupported |
| same, s3 | "~28-bar lag" has no source in the file: treat as UNKNOWN |
| same, s2 source 2 | BeikabuOyaji timeframes come from the TradingView favourites list, not from the author: weak |
| `SPEC.md` / PLAN | M5-M8 (volume at levels, CBP indicator rows, Gemini visual read of CCU frames, Monday wave) not shown as done for ADX; M7 would give ADX at his 3 crosses |
| `CENSUS.md` | the 11-05 red cross (nfwd 0) is in the table, and a green cross 2026-11-03 whipsawed within 1 bar: his "crossed back" case sits in the data |

## 6. Cards touching ADX (`system/tasks/*.json`)

| Card | State | Note |
|---|---|---|
| adx-tv-crosscheck-verdict-line-1111, tvfav-usage-adx-1107, gemini-doc-code-scan-usage-adx-formulas-1111 | done | formula + usage note; scan result recorded as CONSISTENT 5, CONTRADICTION 0 |
| live-aid-board-value-area-not-wired-1111 | ready | board layers incl. adx_di; not an ADX study |
| with-trend-session-census-1111 | dropped | not an ADX study |
| PLAN M5-M8 | no card found | UNKNOWN whether carded elsewhere |
| entry-rule / scalp / 5d / 1w ADX tests | no card | the gaps above |
