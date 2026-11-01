# PRE_REG: reclaim with the video's timing, 4h and 1D (card follow-reclaim-daily-close-stop)

Written and frozen before any result. Source of the idea: Brando cP6xvs2I02s 03:58-04:02, 08:29-08:35 (reclaim of a 4h/1D level, enter at the reclaim close, stop = a close back below). Every number below is OURS unless marked SOURCED.

## Why this is a different hypothesis (verdicts.py check hits tf_break_event_study)
`verdicts.py check` returns the T058 study (one_run, "fade R" FAIL at 15m). Its kill_scope says it says nothing about other exits, the daily frame or other timings. T058 entered at the OPEN after the reclaim window N had elapsed and exited after a fixed 4 bars, with no level stop. This study enters at the CLOSE of the first reclaim bar and exits on the first close back beyond the level (a rule-based stop), cap otherwise. Only the 4h and 1D arms are run; no 15m or 1h arm, so the T058 15m FAIL is not re-run.

## Definitions (reused unchanged from tf_break_event_study_2026-10-30/study.py: CFG, confirmed_pivots; OURS there)
- Level: fractal swing, L bars each side (4h L=3, 1D L=3), confirmed at the close of bar k+L, usable from the next bar; latest live swing per side.
- Break: first bar whose range pierces the level consumes it; a close beyond the level by 0.1 x ATR14(SMA) is a break (else wick sweep, no trade).
- Reclaim: first bar within N bars after the break bar (4h N=6, 1D N=3) whose close is back inside (close >= level for a low break, <= for a high break). No reclaim in N = no trade.
- Entry: the close of the reclaim bar. Low break -> LONG, high break -> SHORT (both sides pooled, symmetric).
- Exit: the first bar close strictly beyond the level (below for a long, above for a short) in the next cap bars; else the close of bar j+cap. cap = 6 bars on 4h, 5 bars on 1D (OURS, from the card). Stop fills at the bar close (no intrabar, no slippage).
- Trades whose cap bar lies beyond the loaded data are dropped (tail truncation, not selected on outcome).
- Fee: SOURCED backtest/fees.py BINANCE_TAKER 0.0005 per side, round trip 0.10 % (regime A). Maker is not tested. Net = gross - 0.10 %.

## Data and splits
BTCUSDT USD-M perpetual 4h and 1d klines from data.binance.vision (public), UTC buckets, monthly files. DEV = 2022-01-01..2024-06-30 (splits.py); 2021-12 is loaded as indicator warm-up only and no trade is dated before 2022-01-01. VALIDATION 2024-07..2025-06 is read ONCE, only if a DEV arm has CI lower bound > 0. HOLDOUT 2025-07+ is never fetched or read. Trade time = reclaim bar time.

## Statistics and verdict
Mean fee-net % per trade, week-block bootstrap 95 % CI (1000 draws, seed 1) on the reclaim bar's week. Rule per arm: n < 100 -> INCONCLUSIVE; else CI upper < 0 FAIL; CI lower > 0 PASS; else INCONCLUSIVE. Verdict arms are the two pooled timeframe arms (4h, 1D), m = 2 (Holm family); per-side rows are descriptive only. DEV already read for this hypothesis: none.

prereg_gate.py --n 111 --sd 0.0245 --cost 0.001 --m 2 (4h; n and sd from tf_break RESULT.md "4h fade R DEV": n 111, SE 0.233 % x sqrt(111) = 2.45 %): MDE 0.007 + cost 0.001 = 0.008 < 0.3, PASS.
prereg_gate.py --n 31 --sd 0.04 --cost 0.001 --m 2 (1D; n from T058 1D R count 20-31, sd 4 % OURS assumed, not measured): MDE 0.022 + cost 0.001 = 0.023 < 0.3, PASS. The gate is count-only; the 1D arm will almost surely be n < 100 and so INCONCLUSIVE by the rule above.

FAIL means stop: entering at the reclaim close of a fractal swing break on BTCUSDT 4h or 1D with a close-back-beyond-the-level stop and a 6/5-bar cap, fee-net at 0.10 % round trip, DEV 2022-01..2024-06; it says nothing about the mirror (trading the failed reclaim), other swing definitions, other caps, maker fees, intrabar stops, other symbols, or the weekly frame.
