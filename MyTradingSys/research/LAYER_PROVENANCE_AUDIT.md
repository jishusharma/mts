# LAYER_PROVENANCE_AUDIT - non-core layer parameters (BUILD_PIPELINE 8.1, LY1)

Session: MTS-2026-10-04-1230Z-APP-BLD-ly1-layer-provenance. Mode: static (code and source files read, nothing run).
Scope: rsi, cryptocred, positioning, session, turn_of_candle, tick, consensus under MyTradingSys/backtest/layers/.
Verdicts use the definitions in research/fast_track_2026-09-27/PROVENANCE_AUDIT_TOM.md:5, with "Tom" read as "the
layer's own source":
- SOURCED = a quote from the layer's source supports the value and the role.
- CONCEPT-ONLY = the source names the idea; the code measures it by proxy or the number is ours.
- NO-SOURCE = no source idea behind it, or it plays a role (gate, stop, target, time exit) the source never gives it.
- DATA-PLUMBING = no trading meaning (fees, file paths, study gates). Listed, not counted.

Source per layer (the "trader" whose words count):
| Layer | Source | Where the words are |
|---|---|---|
| rsi (malkan) | Vishal B Malkan (MalkanView), blog/chartink text | research/malkan_rsi_2026-09-28/WEB_RESEARCH.md (WR) |
| rsi (generic) | none named; params say "source": "operator" | backtest/layers/rsi/params/default.json:3 |
| cryptocred | CryptoCred, videos BHwoN7VPrBE, inqHN8q57X4 | extracts/processed/cryptocred/extract_BHwoN7VPrBE.md (BH), extract_inqHN8q57X4.md (INQ) |
| positioning | Memon 2026 (T2), He/Manela/Ross/von Wachter (T2); CVD leg = internal T055a H2 | research/_archive/loose_2026-10/whale_positioning_evidence_2026-09-12.md:30; backtest/layers/FORMULAS.md:356-370 |
| session | Shen, Urquhart, Wang 2022 (T1) | research/fast_track_2026-09-27/T055b_PROVEN_SETUPS.md:30; FORMULAS.md:372-383 |
| turn_of_candle | Shanaev, Vasenin, Stepanov, Heliyon (T1) | T055b_PROVEN_SETUPS.md:38,51; FORMULAS.md:385-398 |
| tick | operator spec (T040), verbatim operator text | MyTradingSys/items/T040_tick_delta_layer.md (T040) |
| consensus | operator architecture doc | research/_archive/loose_2026-10/ARCHITECTURE_TWO_CORES_2026-10-01.md:29-43 |

Quote rule used: a SOURCED row cites a line that carries the source's own words (in quotes in that file). A summary
bullet written by our researcher is not a quote; rows resting only on one are CONCEPT-ONLY.

## Totals

| Layer | SOURCED | CONCEPT-ONLY | NO-SOURCE | Rows | Plumbing (not counted) |
|---|---|---|---|---|---|
| rsi | 4 | 10 | 12 | 26 | 6 |
| cryptocred | 6 | 11 | 8 | 25 | 2 |
| positioning | 0 | 4 | 3 | 7 | 3 |
| session | 1 | 2 | 3 | 6 | 1 |
| turn_of_candle | 2 | 1 | 2 | 5 | 0 |
| tick | 4 | 6 | 2 | 12 | 3 |
| consensus | 0 | 0 | 0 | 0 | 4 |
| **All** | **17** | **34** | **30** | **81** | **19** |

