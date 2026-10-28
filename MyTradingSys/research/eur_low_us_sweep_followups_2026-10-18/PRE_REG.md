# PRE-REGISTRATION: EUR-LOW-US-SWEEP follow-ups (A long after sweep+reclaim, B LTF RSI-divergence short from the day high, C pre-US double-top short), BTCUSDT 1m, DEV only (frozen 2026-10-18)

Card `eu-low-us-sweep-follow-ups-long-after-sw`. Parent study `research/eur_low_us_sweep_2026-10-14/` (RESULT.md: EXPLORATORY NEGATIVE for the short leg; three legs left open). Code `followups.py` (imports `study.py` `day_event` / `us_dst` unchanged), tests `test_followups.py`.
This file is committed BEFORE `RESULT.md` / `BLOCKED.md`. Labels: SOURCED = the operator's words in RESULT.md of the parent (long after the sweep, RSI divergence on smaller timeframes for the short from the daily high, double top before the US open, fee-net, "a valid back test must be established first"). OURS = every number below (judgement, chosen before any outcome was computed).

## 1. Economics and split
Binance USD-M BTCUSDT 1m, DEV = bars before 2024-07-01 (the loader refuses later bars, so VALIDATION 2024-07..2025-06 and HOLDOUT 2025-07+ are sealed; this follows the repo's current DEV convention, not the parent's 2022-24/2025/2026 split). Taker 0.05 % per side (card) = 0.10 % round trip, no slippage, funding NOT modelled (state it in every result). Decision at a bar close, fill at the open of the second following 1m bar (d = 1), protective stop, time exit, no target (OURS). Trades with entry-to-stop distance < 0.15 % are skipped (OURS) because cost in R explodes.

## 2. Leg definitions (frozen; weekdays; T0 = US cash open - 90 min, `study.py` anchor)
- **A, long after sweep+reclaim.** Event day = `study.day_event` kind RETESTED or SINGLE (EU-session 24 h low L, price >= 0.2 % above L at T0) with a break (1m low < L in [T0, T0+4 h)). Reclaim = first 1m CLOSE > L within 120 min of the break (the parent's finding 4). LONG at the open 2 bars after the reclaim close; stop = lowest low from the break to the reclaim close minus 0.1 %; time exit 120 min. Pooled RETESTED + SINGLE (the parent showed the retest adds nothing over distance). Why it is not the closed `opr_weekly_low_round_sweep` family: that screen used prior-week-low / round-1000 1m breaks with a 60-closes-above precondition and a 5-minute reclaim; this leg is a day-level EU-session 24 h low with a T0 decision time and a 120-minute reclaim window. The weekly-low FAIL (`verdicts.py check` BLOCK, kill_scope UNPARSED) is read as covering weekly/round levels, not this event; flagged in RESULT.md.
- **B, RSI-divergence short from the day high.** 5m bars (UTC-aligned, a bar with any missing 1m bar is NaN), RSI(14) Wilder = FORMULAS.md s.1 (`common.rsi_wilder`). Scan 06:00-20:00 UTC. Bar i makes a new day-to-date high; the previous day high (bar j) is >= 60 min earlier; RSI(j) >= 60 and RSI(i) < RSI(j) - 2. First signal per day. SHORT at the open 2 bars after the 5m bar's last minute; stop = H(i) + 0.1 %; time exit 120 min. "Day high" = running UTC-day high (not the prior-day high).
- **C, pre-US double-top short.** P1 = highest 1m high of [T0-6 h, T0) and at least 61 min before T0; P2 = highest 1m high of [P1+60 min, T0) within 0.15 % under P1; the lows between P1 and P2 fell at least 0.5 % under P1. SHORT at the open of the 2nd bar after the T0-1 close; stop = P1 + 0.1 %; time exit 240 min (the parent's outcome window).
Placebo (planned, not run): same side, same clock time 7 days earlier/later, event's own stop distance and horizon; paired difference clustered by day.

## 3. Power gate (count-only; `python followups.py --count`, no outcome computed; COUNT.md)
`prereg_gate.py --n <tradeable days> --sd 1.0 --cost <0.10 % / median stop distance in R> --m 3` (sd 1.0 R is the favourable end, precedent runs used 1.5; m = 3, the three legs):
| leg | n days | median stop % | cost R | MDE R | MDE + cost | n needed | gate |
|---|---|---|---|---|---|---|---|
| A | 133 | 0.528 | 0.190 | 0.280 | 0.470 | 864 | BLOCK |
| B | 208 | 0.405 | 0.247 | 0.224 | 0.471 | 3723 | BLOCK |
| C | 100 | 0.531 | 0.188 | 0.323 | 0.511 | 834 | BLOCK |
A BLOCK parks the leg: no outcome is computed, no stability test, no variants. Re-opening needs a new pre-reg with a changed design (more units, wider stop, maker fills) decided before any outcome.

## 4. Pass rule (would apply if a gate PASSed; fixed now)
PASS iff gate PASS and n >= 200 and mean net (after 0.10 % fee) > 0 with t >= 2 and paired DIFF vs the placebo >= +0.05 % with t >= 2, same sign in 2022, 2023 and 2024-H1 and in every leave-one-year-out. FAIL if powered and not PASS. BLOCKED if the gate fails. Not changed after the first outcome (none is read).

## 5. Verdict arms (status at freeze)
| arm | n | mean G | SE | verdict |
|---|---|---|---|---|
| A long after sweep+reclaim (BLOCKED, power gate) | 133 | none | none | BLOCKED |
| B RSI-divergence short (BLOCKED, power gate) | 208 | none | none | BLOCKED |
| C pre-US double-top short (BLOCKED, power gate) | 100 | none | none | BLOCKED |

FAIL means stop: none; BLOCKED legs are not killed (no outcome was read), they are untestable at this design and sample.
