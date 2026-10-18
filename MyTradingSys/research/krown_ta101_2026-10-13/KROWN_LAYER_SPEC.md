# KROWN LAYER SPEC v0.2 (2026-10-14) - from 15 extracts (14 TA videos); amended if the 4 missing videos arrive

Status: spec only. Nothing here is an MTS rule until the operator approves it (playbook Part I: a change backed only by T3) and our own
fee-net out-of-sample test passes. Source of every rule: KROWN_RULES.csv (120 rows, ids `KR-xxx`); his words: extracts/.
Layer rules (operator 2026-10-13): no fixed core; Krown is a layer that may be combined, used as a filter or switched off; results decide.

## 0. Answer in nine lines
1. Krown teaches a **swing and context method for the daily and weekly chart**: a trend state from dominant highs and lows, zones from wick to
   close (a close, not a wick, is the verdict), volume at 2x its average, four candle patterns with a strict engulfing definition, 21/55 EMA + 200,
   ranges and coils, a volatility regime (BBWP), RSI zones as confirmation, and a four-signal framework for selling long-term tops.
2. His home is **BTC/crypto on the daily and weekly, daily close 00:00 UTC** (KR-T04, KR-T08): our data, our market, no transfer problem
   (unlike Tom and Fabio, who are futures order-flow traders). Tops are weekly/monthly (KR-P01).
3. Holding period is days to weeks (tops: months), so fees are small next to a daily stop; the Tom/Fabio fee wall (stop under round-trip cost)
   should not apply. The cost is **sample size**: a daily layer gives tens, not thousands, of events per year.
4. Of 120 consolidated rules: 99 READY, 6 BLOCKED, 15 REJECT (framing, claims, fees, options). 67 of the 105 non-reject rows come from fewer than 3 videos (PROVISIONAL).
5. **Stops and sizes are still thin.** One structural stop exists (far side of the compression zone, a close beyond it, KR-Q05) and one structural
   exit rule (a close beyond a zone, KR-X01); targets are the range height (KR-R07) and a volatility peak (KR-Q06); size: "size down as volatility
   rises" and a 20-85 % scale-out at tops (KR-P02). No stop distance, no risk per trade. Everything else is an OURS arm.
6. The first fully specified setup is the **compression breakout** (KR-Q05): BBWP below 25-35, first range-breaking candle with BBWP above 50, stop on the far
   side, exit as BBWP peaks. It is one video (PROVISIONAL) but it is the only one with entry, stop and exit all sourced.
7. Prior evidence in this repo is not friendly: S/R flip + retest (CryptoCred) FAIL, candle patterns no edge, candle-close DEV exploratory negative,
   volume gives intensity not direction, RSI divergence no edge on any timeframe, 62 published rules 0 survive. Krown's differences to test: daily/weekly
   scope, strict definitions, a volatility regime gate, and stacking zone + volume + candle + trend state. Expect small effects; the best role may be a
   **filter or regime context** for other layers.
8. 14 TA videos extracted of 19 reachable (4 captions missing, 18 hidden). The 20-video saturation gate is not met and cannot be on this playlist alone:
   decision q-krown-saturation. Until it is answered only descriptive detectors, a recall check and a DEV study are in scope.
9. "Into play" now means: spec + ledger done, registered as layer family `krown`, cards ready for detectors (k1) and data (k0); recall (k2) and the
   pre-registered DEV study (k3) follow. Nothing is wired to the engine or live.

## 1. Home-fit (PRE_REG item 1)
Market BTC/crypto (TFR-12 "daily is the gold standard for most cryptos"); timeframes 1w, 1d, 6h, 4h (KR-T08); close 00:00 UTC (KR-T04); history >= 200
periods, about 500 ideal (KR-T01). Tops: weekly for Bitcoin, monthly for traditional markets (TOP-01). BBWP settings are for "Bitcoin on higher term
time frames" (KCM-11). Holding period is NOT stated; "scalp" = a short hold he does not size (KR-Z08, KR-L04, KR-R01).
Data needed: OHLCV only. No aggressor side, OI or funding. Volume venue is a data decision (conflict C6).

## 2. Components (pure functions of closed bars, no lookahead)
S = SOURCED (his words), O = OURS (declared before any run; grid values count in the trial ledger).

