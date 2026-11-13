# Fabio team free courses: testable rules and 5 draft pre-registrations (2026-11-14)

Card `fabio-crypto-courses-1114`. Evidence: 39 caption files, 39 extract files in `MyTradingSys/research/fabio_crypto_courses_1114/` (763 quotes, each with a [h:mm:ss] stamp, `verify_extract_quotes.py` exit 0 on every file). Channels and playlists: `FABIO_CHANNELS_1114.md` (same folder).

## Read this first (what the courses are, and are not)

- The courses are CME index futures (NQ, ES), taught on DeepCharts footprint, MBO and heatmap data. No team video, playlist or title is about crypto. The operator's crypto claim is only partly backed:
  - DeepDOM video `TLof1d0jYA0` (2026-05-14, 00:26:53 and 00:39:57): DeepDOM "doesn't have aggregated crypto data yet", crypto expected "next few months" (extract_TLof1d0jYA0, K1-K2). If the team shipped it since, we found no video on it.
  - Fabio's own "Orderflow Series 2025" `8nEDJ5npS1M` (Italian, 2025-06-09) applies his value-area/AMT logic to Bitcoin daily and weekly charts (rules R27, R28 below), and `692OdHaZnRU` says crypto volume is split across venues, so single-venue order flow is unreliable (S7). Our data is one venue (Binance), so every footprint rule is a one-venue read.
- Almost every stop, target and threshold is NOT stated by the speakers: they point at chart levels. Every win rate or R figure is a speaker claim with no data shown (kYX05qESJMs reports 349 hand-picked trades, in-sample, and its pooled totals do not add up).
- Labels: SOURCED = verified quote in an extract file; OURS = our choice, untested.

## A. Table of testable rules (ids point to extract files; all quotes verified)

Computable column: Y = Binance 1m klines (taker_buy_volume gives delta, on disk F:/MTS/data/tom_raw/klines), A = needs aggTrades per price level (public data.binance.vision; only hourly bins on disk), N = not computable.

