# PRE-REGISTRATION: US cash open, first 3 minutes, trade the carry-on or the fade, 10 symbols (frozen 2026-11-15, before any outcome)

Card `rederive-us-open-first3m` (queue row 1, PLAN_24H_2026-11-15 section 8). Code: `study.py`, tests `test_study.py`. Written and committed before study.py was run on any data.
Prior work: `us_open_first3m_2026-11-11` was DESCRIPTIVE (BTC only, no fees, no entries). This study turns it into tradeable rules and tests them fee-net out of sample on 10 symbols.

## Hypothesis
The direction of the first 3 minutes after the 09:30 New York open either carries on (momentum) or reverses (fade) over the next 27 or 57 minutes by more than the round-trip cost. The 11-11 descriptive read (49.5 % agreement over 27 min, 47.1 % over 57 min on BTC) predicts NO edge; this tests it with fees, on more symbols, out of sample.

## Context
- Why now: operator question 2026-11-11 ("first 1-3 min move just after US open") and PLAN_24H_2026-11-15 queue row 1 (re-derive edge candidates on 10 symbols, phase-split).
Regime: BTC bull/bear tag at the event (last completed UTC daily close of BTCUSDT above / below its SMA200); NOT a gate, every row is also reported split by it and the `Regime mix:` line prints the share of events in each.
Phase: the US cash-open opening drive (first 3 minutes) is the phase; the study is the rule inside that phase only.
Session: US open, 09:30 America/New_York on weekdays (DST-aware); US market holidays are NOT removed (OURS, the crypto market trades anyway).
Entry: open of the 4th minute bar (09:33 NY), after the first 3 bars have closed; no look-ahead (test_study.py goes red with ENTRY_OFFSET = 0).

## Rule (SOURCED = given by an order / repo, OURS = chosen here before any outcome)
| Item | Value | Label |
|---|---|---|
| Symbols | BTCUSDT ETHUSDT SOLUSDT BNBUSDT XRPUSDT DOGEUSDT ADAUSDT AVAXUSDT LINKUSDT LTCUSDT (the repo's standard 10-symbol set, PLAN_24H_2026-11-05) | SOURCED (repo set) |
| Data | Binance spot 1m OHLC from the shared cache `F:\MTS\data_cache\binance_1m\<SYM>_1m.npz` (arrays t_ms,o,h,l,c; no volume, so the volume and taker-share cuts of 11-11 are NOT repeated) | SOURCED (cache) |
| Event | each weekday date; T0 = 09:30 New York as UTC; needs all 60 one-minute bars T0..T0+59 present, else the event is skipped and counted | OURS |
| Signal | m3 = close of bar T0+2 / open of bar T0 - 1; side CONT = sign(m3), FADE = -sign(m3); m3 = 0 skipped | OURS |
| Entry | OPEN of bar T0+3 | OURS |
| Exit | fixed horizon: close of bar T0+29 (the "27 min" horizon) or close of bar T0+59 (the "57 min" horizon); no stop, no target | OURS (horizons from the 11-11 study) |
| Big filter | |m3| >= the symbol's own DEV 75th percentile of |m3| (sorted value at index int(0.75 x (n-1)), DEV events only), frozen before VALIDATION | OURS |
| Cost | round trip = `research_kit.TAKER_RT_PCT` (0.14 %: 2 x (5 bp taker + 2 bp slippage)), imported, no own constant; no funding | SOURCED (research_kit, COST_FIGURES.md) |
| Return unit | net bp of entry price per trade = side x (exit/entry - 1) x 10000 - 14 | OURS |
| Split | DEV = events 2021-01-01 .. 2023-12-31 (descriptive only, nothing tuned except the frozen big cut); VALIDATION = 2024-01-01 .. last full day in the cache | SOURCED (order: OOS 2024+) |
| Regime tag | BTCUSDT last completed UTC day before the event date: close > SMA200 of the last 200 completed UTC daily closes = bull, else bear | OURS |

## Rows (8, all pre-registered)
side {CONT, FADE} x horizon {27, 57} x filter {all, big}. Per row: n DEV / VAL, gross and net mean bp VAL, win rate, count of symbols with positive net mean, VAL mean by regime (descriptive).

## Inference and gates (VALIDATION only; per row)
1. Net mean > 0 with day-clustered SE (`research_kit.cluster_mean_se`, cluster = event date across symbols): lower bound mean - 1.96 x SE > 0.
2. n VAL >= 100, else UNDERPOWERED.
3. Holm over the 8 rows (`research_kit.holm`, one-sided p from the clustered t, p = 1 when the mean <= 0) adjusted p < 0.05.
4. Net mean > 0 in at least 6 of the 10 symbols.
5. Net mean still > 0 after dropping the 5 best event dates (by summed net bp across symbols).
Verdict PASS only if 1-5 all hold; UNDERPOWERED if n < 100; else FAIL. Overall: EDGE only if a row PASSes; else NO EDGE. Best cells are descriptive, no row is selected post hoc. Gross edge screen (0b, report only): gross mean >= 2 x cost (28 bp).

## Not tested
Volume and taker-share cuts, open interest, stops or targets, maker entries, funding, other opens (London, Asia), per-minute entry timing after minute 3, holiday removal.