| module | what it computes | SOURCED | OURS |
|---|---|---|---|
| `tf` | closed 1w/1d/6h/4h bars, UTC close | 00:00 UTC (T04) | week start (Monday 00:00 UTC) |
| `swings` | swing highs/lows; dominant highs/lows; trend state (up, down, range); confirmation lag | dominant-low and dominant-lower-high definitions, reversal = trade and close beyond the dominant level, one-bar peaks ignored, confirm on the next reversal close (L10, L01, Z05) | k bars each side {2,3,5}; size of a "one-bar peak"; swings on closes vs on highs/lows; "about the same" range tolerance |
| `zones` | zone = [close, wick extreme] of a pivot bar; turn count; touch count; heavy-volume flag; at most 5 ranked; against-trend flag | wick-to-close (Z01), >= 2 turns (Z02), max 5 (Z03), > 3 tests mature (Z13), 2x volume (Z04), levels work with the trend (Z17) | reaction size to count a turn, grid in ATR units; ranking weights; "recent" for touches (Z18) |
| `volume` | SMA, ratio to SMA, same-slot ratio, 2x flag, 50 % flag | SMA 20 (V01) or 30-day (TOP-05), 2x (V02), 0.5 observation (V10) | same-slot baseline as a second arm; "discernible" breakout threshold grid {1.0,1.25,1.5}x; 20 vs 30 vs 60 (C10) |
| `vol_regime` | BBWP, regime (compression / normal / expansion), BBWP average | basis length 7, lookback 100, close; high >= 85, low <= 25-35, confirm > 50 (Q01, Q02) | band multiplier 2, exact percentile formula (define in FORMULAS.md), grid {80,85,90} x {25,30,35} (C13) |
| `candles` | hammer, shooting star, strict engulfing, doji, three black crows, confirmation close | engulfing definition (C06), confirm = close beyond pattern wick (C08), horizon 3-5 bars (C03), three down bars from the high (C11) | wick-to-range ratio for "big wick", body ratio for doji, "exact low" lookback |
| `mas` | EMA 5/21/55/377, SMA 50/200, slopes, crosses, pair state, first-touch-after-away | periods and pairs (M01, M09), 50/200 (M07), weekly 55 EMA bias (M10) | "long time away" N days, slope thresholds, touch tolerance |
| `rsi` | RSI, zone state (up >40, down <60, range 40-60), divergences, MACD cross | overbought 70, zones 40/60 and 40-80/20-60 (S02, S03), divergence definitions (S05) | RSI period (14), oversold level, divergence lookback and spacing, MACD (12,26,9) |
| `range` | range as two zones, edge/middle position, coil score, compression, breakout close, range height | edges only (R01), close breaks (Z07), height projection (R07) | compression/tightness score thresholds, flat-MA slope threshold |
| `topdown` | trend state per timeframe; agree/disagree; mode (trend/range) | roles 1w tide, 1d decide, 4h/6h timing (T03); state from KR-L10 | none beyond L10's |
| `tops` | four-signal top: reversal candle, extreme volume, extreme volatility, momentum (RSI divergence or MACD cross) | 3 of 4 within "a few bars", weekly/monthly, volume 2x the 30-day average, BBWP > 85 (P01, V02, Q02) | "a few bars" {2,3,4}; which 3 of 4 |
| `events` | emits `{i, side, setup, tags}` per bar, compatible with `layers/runner.py forward_return_stats` | - | - |

## 3. Setups (Krown's language; entry triggers are closed-bar, almost every stop distance is OURS)
| id | setup | trigger (rules) | stop | exit / target |
|---|---|---|---|---|
| S1 | ZONE-TEST | price tests a ranked zone with trend context (Z17), proof candle at the zone (C03-C10), volume >= 2x; mirror for ceilings | A (OURS) beyond the zone's far wick boundary; B his close-based exit (close back beyond the zone, X01) with an OURS hard stop 1.5 x ATR14 | opposite zone; 2R (OURS) |
| S2 | BREAK-CLOSE | close beyond a zone's outer boundary with volume above average (Z07, V05, R06, M13); arm 1 enter at the close, arm 2 at the first retest that holds (Z10 vs Z11, C2) | close back inside the zone | **range height from the trigger (R07, SOURCED)**; 2R |
| S3 | RANGE-EDGE | range = two zones; trade only at an edge with a proof candle, never the middle; fake-out = act on the close back inside (R01, R02) | close beyond the edge | opposite edge |
| S4 | COIL-BREAK | compression (volume falling, tighter, flat averages, RSI 40-60: V09, R03, T07, S03) then S2 in either direction | as S2 | range height |
| S5 | MA-CONTEXT | 21/55 EMA cross with price vs 200 (M02); pair rule (M09); first touch of the 200 after a long absence (M03); pullback into the 21-55 band in an uptrend (M05); weekly 55 EMA bias (M10); all as filters per M12 | below the 55 EMA / close beyond the line | none given: trail on the 55 EMA (OURS) |
| S6 | LEASH (provisional) | candle low above the 5 EMA for >= 3 closes then a pullback to it (M06) | close below the 5 EMA | prior extreme |
| S7 | CAPITULATION (provisional) | hammer on the biggest volume bar after a long downtrend (V07) | below the hammer low | none given |
| **S8** | **VOL-COMPRESSION BREAKOUT** | BBWP below 25-35 (ideally falling from a high), bias from the previous trend (L12), first candle that breaks the range with BBWP rising above 50 and momentum agreeing (Q05, Q02); his preferred variant enters inside the range near the edge of the bias side | **SOURCED structure: far side of the compression zone, a close beyond it; after the break the stop may move to the breakout area (Q05)**; distance beyond it OURS | **SOURCED: take profit as volatility peaks (BBWP in the 90s, reversal candle on high volatility, volatility losing its average: Q06)**; range height (R07) as a second arm |
| S9 | TOP-4 SELL FRAMEWORK | 3 of 4: reversal candle, volume >= 2x the 30-day average, BBWP > 85, RSI bearish divergence or MACD cross, on weekly/monthly (P01); long-term holder scale-out 20-85 % (P02) | n/a (a sell signal, not an entry) | wait for a reset (P06, BLOCKED) |
Context filters (apply to any setup, arms on/off): trend state L10 on each timeframe and the agree rule (T03, L11), mode trend vs range (T06, T07),
range-middle exclusion (R01), volatility regime gates (Q07: no entry after expansion; Q08), RSI zone state (S03), volume confirms/condemns (V04), higher-timeframe veto (T02).