| rule | trigger / definition (his numbers) | source ids | stop / target stated | comp |
|---|---|---|---|---|
| Delta % | (ask - bid volume) / total volume; initiative bar = abs >= 10 %, balanced = 2 to 7 % | Ni6quY00dcw C1-C2; uk2-7T1BW34 U3; M5ipTvMi0tM V2 | n/a | Y |
| Stop-run bar | burst through a prior extreme, one-sided aggression, far side empty, delta >= 25 % (example 40 %, another reading > 50 %); delta 14 % or 5 % = not a stop run | 2Mm_1wS40m0 M1-M2; 3MID2HLZS30 S2-S4 | none | Y |
| Stop-run fade | exhaustion only; enter on close of the signal bar; stop slightly beyond the bar extreme; target = start of the run; London hours, before 7:00 NY, volume spike | kYX05qESJMs S1, S2, S8 | yes (structural, no distances) | Y (volume threshold 1,300 ES lots is OURS to rescale) |
| Sweep without delta | sweep with little delta/imbalance = failed auction, not stop run | 3MID2HLZS30 S3 | none | Y |
| CVD absorption divergence | price does not break the prior low/high, CVD does | Ni6quY00dcw C3 | none | Y |
| CVD exhaustion divergence | price breaks, CVD does not | Ni6quY00dcw C4; uk2-7T1BW34 U5 | none | Y |
| Divergence must be local | 1-minute scale, nearby swings, not whole session | Ni6quY00dcw C5 | what NOT to do | Y |
| Divergence entry | next initiative bar (>= 10 % delta) is the entry; VWAP 1st/2nd SD band as location; target other side of VWAP; trail stop | Ni6quY00dcw C7; kYX05qESJMs S5 | target yes, stop structural | Y |
| CVD leads price | momentum trades follow CVD direction; flip comes before the setup | 8nEDJ5npS1M R19-R21 | R21 stop above sell aggression | Y |
| Diagonal imbalance | ask vs bid one tick below: >= 2x imbalance, >= 4x strong (ZrfwJBaI07Y quotes 300/400 %) | h4emw9_2LU8 F2; KObUowoFiK0 K2; ZrfwJBaI07Y Z2 | none | A |
| Stacked imbalances | 3 imbalances in a row = high-probability signal; enter one tick below after confirmation | h4emw9_2LU8 F7-F8 | none | A |
| Unfinished auction | both sides non-zero at the bar extreme: level likely revisited | h4emw9_2LU8 F4 | none | A |
| Exhaustion ratio | volume at 2nd-to-last tick / last tick >= 10 at the extreme | KObUowoFiK0 K4 | none | A |
| POC shift | POC moving lower = first bearish signal | h4emw9_2LU8 F3 | none | A/Y |
| Value area | 70 % of volume; outside = anomaly, reverts | qihraSSdI_M V2; e_RlG84pq6g E2 | n/a | Y (approx from 1m) |
| Failed auction at VA edge | break out, re-enter, enter on re-entry/test; stop beyond failed extreme (or below POC / whole area); target other side, conservative = POC/HVN | qihraSSdI_M V3; e_RlG84pq6g E3, E5, E8; 8nEDJ5npS1M R9-R10, R14-R15; VHhvg96W6lc V2 | yes (structural) | Y |
| VA breakout continuation | volume filter, enter on test; stop under POC / HVN; target 1:3-1:4 | qihraSSdI_M V4; e_RlG84pq6g E4 | yes | Y |
| VA migration bias | POC and VA shift together = next-day continuation; VA up with POC down = still accumulation | 8nEDJ5npS1M R4-R6; VHhvg96W6lc V10 | none | Y |
| Acceptance | value built outside the area, not a wick | 8nEDJ5npS1M R29; qihraSSdI_M V4 | n/a | Y |
| Range target worth it | R:R 3.45 yes, 1.79 less, 1.5 seen | 8nEDJ5npS1M R11 | R:R only | Y |
| Delta peak + VA low zone | buy zone = delta peak and VAL of the breakout swing; stop below; 1:3 swing target | VHhvg96W6lc V9, V11 | yes (no distance) | A |
| VWAP | session VWAP, bands at 1/1.5/2/3 SD (he keeps 2); mean reversion to VWAP, outer bands raise bounce odds; not alone in strong trends | R5L890juvRw V1-V7 | target = VWAP, stop NOT stated | Y |
| Opening range breakout | 15 or 30 min range, body closes outside, initiative filter (volume, delta > 10 %, big trade); stop under breakout candle or range; 1:1 to 1:3 | M5ipTvMi0tM V1-V4; A5J4e5jbgVI A1-A2; 3Zs52kfCwiU O1-O2; KObUowoFiK0 K9; TjEYZH4u7d0 T2-T4 | yes | Y (BTC "open" is OURS) |
| Regime first | balance vs imbalance; trend phases about 20 % of time; model in wrong phase gets stopped | 8nEDJ5npS1M R1; VHhvg96W6lc V1-V3 | n/a | partly |
| Do not trade list | divergence session-wide; stop-run in NY hours; breakout with rising volume as exhaustion; 1:4-1:6 targets inside balance; buying once value accepted lower | Ni6quY00dcw C5; kYX05qESJMs S8; VHhvg96W6lc V3, V6 | n/a | Y |
| BTC cycle long (weekly) | after exit from weekly accumulation: stop under the breakout-origin candle, target upper dealing range (1:2 and 4.67 in examples); expansion about 2x the balance range | 8nEDJ5npS1M R27-R28 | yes (no distance) | Y (few events) |
| Management | one third of open profit risked in an add; break-even then stop in profit; take profit just before VAL | VHhvg96W6lc V8; agjftXPkLUE A8; 8nEDJ5npS1M R15 | n/a | Y |
| Not computable | MBO icebergs (150-300 lot filters), heatmap liquidity and spoofing, DeepDOM reload, IVB / "Nasdaq effort" / protection level / extended average (proprietary, formula not given), options gamma / call walls | WPAP7JaVzF4; aukc_NLGmxo; TLof1d0jYA0; r1cIAW0zr3Q; JR50FQIQN2A; M5ipTvMi0tM V6 | n/a | N |

