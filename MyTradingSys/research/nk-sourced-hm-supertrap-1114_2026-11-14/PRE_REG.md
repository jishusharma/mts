# PRE_REG nk-sourced-hm-supertrap-1114 (written and committed with the code before any outcome was computed)

Rules under test, exactly as NK states them (verified quotes: `MyTradingSys/research/nk_stocktalk_1113/interviews/CLARIFICATIONS.md`, EXTRACT.md):
Hilega Milega (Qdug_K_TNHg 00:23:25-00:40:21: RSI 9, zone 50, WMA21 and EMA3 ON the RSI, plus VWAP; state not cross; trend frame >= 30m, entry 5/10m, positional daily; never buy below VWAP, stop just under it), the gap rule (PV9HZB8Sb8Q 00:02:41: wait >= 15 min for a close above the gap candle high, then a retest, then enter; previous day H/L matter) and the Supertrap (AKZ-7zvDxpY 00:25:49-00:27:07: big gap, first 5-10 min candle with >= 50% outside the Bollinger Band, stop at VWAP, bull = back above VWAP, bear mirrors).
Our earlier NK4 test (branch JIS-NB/nk4-hilega-milega-recon-1114: 15m cross + RSI 30/70 confirm) is NOT his rule and is not reused. Crypto has no exchange gap and NK never gave Bollinger length, target numbers or a gap size: those are OURS and marked so.

## Context
Regime: bull/bear cycle flag from BTC close vs its 200-week (1400-day) SMA, known from the prior close (BULL / BEAR / NA before 2021-06); reported as a second cut, never pooled.
Phase: daily label per coin from the prior close: UP (ADX14 >= 20, DI+ > DI-, SMA20 slope over 5 days > 0), DOWN (ADX14 >= 20, DI- > DI+, slope < 0), RANGE (else). Every result row is split by phase; there is no pooled headline.
Session: A trades 24/7 with the session VWAP anchored at 00:00 UTC (variant U) or at the 13:30 UTC NY open (variant N); B events are the CME-weekend proxy (Sunday 23:00 UTC) and the 00:00 and 13:30 UTC session opens.
Entry: A = rising edge of {trend-frame HM state = d AND entry-frame HM state = d AND close on the right side of the anchored VWAP}; B = first candle outside the Bollinger Band then VWAP re-cross (Supertrap) or breakout of the first 15 m high/low plus retest (gap rule). Entry at the open of the bar after the signal bar.

## Parameters (S = SOURCED from NK, O = OURS, 3 = third party)
| Param | Value | Label |
|---|---|---|
| HM RSI / lines | RSI(9) Wilder on close; EMA(3) of RSI; WMA(21) of RSI | S |
| HM state | buy = WMA21 below BOTH RSI and EMA3 lines; sell = WMA21 above both; else neutral (a state, not a cross) | S (state rule), O (both lines = "the RSI lines") |
| 50 line | variant h1: buy state also needs RSI9 > 50, sell state RSI9 < 50; variant h0: no 50 condition | S line, O (applying it as a filter, hence both variants) |
| Frames, intraday (I) | trend = 30m state, entry = 5m state | S (>= 30m trend, 5/10m entry); 5m chosen, 10m not run, O |
| Frames, positional (P) | trend = daily state, entry = 30m state | O (NK: positional on daily; one level shift of the same frame ladder) |
| VWAP | typical price (H+L+C)/3 x volume, cumulative, anchored 00:00 UTC (U) or 13:30 UTC, re-anchored every 24 h (N) | S (VWAP leg), O (crypto session anchors) |
| VWAP filter | long needs close > VWAP, short needs close < VWAP at the signal bar | S |
| Stop (A, B) | long: VWAP - 0.1 x ATR14(5m); short mirror; stop distance S = max(entry - stop level, max(0.6 x ATR14(5m), 0.3% of entry)); P: S = max(entry - stop level, max(1.5 x ATR14(daily), 1% of entry)). Fixed at entry. | S (just beyond VWAP), O (buffer, floors) |
| Exit A | stop (intrabar, stop wins ties, gap fills at the open), or the open after the trend-frame state is no longer d (leaving the state, neutral counts), cap 576 5m bars (I) / 8640 (P) | O |
| No overlap | per coin, a new trade only after the previous one exited | O |
| Bollinger | BB(20, 2), population std, closes of the same frame, band at the candle includes the candle | O (NK never spoke the length) |
| "50% outside" | outside part of the candle RANGE (high-low) >= 0.5; upper for a gap up, lower for a gap down | S (50%), O (range not body) |
| First candle | the first 5m candle of the event, or the first 10m candle (first two 5m bars); the earlier qualifying one is the signal | S (5-10 min), O |
| Supertrap entry | after a qualifying candle, the first 5m close beyond the event-anchored VWAP on the fade side (gap down: close > VWAP, long; gap up: close < VWAP, short) within bars 1..11 of the event; VWAP anchored at the event open; exit stop or 72 bars | S (back through VWAP), O (window, exit) |
| Gap rule entry | first-15-min candle high H15 / low L15 (first three 5m bars). Gap up: first 5m close above H15 in bars 3..14 (>= 15 min), then within 12 bars a bar with low <= H15 and close > H15 (retest holds); long at the next open. Gap down mirror, short. Exit stop or 72 bars. | S (15 min, close above high, retest), O (windows, retest definition) |
| Gap rule + prev-day H/L (rule gd) | additionally the breakout close must be beyond the previous UTC day's high (long) / low (short) | S ("previous day H/L matter"), O (as a hard filter) |
| Gap (i) cme | Sunday 23:00 UTC open vs Friday 22:00 UTC close of the same Binance spot pair (proxy for the CME BTC weekend gap, fixed UTC clock, no DST shift), applied to all 20 coins | O proxy |
| Gap (ii) s0000, s1330 | open of the 00:00 / 13:30 UTC bar vs the close at 20:00 UTC of the previous day (prior session close, OURS) | O |
| Gap size | gap / ATR14(daily, completed days) >= theta: cme 0.5 and 1.0, s0000 0.5 and 1.0, s1330 0.75 and 1.5; direction = sign of the gap | O |
| Costs | 12 bp round trip primary; 6 bp row (cost only, no fill model); fee/R = cost x entry / S per row (median) | task |
| Data | Binance spot USDT 5m (public bulk data.binance.vision), 20 coins BTC ETH BNB XRP ADA DOGE SOL LTC LINK TRX DOT AVAX ATOM ETC BCH XLM UNI NEAR FIL EOS, from listing or 2019-01-01, ends 2026-11-12 (EOS ends 2025-05); missing 5m bars forward-filled with volume 0. Cycle flag from BTC 1d from 2017-08. Files copied byte for byte from the shared cache (same fetch code, fetch.py) into F:\MTS\data_cache\binance\nk-sourced-hm-supertrap-1114\ because a fresh pull ran at about 6 min per 100 files. | task |
| Split | DEV <= 2023-12-31, VALIDATION >= 2024-01-01 by entry time; gates on VALIDATION only, DEV reported | task |

