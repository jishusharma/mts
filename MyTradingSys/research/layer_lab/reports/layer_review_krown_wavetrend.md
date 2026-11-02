# Layer review fact sheet: families krown and wavetrend

Card `layer-review-krown-wavetrend` (setup truth, repo only). Built 2026-11-02 at trunk `be2ce0ee9`. Start: `MyTradingSys/research/gemini_burn_2026-10-25/layer_facts/krown.md` and `wavetrend.md`; every file:line below was re-resolved against this tree (the Gemini line numbers drift by up to 15) and the Krown backtest section was rebuilt because the Gemini sheet predates the detectors, the recall check, the fable run 6 and the sim-desk study. No verdict wording on any layer (operator NO 2026-10-25, `MyTradingSys/research/mts_doctor/MAINNET_PATH_2026-10-25.md:34`). Numbers are copied with their source line, never recomputed. Parameter labels: SOURCED = a trader quote or published source is cited; OURS = our choice, never the trader's.

Layers (from `MyTradingSys/system/layer_index.json`): both families list no layers, so each family id is its own section: `krown` (`MyTradingSys/system/layer_index.json:632`) and `wavetrend` (the next family entry in the same file). Quotes of the video are in the extract format (`> "quote"` then `**Source GPS: id | third**`) so `python scripts/dev/verify_extract_quotes.py` can check them against `raw_transcripts_canonical/`.

## krown

Wired in the simulator: yes, as an exploratory desk try. `MyTradingSys/research/sim_desk/PLUGIN.md:4` names `studies/krown.py` as a working example; the study offers only the price-bar setups S5 (21/55 EMA cross), S8 (squeeze break) and S4 (coil break) because the desk bars carry no volume (`MyTradingSys/research/sim_desk/studies/krown.py:33`).

### Idea and source

- Plain statement: "Daily and weekly BTC swing method: trend state from dominant highs and lows, levels from wick to close, volume at 2x its average, a volatility (BBWP) regime, RSI 40/60 zones as confirmation, four candle patterns, 21/55 EMA + 200 SMA; a close, not a wick, is the verdict." (`MyTradingSys/system/layer_index.json`, krown `plain` field, family entry at line 632).
- Analyst: Eric Krown, "TA 101" (Krown Trading); scope is the daily and weekly chart on BTC/crypto (`MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:8-12`; analyst name `MyTradingSys/options/research/KROWN_FREE_VS_PAID.md:1`).
- Corpus: spec v0.2 and a 120-rule ledger from TA 101 extracts (`MyTradingSys/system/LAYERS.md:224`, `MyTradingSys/system/layer_index.json:635`). The index text still says "Detectors not built, not backtested"; that sentence is out of date against the detector and backtest files listed under Backtests below (`MyTradingSys/research/krown_audit_2026-10-22/REPORT.md:54`: "v0 detectors ... done; S10-S16 have no detector").
- Verbatim quotes with a video position:

> "the daily is a gold standard for most cryptos for slower markets like equities the weekly earns the top slot followed by the monthly and the quarterly"
**Source GPS: _t_XIBrcjRk | MIDDLE | t=00:12:17**

> "Only a close beyond the zone breaks a level. No close outside. We don't call it broken. Period."
**Source GPS: qEfES84jwwo | END | t=00:30:46**

> "The middle, that's your no man's land. No memory, no zone, no edge."
**Source GPS: 6aA-P4Gvhrc | BEGIN | t=00:06:08**

> "when you align these things they become infinitely more powerful"
**Source GPS: 8MvxK_nxO-0 | END | t=00:29:10**

- Where the quotes sit: gold standard `MyTradingSys/research/krown_ta101_2026-10-13/extracts/extract__t_XIBrcjRk.md:117-119`; close beyond the zone `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:1021`; no man's land `KROWN_SETUP_CATALOG.md:1005`; align `KROWN_SETUP_CATALOG.md:1032`.

### Parameters

All rows are from the spec module table `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_LAYER_SPEC.md:41-51` (module table; rule ids KR-xx are in the ledger `KROWN_RULES.csv`).