## 4. What is NOT in the spec (and must not be invented)
A stop DISTANCE for any setup, risk per trade, hold time, round-number tolerance (Z12 BLOCKED), steepness degrees (L07 BLOCKED), Coinbase/index volume
(V11 BLOCKED), live use of "no resting stop" (X01 BLOCKED, conflict C3), the reset rule after a top (P06 BLOCKED), anything about the 4 missing and 18
hidden videos. His own statistics (right side of the trend 90-95 %, 80-95 % for the 21/55 cross, 70 % compression, 5 EMA leash counts, the 200-week
back-test) are claims: hypotheses H-L1, H-Q1, H-M3, H-M2, never inputs.

## 5. Isolation and safety
- Code under `MyTradingSys/backtest/layers/krown/` with `params/krown_params.json` carrying a `source` per parameter (SOURCED + ledger id, or OURS).
- Flag-gated, default OFF; alert-only first; no import of Tom or Fabio constants; `test_layer_boundaries.py` must keep passing.
- No live wiring, no engine setup file (extraction.md SAFEGUARD 3 not met), no mainnet.
- Every run: pre-registration first, every variant in the trial ledger, VALIDATION once, HOLDOUT never before a pre-registered rule survives.

## 6. Fit to existing layers and studies (so nothing is rebuilt twice)
| existing | relation |
|---|---|
| `ma_daily` (NO-SOURCE chatbot numbers) | Krown supplies SOURCED numbers: 21/55 EMA, 50/200 SMA, 5 EMA, 377 EMA, 200W (KR-M01..M10). Re-label before re-test. |
| `candle_patterns` (CANDLE-P0/P1/D19, no edge) | check whether the strict engulfing and "exact low" location were used (conflict C4). |
| Codex lab CANDLE-CLOSE-DEV-20261014 (exploratory negative) | borrowed Krown's close-through/reclaim/retest definitions; S2 is the full composite it did not test. |
| `volume` (no directional edge, HOLDOUT sealed) | Krown uses volume as confirmation, not direction: consistent. Same-slot baseline arm is mandatory (C5, C10). |
| `cryptocred` (S/R flip + fib + failed MSB FAIL) | Z09/Z10 overlap strongly: expect the same. The difference to test is the stack and the trend/volatility gates. |
| `rsi` / Malkan (`rsi_levels` 40/60 tolerance study, `rsi_divergence` no edge) | KR-S03 is the same 40/60 regime: reuse that study's tolerance results; KR-S05 divergence overlaps a layer with no edge (C14): descriptive only. |
| `session_levels`, LC (levels confluence) cards | zones are structural levels, not UTC-day levels; LC cards run 1m levels. Different object. |
| options module (`options/`) | KR-Q11 (premium buying only at low implied volatility) belongs there, not here. |

## 7. Build plan (cards)
k0 `krown-data-daily-majors`: BTC spot 1d/1w from 2017-08 (+ ETH/BNB/SOL, Coinbase volume if q-krown-volume-venue allows). k1 `krown-layer-v0-detectors`
(Sonnet): modules above + tests with hand-computed expected numbers (add Krown definitions incl. BBWP to FORMULAS.md), fail-before proof, params
file. k2 `krown-recall-check`: his dated examples (PRE_REG item 3) verified against klines, then recall and fire rate. k3 `krown-dev-event-study`: H-ids under
PRE_REG_KROWN.md, DEV only. k4 VALIDATION once. k5 `krown-ta101-extract-remaining-10` (now 4 videos, blocked on captions). k6
`krown-other-sources-event-study-videos` (his daily event-study videos via the V2 method).

## 8. Open operator decisions (OPERATOR_DECISIONS.md)
q-krown-captions (4 videos), q-krown-saturation (waiver for descriptive work), q-krown-stop (protective stop always), q-krown-volume-venue (Binance only or also Coinbase).