## B. Ranking of the 5 best test candidates

Ranked by specificity first (numbers stated, trigger written), then computability from data we hold. All five are computable from 1m klines except 5.

| rank | candidate | specific (SOURCED numbers) | computable | main risk |
|---|---|---|---|---|
| 1 | Stop-run exhaustion fade | delta >= 25 %, close entry, stop beyond extreme, target start of run, hour filter | 1m klines (delta from taker_buy_volume) | hand-fitted filters, speaker sample in-sample; short-hold trades vs 12 bp |
| 2 | Value-area failed auction (break-in) | 70 % VA, stop beyond failed extreme, target POC / other edge | 1m klines, volume spread over the bar range (approx) | VA from klines is an approximation; needs balance-phase gate |
| 3 | CVD divergence + initiative bar | abs delta >= 10 %, session CVD, VWAP band location, target VWAP | 1m klines | swing/lookback undefined (ours), no stop stated |
| 4 | VWAP 2 SD reversion | 2 SD bands, target central VWAP | 1m klines | stop not stated, fails in trend |
| 5 | Stacked diagonal imbalance | 4x ratio, 3 levels in a row, enter one tick below | aggTrades per price (download, not on disk) | tick size on BTC is ours, one venue, data volume |

Not in the five, noted: opening range breakout (needs a BTC "open", all stop/targets are index session based) and the weekly BTC cycle long (R27-R28: a handful of events, belongs to testnet-forward, not a backtest gate).

## C. Draft pre-registrations (drafts: NOT frozen, no number computed; file name deliberately not PRE_REG.md until a card freezes it)

Shared parameters for all five (labels as in earlier PRE_REG files):

