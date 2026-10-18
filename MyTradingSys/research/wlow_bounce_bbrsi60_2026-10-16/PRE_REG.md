# PRE-REGISTRATION: weekly-low break, bounce, hold under RSI 60 near the upper Bollinger band (BTCUSDT 1h, frozen 2026-10-16)

Session W16 (JIS-NB, claim `wlow-bounce-bbrsi60`). The commit that adds this file precedes the commit that adds any outcome (`git log` is the proof; same convention
as `research/gross_effect_screen_2026-10-15/PRE_REG.md`). Status: EXPLORATORY, UNVALIDATED. Nothing here adopts a rule, places an order or touches the live path.
Labels: SOURCED = operator words or a repo file:line. OURS = judgement, with the reason. Every "DECISION (OURS)" took the most conservative reading.

## 0. Operator request (SOURCED, operator 2026-10-16 ~01:55 IST, screenshot `1249ec1ebab3`, BTCUSDT 1h Binance, 2026-10-15 20:23Z)
1. "Check what happens when BTC breaks weekly lows and then bounces and wait like in this fashion near the upper edge of the BB and sits just under the RSI 60 line - like a flat RSI line as seen here. Move it to right channels for live tracking!"
2. Addition: "keep adding one by one other parameters like how the open interest, CVD and the net delta is changing the overall result of what happens next."
Chart (screenshot, read before this file, no outcome): BTC broke the prior weekly low (~80.2k, 10-15 ~12:00Z), V-bounced in 2-3 1h candles, then 5-6 candles sat at/under the upper BB(20,2) with RSI(14) flat at 56-58; Stoch RSI pinned ~96 (not used: no definition given). OI ~93.66K coins (rising into the bounce then flat; live public read at 10-16 confirms 93.67K); CVD -26.2K (small up then flat); net delta -11.5K (flat, slightly negative in the hold).

## 1. Data, split, costs
- Tape: Binance USD-M BTCUSDT 1m klines `F:/MTS/data/tom_raw/klines/BTCUSDT-1m-*.csv` (fields incl. taker_buy_volume), aggregated to 1h (UTC, an hour needs all 60 minutes). SOURCED: same tape as the gross-effect screen.
- DEV = bar open 2022-01-01 .. 2024-06-30 (the project standard split, `PRE_REG_VOLUME_2026-10-09.md:23`, `gross_effect_screen/PRE_REG.md` section 6). VALIDATION 2024-07-01..2025-06-30 and HOLDOUT 2025-07-01..2026-09-30 are NOT read by this study; loader refuses any bar with open >= 2024-07-01 (`study.py` assert).
- Cost: C = 0.14 % round trip (5+5 bps fee, 2+2 bps slippage), SOURCED `gross_effect_screen/PRE_REG.md` section 1. Net long = mean R - C. Net short = -mean R - C. No funding (horizons <= 24 h; effect < 1 bp per straddle, OURS: ignored and said so).
- Entry = open of the 1h bar after the trigger bar (the trigger bar closes at that open, so this is the nearest tradable price, no extra delay; DECISION OURS, 1h horizons make a further 1 minute immaterial).
- Open interest: Binance metrics archive starts 2025-09-01 (`F:/MTS/Dumps/backtest/raw/metrics`, `F:/MTS/data/orderflow_views_2026-10-14/oi_5m.csv` from 2026): **OI is NOT_IN_DATA for DEV**. Layer 1 is therefore not run; it is a live-tracking-only field.
- CVD and net delta: from kline taker volume, delta = 2*taker_buy_volume - volume (FORMULAS.md section 14, as `gross_effect_screen` section 2).

## 2. Setup definition (closed 1h candles only; code `MyTradingSys/backtest/layers/wlow_bounce/detector.py` is the single definition used by the study and the live status CLI)
| Item | Value | Label |
|---|---|---|
| Weekly low W | low of the previous completed ISO week (Mon 00:00 UTC .. Sun 23:00 UTC bars, all 168 present). A Monday-open week IS the ISO week, so it is the same series; the real variant is the rolling prior 168 bars (V2) | OURS |
| Break | a 1h bar whose low < W (first such bar opens an episode; no new episode within 24 bars of the previous episode start) | SOURCED words "breaks weekly lows"; the 24-bar cooldown OURS |
| Bounce | within B = 6 bars from the break bar (inclusive) a 1h close > W | words SOURCED ("then bounces"); B=6 OURS (chart 2-3, doubled) |
| Hold | K = 4 consecutive closed bars, all after the bounce bar, each with close >= BBupper(20,2) x (1 - 0.5 %) AND RSI14 in [52, 60) , and \|RSI[t] - RSI[t-K+1]\| <= 3 points | BB(20,2), RSI14, "under 60": SOURCED. K=4 (chart 5-6, fewer is more events), 0.5 % band, floor 52 (chart 56-58), flat <= 3 points: OURS |
| BB / RSI form | SMA20 +- 2 population stdev (TradingView); Wilder RSI via `layers/rsi/rsi_core.py` | SOURCED convention |
| Trigger | the close of the first bar t for which the hold holds, and t <= break bar + 24 (HMAX=24, OURS); first trigger per episode only | OURS |
- DECISION (OURS): Stoch RSI "pinned ~96" is on the chart but the operator gave no rule for it; not used.