- tf: bar close 00:00 UTC, targets 1w/1d/6h/4h: SOURCED (KR-T04, KR-T08; spec line 41). Week starts Monday 00:00 UTC: OURS (spec line 41).
- swings: dominant low / dominant lower high, reversal = trade and close beyond the level, one-bar peaks ignored: SOURCED (KR-L10, KR-L01, KR-Z05; spec line 42). Lookback k in {2,3,5} bars each side, size of a "one-bar peak", closes vs highs/lows, "about the same" tolerance: OURS (spec line 42).
- zones: wick-to-close zone (KR-Z01), at least 2 turns (KR-Z02), max 5 active (KR-Z03), more than 3 tests = mature (KR-Z13), heavy-volume anchor 2x (KR-Z04), levels work with the trend (KR-Z17): SOURCED (spec line 43). Reaction size in ATR units, ranking weights, "recent" for touches: OURS (spec line 43).
- volume: SMA 20 baseline (KR-V01) or 30-day (KR-TOP-05), expansion 2x (KR-V02), low-volume observation 0.5 (KR-V10): SOURCED (spec line 44). Same-slot baseline as second arm, breakout grid {1.0, 1.25, 1.5}x, window 20 vs 30 vs 60: OURS (spec line 44).
- vol_regime (BBWP): basis 7, lookback 100, source close (KR-Q01), high >= 85, low <= 25-35, confirm > 50 (KR-Q02): SOURCED (spec line 45). Band multiplier 2, percentile formula, grid {80,85,90} x {25,30,35}: OURS (spec line 45).
- candles: strict engulfing (KR-C06), confirm = close beyond pattern wick (KR-C08), horizon 3-5 bars (KR-C03), three black crows (KR-C11): SOURCED (spec line 46). Wick-to-range ratio for "big wick", body ratio for doji, "exact low" lookback: OURS (spec line 46).
- mas: EMA 5/21/55/377 and SMA 50/200 (KR-M01, KR-M09, KR-M07), weekly 55 EMA bias (KR-M10): SOURCED (spec line 47). "Long time away" N days, slope thresholds, touch tolerance: OURS (spec line 47).
- rsi: overbought 70 (KR-S02), zones 40/60 and 40-80/20-60 (KR-S03), divergence definitions (KR-S05): SOURCED (spec line 48). RSI period 14, oversold level, divergence lookback, MACD (12,26,9): OURS (spec line 48).
- range, topdown, tops: range edges only, close breaks, measured target = range height (KR-R01, KR-Z07, KR-R07), hierarchy 1w tide / 1d decide / 4h-6h timing (KR-T03), "3 of 4" signals on weekly/monthly (KR-P01, KR-V02, KR-Q02): SOURCED (spec lines 49-51). Tightness thresholds, flat-MA slope, window "a few bars" in {2,3,4} and which 3 of 4: OURS (spec lines 49-51).
- Stops and exits: only one structural stop is sourced (compression breakout S8: far side of the zone, a close beyond it, KR-Q05) and one exit (take profit as volatility peaks, KR-Q06); stop distance, risk per trade and hold time are NOT_IN_DATA (`KROWN_LAYER_SPEC.md:70`, "A stop DISTANCE for any setup, risk per trade, hold time").
- Desk-study choices (all OURS, `MyTradingSys/research/sim_desk/studies/krown.py:9`): market entry at the next bar open; stop = far side of the last 10 bars including the signal bar (`krown.py:25`, MAX_HOLD 100, STOP_BARS 10); target 2 x risk; timeframe 4h or daily. SOURCED in the same header (`krown.py:6`): S5 = 21 EMA crosses 55 EMA with price on the 200 SMA side (KR-M02); S8 = BBWP 7/100, low <= 30, first bar above the 50th percentile (KR-Q01, KR-Q02).

### Backtests

No fee-net out-of-sample run exists. VALIDATION and HOLDOUT were never read for this family in any file below.

