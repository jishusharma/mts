# Krown Layer Parameter Labels (`file:line` sweep)

Date: 2026-10-30  
Card: `gemini-param-labels-krown`  
Goal: List each numeric parameter default in `MyTradingSys/backtest/layers/krown` code, find its source (analyst extract, FORMULAS.md, architecture spec, or none), and label SOURCED (quote + path) or OURS. Report only; no verdicts.

## Summary

- **Total numeric parameters / structural constants swept**: 47
- **SOURCED count**: 22
- **OURS count**: 25
- **UNLABELED count**: 0

---

## 1. Parameter and Constant Inventory (`layers/krown/`)

| Parameter / Constant | File:Line (Definition) | File:Line (Code Usage) | Default Value | Label | Provenance / Sourced Quote & Path |
|---|---|---|---|---|---|
| `enabled` | `layers/krown/params/krown_params.json:4` | `layers/krown/krown_events.py:75` | `false` | OURS | Flag-gated default OFF (`KROWN_LAYER_SPEC.md:5`). |
| `zone_k` | `layers/krown/params/krown_params.json:5` | `layers/krown/krown_core.py:283`, `krown_events.py:80,81,101,141` | `3` | OURS | Bars each side of a swing; KR-L01 gives no number, grid `{2,3,5}` (`KROWN_LAYER_SPEC.md:42`). |
| `zone_min_turns` | `layers/krown/params/krown_params.json:6` | `layers/krown/krown_core.py:266` | `2` | SOURCED | Rule KR-Z02: "one touch is an event, two is a memory" (`KROWN_LAYER_SPEC.md:43`, citing rule Z02; `KROWN_RULES.csv:Z02`). |
| `zone_lookback` | `layers/krown/params/krown_params.json:7` | `layers/krown/krown_core.py:259` | `250` | OURS | Pivots older than this many bars are not ranked (KR-Z18 "recent" is not defined, `KROWN_LAYER_SPEC.md:43`). |
| `zone_max` | `layers/krown/params/krown_params.json:8` | `layers/krown/krown_core.py:277` | `5` | SOURCED | Rule KR-Z03: "at most 3 to 5 zones" (`KROWN_LAYER_SPEC.md:43`, citing rule Z03; `KROWN_RULES.csv:Z03`). |
| `zone_mature_tests` | `layers/krown/params/krown_params.json:9` | `layers/krown/krown_core.py:270` | `3` | SOURCED | Rule KR-Z13: "beyond three tests the break probability is higher" (`KROWN_LAYER_SPEC.md:43`, citing rule Z13; `KROWN_RULES.csv:Z13`). |
| `swing_tol` | `layers/krown/params/krown_params.json:10` | `layers/krown/krown_events.py:80` | `0.01` | OURS | "About the same" range tolerance (KR-L10 gives no numeric threshold, `KROWN_LAYER_SPEC.md:42`). |
| `vol_sma` | `layers/krown/params/krown_params.json:11` | `layers/krown/krown_core.py:284`, `krown_events.py:79` | `20` | SOURCED | Rule KR-V01: SMA 20 on volume (`KROWN_LAYER_SPEC.md:44`, citing rule V01; `KROWN_RULES.csv:V01`). |
| `vol_mult` | `layers/krown/params/krown_params.json:12` | `layers/krown/krown_core.py:265`, `krown_events.py:144` | `2` | SOURCED | Rule KR-V02: "two or more times the average" (`KROWN_LAYER_SPEC.md:44`, citing rule V02; `KROWN_RULES.csv:V02`). |
| `vol_half` | `layers/krown/params/krown_params.json:13` | `layers/krown/krown_core.py:102` | `0.5` | SOURCED | Rule KR-V10: observation: "volume near 50 % of average before a breakout" (`KROWN_LAYER_SPEC.md:44`, citing rule V10; `KROWN_RULES.csv:V10`). |
| `vol_slots` | `layers/krown/params/krown_params.json:14` | `layers/krown/krown_core.py:93` | `7` | OURS | Same-slot baseline arm: weekday slot for 1d (`KROWN_LAYER_SPEC.md:44`). |
| `vol_slot_prev` | `layers/krown/params/krown_params.json:15` | `layers/krown/krown_core.py:93` | `8` | OURS | Same-slot baseline arm: previous weeks averaged (`KROWN_LAYER_SPEC.md:44`). |
| `tops_vol_sma` | `layers/krown/params/krown_params.json:16` | `layers/krown/krown_events.py:89` | `30` | SOURCED | Rule KR-V02 / TOP-05: 30-day average in the tops framework (`KROWN_LAYER_SPEC.md:44,51`). |
| `bbwp_basis` | `layers/krown/params/krown_params.json:17` | `layers/krown/krown_events.py:82` | `7` | SOURCED | Rule KR-Q01: basis length 7 (`KROWN_LAYER_SPEC.md:45`, citing rule Q01; `KROWN_RULES.csv:Q01`). |
| `bbwp_lookback` | `layers/krown/params/krown_params.json:18` | `layers/krown/krown_events.py:82` | `100` | SOURCED | Rule KR-Q01: lookback 100 (`KROWN_LAYER_SPEC.md:45`, citing rule Q01; `KROWN_RULES.csv:Q01`). |
| `bbwp_mult` | `layers/krown/params/krown_params.json:19` | `layers/krown/krown_events.py:82` | `2.0` | OURS | Band multiplier not stated by trader (KR-Q01); percentile formula defined in `FORMULAS.md:21.5`. |
| `bbwp_high` | `layers/krown/params/krown_params.json:20` | `layers/krown/krown_events.py:145` | `85` | SOURCED | Rule KR-Q02: high volatility >= 85 (`KROWN_LAYER_SPEC.md:45`, citing rule Q02; `KROWN_RULES.csv:Q02`). |
| `bbwp_low` | `layers/krown/params/krown_params.json:21` | `layers/krown/krown_events.py:44` | `30` | OURS | Rule KR-Q02 gives 25-35 range; 30 picked from grid `{25,30,35}` (`KROWN_LAYER_SPEC.md:45`). |
| `bbwp_confirm` | `layers/krown/params/krown_params.json:22` | `layers/krown/krown_events.py:41` | `50` | SOURCED | Rule KR-Q02: break confirmed above the 50th percentile (`KROWN_LAYER_SPEC.md:45`, citing rule Q02; `KROWN_RULES.csv:Q02`). |
| `hammer_wick` | `layers/krown/params/krown_params.json:23` | `layers/krown/krown_core.py:157,164` | `0.6` | OURS | Wick-to-range ratio for a big wick (KR-C03 gives none, `KROWN_LAYER_SPEC.md:46`). |
| `hammer_close_pos` | `layers/krown/params/krown_params.json:24` | `layers/krown/krown_core.py:157,164` | `0.7` | OURS | Close in the top (hammer) or bottom (star) 30 % of the range (KR-C03 "closes strong", `KROWN_LAYER_SPEC.md:46`). |
| `doji_body` | `layers/krown/params/krown_params.json:25` | `layers/krown/krown_core.py:169` | `0.1` | OURS | Body ratio for a doji (not stated in extracts, `KROWN_LAYER_SPEC.md:46`). |
| `confirm_horizon` | `layers/krown/params/krown_params.json:26` | `layers/krown/krown_core.py:178` | `3` | SOURCED | Rule KR-C03: horizon 3-5 bars (lower end picked); KR-C08 close beyond pattern wick (`KROWN_LAYER_SPEC.md:46`). |
| `crows_bars` | `layers/krown/params/krown_params.json:27` | `layers/krown/krown_core.py:172` | `3` | SOURCED | Rule KR-C11: "three down bars from the high" (`KROWN_LAYER_SPEC.md:46`, citing rule C11; `KROWN_RULES.csv:C11`). |
| `ma_fast` | `layers/krown/params/krown_params.json:28` | `layers/krown/krown_events.py:83` | `21` | SOURCED | Rule KR-M01: 21 EMA (`KROWN_LAYER_SPEC.md:47`, citing rule M01; `KROWN_RULES.csv:M01`). |
| `ma_slow` | `layers/krown/params/krown_params.json:29` | `layers/krown/krown_events.py:83` | `55` | SOURCED | Rule KR-M01: 55 EMA (`KROWN_LAYER_SPEC.md:47`, citing rule M01; `KROWN_RULES.csv:M01`). |
| `ma_long` | `layers/krown/params/krown_params.json:30` | `layers/krown/krown_events.py:84` | `200` | SOURCED | Rule KR-M01 / KR-M07: 200 SMA (`KROWN_LAYER_SPEC.md:47`, citing rule M01/M07; `KROWN_RULES.csv:M01`). |
| `ma_leash` | `layers/krown/params/krown_params.json:31` | `layers/krown/krown_events.py:85` | `5` | SOURCED | Rule KR-M06: 5 EMA (`KROWN_LAYER_SPEC.md:47`, citing rule M06; `KROWN_RULES.csv:M06`). |
| `leash_n` | `layers/krown/params/krown_params.json:32` | `layers/krown/krown_events.py:138` | `3` | SOURCED | Rule KR-M06: "three closes without touching means you are late" (`KROWN_LAYER_SPEC.md:47`, citing rule M06; `KROWN_RULES.csv:M06`). |
| `rsi_period` | `layers/krown/params/krown_params.json:33` | `layers/krown/krown_events.py:86` | `14` | OURS | Standard Wilder period; KR-S02 does not state the period (`KROWN_LAYER_SPEC.md:48`). |
| `rsi_bull` | `layers/krown/params/krown_params.json:34` | `layers/krown/krown_core.py:313` | `60` | SOURCED | Rule KR-S03: downtrend RSI stays below 60; above 60 something else emerges (`KROWN_LAYER_SPEC.md:48`, citing rule S03; `KROWN_RULES.csv:S03`). |
| `rsi_bear` | `layers/krown/params/krown_params.json:35` | `layers/krown/krown_core.py:313` | `40` | SOURCED | Rule KR-S03: uptrend RSI stays above 40 (`KROWN_LAYER_SPEC.md:48`, citing rule S03; `KROWN_RULES.csv:S03`). |
| `macd_fast` | `layers/krown/params/krown_params.json:36` | `layers/krown/krown_events.py:87` | `12` | OURS | Standard fast EMA period; not stated by trader (`KROWN_LAYER_SPEC.md:48`). |
| `macd_slow` | `layers/krown/params/krown_params.json:37` | `layers/krown/krown_events.py:87` | `26` | OURS | Standard slow EMA period; not stated by trader (`KROWN_LAYER_SPEC.md:48`). |
| `macd_signal` | `layers/krown/params/krown_params.json:38` | `layers/krown/krown_events.py:87` | `9` | OURS | Standard signal EMA period; not stated by trader (`KROWN_LAYER_SPEC.md:48`). |
| `range_n` | `layers/krown/params/krown_params.json:39` | `layers/krown/krown_core.py:355`, `krown_events.py:129` | `20` | OURS | Range lookback window not stated in KR-R01 (`KROWN_LAYER_SPEC.md:49`). |
| `range_width_max` | `layers/krown/params/krown_params.json:40` | `layers/krown/krown_core.py:361` | `0.25` | OURS | Max `(top-bottom)/mid` for a range; compression thresholds not stated (`KROWN_LAYER_SPEC.md:49`). |
| `range_edge` | `layers/krown/params/krown_params.json:41` | `layers/krown/krown_core.py:365,367` | `0.2` | OURS | Edge band share of the range; KR-R01 says edges only, no width (`KROWN_LAYER_SPEC.md:49`). |
| `coil_recent` | `layers/krown/params/krown_params.json:42` | `layers/krown/krown_events.py:129` | `5` | OURS | Bars in the coil window; not stated by trader (`KROWN_LAYER_SPEC.md:49`). |
| `coil_max` | `layers/krown/params/krown_params.json:43` | `layers/krown/krown_events.py:130` | `0.7` | OURS | Coil score below this threshold indicates compression; repo choice (`KROWN_LAYER_SPEC.md:49`). |
| `tops_window` | `layers/krown/params/krown_params.json:44` | `layers/krown/krown_events.py:147` | `3` | OURS | Proxy for "a few bars" (KR-P01), grid `{2,3,4}` (`KROWN_LAYER_SPEC.md:51`). |
| `tops_need` | `layers/krown/params/krown_params.json:45` | `layers/krown/krown_events.py:147` | `3` | SOURCED | Rule KR-P01: "three of four" signals required (`KROWN_LAYER_SPEC.md:51`, citing rule P01; `KROWN_RULES.csv:P01`). |
| `s1_vol_mult` | `layers/krown/params/krown_params.json:46` | `layers/krown/krown_events.py:104` | `2` | SOURCED | Rule KR-V02: volume >= 2x at the zone test (S1) (`KROWN_LAYER_SPEC.md:44,51`). |
| `s2_vol_mult` | `layers/krown/params/krown_params.json:47` | `layers/krown/krown_events.py:113` | `1.0` | OURS | S2 volume above average; "discernible" threshold grid `{1.0, 1.25, 1.5}` (`KROWN_LAYER_SPEC.md:44`). |
| `s8_recent` | `layers/krown/params/krown_params.json:48` | `layers/krown/krown_events.py:43` | `5` | OURS | Bars to look back for `BBWP <= low` (S8 setup rule proxy). |
| `s8_break_n` | `layers/krown/params/krown_params.json:49` | `layers/krown/krown_events.py:38` | `10` | OURS | Bars of range the S8 candle must break; repo choice. |
| `s7_vol_lookback` | `layers/krown/params/krown_params.json:50` | `layers/krown/krown_events.py:133` | `100` | OURS | "Biggest volume bar" window for S7 (KR-V07 gives none, `KROWN_LAYER_SPEC.md:44`). |

---

## 2. Details and Observations

1. **Explicit Parameter Architecture**:
   - The Krown layer v0 maintains all parameter definitions in `MyTradingSys/backtest/layers/krown/params/krown_params.json`, linking each parameter to its corresponding source ledger identifier (e.g., `KR-Z02`, `KR-Q01`, `KR-M01`) or marking it as `OURS`.
   - The detector functions in `krown_core.py` and `krown_events.py` strictly ingest these parameters via `kc.load_params()` without ad-hoc magic numbers.
2. **Trader Sourced vs Repo Engineering**:
   - Sourced concepts (22 parameters): zone turn counts (`KR-Z02`), max zones (`KR-Z03`), zone maturity (`KR-Z13`), volume expansion threshold (`KR-V02`), BBWP basis/lookback/thresholds (`KR-Q01`, `KR-Q02`), MA periods (`KR-M01`, `KR-M06`), RSI bounds (`KR-S03`), and tops confluence requirements (`KR-P01`).
   - Engineered parameters (25 parameters): swing lookback windows (`zone_k=3`), tolerance bands (`swing_tol=0.01`), candle shape ratios (`hammer_wick=0.6`, `doji_body=0.1`), MACD default periods, range compression lookbacks, and setup event scan windows.