## 3. Outcome measures (long AND short readouts, fee-net at C)
Forward return R_h = (close[t+h] / open[t+1] - 1) x 100 % for h in {1, 4, 12, 24} hours; MFE / MAE over t+1..t+24 (1h highs/lows); first touch of +1 % / -1 % from the entry within 24 h using 1m bars (a 1m bar touching both counts as "both", read adversely). Short readout = sign-flipped. "Continues up" = positive R; "fails back down" = negative R.

## 4. Baselines
- (a) SAME hold condition (K bars, band, RSI, flat) with NO weekly-low break in the previous 24 bars; 24-bar cooldown between baseline events; whole DEV. Verdict baseline.
- (b) random clock matched by hour-of-day: 20 random bars per event with the same UTC hour of day, at least 24 bars from any event trigger; seed 20261016. Reported, not verdict-bearing.

## 5. PRIMARY CELL and verdict (fixed now; DEV only; one run)
Primary = variant V1 (ISO prior-week low, K=4), LONG, h = 4 h. Statistic: mean R4 of events minus mean R4 of baseline a (DIFF), day-clustered SE (UTC day of trigger; SE of a group mean = sqrt(sum_d S_d^2)/n, groups independent), 95 % CI = DIFF +- 1.96 SE, MDE80 = 2.8 x SE_DIFF.
- n = events with a full 24 h forward window.
- **PASS** iff n >= 30 AND DIFF > 0 with the 95 % CI excluding 0 (low > 0, hence t_DIFF >= 2) AND fee-net long mean (mean R4 - C) > 0.
- **INCONCLUSIVE** iff n < 10 (operator rule), OR the bar is not met and MDE80 > 2C = 0.28 % (the sample could not have detected a cost-sized effect).
- **FAIL** iff n >= 10, bar not met, and MDE80 <= 0.28 %.
- The short readout, other horizons, variants and layers carry NO verdict. A striking short-side result needs its own PRE_REG (a new trial).
- No bar is changed after any outcome is read. Even a PASS is a gross-effect finding on DEV only; promotion needs the full `PROMOTION_PIPELINE.md` path (VALIDATION once, holdout once, n >= 30 OOS trades).

## 6. Expected sample and power (counts only, computed BEFORE any outcome; the only outcome-type number read is the unconditional 4 h return SD over ALL DEV bars, not event-conditioned)
- DEV has 21,888 1h bars. Counts at the frozen parameters: 201 episodes (weekly-low break), 8 triggered events for V1 (122 had no bounce within 6 bars, 71 bounced but never held), baseline a 88 events. V2 rolling-168 6 events, V3 K=3 14, V4 K=6 4.
- Unconditional SD of R4 = 1.141 %. With n = 8 the MDE80 on one group mean is 1.13 %, eight times the cost C. Expectation stated now: the primary verdict will be **INCONCLUSIVE (n = 8 < 10)**.
- Sample needed for a decision at MDE80 <= 0.28 %: n >= (2.8 x 1.141 / 0.28)^2 = about 130 events per group (more with baseline noise). At about 3 events a year that is decades; the only route is a looser PRE_REG (new trial), more instruments, or a forward live sample (which is why the live tracker exists). DECISION (OURS): the parameters are NOT loosened here to manufacture events (that would be tuning after seeing counts); the counts are disclosed instead.

## 7. Conditioning layers (operator addition; one at a time, each a pre-declared split of the SAME V1 events)
Each layer = base + that one split; the outcome table is printed per split side next to the base. No combined or tuned stack unless a single layer passes ON ITS OWN (its side meets the section 5 bar against baseline a: n >= 30, CI above 0, fee-net > 0). A layer is NOT_EVALUATED if either side has n < 10. The base verdict never depends on a layer.
1. **Open interest** change over the hold window (sign; median split): NOT_IN_DATA for DEV (section 1). Live-tracking only: the status CLI logs OI (sign of change over the last K bars and the level) at every armed/active event so a forward sample builds.
2. **CVD change** (sign, > 0 vs <= 0; and median split): DECISION (OURS) the CVD change over the hold window equals the net delta over the same bars by identity, so to make the layers distinct this layer uses the window break-bar open .. trigger close (the whole episode: "CVD small up then flat"); sum of delta = 2 tbv - v.
3. **Net delta** (taker buy - sell) over the hold window only (K bars ending at the trigger): sign and median split.
Trial ledger rows (each split = one variant): see section 8.

## 8. Trial ledger and promotion bookkeeping
`MyTradingSys/research/TRIAL_LEDGER.csv` (created here because it does not exist; column `study` as `promote.py` expects) study id `wlow_bounce_bbrsi60_2026-10-16`. Eight computed variant rows: V1_primary, V2_roll168, V3_K3, V4_K6, L2_cvd_sign, L2_cvd_median, L3_netdelta_sign, L3_netdelta_median. (L1 OI is not computed; recorded in this file, not as a row.) A manifest draft (mode shadow) will state `variants: 8` and is expected to be REJECTED until VALIDATION and holdout reads exist; it is not registered.

## 9. Outputs
`study.py`, `RESULT.md` (verdict first line), `events.csv` (timestamps only), the detector + tests under `layers/wlow_bounce/`, a read-only status CLI, a READY task card to wire a collection-only shadow emitter after fable-h1 ships (NOT wired tonight: another worker is changing the promotion gate in `live_runner_cli.py`).