| Run | Report and line | Fee-net | In-sample or OOS | n | Number as recorded |
|---|---|---|---|---|---|
| Candle-close screen (borrowed Krown close-through, reclaim and retest definitions) | `MyTradingSys/research/layer_lab/candle_close_2026-10-14/REPORT.md:3` | fixed 14 bp round trip screen (`REPORT.md:3`) | DEV only, validation "not opened" (`REPORT.md:7`) | 105,541 correlated event rows, 126 arms (`REPORT.md:3`) | "0 of 126 pooled arms pass the frozen exploratory screen" (`REPORT.md:3`); Krown identity "NOT_IN_DATA" (`REPORT.md:71`) |
| Recall check of the v0 detectors on his dated examples | `MyTradingSys/research/krown_ta101_2026-10-13/RECALL.md:36`; ledger `MyTradingSys/research/TRIAL_LEDGER.csv:19` | not a P&L run | DEV bars before 2024-07-01 | 12 examples listed, 3 verified against klines, 0 strict hits | "RECALL FAIL" against a bar of 6 (`RECALL.md:36`); ledger: "FAIL (bar unreachable: 3 verified)" (`TRIAL_LEDGER.csv:19`) |
| Fire rate of S1-S9 on Binance 1d | `RECALL.md:59` and `RECALL.md:64`; `TRIAL_LEDGER.csv:20` | not a P&L run | DEV | 2,510 daily bars | "FIRE RATE PASS", max S2 0.367 per 10 bars against a ceiling of 1.0 (`TRIAL_LEDGER.csv:20`) |
| Sim desk, S5 4h, target 2R | `MyTradingSys/research/layer_lab/TRIALS.md:280` | yes, maker 0.02 % taker 0.05 % slip 0.02 % | DEV 2022-04-01..2024-06-30 | 35 filled | mean net R +0.278, CI [-0.161, +0.750], "NOT ENOUGH DATA" (`TRIALS.md:280`) |
| Fable run 6, S8 squeeze break 4h, BTC+ETH+SOL pooled (C0) | `MyTradingSys/research/fable_run6_powered_prereg/RESULT.md:3`; `MyTradingSys/research/VERDICTS.csv:65`; `TRIAL_LEDGER.csv:94`; `TRIALS.md:300` | yes (taker 0.05 % + slip 0.02 %, maker 0.02 %) | DEV 2020-01-01..2024-06-30, run once, label NO-RECALL-CLEARANCE (`RESULT.md:5`) | 420 trades on 332 entry days, need >= 439 (`RESULT.md:3`) | mean net R +0.1312, SE 0.0760, t +1.73 against a need of 3.364; verdict INCONCLUSIVE (`RESULT.md:3`). Exits: 238 stop, 138 target, 44 time (`RESULT.md:7`) |
| Same run, strata (no verdict word) | `VERDICTS.csv:66-73`; `TRIALS.md:301-308` | yes | DEV | BTC 142, ETH 153, SOL 125, long 232, short 188, DEV_EXT 175, DEV 245, BTC x DEV 78 | long only +0.2967 (t +2.86, `TRIALS.md:304`); short only -0.0731 (t -0.65, `TRIALS.md:305`); BTC only +0.0664 (`TRIALS.md:301`). "Strata ... can neither rescue nor kill C0" (`RESULT.md`, text after the strata table) |
| Silver cross, daily EMA21 up-cross EMA55, 30-day hold (his free setup) | `MyTradingSys/research/krown_free_2026-10-31/DEV_CHECK.md:5`; `RESULT.csv` in the same folder | yes, 0.10 % round trip from `backtest/fees.py` (`DEV_CHECK.md:1`) | DEV 2022-01..2024-06 (912 days) | 6 events, 5 blocks | 3 of 6 green (50 %) against his quoted 83 %; mean net +7.87 %, CI -9.8 % to +21.7 %; "INCONCLUSIVE by pre-declaration (n = 6)"; all-days 30-day baseline 53.9 % green, mean net +3.10 % (`DEV_CHECK.md:5`, `DEV_CHECK.md:34`) |
| Opr-bb-mtf-center screen with Krown range tests M1-M4 | `MyTradingSys/research/VERDICTS.csv:41-42` | see file | DEV | 194 and 282 | AU +0.0196 INCONCLUSIVE; AD +0.0322 FAIL (`VERDICTS.csv:41-42`) |
| Phase split P1 (Krown x cowen_side, sma200_side, wsma10_phase) | `TRIALS.md:382-384` | none run | DEV | 0 | "BLOCKED: no frozen per-event fee-net R list on disk for Krown; no outcome read; cells not run" (`TRIALS.md:382`) |

The pre-registered Krown DEV event study (card `krown-dev-event-study`) is "not started" (`MyTradingSys/research/krown_audit_2026-10-22/REPORT.md:57`).

### Bugs and assumptions