| Parameter | Value | Label |
|---|---|---|
| Instrument / data | BTCUSDT USD-M perp 1m klines `F:/MTS/data/tom_raw/klines`, resampled 5m where stated; delta% = (2 x taker_buy_volume - volume) / volume x 100 (computed from the klines columns, independent of any repo code; add to FORMULAS.md before the run) | OURS |
| Window | DEV only: event closes in [2022-01-01, 2024-07-01), loader raises on later dates (`backtest/splits.py`); VALIDATION and HOLDOUT not read | SOURCED splits.py |
| Cost | net = gross - 12 bp round trip (all taker) | SOURCED operator task 2026-11-13 |
| Stop floor | stop distance = max(speaker's structural stop, 0.6 x ATR(14) of the signal timeframe, 0.5 % of entry) | SOURCED operator task; speaker stops are tighter or undefined |
| Statistics | day-clustered SE (cluster = UTC day), t = mean / SE; net R and net bp per trade | SOURCED research_kit style |
| Verdict | SURVIVES if net mean > 0 and one-sided p < 0.05 after Holm over the focal cells; UNDERPOWERED if fewer than 100 trade-days in the focal cell; else FAILS | OURS (power floor as in earlier PRE_REGs) |
| Baseline | same-hour bars drawn from the same ATR(14) decile, no signal, same stop/target construction | OURS |
| Phase split | weekly phase tag from `research_kit.regime_tag` (bull / bear / range), reported per cell; focal cell = the phase named in each Context | SOURCED-in-repo |

### P1. Stop-run exhaustion fade (rank 1)

Hypothesis: a bar that sweeps a prior swing extreme with a one-sided delta burst and a volume spike marks exhaustion; fading it at the bar close earns more than 12 bp net on average, in the hours the speaker names.

| Parameter | Value | Label |
|---|---|---|
| Sweep | bar high > highest high of the prior 60 bars (short fade); mirror for lows (long fade) | 60 = OURS; "prior important high" SOURCED kYX05qESJMs S1-S2 |
| Delta | abs(delta%) >= 25 in the sweep direction; sensitivity cells 10 and 50 | 25 SOURCED 2Mm_1wS40m0 M1; 10 / 50 SOURCED 3MID2HLZS30 S2, S4 as readings |
| Volume spike | bar volume >= 3 x median volume of the prior 20 bars | OURS (his 1,300 ES lots cannot be rescaled from the video) |
| Exhaustion only | skip if the prior 10 bars already moved >= 1.5 x ATR(14) in the sweep direction within the last 3 bars (impulse start) | OURS rule for "never at the beginning of an impulse" (SOURCED, kYX05qESJMs S2) |
| Hours | event close 00:00 to 12:00 UTC (London morning, before 7:00 NY); control row 12:00 to 24:00 UTC | SOURCED hours, UTC mapping OURS |
| Entry | close of the signal bar, market | SOURCED kYX05qESJMs S1 |
| Stop | beyond the signal-bar extreme, then the stop floor above | SOURCED structure; floor SOURCED operator |
| Target | start of the run: lowest low (short fade: highest high mirrored) of the 10 bars before the signal bar; second target arm 1:2 | SOURCED idea, 10 bars OURS; 1:2 OURS |
| Time stop | 60 bars | OURS |
| TF | 1m and 5m | OURS |

Context
Regime: weekly tag from regime_tag, reported for bull, bear and range; focal cell = bear and range (the phase BTC is in on 2026-11-14, six red weeks).
Phase: exhaustion at the end of an impulse after a sweep of a prior swing extreme; not impulse start.
Session: 00:00 to 12:00 UTC focal, 12:00 to 24:00 UTC control.
Entry: signal-bar close at market (taker), stop and target as above.

### P2. Value-area failed auction (rank 2)

Hypothesis: when BTC is in balance, a failed break of the previous day's 70 % value-area edge returns to the POC / opposite edge often enough to beat 12 bp net.

| Parameter | Value | Label |
|---|---|---|
| Profile | previous UTC day, 1m volume spread uniformly over each bar's high-low range in 0.1 % price bins; POC = max bin; VA = smallest contiguous set around POC holding 70 % | 70 % SOURCED qihraSSdI_M V2, e_RlG84pq6g E2; binning OURS |
| Balance gate | today's first 4 UTC hours stay inside the previous day's VA +/- 0.25 x ATR(14 daily) | OURS (his classifier is NOT stated) |
| Failed break | a 5m bar closes outside VAH (VAL), then within 6 bars a 5m bar closes back inside | 6 bars OURS; failed-auction idea SOURCED |
| Entry | close of the first re-entry bar, fade toward the value (short after VAH failure) | OURS (exact bar rule NOT stated) |
| Stop | beyond the failed-break extreme, then the stop floor | SOURCED qihraSSdI_M V3 |
| Target arms | A: POC (conservative); B: opposite VA edge | SOURCED both |
| Time stop | end of the UTC day | OURS |

Context
Regime: range-bound balance only, gated by the balance gate; weekly tag reported.
Phase: balance (price rotating inside value), not trend; failed auction at the value edge.
Session: all UTC hours; per-hour split reported as descriptive.
Entry: first re-entry bar close at market, stop and target arms as above.

### P3. CVD divergence plus initiative bar (rank 3)

Hypothesis: a local absorption divergence followed by an initiative bar (abs delta >= 10 %) in the reversal direction beats 12 bp net, best when price sits at VWAP -1 / -2 SD (long) or +1 / +2 SD (short).

| Parameter | Value | Label |
|---|---|---|
| CVD | cumulative delta per bar, reset at 00:00 UTC | reset SOURCED uk2-7T1BW34 U4, 00:00 UTC OURS |
| Swings | 1m pivot lows (highs) with 5 bars each side; compare two consecutive pivots at most 30 bars apart | 5 and 30 OURS; "short-term, small parts" SOURCED Ni6quY00dcw C5 |
| Divergence | price lower low, CVD higher low (long); mirror for shorts | SOURCED Ni6quY00dcw C3, uk2-7T1BW34 U5 |
| Trigger | first bar after the second pivot with delta% >= +10 (long), close above its open | 10 SOURCED Ni6quY00dcw C2 |
| Location split | price between VWAP and the 2nd SD band (SOURCED kYX05qESJMs S5) vs elsewhere | SD volume-weighted, UTC-day VWAP OURS |
| Entry | trigger-bar close | OURS (Ni6quY00dcw C7 states "next initiative candle") |
| Stop | below the second pivot, then the stop floor | OURS; his stop NOT stated |
| Target arms | A: session VWAP; B: 1:2 | A SOURCED kYX05qESJMs S5 ("other side of VWAP"); B OURS |

Context
Regime: weekly tag reported; focal cell = bear and range, long side only (operator long-edge interest), short side descriptive.
Phase: local exhaustion or absorption inside a short pullback, 1m scale; not whole-session divergence.
Session: first 4 UTC hours after the 00:00 reset focal ("beginning of the session" Ni6quY00dcw C8, OURS mapping), rest as control.
Entry: trigger-bar close at market.

### P4. VWAP 2 SD band reversion (rank 4)

Hypothesis: the first close beyond the 2 SD band of the UTC-day VWAP reverts toward VWAP for more than 12 bp net; the edge disappears on trend days.

| Parameter | Value | Label |
|---|---|---|
| VWAP and bands | UTC-day VWAP, volume-weighted SD of price, bands at 2 SD | 2 SD SOURCED R5L890juvRw V3 ("usually keeps 2"); reset time OURS |
| Event | first 5m close below the -2 SD band (long) or above +2 SD (short) per day and side, after at least 2 UTC hours of the day | 2 hours OURS (bands need data) |
| Entry | event close | OURS |
| Target | central VWAP at entry time (fixed at entry) | SOURCED R5L890juvRw V4 |
| Stop | stop floor only (his stop NOT stated) | OURS / SOURCED operator floor |
| Trend split | trend day if abs(close - open) / (high - low) of the signal day so far >= 0.6 at entry | SOURCED-in-repo fabio v3 P41 as in earlier PRE_REGs; used for "not alone in strong trends" (R5L890juvRw V7) |
| Time stop | end of UTC day | OURS |

Context
Regime: weekly tag reported; focal cell = range and bear (reversion in a downtrend is the long-edge question).
Phase: balance or pullback day (not a trend day), price stretched from VWAP.
Session: all hours after the 2-hour warm-up.
Entry: event close at market, target fixed at the VWAP value at entry.

### P5. Stacked diagonal imbalance (rank 5)

Hypothesis: three consecutive price levels at the bar extreme with diagonal ask/bid >= 4x mark initiative aggression that continues for more than 12 bp net after a one-tick retest entry.

| Parameter | Value | Label |
|---|---|---|
| Data | BTCUSDT USD-M aggTrades per 1m bar, price bins of $5 (ticks are $0.10; $5 = OURS), 3 sample months chosen before looking, not on disk (download from data.binance.vision, public) | OURS |
| Imbalance | ask volume at level p / bid volume at p - 1 bin >= 4 (buy imbalance); bid at p / ask at p + 1 bin >= 4 (sell); sensitivity 2 | 4 and 2 SOURCED h4emw9_2LU8 F2, KObUowoFiK0 K2 |
| Stack | 3 consecutive levels | SOURCED h4emw9_2LU8 F7 |
| Entry | after the stack bar, enter at the first return to the stack's near edge within 10 bars (the "one tick below" confirmation) | SOURCED idea h4emw9_2LU8 F8; 10 bars OURS |
| Stop | beyond the stack bar extreme, then the stop floor | OURS; his stop NOT stated |
| Target | 1:2 and next prior-swing extreme | OURS |

Context
Regime: weekly tag reported; no focal gate (sample too small to split).
Phase: initiative after a response / absorption phase (RNI pattern, h4emw9_2LU8 F6), not a balance chop.
Session: all hours.
Entry: limit at the stack edge, filled only if touched within 10 bars.

Power note: P5 on 3 months will most likely be UNDERPOWERED; its job is to show whether the idea has any signal before a larger download.

## D. What this does not decide

No number was computed in this ship. The five drafts are not frozen; a card freezes them (FROZEN_UTC line, prereg lint) before any return is read. Speaker win rates (53-55 %, 66 %, 80 % for stop runs, 60-70 % after stop runs) are claims without data and are not used as targets for our result.