## Variants (26) and rows
Part A (8): anchor {U, N} x frame {I, P} x 50-line {h0, h1}. Part B (18): source {cme, s0000, s1330} x theta (2 each) x rule {st Supertrap, gp gap rule, gd gap rule + prev-day H/L}.
Row = variant x daily phase {UP, DOWN, RANGE} (78 gated rows, all directions pooled inside the phase; long and short shown as descriptive columns). Second cut (descriptive, not gated): variant x cycle {BULL, BEAR}. NO row pools phases.

## Gates for PASS (VALIDATION, 12 bp row, all directions inside the phase)
n >= 100 trades; mean net R > 0; per-trade bootstrap 95% CI lower > 0 (2000 resamples, seed 7); day-cluster bootstrap (UTC day, all coins together, 2000 resamples) 95% CI lower > 0; placebo p < 0.05; survives Benjamini-Hochberg q 0.05 over all 78 rows (one-sided day-cluster bootstrap p of mean <= 0; rows with n < 100 enter with p = 1); mean net R > 0 after removing the best 5 days (by sum R).
Placebo: for each row with n >= 100 and mean > 0, up to 3000 of its trades are sampled; each is replaced 200 times by a random same-coin, same-phase, VALIDATION-period entry with the same direction, the same held bars and the same stop distance as a fraction of price; p = share of placebo mean gross R >= the real mean gross R (+1 smoothing). Placebo is only run for rows that could pass (n >= 100, mean > 0).
Row with n < 100: reported as UNDERPOWERED, never as a failure of the rule.
VERDICT: PASS = at least one gated row passes every gate; otherwise NO PASS. Best VAL row per phase = highest VAL mean net R at 12 bp among rows with n >= 100, reported with its gate flags (best of 26 variants: selection bias, stated).
Power note (scripts/dev/prereg_gate.py --n 350 --sd 1.6 --cost 0.4 --m 78, n = day clusters per phase, sd of per-trade R 1.6 OURS from the NK4 run): MDE 0.364 R + cost 0.4 R = 0.764 vs the 0.30 R plausible-gross limit, the gate says BLOCK. Operator ordered the run; so only a large net edge can be detected and a NO PASS is not proof of no edge (RESULT.md says so).

## Tests (test_study.py, committed with this file)
Causal-prefix tests of the HM states, Bollinger bands, A signals and B signals, a random-walk no-edge test, hand-calculated VWAP / simulator / CME-gap / phase / cycle-flag / BH tests, and `test_bug_is_caught`: with STUDY_BUG=1 (one-bar look-ahead in the states, bands and entry closes) the causal and no-edge tests FAIL (t = 44 on the random walk), proven in the same run.

## Run
`python run.py`: two worker processes below-normal priority (+ the idle parent = 3 processes). Output results.json, then RESULT.md.