- Formal lab rulings: `python scripts/dev/lab_query.py rulings krown` returns an empty list; `MyTradingSys/research/BUGS.md` has no Krown row except the unrelated CBP adapter row B139 (`BUGS.md:250`).
- Assumption, no stop: Krown states "I do not like stop losses" (`MyTradingSys/research/krown_ta101_2026-10-13/reflexivity_log.md:11`); conflicts with the house rule for protective stops (spec conflict C3, `KROWN_LAYER_SPEC.md:70`).
- Assumption, stop distance and size: NOT_IN_DATA (`KROWN_LAYER_SPEC.md:70`).
- His own statistics (90-95 % right side of trend, 80-95 % for the 21/55 cross, and similar) are unverified claims held as T3 hypotheses (`MyTradingSys/research/krown_ta101_2026-10-13/PROTOCOL.md:26`).
- Volume baseline conflict: plain 20-period SMA 2x spike (his) versus a same-slot baseline (ours); both arms are specified (`PROTOCOL.md:28`, conflict C5).
- Volume venue: he reads Coinbase, TradingView index or CME volume; repo data is Binance; the desk bars carry no volume (`MyTradingSys/research/krown_ta101_2026-10-13/PRE_REG_KROWN.md:32-33`; `krown.py:33`).
- Ground truth: the videos are lecture illustrations, not a trade ledger, so no entry/stop/target triplets exist (`PRE_REG_KROWN.md`, ground-truth section); the recall check could verify 3 of 12 examples against klines (`RECALL.md:36`).
- Saturation gate: only part of the reachable TA 101 set is extracted; the 20-video gate is unmet (`PROTOCOL.md:17`).
- Run 6 carries a pre-declared stop list tied to its FAIL branch (`RESULT.md`, line after the arm table); its result was INCONCLUSIVE, not FAIL (`RESULT.md:3`).

### Confluence

- Cross-trader overlap table: `MyTradingSys/research/krown_ta101_2026-10-13/KROWN_SETUP_CATALOG.md:975-1000`. STRONG rows: KR-S1 zone test with TOM-15 (`KROWN_SETUP_CATALOG.md:975-981` region), KR-S2 break-close with TOM-6, KR-S3 range edge with TOM-2 and fake-out return with TOM-12, KR-S3 poke-and-return with FAB-4, KR-S14 regular divergence with MAL-14/16/17 and hidden divergence with MAL-7/8/9. PARTIAL rows: KR-S4/S8 compression breakout with TOM-15/6 and FAB-1, KR-S5 MA pullback with TOM-4, KR-S9 top selling with TOM-16 and MAL-16, KR-S13 effort versus result with TOM-2 and FAB-2/5, KR-S16 with TOM-1.
- No overlap in the repo: KR-S6 (5 EMA leash), S7, S10, S11, S12, S15 (`KROWN_SETUP_CATALOG.md:998-1000` region).
- RSI 40/60 regime (KR-S03) matches the `rsi_levels` 40/60 study; KR-Z09/Z10 overlap with CryptoCred S/R flip and retest; Krown numbers supply the sourced moving-average periods for `ma_daily`; liquidation-cascade rules KR-LQC01..04 are context and sizing filters for `positioning` (`KROWN_LAYER_SPEC.md:84-96`).
- Wiring: detectors `backtest/layers/krown/krown_events.py` and `krown_context.py` are "no live imports; observation only" (`MyTradingSys/system/wiring_registry.json:895`, `:899`). The silver cross check is a one-off by-hand run (`wiring_registry.json:993`).
- Tagging use: `MyTradingSys/research/krown_audit_2026-10-22/REPORT.md:37` proposes a `krown_context_live` writer that tags alerts without gating anything.

## wavetrend

Wired in the simulator: yes. `MyTradingSys/research/sim_desk/PLUGIN.md:4` names `studies/wavetrend.py` as a working example.

### Idea and source