Headline: no non-core layer has a sourced exit. Every stop, target and time exit in these layers (RSI 1%/2%/100 bars,
CryptoCred 0.1% buffers, fixed 1.5R/2R targets, 200/1440-bar expiries) is NO-SOURCE, and two of them reuse a number the
trader gives in a different role (CryptoCred's 1.5:1 and 2:1 are MINIMUM R:R filters, BH:82, used as fixed targets).

## 1. rsi

rsi: 4 SOURCED, 10 CONCEPT-ONLY, 12 NO-SOURCE.

| ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
|---|---|---|---|---|---|---|
| R01 | rsi/rsi_core.py:7; params/default.json:7; params/malkan_40_60_default.json:7 | RSI period | 14 | WR:35 "Period: 14 (RSI 14)" is a researcher bullet, no Malkan quote | CONCEPT-ONLY | Also the live alert RSI (observation.py.new:24). |
| R02 | rsi/rsi_ma.py:8; params/default.json:9-12 | RSI smoothing line | SMA 14 | - (no Malkan text mentions an RSI MA) | NO-SOURCE | default.json:3 "source": "operator"; operator is not a trader source. |
| R03 | params/default.json:14 | Generic RSI levels | 70 / 50 / 30 | - WR:39-40: Malkan uses 40-60 "Instead of traditional overbought (70) / oversold (30)"; WR:93: 50 "not explicitly defined" | NO-SOURCE | Live rsi_events alerts feed the testnet trader. |
| R04 | params/default.json:15 | Generic event tolerance | 0 | - | NO-SOURCE | Invalid: rsi_events.py:20-21 raises on tolerance <= 0 (open question Q3). |
| R05 | params/default.json:16 | ma_support_enabled | false | - | NO-SOURCE | Switch for R07, itself unsourced. |
| R06 | rsi/rsi_events.py:19-103 | Band events support / rejection / failure / cross | rule | WR:60-61 "when it bounces from 40, trend is strong upward" (bullet) | CONCEPT-ONLY | Taxonomy is ours; Malkan names only bounce at 40 / fall from 60. |
| R07 | rsi/rsi_ma_events.py:15; run_rsi_backtest.py:269-270 | RSI-vs-MA events: period 9/14, ma_length 9/14, tolerance 0.5/1/2, mode touch/cross | grid | - | NO-SOURCE | Grid-searched: tuning, forbidden by the provenance rule. |
| R08 | rsi/malkan_40_60.py:24,64; malkan_40_60_default.json:10 | Bull support level lo | 40 | WR:45 "When the market is bearish, it won't be able to cross 60, and whenever in a bullish trend, it won't be able to cross 40." | SOURCED | |
| R09 | rsi/malkan_40_60.py:24,107; malkan_40_60_default.json:11 | Bear resistance level hi | 60 | WR:45 (same quote) | SOURCED | |
| R10 | rsi/malkan_40_60.py:53-58 | Regime: BULL if min >= 40 AND max >= 60; BEAR if max <= 60 AND min <= 40; else RANGE | rule | WR:45, WR:85 support "won't cross 40/60"; the second clause (max >= 60, min <= 40) has no quote | CONCEPT-ONLY | |
| R11 | rsi/malkan_40_60.py:24; malkan_40_60_default.json:12 | Regime lookback | 20 bars | - (no window in WR) | CONCEPT-ONLY | |
| R12 | rsi/malkan_40_60.py:64,107; malkan_40_60_default.json:13 | Band tolerance around 40/60 | 2.0 RSI pts | WR:116 "at or near Daily RSI 40" (bullet); quote WR:120 "Bullish candlestick forms at 40 RSI level" | CONCEPT-ONLY | |
| R13 | rsi/malkan_40_60.py:88,122 | Bull trigger = "support" event (enters band from above, closes back above 40+tol); bear = "rejection" at 60 | rule | WR:77 "Daily RSI supporting near 40"; WR:113 "Daily RSI <= 40" | CONCEPT-ONLY | A dip below 38 is a "failure" in code and is dropped; WR:113 accepts RSI below 40. |
| R14 | rsi/malkan_40_60.py:64,94; malkan_40_60_default.json:14 | Green entry candle required (long) | true | WR:77 "...Daily RSI supporting near 40 with entry on Green Candle." | SOURCED | |
| R15 | rsi/malkan_40_60.py:107,128; malkan_40_60_default.json:15 | Red entry candle required (short) | true | WR:144 "Bearish candlestick forms at 60 RSI level on daily chart = short signal." | SOURCED | |
| R16 | rsi/malkan_40_60.py:91,125 | Gate signal on the SAME timeframe's regime | rule | WR:85 regime quote; WR:77 gates on Monthly + Weekly, not the entry TF | CONCEPT-ONLY | Self-documented MLK-GAP1 (malkan_40_60.py:13-16). |
| R17 | rsi/malkan_mtf.py:69 | MTF bull gate: weekly AND monthly regime == BULL | rule | WR:77 "Monthly RSI >= 60 AND Weekly RSI >= 60" | CONCEPT-ONLY | Malkan reads the HTF RSI value; code uses the 20-bar regime (R10). |
| R18 | rsi/malkan_mtf.py:95 | MTF bear gate: weekly AND monthly regime == BEAR | rule | WR:80-81, WR:138-139 bullets "Monthly RSI < 40 / <= 40"; no quote | CONCEPT-ONLY | |
| R19 | run_rsi_backtest.py:233,268 | HTF regime lookback | grid 3 / 6 / 12 | - | NO-SOURCE | Tuned. |
| R20 | run_rsi_backtest.py:265-266 | malkan_40_60 grid: period 10/14/21, tolerance 1/2/3, lookback 10/20/40 | grid | - | NO-SOURCE | Sweeping a sourced value (period) is tuning. |
| R21 | run_rsi_backtest.py:56,109 | Stop | 1% from entry | - WR:123 "Place below the low of the bullish entry candle" (bullet) | NO-SOURCE | |
| R22 | run_rsi_backtest.py:57,109 | Target | 2% from entry | - WR:128 "Target is 60 RSI level on daily chart" | NO-SOURCE | Malkan's target is an RSI level, not a price %. |
| R23 | run_rsi_backtest.py:58,110 | Time exit | 100 bars | - WR:132-133: hold while Monthly and Weekly RSI stay > 60 | NO-SOURCE | |
| R24 | run_rsi_backtest.py:107 | Entry at the signal bar close | rule | WR:117 "Entry point is determined by placing an order above the high of the signal candle" | CONCEPT-ONLY | Entry named; trigger differs (close vs break of high). |
| R25 | rsi/tolerance_sweep.py:45 | Tolerance sweep 0.5..5.0, horizons 1/3/5/10/20 | grid | - | NO-SOURCE | Tuning machinery. |
| R26 | rsi/tolerance_sweep.py:22-42 | event -> side map (support long, rejection short, cross by direction) | rule | - (docstring :27 "this driver's own heuristic") | NO-SOURCE | |

Plumbing (rsi): run_rsi_backtest.py:55 HORIZONS (1,5,20); :59 MIN_OOS_N 30; :60 MAX_PBO 0.5; :76 is_frac 0.70;
tolerance_sweep.py:83 min_events 5; observation.py.new:50,59-60 TFS, _CHUNK, DEFAULT_MAX_SCAN_BYTES.

## 2. cryptocred

cryptocred: 6 SOURCED, 11 CONCEPT-ONLY, 8 NO-SOURCE.

| ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
|---|---|---|---|---|---|---|
| C01 | cryptocred/cc_structure.py:11 | Swing fractal left | 2 bars | BH:12 "a swing low is a low with a higher low on both sides... there's no single formula" | CONCEPT-ONLY | |
| C02 | cryptocred/cc_structure.py:11 | Swing fractal right | 2 bars | BH:12 (same) | CONCEPT-ONLY | Also the confirmation delay (cc_structure.py:49,57). |
| C03 | cryptocred/cc_structure.py:11,17-21 | Bodies, not wicks, for swings | use_body=True | BH:106 "my preferred variant is using candle bodies for market structure and then closes" | SOURCED | |
| C04 | cryptocred/cc_structure.py:100,122 | Break requires a close through the level | close | BH:106 "i at least like to see a close above or below on the same time frame as the market structure anchor" | SOURCED | |
| C05 | cryptocred/cc_structure.py:81,95,117 | Break must violate a sequence (lower high broken by higher high) | require_prior_sequence=True | BH:23 "for a bullish market structure break it is when a sequence of lower highs is violated by a higher high" | SOURCED | Code checks one prior swing only (H_last < H_prev). |
| C06 | cryptocred/cc_structure.py:81,134-135 | Mid-range MSB filter default | off | BH:66 "i wouldn't put too much stock into those market structure breaks in a range outside of parts of the range that you'd actually trade" | CONCEPT-ONLY | Default OFF keeps the MSBs the trader calls noise. |
| C07 | cryptocred/cc_structure.py:63,81 | Range lookback | 50 bars | BH:66 (same) | CONCEPT-ONLY | |
| C08 | cryptocred/cc_structure.py:63,81 | Range-extreme band | 25% of span | BH:66 (same) | CONCEPT-ONLY | |
| C09 | cryptocred/cc_retest.py:17,37,46 | Retest touch tolerance | 0.15% | INQ:45 "the immediate retest is when you trade at or near structure when it breaks" | CONCEPT-ONLY | |
| C10 | cryptocred/cc_retest.py:17,38,47 | Retest void if close beyond level | 0.5% | INQ:51 "you essentially eradicate the risk of falling for a failed breakout" | CONCEPT-ONLY | Docstring cites C07-E04 for this (cc_retest.py:6); C07-E04 is timeframe alignment. MISCITED. |
| C11 | cryptocred/cc_retest.py:17,31 | Retest expiry | 200 bars | - INQ:139 "a lot can happen between a break and the subsequent retest" (no limit) | NO-SOURCE | |
| C12 | cryptocred/cc_retest.py:57,63 | Immediate vs rounded split | 5 bars | INQ:45 "the main distinguishing factor is time and space" (CT-038) | CONCEPT-ONLY | Imported by cc_setups.py:19, never called. |
| C13 | cryptocred/cc_setups.py:43 | Setup 1 entry at the broken level | level | BH:58 "the long trade is taken on a pullback to the broken high... the short trade is taken on a pullback to the broken low" | SOURCED | |
| C14 | cryptocred/cc_setups.py:34,45 | Setup 1 stop = level x (1 -/+ 0.1%) | 0.1% | - (no stop rule in BH or INQ) | NO-SOURCE | |
| C15 | cryptocred/cc_setups.py:34,64,46,133 | Setups 1-2 fixed target | 1.5R | - BH:82 "greater minimum risk reward requirements... let's say two reward for one risk instead of 1.5" | NO-SOURCE | 1.5 is his trend MINIMUM R:R (a filter); code uses it as the take-profit. |
| C16 | cryptocred/cc_setups.py:64,91,118 | Fib zone shallow edge | 0.618 | BH:114 "personally i look for support resistance structures anywhere between the 618 and 786 retracement" | SOURCED | BH:117 "there's no fixed answer really". |
| C17 | cryptocred/cc_setups.py:64,91,118 | Fib zone deep edge | 0.786 | BH:114 (same) | SOURCED | |
| C18 | cryptocred/cc_setups.py:96-102,123-129 | Setup 2 entry = first touch, filled at the 0.618 edge | rule | BH:114 looks for "structures" inside the zone | CONCEPT-ONLY | He waits for structure in the zone; code fills on touch. |
| C19 | cryptocred/cc_setups.py:104,131 | Setup 2 stop beyond 0.786 x 0.1% | rule | - BH:114 "above the most recent low" is entry location, no stop | NO-SOURCE | |
| C20 | cryptocred/cc_setups.py:65,94,121 | Setup 2 zone expiry | 200 bars | - | NO-SOURCE | Hard-coded. |
| C21 | cryptocred/cc_setups.py:151,168 | Setup 3 failure window | 20 bars | BH:128 "failed continuation is suggestive of reversal" | CONCEPT-ONLY | |
| C22 | cryptocred/cc_setups.py:173-182,196-205 | Setup 3 trigger: no new extreme in window AND window-end close back through the broken level | rule | BH:128 "if we get a higher high bullish into a lower low invalidated then you have bulls offside" | CONCEPT-ONLY | His trigger is the invalidating swing, not a close after N bars. |
| C23 | cryptocred/cc_setups.py:183,206 | Setup 3 stop = broken level x 0.1% | 0.1% | - | NO-SOURCE | |
| C24 | cryptocred/cc_setups.py:151,207 | Setup 3 fixed target | 2.0R | - BH:82 (counter-trend MINIMUM 2:1) | NO-SOURCE | Same role swap as C15. |
| C25 | cryptocred/cc_bt_adapter.py:17,47 | Time exit | 1440 bars | - BH:82 "shorter holding periods" (counter-trend only, no number) | NO-SOURCE | |

Plumbing (cryptocred): cc_bt_adapter.py:17 taker_fee 0.0005 / maker_fee 0.0; stop_first=True.

## 3. positioning

positioning: 0 SOURCED, 4 CONCEPT-ONLY, 3 NO-SOURCE.

| ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
|---|---|---|---|---|---|---|
| P01 | positioning/funding_cvd_fade.py:70 | Funding percentile window | 90 records | whale_positioning_evidence:30 "Extreme funding" T2 (Memon 2026) - a table row, no quote | CONCEPT-ONLY | FORMULAS.md:369 "all UNDEFINED in source". |
| P02 | positioning/funding_cvd_fade.py:70-71 | High-funding extreme | pct >= 0.95 | same | CONCEPT-ONLY | |
| P03 | positioning/funding_cvd_fade.py:71 | Low-funding extreme | pct <= 0.05 | same | CONCEPT-ONLY | |
| P04 | positioning/funding_cvd_fade.py:88-91,114-117 | Side: high funding -> short, low -> long | rule | FORMULAS.md:356 "funding-extreme reversion"; no source sentence on direction in repo | CONCEPT-ONLY | |
| P05 | positioning/funding_cvd_fade.py:70 | Divergence lookback n | 20 bars | - T055a_POSITIONING_FLOW.md:113 "20-50 bar lookback" (our own hypothesis) | NO-SOURCE | |
| P06 | positioning/funding_cvd_fade.py:71,79-91 | Divergence AND funding both required (use_divergence=True) | gate | - FORMULAS.md:361 "Merge decision: supervisor 2026-09-29" | NO-SOURCE | A gate no source gives. |
| P07 | positioning/funding_cvd_fade.py:62-65 | Divergence: new n-bar close extreme with CVD inside its n-bar range | rule | - (T055a H2, internal) | NO-SOURCE | |

Plumbing (positioning): funding_cvd_fade.py:48 CVD = running sum of 2*tbv - v; trade_costs.py:47 fee_rt 0.0010
(Binance taker; live venue is Deribit, backtest/fees.py); trade_costs.py:47 slip_rt 0.0002 (FORMULAS.md:347 "internal arithmetic").

## 4. session

session: 1 SOURCED, 2 CONCEPT-ONLY, 3 NO-SOURCE.

| ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
|---|---|---|---|---|---|---|
| S01 | session/session_momentum.py:12,40 | First window | 30 min | T055b:30 "intraday momentum, first-half-hour predicts last-half-hour" | CONCEPT-ONLY | Paper is in VOLUME time (FABIO_BTC_RESEARCH_2026-09-30.md:70, BTC_SESSION_EXTERNAL_2026-10-04.md:90); code uses clock minutes. |
| S02 | session/session_momentum.py:12,80 | Entry time | 30 min after start | T055b:30 predicts the LAST half-hour | CONCEPT-ONLY | Default enters for the rest of the day, not the last half-hour (FORMULAS.md:381). |
| S03 | session/session_momentum.py:11,29 | Session start | 00:00 UTC | - FORMULAS.md:382 "UNDEFINED in source" | NO-SOURCE | Fixed UTC, no DST (B102). |
| S04 | session/session_momentum.py:23,29 | Session length | 24 h (UTC day) | - | NO-SOURCE | 24/7 adaptation is ours (session_momentum.py:5-6). |
| S05 | session/session_momentum.py:12,71-74 | Minimum first-window move | 0.0 | - | NO-SOURCE | Inert at default. |
| S06 | session/session_momentum.py:71-74 | Side = sign of first-window return (continuation) | rule | T055b:30 "first-half-hour predicts last-half-hour" | SOURCED | BTC_SESSION_EXTERNAL:88-90 reports reversal at hour scale (counter-evidence). |

Plumbing (session): session_momentum.py:11 bar_min 1.

## 5. turn_of_candle

turn_of_candle: 2 SOURCED, 1 CONCEPT-ONLY, 2 NO-SOURCE.

| ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
|---|---|---|---|---|---|---|
| T01 | turn_of_candle/turn_of_candle.py:3 | Candle length | 15 min | T055b:51 "Turn-of-candle effect (returns concentrated at 15-min candle opens)" | SOURCED | |
| T02 | turn_of_candle/turn_of_candle.py:36 | Turn minute | minute 0 of the quarter | T055b:51 (same) | SOURCED | |
| T03 | turn_of_candle/turn_of_candle.py:59,68; alerts/live_layers.py:177 | Lead | 1 min (enter at minute 14 close) | - | CONCEPT-ONLY | |
| T04 | turn_of_candle/turn_of_candle.py:59 | Side (backtest) | long | - FORMULAS.md:393 "direction of the effect is NOT stated" | NO-SOURCE | |
| T05 | alerts/live_layers.py:170-182 | Side (live testnet) = sign of the quarter's minute-0 taker imbalance | rule | - (operator 2026-09-30 data-collection ruling, live_layers.py:171-175) | NO-SOURCE | Trades on testnet as "sampling"; T055_BT_c3.md: no gross edge. |

## 6. tick

tick: 4 SOURCED, 6 CONCEPT-ONLY, 2 NO-SOURCE. Source is the operator's own spec (T040), the only trader-equivalent
for this layer.

| ID | Code (file:line) | Parameter | Value | Source quote / nearest content | Verdict | Note |
|---|---|---|---|---|---|---|
| K01 | tick/tick_extremes.py:214; tick/build_tiers.py:66,72 | Timeframes | 1, 2, 3, 5, 10, 15 min | T040:40-41 "Compute for each time frame 1m, 2m, 3m, 5m, 10m and 15 minutes" | SOURCED | |
| K02 | tick/tick_extremes.py:162,214; tick/build_tiers.py:29,68-70 | Indicators: net_delta, cvd_change, volume, price_change_pct, oi_delta | list | T040:35-36 "flag unusual increase or decrease(the change) in price or cvd or volume or oi or net delta etc." | SOURCED | cvd_change == net_delta per bucket (tick_extremes.py:56): one reading, two flags (Q9). |
| K03 | tick/build_tiers.py:33-38,67 | History | klines 2022-01..; OI 2025-09.. | T040:39-40 "duration/range of ALL TIME using our Binance exchange API" | CONCEPT-ONLY | Neither series is all-time. |
| K04 | tick/tick_extremes.py:108-147; tick/tick_oi_extremes.py:90-112 | Tiering by gaps between consecutive ranks | rule | T040:46-48 "check the diff from 1st -> check third highest and check the diff from 2nd -> In this way detect a range to group these" | SOURCED | |
| K05 | tick/tick_extremes.py:108,143; tick/tick_oi_extremes.py:90,103; tiers_meta.json:30 | New tier when gap > factor x median gap | 1.5 | T040:47-48 (same; no number) | CONCEPT-ONLY | |
| K06 | tick/tick_extremes.py:149,214; tick/tick_oi_extremes.py:115,156; tick/build_tiers.py:66-67 | Ranks kept per side | top 20 | T040:43-47 highest, second, third... (no cut-off) | CONCEPT-ONLY | Only the 20 all-time extremes can ever flag: 0.11 flags/day (tiers_meta.json:17). |
| K07 | tick/tick_extremes.py:80-96; tick/tick_oi_extremes.py:65-77 | Session windows asian 00-08, european 08-13, overlap 13-16:30, american 16:30-21, off 21-24 UTC | rule | T040:50 "Also note the time period (when it happened - session info etc.)" | CONCEPT-ONLY | Context tag only. |
| K08 | tick/tick_extremes.py:98-106; tick/tick_oi_extremes.py:80-87 | Funding window | +-30 min of 00/08/16 UTC | - (the operator text has no funding window; added in our design, T040:70) | NO-SOURCE | Context tag only. |
| K09 | tick/tick_extremes.py:58 | Price % change over the same bucket | rule | T040:51 "Calculate the % change in price during the corresponding time period." | SOURCED | |
| K10 | tick/tick_flagger.py:142,100 | Cooldown | 30 min | T040:18 "Needs its own cooldown, same as the existing candle-alert cooldown" | CONCEPT-ONLY | No candle-alert cooldown exists to copy (alerts dedup on (t, event), alerts/live_layers.py:6). |
| K11 | tick/tick_flagger.py:95-97 | Escalation to a more extreme tier bypasses cooldown | rule | - | NO-SOURCE | |
| K12 | tick/tick_flagger.py:14-46,62-69 | Boundary = least extreme value of a tier; reading >= boundary flags | rule | T040:48 "group these as per categories of severity/intensity/strength" | CONCEPT-ONLY | |

Plumbing (tick): tick_oi_extremes.py:16-17 OI tf must be a multiple of 5 (5m metrics); build_tiers.py:67 OI tfs 5/10/15;
tick_extremes.py:101 funding resets 0/480/960 (exchange schedule).

## 7. consensus

consensus: 0 SOURCED, 0 CONCEPT-ONLY, 0 NO-SOURCE. No trading parameter: the writer never gates, votes or weights
(writer.py.new:4-6; ARCHITECTURE_TWO_CORES_2026-10-01.md:43 "Consensus is an observation. It does not gate, veto, or
delay any core trade.").
Plumbing: writer.py.new:44 TOM_KEYS, :45 FABIO_KEYS, :46 RSI_TFS (all from ARCHITECTURE:37-39), :42 DEFAULT_DIR.

## 8. REJECT list

Playbook Part I (methodology/playbook.md:28,36): a citation that cannot be opened and matched is REJECT.
1. Malkan quotes (WR:45, :77, :117, :120, :128, :144) are copied from blog.elearnmarkets.com and chartink.com; no
   Malkan transcript or saved page is in the repo. Until a page capture or transcript is matched, R08/R09/R14/R15 rest
   on a secondary copy. Not downgraded here (the text is quoted and URL-cited) but REJECT if the URLs fail to match.
2. Memon 2026 (positioning): the repo holds a tier label only (whale_positioning_evidence:30); no title, URL, quote or
   threshold. P01-P04 cannot rise above CONCEPT-ONLY, and the citation is REJECT until opened and matched.
3. cc_retest.py:6 cites C07-E04 for the 0.5% invalidation; C07-E04 (INQ RULE 3) is timeframe alignment. Miscited.
4. Tuning grids: run_rsi_backtest.py:265-271 and tolerance_sweep.py:45 search over parameters (including the period
   that has a source). The provenance rule says unsourced values are removed or replaced, never tuned: these grids
   should not choose live values.
5. Role swaps (NO-SOURCE although the number is the trader's): C15 1.5R and C24 2.0R targets (BH:82 minimums).

Remove-or-replace candidates (NO-SOURCE that decide a trade): R21-R23, C14, C15, C19, C23, C24, C25, P06, T04, T05.

## 9. Open questions

- Q1 (rsi): fetch a Malkan transcript or page capture for period 14 (R01), the regime window (R11) and the band (R12).
- Q2 (rsi): replace the 1%/2%/100-bar bracket (R21-R23) with Malkan's own exit (candle-low stop WR:123, RSI-60 target
  WR:128, HTF-RSI hold WR:132-133)? Operator call.
- Q3 (rsi): params/default.json:15 tolerance 0 is rejected by rsi_events.py:20-21. What does the live runner pass?
- Q4 (rsi): malkan_mtf.state_asof doc (malkan_mtf.py:26-31) takes bar-OPEN times; run_rsi_backtest.py:220,234 passes
  close times (htf_close_times). A caller that follows the docstring leaks the unclosed HTF bar. Confirm and fix doc.
- Q5 (cryptocred): no stop rule in BH or INQ. Is there a CryptoCred source (other videos: XeQV2ECtZVQ, Yp0k8HD5xro,
  _ndAoizXy64) that gives stop placement or a target method?
- Q6 (cryptocred): classify_retest_timing is never called; INQ:51 says rounded retests are clearer. Should setup 1
  use it?
- Q7 (positioning): open Memon 2026 and record title, URL and the extreme definition, or drop P01-P04.
- Q8 (session): volume-time vs clock-time (S01). Keep the clock proxy or build volume time?
- Q9 (tick): cvd_change equals net_delta for a single bucket, so each reading flags twice. Was CVD meant as a
  multi-bucket running change?
- Q10 (tick): K10 copies a candle-alert cooldown that does not exist. Operator to state the cooldown.
- Q11 (turn_of_candle): T05 trades on testnet with a NO-SOURCE side under a sampling ruling; confirm it stays
  sampling-only and is excluded from any edge claim.