- Plain statement: "LazyBear WaveTrend as a causal BTC context layer; observable oscillator states are implemented, while event definitions, controls and fee-net strategy value remain under research." (`MyTradingSys/system/layer_index.json`, wavetrend `plain` field).
- Author header quoted: "@author LazyBear ... If you use this code in its original/modified form, do drop me a note." (`MyTradingSys/research/wavetrend_2026-10-17/PARITY_CONTRACT.md:12-13`; also `MyTradingSys/backtest/layers/wavetrend/wavetrend.py:5`). This is a source-code header, not a video, so it carries no Source GPS line.
- Published source: TradingView "WaveTrend with Crosses [LazyBear]" by lonestar108, id jFQn4jYZ, script id 2295, created 2016-02-20; snapshot at `MyTradingSys/research/wavetrend_2026-10-17/source_snapshot/WT_Crosses_lonestar108_jFQn4jYZ.pine.txt` (`PARITY_CONTRACT.md:9`). The oscillator mathematics are identical to the marketcalls gist copy (`PARITY_CONTRACT.md:10-12`).
- Original signal idea: LazyBear's 2014 publication calls WaveTrend a port of an earlier TS/MT indicator; sell when the oscillator crosses down through its signal line above an overbought band, buy on a cross up below an oversold band (`MyTradingSys/research/wavetrend_2026-10-17/EXTERNAL_SETUPS.md:13`).

### Parameters

- SOURCED (Pine code lines 9-23 of the snapshot, cited in `PARITY_CONTRACT.md:15-18`, `MyTradingSys/backtest/layers/FORMULAS.md:516`): price ap = (h+l+c)/3; esa = EMA(ap,10); d = EMA(|ap-esa|,10); ci = (ap-esa)/(0.015*d); wt1 = EMA(ci,21); wt2 = SMA(wt1,4); bands +/-53 and +/-60 around centre 0 (`PARITY_CONTRACT.md:18`; `MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md`).
- SOURCED (external setup, `EXTERNAL_SETUPS.md:23-24`): long on up-cross below the oversold band, short on down-cross above the overbought band; the long-only variant with a stop at the preceding three-bar low and target 1.5x risk comes from a named third-party setup (`EXTERNAL_SETUPS.md:24`), not from LazyBear.
- OURS (`PARITY_CONTRACT.md:23-30`): warm-up 200 bars (line 23); flat window `d <= 1e-9*|ap|` gives ci = NaN (line 24); cross convention "first bar strictly on the opposite side of the last strict side" (line 26); closed bars only, `available_at = bar_open_time + timeframe`, earliest executable price the next bar open (line 29); higher-timeframe value is the last HTF bar whose close time <= t (line 30).
- OURS (`MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:20-23`): power floor 153 distinct UTC event-days (Holm over 12 cells, alpha 0.05/12, power 80 %), later re-gated to 200 days (`MyTradingSys/research/wavetrend_2026-10-17/DISPOSITION_2026-10-19.md:13`); R_out = 3; c = 5; k = 2 and G = 20; context bins (volatility terciles, EMA(200) trend state with 10-bar slope, HTF zone, 20-day same-slot volume terciles, UTC 8-hour windows); primary horizon H = 12 bars.
- OURS (desk study, `MyTradingSys/research/sim_desk/studies/wavetrend.py:8-10`, `:21-23`): entry at the next bar open, both lines beyond the band, max hold 100 bars, timeframes 1h, 4h, 15m.

### Backtests

| Run | Report and line | Fee-net | In-sample or OOS | n | Number as recorded |
|---|---|---|---|---|---|
| DEV behaviour atlas, nine primary cells W01-W09 | `MyTradingSys/research/wavetrend_2026-10-17/RESULT.md:15-23`; `MyTradingSys/research/VERDICTS.csv:56-64`; `MyTradingSys/research/TRIAL_LEDGER.csv:10-18` | no, gross only, no fees, no funding, no strategy stops (`PRE_REG.md:84`; `RESULT.md:5`) | DEV only, BTCUSDT 2022-01-01..2024-06-30, 912 days; VALIDATION and HOLDOUT reads 0 (`RESULT.md:5`; `DISPOSITION_2026-10-19.md:3`) | W01 3893 events; W02 4196; W03 3509; W04 1154; W05 788; W06 538; W07 298; W08 271; W09 947 (`RESULT.md:15-23`) | mean returns: W01 -0.0143 %, W02 -0.0078 %, W03 -0.0043 %, W04 -0.0209 %, W05 -0.0578 %, W06 -0.0422 %, W07 -0.0295 %, W08 +0.0897 %, W09 +0.0241 % (`RESULT.md:29-63`). Final labels: W01-W03 and W09 FAIL; W04-W08 INCONCLUSIVE (`VERDICTS.csv:56-64`; `layer_index.json` wavetrend status field) |
| Control arms A3_L53, A1_L60, A3_L60 | `RESULT.md:102-108` | no | DEV | 291 to 6,373 | descriptive (`RESULT.md:101-110` region) |
| Descriptive 4h and C2 runs | `RESULT.md:112-123` region | no | DEV | 4h unconditioned 22 to 244; C2 on 5m 1,207, on 15m 402 | descriptive |
| Sim desk, 1h band 53 both sides, 1.5R | `MyTradingSys/research/layer_lab/TRIALS.md:273` | yes, maker 0.02 % taker 0.05 % | DEV 2022-04-01..2024-06-30 | 369 filled | mean net R -0.158, CI [-0.288, -0.023], worst losing streak 8, recorded "FAILED"; default configuration only (`TRIALS.md:273`) |
| Sim desk, same config, short window | `TRIALS.md:285` | yes, slip 0.02 % added | DEV 2023-03-01..2023-05-31 | 50 | mean net R -0.074, CI [-0.401, +0.282], "NOT ENOUGH DATA" (`TRIALS.md:285`); filtered variants n 7 and n 23 (`TRIALS.md:293-294`) |
| Indicator mutation audit | `TRIALS.md:429-430` | not a P&L run | 400-bar DEV fixture, January 2022 | 20 independent pairs | original 13/13; full suite kills 5/5; golden kills 3/5 (`TRIALS.md:429`) |

### Bugs and assumptions

- Formal lab rulings: `python scripts/dev/lab_query.py rulings wavetrend` returns an empty list; no BUGS.md row names wavetrend except the integration ticket T061 (`MyTradingSys/research/BUGS.md:170`).
- C1 divergence detector mismatch (HIGH): C1 confirmed two price pivots and read wt1 at those bars without checking that either was a confirmed WT pivot (`MyTradingSys/research/wavetrend_2026-10-17/AUDIT_2026-10-18.md:7-11`; repro `repro_c1_spec_mismatch.py`, `AUDIT_2026-10-18.md:9`). Cells W07 and W08 do not measure the intended event (`DISPOSITION_2026-10-19.md:9`; `MyTradingSys/system/LAYERS.md`, WaveTrend section).
- Control-arm uncertainty basis (MEDIUM): primary arm uses day-clustered SE while random-clock and context-only arms use the SD of 200 draw means; the difference test assumes independence (`AUDIT_2026-10-18.md:13-17`).
- Input manifest pinning (MEDIUM): the exposure ledger stored the directory path and script SHA but no file digests (`AUDIT_2026-10-18.md:19-23`); the card `wavetrend-data-inference` followed up and `input_manifest.json` now exists in the study folder.
- Parity scope: formula parity against `make_golden.py` and `wt_parity_ref.py`, not TradingView runtime parity, because no TradingView export was available (`PARITY_CONTRACT.md:32`; `AUDIT_2026-10-18.md:27`).
- Desk-study caveat: the n = 369 run is the default configuration only (1h, band 53, both sides, 1.5R), not the other timeframes (`TRIALS.md:273`).

### Confluence

- Observation-only module with no live callers: header "OBSERVATION ONLY: no side, no routing, no Tom/Fabio gate" (`MyTradingSys/backtest/layers/wavetrend/wavetrend.py:1`); wiring row "no caller yet" (`MyTradingSys/system/wiring_registry.json:872-875`).
- Context factors in the atlas design: EMA(200) trend state, next-higher-timeframe WT zone, same-slot volume participation, realised-volatility terciles (`MyTradingSys/research/wavetrend_2026-10-17/PRE_REG.md:25-28`).
- Third-party confluence set surveyed, not tested: Squeeze Momentum, Supertrend / multi-timeframe agreement, VWMA, Market Cipher composites, support/resistance pivots (`EXTERNAL_SETUPS.md:27-31` region).
- Row in `MyTradingSys/system/layer_map.json`: NOT_IN_DATA (`DISPOSITION_2026-10-19.md:21`).
- Inside the simulator, the Krown S5 desk run was filtered by "if wavetrend fired within 20x60m": n 1, mean net R +1.072, "NOT ENOUGH DATA" (`MyTradingSys/research/layer_lab/TRIALS.md:299`).
- Live read note (observation only, no trade advice): `MyTradingSys/research/wavetrend_2026-10-17/LIVE_NOTE_2026-10-27.md:1-12`.
